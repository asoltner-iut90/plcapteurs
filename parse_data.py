def parse_sensor_data(file_path: str) -> dict:
    with open(file_path, 'r') as file:
        lines = [line.strip() for line in file if line.strip()]
    
    num_sensors = int(lines[0])
    num_zones = int(lines[1])
    lifetimes = [float(x) for x in lines[2].split()]
    
    sensors = {}
    for i in range(num_sensors):
        sensors[i + 1] = [int(z) for z in lines[3 + i].split()]
        
    return {
        "num_sensors": num_sensors,
        "num_zones": num_zones,
        "lifetimes": lifetimes,
        "sensors": sensors
    }