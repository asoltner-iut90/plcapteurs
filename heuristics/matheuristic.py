import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import random
from heuristic import Heuristic
import solver


class Matheuristic(Heuristic):
    def __init__(self, initial_iterations=10_000, neighborhood_samples=50):
        self.initial_iterations = initial_iterations
        self.neighborhood_samples = neighborhood_samples

    def _prune(self, num_zones, sensors, selected):
        all_zones = set(range(1, num_zones + 1))
        random.shuffle(selected)
        pruned = selected[:]
        for s_id in selected:
            pruned.remove(s_id)
            current_coverage = set()
            for other_id in pruned:
                current_coverage.update(sensors[other_id])
            if current_coverage != all_zones:
                pruned.append(s_id)
        return sorted(pruned)

    def _generate_base_config(self, num_zones, sensors):
        sensor_ids = list(sensors.keys())
        random.shuffle(sensor_ids)
        selected = []
        uncovered = set(range(1, num_zones + 1))
        for s_id in sensor_ids:
            if not uncovered:
                break
            if set(sensors[s_id]) & uncovered:
                selected.append(s_id)
                uncovered -= set(sensors[s_id])
        if uncovered:
            return []
        return self._prune(num_zones, sensors, selected)

    def _get_neighborhood(self, config, parsed_data):
        num_zones = parsed_data["num_zones"]
        sensors = parsed_data["sensors"]
        neighbors = []
        
        for dropped in config:
            temp_config = [s for s in config if s != dropped]
            covered = set()
            for s_id in temp_config:
                covered.update(sensors[s_id])
            uncovered = set(range(1, num_zones + 1)) - covered
            
            alternatives = [
                s_id for s_id, zones in sensors.items()
                if s_id != dropped and s_id not in temp_config and (set(zones) & uncovered)
            ]
            
            for _ in range(min(self.neighborhood_samples, len(alternatives))):
                random.shuffle(alternatives)
                current_neighbor = temp_config[:]
                current_uncovered = uncovered.copy()
                
                for s_id in alternatives:
                    if not current_uncovered:
                        break
                    cov = set(sensors[s_id]) & current_uncovered
                    if cov:
                        current_neighbor.append(s_id)
                        current_uncovered -= cov
                        
                if not current_uncovered:
                    pruned = self._prune(num_zones, sensors, current_neighbor)
                    neighbors.append(tuple(pruned))
        return neighbors

    def solve(self, parsed_data: dict) -> None:
        num_zones = parsed_data["num_zones"]
        sensors = parsed_data["sensors"]
        lifetimes = parsed_data["lifetimes"]
        
        self.current_pool = []
        pool_set = set()
        for _ in range(self.initial_iterations):
            config = self._generate_base_config(num_zones, sensors)
            if config:
                t_cfg = tuple(config)
                if t_cfg not in pool_set:
                    pool_set.add(t_cfg)
                    self.current_pool.append(config)
                
        if not self.current_pool:
            return
            
        results = solver.solve_sensor_scheduling(lifetimes, sensors, self.current_pool)
        
        active_configs = []
        for config_tuple, duration in results["schedule"].items():
            if duration and duration > 1e-5:
                active_configs.append(config_tuple)
                
        for config in active_configs:
            neighbors = self._get_neighborhood(config, parsed_data)
            for n_cfg in neighbors:
                if n_cfg not in pool_set:
                    pool_set.add(n_cfg)
                    self.current_pool.append(list(n_cfg))
            
        return

if __name__ == "__main__":
    from tester import Tester
    Tester(Matheuristic(1000, 50)).execute_all_tests()