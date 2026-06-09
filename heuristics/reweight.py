import random
from heuristic import Heuristic


class ReweightHeuristic(Heuristic):
    def __init__(self, pool_size: int = 2000, penalty_factor: float = 1.3):
        self.pool_size = pool_size
        self.penalty_factor = penalty_factor

    def solve(self, parsed_data: dict) -> list[list[int]]:
        num_sensors = parsed_data["num_sensors"]
        num_zones = parsed_data["num_zones"]
        sensors = parsed_data["sensors"]
        lifetimes = parsed_data["lifetimes"]

        weights = [1000.0 / max(1.0, float(lifetimes[i])) for i in range(num_sensors)]
        global_pool = set()

        max_attempts = self.pool_size * 2
        attempts = 0

        while len(global_pool) < self.pool_size and attempts < max_attempts:
            attempts += 1
            uncovered = set(range(1, num_zones + 1))
            config = []

            while uncovered:
                candidates = []
                for s in range(1, num_sensors + 1):
                    if s not in config:
                        cov = len(uncovered.intersection(sensors[s]))
                        if cov > 0:
                            ratio = cov / weights[s - 1]
                            candidates.append((ratio, s))

                if not candidates:
                    break

                candidates.sort(key=lambda x: x[0], reverse=True)
                pool_k = min(3, len(candidates))
                chosen_s = random.choice(candidates[:pool_k])[1]

                config.append(chosen_s)
                uncovered -= set(sensors[chosen_s])

            config.sort(key=lambda x: weights[x - 1], reverse=True)
            active_set = set(config)
            zone_counts = {}

            for s in active_set:
                for z in sensors[s]:
                    zone_counts[z] = zone_counts.get(z, 0) + 1

            for s in list(active_set):
                if all(zone_counts[z] > 1 for z in sensors[s]):
                    active_set.remove(s)
                    for z in sensors[s]:
                        zone_counts[z] -= 1

            for s in active_set:
                weights[s - 1] *= self.penalty_factor

            global_pool.add(tuple(sorted(active_set)))

        return [list(c) for c in global_pool]


if __name__ == "__main__":
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from tester import Tester

    Tester(ReweightHeuristic(pool_size=2000, penalty_factor=1.3)).execute_all_tests()