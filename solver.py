import pulp

def solve_sensor_scheduling(lifetimes: list, sensors: dict, configurations: list) -> dict:
    prob = pulp.LpProblem("Sensor_Lifetime_Maximization", pulp.LpMaximize)
    
    t_vars = [
        pulp.LpVariable(f"t_{i}", lowBound=0, cat="Continuous") 
        for i in range(len(configurations))
    ]
    
    prob += pulp.lpSum(t_vars)
    
    for sensor_id in sensors.keys():
        active_in_configs = [
            t_vars[i] 
            for i, config in enumerate(configurations) 
            if sensor_id in config
        ]
        if active_in_configs:
            prob += pulp.lpSum(active_in_configs) <= lifetimes[sensor_id - 1]
            
    prob.solve(pulp.PULP_CBC_CMD(msg=False))
    
    return {
        "status": pulp.LpStatus[prob.status],
        "objective": pulp.value(prob.objective),
        "schedule": {tuple(configurations[i]): pulp.value(t_vars[i]) for i in range(len(configurations))}
    }