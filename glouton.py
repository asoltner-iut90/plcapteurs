def get_greedy_configuration(num_zones: int, sensors: dict) -> list:
    uncovered = set(range(1, num_zones + 1))
    selected = []
    
    while uncovered:
        best_sensor = None
        max_coverage = -1
        
        for s_id, zones in sensors.items():
            if s_id in selected:
                continue
            coverage = len(set(zones) & uncovered)
            if coverage > max_coverage:
                max_coverage = coverage
                best_sensor = s_id
                
        if max_coverage <= 0:
            return []
            
        selected.append(best_sensor)
        uncovered -= set(sensors[best_sensor])
        
    all_zones = set(range(1, num_zones + 1))
    for s_id in list(selected):
        current_coverage = set()
        for other_id in selected:
            if other_id != s_id:
                current_coverage.update(sensors[other_id])
        if current_coverage == all_zones:
            selected.remove(s_id)
            
    return sorted(selected)