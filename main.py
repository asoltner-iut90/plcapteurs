import parse_data
from heuristic import Heuristic
from greedy import RandomPruning
import solver
import sys
import os
import glob
import time

def run_solver(file_path: str, heuristic: Heuristic) -> dict:
    data = parse_data.parse_sensor_data(file_path)
    
    # Génération du pool de configurations (heuristique agnostique)
    configurations_pool = heuristic.solve(data)
    best_config = min(configurations_pool, key=len) if configurations_pool else []
    
    results = solver.solve_sensor_scheduling(data["lifetimes"], data["sensors"], configurations_pool)
    return {
        "best_config": best_config,
        "status": results["status"],
        "objective": results["objective"],
        "schedule": results["schedule"]
    }

def get_expected_and_diff(obtained: float, out_file: str) -> tuple:
    """
    Lit le résultat attendu dans out_file s'il existe et calcule la différence en pourcentage.
    Retourne un tuple (expected_value, difference_string).
    """
    if os.path.exists(out_file):
        try:
            with open(out_file, 'r') as f:
                expected = float(f.read().strip())
            if expected != 0:
                diff_pct = ((obtained - expected) / expected) * 100
                diff_str = f"{diff_pct:+.2f}%"
            else:
                diff_str = "0.00%" if obtained == 0 else "N/A"
            return expected, diff_str
        except Exception:
            pass
    return None, "N/A"

def execute_test(n: int, heuristic: Heuristic):
    file_path = f"tests/{n:02d}.in"
    out_file = file_path.rsplit('.', 1)[0] + ".out"
    print(f"Exécution du test : {file_path}")
    
    start_time = time.time()
    try:
        res = run_solver(file_path, heuristic)
        elapsed = time.time() - start_time
        obtained = res["objective"]
        
        expected, diff_str = get_expected_and_diff(obtained, out_file)
        expected_val = expected if expected is not None else "N/A"
        
        print(f"Terminé en {elapsed:.2f}s | Obtenu: {obtained} (Attendu: {expected_val}) | Différence: {diff_str}")
        
        print("Ordonnancement choisi par le solveur :")
        has_active_config = False
        for config, duration in res["schedule"].items():
            if duration and duration > 1e-5:
                print(f"  - Capteurs {list(config)} activés pendant {duration:.2f} unités de temps")
                has_active_config = True
                
        if not has_active_config:
            print("  - Aucune configuration active trouvée.")
        print()
        
    except Exception as e:
        print(f"Erreur lors de l'exécution de {file_path} : {e}\n")

def execute_all_tests(heuristic: Heuristic):
    for i in range(1, 6):
        execute_test(i, heuristic)

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
    # Définition de l'heuristique choisie
    heuristic = RandomPruning(iterations=10000)
    
    if len(sys.argv) == 1:
        execute_all_tests(heuristic)
    elif len(sys.argv) == 2:
        num = int(sys.argv[1])
        execute_test(num, heuristic)
    else:
        print("Usage:")
        print("  python main.py                 # Exécute tous les tests")
        print("  python main.py <num>           # Exécute un test spécifique")
        sys.exit(1)