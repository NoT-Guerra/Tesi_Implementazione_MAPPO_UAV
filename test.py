from stable_baselines3 import PPO
from env import SingleUAVEnv
import time

if __name__ == "__main__":
    # crea l'ambiente con render_mode="human" per vedere a schermo la gui
    env = SingleUAVEnv(render_mode="human", size=10)

    # carica il modello precedentemente addestrato
    try:
        model = PPO.load("ppo_single_uav")
    except FileNotFoundError:
        print("Errore: Modello non trovato. Devi prima eseguire train.py!")
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
