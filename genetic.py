from heuristic import Heuristic
import random

class GeneticAlgorithm(Heuristic):
    def __init__(self, iterations: int = 1000):
        self.iterations = iterations

    def solve(self, parsed_data: dict) -> list[list[int]]:
        raise NotImplementedError("GeneticAlgorithm.solve is not implemented yet")

    def generate_random_greedy_chromosome(self, parsed_data: dict, top_k: int = 3) -> list[int]:
        num_sensors = parsed_data["num_sensors"]
        num_zones = parsed_data["num_zones"]
        sensors = parsed_data["sensors"]
        
        chromosome = [0] * num_sensors
        uncovered_zones = set(range(1, num_zones + 1))
        
        while uncovered_zones:
            candidates = []
            for sensor_id, covered in sensors.items():
                if chromosome[sensor_id - 1] == 0:
                    coverage = len(uncovered_zones.intersection(set(covered)))
                    if coverage > 0:
                        candidates.append((coverage, sensor_id))
            
            if not candidates:
                break
                
            candidates.sort(reverse=True, key=lambda x: x[0])
            pool = candidates[:top_k]
            chosen_sensor = random.choice(pool)[1]
            
            chromosome[chosen_sensor - 1] = 1
            uncovered_zones -= set(sensors[chosen_sensor])
            
        active_sensors = [i + 1 for i, val in enumerate(chromosome) if val == 1]
        random.shuffle(active_sensors)
        
        for sensor_id in active_sensors:
            chromosome[sensor_id - 1] = 0
            covered = set()
            for i, val in enumerate(chromosome):
                if val == 1:
                    covered.update(sensors[i + 1])
            if len(covered) < num_zones:
                chromosome[sensor_id - 1] = 1
                
        return chromosome

    def generate_population(self, parsed_data: dict, size: int) -> list[list[int]]:
        return [self.generate_random_greedy_chromosome(parsed_data) for _ in range(size)]