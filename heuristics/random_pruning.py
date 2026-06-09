import random
from heuristic import Heuristic

class Greedy(Heuristic):
    def prune(self, num_zones: int, sensors: dict, selected: list) -> list:
        """Élimine les capteurs redondants pour minimiser la configuration."""
        all_zones = set(range(1, num_zones + 1))
        for s_id in list(selected):
            current_coverage = set()
            for other_id in selected:
                if other_id != s_id:
                    current_coverage.update(sensors[other_id])
            if current_coverage == all_zones:
                selected.remove(s_id)
        return sorted(selected)

    def solve(self, parsed_data: dict) -> None:
        num_zones = parsed_data["num_zones"]
        sensors = parsed_data["sensors"]
        
        self.current_pool = []
        uncovered = set(range(1, num_zones + 1))
        selected = []
        
        while uncovered:
            best_sensor = None
            max_coverage = -1
            
            for s_id, zones in sensors.items():
                if s_id in selected:
                    continue
                coverage = len(set(zones) & uncovered)
                if coverage > max_coverage:
                    max_coverage = coverage
                    best_sensor = s_id
                    
            if max_coverage <= 0:
                return
                
            selected.append(best_sensor)
            uncovered -= set(sensors[best_sensor])
            
        config = self.prune(num_zones, sensors, selected)
        if config:
            self.current_pool.append(config)
        return


class RandomPruning(Greedy):
    def __init__(self, iterations: int = 1_000_000):
        self.iterations = iterations

    def _get_random_configuration(self, num_zones: int, sensors: dict) -> list:
        sensor_ids = list(sensors.keys())
        random.shuffle(sensor_ids)
        
        selected = []
        uncovered = set(range(1, num_zones + 1))
        
        for s_id in sensor_ids:
            if not uncovered:
                break
            selected.append(s_id)
            uncovered -= set(sensors[s_id])
            
        if uncovered:
            return []
            
        return self.prune(num_zones, sensors, selected)

    def solve(self, parsed_data: dict) -> None:
        num_zones = parsed_data["num_zones"]
        sensors = parsed_data["sensors"]
        
        self.current_pool = []
        unique_configs = set()
        for _ in range(self.iterations):
            config = self._get_random_configuration(num_zones, sensors)
            if config:
                t_cfg = tuple(config)
                if t_cfg not in unique_configs:
                    unique_configs.add(t_cfg)
                    self.current_pool.append(config)
        return
        
if __name__ == "__main__":
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from tester import Tester
    Tester(RandomPruning(iterations=100_000)).execute_all_tests()