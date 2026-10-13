from stable_baselines3 import PPO
from stable_baselines3.common.evaluation import evaluate_policy
from env import MultiUAVEnv

if __name__ == "__main__":
    NUM_UAVS = 2
    SIZE = 10
    SEED = 42
    NUM_OBSTACLES = 4

    # crea l'ambiente senza render per massimizzare la velocità di addestramento
    env = MultiUAVEnv(size=SIZE, num_obstacles=NUM_OBSTACLES, num_uavs=NUM_UAVS)

    # inizializza ppo con mlppolicy
    model = PPO("MlpPolicy", env, seed=SEED, verbose=1, tensorboard_log="./ppo_uav_tensorboard/")

    print("Inizio dell'addestramento...")
    # addestra per 1.500.000 step
    model.learn(total_timesteps=1500000)
    print("Addestramento completato!")

    # salva il modello addestrato
    model_name = f"ppo_multi_uav_{NUM_UAVS}_{SEED}"
    model.save(model_name)
    print(f"Modello salvato come '{model_name}.zip'")

    # valuta la performance del modello dopo l'addestramento
    mean_reward, std_reward = evaluate_policy(model, env, n_eval_episodes=10)
    print(f"Mean reward su 10 episodi: {mean_reward:.2f} +/- {std_reward:.2f}")

    env.close()
