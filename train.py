"""
Script di addestramento parametrico per MAPPO (Multi-Agent PPO) e PPO baseline.
Consente di addestrare a partire da un singolo drone (N=1) fino a N droni (2, 3, 4).
"""

import argparse
from env import MultiUAVEnv
from mappo import MAPPO


def parse_args():
    parser = argparse.ArgumentParser(description="Addestramento MAPPO Parametrico per Flotta UAV")
    parser.add_argument("--uavs", type=int, default=1, help="Numero di droni")
    parser.add_argument("--timesteps", type=int, default=200000, help="Step totali di simulazione")
    parser.add_argument("--algo", type=str, default="mappo", choices=["mappo", "ppo"], help="Algoritmo: mappo o ppo")
    parser.add_argument("--size", type=int, default=10, help="Dimensione della griglia NxN")
    parser.add_argument("--obstacles", type=int, default=4, help="Numero di ostacoli/montagne")
    parser.add_argument("--seed", type=int, default=42, help="Seed casuale per riproducibilità")
    return parser.parse_args()


def train(num_uavs=1, total_timesteps=200000, algo="mappo", size=10, num_obstacles=4, seed=42):
    drone_label = f"{num_uavs} dron{'e' if num_uavs == 1 else 'i'}"
    print(f" AVVIO ADDESTRAMENTO {algo.upper()} SU {drone_label.upper()} (Griglia {size}x{size})")
    print(f" Timesteps totali: {total_timesteps:,} | Ostacoli: {num_obstacles} | Seed: {seed}")


    # crea l'ambiente multi-uav senza render per velocizzare
    env = MultiUAVEnv(size=size, num_obstacles=num_obstacles, num_uavs=num_uavs)

    if algo.lower() == "mappo":
        # inizializza mappo
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
        model.learn(env, total_timesteps=total_timesteps, verbose=1, log_interval=10)
        print("Addestramento MAPPO completato!")

        # salva il modello in formato .pt
        model_name = f"mappo_uav_{num_uavs}_{seed}"
        model.save(model_name)
        print(f"Modello salvato come '{model_name}.pt'")

        # valuta la performance su 100 episodi di test
        print("\nValutazione del modello su 100 episodi...")
        mean_reward, std_reward, success_rate, avg_steps = model.evaluate(env, n_eval_episodes=100)
        print(f"Mean Reward:  {mean_reward:.2f} +/- {std_reward:.2f}")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Passi Medi:   {avg_steps:.1f} step")

    else:
        # fallback su ppo di stable-baselines3
        from stable_baselines3 import PPO
        from stable_baselines3.common.evaluation import evaluate_policy

        model = PPO("MlpPolicy", env, seed=seed, verbose=1, tensorboard_log="./ppo_uav_tensorboard/")
        print("Inizio dell'addestramento PPO centralizzato...")
        model.learn(total_timesteps=total_timesteps)
        print("Addestramento PPO completato!")

        model_name = f"ppo_multi_uav_{num_uavs}_{seed}"
        model.save(model_name)
        print(f"Modello salvato come '{model_name}.zip'")

        mean_reward, std_reward = evaluate_policy(model, env, n_eval_episodes=10)
        print(f"Mean reward su 10 episodi: {mean_reward:.2f} +/- {std_reward:.2f}")

    env.close()

if __name__ == "__main__":
    args = parse_args()
    train(
        num_uavs=args.uavs,
        total_timesteps=args.timesteps,
        algo=args.algo,
        size=args.size,
        num_obstacles=args.obstacles,
        seed=args.seed
    )
