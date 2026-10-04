import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pygame

class SingleUAVEnv(gym.Env):
    """
    ambiente 2d su griglia per un singolo uav.
    l'obiettivo è raggiungere un target statico nel minor numero di step.
    """
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 10}

    def __init__(self, render_mode=None, size=10):
        self.size = size  # dimensione della griglia nxn
        self.window_size = 768  # dimensione della finestra pygame in pixel

        # lo stato è un vettore di 4 elementi: [uav_x, uav_y, target_x, target_y]
        self.observation_space = spaces.Box(low=0, high=size-1, shape=(4,), dtype=np.int32)

        # 5 azioni: 0: fermo, 1: destra, 2: giù, 3: sinistra, 4: su
        self.action_space = spaces.Discrete(5)
        self._action_to_direction = {
            0: np.array([0, 0]),
            1: np.array([1, 0]),
            2: np.array([0, 1]),
            3: np.array([-1, 0]),
            4: np.array([0, -1]),
        }

        self.render_mode = render_mode
        self.window = None
        self.clock = None

    def _get_obs(self):
        return np.array([
            self._agent_location[0], self._agent_location[1],
            self._target_location[0], self._target_location[1]
        ], dtype=np.int32)

    def _get_info(self):
        # distanza di manhattan tra uav e target
        return {"distance": np.linalg.norm(self._agent_location - self._target_location, ord=1)}

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        
        # posiziona l'agent casualmente
        self._agent_location = self.np_random.integers(0, self.size, size=2, dtype=np.int32)
        
        # posiziona il target casualmente, assicurandosi che non sia sopra l'agent
        self._target_location = self._agent_location
        while np.array_equal(self._target_location, self._agent_location):
            self._target_location = self.np_random.integers(0, self.size, size=2, dtype=np.int32)
            
        self.step_count = 0
            
        observation = self._get_obs()
        info = self._get_info()

        if self.render_mode == "human":
            self._render_frame()

        return observation, info

    def step(self, action):
        self.step_count += 1
        # stable-baselines3 passa l'azione come un array numpy, la converte in intero
        action = int(action)
        direction = self._action_to_direction[action]
        
        # nuova posizione potenziale
        new_location = self._agent_location + direction
        
        reward = -1.0 # penalità per ogni passo
        
        # penalità se sbatte contro i bordi
        if np.any(new_location < 0) or np.any(new_location >= self.size):
            reward -= 10.0
            
        # limita la posizione dentro la griglia
        self._agent_location = np.clip(new_location, 0, self.size - 1)
        
        # condizione di successo
        terminated = np.array_equal(self._agent_location, self._target_location)
        if terminated:
            reward += 100.0
            
        # tronca dopo 100 step per evitare episodi infiniti
        truncated = self.step_count >= 100
        
        observation = self._get_obs()
        info = self._get_info()

        if self.render_mode == "human":
            self._render_frame()

        return observation, reward, terminated, truncated, info

    def render(self):
        if self.render_mode == "human":
            return self._render_frame()

    def _render_frame(self):
        if self.window is None and self.render_mode == "human":
            pygame.init()
            pygame.display.init()
            self.window = pygame.display.set_mode((self.window_size, self.window_size))
            pygame.display.set_caption("UAV Target Search (PPO)")
            
            # carica l'immagine del drone
            try:
                import os
                img_path = os.path.join("Img", "drone.png")
                self.drone_img = pygame.image.load(img_path)
            except (FileNotFoundError, pygame.error):
                self.drone_img = None
                
            # carica l'immagine del target
            try:
                import os
                target_img_path = os.path.join("Img", "hangar.png")
                self.hangar_img = pygame.image.load(target_img_path)
            except (FileNotFoundError, pygame.error):
                self.hangar_img = None
            
        if self.clock is None and self.render_mode == "human":
            self.clock = pygame.time.Clock()

        canvas = pygame.Surface((self.window_size, self.window_size))
        canvas.fill((255, 255, 255))
        pix_square_size = (self.window_size / self.size)

        # carica l'immagine del target
        if hasattr(self, 'hangar_img') and self.hangar_img is not None:
            # ridimensiona l'immagine per essere un po' più grande della cella
            scaled_hangar = pygame.transform.scale(self.hangar_img, (int(pix_square_size * 1.2), int(pix_square_size * 1.2)))
            # calcola la posizione per centrarlo
            pos_x = self._target_location[0] * pix_square_size - (pix_square_size * 0.1)
            pos_y = self._target_location[1] * pix_square_size - (pix_square_size * 0.1)
            canvas.blit(scaled_hangar, (pos_x, pos_y))
        
        # disegna l'uav
        if hasattr(self, 'drone_img') and self.drone_img is not None:
            # ridimensiona l'immagine per farla stare bene nel quadrato
            scaled_drone = pygame.transform.scale(self.drone_img, (int(pix_square_size * 0.8), int(pix_square_size * 0.8)))
            # calcola la posizione centrata
            pos_x = self._agent_location[0] * pix_square_size + (pix_square_size * 0.1)
            pos_y = self._agent_location[1] * pix_square_size + (pix_square_size * 0.1)
            canvas.blit(scaled_drone, (pos_x, pos_y))

        # disegna la griglia
        for x in range(self.size + 1):
            pygame.draw.line(
                canvas, (200, 200, 200),
                (0, pix_square_size * x), (self.window_size, pix_square_size * x), width=2
            )
            pygame.draw.line(
                canvas, (200, 200, 200),
                (pix_square_size * x, 0), (pix_square_size * x, self.window_size), width=2
            )

        if self.render_mode == "human":
            self.window.blit(canvas, canvas.get_rect())
            pygame.event.pump()
            pygame.display.update()
            self.clock.tick(self.metadata["render_fps"])
        else:
            return np.transpose(np.array(pygame.surfarray.pixels3d(canvas)), axes=(1, 0, 2))

    def close(self):
        if self.window is not None:
            pygame.display.quit()
            pygame.quit()
