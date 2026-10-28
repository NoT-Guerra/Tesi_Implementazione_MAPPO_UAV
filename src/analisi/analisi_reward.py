"""
Script di analisi diagnostica per la scomposizione delle componenti di Reward.

Permette di isolare ed esaminare separatamente:
- Bonus per atterraggio all'hangar (+100 per drone)
- Penalità temporale per passi in volo (-1 per drone a step)
- Penalità per collisioni tra droni (-20 per scontro)
- Penalità per collisioni con ostacoli montuosi (-10 per scontro)
- Penalità per tentativi di uscita dai bordi della mappa (-10 per scontro)
"""

import os
import sys
import argparse
import csv
import numpy as np

# Risoluzione dinamica dei percorsi
ANALISI_DIR = os.path.abspath(os.path.dirname(__file__))
SRC_DIR = os.path.abspath(os.path.join(ANALISI_DIR, ".."))
PROJECT_ROOT = os.path.abspath(os.path.join(SRC_DIR, ".."))

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from env import MultiUAVEnv
from mappo import MAPPO
from stable_baselines3 import PPO


class InstrumentedMultiUAVEnv(MultiUAVEnv):
    """
    Sottoclasse di MultiUAVEnv che traccia e disaccoppia analiticamente
    ciascuna delle 5 componenti della funzione di reward durante ogni step.
    """
    def reset(self, seed=None, options=None):
        obs, info = super().reset(seed=seed, options=options)
        self.ep_bonus_landing = 0.0
        self.ep_penalty_step = 0.0
        self.ep_penalty_drone_collision = 0.0
        self.ep_penalty_obstacle = 0.0
        self.ep_penalty_boundary = 0.0
        self.ep_drone_collisions_count = 0
        self.ep_obstacle_collisions_count = 0
        self.ep_boundary_collisions_count = 0
        return obs, info

    def step(self, action):
        self.step_count += 1
        rewards = 0.0
        ind_rewards = [0.0] * self.num_uavs

        actions = np.array(action, dtype=int).flatten()
        new_locations = [np.copy(loc) for loc in self._uav_locations]

        step_bonus_landing = 0.0
        step_penalty_step = 0.0
        step_penalty_drone_collision = 0.0
        step_penalty_obstacle = 0.0
        step_penalty_boundary = 0.0

        # Movimento candidato e controllo bordi/ostacoli
        for i in range(self.num_uavs):
            if self._arrived[i]:
                new_locations[i] = self._target_location
                continue

            act = int(actions[i])
            direction = self._action_to_direction[act]
            candidate_pos = self._uav_locations[i] + direction

            # Controllo bordi mappa
            if np.any(candidate_pos < 0) or np.any(candidate_pos >= self.size):
                rewards -= 10.0
                ind_rewards[i] -= 10.0
                step_penalty_boundary += 10.0
                self.ep_boundary_collisions_count += 1
                new_locations[i] = self._uav_locations[i]
            # Controllo ostacoli montuosi
            elif any(np.array_equal(candidate_pos, ob) for ob in self._obstacles):
                rewards -= 10.0
                ind_rewards[i] -= 10.0
                step_penalty_obstacle += 10.0
                self.ep_obstacle_collisions_count += 1
                new_locations[i] = self._uav_locations[i]
            else:
                new_locations[i] = candidate_pos

        # Controllo collisioni reciproche tra droni (Vertex ed Edge swap)
        for i in range(self.num_uavs):
            for j in range(i + 1, self.num_uavs):
                if self._arrived[i] and self._arrived[j]:
                    continue

                vertex_collision = (
                    np.array_equal(new_locations[i], new_locations[j])
                    and not np.array_equal(new_locations[i], self._target_location)
                )

                edge_collision = (
                    not self._arrived[i] and not self._arrived[j]
                    and np.array_equal(new_locations[i], self._uav_locations[j])
                    and np.array_equal(new_locations[j], self._uav_locations[i])
                )

                if vertex_collision or edge_collision:
                    rewards -= 20.0
                    ind_rewards[i] -= 10.0
                    ind_rewards[j] -= 10.0
                    step_penalty_drone_collision += 20.0
                    self.ep_drone_collisions_count += 1
                    new_locations[i] = self._uav_locations[i]
                    new_locations[j] = self._uav_locations[j]

        # Aggiornamento posizioni, bonus arrivo e penalità temporale di volo
        for i in range(self.num_uavs):
            self._uav_locations[i] = np.clip(new_locations[i], 0, self.size - 1)

            if not self._arrived[i]:
                if np.array_equal(self._uav_locations[i], self._target_location):
                    self._arrived[i] = True
                    rewards += 100.0
                    ind_rewards[i] += 100.0
                    step_bonus_landing += 100.0
                else:
                    rewards -= 1.0
                    ind_rewards[i] -= 1.0
                    step_penalty_step += 1.0

        self._last_ind_rewards = ind_rewards
        self.ep_bonus_landing += step_bonus_landing
        self.ep_penalty_step += step_penalty_step
        self.ep_penalty_drone_collision += step_penalty_drone_collision
        self.ep_penalty_obstacle += step_penalty_obstacle
        self.ep_penalty_boundary += step_penalty_boundary

        terminated = all(self._arrived)
        truncated = self.step_count >= self.max_steps

        observation = self._get_obs()
        info = self._get_info()
        info["breakdown"] = {
            "bonus_landing": self.ep_bonus_landing,
            "penalty_step": -self.ep_penalty_step,
            "penalty_drone_collision": -self.ep_penalty_drone_collision,
            "penalty_obstacle": -self.ep_penalty_obstacle,
            "penalty_boundary": -self.ep_penalty_boundary,
            "drone_collisions_count": self.ep_drone_collisions_count,
            "obstacle_collisions_count": self.ep_obstacle_collisions_count,
            "boundary_collisions_count": self.ep_boundary_collisions_count,
            "arrived_count": sum(self._arrived)
        }

        return observation, rewards, terminated, truncated, info


def evaluate_breakdown(model, algo, env, n_episodes=100):
    """
    Valuta una policy raccogliendo le statistiche disaggregate sulle componenti del reward.
    """
    total_rewards = []
    bonus_landings = []
    penalty_steps = []
    penalty_drone_cols = []
    penalty_obstacles = []
    penalty_boundaries = []
    drone_col_counts = []
    obs_col_counts = []
    bnd_col_counts = []
    arrived_counts = []
    steps_list = []
    successes = []

    for _ in range(n_episodes):
        obs, info = env.reset()
        done = False
        ep_rew = 0.0

        while not done:
            action, _ = model.predict(obs, deterministic=True)
            if algo.lower() == "mappo":
                env_action = action if env.num_uavs > 1 else (action[0] if hasattr(action, "__len__") else action)
            else:
                env_action = action

            obs, r, term, trunc, info = env.step(env_action)
            ep_rew += r
            done = term or trunc

        bd = info["breakdown"]
        total_rewards.append(ep_rew)
        bonus_landings.append(bd["bonus_landing"])
        penalty_steps.append(bd["penalty_step"])
        penalty_drone_cols.append(bd["penalty_drone_collision"])
        penalty_obstacles.append(bd["penalty_obstacle"])
        penalty_boundaries.append(bd["penalty_boundary"])
        drone_col_counts.append(bd["drone_collisions_count"])
        obs_col_counts.append(bd["obstacle_collisions_count"])
        bnd_col_counts.append(bd["boundary_collisions_count"])
        arrived_counts.append(bd["arrived_count"])
        steps_list.append(env.step_count)
        successes.append(1.0 if info.get("success", term) else 0.0)

    return {
        "reward_mean": float(np.mean(total_rewards)),
        "reward_std": float(np.std(total_rewards)),
        "bonus_landing_mean": float(np.mean(bonus_landings)),
        "penalty_step_mean": float(np.mean(penalty_steps)),
        "penalty_drone_col_mean": float(np.mean(penalty_drone_cols)),
        "penalty_obs_mean": float(np.mean(penalty_obstacles)),
        "penalty_bnd_mean": float(np.mean(penalty_boundaries)),
        "drone_col_count_mean": float(np.mean(drone_col_counts)),
        "obs_col_count_mean": float(np.mean(obs_col_counts)),
        "bnd_col_count_mean": float(np.mean(bnd_col_counts)),
        "arrived_count_mean": float(np.mean(arrived_counts)),
        "steps_mean": float(np.mean(steps_list)),
        "success_rate": float(np.mean(successes) * 100.0),
    }


def parse_args():
    parser = argparse.ArgumentParser(description="Analisi e Scomposizione Dettagliata del Reward (Multi-UAV)")
    parser.add_argument("--uavs", type=int, default=4, help="Numero di droni (default: 4)")
    parser.add_argument("--seeds", type=str, default="42,123,999", help="Semi da analizzare separati da virgola (default: 42,123,999)")
    parser.add_argument("--mode", type=str, default="both", choices=["both", "mappo", "ppo"], help="Algoritmi da analizzare (default: both)")
    parser.add_argument("--models-dir", type=str, default=os.path.join(PROJECT_ROOT, "models", "EXTENDED_4UAV"), help="Cartella contenente i checkpoint dei modelli")
    parser.add_argument("--episodes", type=int, default=100, help="Numero di episodi di test per seed (default: 100)")
    parser.add_argument("--save-csv", type=str, default=None, help="Percorso opzionale in cui salvare la tabella CSV riassuntiva")
    return parser.parse_args()


def main():
    args = parse_args()
    seeds = [int(s.strip()) for s in args.seeds.split(",") if s.strip()]
    algos = ["mappo", "ppo"] if args.mode == "both" else [args.mode.lower()]

    env = InstrumentedMultiUAVEnv(size=10, num_obstacles=4, num_uavs=args.uavs)

    print(f"\nAnalisi Scomposizione Reward ({args.uavs} UAV | {args.episodes} episodi/seed | Semi: {seeds})\n")

    csv_rows = []

    for algo in algos:
        algo_results = []
        for s in seeds:
            if algo == "mappo":
                model_file = os.path.join(args.models_dir, f"mappo_uav_{args.uavs}_{s}.pt")
                if not os.path.exists(model_file):
                    print(f"Checkpoint MAPPO non trovato per seed {s}: {model_file}")
                    continue
                model = MAPPO.load(model_file)
            else:
                model_file = os.path.join(args.models_dir, f"ppo_multi_uav_{args.uavs}_{s}.zip")
                if not os.path.exists(model_file):
                    print(f"Checkpoint PPO non trovato per seed {s}: {model_file}")
                    continue
                model = PPO.load(model_file)

            res = evaluate_breakdown(model, algo, env, n_episodes=args.episodes)
            res["seed"] = s
            res["algo"] = algo.upper()
            algo_results.append(res)

            csv_rows.append({
                "Algoritmo": algo.upper(),
                "Seed": s,
                "Reward_Totale": f"{res['reward_mean']:.2f}",
                "Success_Rate": f"{res['success_rate']:.1f}%",
                "Passi_Medi": f"{res['steps_mean']:.1f}",
                "Droni_Arrivati": f"{res['arrived_count_mean']:.2f}",
                "Bonus_Atterraggi": f"{res['bonus_landing_mean']:.2f}",
                "Penalita_Passi": f"{res['penalty_step_mean']:.2f}",
                "Penalita_Collisioni_Droni": f"{res['penalty_drone_col_mean']:.2f}",
                "Scontri_Droni_Medi": f"{res['drone_col_count_mean']:.1f}",
                "Penalita_Ostacoli": f"{res['penalty_obs_mean']:.2f}",
                "Scontri_Ostacoli_Medi": f"{res['obs_col_count_mean']:.1f}",
                "Penalita_Bordi": f"{res['penalty_bnd_mean']:.2f}",
                "Uscite_Bordi_Medi": f"{res['bnd_col_count_mean']:.1f}"
            })

        if algo_results:
            print(f"\nSintesi Aggregata {algo.upper()} ({len(algo_results)} SEMI) ---")
            print(f"Reward Totale:              {np.mean([r['reward_mean'] for r in algo_results]):.1f} \u00b1 {np.std([r['reward_mean'] for r in algo_results]):.1f}")
            print(f"Success Rate:               {np.mean([r['success_rate'] for r in algo_results]):.1f}%")
            print(f"Passi Medi:                 {np.mean([r['steps_mean'] for r in algo_results]):.1f}")
            print(f"Droni Atterrati medi:       {np.mean([r['arrived_count_mean'] for r in algo_results]):.2f} / {args.uavs}")
            print(f"+ Bonus Atterraggi (+100):  +{np.mean([r['bonus_landing_mean'] for r in algo_results]):.1f}")
            print(f"- Penalita Passi (-1/drone):{np.mean([r['penalty_step_mean'] for r in algo_results]):.1f}")
            print(f"- Collisioni Droni (-20):   {np.mean([r['penalty_drone_col_mean'] for r in algo_results]):.1f} (Media scontri: {np.mean([r['drone_col_count_mean'] for r in algo_results]):.1f})")
            print(f"- Collisioni Ostacoli (-10):{np.mean([r['penalty_obs_mean'] for r in algo_results]):.1f} (Media scontri: {np.mean([r['obs_col_count_mean'] for r in algo_results]):.1f})")
            print(f"- Uscita Bordi Mappa (-10): {np.mean([r['penalty_bnd_mean'] for r in algo_results]):.1f} (Media uscite: {np.mean([r['bnd_col_count_mean'] for r in algo_results]):.1f})")

    env.close()

    if args.save_csv and csv_rows:
        os.makedirs(os.path.dirname(os.path.abspath(args.save_csv)), exist_ok=True)
        with open(args.save_csv, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(csv_rows[0].keys()))
            writer.writeheader()
            for r in csv_rows:
                writer.writerow(r)
        print(f"\nTabella di scomposizione salvata in: {args.save_csv}")

    print("\nAnalisi completata")


if __name__ == "__main__":
    main()
