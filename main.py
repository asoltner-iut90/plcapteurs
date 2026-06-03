import parse_data
import glouton
import random_prunning
import solver
import sys

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <nom_fichier>")
        sys.exit(1)
        
    data = parse_data.parse_sensor_data(sys.argv[1])

    # Recherche gloutonne
    configuration = glouton.get_greedy_configuration(data["num_zones"], data["sensors"])
    
    print(configuration)
    
    # Recherche aléatoire
    configurations_pool = random_prunning.generate_configurations_pool(data["num_zones"], data["sensors"], iterations=1000)
    best_random_config = min(configurations_pool, key=len) if configurations_pool else []
    
    results = solver.solve_sensor_scheduling(data["lifetimes"], data["sensors"], configurations_pool)
    print(f"Statut : {results['status']}")
    print(f"Durée de vie maximale du réseau : {results['objective']}")
    print(f"Planning d'activation : {results['schedule']}")
        
    print(best_random_config)