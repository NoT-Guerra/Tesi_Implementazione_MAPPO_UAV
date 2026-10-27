# Benchmark Aggregato Multi-Seed (Semi: 42, 123, 999)
Valori medi e deviazione standard campionaria calcolati su **3 run indipendenti**.

| Droni | Algoritmo | Timesteps | Reward Medio | Success Rate (%) | Tempo (s) | FPS | CPU Avg (%) | RAM (MB) |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 4 | **MAPPO** | 4,000,000 | -1083.3 ± 96.5 | **18.0 ± 6.6%** | 5375.6 ± 159.9s | 745 ± 23 | 795.9% | 354.5 MB |
| 4 | **PPO** | 4,000,000 | -1011.6 ± 163.1 | **41.0 ± 7.5%** | 3447.1 ± 67.3s | 1161 ± 22 | 425.0% | 355.9 MB |
