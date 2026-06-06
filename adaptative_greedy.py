import random
from heuristic import Heuristic


class AdaptiveGreedy(Heuristic):
    def __init__(self, iterations=3000):
        self.iterations = iterations

    def solve(self, parsed_data: dict) -> list[list[int]]:
        num_sensors = parsed_data["num_sensors"]
        num_zones = parsed_data["num_zones"]
        sensors = parsed_data["sensors"]
        lifetimes = parsed_data["lifetimes"]

        sensor_sets = {i: set(z) for i, z in sensors.items()}
        pool = set()
        usage_counts = {i: 0 for i in range(1, num_sensors + 1)}

        for _ in range(self.iterations):
            chromosome = [0] * num_sensors
            uncovered = set(range(1, num_zones + 1))

            while uncovered:
                cands = []
                for i in range(num_sensors):
                    if chromosome[i] == 0:
                        cov_zones = uncovered.intersection(sensor_sets[i + 1])
                        if cov_zones:
                            usage_ratio = usage_counts[i + 1] / max(1.0, lifetimes[i])
                            cost = (1.0 + usage_ratio) * random.uniform(0.8, 1.2)
                            score = len(cov_zones) / cost
                            cands.append((score, i))

                if not cands:
                    break

                cands.sort(key=lambda x: x[0], reverse=True)
                if random.random() < 0.1:
                    chosen_idx = random.choice(cands)[1]
                else:
                    top_k = min(3, len(cands))
                    chosen_idx = random.choice(cands[:top_k])[1]

                chromosome[chosen_idx] = 1
                uncovered -= sensor_sets[chosen_idx + 1]

            active_sensors = [i for i, active in enumerate(chromosome) if active]
            random.shuffle(active_sensors)

            for idx in active_sensors:
                chromosome[idx] = 0
                covered = set()
                for i, active in enumerate(chromosome):
                    if active:
                        covered.update(sensor_sets[i + 1])
                if len(covered) < num_zones:
                    chromosome[idx] = 1

            config_tuple = tuple(chromosome)
            if config_tuple not in pool:
                pool.add(config_tuple)
                for i, active in enumerate(config_tuple):
                    if active:
                        usage_counts[i + 1] += 1

        return [[i + 1 for i, val in enumerate(c) if val == 1] for c in pool]

if __name__ == "__main__":
    from tester import Tester
    Tester(AdaptiveGreedy(iterations=10000)).execute_all_tests()