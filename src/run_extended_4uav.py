"""
Suite notturna automatica per lo studio di convergenza asintotica a 4 UAV.
Esegue l'addestramento esteso (default: 4.000.000 step) per MAPPO e PPO
su 3 semi indipendenti (42, 123, 999), salva modelli, log TensorBoard e metriche,
e genera automaticamente report e grafici aggregati finali con deviazione standard.
"""

import os
import sys
import time
import datetime
import argparse
import numpy as np
import matplotlib.pyplot as plt

# Risoluzione percorsi per esecuzione diretta o da IDE
SRC_DIR = os.path.abspath(os.path.dirname(__file__))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

PROJECT_ROOT = os.path.abspath(os.path.join(SRC_DIR, ".."))
DEFAULT_SAVE_DIR = os.path.join(PROJECT_ROOT, "benchmarks", "EXTENDED_4UAV")
DEFAULT_MODELS_DIR = os.path.join(PROJECT_ROOT, "models", "EXTENDED_4UAV")
DEFAULT_TB_LOG = os.path.join(PROJECT_ROOT, "tensorboard_logs", "EXTENDED_4UAV")

from env import MultiUAVEnv
from mappo import MAPPO
from stable_baselines3 import PPO
from benchmark import ResourceMonitor, evaluate_agent
from aggregate_benchmarks import (
    compute_statistics,
    export_aggregated_csv,
    export_markdown_and_print_summary,
    load_and_group_benchmarks,
    find_benchmark_csvs
)

def plot_4uav_comparison(stats, seeds, output_png):
    """
    Genera un grafico a barre comparativo professionale (Media +/- Deviazione Standard)
    dedicato al confronto a 4 UAV tra MAPPO e PPO.
    """
    key_mappo = (4, "MAPPO")
    key_ppo = (4, "PPO")

    has_mappo = key_mappo in stats
    has_ppo = key_ppo in stats

    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    plt.subplots_adjust(hspace=0.35, wspace=0.30)

    seeds_str = ", ".join(map(str, seeds))
    fig.suptitle(
        f"Studio di Convergenza Asintotica Flotta 4 UAV (Semi: {seeds_str})\n"
        f"Confronto MAPPO (CTDE) vs PPO Centralizzato ad Alto Budget (Media \u00b1 \u03c3 su {len(seeds)} run)",
        fontsize=14,
        fontweight="bold"
    )

    metrics = [
        ("Success_Rate_pct", "Tasso di Successo (%)", "Success Rate (%)", (-5, 105), axes[0, 0]),
        ("Reward_Medio", "Reward Medio di Valutazione", "Reward", None, axes[0, 1]),
        ("FPS", "Throughput di Calcolo (FPS)", "Step / s", None, axes[0, 2]),
        ("Tempo_s", "Tempo di Addestramento (s)", "Secondi", None, axes[1, 0]),
        ("CPU_Media_pct", "Utilizzo CPU Media (%)", "CPU %", None, axes[1, 1]),
        ("RAM_MB", "Consumo Memoria RAM (MB)", "Megabyte", None, axes[1, 2]),
    ]

    labels = []
    if has_mappo:
        labels.append("MAPPO")
    if has_ppo:
        labels.append("PPO Centralizzato")

    colors = ["#1f77b4", "#d62728"]
    x = np.arange(len(labels))
    bar_width = 0.55

    for m_key, title, ylabel, ylim, ax in metrics:
        means = []
        stds = []
        if has_mappo:
            means.append(stats[key_mappo][f"{m_key}_mean"])
            stds.append(stats[key_mappo][f"{m_key}_std"])
        if has_ppo:
            means.append(stats[key_ppo][f"{m_key}_mean"])
            stds.append(stats[key_ppo][f"{m_key}_std"])

        bars = ax.bar(x, means, yerr=stds, capsize=6, width=bar_width, color=colors[:len(labels)], edgecolor="black", alpha=0.9)
        ax.set_title(title, fontweight="bold", fontsize=11)
        ax.set_ylabel(ylabel, fontsize=10)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontweight="bold")
        ax.grid(True, linestyle="--", alpha=0.5, axis="y")
        if ylim:
            ax.set_ylim(ylim)

        # Aggiunta etichette numeriche sopra le barre
        for bar, m_val, s_val in zip(bars, means, stds):
            h = bar.get_height()
            v_offset = (s_val if s_val > 0 else 0) + (abs(h) * 0.03 if h != 0 else 1)
            y_pos = h + v_offset if h >= 0 else h - v_offset
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                y_pos,
                f"{m_val:.1f}\n\u00b1{s_val:.1f}",
                ha="center",
                va="bottom" if h >= 0 else "top",
                fontsize=8.5,
                fontweight="bold"
            )

    os.makedirs(os.path.dirname(os.path.abspath(output_png)), exist_ok=True)
    plt.savefig(output_png, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  Grafico comparativo 4 UAV salvato in: {output_png}")


def run_single_algorithm(algo, uavs, timesteps, seed, save_dir, models_dir, tb_log, eval_episodes=100):
    """
    Esegue l'addestramento completo di un singolo algoritmo a 4 UAV con monitoraggio risorse e salvataggio checkpoint.
    """
    now_str = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{now_str}] AVVIO RUN: {algo.upper()} | {uavs} UAV | {timesteps:,} step | Seed {seed}")

    env = MultiUAVEnv(size=10, num_obstacles=4, num_uavs=uavs)

    # Monitoraggio risorse in background
    monitor = ResourceMonitor(interval=0.5)
    monitor.start()
    start_time = time.time()

    os.makedirs(models_dir, exist_ok=True)

    if algo.lower() == "mappo":
        model_mappo = MAPPO(
            num_uavs=uavs,
            grid_size=10,
            num_obstacles=4,
            hidden_dim=128,
            lr_actor=3e-4,
            lr_critic=1e-3,
            n_steps=1024,
            batch_size=64,
            seed=seed
        )
        model_mappo.learn(env, total_timesteps=timesteps, verbose=0, tensorboard_log=tb_log)
        elapsed_time = time.time() - start_time
        monitor.stop()
        monitor.join()

        # Salvataggio pesi modello MAPPO (.pt)
        model_path = os.path.join(models_dir, f"mappo_uav_{uavs}_{seed}")
        model_mappo.save(model_path)
        print(f"  Checkpoint MAPPO salvato: {model_path}.pt")

        # Valutazione finale
        print(f"  Valutazione in corso su {eval_episodes} episodi di test...")
        mean_rew, std_rew, succ_rate, avg_steps = evaluate_agent(model_mappo, "mappo", env, n_eval_episodes=eval_episodes)
    else:
        model_ppo = PPO("MlpPolicy", env, seed=seed, verbose=0, tensorboard_log=tb_log)
        model_ppo.learn(total_timesteps=timesteps, tb_log_name=f"PPO_{uavs}_UAV_{seed}")
        elapsed_time = time.time() - start_time
        monitor.stop()
        monitor.join()

        # Salvataggio pesi modello PPO (.zip)
        model_path = os.path.join(models_dir, f"ppo_multi_uav_{uavs}_{seed}")
        model_ppo.save(model_path)
        print(f"  Checkpoint PPO salvato: {model_path}.zip")

        # Valutazione finale
        print(f"  Valutazione in corso su {eval_episodes} episodi di test...")
        mean_rew, std_rew, succ_rate, avg_steps = evaluate_agent(model_ppo, "ppo", env, n_eval_episodes=eval_episodes)

    env.close()

    fps = timesteps / elapsed_time if elapsed_time > 0 else 0.0
    stats = monitor.get_summary()

    elapsed_m = elapsed_time / 60.0
    print(f"  Completato in {elapsed_time:.1f}s ({elapsed_m:.1f} min) | Throughput: {fps:.1f} FPS")
    print(f"  Success Rate: {succ_rate:.1f}% | Reward: {mean_rew:.1f} +/- {std_rew:.1f} | Passi Medi: {avg_steps:.1f}")
    print(f"  CPU Media: {stats['cpu_avg']:.1f}% | RAM: {stats['ram_avg']:.1f} MB | GPU: {stats['gpu_avg']:.1f}%")

    return {
        "Droni": uavs,
        "Algoritmo": algo.upper(),
        "Timesteps": timesteps,
        "Tempo_s": elapsed_time,
        "FPS": fps,
        "CPU_Media_pct": stats["cpu_avg"],
        "CPU_Picco_pct": stats["cpu_max"],
        "RAM_MB": stats["ram_avg"],
        "GPU_Media_pct": stats["gpu_avg"],
        "GPU_Picco_pct": stats["gpu_max"],
        "VRAM_MB": stats["vram_avg"],
        "Reward_Medio": mean_rew,
        "Reward_Std": std_rew,
        "Success_Rate_pct": succ_rate,
        "Avg_Steps": avg_steps,
    }


def save_seed_csv(results, seed_dir, seed):
    """Salva il file CSV dei risultati per un dato seed."""
    os.makedirs(seed_dir, exist_ok=True)
    csv_file = os.path.join(seed_dir, f"benchmark_confronto_mappo_{seed}.csv")
    with open(csv_file, "w", encoding="utf-8") as f:
        f.write("Droni,Algoritmo,Timesteps,Tempo_s,FPS,CPU_Media_pct,CPU_Picco_pct,RAM_MB,GPU_Media_pct,GPU_Picco_pct,VRAM_MB,Reward_Medio,Reward_Std,Success_Rate_pct,Avg_Steps\n")
        for r in results:
            f.write(
                f"{r['Droni']},{r['Algoritmo']},{r['Timesteps']},{r['Tempo_s']:.2f},{r['FPS']:.1f},"
                f"{r['CPU_Media_pct']:.2f},{r['CPU_Picco_pct']:.2f},{r['RAM_MB']:.2f},{r['GPU_Media_pct']:.2f},"
                f"{r['GPU_Picco_pct']:.2f},{r['VRAM_MB']:.2f},{r['Reward_Medio']:.2f},{r['Reward_Std']:.2f},"
                f"{r['Success_Rate_pct']:.2f},{r['Avg_Steps']:.2f}\n"
            )
    print(f"  File CSV del seed {seed} salvato in: {csv_file}")


def main():
    parser = argparse.ArgumentParser(description="Suite Notturna Convergenza 4 UAV Multi-Seed (MAPPO vs PPO)")
    parser.add_argument("--timesteps", type=int, default=4000000, help="Timesteps totali di addestramento (default: 4.000.000)")
    parser.add_argument("--seeds", type=str, default="42,123,999", help="Semi da eseguire separati da virgola (default: 42,123,999)")
    parser.add_argument("--uavs", type=int, default=4, help="Numero di droni (default: 4)")
    parser.add_argument("--mode", type=str, default="both", choices=["both", "mappo", "ppo"], help="Algoritmi da eseguire (default: both)")
    parser.add_argument("--save-dir", type=str, default=DEFAULT_SAVE_DIR, help="Cartella risultati benchmark")
    parser.add_argument("--models-dir", type=str, default=DEFAULT_MODELS_DIR, help="Cartella salvataggio modelli")
    parser.add_argument("--tb-log", type=str, default=DEFAULT_TB_LOG, help="Cartella log TensorBoard")
    parser.add_argument("--eval-episodes", type=int, default=100, help="Numero di episodi di test per modello (default: 100)")
    args = parser.parse_args()

    seeds = [int(s.strip()) for s in args.seeds.split(",") if s.strip()]
    algos = ["mappo", "ppo"] if args.mode == "both" else [args.mode.lower()]

    total_runs = len(seeds) * len(algos)
    suite_start_time = time.time()
    start_dt = datetime.datetime.now().strftime("%d/%m/%Y alle %H:%M:%S")

    print(" SUITE NOTTURNA: STUDIO DI CONVERGENZA ASINTOTICA (4 UAV)")
    print(f" Avvio: {start_dt}")
    print(f" Configurazione: {args.uavs} Droni | {args.timesteps:,} step | Algoritmi: {[a.upper() for a in algos]}")
    print(f" Semi: {seeds} | Totale run pianificate: {total_runs}")

    current_run = 0
    for seed in seeds:
        seed_dir = os.path.join(args.save_dir, f"SEED_{seed}")
        seed_results = []

        for algo in algos:
            current_run += 1
            print(f"\n>>> AVANZAMENTO SUITE NOTTURNA: [{current_run}/{total_runs}] (Seed {seed} - {algo.upper()}) <<<")
            res = run_single_algorithm(
                algo=algo,
                uavs=args.uavs,
                timesteps=args.timesteps,
                seed=seed,
                save_dir=seed_dir,
                models_dir=args.models_dir,
                tb_log=args.tb_log,
                eval_episodes=args.eval_episodes
            )
            seed_results.append(res)

        save_seed_csv(seed_results, seed_dir, seed)

    seed_files = find_benchmark_csvs(args.save_dir, seeds)
    if seed_files:
        grouped_data, seeds_used = load_and_group_benchmarks(seed_files)
        stats = compute_statistics(grouped_data)

        out_csv = os.path.join(args.save_dir, "benchmark_aggregato_multi_seed.csv")
        out_md = os.path.join(args.save_dir, "benchmark_aggregato_multi_seed.md")
        out_png = os.path.join(args.save_dir, "benchmark_aggregato_multi_seed.png")

        export_aggregated_csv(stats, out_csv)
        export_markdown_and_print_summary(stats, seeds_used, out_md)
        plot_4uav_comparison(stats, seeds_used, out_png)

    suite_duration = time.time() - suite_start_time
    hours = int(suite_duration // 3600)
    minutes = int((suite_duration % 3600) // 60)
    end_dt = datetime.datetime.now().strftime("%d/%m/%Y alle %H:%M:%S")

    print(f" SUITE NOTTURNA COMPLETATA CON SUCCESSO")
    print(f" Terminato: {end_dt}")
    print(f" Tempo totale impiegato: {hours} ore e {minutes} minuti ({suite_duration:.1f} secondi)")


if __name__ == "__main__":
    main()
