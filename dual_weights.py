import random
from heuristic import Heuristic


class DualWeightsHeuristic(Heuristic):
    def __init__(self, iterations=5000, beta=1.2):
        self.iterations = iterations
        self.beta = beta

    def _prune(self, num_zones, sensor_sets, selected, weights):
        # On trie pour retirer les capteurs les "plus lourds" (les plus pénalisés) en premier
        selected.sort(key=lambda s: weights[s], reverse=True)
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
        lifetimes = parsed_data["lifetimes"]

        sensor_sets = {s: set(z) for s, z in sensors.items()}
        pool = set()

        # Initialize sensor weights inversely proportional to their lifetime
        weights = {}
        for s in sensors.keys():
            lt = 1.0
            if isinstance(lifetimes, dict):
                lt = lifetimes.get(s, lifetimes.get(s - 1, 1.0))
            elif isinstance(lifetimes, list):
                if 0 <= s - 1 < len(lifetimes):
                    lt = lifetimes[s - 1]
            weights[s] = 100.0 / max(1.0, lt)

        for _ in range(self.iterations):
            uncovered = set(range(1, num_zones + 1))
            selected = set()

            while uncovered:
                candidates = []
                for s_id, z_set in sensor_sets.items():
                    if s_id in selected:
                        continue
                    new_cov = len(z_set & uncovered)
                    if new_cov > 0:
                        # Score represents "Price per newly covered zone" (lower is better)
                        score = weights[s_id] / new_cov
                        candidates.append((score, s_id))

                if not candidates:
                    break

                # Take one of the top 3 best sensors (adds slight diversity)
                candidates.sort(key=lambda x: x[0])
                top_k = min(3, len(candidates))
                _, chosen_id = random.choice(candidates[:top_k])

                selected.add(chosen_id)
                uncovered -= sensor_sets[chosen_id]

            if not uncovered:
                # Prune expensive sensors first
                final_config = self._prune(num_zones, sensor_sets, list(selected), weights)
                pool.add(tuple(final_config))

                # Multiplicative weight update (penalize used sensors)
                for s in final_config:
                    weights[s] *= self.beta

                # Normalize to prevent float overflow over thousands of iterations
                max_w = max(weights.values())
                if max_w > 1e15:
                    for s in weights:
                        weights[s] /= 1e10

        return [list(c) for c in pool]


if __name__ == "__main__":
    from tester import Tester
    Tester(DualWeightsHeuristic(iterations=10000, beta=1.2)).execute_all_tests()