from stable_baselines3 import PPO
from env import MultiUAVEnv
import time

if __name__ == "__main__":
    NUM_UAVS = 2
    SIZE = 10
    SEED = 42
    NUM_OBSTACLES = 4

    # crea l'ambiente con render_mode="human" per vedere a schermo la gui
    env = MultiUAVEnv(render_mode="human", size=SIZE, num_obstacles=NUM_OBSTACLES, num_uavs=NUM_UAVS)

    model_name = f"ppo_multi_uav_{NUM_UAVS}_{SEED}"
    # carica il modello precedentemente addestrato (con fallback sul modello senza seed)
    try:
        model = PPO.load(model_name)
    except FileNotFoundError:
        fallback_name = f"ppo_multi_uav_{NUM_UAVS}"
        try:
            model = PPO.load(fallback_name)
            model_name = fallback_name
        except FileNotFoundError:
            print(f"Errore: Modello non trovato ({model_name}.zip o {fallback_name}.zip). Devi prima eseguire train.py!")
            exit(1)

    print("Avvio della simulazione visiva...")
    
    # 10 episodi di test
    for episode in range(10):
        obs, info = env.reset()
        done = False
        truncated = False
        total_reward = 0
        step = 0
        
        print(f"\n--- Episodio {episode + 1} ---")
        while not done and not truncated:
            # chiede al modello quale azione eseguire
            action, _states = model.predict(obs, deterministic=True)
            obs, reward, done, truncated, info = env.step(action)
            total_reward += reward
            step += 1
            
            # per vedere uav muoversi
            time.sleep(0.1) 
            
        if done:
            print(f"Obiettivo RAGGIUNTO in {step} step con reward totale: {total_reward:.2f}")
        elif truncated:
            print(f"Obiettivo FALLITO (massimo step raggiunti) con reward totale: {total_reward:.2f}")

    env.close()
