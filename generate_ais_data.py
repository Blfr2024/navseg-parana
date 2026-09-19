import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def create_parana_river_corridor():
    waypoints = [
        (-27.4580, -58.8500, "Confluencia / Corrientes", 1240, 150),
        (-27.4680, -58.8650, "Paso Puente General Belgrano", 1208, 120),
        (-27.9500, -59.0800, "Empedrado", 1140, 140),
        (-28.4700, -59.1000, "Bella Vista", 1057, 130),
        (-29.1400, -59.2600, "Goya", 970, 130),
        (-30.0500, -59.5500, "La Paz", 750, 140),
        (-31.7100, -60.5200, "Paraná / Santa Fe", 590, 120),
        (-32.0500, -60.6300, "Diamante", 533, 150),
        (-32.7200, -60.7200, "Polo San Lorenzo / San Martín", 445, 160),
        (-32.9400, -60.6300, "Rosario Rada / Puertos", 410, 180),
        (-33.3200, -60.2200, "San Nicolás", 345, 160),
        (-33.6800, -59.6600, "San Pedro", 275, 150),
        (-34.1500, -58.9500, "Campana (Paraná de las Palmas)", 95, 100),
        (-34.3500, -58.5500, "Zona Común La Plata / Río de la Plata", 0, 250)
    ]
    return waypoints

def generate_synthetic_ais_stream(n_vessels=35):
    np.random.seed(42)
    waypoints = create_parana_river_corridor()
    vessels = []
    
    profiles = [
        {"type": "Remolcador de Empuje (Convoy)", "prob": 0.55, "flags": ["Paraguay", "Paraguay", "Paraguay", "Bolivia", "Argentina"], "speed_range": (5.0, 9.5), "draught_range": (2.4, 3.4), "length_range": (140, 290)},
        {"type": "Granelero Panamax / Handymax", "prob": 0.30, "flags": ["Liberia", "Panamá", "Islas Marshall", "Malta"], "speed_range": (8.0, 12.0), "draught_range": (8.5, 10.5), "length_range": (180, 230)},
        {"type": "Tanquero Fluvial", "prob": 0.15, "flags": ["Argentina", "Paraguay"], "speed_range": (7.0, 10.5), "draught_range": (3.5, 6.0), "length_range": (90, 140)}
    ]
    
    types_list = [p["type"] for p in profiles]
    probs = [p["prob"] for p in profiles]
    start_time = datetime.now()
    
    for i in range(1, n_vessels + 1):
        v_profile = np.random.choice(profiles, p=probs)
        v_type = v_profile["type"]
        v_flag = np.random.choice(v_profile["flags"])
        mmsi = int(f"7{np.random.randint(10, 99)}{np.random.randint(10000, 99999)}")
        
        if "Remolcador" in v_type:
            v_name = f"R/E {np.random.choice(['GUARAN I', 'ASUNCION B', 'CAACUPE', 'RIO PARANA', 'DON CARLOS', 'ITAIPU III', 'ALIANZA G', 'PAMPERO V', 'YASYRETA'])} - C{np.random.randint(10, 99)}"
        elif "Granelero" in v_type:
            v_name = f"M/V {np.random.choice(['ATLANTIC GLORY', 'NORDIC BULKER', 'PACIFIC TRADER', 'NAVIGATOR I', 'GLOBAL EXPLORER'])}"
        else:
            v_name = f"T/K {np.random.choice(['SOL DEL PLATA', 'PETRO SUR', 'DELTA STAR'])}"
            
        wp_idx = np.random.randint(0, len(waypoints) - 1)
        wp_start = waypoints[wp_idx]
        wp_end = waypoints[wp_idx + 1]
        
        fraction = np.random.uniform(0.1, 0.9)
        cross_track_offset = np.random.normal(0, 0.003)
        lat = wp_start[0] + (wp_end[0] - wp_start[0]) * fraction + cross_track_offset
        lon = wp_start[1] + (wp_end[1] - wp_start[1]) * fraction + cross_track_offset
        
        direction = np.random.choice(["Aguas Abajo (Descendente)", "Aguas Arriba (Ascendente)"])
        cog = np.random.uniform(150, 190) if direction == "Aguas Abajo (Descendente)" else np.random.uniform(330, 370) % 360
        sog = np.random.uniform(v_profile["speed_range"][0], v_profile["speed_range"][1])
        draught = round(np.random.uniform(v_profile["draught_range"][0], v_profile["draught_range"][1]), 1)
        length = np.random.randint(v_profile["length_range"][0], v_profile["length_range"][1])
        
        anomaly_type = "Operación Normal"
        nav_status = "Underway using engine"
        
        if i in [7, 18]:
            sog = 0.2
            anomaly_type = "Posible Varadura / Parada No Autorizada en Canal"
            nav_status = "Restricted Maneuverability"
        elif i in [12, 24]:
            sog = 14.2
            anomaly_type = "Exceso de Velocidad en Solera Estrecha"
        elif i in [4, 31]:
            lat += 0.015
            anomaly_type = "Derrota Fuera del Canal Balizado"
            
        vessels.append({
            "mmsi": mmsi,
            "vessel_name": v_name,
            "vessel_type": v_type,
            "flag": v_flag,
            "latitude": round(lat, 5),
            "longitude": round(lon, 5),
            "sog_knots": round(sog, 1),
            "cog_degrees": round(cog, 1),
            "draught_m": draught,
            "length_m": length,
            "direction": direction,
            "current_zone": wp_start[2],
            "nav_status": nav_status,
            "safety_assessment": anomaly_type,
            "timestamp": (start_time - timedelta(minutes=np.random.randint(1, 20))).strftime("%Y-%m-%d %H:%M:%S")
        })
        
    df = pd.DataFrame(vessels)
    df.to_csv("telemetria_ais_parana.csv", index=False)
    print(f"Dataset AIS generado exitosamente con {len(df)} embarcaciones activas en 'telemetria_ais_parana.csv'")

if __name__ == "__main__":
    generate_synthetic_ais_stream()