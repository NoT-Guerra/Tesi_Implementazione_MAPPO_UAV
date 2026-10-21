import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pygame
import os

class SingleUAVEnv(gym.Env):
    """
    Ambiente 2D su griglia per un singolo UAV.
    L'obiettivo è raggiungere un target statico nel minor numero di step.
    """
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 10}

    def __init__(self, render_mode=None, size=10, num_obstacles=4):
        self.size = size  # dimensione della griglia nxn
        self.window_size = 768  # dimensione della finestra pygame in pixel
        self.num_obstacles = num_obstacles

        # lo stato è un vettore: [uav_x, uav_y, target_x, target_y] + 2 coordinate per ogni ostacolo
        self.observation_space = spaces.Box(low=0, high=size-1, shape=(4 + self.num_obstacles * 2,), dtype=np.int32)

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
        obs = [
            self._agent_location[0], self._agent_location[1],
            self._target_location[0], self._target_location[1]
        ]
        for ob in self._obstacles:
            obs.extend([ob[0], ob[1]])
        return np.array(obs, dtype=np.int32)

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
            
        # posiziona le montagne casualmente
        self._obstacles = []
        for _ in range(self.num_obstacles):
            obs_loc = self.np_random.integers(0, self.size, size=2, dtype=np.int32)
            while np.array_equal(obs_loc, self._agent_location) or \
                  np.array_equal(obs_loc, self._target_location) or \
                  any(np.array_equal(obs_loc, o) for o in self._obstacles):
                obs_loc = self.np_random.integers(0, self.size, size=2, dtype=np.int32)
            self._obstacles.append(obs_loc)
            
        self.step_count = 0
            
        observation = self._get_obs()
        info = self._get_info()

        if self.render_mode == "human":
            self._render_frame()

        return observation, info

    def step(self, action):
        self.step_count += 1
        action = int(action)
        direction = self._action_to_direction[action]
        
        new_location = self._agent_location + direction
        reward = -1.0 # penalità per ogni passo
        
        # penalità se sbatte contro i bordi
        if np.any(new_location < 0) or np.any(new_location >= self.size):
            reward -= 10.0
            
        new_location = np.clip(new_location, 0, self.size - 1)
        
        # check collisione montagne
        hit_obstacle = False
        for obs in self._obstacles:
            if np.array_equal(new_location, obs):
                hit_obstacle = True
                break
                
        if hit_obstacle:
            reward -= 10.0
            new_location = self._agent_location
            
        self._agent_location = new_location
        
        terminated = np.array_equal(self._agent_location, self._target_location)
        if terminated:
            reward += 100.0
            
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
            
            try:
                img_path = os.path.join("Img", "drone.png")
                self.drone_img = pygame.image.load(img_path)
            except (FileNotFoundError, pygame.error):
                self.drone_img = None
                
            try:
                target_img_path = os.path.join("Img", "hangar.png")
                self.hangar_img = pygame.image.load(target_img_path)
            except (FileNotFoundError, pygame.error):
                self.hangar_img = None
                
            try:
                mountain_img_path = os.path.join("Img", "montagna.png")
                self.mountain_img = pygame.image.load(mountain_img_path)
            except (FileNotFoundError, pygame.error):
                self.mountain_img = None
            
        if self.clock is None and self.render_mode == "human":
            self.clock = pygame.time.Clock()

        canvas = pygame.Surface((self.window_size, self.window_size))
        canvas.fill((255, 255, 255))
        pix_square_size = (self.window_size / self.size)

        if hasattr(self, 'hangar_img') and self.hangar_img is not None:
            scaled_hangar = pygame.transform.scale(self.hangar_img, (int(pix_square_size * 1.2), int(pix_square_size * 1.2)))
            pos_x = self._target_location[0] * pix_square_size - (pix_square_size * 0.1)
            pos_y = self._target_location[1] * pix_square_size - (pix_square_size * 0.1)
            canvas.blit(scaled_hangar, (pos_x, pos_y))
            
        if hasattr(self, 'mountain_img') and self.mountain_img is not None:
            scaled_mountain = pygame.transform.scale(self.mountain_img, (int(pix_square_size * 1.0), int(pix_square_size * 1.0)))
            for obs in self._obstacles:
                pos_x = obs[0] * pix_square_size
                pos_y = obs[1] * pix_square_size
                canvas.blit(scaled_mountain, (pos_x, pos_y))
        
        if hasattr(self, 'drone_img') and self.drone_img is not None:
            scaled_drone = pygame.transform.scale(self.drone_img, (int(pix_square_size * 0.8), int(pix_square_size * 0.8)))
            pos_x = self._agent_location[0] * pix_square_size + (pix_square_size * 0.1)
            pos_y = self._agent_location[1] * pix_square_size + (pix_square_size * 0.1)
            canvas.blit(scaled_drone, (pos_x, pos_y))

        for x in range(self.size + 1):
            pygame.draw.line(canvas, (200, 200, 200), (0, pix_square_size * x), (self.window_size, pix_square_size * x), width=2)
            pygame.draw.line(canvas, (200, 200, 200), (pix_square_size * x, 0), (pix_square_size * x, self.window_size), width=2)

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


class MultiUAVEnv(gym.Env):
    """
    Ambiente 2D su griglia parametrico per N droni (Multi-UAV).
    Tutti i droni cooperano per raggiungere lo STESSO target (Hangar),
    evitando bordi, ostacoli e collisioni reciproche in volo.
    """
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 10}

    def __init__(self, render_mode=None, size=10, num_obstacles=4, num_uavs=2):
        super(MultiUAVEnv, self).__init__()

        self.size = size  # dimensione griglia NxN
        self.window_size = 768  # dimensione finestra Pygame in pixel
        self.num_obstacles = num_obstacles  # numero di montagne/ostacoli
        self.num_uavs = num_uavs  # PARAMETRICO: numero di droni nella flotta
        self.max_steps = 100

        # Spazio delle Azioni: MultiDiscrete con 5 azioni per ciascun drone
        # [0: Fermo, 1: Destra, 2: Giù, 3: Sinistra, 4: Su]
        self.action_space = spaces.MultiDiscrete([5] * self.num_uavs)

        # Spazio delle Osservazioni:
        # [UAV_0_x, UAV_0_y, ..., UAV_N_x, UAV_N_y, Target_x, Target_y, Obs_1_x, Obs_1_y, ...]
        obs_shape = (self.num_uavs * 2) + 2 + (self.num_obstacles * 2)
        self.observation_space = spaces.Box(
            low=0, high=size - 1, shape=(obs_shape,), dtype=np.int32
        )

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
        self.font = None

    def _get_obs(self):
        obs = []
        # 1. Coordinate di tutti i droni
        for uav in self._uav_locations:
            obs.extend([uav[0], uav[1]])
        # 2. Coordinate del Target comune
        obs.extend([self._target_location[0], self._target_location[1]])
        # 3. Coordinate degli ostacoli
        for ob in self._obstacles:
            obs.extend([ob[0], ob[1]])
        return np.array(obs, dtype=np.int32)

    def get_agent_obs(self, agent_idx, normalized=False):
        """
        Restituisce l'osservazione locale per il drone specificato (agent_idx).
        Struttura ego-centrica:
        [self_x, self_y, target_x, target_y, obs_1_x, obs_1_y, ..., other_uav_1_x, other_uav_1_y, ...]
        Se normalized=True, le coordinate sono divise per (self.size - 1.0).
        """
        scale = float(self.size - 1.0) if normalized else 1.0
        
        # 1. Coordinate proprie (ego-centriche)
        obs = [
            float(self._uav_locations[agent_idx][0]) / scale,
            float(self._uav_locations[agent_idx][1]) / scale,
            float(self._target_location[0]) / scale,
            float(self._target_location[1]) / scale,
        ]
        # 2. Coordinate ostacoli
        for ob in self._obstacles:
            obs.extend([float(ob[0]) / scale, float(ob[1]) / scale])
        # 3. Coordinate altri droni
        for j in range(self.num_uavs):
            if j != agent_idx:
                obs.extend([
                    float(self._uav_locations[j][0]) / scale,
                    float(self._uav_locations[j][1]) / scale,
                ])
        return np.array(obs, dtype=np.float32)

    def get_all_agent_obs(self, normalized=False):
        """
        Restituisce le osservazioni locali di tutti i droni: matrice (num_uavs, obs_dim).
        """
        return np.array([self.get_agent_obs(i, normalized=normalized) for i in range(self.num_uavs)], dtype=np.float32)

    def get_global_state(self, normalized=False):
        """
        Restituisce lo stato globale per il Critic centralizzato di MAPPO.
        Struttura canonica: [uav_0_x, uav_0_y, ..., uav_{N-1}_x, uav_{N-1}_y, target_x, target_y, obs...]
        """
        scale = float(self.size - 1.0) if normalized else 1.0
        obs = []
        for uav in self._uav_locations:
            obs.extend([float(uav[0]) / scale, float(uav[1]) / scale])
        obs.extend([float(self._target_location[0]) / scale, float(self._target_location[1]) / scale])
        for ob in self._obstacles:
            obs.extend([float(ob[0]) / scale, float(ob[1]) / scale])
        return np.array(obs, dtype=np.float32)

    def _get_info(self):
        # Distanze di Manhattan di ciascun drone dal target comune
        distances = [
            int(np.linalg.norm(uav - self._target_location, ord=1))
            for uav in self._uav_locations
        ]
        return {
            "distances": distances,
            "arrived": list(self._arrived),
            "success": bool(all(self._arrived)),
            "individual_rewards": getattr(self, "_last_ind_rewards", [0.0] * self.num_uavs),
        }

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)

        occupied_positions = set()

        # 1. Posiziona il target comune (Hangar)
        self._target_location = self.np_random.integers(0, self.size, size=2, dtype=np.int32)
        occupied_positions.add(tuple(self._target_location))

        # 2. Posiziona gli ostacoli (Montagne)
        self._obstacles = []
        for _ in range(self.num_obstacles):
            while True:
                obs_loc = self.np_random.integers(0, self.size, size=2, dtype=np.int32)
                tup = tuple(obs_loc)
                if tup not in occupied_positions:
                    self._obstacles.append(obs_loc)
                    occupied_positions.add(tup)
                    break

        # 3. Posiziona i droni in caselle libere distinte
        self._uav_locations = []
        for _ in range(self.num_uavs):
            while True:
                uav_loc = self.np_random.integers(0, self.size, size=2, dtype=np.int32)
                tup = tuple(uav_loc)
                if tup not in occupied_positions:
                    self._uav_locations.append(uav_loc)
                    occupied_positions.add(tup)
                    break

        # Stato di arrivo dei droni
        self._arrived = [False] * self.num_uavs
        self._last_ind_rewards = [0.0] * self.num_uavs
        self.step_count = 0

        observation = self._get_obs()
        info = self._get_info()

        if self.render_mode == "human":
            self._render_frame()

        return observation, info

    def step(self, action):
        self.step_count += 1
        rewards = 0.0
        ind_rewards = [0.0] * self.num_uavs

        # Converte l'azione in un array 1D di interi
        actions = np.array(action, dtype=int).flatten()
        new_locations = [np.copy(loc) for loc in self._uav_locations]

        # 1. Movimento candidato per ciascun drone che non sia già arrivato
        for i in range(self.num_uavs):
            if self._arrived[i]:
                # Il drone è già atterrato all'hangar: resta fermo
                new_locations[i] = self._target_location
                continue

            act = int(actions[i])
            direction = self._action_to_direction[act]
            candidate_pos = self._uav_locations[i] + direction

            # Controllo bordi mappa
            if np.any(candidate_pos < 0) or np.any(candidate_pos >= self.size):
                rewards -= 10.0
                ind_rewards[i] -= 10.0
                new_locations[i] = self._uav_locations[i]
            # Controllo collisione ostacoli
            elif any(np.array_equal(candidate_pos, ob) for ob in self._obstacles):
                rewards -= 10.0
                ind_rewards[i] -= 10.0
                new_locations[i] = self._uav_locations[i]
            else:
                new_locations[i] = candidate_pos

        # 2. Controllo collisioni Drone-Drone (vertice ed edge collision)
        for i in range(self.num_uavs):
            for j in range(i + 1, self.num_uavs):
                if self._arrived[i] and self._arrived[j]:
                    continue

                # collisione di vertice: finiscono sulla stessa casella fuori dal target
                vertex_collision = (
                    np.array_equal(new_locations[i], new_locations[j])
                    and not np.array_equal(new_locations[i], self._target_location)
                )

                # collisione di spigolo (swap): scambio frontale di posizioni in volo
                edge_collision = (
                    not self._arrived[i] and not self._arrived[j]
                    and np.array_equal(new_locations[i], self._uav_locations[j])
                    and np.array_equal(new_locations[j], self._uav_locations[i])
                )

                if vertex_collision or edge_collision:
                    rewards -= 20.0  # penalità per scontro tra droni
                    ind_rewards[i] -= 10.0
                    ind_rewards[j] -= 10.0
                    # entrambi rimangono fermi alle coordinate precedenti
                    new_locations[i] = self._uav_locations[i]
                    new_locations[j] = self._uav_locations[j]

        # 3. Aggiorna posizioni e valuta arrivo all'hangar
        for i in range(self.num_uavs):
            self._uav_locations[i] = np.clip(new_locations[i], 0, self.size - 1)

            if not self._arrived[i]:
                if np.array_equal(self._uav_locations[i], self._target_location):
                    self._arrived[i] = True
                    rewards += 100.0  # Bonus per aver raggiunto l'hangar
                    ind_rewards[i] += 100.0
                else:
                    rewards -= 1.0  # Penalità temporale per ogni drone ancora in volo
                    ind_rewards[i] -= 1.0

        self._last_ind_rewards = ind_rewards

        # 4. Condizioni di terminazione
        terminated = all(self._arrived)  # Vittoria: TUTTI i droni sono all'hangar!
        truncated = self.step_count >= self.max_steps

        observation = self._get_obs()
        info = self._get_info()

        if self.render_mode == "human":
            self._render_frame()

        return observation, rewards, terminated, truncated, info

    def render(self):
        if self.render_mode == "human":
            return self._render_frame()

    def _render_frame(self):
        if self.window is None and self.render_mode == "human":
            pygame.init()
            pygame.display.init()
            self.window = pygame.display.set_mode((self.window_size, self.window_size))
            pygame.display.set_caption("Flotta Multi-UAV (Target Comune)")

            # Caricamento Sprites se presenti
            try:
                self.drone_img = pygame.image.load(os.path.join("Img", "drone.png"))
            except (FileNotFoundError, pygame.error):
                self.drone_img = None

            try:
                self.hangar_img = pygame.image.load(os.path.join("Img", "hangar.png"))
            except (FileNotFoundError, pygame.error):
                self.hangar_img = None

            try:
                self.mountain_img = pygame.image.load(os.path.join("Img", "montagna.png"))
            except (FileNotFoundError, pygame.error):
                self.mountain_img = None

        if self.clock is None and self.render_mode == "human":
            self.clock = pygame.time.Clock()

        canvas = pygame.Surface((self.window_size, self.window_size))
        canvas.fill((255, 255, 255))
        pix_square_size = (self.window_size / self.size)

        # 1. Disegna il Target Comune (Hangar)
        if hasattr(self, 'hangar_img') and self.hangar_img is not None:
            scaled_hangar = pygame.transform.scale(self.hangar_img, (int(pix_square_size * 1.2), int(pix_square_size * 1.2)))
            pos_x = self._target_location[0] * pix_square_size - (pix_square_size * 0.1)
            pos_y = self._target_location[1] * pix_square_size - (pix_square_size * 0.1)
            canvas.blit(scaled_hangar, (pos_x, pos_y))
        else:
            pygame.draw.rect(
                canvas, (220, 20, 60),
                pygame.Rect(pix_square_size * self._target_location, (pix_square_size, pix_square_size))
            )

        # 2. Disegna gli Ostacoli (Montagne)
        if hasattr(self, 'mountain_img') and self.mountain_img is not None:
            scaled_mountain = pygame.transform.scale(self.mountain_img, (int(pix_square_size * 1.0), int(pix_square_size * 1.0)))
            for obs in self._obstacles:
                pos_x = obs[0] * pix_square_size
                pos_y = obs[1] * pix_square_size
                canvas.blit(scaled_mountain, (pos_x, pos_y))
        else:
            for obs in self._obstacles:
                pygame.draw.rect(
                    canvas, (100, 100, 100),
                    pygame.Rect(pix_square_size * obs, (pix_square_size, pix_square_size))
                )

        # Palette di colori per distinguere visivamente i droni
        uav_colors = [(30, 144, 255), (255, 140, 0), (148, 0, 211), (0, 180, 0), (255, 20, 147)]

        # 3. Disegna i Droni
        for i, uav in enumerate(self._uav_locations):
            pos_x = uav[0] * pix_square_size + (pix_square_size * 0.1)
            pos_y = uav[1] * pix_square_size + (pix_square_size * 0.1)
            color = uav_colors[i % len(uav_colors)]

            if hasattr(self, 'drone_img') and self.drone_img is not None:
                scaled_drone = pygame.transform.scale(self.drone_img, (int(pix_square_size * 0.8), int(pix_square_size * 0.8)))
                # Bordo colorato per distinguere il drone
                pygame.draw.circle(
                    canvas, color,
                    (int(pos_x + pix_square_size * 0.4), int(pos_y + pix_square_size * 0.4)),
                    int(pix_square_size * 0.42), width=3
                )
                canvas.blit(scaled_drone, (pos_x, pos_y))
            else:
                pygame.draw.circle(
                    canvas, color,
                    (uav + 0.5) * pix_square_size,
                    pix_square_size / 3,
                )



        # 4. Disegna la Griglia
        for x in range(self.size + 1):
            pygame.draw.line(canvas, (200, 200, 200), (0, pix_square_size * x), (self.window_size, pix_square_size * x), width=2)
            pygame.draw.line(canvas, (200, 200, 200), (pix_square_size * x, 0), (pix_square_size * x, self.window_size), width=2)

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
