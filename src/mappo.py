"""
Implementazione di MAPPO (Multi-Agent Proximal Policy Optimization) parametrico.
Architettura CTDE (Centralized Training with Decentralized Execution) con Parameter Sharing.

Supporta flotte UAV scalabili (da N=1 a N droni) con osservazioni locali e valutazione.
"""

import os
import time
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.distributions import Categorical

try:
    from torch.utils.tensorboard import SummaryWriter
except ImportError:
    SummaryWriter = None


class ActorNetwork(nn.Module):
    """
    Rete neurale dell'Actor (Policy decentralizzata).
    Prende in input l'osservazione locale o_i dell'agente i (rappresentazione ego-centrica)
    e restituisce una distribuzione categorica sulle azioni discrete.
    """
    def __init__(self, obs_dim, action_dim=5, hidden_dim=128):
        """
        Inizializza gli strati della rete dell'Actor e applica l'inizializzazione ortogonale.

        Args:
            obs_dim (int): Dimensione del vettore di osservazione locale.
            action_dim (int): Numero di azioni discrete disponibili.
            hidden_dim (int): Dimensione dei layer nascosti.
        """
        super().__init__()
        self.obs_dim = obs_dim
        self.action_dim = action_dim

        self.net = nn.Sequential(
            nn.Linear(obs_dim, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, action_dim)
        )

        # Inizializzazione ortogonale dei pesi (standard PPO/MAPPO)
        for name, param in self.net.named_parameters():
            if "weight" in name:
                nn.init.orthogonal_(param, gain=np.sqrt(2))
            elif "bias" in name:
                nn.init.constant_(param, 0.0)
        # Gain ridotto sull'ultimo layer per una distribuzione di probabilità iniziale bilanciata
        nn.init.orthogonal_(self.net[-1].weight, gain=0.01)

    def forward(self, obs):
        """Calcola la distribuzione di probabilità categorica sulle azioni a partire dall'osservazione."""
        logits = self.net(obs)
        return Categorical(logits=logits)

    def get_action(self, obs, deterministic=False):
        """
        Campiona o seleziona l'azione e calcola la relativa log-probabilità.

        Args:
            obs (torch.Tensor): Tensore delle osservazioni locali.
            deterministic (bool): Se True, seleziona l'azione con probabilità massima.

        Returns:
            tuple: (azione scelta, log-probabilità dell'azione).
        """
        dist = self.forward(obs)
        if deterministic:
            action = torch.argmax(dist.logits, dim=-1)
        else:
            action = dist.sample()
        log_prob = dist.log_prob(action)
        return action, log_prob

    def evaluate_actions(self, obs, actions):
        """
        Valuta le azioni per il calcolo della loss dell'Actor durante l'aggiornamento PPO.

        Args:
            obs (torch.Tensor): Tensore delle osservazioni locali.
            actions (torch.Tensor): Azioni eseguite.

        Returns:
            tuple: (log-probabilità correnti, entropia della distribuzione).
        """
        dist = self.forward(obs)
        log_prob = dist.log_prob(actions)
        entropy = dist.entropy()
        return log_prob, entropy


class CriticNetwork(nn.Module):
    """
    Rete neurale del Critic (Valutazione dello stato globale).
    Architettura centralizzata: durante l'addestramento (CTDE) riceve lo stato globale s
    contenente le informazioni complete di tutti i droni, target e ostacoli.
    """
    def __init__(self, state_dim, hidden_dim=128):
        """
        Inizializza la rete neurale del Critic con inizializzazione ortogonale dei pesi.

        Args:
            state_dim (int): Dimensione del vettore dello stato globale.
            hidden_dim (int): Dimensione dei layer nascosti.
        """
        super().__init__()
        self.state_dim = state_dim

        self.net = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, 1)
        )

        # Inizializzazione ortogonale dei pesi
        for name, param in self.net.named_parameters():
            if "weight" in name:
                nn.init.orthogonal_(param, gain=np.sqrt(2))
            elif "bias" in name:
                nn.init.constant_(param, 0.0)
        nn.init.orthogonal_(self.net[-1].weight, gain=1.0)

    def forward(self, state):
        """Stima il valore scalare dello stato globale."""
        return self.net(state)


class MAPPORolloutBuffer:
    """
    Buffer di traiettorie per MAPPO.
    Memorizza transizioni multi-agente e calcola GAE (Generalized Advantage Estimation).
    """
    def __init__(self, buffer_size, num_uavs, obs_dim, state_dim, device="cpu"):
        """
        Inizializza la struttura dati del buffer di rollout.

        Args:
            buffer_size (int): Numero massimo di step temporali per rollout.
            num_uavs (int): Numero di droni nella flotta.
            obs_dim (int): Dimensione dell'osservazione locale.
            state_dim (int): Dimensione dello stato globale.
            device (str): Device PyTorch su cui allocare i tensori.
        """
        self.buffer_size = buffer_size
        self.num_uavs = num_uavs
        self.obs_dim = obs_dim
        self.state_dim = state_dim
        self.device = device
        self.reset()

    def reset(self):
        """Azzera i buffer di memoria delle transizioni."""
        self.obs = np.zeros((self.buffer_size, self.num_uavs, self.obs_dim), dtype=np.float32)
        self.states = np.zeros((self.buffer_size, self.state_dim), dtype=np.float32)
        self.actions = np.zeros((self.buffer_size, self.num_uavs), dtype=np.int64)
        self.log_probs = np.zeros((self.buffer_size, self.num_uavs), dtype=np.float32)
        self.rewards = np.zeros((self.buffer_size, 1), dtype=np.float32)
        self.dones = np.zeros((self.buffer_size, 1), dtype=np.float32)
        self.values = np.zeros((self.buffer_size, 1), dtype=np.float32)
        self.returns = np.zeros((self.buffer_size, 1), dtype=np.float32)
        self.advantages = np.zeros((self.buffer_size, 1), dtype=np.float32)
        self.step = 0

    def add(self, obs, state, actions, log_probs, reward, done, value):
        """Registra una transizione multi-agente nel buffer."""
        self.obs[self.step] = obs
        self.states[self.step] = state
        self.actions[self.step] = actions
        self.log_probs[self.step] = log_probs
        self.rewards[self.step] = reward
        self.dones[self.step] = done
        self.values[self.step] = value
        self.step += 1

    def compute_returns_and_advantages(self, last_val, last_done, gamma=0.99, gae_lambda=0.95):
        """
        Calcola i ritorni scontati e gli advantage con Generalized Advantage Estimation (GAE).

        Args:
            last_val (float): Valore stimato per lo stato finale di bootstrap.
            last_done (bool): Flag di terminazione dell'ultimo step.
            gamma (float): Fattore di sconto dei reward futuri.
            gae_lambda (float): Parametro di trade-off bias-varianza per GAE.
        """
        last_gae_lam = 0.0
        for t in reversed(range(self.buffer_size)):
            if t == self.buffer_size - 1:
                next_non_terminal = 1.0 - float(last_done)
                next_val = last_val
            else:
                next_non_terminal = 1.0 - self.dones[t]
                next_val = self.values[t + 1]

            delta = self.rewards[t] + gamma * next_val * next_non_terminal - self.values[t]
            last_gae_lam = delta + gamma * gae_lambda * next_non_terminal * last_gae_lam
            self.advantages[t] = last_gae_lam
            self.returns[t] = self.advantages[t] + self.values[t]

    def get_batches(self, batch_size):
        """
        Suddivide le transizioni in mini-batch per l'ottimizzazione SGD di Actor e Critic.

        Args:
            batch_size (int): Dimensione di ciascun mini-batch.

        Returns:
            list: Lista di dizionari contenenti i tensori di addestramento.
        """
        # Con Parameter Sharing, le transizioni dell'Actor vengono appiattite su tutti gli N agenti
        total_transitions = self.buffer_size * self.num_uavs

        flat_obs = self.obs.reshape(total_transitions, self.obs_dim)
        flat_actions = self.actions.reshape(total_transitions)
        flat_old_log_probs = self.log_probs.reshape(total_transitions)

        # Gli advantage calcolati dal Critic centralizzato sono condivisi con tutti i droni
        repeated_advantages = np.repeat(self.advantages, self.num_uavs, axis=0).flatten()
        # Normalizzazione degli advantage
        adv_std = repeated_advantages.std()
        normalized_advantages = (repeated_advantages - repeated_advantages.mean()) / (adv_std + 1e-8)

        # Buffer del Critic
        states = self.states
        returns = self.returns
        old_values = self.values

        # Generazione di indici casuali per i mini-batch
        actor_indices = np.random.permutation(total_transitions)
        critic_indices = np.random.permutation(self.buffer_size)

        num_batches = max(1, total_transitions // batch_size)
        critic_batch_size = max(1, self.buffer_size // num_batches)

        batches = []
        for b in range(num_batches):
            act_idx = actor_indices[b * batch_size : (b + 1) * batch_size]
            crit_idx = critic_indices[b * critic_batch_size : (b + 1) * critic_batch_size]

            batches.append({
                "actor_obs": torch.tensor(flat_obs[act_idx], dtype=torch.float32, device=self.device),
                "actor_actions": torch.tensor(flat_actions[act_idx], dtype=torch.int64, device=self.device),
                "actor_old_log_probs": torch.tensor(flat_old_log_probs[act_idx], dtype=torch.float32, device=self.device),
                "actor_advantages": torch.tensor(normalized_advantages[act_idx], dtype=torch.float32, device=self.device),
                "critic_states": torch.tensor(states[crit_idx], dtype=torch.float32, device=self.device),
                "critic_returns": torch.tensor(returns[crit_idx], dtype=torch.float32, device=self.device),
                "critic_old_values": torch.tensor(old_values[crit_idx], dtype=torch.float32, device=self.device),
            })

        return batches


class MAPPO:
    """
    Algoritmo MAPPO parametrico (Multi-Agent Proximal Policy Optimization).
    Supporta configurazioni da singolo drone (PPO standard) fino a N droni cooperanti.

    Caratteristiche principali:
    - CTDE (Centralized Training, Decentralized Execution)
    - Parameter Sharing tra tutti gli agenti della flotta
    - Rappresentazione ego-centrica per l'Actor
    - Clipping della policy e Generalized Advantage Estimation (GAE)
    """
    def __init__(
        self,
        num_uavs=1,
        obs_dim=None,
        state_dim=None,
        action_dim=5,
        grid_size=10,
        num_obstacles=4,
        hidden_dim=128,
        lr_actor=3e-4,
        lr_critic=1e-3,
        gamma=0.99,
        gae_lambda=0.95,
        clip_param=0.2,
        entropy_coef=0.01,
        value_loss_coef=0.5,
        max_grad_norm=0.5,
        ppo_epochs=10,
        batch_size=64,
        n_steps=1024,
        device=None,
        seed=42,
    ):
        """
        Inizializza i moduli Actor-Critic, gli iperparametri PPO e i buffer di memoria.
        """
        self.num_uavs = num_uavs
        self.action_dim = action_dim
        self.grid_size = grid_size
        self.num_obstacles = num_obstacles
        self.hidden_dim = hidden_dim

        # Calcolo automatico delle dimensioni se non specificate
        # obs_dim = 2 (self) + 2 (target) + 2 * num_obstacles + 2 * (num_uavs - 1)
        if obs_dim is None:
            self.obs_dim = 2 * num_uavs + 2 + 2 * num_obstacles
        else:
            self.obs_dim = obs_dim

        if state_dim is None:
            self.state_dim = 2 * num_uavs + 2 + 2 * num_obstacles
        else:
            self.state_dim = state_dim

        self.lr_actor = lr_actor
        self.lr_critic = lr_critic
        self.gamma = gamma
        self.gae_lambda = gae_lambda
        self.clip_param = clip_param
        self.entropy_coef = entropy_coef
        self.value_loss_coef = value_loss_coef
        self.max_grad_norm = max_grad_norm
        self.ppo_epochs = ppo_epochs
        self.batch_size = batch_size
        self.n_steps = n_steps
        self.seed = seed

        # Rilevamento del device (CPU o CUDA)
        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)

        # Impostazione dei seed per la riproducibilità
        torch.manual_seed(seed)
        np.random.seed(seed)

        # Inizializzazione delle reti neurali
        self.actor = ActorNetwork(self.obs_dim, self.action_dim, self.hidden_dim).to(self.device)
        self.critic = CriticNetwork(self.state_dim, self.hidden_dim).to(self.device)

        # Ottimizzatori Adam
        self.actor_optimizer = optim.Adam(self.actor.parameters(), lr=self.lr_actor, eps=1e-5)
        self.critic_optimizer = optim.Adam(self.critic.parameters(), lr=self.lr_critic, eps=1e-5)

        # Buffer di rollout
        self.buffer = MAPPORolloutBuffer(
            buffer_size=self.n_steps,
            num_uavs=self.num_uavs,
            obs_dim=self.obs_dim,
            state_dim=self.state_dim,
            device=self.device
        )

    def extract_agent_observations(self, raw_obs):
        """
        Estrae le osservazioni locali per ciascun drone dal vettore di stato raw.

        Args:
            raw_obs (np.ndarray): Vettore globale dell'ambiente.

        Returns:
            np.ndarray: Matrice delle osservazioni locali di forma (num_uavs, obs_dim).
        """
        raw_obs = np.array(raw_obs, dtype=np.float32).flatten()
        n = self.num_uavs
        m = self.num_obstacles

        # Parsing del vettore raw [uav_0, ..., uav_{N-1}, target, ostacoli]
        uavs = [raw_obs[2 * i : 2 * i + 2] for i in range(n)]
        target = raw_obs[2 * n : 2 * n + 2]
        obstacles = raw_obs[2 * n + 2 : 2 * n + 2 + 2 * m]

        # Costruzione del vettore per ciascun drone
        all_obs = []
        for i in range(n):
            obs_i = list(uavs[i]) + list(target) + list(obstacles)
            for j in range(n):
                if j != i:
                    obs_i.extend(list(uavs[j]))
            all_obs.append(obs_i)

        return np.array(all_obs, dtype=np.float32)

    def predict(self, obs, deterministic=True):
        """
        Interfaccia di inferenza compatibile con Stable-Baselines3.

        Args:
            obs: Osservazioni locali (num_uavs, obs_dim) o vettore globale raw.
            deterministic (bool): Se True, esegue l'azione con probabilità massima.

        Returns:
            tuple: (azioni scelte per tutti i droni, None).
        """
        obs_array = np.array(obs, dtype=np.float32)
        if obs_array.ndim == 1:
            if len(obs_array) == self.obs_dim and self.num_uavs == 1:
                # Singolo drone: l'osservazione raw coincide con quella locale
                agent_obs = obs_array.reshape(1, self.obs_dim)
            else:
                agent_obs = self.extract_agent_observations(obs_array)
        else:
            agent_obs = obs_array

        self.actor.eval()
        with torch.no_grad():
            obs_tensor = torch.tensor(agent_obs, dtype=torch.float32, device=self.device)
            actions, _ = self.actor.get_action(obs_tensor, deterministic=deterministic)
            actions = actions.cpu().numpy()

        # Restituisce formato compatibile (array 1D)
        return actions, None

    def get_actions_and_values(self, agent_obs, global_state):
        """
        Campiona le azioni dalla policy e calcola la stima di valore dallo stato globale.

        Args:
            agent_obs (np.ndarray): Osservazioni locali dei droni.
            global_state (np.ndarray): Stato globale per il Critic.

        Returns:
            tuple: (azioni, log_probs, valore stimato dallo stato).
        """
        self.actor.eval()
        self.critic.eval()
        with torch.no_grad():
            obs_tensor = torch.tensor(agent_obs, dtype=torch.float32, device=self.device)
            actions, log_probs = self.actor.get_action(obs_tensor, deterministic=False)

            state_tensor = torch.tensor(global_state, dtype=torch.float32, device=self.device).unsqueeze(0)
            value = self.critic(state_tensor).squeeze(-1)

        return (
            actions.cpu().numpy(),
            log_probs.cpu().numpy(),
            value.item()
        )

    def train_step(self):
        """
        Esegue l'aggiornamento dei gradienti con mini-batch SGD su Actor e Critic.

        Returns:
            dict: Valori medi delle loss di Actor, Critic ed entropia.
        """
        self.actor.train()
        self.critic.train()

        actor_losses = []
        critic_losses = []
        entropies = []

        batches = self.buffer.get_batches(self.batch_size)

        for _ in range(self.ppo_epochs):
            for batch in batches:
                # Aggiornamento dell'Actor con objective PPO clipped ed entropia
                new_log_probs, entropy = self.actor.evaluate_actions(
                    batch["actor_obs"], batch["actor_actions"]
                )

                ratio = torch.exp(new_log_probs - batch["actor_old_log_probs"])
                surr1 = ratio * batch["actor_advantages"]
                surr2 = torch.clamp(ratio, 1.0 - self.clip_param, 1.0 + self.clip_param) * batch["actor_advantages"]
                actor_loss = -torch.min(surr1, surr2).mean() - self.entropy_coef * entropy.mean()

                self.actor_optimizer.zero_grad()
                actor_loss.backward()
                nn.utils.clip_grad_norm_(self.actor.parameters(), self.max_grad_norm)
                self.actor_optimizer.step()

                # Aggiornamento del Critic con value loss clipped
                current_values = self.critic(batch["critic_states"]).squeeze(-1)
                value_pred_clipped = batch["critic_old_values"].squeeze(-1) + torch.clamp(
                    current_values - batch["critic_old_values"].squeeze(-1),
                    -self.clip_param,
                    self.clip_param
                )
                vf_loss1 = (current_values - batch["critic_returns"].squeeze(-1)) ** 2
                vf_loss2 = (value_pred_clipped - batch["critic_returns"].squeeze(-1)) ** 2
                critic_loss = 0.5 * torch.max(vf_loss1, vf_loss2).mean()

                self.critic_optimizer.zero_grad()
                critic_loss.backward()
                nn.utils.clip_grad_norm_(self.critic.parameters(), self.max_grad_norm)
                self.critic_optimizer.step()

                actor_losses.append(actor_loss.item())
                critic_losses.append(critic_loss.item())
                entropies.append(entropy.mean().item())

        return {
            "actor_loss": float(np.mean(actor_losses)),
            "critic_loss": float(np.mean(critic_losses)),
            "entropy": float(np.mean(entropies)),
        }

    def learn(self, env, total_timesteps=100000, verbose=1, log_interval=10, tensorboard_log=None):
        """
        Esegue il ciclo completo di addestramento su total_timesteps step di simulazione.

        Args:
            env: Istanza dell'ambiente di simulazione MultiUAVEnv.
            total_timesteps (int): Numero totale di passi di interazione.
            verbose (int): Livello di verbosità (0 o 1).
            log_interval (int): Frequenza di stampa delle metriche (in aggiornamenti).
            tensorboard_log (str, optional): Cartella di destinazione per i log TensorBoard.

        Returns:
            dict: Riepilogo delle metriche finali di addestramento.
        """
        start_time = time.time()
        obs, info = env.reset(seed=self.seed)

        # Inizializzazione di TensorBoard
        writer = None
        if tensorboard_log is not None and SummaryWriter is not None:
            tb_dir = os.path.join(tensorboard_log, f"MAPPO_{self.num_uavs}_UAV_{self.seed}")
            writer = SummaryWriter(log_dir=tb_dir)
            if verbose:
                print(f"TensorBoard attivo in: {tb_dir}")

        # Estrazione delle osservazioni locali e dello stato globale
        if hasattr(env, "get_all_agent_obs"):
            agent_obs = env.get_all_agent_obs()
            global_state = env.get_global_state()
        else:
            agent_obs = self.extract_agent_observations(obs)
            global_state = np.array(obs, dtype=np.float32)

        ep_rewards = []
        current_ep_reward = 0.0
        current_ep_steps = 0
        ep_successes = []

        total_steps = 0
        update_count = 0

        if verbose:
            drone_str = f"{self.num_uavs} dron{'e' if self.num_uavs == 1 else 'i'}"
            print(f"Inizio addestramento MAPPO per {drone_str} ({total_timesteps:,} step totali)")
            print(f"Dimensione Input: Actor={self.obs_dim}, Critic={self.state_dim} | Device: {self.device}")

        # Ciclo principale di campionamento e interazione
        while total_steps < total_timesteps:
            self.buffer.reset()

            for step_in_buffer in range(self.n_steps):
                actions, log_probs, value = self.get_actions_and_values(agent_obs, global_state)

                # Adattamento del formato dell'azione per l'ambiente
                env_action = actions if self.num_uavs > 1 else actions[0]

                next_obs, reward, terminated, truncated, info = env.step(env_action)
                done = terminated or truncated

                # Memorizzazione della transizione nel buffer di rollout
                self.buffer.add(agent_obs, global_state, actions, log_probs, reward, done, value)

                current_ep_reward += reward
                current_ep_steps += 1
                total_steps += 1

                if done:
                    ep_rewards.append(current_ep_reward)
                    is_success = info.get("success", terminated)
                    ep_successes.append(1.0 if is_success else 0.0)

                    current_ep_reward = 0.0
                    current_ep_steps = 0
                    obs, info = env.reset()
                    if hasattr(env, "get_all_agent_obs"):
                        agent_obs = env.get_all_agent_obs()
                        global_state = env.get_global_state()
                    else:
                        agent_obs = self.extract_agent_observations(obs)
                        global_state = np.array(obs, dtype=np.float32)
                else:
                    obs = next_obs
                    if hasattr(env, "get_all_agent_obs"):
                        agent_obs = env.get_all_agent_obs()
                        global_state = env.get_global_state()
                    else:
                        agent_obs = self.extract_agent_observations(obs)
                        global_state = np.array(obs, dtype=np.float32)

                if total_steps >= total_timesteps:
                    break

            # Bootstrap dell'ultimo valore
            with torch.no_grad():
                state_tensor = torch.tensor(global_state, dtype=torch.float32, device=self.device).unsqueeze(0)
                last_value = self.critic(state_tensor).squeeze(-1).item()

            self.buffer.compute_returns_and_advantages(
                last_value, done, self.gamma, self.gae_lambda
            )

            # Aggiornamento dei pesi delle reti neurali
            losses = self.train_step()
            update_count += 1

            # Logging periodico a terminale e su TensorBoard
            if update_count % log_interval == 0 or total_steps >= total_timesteps:
                elapsed = time.time() - start_time
                fps = total_steps / elapsed if elapsed > 0 else 0
                avg_rew = np.mean(ep_rewards[-100:]) if ep_rewards else 0.0
                succ_rate = (np.mean(ep_successes[-100:]) * 100) if ep_successes else 0.0

                if verbose:
                    print(
                        f"[Step {total_steps:>7}/{total_timesteps}] "
                        f"FPS: {fps:>5.0f} | "
                        f"Reward Medio: {avg_rew:>7.2f} | "
                        f"Success Rate: {succ_rate:>5.1f}% | "
                        f"Loss Actor: {losses['actor_loss']:>6.3f} | "
                        f"Loss Critic: {losses['critic_loss']:>6.3f}"
                    )

                if writer is not None:
                    writer.add_scalar("rollout/ep_rew_mean", avg_rew, total_steps)
                    writer.add_scalar("rollout/success_rate", succ_rate, total_steps)
                    writer.add_scalar("train/actor_loss", losses["actor_loss"], total_steps)
                    writer.add_scalar("train/critic_loss", losses["critic_loss"], total_steps)
                    writer.add_scalar("train/entropy", losses["entropy"], total_steps)
                    writer.add_scalar("time/fps", fps, total_steps)

        if writer is not None:
            writer.flush()
            writer.close()

        if verbose:
            total_elapsed = time.time() - start_time
            print(f"Addestramento completato in {total_elapsed:.2f}s ({total_steps / total_elapsed:.0f} FPS totali)")

        return {
            "total_timesteps": total_steps,
            "elapsed_time": time.time() - start_time,
            "episodes": len(ep_rewards),
            "mean_reward": float(np.mean(ep_rewards[-100:])) if ep_rewards else 0.0,
            "success_rate": float(np.mean(ep_successes[-100:])) if ep_successes else 0.0,
        }

    def evaluate(self, env, n_eval_episodes=10, deterministic=True):
        """
        Valuta le prestazioni della policy addestrata su un dato numero di episodi.

        Args:
            env: Ambiente di simulazione.
            n_eval_episodes (int): Numero di episodi di valutazione.
            deterministic (bool): Se True, utilizza inferenza deterministica.

        Returns:
            tuple: (reward medio, deviazione standard reward, success rate percentuale, passi medi).
        """
        rewards = []
        successes = []
        steps_list = []

        # Loop di valutazione sugli episodi di test
        for _ in range(n_eval_episodes):
            obs, info = env.reset()
            done = False
            ep_reward = 0.0
            ep_steps = 0

            while not done:
                actions, _ = self.predict(obs, deterministic=deterministic)
                env_action = actions if self.num_uavs > 1 else actions[0]
                obs, reward, terminated, truncated, info = env.step(env_action)
                ep_reward += reward
                ep_steps += 1
                done = terminated or truncated

            rewards.append(ep_reward)
            is_success = info.get("success", terminated)
            successes.append(1.0 if is_success else 0.0)
            steps_list.append(ep_steps)

        return (
            float(np.mean(rewards)),
            float(np.std(rewards)),
            float(np.mean(successes) * 100.0),
            float(np.mean(steps_list))
        )

    def save(self, filepath):
        """
        Salva i pesi delle reti neurali e gli iperparametri dell'agente MAPPO in un file .pt.

        Args:
            filepath (str): Percorso del checkpoint da salvare.
        """
        if not filepath.endswith(".pt"):
            filepath = filepath + ".pt"

        save_dict = {
            "num_uavs": self.num_uavs,
            "obs_dim": self.obs_dim,
            "state_dim": self.state_dim,
            "action_dim": self.action_dim,
            "grid_size": self.grid_size,
            "num_obstacles": self.num_obstacles,
            "hidden_dim": self.hidden_dim,
            "actor_state_dict": self.actor.state_dict(),
            "critic_state_dict": self.critic.state_dict(),
            "actor_optimizer": self.actor_optimizer.state_dict(),
            "critic_optimizer": self.critic_optimizer.state_dict(),
            "hyperparams": {
                "lr_actor": self.lr_actor,
                "lr_critic": self.lr_critic,
                "gamma": self.gamma,
                "gae_lambda": self.gae_lambda,
                "clip_param": self.clip_param,
                "entropy_coef": self.entropy_coef,
                "value_loss_coef": self.value_loss_coef,
                "max_grad_norm": self.max_grad_norm,
                "ppo_epochs": self.ppo_epochs,
                "batch_size": self.batch_size,
                "n_steps": self.n_steps,
            }
        }
        torch.save(save_dict, filepath)

    @classmethod
    def load(cls, filepath, device=None):
        """
        Carica un checkpoint salvato e ricostruisce l'agente MAPPO.

        Args:
            filepath (str): Percorso del file .pt.
            device (str, optional): Device su cui caricare il modello.

        Returns:
            MAPPO: Istanza dell'agente con pesi e iperparametri ripristinati.
        """
        if not filepath.endswith(".pt"):
            filepath = filepath + ".pt"

        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File modello non trovato: {filepath}")

        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"

        checkpoint = torch.load(filepath, map_location=device)

        agent = cls(
            num_uavs=checkpoint["num_uavs"],
            obs_dim=checkpoint["obs_dim"],
            state_dim=checkpoint["state_dim"],
            action_dim=checkpoint["action_dim"],
            grid_size=checkpoint.get("grid_size", 10),
            num_obstacles=checkpoint.get("num_obstacles", 4),
            hidden_dim=checkpoint.get("hidden_dim", 128),
            device=device,
            **checkpoint.get("hyperparams", {})
        )

        agent.actor.load_state_dict(checkpoint["actor_state_dict"])
        agent.critic.load_state_dict(checkpoint["critic_state_dict"])
        if "actor_optimizer" in checkpoint:
            agent.actor_optimizer.load_state_dict(checkpoint["actor_optimizer"])
        if "critic_optimizer" in checkpoint:
            agent.critic_optimizer.load_state_dict(checkpoint["critic_optimizer"])

        return agent
