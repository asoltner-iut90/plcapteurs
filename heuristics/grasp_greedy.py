import random
from heuristic import Heuristic

class GraspGreedy(Heuristic):
    def __init__(self, iterations=10000, alpha=0.8):
        self.iterations = iterations
        self.alpha = alpha

    def _prune(self, num_zones, sensor_sets, selected):
        selected.sort(key=lambda s: len(sensor_sets[s]))
        pruned = selected[:]
        for s_id in selected:
            pruned.remove(s_id)
            covered = set()
            for active in pruned:
                covered.update(sensor_sets[active])
            if len(covered) < num_zones:
                pruned.append(s_id)
        return sorted(pruned)

    def solve(self, parsed_data: dict) -> list[list[int]]:
        num_zones = parsed_data["num_zones"]
        sensors = parsed_data["sensors"]
        
        sensor_sets = {s: set(z) for s, z in sensors.items()}
        pool = set()
        
        for _ in range(self.iterations):
            uncovered = set(range(1, num_zones + 1))
            selected = set()
            
            while uncovered:
                max_cov = 0
                candidates = []
                
                for s_id, z_set in sensor_sets.items():
                    if s_id in selected:
                        continue
                    cov = len(z_set & uncovered)
                    if cov > max_cov:
                        max_cov = cov
                    if cov > 0:
                        candidates.append((cov, s_id))
                
                threshold = max_cov * self.alpha
                rcl = [s for cov, s in candidates if cov >= threshold]
                
                chosen = random.choice(rcl)
                selected.add(chosen)
                uncovered -= sensor_sets[chosen]
                
            final_config = self._prune(num_zones, sensor_sets, list(selected))
            pool.add(tuple(final_config))
            
        return [list(c) for c in pool]

if __name__ == "__main__":
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from tester import Tester
    Tester(GraspGreedy(iterations=100000, alpha=0.8)).execute_all_tests()
