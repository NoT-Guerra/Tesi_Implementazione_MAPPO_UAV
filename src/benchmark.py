"""
Benchmark comparativo tra MAPPO e PPO centralizzato al variare del numero di droni.
Misura prestazioni di apprendimento, tempo di calcolo e utilizzo risorse hardware (CPU, RAM, GPU, VRAM).
Genera report tabellari in CSV e grafici di scalabilità in formato PNG.
"""

import time
import threading
import subprocess
import os
import argparse
import psutil
import numpy as np
import matplotlib.pyplot as plt

from env import MultiUAVEnv
from mappo import MAPPO
from stable_baselines3 import PPO


# Configurazione di default per gli esperimenti di benchmark
DEFAULT_DRONE_COUNTS = [1, 2, 3, 4]
DEFAULT_TIMESTEPS = "150000,450000,750000,1000000"  # Step calibrati: 150k (1 drone), 450k (2), 750k (3), 1M (4)
DEFAULT_EVAL_EPISODES = 100  # Episodi di test per ridurre la varianza statistica
SIZE = 10
NUM_OBSTACLES = 4
SEED = 42

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_BENCHMARK_DIR = os.path.join(PROJECT_ROOT, "benchmarks")


def get_gpu_stats():
    """
    Rileva l'utilizzo percentuale della GPU e la memoria VRAM occupata tramite nvidia-smi.

    Returns:
        tuple: (percentuale utilizzo GPU, memoria VRAM occupata in MB).
    """
    try:
        flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
        out = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=utilization.gpu,memory.used", "--format=csv,noheader,nounits"],
            encoding="utf-8",
            creationflags=flags,
            timeout=1
        )
        parts = [p.strip() for p in out.strip().split(",")]
        return float(parts[0]), float(parts[1])
    except Exception:
        return 0.0, 0.0


class ResourceMonitor(threading.Thread):
    """
    Thread daemon per il campionamento periodico dell'utilizzo di risorse hardware (CPU, RAM, GPU, VRAM).
    """
    def __init__(self, interval=0.25):
        super().__init__()
        self.interval = interval
        self.running = True
        self.process = psutil.Process()

        self.cpu_samples = []
        self.ram_samples = []
        self.gpu_samples = []
        self.vram_samples = []

    def run(self):
        while self.running:
            try:
                # Campionamento CPU e RAM del processo corrente
                cpu = self.process.cpu_percent(interval=None)
                ram_mb = self.process.memory_info().rss / (1024 * 1024)
                # Campionamento GPU e VRAM
                gpu_util, vram_mb = get_gpu_stats()

                if cpu > 0.0:
                    self.cpu_samples.append(cpu)
                self.ram_samples.append(ram_mb)
                self.gpu_samples.append(gpu_util)
                self.vram_samples.append(vram_mb)
            except Exception:
                pass
            time.sleep(self.interval)

    def stop(self):
        """Interrompe il campionamento del thread."""
        self.running = False

    def get_summary(self):
        """
        Calcola le statistiche riassuntive (valori medi e picchi massimi) registrate.

        Returns:
            dict: Valori medi e massimi di CPU, RAM, GPU e VRAM.
        """
        return {
            "cpu_avg": float(np.mean(self.cpu_samples)) if self.cpu_samples else 0.0,
            "cpu_max": float(np.max(self.cpu_samples)) if self.cpu_samples else 0.0,
            "ram_avg": float(np.mean(self.ram_samples)) if self.ram_samples else 0.0,
            "ram_max": float(np.max(self.ram_samples)) if self.ram_samples else 0.0,
            "gpu_avg": float(np.mean(self.gpu_samples)) if self.gpu_samples else 0.0,
            "gpu_max": float(np.max(self.gpu_samples)) if self.gpu_samples else 0.0,
            "vram_avg": float(np.mean(self.vram_samples)) if self.vram_samples else 0.0,
            "vram_max": float(np.max(self.vram_samples)) if self.vram_samples else 0.0,
        }


def evaluate_agent(model, algo, env, n_eval_episodes=DEFAULT_EVAL_EPISODES):
    """
    Valuta le prestazioni di una policy addestrata (MAPPO o PPO) su un set di episodi di test.

    Args:
        model: Istanza del modello addestrato (MAPPO o PPO).
        algo (str): Nome dell'algoritmo ('mappo' o 'ppo').
        env (MultiUAVEnv): Ambiente di simulazione.
        n_eval_episodes (int): Numero di episodi per la valutazione empirica.

    Returns:
        tuple: (reward medio, deviazione standard reward, success rate percentuale, passi medi).
    """
    rewards = []
    successes = []
    steps_list = []

    # Ciclo di valutazione sugli episodi di test
    for _ in range(n_eval_episodes):
        obs, info = env.reset()
        done = False
        ep_rew = 0.0
        step_count = 0

        while not done:
            action, _ = model.predict(obs, deterministic=True)
            # Adattamento del formato dell'azione per l'ambiente (scalare per N=1, array per N>1)
            if algo.lower() == "mappo":
                env_action = action if env.num_uavs > 1 else (action[0] if hasattr(action, "__len__") else action)
            else:
                env_action = action

            obs, r, term, trunc, info = env.step(env_action)
            ep_rew += r
            step_count += 1
            done = term or trunc

        rewards.append(ep_rew)
        # Verifica del raggiungimento dell'obiettivo
        is_succ = info.get("success", term)
        successes.append(1.0 if is_succ else 0.0)
        steps_list.append(step_count)

    return (
        float(np.mean(rewards)),
        float(np.std(rewards)),
        float(np.mean(successes) * 100.0),
        float(np.mean(steps_list))
    )


def run_single_benchmark(algo, n_uavs, timesteps, size=SIZE, num_obstacles=NUM_OBSTACLES, seed=SEED):
    """
    Esegue una singola sessione di benchmark per un dato algoritmo e numero di UAV.

    Args:
        algo (str): Algoritmo da testare ('mappo' o 'ppo').
        n_uavs (int): Numero di droni nella flotta.
        timesteps (int): Numero totale di passi di addestramento.
        size (int): Dimensione della griglia.
        num_obstacles (int): Numero di ostacoli.
        seed (int): Seed di riproducibilità.

    Returns:
        dict: Dizionario con metriche prestazionali, temporali e di utilizzo risorse.
    """
    # Inizializzazione dell'ambiente di simulazione
    env = MultiUAVEnv(size=size, num_obstacles=num_obstacles, num_uavs=n_uavs)

    # Inizializzazione del modello
    if algo.lower() == "mappo":
        model = MAPPO(
            num_uavs=n_uavs,
            grid_size=size,
            num_obstacles=num_obstacles,
            hidden_dim=128,
            lr_actor=3e-4,
            lr_critic=1e-3,
            n_steps=1024,
            batch_size=64,
            seed=seed
        )
    else:
        model = PPO("MlpPolicy", env, seed=seed, verbose=0)

    # Avvio del monitoraggio in background delle risorse hardware
    monitor = ResourceMonitor(interval=0.25)
    monitor.start()

    # Addestramento e misurazione del tempo impiegato
    start_time = time.time()
    if isinstance(model, MAPPO):
        model.learn(env, total_timesteps=timesteps, verbose=0)
    else:
        model.learn(total_timesteps=timesteps)
    elapsed_time = time.time() - start_time

    # Arresto del thread di monitoraggio
    monitor.stop()
    monitor.join()

    # Calcolo del throughput (FPS) e metriche hardware
    fps = timesteps / elapsed_time if elapsed_time > 0 else 0
    stats = monitor.get_summary()

    # Valutazione delle prestazioni della policy addestrata su episodi di test
    mean_rew, std_rew, succ_rate, avg_steps = evaluate_agent(model, algo, env, n_eval_episodes=DEFAULT_EVAL_EPISODES)
    env.close()

    return {
        "algo": algo.upper(),
        "n_uavs": n_uavs,
        "timesteps": timesteps,
        "time_s": elapsed_time,
        "fps": fps,
        "cpu_avg": stats["cpu_avg"],
        "cpu_max": stats["cpu_max"],
        "ram_avg": stats["ram_avg"],
        "ram_max": stats["ram_max"],
        "gpu_avg": stats["gpu_avg"],
        "gpu_max": stats["gpu_max"],
        "vram_avg": stats["vram_avg"],
        "mean_reward": mean_rew,
        "std_reward": std_rew,
        "success_rate": succ_rate,
        "avg_steps": avg_steps,
    }


def generate_comparison_plots(results_mappo, results_ppo, output_image="benchmark_confronto_mappo.png", seed=SEED):
    """
    Genera e salva su file i grafici comparativi tra MAPPO e PPO al variare del numero di droni.

    Args:
        results_mappo (list): Risultati benchmark per MAPPO.
        results_ppo (list): Risultati benchmark per PPO.
        output_image (str): Percorso del file immagine PNG di output.
        seed (int): Seed utilizzato negli esperimenti.
    """
    droni_mappo = [r["n_uavs"] for r in results_mappo]
    droni_ppo = [r["n_uavs"] for r in results_ppo]

    fig, axes = plt.subplots(3, 2, figsize=(14, 15))
    plt.subplots_adjust(hspace=0.35, wspace=0.25)
    fig.suptitle(
        f"Confronto Benchmark (Seed {seed}): MAPPO (CTDE Parametrico) vs PPO Centralizzato al variare del Numero di UAV",
        fontsize=16,
        fontweight="bold"
    )

    color_mappo = "blue"
    color_ppo = "red"

    # Reward medio
    axes[0, 0].plot(droni_mappo, [r["mean_reward"] for r in results_mappo], marker="o", linewidth=2.5, color=color_mappo, label="MAPPO")
    axes[0, 0].plot(droni_ppo, [r["mean_reward"] for r in results_ppo], marker="s", linewidth=2.5, color=color_ppo, linestyle="--", label="PPO Centralizzato")
    axes[0, 0].set_title(f"Reward Medio ({DEFAULT_EVAL_EPISODES} Episodi di Valutazione)", fontweight="bold")
    axes[0, 0].set_xlabel("Numero di Droni (UAV)")
    axes[0, 0].set_ylabel("Reward Medio")
    axes[0, 0].set_xticks(droni_mappo)
    axes[0, 0].grid(True, linestyle="--", alpha=0.6)
    axes[0, 0].legend(fontsize=11)

    # Tasso di successo della missione
    axes[0, 1].plot(droni_mappo, [r["success_rate"] for r in results_mappo], marker="^", linewidth=2.5, color=color_mappo, label="MAPPO")
    axes[0, 1].plot(droni_ppo, [r["success_rate"] for r in results_ppo], marker="v", linewidth=2.5, color=color_ppo, linestyle="--", label="PPO Centralizzato")
    axes[0, 1].set_title("Tasso di Successo Missione (% Arrivo Completo Flotta)", fontweight="bold")
    axes[0, 1].set_xlabel("Numero di Droni (UAV)")
    axes[0, 1].set_ylabel("Success Rate (%)")
    axes[0, 1].set_xticks(droni_mappo)
    axes[0, 1].set_ylim(-5, 105)
    axes[0, 1].grid(True, linestyle="--", alpha=0.6)
    axes[0, 1].legend(fontsize=11)

    # Throughput di calcolo (FPS)
    axes[1, 0].plot(droni_mappo, [r["fps"] for r in results_mappo], marker="D", linewidth=2.5, color=color_mappo, label="MAPPO")
    axes[1, 0].plot(droni_ppo, [r["fps"] for r in results_ppo], marker="x", linewidth=2.5, color=color_ppo, linestyle="--", label="PPO Centralizzato")
    axes[1, 0].set_title("Throughput di Calcolo (FPS - Step/secondo)", fontweight="bold")
    axes[1, 0].set_xlabel("Numero di Droni (UAV)")
    axes[1, 0].set_ylabel("Step / secondo")
    axes[1, 0].set_xticks(droni_mappo)
    axes[1, 0].grid(True, linestyle="--", alpha=0.6)
    axes[1, 0].legend(fontsize=11)

    # Tempo totale di addestramento
    x = np.array(droni_mappo)
    width = 0.35
    axes[1, 1].bar(x - width/2, [r["time_s"] for r in results_mappo], width=width, color=color_mappo, label="MAPPO", edgecolor="black")
    axes[1, 1].bar(x + width/2, [r["time_s"] for r in results_ppo], width=width, color=color_ppo, label="PPO Centralizzato", edgecolor="black")
    axes[1, 1].set_title("Tempo di Addestramento Totale (s)", fontweight="bold")
    axes[1, 1].set_xlabel("Numero di Droni (UAV)")
    axes[1, 1].set_ylabel("Secondi (s)")
    axes[1, 1].set_xticks(droni_mappo)
    axes[1, 1].grid(True, linestyle="--", alpha=0.6, axis="y")
    axes[1, 1].legend(fontsize=11)

    # Utilizzo del processore (CPU)
    axes[2, 0].plot(droni_mappo, [r["cpu_avg"] for r in results_mappo], marker="o", linewidth=2.5, color=color_mappo, label="MAPPO (CPU Media)")
    axes[2, 0].plot(droni_ppo, [r["cpu_avg"] for r in results_ppo], marker="s", linewidth=2.5, color=color_ppo, linestyle="--", label="PPO (CPU Media)")
    axes[2, 0].set_title("Utilizzo Processore CPU (%)", fontweight="bold")
    axes[2, 0].set_xlabel("Numero di Droni (UAV)")
    axes[2, 0].set_ylabel("Utilizzo CPU (%)")
    axes[2, 0].set_xticks(droni_mappo)
    axes[2, 0].grid(True, linestyle="--", alpha=0.6)
    axes[2, 0].legend(fontsize=11)

    # Consumo memoria RAM
    axes[2, 1].plot(droni_mappo, [r["ram_avg"] for r in results_mappo], marker="D", linewidth=2.5, color=color_mappo, label="MAPPO (RAM Processo)")
    axes[2, 1].plot(droni_ppo, [r["ram_avg"] for r in results_ppo], marker="v", linewidth=2.5, color=color_ppo, linestyle="--", label="PPO (RAM Processo)")
    axes[2, 1].set_title("Consumo Memoria RAM (MB)", fontweight="bold")
    axes[2, 1].set_xlabel("Numero di Droni (UAV)")
    axes[2, 1].set_ylabel("Megabyte (MB)")
    axes[2, 1].set_xticks(droni_mappo)
    axes[2, 1].grid(True, linestyle="--", alpha=0.6)
    axes[2, 1].legend(fontsize=11)

    # Salvataggio dell'immagine
    plt.savefig(output_image, dpi=300, bbox_inches="tight")
    plt.close()


def run_benchmark(drone_counts=None, timesteps_per_run=DEFAULT_TIMESTEPS, mode="both", seed=SEED, save_dir=DEFAULT_BENCHMARK_DIR):
    """
    Coordina l'esecuzione del benchmark completo su varie configurazioni di flotta.

    Args:
        drone_counts (list): Lista con il numero di UAV da testare (es. [1, 2, 3, 4]).
        timesteps_per_run (str|int|dict): Configurazione degli step di addestramento.
        mode (str): Modalità di confronto ('both', 'mappo' o 'ppo').
        seed (int): Seed casuale per la riproducibilità.
        save_dir (str): Cartella in cui salvare i risultati (file CSV e grafici PNG).
    """
    if drone_counts is None:
        drone_counts = DEFAULT_DRONE_COUNTS

    # Mappatura dei timesteps: supporta valore unico o lista separata da virgole
    if isinstance(timesteps_per_run, str):
        parts = [int(p.strip()) for p in timesteps_per_run.split(",") if p.strip()]
        if len(parts) == 1:
            timesteps_map = {n: parts[0] for n in drone_counts}
        elif len(parts) == len(drone_counts):
            timesteps_map = {n: parts[i] for i, n in enumerate(drone_counts)}
        elif max(drone_counts) <= len(parts):
            timesteps_map = {n: parts[n - 1] for n in drone_counts}
        else:
            raise ValueError(f"Numero di valori per --timesteps ({len(parts)}) non compatibile con i droni richiesti ({drone_counts}).")
    elif isinstance(timesteps_per_run, (int, float)):
        timesteps_map = {n: int(timesteps_per_run) for n in drone_counts}
    elif isinstance(timesteps_per_run, dict):
        timesteps_map = timesteps_per_run
    else:
        timesteps_map = {n: int(timesteps_per_run) for n in drone_counts}

    steps_desc = ", ".join(f"{n} UAV: {timesteps_map[n]:,} step" for n in drone_counts)
    print(f" AVVIO BENCHMARK COMPARATIVO PER OGNI QUANTITA DI DRONI ({drone_counts})")
    print(f" Configurazione Timesteps: {steps_desc} | Seed: {seed} | Griglia: {SIZE}x{SIZE} | Ostacoli: {NUM_OBSTACLES}")

    results_mappo = []
    results_ppo = []

    # Esecuzione del benchmark per ciascuna configurazione di droni
    for n_uavs in drone_counts:
        steps = timesteps_map[n_uavs]
        # Benchmark MAPPO
        if mode in ["both", "mappo"]:
            res_mappo = run_single_benchmark("mappo", n_uavs, steps, seed=seed)
            results_mappo.append(res_mappo)

        # Benchmark PPO centralizzato
        if mode in ["both", "ppo"]:
            res_ppo = run_single_benchmark("ppo", n_uavs, steps, seed=seed)
            results_ppo.append(res_ppo)

    all_results = []
    for n in drone_counts:
        m_res = next((r for r in results_mappo if r["n_uavs"] == n), None)
        p_res = next((r for r in results_ppo if r["n_uavs"] == n), None)

        if m_res:
            all_results.append(m_res)
        if p_res:
            all_results.append(p_res)

    import shutil
    os.makedirs(save_dir, exist_ok=True)

    # Salvataggio dei risultati in formato CSV
    csv_file = os.path.join(save_dir, f"benchmark_confronto_mappo_{seed}.csv")
    with open(csv_file, "w", encoding="utf-8") as f:
        f.write(
            "Droni,Algoritmo,Timesteps,Tempo_s,FPS,CPU_Media_pct,CPU_Picco_pct,RAM_MB,GPU_Media_pct,GPU_Picco_pct,VRAM_MB,Reward_Medio,Reward_Std,Success_Rate_pct,Avg_Steps\n"
        )
        for r in all_results:
            f.write(
                f"{r['n_uavs']},{r['algo']},{r.get('timesteps', 0)},{r['time_s']:.2f},{r['fps']:.1f},"
                f"{r['cpu_avg']:.2f},{r['cpu_max']:.2f},{r['ram_avg']:.2f},{r['gpu_avg']:.2f},"
                f"{r['gpu_max']:.2f},{r['vram_avg']:.2f},{r['mean_reward']:.2f},{r['std_reward']:.2f},"
                f"{r['success_rate']:.2f},{r['avg_steps']:.2f}\n"
            )
    shutil.copyfile(csv_file, os.path.join(save_dir, "benchmark_confronto_mappo.csv"))

    png_file = os.path.join(save_dir, f"benchmark_confronto_mappo_{seed}.png")
    # Generazione dei grafici
    if results_mappo and results_ppo:
        generate_comparison_plots(results_mappo, results_ppo, output_image=png_file, seed=seed)
        shutil.copyfile(png_file, os.path.join(save_dir, "benchmark_confronto_mappo.png"))
    elif results_mappo:
        # Se è presente solo MAPPO, genera il grafico dedicato
        droni = [r["n_uavs"] for r in results_mappo]
        fig, axes = plt.subplots(2, 2, figsize=(13, 9))
        plt.subplots_adjust(hspace=0.35, wspace=0.25)
        fig.suptitle(f"Analisi di Scalabilità e Consumo Risorse MAPPO (Seed {seed})", fontsize=15, fontweight="bold")

        axes[0, 0].plot(droni, [r["cpu_avg"] for r in results_mappo], marker="o", color="#d9534f", label="CPU Media (%)")
        axes[0, 0].plot(droni, [r["gpu_avg"] for r in results_mappo], marker="s", color="#0275d8", label="GPU Media (%)")
        axes[0, 0].set_title("Utilizzo CPU e GPU (%)", fontweight="bold")
        axes[0, 0].set_xlabel("Numero di Droni")
        axes[0, 0].grid(True, linestyle="--", alpha=0.6)
        axes[0, 0].legend()

        axes[0, 1].plot(droni, [r["fps"] for r in results_mappo], marker="^", color="#5cb85c")
        axes[0, 1].set_title("Throughput (FPS - Step/s)", fontweight="bold")
        axes[0, 1].set_xlabel("Numero di Droni")
        axes[0, 1].grid(True, linestyle="--", alpha=0.6)

        axes[1, 0].plot(droni, [r["mean_reward"] for r in results_mappo], marker="o", color="#0275d8")
        axes[1, 0].set_title("Reward Medio (Valutazione)", fontweight="bold")
        axes[1, 0].set_xlabel("Numero di Droni")
        axes[1, 0].grid(True, linestyle="--", alpha=0.6)

        axes[1, 1].plot(droni, [r["ram_avg"] for r in results_mappo], marker="D", color="#6f42c1")
        axes[1, 1].set_title("Utilizzo Memoria RAM (MB)", fontweight="bold")
        axes[1, 1].set_xlabel("Numero di Droni")
        axes[1, 1].grid(True, linestyle="--", alpha=0.6)

        # Salvataggio del grafico
        plt.savefig(png_file, dpi=300, bbox_inches="tight")
        plt.close()
        shutil.copyfile(png_file, os.path.join(save_dir, "benchmark_confronto_mappo.png"))

    print(f"\nBenchmark completato\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Benchmark Scalabilità MAPPO vs PPO")
    parser.add_argument("--timesteps", type=str, default=str(DEFAULT_TIMESTEPS), help=f"Step per run: singolo numero o lista separata da virgole per ogni drone (default: {DEFAULT_TIMESTEPS})")
    parser.add_argument("--mode", type=str, default="both", choices=["both", "mappo", "ppo"], help="Algoritmi da testare (default: both)")
    parser.add_argument("--drones", type=str, default="1,2,3,4", help="Quantità di droni separati da virgola (default: 1,2,3,4)")
    parser.add_argument("--seed", type=int, default=SEED, help=f"Seed casuale per riproducibilità (default: {SEED})")
    parser.add_argument("--save-dir", type=str, default=DEFAULT_BENCHMARK_DIR, help="Cartella salvataggio benchmark")
    args = parser.parse_args()

    counts = [int(x.strip()) for x in args.drones.split(",") if x.strip()]
    run_benchmark(drone_counts=counts, timesteps_per_run=args.timesteps, mode=args.mode, seed=args.seed, save_dir=args.save_dir)
