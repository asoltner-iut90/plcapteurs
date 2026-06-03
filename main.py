import parse_data
import glouton
import random_prunning
import solver

def main():
    data = parse_data.parse_sensor_data('test_5.txt')

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


if __name__ == "__main__":
    main()