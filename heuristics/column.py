import random
import numpy as np
import scipy.sparse as sp
from scipy.optimize import linprog
from heuristic import Heuristic

class ColumnGeneration(Heuristic):
    def __init__(self, max_iter: int = 1500, n_initial: int = 30000, ga_pop_size: int = 50, ga_generations: int = 40):
        self.max_iter = max_iter
        self.n_initial = n_initial
        self.ga_pop_size = ga_pop_size
        self.ga_generations = ga_generations

    def _build_sets(self, sensors: dict) -> dict:
        return {s: set(zs) for s, zs in sensors.items()}

    def _prune(self, num_zones: int, sensor_sets: dict, selected: list, pi: dict = None) -> list:
        unique_selected = list(set(selected))
        if pi:
            unique_selected.sort(key=lambda x: pi.get(x, 0.0), reverse=True)
        else:
            random.shuffle(unique_selected)

        cover_counts = {z: 0 for z in range(1, num_zones + 1)}
        for s in unique_selected:
            for z in sensor_sets[s]:
                cover_counts[z] += 1

        final_selected = []
        for s in unique_selected:
            redundant = True
            for z in sensor_sets[s]:
                if cover_counts[z] <= 1:
                    redundant = False
                    break
            if redundant:
                for z in sensor_sets[s]:
                    cover_counts[z] -= 1
            else:
                final_selected.append(s)

        return sorted(final_selected)

    def _random_greedy(self, num_zones: int, sensor_sets: dict, available_sensors: list) -> list:
        uncovered = set(range(1, num_zones + 1))
        selected = []
        shuffled = random.sample(available_sensors, len(available_sensors))

        for s in shuffled:
            if not uncovered.isdisjoint(sensor_sets[s]):
                selected.append(s)
                uncovered -= sensor_sets[s]
            if not uncovered:
                break

        if uncovered:
            return None
        return self._prune(num_zones, sensor_sets, selected)

    def _dual_greedy(self, num_zones: int, sensor_sets: dict, available_sensors: list, pi: dict, noise: float = 0.0) -> list:
        uncovered = set(range(1, num_zones + 1))
        selected = []
        weights = {s: pi.get(s, 0.0) + random.random() * noise for s in available_sensors}

        while uncovered:
            best_s = None
            best_score = float('inf')
            for s in available_sensors:
                if uncovered.isdisjoint(sensor_sets[s]):
                    continue
                gain = len(sensor_sets[s] & uncovered)
                score = weights[s] / gain
                if score < best_score:
                    best_score = score
                    best_s = s
            if best_s is None:
                return None
            selected.append(best_s)
            uncovered -= sensor_sets[best_s]

        return self._prune(num_zones, sensor_sets, selected, pi)

    def _genetic_pricing(self, num_zones: int, sensor_sets: dict, all_sensors: list, pi: dict) -> list:
        population = []
        max_pi = max(pi.values()) if pi else 1.0

        for _ in range(self.ga_pop_size):
            noise = random.uniform(0.0, max_pi)
            ind = self._dual_greedy(num_zones, sensor_sets, all_sensors, pi, noise)
            if not ind:
                ind = self._random_greedy(num_zones, sensor_sets, all_sensors)
            if ind:
                cost = sum(pi.get(s, 0.0) for s in ind)
                population.append((cost, ind))

        if not population:
            return []

        population.sort(key=lambda x: x[0])
        attractive_columns = {}

        for generation in range(self.ga_generations):
            new_population = []
            elites = population[:self.ga_pop_size // 5]
            new_population.extend(elites)

            while len(new_population) < self.ga_pop_size:
                p1 = min(random.sample(population, min(3, len(population))), key=lambda x: x[0])[1]
                p2 = min(random.sample(population, min(3, len(population))), key=lambda x: x[0])[1]

                child_genes = list(set(p1) | set(p2))
                if random.random() < 0.5:
                    mutations = random.sample(all_sensors, min(5, len(all_sensors)))
                    child_genes.extend(mutations)

                child = self._prune(num_zones, sensor_sets, child_genes, pi)
                cost = sum(pi.get(s, 0.0) for s in child)
                new_population.append((cost, child))

                if cost < 1.0 - 1e-6:
                    attractive_columns[tuple(child)] = cost

            population = new_population
            population.sort(key=lambda x: x[0])

        return [list(c) for c in attractive_columns.keys()]

    def solve(self, parsed_data: dict) -> list[list[int]]:
        num_zones = parsed_data["num_zones"]
        sensors = parsed_data["sensors"]
        lifetimes = parsed_data["lifetimes"]
        num_sensors = len(sensors)
        all_sensors = list(sensors.keys())
        sensor_sets = self._build_sets(sensors)

        pool = set()
        configs = []

        for _ in range(self.n_initial):
            cfg = self._random_greedy(num_zones, sensor_sets, all_sensors)
            if cfg:
                t_cfg = tuple(cfg)
                if t_cfg not in pool:
                    pool.add(t_cfg)
                    configs.append(cfg)

        b = np.array([lifetimes[s - 1] for s in range(1, num_sensors + 1)])
        stall_count = 0

        for iteration in range(self.max_iter):
            n = len(configs)
            c = -np.ones(n)

            row_indices, col_indices, data = [], [], []
            for j, cfg in enumerate(configs):
                for s in cfg:
                    row_indices.append(s - 1)
                    col_indices.append(j)
                    data.append(1.0)

            A_ub = sp.csc_matrix((data, (row_indices, col_indices)), shape=(num_sensors, n))

            res = linprog(c, A_ub=A_ub, b_ub=b, bounds=(0, None), method='highs')
            if not res.success:
                break

            pi = {s + 1: max(-res.ineqlin.marginals[s], 0.0) for s in range(num_sensors)}

            new_columns = self._genetic_pricing(num_zones, sensor_sets, all_sensors, pi)

            added = False
            for cfg in new_columns:
                t_cfg = tuple(cfg)
                if t_cfg not in pool:
                    pool.add(t_cfg)
                    configs.append(cfg)
                    added = True

            if added:
                stall_count = 0
            else:
                stall_count += 1

            if stall_count >= 3:
                break

        return configs

if __name__ == "__main__":
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from tester import Tester
    Tester(ColumnGeneration()).execute_all_tests()