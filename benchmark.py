import time
import threading
import subprocess
import os
import psutil
import numpy as np
import matplotlib.pyplot as plt
from stable_baselines3 import PPO
from stable_baselines3.common.evaluation import evaluate_policy
from env import MultiUAVEnv


# CONFIGURAZIONE DEL BENCHMARK
# Testa con un numero crescente di droni
DRONE_COUNTS = [1, 2, 3, 4, 5]

# Step di addestramento per ciascun test (50.000 è ideale per un benchmark rapido)
TIMESTEPS_PER_RUN = 50000

SIZE = 10
NUM_OBSTACLES = 4
SEED = 42

def get_gpu_stats():
    """
    Rileva utilizzo istantaneo e memoria VRAM della GPU tramite nvidia-smi.
    Restituisce (gpu_util_percent, vram_used_mb).
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
    Monitor in background che campiona CPU, RAM di processo, GPU e VRAM a intervalli regolari.
    """
    def __init__(self, interval=0.3):
        super().__init__()
        self.interval = interval
        self.running = True
        self.process = psutil.Process()

        self.cpu_samples = []
        self.ram_samples = []
        self.gpu_samples = []
        self.vram_samples = []

    def run(self):
        # Campiona le risorse finché running è True
        while self.running:
            try:
                # Utilizzo CPU e memoria RAM di sistema/processo
                cpu = self.process.cpu_percent(interval=None)
                ram_mb = self.process.memory_info().rss / (1024 * 1024)
                
                # Utilizzo GPU e VRAM da nvidia-smi
                gpu_util, vram_mb = get_gpu_stats()

                if cpu > 0.0:  # Ignora il primo campione non inizializzato
                    self.cpu_samples.append(cpu)
                self.ram_samples.append(ram_mb)
                self.gpu_samples.append(gpu_util)
                self.vram_samples.append(vram_mb)
            except Exception:
                pass
            time.sleep(self.interval)

    def stop(self):
        self.running = False

    def get_summary(self):
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

def run_benchmark():
    results = []

    print(" AVVIO BENCHMARK CONSUMO RISORSE (CPU & GPU) SU PPO MULTI-UAV (MAX 5 DRONI)")
    print(f" Timesteps per configurazione: {TIMESTEPS_PER_RUN} | Griglia: {SIZE}x{SIZE} | Seed: {SEED}")

    for n_uavs in DRONE_COUNTS:
        print(f"\n>>> Test in corso: N = {n_uavs} dron{'e' if n_uavs == 1 else 'i'}...")

        # 1. Crea l'ambiente
        env = MultiUAVEnv(size=SIZE, num_obstacles=NUM_OBSTACLES, num_uavs=n_uavs)

        # 2. Inizializza PPO
        model = PPO("MlpPolicy", env, seed=SEED, verbose=0)

        # 3. Avvia il monitoraggio delle risorse
        monitor = ResourceMonitor(interval=0.3)
        monitor.start()

        # 4. Misura tempo e addestra
        start_time = time.time()
        model.learn(total_timesteps=TIMESTEPS_PER_RUN)
        elapsed_time = time.time() - start_time

        # 5. Ferma il monitoraggio
        monitor.stop()
        monitor.join()

        # 6. Calcola throughput (FPS) e valuta la policy
        fps = TIMESTEPS_PER_RUN / elapsed_time if elapsed_time > 0 else 0
        mean_rew, std_rew = evaluate_policy(model, env, n_eval_episodes=5)
        stats = monitor.get_summary()

        env.close()

        run_data = {
            "n_uavs": n_uavs,
            "time_s": elapsed_time,
            "fps": fps,
            "cpu_avg": stats["cpu_avg"],
            "cpu_max": stats["cpu_max"],
            "ram_avg": stats["ram_avg"],
            "gpu_avg": stats["gpu_avg"],
            "gpu_max": stats["gpu_max"],
            "vram_avg": stats["vram_avg"],
            "mean_reward": mean_rew,
        }
        results.append(run_data)

        print(f"    Completato in {elapsed_time:.2f}s ({fps:.1f} FPS)")
        print(f"    CPU: {stats['cpu_avg']:.1f}% (picco {stats['cpu_max']:.1f}%) | RAM: {stats['ram_avg']:.1f} MB")
        print(f"    GPU: {stats['gpu_avg']:.1f}% (picco {stats['gpu_max']:.1f}%) | VRAM: {stats['vram_avg']:.0f} MB")
        print(f"    Reward Medio (5 ep): {mean_rew:.2f}")

    # STAMPA TABELLA RIASSUNTIVA
    print("TABELLA FINALE COMPARATIVA DELLE RISORSE COMPUTAZIONALI")
    header = f"{'Droni':<6} | {'Tempo (s)':<10} | {'FPS (step/s)':<13} | {'CPU Media':<11} | {'CPU Picco':<11} | {'RAM (MB)':<10} | {'GPU Media':<11} | {'VRAM (MB)':<10} | {'Reward':<10}"
    print(header)
    for r in results:
        row = (
            f"{r['n_uavs']:<6} | "
            f"{r['time_s']:<10.2f} | "
            f"{r['fps']:<13.1f} | "
            f"{r['cpu_avg']:<10.1f}% | "
            f"{r['cpu_max']:<10.1f}% | "
            f"{r['ram_avg']:<10.1f} | "
            f"{r['gpu_avg']:<10.1f}% | "
            f"{r['vram_avg']:<10.0f} | "
            f"{r['mean_reward']:<10.2f}"
        )
        print(row)

    # SALVATAGGIO DEI RISULTATI SU FILE CSV
    csv_file = "benchmark_risultati.csv"
    with open(csv_file, "w", encoding="utf-8") as f:
        f.write("Droni,Tempo_s,FPS,CPU_Media_pct,CPU_Picco_pct,RAM_MB,GPU_Media_pct,GPU_Picco_pct,VRAM_MB,Reward_Medio\n")
        for r in results:
            f.write(f"{r['n_uavs']},{r['time_s']:.2f},{r['fps']:.1f},{r['cpu_avg']:.2f},{r['cpu_max']:.2f},{r['ram_avg']:.2f},{r['gpu_avg']:.2f},{r['gpu_max']:.2f},{r['vram_avg']:.2f},{r['mean_reward']:.2f}\n")
    print(f"\n[+] Risultati salvati in: {csv_file}")

    # GENERAZIONE GRAFICO COMPARATIVO
    droni = [r["n_uavs"] for r in results]
    fig, axes = plt.subplots(2, 2, figsize=(13, 9))
    plt.subplots_adjust(hspace=0.35, wspace=0.25)
    fig.suptitle("Analisi di Scalabilità e Consumo Risorse Hardware al variare del Numero di UAV", fontsize=15, fontweight="bold")

    # 1. Utilizzo CPU e GPU (%)
    axes[0, 0].plot(droni, [r["cpu_avg"] for r in results], marker="o", color="#d9534f", linewidth=2, label="CPU Media (%)")
    axes[0, 0].plot(droni, [r["gpu_avg"] for r in results], marker="s", color="#0275d8", linewidth=2, label="GPU Media (%)")
    axes[0, 0].set_title("Utilizzo Processore (CPU) e GPU (%)", fontweight="bold")
    axes[0, 0].set_xlabel("Numero di Droni (UAV)")
    axes[0, 0].set_ylabel("Utilizzo (%)")
    axes[0, 0].set_xticks(droni)
    axes[0, 0].grid(True, linestyle="--", alpha=0.6)
    axes[0, 0].legend()

    # 2. Throughput / Velocità di elaborazione (FPS)
    axes[0, 1].plot(droni, [r["fps"] for r in results], marker="^", color="#5cb85c", linewidth=2)
    axes[0, 1].set_title("Throughput di Calcolo (FPS - Step/secondo)", fontweight="bold")
    axes[0, 1].set_xlabel("Numero di Droni (UAV)")
    axes[0, 1].set_ylabel("Step / secondo")
    axes[0, 1].set_xticks(droni)
    axes[0, 1].grid(True, linestyle="--", alpha=0.6)

    # 3. Tempo di Addestramento Totale (s)
    axes[1, 0].bar(droni, [r["time_s"] for r in results], color="#f0ad4e", width=0.5, edgecolor="black")
    axes[1, 0].set_title(f"Tempo di Addestramento Totale ({TIMESTEPS_PER_RUN} step)", fontweight="bold")
    axes[1, 0].set_xlabel("Numero di Droni (UAV)")
    axes[1, 0].set_ylabel("Secondi (s)")
    axes[1, 0].set_xticks(droni)
    axes[1, 0].grid(True, linestyle="--", alpha=0.6, axis="y")

    # 4. Consumo Memoria RAM e VRAM (MB)
    axes[1, 1].plot(droni, [r["ram_avg"] for r in results], marker="D", color="#6f42c1", linewidth=2, label="RAM Processo (MB)")
    axes[1, 1].set_title("Utilizzo Memoria RAM (MB)", fontweight="bold")
    axes[1, 1].set_xlabel("Numero di Droni (UAV)")
    axes[1, 1].set_ylabel("Megabyte (MB)")
    axes[1, 1].set_xticks(droni)
    axes[1, 1].grid(True, linestyle="--", alpha=0.6)
    axes[1, 1].legend()

    img_file = "benchmark_risorse.png"
    plt.savefig(img_file, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[+] Grafico comparativo salvato in: {img_file}")
    print("Benchmark completato con successo!")

if __name__ == "__main__":
    run_benchmark()
