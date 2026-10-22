"""
Script di addestramento parametrico per MAPPO (Multi-Agent PPO) e PPO baseline.

Permette l'addestramento della flotta di UAV sia in configurazione a singolo drone (N=1)
sia in scenari multi-agente cooperativi (N >= 2), supportando il logging su TensorBoard
e la valutazione automatica delle prestazioni al termine del training.
"""

import os
import argparse
from env import MultiUAVEnv
from mappo import MAPPO


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_SAVE_DIR = os.path.join(PROJECT_ROOT, "models")
DEFAULT_TB_LOG = os.path.join(PROJECT_ROOT, "tensorboard_logs")


def parse_args():
    """
    Esegue il parsing degli argomenti da riga di comando per la configurazione dell'addestramento.

    Returns:
        argparse.Namespace: Parametri configurati dall'utente o valori di default.
    """
    parser = argparse.ArgumentParser(description="Addestramento MAPPO Parametrico per Flotta UAV")
    parser.add_argument("--uavs", type=int, default=1, help="Numero di droni")
    parser.add_argument("--timesteps", type=int, default=200000, help="Step totali di simulazione")
    parser.add_argument("--algo", type=str, default="mappo", choices=["mappo", "ppo"], help="Algoritmo: mappo o ppo")
    parser.add_argument("--size", type=int, default=10, help="Dimensione della griglia NxN")
    parser.add_argument("--obstacles", type=int, default=4, help="Numero di ostacoli/montagne")
    parser.add_argument("--seed", type=int, default=42, help="Seed casuale per riproducibilità")
    parser.add_argument("--tb-log", type=str, default=DEFAULT_TB_LOG, help="Directory log TensorBoard")
    parser.add_argument("--save-dir", type=str, default=DEFAULT_SAVE_DIR, help="Cartella salvataggio modelli")
    return parser.parse_args()


def train(num_uavs=1, total_timesteps=200000, algo="mappo", size=10, num_obstacles=4, seed=42, tb_log=DEFAULT_TB_LOG, save_dir=DEFAULT_SAVE_DIR):
    """
    Funzione principale per l'addestramento e la valutazione della policy (MAPPO o PPO).

    Args:
        num_uavs (int): Numero di droni cooperanti nell'ambiente.
        total_timesteps (int): Numero totale di passi di interazione con l'ambiente.
        algo (str): Algoritmo RL da impiegare ('mappo' o 'ppo').
        size (int): Dimensione della griglia dell'ambiente (size x size).
        num_obstacles (int): Numero di ostacoli posizionati nell'ambiente.
        seed (int): Seed pseudo-casuale per garantire la riproducibilità.
        tb_log (str): Percorso della directory per i grafici e le metriche TensorBoard.
        save_dir (str): Percorso della cartella in cui salvare i pesi del modello.
    """
    drone_label = f"{num_uavs} dron{'e' if num_uavs == 1 else 'i'}"
    print(f" AVVIO ADDESTRAMENTO {algo.upper()} SU {drone_label.upper()} (Griglia {size}x{size})")
    print(f" Timesteps totali: {total_timesteps:,} | Ostacoli: {num_obstacles} | Seed: {seed} | TensorBoard: {tb_log}")

    # Inizializzazione dell'ambiente di simulazione Multi-UAV
    env = MultiUAVEnv(size=size, num_obstacles=num_obstacles, num_uavs=num_uavs)

    if algo.lower() == "mappo":
        # Inizializzazione dell'architettura MAPPO
        model = MAPPO(
            num_uavs=num_uavs,
            grid_size=size,
            num_obstacles=num_obstacles,
            hidden_dim=128,
            lr_actor=3e-4,
            lr_critic=1e-3,
            n_steps=1024,
            batch_size=64,
            seed=seed
        )

        print("Inizio dell'addestramento MAPPO...")
        # Ciclo di addestramento con logging periodico su TensorBoard
        model.learn(env, total_timesteps=total_timesteps, verbose=1, log_interval=10, tensorboard_log=tb_log)
        print("Addestramento MAPPO completato!")

        # Salvataggio dei pesi del modello e della configurazione (.pt)
        os.makedirs(save_dir, exist_ok=True)
        model_name = f"mappo_uav_{num_uavs}_{seed}"
        model_path = os.path.join(save_dir, model_name)
        model.save(model_path)
        print(f"Modello salvato come '{model_path}.pt'")

        # Valutazione quantitativa delle prestazioni su 100 episodi di test
        print("\nValutazione del modello su 100 episodi...")
        mean_reward, std_reward, success_rate, avg_steps = model.evaluate(env, n_eval_episodes=100)
        print(f"Mean Reward:  {mean_reward:.2f} +/- {std_reward:.2f}")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Passi Medi:   {avg_steps:.1f} step")

    else:
        # Fallback sull'algoritmo baseline PPO centralizzato (Stable-Baselines3)
        from stable_baselines3 import PPO
        from stable_baselines3.common.evaluation import evaluate_policy

        # Configurazione del modello PPO standard con policy MLP centralizzata
        model = PPO("MlpPolicy", env, seed=seed, verbose=1, tensorboard_log=tb_log)
        print("Inizio dell'addestramento PPO centralizzato...")
        # Avvio dell'addestramento di baseline
        model.learn(total_timesteps=total_timesteps, tb_log_name=f"PPO_{num_uavs}_UAV_{seed}")
        print("Addestramento PPO completato!")

        # Salvataggio del modello PPO compresso (.zip)
        os.makedirs(save_dir, exist_ok=True)
        model_name = f"ppo_multi_uav_{num_uavs}_{seed}"
        model_path = os.path.join(save_dir, model_name)
        model.save(model_path)
        print(f"Modello salvato come '{model_path}.zip'")

        # Valutazione empirica della policy PPO su 100 episodi
        mean_reward, std_reward = evaluate_policy(model, env, n_eval_episodes=100)
        print(f"Mean reward su 100 episodi: {mean_reward:.2f} +/- {std_reward:.2f}")

    # Chiusura e rilascio delle risorse dell'ambiente
    env.close()


if __name__ == "__main__":
    # Parsing degli argomenti da CLI ed esecuzione della pipeline di addestramento
    args = parse_args()
    train(
        num_uavs=args.uavs,
        total_timesteps=args.timesteps,
        algo=args.algo,
        size=args.size,
        num_obstacles=args.obstacles,
        seed=args.seed,
        tb_log=args.tb_log,
        save_dir=args.save_dir
    )
