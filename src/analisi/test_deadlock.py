"""
Script di test per analizzare i casi di deadlock e verificare l'efficacia di:
1) Regola di precedenza sui conflitti di vertice (distanza dall'hangar + ID minore)
2) Action Masking sulle mosse invalide (bordi mappa, montagne e stazionamento volontario)
3) Meccanismo Anti-Livelock / Loop-Breaking (mascheramento delle oscillazioni A <-> B)
"""

import os
import sys
import time
import argparse
import csv
import numpy as np

# Risoluzione dinamica dei percorsi
ANALISI_DIR = os.path.abspath(os.path.dirname(__file__))
SRC_DIR = os.path.abspath(os.path.join(ANALISI_DIR, ".."))
PROJECT_ROOT = os.path.abspath(os.path.join(SRC_DIR, ".."))

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from env import MultiUAVEnv
from mappo import MAPPO
from stable_baselines3 import PPO


ACTION_NAMES = {
    0: "Fermo",
    1: "Destra",
    2: "Giu",
    3: "Sinistra",
    4: "Su",
}


DEADLOCK_SCENARIOS = {
    "caso1_lati_hangar_simmetrico": {
        "title": "Caso 1a - Contesa della stessa casella ai lati dell'hangar (2 droni)",
        "description": (
            "Hangar in (4,8). I droni D0 e D2 sono gia arrivati, mentre D1 in (5,7) e D3 in (4,6) "
            "cercano entrambi di passare per la casella (4,7) sopra l'hangar."
        ),
        "target": (4, 8),
        "obstacles": [(1, 1), (8, 1), (1, 4), (8, 4)],
        "uavs": [(4, 8), (5, 7), (4, 8), (4, 6)],
    },
    "caso1_lati_hangar_4droni": {
        "title": "Caso 1b - Contesa ai lati dell'hangar con 4 droni",
        "description": (
            "Hangar in (5,5) con montagne sopra (5,4) e sotto (5,6). "
            "D0(3,5) e D1(4,4) puntano al lato sinistro (4,5), mentre D2(7,5) e D3(6,6) puntano al lato destro (6,5)."
        ),
        "target": (5, 5),
        "obstacles": [(5, 4), (5, 6), (1, 1), (8, 8)],
        "uavs": [(3, 5), (4, 4), (7, 5), (6, 6)],
    },
    "caso2_varco_bordo_ovest": {
        "title": "Caso 2a - Montagne a 1 cella dal bordo sinistro",
        "description": (
            "Montagne in (1,5), (2,5), (3,5), (4,5) che lasciano solo la cella (0,5) libera sul bordo sinistro. "
            "Hangar in (0,7) e droni in (0,4), (1,4), (0,3) e (2,4) che devono passare da (0,5)."
        ),
        "target": (0, 7),
        "obstacles": [(1, 5), (2, 5), (3, 5), (4, 5)],
        "uavs": [(0, 4), (1, 4), (0, 3), (2, 4)],
    },
    "caso2_varco_bordo_nord": {
        "title": "Caso 2b - Montagne a 1 cella dal bordo superiore",
        "description": (
            "Montagne in (5,1), (5,2), (5,3), (5,4) che lasciano solo la cella (5,0) libera sul bordo in alto. "
            "Hangar in (7,0) e droni in (4,0), (4,1), (3,0), (4,2) che devono passare da (5,0)."
        ),
        "target": (7, 0),
        "obstacles": [(5, 1), (5, 2), (5, 3), (5, 4)],
        "uavs": [(4, 0), (4, 1), (3, 0), (4, 2)],
    },
    "caso2_corridoio_bordo_est": {
        "title": "Caso 2c - Passaggio di 1 cella lungo il bordo destro",
        "description": (
            "Montagne in (8,5), (8,6), (8,7), (7,7) che lasciano un passaggio di 1 cella sul bordo destro "
            "per arrivare all'hangar in (9,8). Droni in partenza da (9,4), (8,4), (9,3), (7,4)."
        ),
        "target": (9, 8),
        "obstacles": [(8, 5), (8, 6), (8, 7), (7, 7)],
        "uavs": [(9, 4), (8, 4), (9, 3), (7, 4)],
    },
}


class DeadlockTestEnv(MultiUAVEnv):
    """
    Sottoclasse di MultiUAVEnv per posizionare manualmente hangar, montagne e droni
    al reset dell'episodio e testare opzionalmente una regola di precedenza sui conflitti.
    """

    def __init__(self, render_mode=None, size=10, num_obstacles=4, num_uavs=4, use_precedence=False):
        super().__init__(render_mode=render_mode, size=size, num_obstacles=num_obstacles, num_uavs=num_uavs)
        self.custom_scenario = None
        self.use_precedence = use_precedence

    def set_custom_scenario(self, scenario_dict):
        self.custom_scenario = scenario_dict

    def clear_custom_scenario(self):
        self.custom_scenario = None

    def set_precedence(self, enabled: bool):
        self.use_precedence = bool(enabled)

    def reset(self, seed=None, options=None):
        obs, info = super().reset(seed=seed, options=options)

        if self.custom_scenario is not None:
            self._target_location = np.array(self.custom_scenario["target"], dtype=np.int32)
            obs_list = self.custom_scenario["obstacles"][: self.num_obstacles]
            self._obstacles = [np.array(o, dtype=np.int32) for o in obs_list]

            uav_list = self.custom_scenario["uavs"][: self.num_uavs]
            self._uav_locations = [np.array(u, dtype=np.int32) for u in uav_list]

            self._arrived = [
                bool(np.array_equal(self._uav_locations[i], self._target_location))
                for i in range(self.num_uavs)
            ]
            self._last_ind_rewards = [0.0] * self.num_uavs
            self.step_count = 0

            obs = self._get_obs()
            info = self._get_info()

            if self.render_mode == "human":
                self._render_frame()
                if self.window is not None and "title" in self.custom_scenario:
                    import pygame
                    algo_label = self.custom_scenario.get(" current_algo", "")
                    prefix = f"[{algo_label}] " if algo_label else ""
                    pygame.display.set_caption(f"{prefix}{self.custom_scenario['title']}")

        return obs, info

    def step(self, action):
        """
        Esegue un passo di simulazione. Se use_precedence=False mantiene il comportamento
        standard di MultiUAVEnv; se use_precedence=True risolve le contese su celle libere
        assegnando la precedenza al drone piu vicino all'hangar (a parita, ID minore).
        """
        self.step_count += 1
        rewards = 0.0
        ind_rewards = [0.0] * self.num_uavs

        actions = np.array(action, dtype=int).flatten()
        curr_locs = [np.copy(loc) for loc in self._uav_locations]
        curr_arrived = list(self._arrived)
        new_locations = [np.copy(loc) for loc in self._uav_locations]

        step_details = {
            "boundary_hits": [],
            "obstacle_hits": [],
            "vertex_collisions": [],
            "edge_collisions": [],
            "precedence_events": [],
            "hangar_side_contentions": [],
            "border_gap_events": [],
            "stay_actions": [],
        }

        # 1. Movimento candidato e controllo bordi / ostacoli
        for i in range(self.num_uavs):
            if curr_arrived[i]:
                new_locations[i] = np.copy(self._target_location)
                continue

            act = int(actions[i])
            if act == 0:
                step_details["stay_actions"].append(i)
            direction = self._action_to_direction[act]
            candidate_pos = curr_locs[i] + direction

            if np.any(candidate_pos < 0) or np.any(candidate_pos >= self.size):
                rewards -= 10.0
                ind_rewards[i] -= 10.0
                new_locations[i] = np.copy(curr_locs[i])
                step_details["boundary_hits"].append((i, tuple(int(x) for x in curr_locs[i]), act))
            elif any(np.array_equal(candidate_pos, ob) for ob in self._obstacles):
                rewards -= 10.0
                ind_rewards[i] -= 10.0
                new_locations[i] = np.copy(curr_locs[i])
                hit_ob = next(
                    tuple(int(x) for x in ob)
                    for ob in self._obstacles
                    if np.array_equal(candidate_pos, ob)
                )
                step_details["obstacle_hits"].append((i, tuple(int(x) for x in curr_locs[i]), hit_ob, act))
                if is_border_gap_cell(curr_locs[i], self._obstacles, self.size):
                    step_details["border_gap_events"].append(
                        ("obstacle_hit", i, tuple(int(x) for x in curr_locs[i]), hit_ob)
                    )
            else:
                new_locations[i] = candidate_pos

        # 2. Risoluzione conflitti tra droni
        if not self.use_precedence:
            for i in range(self.num_uavs):
                for j in range(i + 1, self.num_uavs):
                    if curr_arrived[i] and curr_arrived[j]:
                        continue

                    vertex_collision = (
                        np.array_equal(new_locations[i], new_locations[j])
                        and not np.array_equal(new_locations[i], self._target_location)
                    )
                    edge_collision = (
                        not curr_arrived[i]
                        and not curr_arrived[j]
                        and np.array_equal(new_locations[i], curr_locs[j])
                        and np.array_equal(new_locations[j], curr_locs[i])
                    )

                    if vertex_collision or edge_collision:
                        rewards -= 20.0
                        ind_rewards[i] -= 10.0
                        ind_rewards[j] -= 10.0
                        p_i = tuple(int(x) for x in curr_locs[i])
                        p_j = tuple(int(x) for x in curr_locs[j])

                        if vertex_collision:
                            c_cell = tuple(int(x) for x in new_locations[i])
                            step_details["vertex_collisions"].append((i, j, c_cell, p_i, p_j))
                            if is_adjacent_to_target(new_locations[i], self._target_location):
                                step_details["hangar_side_contentions"].append((i, j, c_cell, p_i, p_j))
                            if is_border_gap_cell(new_locations[i], self._obstacles, self.size):
                                step_details["border_gap_events"].append(("vertex_collision", (i, j), c_cell))

                        if edge_collision:
                            step_details["edge_collisions"].append((i, j, p_i, p_j))
                            if (
                                is_border_gap_cell(curr_locs[i], self._obstacles, self.size)
                                or is_border_gap_cell(curr_locs[j], self._obstacles, self.size)
                            ):
                                step_details["border_gap_events"].append(("edge_collision", (i, j), p_i, p_j))

                        new_locations[i] = np.copy(curr_locs[i])
                        new_locations[j] = np.copy(curr_locs[j])
        else:
            # 2a. Edge collisions (scambio frontale di cella): nessuno dei due puo attraversare l'altro
            for i in range(self.num_uavs):
                for j in range(i + 1, self.num_uavs):
                    if not curr_arrived[i] and not curr_arrived[j]:
                        if (
                            np.array_equal(new_locations[i], curr_locs[j])
                            and np.array_equal(new_locations[j], curr_locs[i])
                        ):
                            rewards -= 20.0
                            ind_rewards[i] -= 10.0
                            ind_rewards[j] -= 10.0
                            p_i = tuple(int(x) for x in curr_locs[i])
                            p_j = tuple(int(x) for x in curr_locs[j])
                            step_details["edge_collisions"].append((i, j, p_i, p_j))
                            if (
                                is_border_gap_cell(curr_locs[i], self._obstacles, self.size)
                                or is_border_gap_cell(curr_locs[j], self._obstacles, self.size)
                            ):
                                step_details["border_gap_events"].append(("edge_collision", (i, j), p_i, p_j))
                            new_locations[i] = np.copy(curr_locs[i])
                            new_locations[j] = np.copy(curr_locs[j])

            # 2b. Contese di vertice con regola di precedenza (e gestione cascata)
            target_tuple = tuple(int(x) for x in self._target_location)
            while True:
                cell_to_uavs = {}
                for i in range(self.num_uavs):
                    if curr_arrived[i]:
                        continue
                    c_tuple = tuple(int(x) for x in new_locations[i])
                    if c_tuple == target_tuple:
                        continue
                    cell_to_uavs.setdefault(c_tuple, []).append(i)

                contended = {c: u_list for c, u_list in cell_to_uavs.items() if len(u_list) >= 2}
                if not contended:
                    break

                for c_cell, contenders in contended.items():
                    stationary = [
                        u for u in contenders
                        if tuple(int(x) for x in curr_locs[u]) == c_cell
                    ]
                    if stationary:
                        # La cella e gia occupata da un drone fermo/bloccato: gli altri non possono entrare
                        s_uav = stationary[0]
                        p_s = tuple(int(x) for x in curr_locs[s_uav])
                        for m_uav in contenders:
                            if m_uav != s_uav:
                                rewards -= 20.0
                                ind_rewards[s_uav] -= 10.0
                                ind_rewards[m_uav] -= 10.0
                                p_m = tuple(int(x) for x in curr_locs[m_uav])
                                u1, u2 = (s_uav, m_uav) if s_uav < m_uav else (m_uav, s_uav)
                                p1, p2 = (p_s, p_m) if s_uav < m_uav else (p_m, p_s)
                                step_details["vertex_collisions"].append((u1, u2, c_cell, p1, p2))
                                if is_adjacent_to_target(c_cell, self._target_location):
                                    step_details["hangar_side_contentions"].append((u1, u2, c_cell, p1, p2))
                                if is_border_gap_cell(c_cell, self._obstacles, self.size):
                                    step_details["border_gap_events"].append(("vertex_collision", (u1, u2), c_cell))
                                new_locations[m_uav] = np.copy(curr_locs[m_uav])
                    else:
                        # Contesa di una cella libera: applica la regola di precedenza
                        # Priorita: 1) drone che si sta avvicinando all'hangar (delta_dist = -1 vs +1),
                        #           2) a parita di direzione/distanza, indice drone minore (D0 > D1 > D2 > D3)
                        next_d = int(np.linalg.norm(np.array(c_cell) - self._target_location, ord=1))

                        def _priority_key(u_idx):
                            curr_d = int(np.linalg.norm(curr_locs[u_idx] - self._target_location, ord=1))
                            delta_d = next_d - curr_d  # -1 se avanza verso l'hangar, +1 se arretra
                            return (delta_d, u_idx)

                        winner = min(contenders, key=_priority_key)
                        w_dist = int(np.linalg.norm(curr_locs[winner] - self._target_location, ord=1))
                        p_w = tuple(int(x) for x in curr_locs[winner])

                        for loser in contenders:
                            if loser != winner:
                                l_dist = int(np.linalg.norm(curr_locs[loser] - self._target_location, ord=1))
                                p_l = tuple(int(x) for x in curr_locs[loser])
                                step_details["precedence_events"].append(
                                    (winner, loser, c_cell, p_w, p_l, w_dist, l_dist)
                                )
                                new_locations[loser] = np.copy(curr_locs[loser])

        # 3. Aggiornamento posizioni e verifica arrivo all'hangar
        for i in range(self.num_uavs):
            self._uav_locations[i] = np.clip(new_locations[i], 0, self.size - 1)

            if not self._arrived[i]:
                if np.array_equal(self._uav_locations[i], self._target_location):
                    self._arrived[i] = True
                    rewards += 100.0
                    ind_rewards[i] += 100.0
                else:
                    rewards -= 1.0
                    ind_rewards[i] -= 1.0

        self._last_ind_rewards = ind_rewards

        terminated = all(self._arrived)
        truncated = self.step_count >= self.max_steps

        observation = self._get_obs()
        info = self._get_info()
        info["step_details"] = step_details

        if self.render_mode == "human":
            self._render_frame()

        return observation, rewards, terminated, truncated, info


def is_adjacent_to_target(pos, target):
    return int(np.linalg.norm(np.array(pos) - np.array(target), ord=1)) == 1


def is_border_gap_cell(pos, obstacles, size=10):
    x, y = int(pos[0]), int(pos[1])
    for ob in obstacles:
        ox, oy = int(ob[0]), int(ob[1])
        if ox == 1 and x <= 1 and abs(y - oy) <= 1:
            return True
        if ox == size - 2 and x >= size - 2 and abs(y - oy) <= 1:
            return True
        if oy == 1 and y <= 1 and abs(x - ox) <= 1:
            return True
        if oy == size - 2 and y >= size - 2 and abs(x - ox) <= 1:
            return True
    return False


def _get_action_logits(model, algo, obs, num_uavs):
    """
    Estrae i logit delle 5 azioni discrete per ciascun drone (forma: (num_uavs, 5))
    sia per MAPPO sia per PPO (Stable-Baselines3).
    """
    import torch

    if algo.lower() == "mappo":
        obs_array = np.array(obs, dtype=np.float32)
        if obs_array.ndim == 1:
            if len(obs_array) == model.obs_dim and model.num_uavs == 1:
                agent_obs = obs_array.reshape(1, model.obs_dim)
            else:
                agent_obs = model.extract_agent_observations(obs_array)
        else:
            agent_obs = obs_array
        model.actor.eval()
        with torch.no_grad():
            obs_tensor = torch.tensor(agent_obs, dtype=torch.float32, device=model.device)
            logits = model.actor.net(obs_tensor).cpu().numpy()
        return logits
    else:
        with torch.no_grad():
            obs_tensor, _ = model.policy.obs_to_tensor(obs)
            dist = model.policy.get_distribution(obs_tensor)
            if isinstance(dist.distribution, list):
                logits = np.stack(
                    [d.logits.squeeze(0).cpu().numpy() for d in dist.distribution],
                    axis=0,
                )
            else:
                logits = dist.distribution.logits.cpu().numpy().reshape(num_uavs, -1)
        return logits


def select_actions_with_mask_and_anti_livelock(
    env,
    model,
    algo,
    obs,
    prev_locs,
    visit_counts,
    blocked_cells_prev,
):
    """
    Seleziona le azioni applicando:
    1) Action Masking sulle mosse invalide (bordi mappa, montagne, azione Fermo volontaria e celle bloccate al passo precedente).
    2) Anti-Livelock / Loop-Breaking (mascheramento del ritorno immediato A <-> B e preferenza per celle meno visitate nei cicli).
    """
    num_uavs = env.num_uavs
    logits = _get_action_logits(model, algo, obs, num_uavs)
    target_pos = tuple(int(x) for x in env._target_location)
    obstacle_set = {tuple(int(x) for x in ob) for ob in env._obstacles}

    chosen_actions = np.zeros(num_uavs, dtype=int)
    mask_events = []
    anti_livelock_events = []

    for i in range(num_uavs):
        if env._arrived[i]:
            chosen_actions[i] = 0
            continue

        curr_pos = tuple(int(x) for x in env._uav_locations[i])
        raw_logits = logits[i].copy()
        raw_best = int(np.argmax(raw_logits))

        # 1. Action Masking: escludi Fermo (0), bordi mappa e ostacoli montuosi
        masked_logits = raw_logits.copy()
        masked_logits[0] = -np.inf

        cand_by_act = {}
        for a in (1, 2, 3, 4):
            d = env._action_to_direction[a]
            cand = (curr_pos[0] + int(d[0]), curr_pos[1] + int(d[1]))
            cand_by_act[a] = cand
            if cand[0] < 0 or cand[0] >= env.size or cand[1] < 0 or cand[1] >= env.size:
                masked_logits[a] = -np.inf
            elif cand in obstacle_set:
                masked_logits[a] = -np.inf

        valid_acts = [a for a in (1, 2, 3, 4) if np.isfinite(masked_logits[a])]
        if not valid_acts:
            chosen_actions[i] = 0
            continue

        # Se al passo precedente il drone era rimasto bloccato contro un altro drone fermo/in swap,
        # maschera temporaneamente quella cella se esistono altre direzioni valide
        if blocked_cells_prev[i] and len(valid_acts) > 1:
            alt_acts = [a for a in valid_acts if cand_by_act[a] not in blocked_cells_prev[i]]
            if alt_acts:
                for a in valid_acts:
                    if a not in alt_acts:
                        masked_logits[a] = -np.inf
                valid_acts = alt_acts

        best_after_mask = int(max(valid_acts, key=lambda a: masked_logits[a]))
        if best_after_mask != raw_best:
            mask_events.append((i, curr_pos, raw_best, best_after_mask))

        # 2. Anti-Livelock / Loop-Breaking
        chosen_act = best_after_mask
        cand_best = cand_by_act[best_after_mask]

        # Se una mossa valida entra direttamente nell'hangar, eseguila subito
        hangar_acts = [a for a in valid_acts if cand_by_act[a] == target_pos]
        if hangar_acts:
            chosen_act = hangar_acts[0]
            if chosen_act != best_after_mask:
                anti_livelock_events.append((i, curr_pos, best_after_mask, chosen_act, prev_locs[i]))
        elif len(valid_acts) > 1:
            # 2a. Evita oscillazione di periodo 2 (ritorno immediato alla cella t-1)
            non_back_acts = [
                a for a in valid_acts
                if prev_locs[i] is None or cand_by_act[a] != prev_locs[i]
            ]
            if prev_locs[i] is not None and cand_best == prev_locs[i] and non_back_acts:
                min_v = min(visit_counts[i].get(cand_by_act[a], 0) for a in non_back_acts)
                best_non_back = [
                    a for a in non_back_acts
                    if visit_counts[i].get(cand_by_act[a], 0) == min_v
                ]
                chosen_act = int(max(best_non_back, key=lambda a: masked_logits[a]))
                anti_livelock_events.append((i, curr_pos, best_after_mask, chosen_act, prev_locs[i]))
            # 2b. Se il drone sta gia ripassando su celle visitate (ciclo > 2 passi), preferisci celle meno visitate
            elif visit_counts[i].get(curr_pos, 0) >= 2 and visit_counts[i].get(cand_best, 0) >= 1:
                pool = non_back_acts if non_back_acts else valid_acts
                min_v = min(visit_counts[i].get(cand_by_act[a], 0) for a in pool)
                if min_v < visit_counts[i].get(cand_best, 0):
                    least_visited = [
                        a for a in pool
                        if visit_counts[i].get(cand_by_act[a], 0) == min_v
                    ]
                    chosen_act = int(max(least_visited, key=lambda a: masked_logits[a]))
                    anti_livelock_events.append((i, curr_pos, best_after_mask, chosen_act, cand_best))

        chosen_actions[i] = chosen_act

    return chosen_actions, mask_events, anti_livelock_events


def run_and_analyze_episode(env, model, algo, deterministic=True, render_delay=0.0):
    obs, info = env.reset()
    target = np.copy(env._target_location)
    obstacles = [np.copy(o) for o in env._obstacles]
    num_uavs = env.num_uavs

    history_positions = []
    step_events = []
    total_reward = 0.0
    done = False

    prev_locs = [None] * num_uavs
    visit_counts = [
        {tuple(int(x) for x in env._uav_locations[i]): 1}
        for i in range(num_uavs)
    ]
    blocked_cells_prev = [set() for _ in range(num_uavs)]

    while not done:
        if env.render_mode == "human":
            import pygame
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    env.close()
                    sys.exit(0)

        curr_locs = [np.copy(loc) for loc in env._uav_locations]
        curr_arrived = list(env._arrived)
        state_tuple = tuple(
            (int(loc[0]), int(loc[1]), bool(arr))
            for loc, arr in zip(curr_locs, curr_arrived)
        )
        history_positions.append(state_tuple)

        if env.use_precedence:
            actions, mask_events, anti_livelock_events = select_actions_with_mask_and_anti_livelock(
                env, model, algo, obs, prev_locs, visit_counts, blocked_cells_prev
            )
            env_action = actions if num_uavs > 1 else int(actions[0])
        else:
            action, _ = model.predict(obs, deterministic=deterministic)
            if algo.lower() == "mappo":
                env_action = action if num_uavs > 1 else (action[0] if hasattr(action, "__len__") else action)
            else:
                env_action = action
            actions = np.array(env_action, dtype=int).flatten()
            mask_events = []
            anti_livelock_events = []

        step_num = env.step_count + 1

        obs, reward, terminated, truncated, info = env.step(env_action)
        total_reward += reward

        details = info.get("step_details", {})
        new_locs = [np.copy(loc) for loc in env._uav_locations]

        # Aggiornamento memoria posizioni precedenti e contatori visite per Anti-Livelock
        new_blocked = [set() for _ in range(num_uavs)]
        for u1, u2, c_cell, p1, p2 in details.get("vertex_collisions", []):
            if p1 != c_cell:
                new_blocked[u1].add(c_cell)
            if p2 != c_cell:
                new_blocked[u2].add(c_cell)
        for u1, u2, p1, p2 in details.get("edge_collisions", []):
            d1 = int(np.linalg.norm(curr_locs[u1] - target, ord=1))
            d2 = int(np.linalg.norm(curr_locs[u2] - target, ord=1))
            loser = u2 if (d1, u1) <= (d2, u2) else u1
            other_pos = p1 if loser == u2 else p2
            new_blocked[loser].add(other_pos)
        blocked_cells_prev = new_blocked

        for i in range(num_uavs):
            if not curr_arrived[i]:
                c_pos = tuple(int(x) for x in curr_locs[i])
                n_pos = tuple(int(x) for x in new_locs[i])
                if n_pos != c_pos:
                    prev_locs[i] = c_pos
                    visit_counts[i][n_pos] = visit_counts[i].get(n_pos, 0) + 1

        ev = {
            "step": step_num,
            "curr_locs": [tuple(int(x) for x in loc) for loc in curr_locs],
            "curr_arrived": list(curr_arrived),
            "actions": [int(a) for a in actions],
            "boundary_hits": details.get("boundary_hits", []),
            "obstacle_hits": details.get("obstacle_hits", []),
            "vertex_collisions": details.get("vertex_collisions", []),
            "edge_collisions": details.get("edge_collisions", []),
            "precedence_events": details.get("precedence_events", []),
            "mask_events": mask_events,
            "anti_livelock_events": anti_livelock_events,
            "hangar_side_contentions": details.get("hangar_side_contentions", []),
            "border_gap_events": details.get("border_gap_events", []),
            "stay_actions": details.get("stay_actions", []),
            "new_locs": [tuple(int(x) for x in loc) for loc in new_locs],
            "moved_uavs": [
                i for i in range(num_uavs)
                if not curr_arrived[i] and not np.array_equal(curr_locs[i], new_locs[i])
            ],
        }
        step_events.append(ev)

        if env.render_mode == "human" and render_delay > 0:
            time.sleep(render_delay)

        done = terminated or truncated

    success = bool(info.get("success", False))
    regime = "SUCCESS"
    drone_kinematics = {}

    if not success:
        tail = history_positions[-30:]
        if len(set(tail)) == 1:
            regime = "STATIC_DEADLOCK"
        else:
            regime = "LIVELOCK"

        for i in range(num_uavs):
            if not env._arrived[i]:
                d_cells = [s[i][:2] for s in history_positions[-30:]]
                unique_cells = list(dict.fromkeys(d_cells))
                if len(unique_cells) == 1:
                    drone_kinematics[i] = {
                        "state": "fermo",
                        "desc": f"resta fermo nella cella {unique_cells[0]}",
                    }
                else:
                    drone_kinematics[i] = {
                        "state": "in_movimento",
                        "desc": f"si muove avanti e indietro tra le celle {unique_cells}",
                    }

    total_precedence_events = sum(len(x["precedence_events"]) for x in step_events)
    total_vertex_collisions = sum(len(x["vertex_collisions"]) for x in step_events)
    total_mask_events = sum(len(x.get("mask_events", [])) for x in step_events)
    total_anti_livelock_events = sum(len(x.get("anti_livelock_events", [])) for x in step_events)

    return {
        "success": success,
        "steps": env.step_count,
        "total_reward": total_reward,
        "arrived_count": sum(env._arrived),
        "arrived_mask": list(env._arrived),
        "target": tuple(int(x) for x in target),
        "obstacles": [tuple(int(x) for x in o) for o in obstacles],
        "regime": regime,
        "drone_kinematics": drone_kinematics,
        "step_events": step_events,
        "total_precedence_events": total_precedence_events,
        "total_vertex_collisions": total_vertex_collisions,
        "total_mask_events": total_mask_events,
        "total_anti_livelock_events": total_anti_livelock_events,
    }


def print_scenario_report(scenario_key, scenario_cfg, algo, seed, res, prec_label="", md_lines=None):
    tag = f" - {prec_label}" if prec_label else ""
    header = f"\n[{algo.upper()} - seed {seed}{tag}] {scenario_cfg['title']}"
    print(header)
    print(f"Descrizione: {scenario_cfg['description']}")
    print(f"Hangar: {res['target']} | Montagne: {res['obstacles']} | Droni iniziali: {scenario_cfg['uavs']}")

    if md_lines is not None:
        md_lines.append(f"### [{algo.upper()} - seed {seed}{tag}] {scenario_cfg['title']}")
        md_lines.append(f"{scenario_cfg['description']}")
        md_lines.append(f"- Hangar: `{res['target']}` | Montagne: `{res['obstacles']}` | Droni: `{scenario_cfg['uavs']}`\n")
        md_lines.append("```text")

    evs = res["step_events"]
    steps_to_show = list(range(min(8, len(evs))))
    for idx in range(max(0, len(evs) - 3), len(evs)):
        if idx not in steps_to_show:
            steps_to_show.append(idx)
    steps_to_show.sort()

    last_idx = -1
    for idx in steps_to_show:
        if last_idx != -1 and idx > last_idx + 1:
            sep_line = f"  ... (dal passo {last_idx + 2} al {idx} si ripete lo stesso comportamento) ..."
            print(sep_line)
            if md_lines is not None:
                md_lines.append(sep_line)
        ev = evs[idx]
        act_desc = ", ".join(
            f"D{i}:{'arrivato' if ev['curr_arrived'][i] else ACTION_NAMES[ev['actions'][i]]}"
            for i in range(len(ev["actions"]))
        )
        events_list = []
        for i, c_pos, raw_a, new_a in ev.get("mask_events", []):
            events_list.append(
                f"mask D{i}{c_pos}: {ACTION_NAMES[raw_a]}->{ACTION_NAMES[new_a]}"
            )
        for i, c_pos, old_a, new_a, _ in ev.get("anti_livelock_events", []):
            events_list.append(
                f"anti-loop D{i}{c_pos}: {ACTION_NAMES[old_a]}->{ACTION_NAMES[new_a]}"
            )
        for w, l, c_cell, pw, pl, dw, dl in ev.get("precedence_events", []):
            events_list.append(
                f"precedenza su {c_cell}: passa D{w}{pw} (dist={dw}), attende D{l}{pl} (dist={dl})"
            )
        for i, j, c_cell, pi, pj in ev["hangar_side_contentions"]:
            events_list.append(
                f"scontro tra D{i}{pi} e D{j}{pj} sulla cella {c_cell} a lato dell'hangar"
            )
        for i, j, c_cell, pi, pj in ev["vertex_collisions"]:
            if not any(c_cell == h[2] for h in ev["hangar_side_contentions"]):
                events_list.append(
                    f"scontro tra D{i}{pi} e D{j}{pj} sulla cella {c_cell}"
                )
        for i, j, pi, pj in ev["edge_collisions"]:
            events_list.append(
                f"scambio di posizione bloccato tra D{i}{pi} e D{j}{pj}"
            )
        for i, pi, ob, act in ev["obstacle_hits"]:
            events_list.append(
                f"D{i} da {pi} colpisce la montagna in {ob}"
            )
        for i, pi, act in ev["boundary_hits"]:
            events_list.append(
                f"D{i} da {pi} tocca il bordo mappa"
            )
        if ev["stay_actions"]:
            events_list.append(f"droni fermi: {['D' + str(d) for d in ev['stay_actions']]}")

        outcome_str = " | ".join(events_list) if events_list else f"droni mossi: {ev['moved_uavs']}"
        line1 = f"Step {ev['step']:3d}: pos={ev['curr_locs']} | azioni=[{act_desc}]"
        line2 = f"          -> nuove pos={ev['new_locs']} ({outcome_str})"
        print(line1)
        print(line2)
        if md_lines is not None:
            md_lines.append(line1)
            md_lines.append(line2)
        last_idx = idx

    if md_lines is not None:
        md_lines.append("```\n")

    if res["success"]:
        msg = (
            f"Esito: completato in {res['steps']} step "
            f"(reward: {res['total_reward']:.1f}, precedenze: {res['total_precedence_events']}, "
            f"action-mask: {res['total_mask_events']}, anti-loop: {res['total_anti_livelock_events']})"
        )
        print(msg)
        if md_lines is not None:
            md_lines.append(f"- {msg}\n")
    else:
        msg = (
            f"Esito: fallimento per timeout a {res['steps']} step "
            f"(reward: {res['total_reward']:.1f}, droni arrivati: {res['arrived_count']}/{len(res['arrived_mask'])}, "
            f"precedenze: {res['total_precedence_events']}, action-mask: {res['total_mask_events']}, "
            f"anti-loop: {res['total_anti_livelock_events']})"
        )
        print(msg)
        if res["regime"] == "STATIC_DEADLOCK":
            kin_msg = "Comportamento: i droni rimangono effettivamente bloccati"
        else:
            kin_msg = "Comportamento: i droni continuano a muoversi senza progredire"
        print(kin_msg)

        if md_lines is not None:
            md_lines.append(f"- {msg}")
            md_lines.append(f"- {kin_msg}")

        for d_idx, k_info in res["drone_kinematics"].items():
            d_line = f"  - Drone D{d_idx}: {k_info['desc']}"
            print(d_line)
            if md_lines is not None:
                md_lines.append(d_line)
        if md_lines is not None:
            md_lines.append("")


def _compute_survey_metrics(all_episodes):
    total_ep = len(all_episodes)
    failed_ep = [e for e in all_episodes if not e["success"]]
    n_fail = len(failed_ep)
    n_succ = total_ep - n_fail

    total_stuck_drones = 0
    immobile_drones = 0
    oscillating_drones = 0

    cause_hangar_side_any = 0
    cause_hangar_side_persistent = 0
    cause_border_gap_any = 0
    cause_border_gap_persistent = 0

    total_vertex_collisions = sum(e["total_vertex_collisions"] for e in all_episodes)
    total_precedence_events = sum(e["total_precedence_events"] for e in all_episodes)
    episodes_with_precedence = sum(1 for e in all_episodes if e["total_precedence_events"] > 0)
    total_mask_events = sum(e["total_mask_events"] for e in all_episodes)
    total_anti_livelock_events = sum(e["total_anti_livelock_events"] for e in all_episodes)

    for e in failed_ep:
        for _, k_info in e["drone_kinematics"].items():
            total_stuck_drones += 1
            if k_info["state"] == "fermo":
                immobile_drones += 1
            else:
                oscillating_drones += 1

        evs = e["step_events"]
        tail_evs = evs[-30:]

        hs_all = sum(len(x["hangar_side_contentions"]) for x in evs)
        bg_all = sum(len(x["border_gap_events"]) for x in evs)

        if hs_all > 0:
            cause_hangar_side_any += 1
        if bg_all > 0:
            cause_border_gap_any += 1

        hs_tail = sum(len(x["hangar_side_contentions"]) for x in tail_evs)
        bg_tail = sum(len(x["border_gap_events"]) for x in tail_evs)

        if hs_tail >= 5:
            cause_hangar_side_persistent += 1
        if bg_tail >= 5:
            cause_border_gap_persistent += 1

    return {
        "total_ep": total_ep,
        "n_succ": n_succ,
        "n_fail": n_fail,
        "total_stuck_drones": total_stuck_drones,
        "immobile_drones": immobile_drones,
        "oscillating_drones": oscillating_drones,
        "cause_hangar_side_any": cause_hangar_side_any,
        "cause_hangar_side_persistent": cause_hangar_side_persistent,
        "cause_border_gap_any": cause_border_gap_any,
        "cause_border_gap_persistent": cause_border_gap_persistent,
        "total_vertex_collisions": total_vertex_collisions,
        "total_precedence_events": total_precedence_events,
        "episodes_with_precedence": episodes_with_precedence,
        "total_mask_events": total_mask_events,
        "total_anti_livelock_events": total_anti_livelock_events,
    }


def run_statistical_survey(
    models_dir,
    seeds,
    algos,
    num_uavs=4,
    episodes_per_seed=100,
    prec_modes=(False, True),
    save_csv=None,
    md_lines=None,
):
    print(f"\nStatistiche su frequenza e cause dei fallimenti ({num_uavs} droni, {episodes_per_seed} episodi per seed)")
    if md_lines is not None:
        md_lines.append(f"## Statistiche su frequenza e cause dei fallimenti ({num_uavs} droni, {episodes_per_seed} episodi/seed)\n")

    env = DeadlockTestEnv(render_mode=None, size=10, num_obstacles=4, num_uavs=num_uavs)
    env.clear_custom_scenario()
    csv_rows = []
    all_algo_metrics = {}

    for algo in algos:
        metrics_by_mode = {}
        episodes_by_mode = {}

        for use_prec in prec_modes:
            env.set_precedence(use_prec)
            all_episodes = []
            for s in seeds:
                model = load_trained_model(algo, num_uavs, s, models_dir)
                if model is None:
                    continue

                env.reset(seed=s)
                for ep in range(episodes_per_seed):
                    res = run_and_analyze_episode(env, model, algo, deterministic=True)
                    res["seed"] = s
                    res["ep"] = ep
                    all_episodes.append(res)

            if not all_episodes:
                continue

            m = _compute_survey_metrics(all_episodes)
            metrics_by_mode[use_prec] = m
            episodes_by_mode[use_prec] = all_episodes

            prec_title = (
                "CON PRECEDENZA + ACTION MASKING + ANTI-LIVELOCK"
                if use_prec
                else "SENZA PRECEDENZA (standard)"
            )
            total_ep = m["total_ep"]
            n_succ = m["n_succ"]
            n_fail = m["n_fail"]
            total_stuck_drones = m["total_stuck_drones"]
            immobile_drones = m["immobile_drones"]
            oscillating_drones = m["oscillating_drones"]
            cause_hangar_side_any = m["cause_hangar_side_any"]
            cause_hangar_side_persistent = m["cause_hangar_side_persistent"]
            cause_border_gap_any = m["cause_border_gap_any"]
            cause_border_gap_persistent = m["cause_border_gap_persistent"]

            print(f"\nRisultati {algo.upper()} - {prec_title} ({total_ep} episodi totali sui semi {seeds}):")
            print(f"Episodi completati: {n_succ}/{total_ep} ({n_succ / total_ep * 100:.1f}%)")
            print(f"Episodi falliti:    {n_fail}/{total_ep} ({n_fail / total_ep * 100:.1f}%)")
            print(
                f"Scontri di vertice totali: {m['total_vertex_collisions']} | "
                f"Precedenze: {m['total_precedence_events']} (in {m['episodes_with_precedence']}/{total_ep} ep.) | "
                f"Action-Mask: {m['total_mask_events']} | Anti-Livelock: {m['total_anti_livelock_events']}"
            )

            if md_lines is not None:
                md_lines.append(f"### Risultati {algo.upper()} - {prec_title} ({total_ep} episodi sui semi `{seeds}`)")
                md_lines.append(f"- Episodi completati: {n_succ}/{total_ep} ({n_succ / total_ep * 100:.1f}%)")
                md_lines.append(f"- Episodi falliti: {n_fail}/{total_ep} ({n_fail / total_ep * 100:.1f}%)")
                md_lines.append(
                    f"- Scontri di vertice totali: {m['total_vertex_collisions']} | "
                    f"Precedenze attivate: {m['total_precedence_events']} (in {m['episodes_with_precedence']}/{total_ep} ep.) | "
                    f"Action-Masking: {m['total_mask_events']} | Anti-Livelock: {m['total_anti_livelock_events']}"
                )

            if n_fail > 0:
                print(f"\nComportamento dei droni non arrivati ({total_stuck_drones} totali, media {total_stuck_drones / n_fail:.2f} per episodio fallito):")
                print(f"  - Rimasti bloccati nella stessa cella:    {immobile_drones}/{total_stuck_drones} ({immobile_drones / total_stuck_drones * 100:.1f}%)")
                print(f"  - In movimento continuo senza progredire: {oscillating_drones}/{total_stuck_drones} ({oscillating_drones / total_stuck_drones * 100:.1f}%)")

                print("\nFrequenza dei casi analizzati (almeno una volta nell'episodio | persistente a fine episodio):")
                print(
                    f"  - Contesa casella ai lati dell'hangar:            "
                    f"{cause_hangar_side_any}/{n_fail} ({cause_hangar_side_any / n_fail * 100:.1f}%) | "
                    f"fino a fine episodio: {cause_hangar_side_persistent}/{n_fail} ({cause_hangar_side_persistent / n_fail * 100:.1f}%)"
                )
                print(
                    f"  - Spazio di 1 cella tra montagna e bordo mappa:   "
                    f"{cause_border_gap_any}/{n_fail} ({cause_border_gap_any / n_fail * 100:.1f}%) | "
                    f"fino a fine episodio: {cause_border_gap_persistent}/{n_fail} ({cause_border_gap_persistent / n_fail * 100:.1f}%)"
                )

                if md_lines is not None:
                    md_lines.append(f"- Droni non arrivati ({total_stuck_drones} totali, media {total_stuck_drones / n_fail:.2f} per episodio fallito):")
                    md_lines.append(f"  - Rimasti bloccati nella stessa cella: {immobile_drones}/{total_stuck_drones} ({immobile_drones / total_stuck_drones * 100:.1f}%)")
                    md_lines.append(f"  - In movimento continuo senza progredire: {oscillating_drones}/{total_stuck_drones} ({oscillating_drones / total_stuck_drones * 100:.1f}%)\n")
                    md_lines.append("| Caso analizzato | Almeno una volta nell'episodio | Fino a fine episodio |")
                    md_lines.append("|:---|:---:|:---:|")
                    md_lines.append(
                        f"| Contesa casella ai lati dell'hangar | "
                        f"{cause_hangar_side_any}/{n_fail} ({cause_hangar_side_any / n_fail * 100:.1f}%) | "
                        f"{cause_hangar_side_persistent}/{n_fail} ({cause_hangar_side_persistent / n_fail * 100:.1f}%) |"
                    )
                    md_lines.append(
                        f"| Spazio di 1 cella tra montagna e bordo | "
                        f"{cause_border_gap_any}/{n_fail} ({cause_border_gap_any / n_fail * 100:.1f}%) | "
                        f"{cause_border_gap_persistent}/{n_fail} ({cause_border_gap_persistent / n_fail * 100:.1f}%) |\n"
                    )
            elif md_lines is not None:
                md_lines.append("- Nessun episodio fallito (100% di successo).\n")

            csv_rows.append({
                "Algoritmo": algo.upper(),
                "Regola_Precedenza": "ON" if use_prec else "OFF",
                "Episodi_Totali": total_ep,
                "Fallimenti": n_fail,
                "Failure_Rate_pct": f"{n_fail / total_ep * 100:.1f}",
                "Scontri_Vertice_Totali": m["total_vertex_collisions"],
                "Precedenze_Attivate": m["total_precedence_events"],
                "Action_Mask_Attivati": m["total_mask_events"],
                "Anti_Livelock_Attivati": m["total_anti_livelock_events"],
                "Droni_Immobili_pct": f"{immobile_drones / total_stuck_drones * 100:.1f}" if total_stuck_drones > 0 else "0.0",
                "Droni_Oscillanti_pct": f"{oscillating_drones / total_stuck_drones * 100:.1f}" if total_stuck_drones > 0 else "0.0",
                "Contesa_Lati_Hangar_Any_pct": f"{cause_hangar_side_any / n_fail * 100:.1f}" if n_fail > 0 else "0.0",
                "Contesa_Lati_Hangar_Persist_pct": f"{cause_hangar_side_persistent / n_fail * 100:.1f}" if n_fail > 0 else "0.0",
                "Varco_1Cella_Bordo_Any_pct": f"{cause_border_gap_any / n_fail * 100:.1f}" if n_fail > 0 else "0.0",
                "Varco_1Cella_Bordo_Persist_pct": f"{cause_border_gap_persistent / n_fail * 100:.1f}" if n_fail > 0 else "0.0",
            })

        all_algo_metrics[algo.lower()] = metrics_by_mode

        if False in metrics_by_mode and True in metrics_by_mode:
            m_off = metrics_by_mode[False]
            m_on = metrics_by_mode[True]
            ep_off = episodes_by_mode[False]
            ep_on = episodes_by_mode[True]
            resolved_eps = [
                (e0["seed"], e0["ep"], e1["steps"], e1["total_precedence_events"], e1["total_mask_events"], e1["total_anti_livelock_events"])
                for e0, e1 in zip(ep_off, ep_on)
                if not e0["success"] and e1["success"]
            ]
            regressed_eps = [
                (e0["seed"], e0["ep"])
                for e0, e1 in zip(ep_off, ep_on)
                if e0["success"] and not e1["success"]
            ]
            print(f"\n--- Confronto diretto {algo.upper()} (Standard vs Precedenza + Masking + Anti-Livelock) ---")
            print(f"  Success Rate: {m_off['n_succ']}/{m_off['total_ep']} ({m_off['n_succ']/m_off['total_ep']*100:.1f}%) -> {m_on['n_succ']}/{m_on['total_ep']} ({m_on['n_succ']/m_on['total_ep']*100:.1f}%)")
            print(
                f"  Scontri di vertice totali: {m_off['total_vertex_collisions']} -> {m_on['total_vertex_collisions']} "
                f"(precedenze: {m_on['total_precedence_events']}, mask: {m_on['total_mask_events']}, anti-loop: {m_on['total_anti_livelock_events']})"
            )
            print(f"  Episodi falliti risolti: {len(resolved_eps)} | Regressioni: {len(regressed_eps)}")

            if md_lines is not None:
                md_lines.append(f"#### Confronto diretto {algo.upper()} (Standard vs Precedenza + Masking + Anti-Livelock)\n")
                md_lines.append("| Metrica | Senza Precedenza (Standard) | Con Precedenza + Masking + Anti-Livelock | Differenza |")
                md_lines.append("|:---|:---:|:---:|:---:|")
                md_lines.append(
                    f"| Episodi completati | {m_off['n_succ']}/{m_off['total_ep']} ({m_off['n_succ']/m_off['total_ep']*100:.1f}%) | "
                    f"{m_on['n_succ']}/{m_on['total_ep']} ({m_on['n_succ']/m_on['total_ep']*100:.1f}%) | "
                    f"{m_on['n_succ'] - m_off['n_succ']:+d} |"
                )
                md_lines.append(
                    f"| Scontri di vertice | {m_off['total_vertex_collisions']} | {m_on['total_vertex_collisions']} | "
                    f"{m_on['total_vertex_collisions'] - m_off['total_vertex_collisions']:+d} |"
                )
                md_lines.append(
                    f"| Interventi regola di precedenza | 0 | {m_on['total_precedence_events']} (in {m_on['episodes_with_precedence']} ep.) | "
                    f"+{m_on['total_precedence_events']} |"
                )
                md_lines.append(
                    f"| Interventi Action Masking | 0 | {m_on['total_mask_events']} | +{m_on['total_mask_events']} |"
                )
                md_lines.append(
                    f"| Interventi Anti-Livelock | 0 | {m_on['total_anti_livelock_events']} | +{m_on['total_anti_livelock_events']} |"
                )
                md_lines.append(
                    f"| Contesa lati hangar (persistente) | {m_off['cause_hangar_side_persistent']} | {m_on['cause_hangar_side_persistent']} | "
                    f"{m_on['cause_hangar_side_persistent'] - m_off['cause_hangar_side_persistent']:+d} |"
                )
                md_lines.append(
                    f"| Varco 1 cella sul bordo (persistente) | {m_off['cause_border_gap_persistent']} | {m_on['cause_border_gap_persistent']} | "
                    f"{m_on['cause_border_gap_persistent'] - m_off['cause_border_gap_persistent']:+d} |\n"
                )

    # Tabella riepilogativa unificata MAPPO vs PPO (Senza vs Con Precedenza + Masking + Anti-Livelock)
    if (
        "mappo" in all_algo_metrics
        and "ppo" in all_algo_metrics
        and False in all_algo_metrics["mappo"]
        and True in all_algo_metrics["mappo"]
        and False in all_algo_metrics["ppo"]
        and True in all_algo_metrics["ppo"]
    ):
        mm0 = all_algo_metrics["mappo"][False]
        mm1 = all_algo_metrics["mappo"][True]
        mp0 = all_algo_metrics["ppo"][False]
        mp1 = all_algo_metrics["ppo"][True]

        tot_m = mm0["total_ep"]
        tot_p = mp0["total_ep"]
        seeds_str = ", ".join(str(s) for s in seeds)

        def _fmt_int_dot(n):
            return f"{n:,}".replace(",", ".")

        def _fmt_succ_delta(m0, m1):
            diff = m1["n_succ"] - m0["n_succ"]
            pct_diff = (m1["n_succ"] / m1["total_ep"] - m0["n_succ"] / m0["total_ep"]) * 100.0
            return f"**{diff:+d} ({pct_diff:+.1f}%)**"

        def _fmt_vcol_delta(m0, m1):
            diff = m1["total_vertex_collisions"] - m0["total_vertex_collisions"]
            pct = (diff / m0["total_vertex_collisions"] * 100.0) if m0["total_vertex_collisions"] > 0 else 0.0
            return f"**{_fmt_int_dot(diff)} ({pct:+.1f}%)**"

        def _fmt_cause_cell(m, key):
            nf = m["n_fail"]
            val = m[key]
            pct = (val / nf * 100.0) if nf > 0 else 0.0
            return f"{val} / {nf} ({pct:.1f}%)"

        def _fmt_cause_delta(m0, m1, key):
            v0 = m0[key]
            v1 = m1[key]
            if v0 == 0 and v1 == 0:
                return "0"
            if v0 == 0:
                return f"{v1:+d}"
            diff = v1 - v0
            pct = (v1 - v0) / v0 * 100.0
            return f"**{diff:+d} ({pct:+.1f}%)**"

        table_title = f"### Risultati su {tot_m} episodi per algoritmo (semi `{seeds_str}`)"
        table_rows = [
            table_title,
            "",
            "| Metrica | MAPPO (Standard) | MAPPO (Precedenza + Mask + Anti-Loop) | $\\Delta$ MAPPO | PPO (Standard) | PPO (Precedenza + Mask + Anti-Loop) | $\\Delta$ PPO |",
            "| :--- | :---: | :---: | :---: | :---: | :---: | :---: |",
            (
                f"| **Episodi completati** | {mm0['n_succ']} / {tot_m} ({mm0['n_succ']/tot_m*100:.1f}%) | "
                f"**{mm1['n_succ']} / {tot_m} ({mm1['n_succ']/tot_m*100:.1f}%)** | {_fmt_succ_delta(mm0, mm1)} | "
                f"{mp0['n_succ']} / {tot_p} ({mp0['n_succ']/tot_p*100:.1f}%) | "
                f"**{mp1['n_succ']} / {tot_p} ({mp1['n_succ']/tot_p*100:.1f}%)** | {_fmt_succ_delta(mp0, mp1)} |"
            ),
            (
                f"| **Scontri di vertice totali** | {_fmt_int_dot(mm0['total_vertex_collisions'])} | "
                f"**{_fmt_int_dot(mm1['total_vertex_collisions'])}** | {_fmt_vcol_delta(mm0, mm1)} | "
                f"{_fmt_int_dot(mp0['total_vertex_collisions'])} | "
                f"**{_fmt_int_dot(mp1['total_vertex_collisions'])}** | {_fmt_vcol_delta(mp0, mp1)} |"
            ),
            (
                f"| **Interventi regola precedenza** | 0 | **{mm1['total_precedence_events']}** (in {mm1['episodes_with_precedence']} ep.) | "
                f"+{mm1['total_precedence_events']} | 0 | **{mp1['total_precedence_events']}** (in {mp1['episodes_with_precedence']} ep.) | "
                f"+{mp1['total_precedence_events']} |"
            ),
            (
                f"| **Interventi Action Masking** | 0 | **{_fmt_int_dot(mm1['total_mask_events'])}** | "
                f"+{_fmt_int_dot(mm1['total_mask_events'])} | 0 | **{_fmt_int_dot(mp1['total_mask_events'])}** | "
                f"+{_fmt_int_dot(mp1['total_mask_events'])} |"
            ),
            (
                f"| **Interventi Anti-Livelock** | 0 | **{_fmt_int_dot(mm1['total_anti_livelock_events'])}** | "
                f"+{_fmt_int_dot(mm1['total_anti_livelock_events'])} | 0 | **{_fmt_int_dot(mp1['total_anti_livelock_events'])}** | "
                f"+{_fmt_int_dot(mp1['total_anti_livelock_events'])} |"
            ),
            (
                f"| **Contesa lati hangar (persistente)** | {_fmt_cause_cell(mm0, 'cause_hangar_side_persistent')} | "
                f"**{_fmt_cause_cell(mm1, 'cause_hangar_side_persistent')}** | {_fmt_cause_delta(mm0, mm1, 'cause_hangar_side_persistent')} | "
                f"{_fmt_cause_cell(mp0, 'cause_hangar_side_persistent')} | "
                f"**{_fmt_cause_cell(mp1, 'cause_hangar_side_persistent')}** | {_fmt_cause_delta(mp0, mp1, 'cause_hangar_side_persistent')} |"
            ),
            (
                f"| **Varco 1 cella sul bordo (persistente)** | {_fmt_cause_cell(mm0, 'cause_border_gap_persistent')} | "
                f"**{_fmt_cause_cell(mm1, 'cause_border_gap_persistent')}** | {_fmt_cause_delta(mm0, mm1, 'cause_border_gap_persistent')} | "
                f"{_fmt_cause_cell(mp0, 'cause_border_gap_persistent')} | "
                f"**{_fmt_cause_cell(mp1, 'cause_border_gap_persistent')}** | {_fmt_cause_delta(mp0, mp1, 'cause_border_gap_persistent')} |"
            ),
            "",
        ]

        print("\n" + "\n".join(table_rows))
        if md_lines is not None:
            md_lines.extend(table_rows)

    env.close()

    if save_csv and csv_rows:
        os.makedirs(os.path.dirname(os.path.abspath(save_csv)), exist_ok=True)
        with open(save_csv, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(csv_rows[0].keys()))
            writer.writeheader()
            for r in csv_rows:
                writer.writerow(r)
        print(f"\nCSV salvato in: {save_csv}")


def load_trained_model(algo, num_uavs, seed, models_dir):
    if algo.lower() == "mappo":
        candidates = [
            os.path.join(models_dir, f"mappo_uav_{num_uavs}_{seed}.pt"),
            os.path.join(PROJECT_ROOT, "models", f"SEED_{seed}", f"mappo_uav_{num_uavs}_{seed}.pt"),
        ]
        for path in candidates:
            if os.path.exists(path):
                return MAPPO.load(path)
        print(f"Checkpoint MAPPO non trovato per seed={seed} in {models_dir}")
        return None
    else:
        candidates = [
            os.path.join(models_dir, f"ppo_multi_uav_{num_uavs}_{seed}.zip"),
            os.path.join(PROJECT_ROOT, "models", f"SEED_{seed}", f"ppo_multi_uav_{num_uavs}_{seed}.zip"),
        ]
        for path in candidates:
            if os.path.exists(path):
                clean_path = path[:-4] if path.endswith(".zip") else path
                return PPO.load(clean_path)
        print(f"Checkpoint PPO non trovato per seed={seed} in {models_dir}")
        return None


def parse_args():
    parser = argparse.ArgumentParser(description="Test dei casi di deadlock con posizionamento manuale e raccolta statistiche")
    parser.add_argument(
        "--scenario",
        type=str,
        default="all",
        choices=["all"] + list(DEADLOCK_SCENARIOS.keys()),
        help="Scenario da eseguire o 'all' per tutti (default: all)",
    )
    parser.add_argument(
        "--mode",
        type=str,
        default="both",
        choices=["both", "mappo", "ppo"],
        help="Algoritmo da testare: mappo, ppo o both (default: both)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Seed del modello per i test sugli scenari fissi (default: 42)",
    )
    parser.add_argument(
        "--seeds-survey",
        type=str,
        default="42,123,999",
        help="Semi per le statistiche sui fallimenti (default: 42,123,999)",
    )
    parser.add_argument(
        "--uavs",
        type=int,
        default=4,
        help="Numero di droni (default: 4)",
    )
    parser.add_argument(
        "--models-dir",
        type=str,
        default=os.path.join(PROJECT_ROOT, "models", "EXTENDED_4UAV"),
        help="Cartella modelli (default: models/EXTENDED_4UAV)",
    )
    parser.add_argument(
        "--render",
        action="store_true",
        help="Mostra la simulazione con Pygame",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.10,
        help="Pausa tra gli step nel rendering (default: 0.10)",
    )
    parser.add_argument(
        "--no-survey",
        action="store_true",
        help="Esegue solo gli scenari fissi saltando le statistiche finali",
    )
    parser.add_argument(
        "--episodes",
        type=int,
        default=100,
        help="Numero di episodi per seed nelle statistiche (default: 100)",
    )
    parser.add_argument(
        "--precedence",
        type=str,
        default="compare",
        choices=["compare", "on", "off"],
        help="Modalita di risoluzione conflitti/blocchi: 'compare' (confronto Prima/Dopo), 'on' (attiva), 'off' (disattiva)",
    )
    parser.add_argument(
        "--save-md",
        type=str,
        default=os.path.join(PROJECT_ROOT, "benchmarks", "risultati_deadlock", "risultati_deadlock.md"),
        help="Percorso dove salvare il file markdown con i risultati",
    )
    parser.add_argument(
        "--save-csv",
        type=str,
        default=None,
        help="Percorso opzionale per salvare le statistiche in CSV",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    algos = ["mappo", "ppo"] if args.mode == "both" else [args.mode.lower()]
    scenarios_to_run = (
        list(DEADLOCK_SCENARIOS.keys()) if args.scenario == "all" else [args.scenario]
    )
    if args.precedence == "compare":
        prec_modes = (False, True)
    elif args.precedence == "on":
        prec_modes = (True,)
    else:
        prec_modes = (False,)

    md_lines = [
        f"# Risultati test deadlock: Regola di Precedenza + Action Masking + Anti-Livelock ({args.uavs} droni)\n",
        "Meccanismi testati in esecuzione (senza riaddestramento):\n"
        "1. **Regola di precedenza**: su cella libera contesa passa il drone che si avvicina all'hangar (a parità, indice minore `D0 > D1 > D2 > D3`).\n"
        "2. **Action Masking sulle mosse invalide**: mascheramento ($-\\infty$) delle direzioni che portano fuori griglia, dentro una montagna o a restare fermi volontariamente.\n"
        "3. **Anti-Livelock / Loop-Breaking**: mascheramento del ritorno immediato alla cella del passo $t-1$ ($A \\leftrightarrow B$) e preferenza per le celle meno visitate in caso di cicli.\n",
        f"## Scenari con posizionamento specifico (seed modello: {args.seed})\n",
    ]

    render_mode = "human" if args.render else None
    env = DeadlockTestEnv(render_mode=render_mode, size=10, num_obstacles=4, num_uavs=args.uavs)

    print(f"\nTest scenari di deadlock ({args.uavs} droni, seed modello: {args.seed}, modalita: {args.precedence})")

    scenario_summary_rows = []

    for algo in algos:
        model = load_trained_model(algo, args.uavs, args.seed, args.models_dir)
        if model is None:
            continue

        for sc_key in scenarios_to_run:
            sc_cfg = dict(DEADLOCK_SCENARIOS[sc_key])
            res_by_prec = {}
            for use_prec in prec_modes:
                prec_label = "CON PRECEDENZA + MASK + ANTI-LOOP" if use_prec else "SENZA PRECEDENZA (STANDARD)"
                sc_cfg[" current_algo"] = f"{algo.upper()} ({prec_label})"
                env.set_precedence(use_prec)
                env.set_custom_scenario(sc_cfg)
                res = run_and_analyze_episode(
                    env, model, algo, deterministic=True, render_delay=args.delay
                )
                res_by_prec[use_prec] = res
                print_scenario_report(
                    sc_key,
                    sc_cfg,
                    algo,
                    args.seed,
                    res,
                    prec_label=prec_label if len(prec_modes) > 1 or use_prec else "",
                    md_lines=md_lines,
                )

            if False in res_by_prec and True in res_by_prec:
                r0 = res_by_prec[False]
                r1 = res_by_prec[True]
                scenario_summary_rows.append({
                    "algo": algo.upper(),
                    "title": sc_cfg["title"],
                    "off_outcome": f"OK ({r0['steps']} step)" if r0["success"] else f"FAIL ({r0['arrived_count']}/{args.uavs} arr.)",
                    "on_outcome": f"OK ({r1['steps']} step)" if r1["success"] else f"FAIL ({r1['arrived_count']}/{args.uavs} arr.)",
                    "off_vcol": r0["total_vertex_collisions"],
                    "on_vcol": r1["total_vertex_collisions"],
                    "on_prec": r1["total_precedence_events"],
                    "on_mask": r1["total_mask_events"],
                    "on_loop": r1["total_anti_livelock_events"],
                })

    if scenario_summary_rows:
        print("\n=== Riepilogo Scenari Fissi: Standard vs Precedenza + Action Masking + Anti-Livelock ===")
        for row in scenario_summary_rows:
            print(
                f"  [{row['algo']}] {row['title']}:\n"
                f"      Standard: {row['off_outcome']} (scontri vertice: {row['off_vcol']}) -> "
                f"Con Precedenza+Mask+AntiLoop: {row['on_outcome']} "
                f"(scontri: {row['on_vcol']}, prec: {row['on_prec']}, mask: {row['on_mask']}, anti-loop: {row['on_loop']})"
            )
        md_lines.append("### Riepilogo confronto scenari fissi (Standard vs Precedenza + Masking + Anti-Livelock)\n")
        md_lines.append("| Algoritmo | Scenario | Standard | Con Precedenza + Mask + Anti-Loop | Scontri Vertice (Prima -> Dopo) | Precedenze | Action Mask | Anti-Loop |")
        md_lines.append("|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---:|")
        for row in scenario_summary_rows:
            md_lines.append(
                f"| {row['algo']} | {row['title']} | {row['off_outcome']} | **{row['on_outcome']}** | "
                f"{row['off_vcol']} -> {row['on_vcol']} | {row['on_prec']} | {row['on_mask']} | {row['on_loop']} |"
            )
        md_lines.append("")

    env.close()

    if not args.no_survey:
        survey_seeds = [int(s.strip()) for s in args.seeds_survey.split(",") if s.strip()]
        run_statistical_survey(
            models_dir=args.models_dir,
            seeds=survey_seeds,
            algos=algos,
            num_uavs=args.uavs,
            episodes_per_seed=args.episodes,
            prec_modes=prec_modes,
            save_csv=args.save_csv,
            md_lines=md_lines,
        )

    if args.save_md:
        md_path = os.path.abspath(args.save_md)
        os.makedirs(os.path.dirname(md_path), exist_ok=True)
        with open(md_path, mode="w", encoding="utf-8") as f:
            f.write("\n".join(md_lines))
        print(f"\nRisultati salvati in: {md_path}")


if __name__ == "__main__":
    main()
