import parse_data
import glouton
import random_prunning
import solver
import sys
import os
import glob
import time

def run_solver(file_path: str) -> dict:
    data = parse_data.parse_sensor_data(file_path)
    
    # Recherche gloutonne
    configuration = glouton.get_greedy_configuration(data["num_zones"], data["sensors"])
    
    # Recherche aléatoire
    configurations_pool = random_prunning.generate_configurations_pool(data["num_zones"], data["sensors"], iterations=100000)
    best_random_config = min(configurations_pool, key=len) if configurations_pool else []
    
    results = solver.solve_sensor_scheduling(data["lifetimes"], data["sensors"], configurations_pool)
    return {
        "configuration": configuration,
        "best_random_config": best_random_config,
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

def execute_all_tests():
    test_files = sorted(glob.glob("tests/*.in"))
    if not test_files:
        print("Aucun fichier de test trouvé dans le dossier 'tests/'")
        return

    for in_file in test_files:
        out_file = in_file.rsplit('.', 1)[0] + ".out"
        print(f"Exécution du test : {in_file}")
        
        start_time = time.time()
        try:
            res = run_solver(in_file)
            elapsed = time.time() - start_time
            obtained = res["objective"]
            
            # Lecture du résultat attendu et différence
            expected, diff_str = get_expected_and_diff(obtained, out_file)
            expected_val = expected if expected is not None else "N/A"
            
            print(f"Terminé en {elapsed:.2f}s | Obtenu: {obtained} (Attendu: {expected_val}) | Différence: {diff_str}\n")
        except Exception as e:
            print(f"Erreur lors de l'exécution de {in_file} : {e}\n")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        execute_all_tests()
    elif len(sys.argv) == 2:
        file_path = sys.argv[1]
        if not os.path.exists(file_path):
            print(f"Erreur : Le fichier '{file_path}' n'existe pas.")
            sys.exit(1)
            
        res = run_solver(file_path)
        print("\n" + "=" * 50)
        print(f"Résultats pour {file_path} :")
        print("=" * 50)
        print(f"Configuration Gloutonne : {res['configuration']}")
        print(f"Meilleure configuration aléatoire : {res['best_random_config']}")
        print(f"Statut : {res['status']}")
        print(f"Durée de vie maximale du réseau : {res['objective']}")
        print(f"Planning d'activation : {res['schedule']}")
        
        # Si un fichier .out existe, afficher également la comparaison
        out_file = file_path.rsplit('.', 1)[0] + ".out"
        expected, diff_str = get_expected_and_diff(res["objective"], out_file)
        if expected is not None:
            print("-" * 50)
            print(f"Valeur Attendue : {expected:.2f}")
            print(f"Différence      : {diff_str}")
        print("=" * 50)
    else:
        print("Usage:")
        print("  python main.py                 # Exécute tous les tests dans le dossier 'tests/'")
        print("  python main.py <nom_fichier>   # Exécute le solver sur un fichier spécifique")
        sys.exit(1)