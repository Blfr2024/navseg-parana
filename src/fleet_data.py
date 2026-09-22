from src.config import CANAL_HIDROVIA, TRAMO_ALTO_PARANA, TOTAL_SIM_STEPS

def get_base_fleet():
    fleet = [
        {
            "name": "R/E CAVALIER VII",
            "mmsi": 745001007,
            "origin": "Puerto Corumbá (Brasil)",
            "dest": "San Nicolás (Argentina)",
            "cargo": "Mineral de Hierro",
            "indices": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14],
            "custom_path": None,
            "downstream": True,
            "sog": 7.8,
            "draught": 3.2,
            "channel_depth": 4.10,
            "color_rgb": [52, 211, 153],
            "color_hex": "#34d399",
            "status": "Operación Normal"
        },
        {
            "name": "R/E CAVALIER XII",
            "mmsi": 745001012,
            "origin": "Puerto Quijarro (Bolivia)",
            "dest": "Nueva Palmira (Uruguay)",
            "cargo": "Granos y Harina",
            "indices": [0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 13, 15, 16],
            "custom_path": None,
            "downstream": True,
            "sog": 0.5,
            "draught": 3.1,
            "channel_depth": 3.45,
            "color_rgb": [244, 63, 94],
            "color_hex": "#f43f5e",
            "status": "Alerta Varadura / Pérdida de Franquía"
        },
        {
            "name": "R/E CAVALIER IV",
            "mmsi": 745001004,
            "origin": "Puerto Villeta (Paraguay)",
            "dest": "San Lorenzo (Argentina)",
            "cargo": "Pellets de Soja",
            "indices": [5, 6, 7, 8, 9, 10, 11, 12],
            "custom_path": None,
            "downstream": True,
            "sog": 8.4,
            "draught": 3.0,
            "channel_depth": 4.20,
            "color_rgb": [56, 189, 248],
            "color_hex": "#38bdf8",
            "status": "Operación Normal"
        },
        {
            "name": "R/E CAVALIER XX",
            "mmsi": 745001020,
            "origin": "Puerto Villeta (Paraguay)",
            "dest": "Pto. Gral. San Martín",
            "cargo": "Trigo Transbordo",
            "indices": [5, 6, 7, 9, 11, 12],
            "custom_path": None,
            "downstream": True,
            "sog": 13.6,
            "draught": 3.0,
            "channel_depth": 4.50,
            "color_rgb": [251, 146, 60],
            "color_hex": "#fb923c",
            "status": "Exceso de Velocidad en Solera"
        },
        {
            "name": "R/E CAVALIER XV",
            "mmsi": 745001015,
            "origin": "Rada Rosario (Argentina)",
            "dest": "Asunción (Paraguay)",
            "cargo": "En Lastre (Vacío)",
            "indices": [13, 12, 11, 10, 8, 7, 6, 5, 4],
            "custom_path": None,
            "downstream": False,
            "sog": 9.4,
            "draught": 2.2,
            "channel_depth": 3.80,
            "color_rgb": [251, 191, 36],
            "color_hex": "#fbbf24",
            "status": "Operación Normal"
        },
        {
            "name": "R/E CAVALIER XVIII",
            "mmsi": 745001018,
            "origin": "Esclusa Yacyretá",
            "dest": "Campana / Zárate",
            "cargo": "Cereales y Madera",
            "indices": None,
            "custom_path": TRAMO_ALTO_PARANA + [CANAL_HIDROVIA[i] for i in [8, 10, 12, 13, 15]],
            "downstream": True,
            "sog": 8.0,
            "draught": 2.9,
            "channel_depth": 3.90,
            "color_rgb": [168, 85, 247],
            "color_hex": "#a855f7",
            "status": "Operación Normal"
        }
    ]

    for unit in fleet:
        coords = unit["custom_path"] if unit["custom_path"] else [CANAL_HIDROVIA[i] for i in unit["indices"]]
        n_seg = len(coords)
        step = TOTAL_SIM_STEPS / (n_seg - 1)
        unit["path"] = coords
        unit["timestamps"] = [int(i * step) for i in range(n_seg)]

    return fleet

def compute_instant_position(fleet, t_actual):
    active_points = []
    for v in fleet:
        coords = v["path"]
        times = v["timestamps"]

        if t_actual <= times[0]:
            pos = coords[0]
        elif t_actual >= times[-1]:
            pos = coords[-1]
        else:
            for j in range(len(times) - 1):
                if times[j] <= t_actual <= times[j + 1]:
                    frac = (t_actual - times[j]) / (times[j + 1] - times[j])
                    lon = coords[j][0] + (coords[j + 1][0] - coords[j][0]) * frac
                    lat = coords[j][1] + (coords[j + 1][1] - coords[j][1]) * frac
                    pos = [lon, lat]
                    break

        active_points.append({
            "name": v["name"],
            "mmsi": v["mmsi"],
            "origin": v["origin"],
            "dest": v["dest"],
            "cargo": v["cargo"],
            "sog": v["sog"],
            "draught": v["draught"],
            "channel_depth": v["channel_depth"],
            "status": v["status"],
            "direction": "Descendente" if v["downstream"] else "Ascendente",
            "color": v["color_rgb"],
            "color_hex": v["color_hex"],
            "position": pos,
            "radius": 15000
        })
    return active_points