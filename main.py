import parse_data
from heuristic import Heuristic
from greedy import Greedy, RandomPruning
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
        
        # Lecture du résultat attendu et différence
        expected, diff_str = get_expected_and_diff(obtained, out_file)
        expected_val = expected if expected is not None else "N/A"
        
        print(f"Terminé en {elapsed:.2f}s | Obtenu: {obtained} (Attendu: {expected_val}) | Différence: {diff_str}")
        print(f"Meilleure solution : {res['best_config']}\n")
    except Exception as e:
        print(f"Erreur lors de l'exécution de {file_path} : {e}\n")

def execute_all_tests(heuristic: Heuristic):
    for i in range(1, 6):
        execute_test(i, heuristic)

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