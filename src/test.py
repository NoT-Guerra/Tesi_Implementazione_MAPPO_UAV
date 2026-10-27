"""
Script di simulazione visiva (GUI Pygame) per testare le policy addestrate (MAPPO o PPO).
Supporta qualsiasi numero di droni (N=1, 2, 3, 4, ecc.) e visualizza in tempo reale
la navigazione della flotta, monitorando success rate e reward complessivo.
"""

import time
import argparse
import os
from env import MultiUAVEnv
from mappo import MAPPO


def parse_args():
    """
    Esegue il parsing degli argomenti da riga di comando per la simulazione grafica.

    Returns:
        argparse.Namespace: Parametri di configurazione del test.
    """
    parser = argparse.ArgumentParser(description="Test e Simulazione Visiva Policy UAV")
    parser.add_argument("--uavs", type=int, default=1, help="Numero di droni")
    parser.add_argument("--algo", type=str, default="mappo", choices=["mappo", "ppo"], help="Algoritmo da testare: mappo o ppo")
    parser.add_argument("--episodes", type=int, default=10, help="Numero di episodi di test")
    parser.add_argument("--delay", type=float, default=0.08, help="Pausa in secondi tra passi per la grafica")
    parser.add_argument("--size", type=int, default=10, help="Dimensione griglia")
    parser.add_argument("--obstacles", type=int, default=4, help="Numero di ostacoli")
    parser.add_argument("--seed", type=int, default=42, help="Seed")
    parser.add_argument("--model-path", type=str, default=None, help="Percorso esplicito al file checkpoint (.pt o .zip)")
    parser.add_argument("--models-dir", type=str, default=None, help="Cartella contenente i modelli salvati (es. models/EXTENDED_4UAV)")
    return parser.parse_args()


def load_model(algo, num_uavs, seed=42, model_path=None, models_dir=None):
    """
    Carica il modello addestrato (MAPPO o PPO) ricercando i percorsi e pattern standard,
    inclusi models/EXTENDED_4UAV/ e models/SEED_*/.

    Args:
        algo (str): Algoritmo atteso ('mappo' o 'ppo').
        num_uavs (int): Numero di UAV per cui caricare la policy.
        seed (int): Seed utilizzato durante il salvataggio.
        model_path (str, optional): Percorso specifico fornito da CLI.
        models_dir (str, optional): Cartella modelli fornita da CLI.

    Returns:
        tuple: (modello caricato, nome algoritmo effettivo, percorso del file)
    """
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    base_models_dir = os.path.join(project_root, "models")

    # 1. Se l'utente specifica un percorso esatto
    if model_path:
        candidates = [
            model_path,
            os.path.join(project_root, model_path),
            f"{model_path}.pt",
            f"{model_path}.zip",
        ]
        for c in candidates:
            if os.path.exists(c):
                if c.endswith(".pt") or algo.lower() == "mappo":
                    print(f"[+] Caricamento modello MAPPO da: {c}")
                    return MAPPO.load(c), "mappo", c
                else:
                    from stable_baselines3 import PPO
                    print(f"[+] Caricamento modello PPO da: {c}")
                    return PPO.load(c), "ppo", c
        raise FileNotFoundError(f"File modello specificato non trovato: '{model_path}'")

    # 2. Directory di ricerca prioritarie
    search_dirs = []
    if models_dir:
        search_dirs.append(models_dir)
        search_dirs.append(os.path.join(project_root, models_dir))

    search_dirs.extend([
        os.path.join(base_models_dir, "EXTENDED_4UAV"),
        os.path.join(base_models_dir, f"SEED_{seed}"),
        base_models_dir,
        os.path.join("models", "EXTENDED_4UAV"),
        os.path.join("models", f"SEED_{seed}"),
        "models",
        "."
    ])

    if algo.lower() == "mappo":
        names_to_try = []
        for sdir in search_dirs:
            names_to_try.extend([
                os.path.join(sdir, f"mappo_uav_{num_uavs}_{seed}.pt"),
                os.path.join(sdir, f"mappo_uav_{num_uavs}.pt"),
            ])

        for name in names_to_try:
            if os.path.exists(name):
                print(f"[+] Caricamento modello MAPPO da: {name}")
                return MAPPO.load(name), "mappo", name

        # Se non trova il modello MAPPO, tenta il fallback automatico su PPO
        fallback_names = []
        for sdir in search_dirs:
            fallback_names.extend([
                os.path.join(sdir, f"ppo_multi_uav_{num_uavs}_{seed}.zip"),
                os.path.join(sdir, f"ppo_multi_uav_{num_uavs}.zip"),
            ])
        for fb in fallback_names:
            if os.path.exists(fb):
                from stable_baselines3 import PPO
                print(f"[!] Modello MAPPO non trovato. Fallback automatico su modello PPO: {fb}")
                return PPO.load(fb), "ppo", fb

        raise FileNotFoundError(f"Nessun modello trovato per N={num_uavs} (seed={seed}). Controlla i percorsi dei modelli!")

    else:
        from stable_baselines3 import PPO
        names_to_try = []
        for sdir in search_dirs:
            names_to_try.extend([
                os.path.join(sdir, f"ppo_multi_uav_{num_uavs}_{seed}"),
                os.path.join(sdir, f"ppo_multi_uav_{num_uavs}"),
                os.path.join(sdir, "ppo_single_uav") if num_uavs == 1 else "",
            ])
        for name in names_to_try:
            if not name:
                continue
            zip_name = name if name.endswith(".zip") else f"{name}.zip"
            if os.path.exists(zip_name):
                print(f"[+] Caricamento modello PPO da: {zip_name}")
                return PPO.load(name), "ppo", zip_name

        raise FileNotFoundError(f"Modello PPO non trovato per N={num_uavs} (seed={seed}). Controlla i percorsi dei modelli!")


def main():
    """
    Esegue la simulazione grafica interattiva della flotta di droni con rendering Pygame.
    """
    # Parsing e lettura dei parametri di configurazione
    args = parse_args()
    num_uavs = args.uavs
    size = args.size
    num_obstacles = args.obstacles
    seed = args.seed

    print(f"\n{'='*70}")
    drone_str = f"{num_uavs} dron{'e' if num_uavs == 1 else 'i'}"
    print(f" SIMULAZIONE VISIVA FLOTTA UAV: {drone_str.upper()} ({args.algo.upper()})")
    print(f"{'='*70}\n")

    # Caricamento del modello e dei relativi pesi
    model, loaded_algo, model_path = load_model(
        args.algo,
        num_uavs,
        seed=seed,
        model_path=args.model_path,
        models_dir=args.models_dir
    )

    # Inizializzazione dell'ambiente con interfaccia grafica
    env = MultiUAVEnv(
        render_mode="human",
        size=size,
        num_obstacles=num_obstacles,
        num_uavs=num_uavs
    )

    print(f"Avvio della simulazione per {args.episodes} episodi...")
    successes = 0
    total_rewards = []
    user_interrupted = False

    # Ciclo di simulazione sugli episodi configurati
    for episode in range(args.episodes):
        if user_interrupted:
            break

        obs, info = env.reset()
        done = False
        truncated = False
        total_reward = 0.0
        step = 0

        print(f"\n--- Episodio {episode + 1}/{args.episodes} ---")

        # Loop di avanzamento del singolo episodio fino a completamento o timeout
        while not done and not truncated:
            # Controllo eventi Pygame (chiusura finestra)
            import pygame
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("\n[!] Finestra Pygame chiusa dall'utente. Uscita...")
                    user_interrupted = True
                    break

            if user_interrupted:
                break

            # Predizione delle azioni dalla policy (in modalità deterministica per il test)
            action, _states = model.predict(obs, deterministic=True)
            
            # Adattamento del formato delle azioni per l'ambiente (scalare per N=1, array per N>1)
            env_action = action if num_uavs > 1 else (action[0] if hasattr(action, "__len__") else action)

            # Esecuzione dell'azione nell'ambiente
            obs, reward, terminated, truncated, info = env.step(env_action)
            total_reward += reward
            step += 1

            # Pausa per regolare la velocità di riproduzione della grafica
            time.sleep(args.delay)

            done = terminated

        # Valutazione dell'esito dell'episodio
        is_success = info.get("success", done)
        if is_success:
            successes += 1
            print(f" Obiettivo RAGGIUNTO in {step} step! Reward totale: {total_reward:.2f}")
        elif truncated:
            print(f" Obiettivo NON raggiunto (timeout step massimi). Reward totale: {total_reward:.2f}")
        else:
            print(f" Episodio terminato in {step} step. Reward totale: {total_reward:.2f}")

        total_rewards.append(total_reward)

    # Chiusura e rilascio delle risorse della finestra grafica
    env.close()

    # Riepilogo finale delle metriche di test
    print(f" RIEPILOGO TEST ({drone_str.upper()} - {loaded_algo.upper()})")
    print(f"Success Rate: {successes}/{args.episodes} ({(successes / args.episodes) * 100:.1f}%)")
    print(f"Reward Medio: {sum(total_rewards)/len(total_rewards):.2f}")


if __name__ == "__main__":
    main()
