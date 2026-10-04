from stable_baselines3 import PPO
from stable_baselines3.common.evaluation import evaluate_policy
from env import SingleUAVEnv

if __name__ == "__main__":
    # crea l'ambiente senza render per massimizzare la velocità di addestramento
    env = SingleUAVEnv(size=10)

    # inizializza ppo con mlppolicy, che è perfetta per l'observation space (box)
    model = PPO("MlpPolicy", env, verbose=1, tensorboard_log="./ppo_uav_tensorboard/")

    print("Inizio dell'addestramento...")
    # addestra per 500.000 step (ora il problema è più complesso)
    model.learn(total_timesteps=500000)
    print("Addestramento completato!")

    # salva il modello addestrato
    model.save("ppo_single_uav")
    print("Modello salvato come 'ppo_single_uav.zip'")

    # valuta la performance del modello dopo l'addestramento
    mean_reward, std_reward = evaluate_policy(model, env, n_eval_episodes=10)
    print(f"Mean reward su 10 episodi: {mean_reward:.2f} +/- {std_reward:.2f}")

    env.close()
