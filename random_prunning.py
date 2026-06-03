import random

def get_random_configuration(num_zones: int, sensors: dict) -> list:
    sensor_ids = list(sensors.keys())
    random.shuffle(sensor_ids)
    
    selected = []
    uncovered = set(range(1, num_zones + 1))
    
    for s_id in sensor_ids:
        if not uncovered:
            break
        selected.append(s_id)
        uncovered -= set(sensors[s_id])
        
    if uncovered:
        return []
        
    all_zones = set(range(1, num_zones + 1))
    for s_id in list(selected):
        current_coverage = set()
        for other_id in selected:
            if other_id != s_id:
                current_coverage.update(sensors[other_id])
        if current_coverage == all_zones:
            selected.remove(s_id)
            
    return sorted(selected)

def generate_configurations_pool(num_zones: int, sensors: dict, iterations: int = 100) -> list:
    unique_configs = set()
    for _ in range(iterations):
        config = get_random_configuration(num_zones, sensors)
        if config:
            unique_configs.add(tuple(config))
    return [list(c) for c in unique_configs]