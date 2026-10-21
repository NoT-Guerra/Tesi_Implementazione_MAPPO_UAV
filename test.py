"""
Script di simulazione visiva (GUI Pygame) per testare le policy addestrate (MAPPO o PPO).
Supporta qualsiasi numero di droni (N=1, 2, 3, 4, 5, ...).
"""

import time
import argparse
import os
from env import MultiUAVEnv
from mappo import MAPPO


def parse_args():
    parser = argparse.ArgumentParser(description="Test e Simulazione Visiva Policy UAV")
    parser.add_argument("--uavs", type=int, default=1, help="Numero di droni")
    parser.add_argument("--algo", type=str, default="mappo", choices=["mappo", "ppo"], help="Algoritmo da testare: mappo o ppo")
    parser.add_argument("--episodes", type=int, default=10, help="Numero di episodi di test")
    parser.add_argument("--delay", type=float, default=0.08, help="Pausa in secondi tra passi per la grafica")
    parser.add_argument("--size", type=int, default=10, help="Dimensione griglia")
    parser.add_argument("--obstacles", type=int, default=4, help="Numero di ostacoli")
    parser.add_argument("--seed", type=int, default=42, help="Seed")
    return parser.parse_args()


def load_model(algo, num_uavs, seed=42):
    """
    Carica il modello MAPPO o PPO cercando i pattern di salvataggio standard.
    """
    if algo.lower() == "mappo":
        names_to_try = [
            f"mappo_uav_{num_uavs}_{seed}.pt",
            f"mappo_uav_{num_uavs}.pt",
        ]
        for name in names_to_try:
            if os.path.exists(name):
                print(f"[+] Caricamento modello MAPPO da: {name}")
                return MAPPO.load(name), "mappo", name

        # se non trova mappo prova il fallback su ppo
        fallback_names = [f"ppo_multi_uav_{num_uavs}_{seed}.zip", f"ppo_multi_uav_{num_uavs}.zip"]
        for fb in fallback_names:
            if os.path.exists(fb):
                from stable_baselines3 import PPO
                print(f"[!] Modello MAPPO non trovato. Fallback automatico su modello PPO: {fb}")
                return PPO.load(fb), "ppo", fb

        raise FileNotFoundError(f"Nessun modello trovato per N={num_uavs}. Esegui prima train.py!")

    else:
        from stable_baselines3 import PPO
        names_to_try = [
            f"ppo_multi_uav_{num_uavs}_{seed}",
            f"ppo_multi_uav_{num_uavs}",
            f"ppo_single_uav" if num_uavs == 1 else ""
        ]
        for name in names_to_try:
            if not name:
                continue
            zip_name = name if name.endswith(".zip") else f"{name}.zip"
            if os.path.exists(zip_name):
                print(f"[+] Caricamento modello PPO da: {zip_name}")
                return PPO.load(name), "ppo", zip_name

        raise FileNotFoundError(f"Modello PPO non trovato per N={num_uavs}. Esegui prima train.py!")


def main():
    args = parse_args()
    num_uavs = args.uavs
    size = args.size
    num_obstacles = args.obstacles
    seed = args.seed

    print(f"\n{'='*70}")
    drone_str = f"{num_uavs} dron{'e' if num_uavs == 1 else 'i'}"
    print(f" SIMULAZIONE VISIVA FLOTTA UAV: {drone_str.upper()} ({args.algo.upper()})")
    print(f"{'='*70}\n")

    # carica il modello
    model, loaded_algo, model_path = load_model(args.algo, num_uavs, seed)

    # crea l'ambiente con rendering grafico pygame
    env = MultiUAVEnv(
        render_mode="human",
        size=size,
        num_obstacles=num_obstacles,
        num_uavs=num_uavs
    )

    print(f"Avvio della simulazione per {args.episodes} episodi...")
    successes = 0
    total_rewards = []

    for episode in range(args.episodes):
        obs, info = env.reset()
        done = False
        truncated = False
        total_reward = 0.0
        step = 0

        print(f"\n--- Episodio {episode + 1}/{args.episodes} ---")

        while not done and not truncated:
            action, _states = model.predict(obs, deterministic=True)
            
            # adatta l'azione per l'ambiente
            env_action = action if num_uavs > 1 else (action[0] if hasattr(action, "__len__") else action)

            obs, reward, terminated, truncated, info = env.step(env_action)
            total_reward += reward
            step += 1

            time.sleep(args.delay)

            done = terminated

        is_success = info.get("success", done)
        if is_success:
            successes += 1
            print(f" Obiettivo RAGGIUNTO in {step} step! Reward totale: {total_reward:.2f}")
        elif truncated:
            print(f" Obiettivo NON raggiunto (timeout step massimi). Reward totale: {total_reward:.2f}")
        else:
            print(f" Episodio terminato in {step} step. Reward totale: {total_reward:.2f}")

        total_rewards.append(total_reward)

    env.close()

    print(f" RIEPILOGO TEST ({drone_str.upper()} - {loaded_algo.upper()})")
    print(f"[*] Success Rate: {successes}/{args.episodes} ({(successes / args.episodes) * 100:.1f}%)")
    print(f"[*] Reward Medio: {sum(total_rewards)/len(total_rewards):.2f}")

if __name__ == "__main__":
    main()
