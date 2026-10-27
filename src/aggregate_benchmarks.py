"""
Script per l'aggregazione statistica e visualizzazione multi-seed dei benchmark (MAPPO vs PPO).
Legge i file CSV generati per ciascun seed (es. SEED_42, SEED_123, SEED_999),
calcola Media e Deviazione Standard per tutte le metriche e produce:
1. File CSV dettagliato con medie e deviazioni standard;
2. File Markdown con tabella riassuntiva formattata (Mean +/- Std) pronta per la tesi;
3. Grafici comparativi accademici in PNG con bande di dispersione (shaded error area).
"""

import os
import glob
import csv
import argparse
import numpy as np
import matplotlib.pyplot as plt

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_BENCHMARK_DIR = os.path.join(PROJECT_ROOT, "benchmarks")


def find_benchmark_csvs(benchmark_dir, requested_seeds=None):
    """
    Individua automaticamente i file CSV dei benchmark per ciascun seed.

    Args:
        benchmark_dir (str): Cartella principale dei benchmark.
        requested_seeds (list[int], optional): Lista di semi specifici da includere.

    Returns:
        dict: Dizionario {seed: path_al_csv}.
    """
    seed_files = {}

    if requested_seeds:
        for s in requested_seeds:
            # Cerca sia nel sottodirettorio SEED_<seed> che direttamente nella cartella benchmarks
            sub_path = os.path.join(benchmark_dir, f"SEED_{s}", f"benchmark_confronto_mappo_{s}.csv")
            direct_path = os.path.join(benchmark_dir, f"benchmark_confronto_mappo_{s}.csv")
            if os.path.isfile(sub_path):
                seed_files[s] = sub_path
            elif os.path.isfile(direct_path):
                seed_files[s] = direct_path
            else:
                print(f"  Attenzione: file benchmark per il seed {s} non trovato.")
    else:
        # Ricerca automatica in tutte le cartelle SEED_*
        pattern = os.path.join(benchmark_dir, "SEED_*", "benchmark_confronto_mappo_*.csv")
        for fpath in glob.glob(pattern):
            fname = os.path.basename(fpath)
            try:
                # Estrae il seed dal nome: benchmark_confronto_mappo_<seed>.csv
                seed_str = fname.replace("benchmark_confronto_mappo_", "").replace(".csv", "")
                seed = int(seed_str)
                seed_files[seed] = fpath
            except ValueError:
                continue

    return seed_files


def load_and_group_benchmarks(seed_files):
    """
    Carica i dati CSV e li raggruppa per (n_uavs, algo).

    Args:
        seed_files (dict): Mappa {seed: filepath}.

    Returns:
        tuple: (dati raggruppati { (n_uavs, algo): {metrica: [valori]} }, lista semi utilizzati).
    """
    grouped_data = {}
    seeds_used = sorted(list(seed_files.keys()))

    metric_keys = [
        "Timesteps", "Tempo_s", "FPS", "CPU_Media_pct", "CPU_Picco_pct",
        "RAM_MB", "GPU_Media_pct", "GPU_Picco_pct", "VRAM_MB",
        "Reward_Medio", "Reward_Std", "Success_Rate_pct", "Avg_Steps"
    ]

    for seed, fpath in seed_files.items():
        with open(fpath, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                n_uavs = int(row["Droni"])
                algo = row["Algoritmo"].strip().upper()
                key = (n_uavs, algo)

                if key not in grouped_data:
                    grouped_data[key] = {m: [] for m in metric_keys}
                    grouped_data[key]["seeds"] = []

                grouped_data[key]["seeds"].append(seed)
                for m in metric_keys:
                    val = float(row.get(m, 0.0))
                    grouped_data[key][m].append(val)

    return grouped_data, seeds_used


def compute_statistics(grouped_data):
    """
    Calcola Media e Deviazione Standard campionaria (ddof=1 se N>1) per ogni metrica.

    Returns:
        dict: { (n_uavs, algo): { 'metric_mean': float, 'metric_std': float } }
    """
    stats = {}
    for key, metrics in grouped_data.items():
        stats[key] = {}
        for m, values in metrics.items():
            if m == "seeds":
                stats[key]["seeds"] = values
                continue
            arr = np.array(values, dtype=float)
            stats[key][f"{m}_mean"] = float(np.mean(arr))
            stats[key][f"{m}_std"] = float(np.std(arr, ddof=1)) if len(arr) > 1 else 0.0
            stats[key][f"{m}_values"] = values

    return stats


def generate_aggregated_plots(stats, seeds, output_png):
    """
    Genera grafici accademici ad alta risoluzione con curve medie e aree di dispersione (shaded area).
    """
    drone_counts = sorted(list({k[0] for k in stats.keys()}))
    algos = sorted(list({k[1] for k in stats.keys()}))

    # Verifica presenza MAPPO e PPO
    has_mappo = "MAPPO" in algos
    has_ppo = "PPO" in algos

    fig, axes = plt.subplots(3, 2, figsize=(14, 15))
    plt.subplots_adjust(hspace=0.35, wspace=0.25)
    
    seeds_str = ", ".join(map(str, seeds))
    fig.suptitle(
        f"Benchmark Aggregato Multi-Seed (Seed: {seeds_str})\n"
        f"Confronto MAPPO vs PPO Centralizzato (Media \u00b1 Deviazione Standard su {len(seeds)} run indipendenti)",
        fontsize=15,
        fontweight="bold"
    )

    color_mappo = "#1f77b4"  # Blu
    color_ppo = "#d62728"    # Rosso

    # Estrazione vettori per MAPPO
    m_drones = [n for n in drone_counts if (n, "MAPPO") in stats]
    m_rew_mean = np.array([stats[(n, "MAPPO")]["Reward_Medio_mean"] for n in m_drones])
    m_rew_std = np.array([stats[(n, "MAPPO")]["Reward_Medio_std"] for n in m_drones])
    m_succ_mean = np.array([stats[(n, "MAPPO")]["Success_Rate_pct_mean"] for n in m_drones])
    m_succ_std = np.array([stats[(n, "MAPPO")]["Success_Rate_pct_std"] for n in m_drones])
    m_fps_mean = np.array([stats[(n, "MAPPO")]["FPS_mean"] for n in m_drones])
    m_fps_std = np.array([stats[(n, "MAPPO")]["FPS_std"] for n in m_drones])
    m_time_mean = np.array([stats[(n, "MAPPO")]["Tempo_s_mean"] for n in m_drones])
    m_time_std = np.array([stats[(n, "MAPPO")]["Tempo_s_std"] for n in m_drones])
    m_cpu_mean = np.array([stats[(n, "MAPPO")]["CPU_Media_pct_mean"] for n in m_drones])
    m_cpu_std = np.array([stats[(n, "MAPPO")]["CPU_Media_pct_std"] for n in m_drones])
    m_ram_mean = np.array([stats[(n, "MAPPO")]["RAM_MB_mean"] for n in m_drones])
    m_ram_std = np.array([stats[(n, "MAPPO")]["RAM_MB_std"] for n in m_drones])

    # Estrazione vettori per PPO
    p_drones = [n for n in drone_counts if (n, "PPO") in stats]
    p_rew_mean = np.array([stats[(n, "PPO")]["Reward_Medio_mean"] for n in p_drones]) if has_ppo else []
    p_rew_std = np.array([stats[(n, "PPO")]["Reward_Medio_std"] for n in p_drones]) if has_ppo else []
    p_succ_mean = np.array([stats[(n, "PPO")]["Success_Rate_pct_mean"] for n in p_drones]) if has_ppo else []
    p_succ_std = np.array([stats[(n, "PPO")]["Success_Rate_pct_std"] for n in p_drones]) if has_ppo else []
    p_fps_mean = np.array([stats[(n, "PPO")]["FPS_mean"] for n in p_drones]) if has_ppo else []
    p_fps_std = np.array([stats[(n, "PPO")]["FPS_std"] for n in p_drones]) if has_ppo else []
    p_time_mean = np.array([stats[(n, "PPO")]["Tempo_s_mean"] for n in p_drones]) if has_ppo else []
    p_time_std = np.array([stats[(n, "PPO")]["Tempo_s_std"] for n in p_drones]) if has_ppo else []
    p_cpu_mean = np.array([stats[(n, "PPO")]["CPU_Media_pct_mean"] for n in p_drones]) if has_ppo else []
    p_cpu_std = np.array([stats[(n, "PPO")]["CPU_Media_pct_std"] for n in p_drones]) if has_ppo else []
    p_ram_mean = np.array([stats[(n, "PPO")]["RAM_MB_mean"] for n in p_drones]) if has_ppo else []
    p_ram_std = np.array([stats[(n, "PPO")]["RAM_MB_std"] for n in p_drones]) if has_ppo else []

    # 1. Reward Medio
    ax = axes[0, 0]
    if has_mappo:
        ax.plot(m_drones, m_rew_mean, marker="o", linewidth=2.5, color=color_mappo, label="MAPPO")
        ax.fill_between(m_drones, m_rew_mean - m_rew_std, m_rew_mean + m_rew_std, color=color_mappo, alpha=0.18)
    if has_ppo:
        ax.plot(p_drones, p_rew_mean, marker="s", linewidth=2.5, color=color_ppo, linestyle="--", label="PPO Centralizzato")
        ax.fill_between(p_drones, p_rew_mean - p_rew_std, p_rew_mean + p_rew_std, color=color_ppo, alpha=0.18)
    ax.set_title("Reward Medio di Valutazione (Media \u00b1 \u03c3)", fontweight="bold")
    ax.set_xlabel("Numero di Droni (UAV)")
    ax.set_ylabel("Reward Cumulativo")
    ax.set_xticks(drone_counts)
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.legend(fontsize=11)

    # 2. Tasso di Successo
    ax = axes[0, 1]
    if has_mappo:
        ax.plot(m_drones, m_succ_mean, marker="^", linewidth=2.5, color=color_mappo, label="MAPPO")
        ax.fill_between(m_drones, m_succ_mean - m_succ_std, m_succ_mean + m_succ_std, color=color_mappo, alpha=0.18)
    if has_ppo:
        ax.plot(p_drones, p_succ_mean, marker="v", linewidth=2.5, color=color_ppo, linestyle="--", label="PPO Centralizzato")
        ax.fill_between(p_drones, p_succ_mean - p_succ_std, p_succ_mean + p_succ_std, color=color_ppo, alpha=0.18)
    ax.set_title("Tasso di Successo Missione % (Media \u00b1 \u03c3)", fontweight="bold")
    ax.set_xlabel("Numero di Droni (UAV)")
    ax.set_ylabel("Success Rate (%)")
    ax.set_xticks(drone_counts)
    ax.set_ylim(-5, 105)
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.legend(fontsize=11)

    # 3. Throughput (FPS)
    ax = axes[1, 0]
    if has_mappo:
        ax.plot(m_drones, m_fps_mean, marker="D", linewidth=2.5, color=color_mappo, label="MAPPO")
        ax.fill_between(m_drones, m_fps_mean - m_fps_std, m_fps_mean + m_fps_std, color=color_mappo, alpha=0.18)
    if has_ppo:
        ax.plot(p_drones, p_fps_mean, marker="x", linewidth=2.5, color=color_ppo, linestyle="--", label="PPO Centralizzato")
        ax.fill_between(p_drones, p_fps_mean - p_fps_std, p_fps_mean + p_fps_std, color=color_ppo, alpha=0.18)
    ax.set_title("Throughput di Simulazione (FPS - Step/s)", fontweight="bold")
    ax.set_xlabel("Numero di Droni (UAV)")
    ax.set_ylabel("Step / secondo")
    ax.set_xticks(drone_counts)
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.legend(fontsize=11)

    # 4. Tempo di Addestramento Totale (Bar Plot con barre d'errore)
    ax = axes[1, 1]
    width = 0.35
    x = np.array(drone_counts)
    if has_mappo and has_ppo:
        ax.bar(x - width/2, m_time_mean, yerr=m_time_std, capsize=5, width=width, color=color_mappo, label="MAPPO", edgecolor="black")
        ax.bar(x + width/2, p_time_mean, yerr=p_time_std, capsize=5, width=width, color=color_ppo, label="PPO Centralizzato", edgecolor="black")
    elif has_mappo:
        ax.bar(x, m_time_mean, yerr=m_time_std, capsize=5, width=width, color=color_mappo, label="MAPPO", edgecolor="black")
    ax.set_title("Tempo di Addestramento Totale (s) (Media \u00b1 \u03c3)", fontweight="bold")
    ax.set_xlabel("Numero di Droni (UAV)")
    ax.set_ylabel("Secondi (s)")
    ax.set_xticks(drone_counts)
    ax.grid(True, linestyle="--", alpha=0.6, axis="y")
    ax.legend(fontsize=11)

    # 5. Utilizzo CPU
    ax = axes[2, 0]
    if has_mappo:
        ax.plot(m_drones, m_cpu_mean, marker="o", linewidth=2.5, color=color_mappo, label="MAPPO")
        ax.fill_between(m_drones, m_cpu_mean - m_cpu_std, m_cpu_mean + m_cpu_std, color=color_mappo, alpha=0.18)
    if has_ppo:
        ax.plot(p_drones, p_cpu_mean, marker="s", linewidth=2.5, color=color_ppo, linestyle="--", label="PPO Centralizzato")
        ax.fill_between(p_drones, p_cpu_mean - p_cpu_std, p_cpu_mean + p_cpu_std, color=color_ppo, alpha=0.18)
    ax.set_title("Utilizzo Processore CPU (%)", fontweight="bold")
    ax.set_xlabel("Numero di Droni (UAV)")
    ax.set_ylabel("CPU Media (%)")
    ax.set_xticks(drone_counts)
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.legend(fontsize=11)

    # 6. Memoria RAM
    ax = axes[2, 1]
    if has_mappo:
        ax.plot(m_drones, m_ram_mean, marker="D", linewidth=2.5, color=color_mappo, label="MAPPO")
        ax.fill_between(m_drones, m_ram_mean - m_ram_std, m_ram_mean + m_ram_std, color=color_mappo, alpha=0.18)
    if has_ppo:
        ax.plot(p_drones, p_ram_mean, marker="v", linewidth=2.5, color=color_ppo, linestyle="--", label="PPO Centralizzato")
        ax.fill_between(p_drones, p_ram_mean - p_ram_std, p_ram_mean + p_ram_std, color=color_ppo, alpha=0.18)
    ax.set_title("Consumo Memoria RAM (MB)", fontweight="bold")
    ax.set_xlabel("Numero di Droni (UAV)")
    ax.set_ylabel("Megabyte (MB)")
    ax.set_xticks(drone_counts)
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.legend(fontsize=11)

    # Salvataggio
    os.makedirs(os.path.dirname(os.path.abspath(output_png)), exist_ok=True)
    plt.savefig(output_png, dpi=300, bbox_inches="tight")
    plt.close()


def export_aggregated_csv(stats, output_csv):
    """
    Salva tutte le statistiche aggregate in formato CSV standard.
    """
    sorted_keys = sorted(stats.keys(), key=lambda x: (x[0], 0 if x[1] == "MAPPO" else 1))

    fieldnames = [
        "Droni", "Algoritmo", "Num_Semi", "Semi_Utilizzati", "Timesteps",
        "Reward_Medio_mean", "Reward_Medio_std",
        "Success_Rate_pct_mean", "Success_Rate_pct_std",
        "Avg_Steps_mean", "Avg_Steps_std",
        "Tempo_s_mean", "Tempo_s_std",
        "FPS_mean", "FPS_std",
        "CPU_Media_pct_mean", "CPU_Media_pct_std",
        "CPU_Picco_pct_mean", "CPU_Picco_pct_std",
        "RAM_MB_mean", "RAM_MB_std",
        "GPU_Media_pct_mean", "GPU_Media_pct_std",
        "VRAM_MB_mean", "VRAM_MB_std"
    ]

    os.makedirs(os.path.dirname(os.path.abspath(output_csv)), exist_ok=True)
    with open(output_csv, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for (n_uavs, algo) in sorted_keys:
            st = stats[(n_uavs, algo)]
            row = {
                "Droni": n_uavs,
                "Algoritmo": algo,
                "Num_Semi": len(st.get("seeds", [])),
                "Semi_Utilizzati": "-".join(map(str, st.get("seeds", []))),
                "Timesteps": int(round(st.get("Timesteps_mean", 0))),
                "Reward_Medio_mean": f"{st['Reward_Medio_mean']:.2f}",
                "Reward_Medio_std": f"{st['Reward_Medio_std']:.2f}",
                "Success_Rate_pct_mean": f"{st['Success_Rate_pct_mean']:.2f}",
                "Success_Rate_pct_std": f"{st['Success_Rate_pct_std']:.2f}",
                "Avg_Steps_mean": f"{st['Avg_Steps_mean']:.2f}",
                "Avg_Steps_std": f"{st['Avg_Steps_std']:.2f}",
                "Tempo_s_mean": f"{st['Tempo_s_mean']:.2f}",
                "Tempo_s_std": f"{st['Tempo_s_std']:.2f}",
                "FPS_mean": f"{st['FPS_mean']:.1f}",
                "FPS_std": f"{st['FPS_std']:.1f}",
                "CPU_Media_pct_mean": f"{st['CPU_Media_pct_mean']:.2f}",
                "CPU_Media_pct_std": f"{st['CPU_Media_pct_std']:.2f}",
                "CPU_Picco_pct_mean": f"{st['CPU_Picco_pct_mean']:.2f}",
                "CPU_Picco_pct_std": f"{st['CPU_Picco_pct_std']:.2f}",
                "RAM_MB_mean": f"{st['RAM_MB_mean']:.2f}",
                "RAM_MB_std": f"{st['RAM_MB_std']:.2f}",
                "GPU_Media_pct_mean": f"{st['GPU_Media_pct_mean']:.2f}",
                "GPU_Media_pct_std": f"{st['GPU_Media_pct_std']:.2f}",
                "VRAM_MB_mean": f"{st['VRAM_MB_mean']:.2f}",
                "VRAM_MB_std": f"{st['VRAM_MB_std']:.2f}"
            }
            writer.writerow(row)


def export_markdown_and_print_summary(stats, seeds, output_md=None):
    """
    Formatta e stampa a console e su file Markdown una tabella adatta alla stesura della tesi.
    """
    sorted_keys = sorted(stats.keys(), key=lambda x: (x[0], 0 if x[1] == "MAPPO" else 1))

    seeds_str = ", ".join(map(str, seeds))
    lines = [
        f"# Benchmark Aggregato Multi-Seed (Semi: {seeds_str})",
        f"Valori medi e deviazione standard campionaria calcolati su **{len(seeds)} run indipendenti**.",
        "",
        "| Droni | Algoritmo | Timesteps | Reward Medio | Success Rate (%) | Tempo (s) | FPS | CPU Avg (%) | RAM (MB) |",
        "|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|"
    ]

    for (n_uavs, algo) in sorted_keys:
        st = stats[(n_uavs, algo)]
        r_m, r_s = st["Reward_Medio_mean"], st["Reward_Medio_std"]
        sr_m, sr_s = st["Success_Rate_pct_mean"], st["Success_Rate_pct_std"]
        t_m, t_s = st["Tempo_s_mean"], st["Tempo_s_std"]
        fps_m, fps_s = st["FPS_mean"], st["FPS_std"]
        cpu_m, cpu_s = st["CPU_Media_pct_mean"], st["CPU_Media_pct_std"]
        ram_m, ram_s = st["RAM_MB_mean"], st["RAM_MB_std"]
        timesteps = int(round(st.get("Timesteps_mean", 0)))

        line = (
            f"| {n_uavs} | **{algo}** | {timesteps:,} | "
            f"{r_m:.1f} \u00b1 {r_s:.1f} | "
            f"**{sr_m:.1f} \u00b1 {sr_s:.1f}%** | "
            f"{t_m:.1f} \u00b1 {t_s:.1f}s | "
            f"{fps_m:.0f} \u00b1 {fps_s:.0f} | "
            f"{cpu_m:.1f}% | "
            f"{ram_m:.1f} MB |"
        )
        lines.append(line)

    content = "\n".join(lines)


    if output_md:
        os.makedirs(os.path.dirname(os.path.abspath(output_md)), exist_ok=True)
        with open(output_md, "w", encoding="utf-8") as f:
            f.write(content + "\n")


def main():
    parser = argparse.ArgumentParser(description="Aggregatore Statistico Multi-Seed per Benchmark MAPPO vs PPO")
    parser.add_argument("--benchmark-dir", type=str, default=DEFAULT_BENCHMARK_DIR, help="Cartella contenente i file di benchmark")
    parser.add_argument("--seeds", type=str, default="42,123,999", help="Lista di semi separati da virgola (default: 42,123,999)")
    parser.add_argument("--output-name", type=str, default="benchmark_aggregato_multi_seed", help="Nome base dei file di output")
    args = parser.parse_args()

    requested_seeds = [int(s.strip()) for s in args.seeds.split(",") if s.strip()]
    print(f"[*] Ricerca file di benchmark per i semi: {requested_seeds} in '{args.benchmark_dir}'...")

    seed_files = find_benchmark_csvs(args.benchmark_dir, requested_seeds)
    if not seed_files:
        print("  Nessun file di benchmark trovato con i semi specificati. Interruzione.")
        return

    grouped_data, seeds_used = load_and_group_benchmarks(seed_files)
    stats = compute_statistics(grouped_data)

    out_csv = os.path.join(args.benchmark_dir, f"{args.output_name}.csv")
    out_md = os.path.join(args.benchmark_dir, f"{args.output_name}.md")
    out_png = os.path.join(args.benchmark_dir, f"{args.output_name}.png")

    export_aggregated_csv(stats, out_csv)
    export_markdown_and_print_summary(stats, seeds_used, out_md)
    generate_aggregated_plots(stats, seeds_used, out_png)

    print("\n  Aggregazione multi-seed completata con successo!\n")


if __name__ == "__main__":
    main()
