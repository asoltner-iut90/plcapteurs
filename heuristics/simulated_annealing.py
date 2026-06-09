import random
import math
from heuristic import Heuristic


class SimulatedAnnealing(Heuristic):
    def __init__(self, initial_temp=100.0, cooling_rate=0.995, iterations=5000):
        self.initial_temp = initial_temp
        self.cooling_rate = cooling_rate
        self.iterations = iterations

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

    def _generate_initial_config(self, num_zones, sensors):
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

    def _get_neighbor(self, config, num_zones, sensors):
        if not config:
            return []
        neighbor = list(config)
        dropped = random.choice(neighbor)
        neighbor.remove(dropped)

        covered = set()
        for s_id in neighbor:
            covered.update(sensors[s_id])
        uncovered = set(range(1, num_zones + 1)) - covered

        available = list(set(sensors.keys()) - set(neighbor))
        random.shuffle(available)

        for s_id in available:
            if not uncovered:
                break
            if set(sensors[s_id]) & uncovered:
                neighbor.append(s_id)
                uncovered -= set(sensors[s_id])

        return self._prune(num_zones, sensors, neighbor)

    def _calculate_cost(self, config, lifetimes):
        cost = 0.0
        for s in config:
            lt = 1.0
            if isinstance(lifetimes, dict):
                if s in lifetimes:
                    lt = lifetimes[s]
                elif (s - 1) in lifetimes:
                    lt = lifetimes[s - 1]
            elif isinstance(lifetimes, list):
                if 0 <= s - 1 < len(lifetimes):
                    lt = lifetimes[s - 1]
                elif 0 <= s < len(lifetimes):
                    lt = lifetimes[s]

            if lt <= 0 or lt is None:
                lt = 1.0
            cost += 100.0 / lt
        return cost

    def solve(self, parsed_data: dict) -> list[list[int]]:
        num_zones = parsed_data["num_zones"]
        sensors = parsed_data["sensors"]
        lifetimes = parsed_data["lifetimes"]

        current_config = self._generate_initial_config(num_zones, sensors)
        if not current_config:
            return []

        current_cost = self._calculate_cost(current_config, lifetimes)
        pool = {tuple(current_config)}
        temp = self.initial_temp

        for _ in range(self.iterations):
            neighbor = self._get_neighbor(current_config, num_zones, sensors)
            if not neighbor:
                continue

            neighbor_cost = self._calculate_cost(neighbor, lifetimes)
            delta = neighbor_cost - current_cost

            if delta <= 0 or random.random() < math.exp(-delta / temp):
                current_config = neighbor
                current_cost = neighbor_cost
                pool.add(tuple(current_config))

            temp *= self.cooling_rate
            if temp < 1e-4:
                temp = self.initial_temp

        return [list(c) for c in pool]


if __name__ == "__main__":
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from tester import Tester
    Tester(SimulatedAnnealing(initial_temp=500.0, cooling_rate=0.999, iterations=500000)).execute_all_tests()
