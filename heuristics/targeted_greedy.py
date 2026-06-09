import random
from heuristic import Heuristic


class TargetedGreedy(Heuristic):
    def __init__(self, iterations=10000):
        self.iterations = iterations

    def _prune(self, num_zones, sensors, selected):
        all_zones = set(range(1, num_zones + 1))
        random.shuffle(selected)
        pruned = selected[:]
        for s_id in selected:
            pruned.remove(s_id)
            current_coverage = set()
            for active in pruned:
                current_coverage.update(sensors[active])
            if current_coverage != all_zones:
                pruned.append(s_id)
        return sorted(pruned)

    def solve(self, parsed_data: dict) -> list[list[int]]:
        num_zones = parsed_data["num_zones"]
        sensors = parsed_data["sensors"]

        zone_to_sensors = {z: [] for z in range(1, num_zones + 1)}
        for s_id, zones in sensors.items():
            for z in zones:
                zone_to_sensors[z].append(s_id)

        self.current_pool = []
        pool_set = set()

        for _ in range(self.iterations):
            uncovered = set(range(1, num_zones + 1))
            selected = []

            while uncovered:
                target_zone = random.choice(tuple(uncovered))
                candidates = zone_to_sensors[target_zone]

                best_sensors = []
                max_cov = -1

                for c_id in candidates:
                    cov_score = len(set(sensors[c_id]) & uncovered)
                    if cov_score > max_cov:
                        max_cov = cov_score
                        best_sensors = [c_id]
                    elif cov_score == max_cov:
                        best_sensors.append(c_id)

                chosen = random.choice(best_sensors)
                selected.append(chosen)
                uncovered -= set(sensors[chosen])

            final_config = self._prune(num_zones, sensors, selected)
            t_cfg = tuple(final_config)
            if t_cfg not in pool_set:
                pool_set.add(t_cfg)
                self.current_pool.append(final_config)

        return self.current_pool

if __name__ == "__main__":
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from tester import Tester
    Tester(TargetedGreedy(iterations=100000)).execute_all_tests()