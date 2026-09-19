import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import time

# Configuración de página
st.set_page_config(
    page_title="NavSeg Paraná | Control Flota Cavalier",
    page_icon="⚓",
    layout="wide"
)

# Estilos de centro de operaciones naval
st.markdown("""
    <style>
    .stApp {
        background-color: #080c14;
        color: #e2e8f0;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 700;
        color: #38bdf8;
    }
    </style>
""", unsafe_allow_html=True)

# Red troncal de navegación de la Hidrovía Paraguay-Paraná (coordenadas geográficas exactas)
CANAL_HIDROVIA_PUNTOS = [
    [-57.7667, -17.7833], # 0. Puerto Quijarro / Tamengo (Bolivia)
    [-57.6530, -19.0060], # 1. Puerto Corumbá / Ladário (Brasil)
    [-57.8810, -21.6980], # 2. Porto Murtinho (Brasil)
    [-57.4320, -23.4020], # 3. Concepción (Paraguay)
    [-57.6350, -25.2810], # 4. Asunción (Paraguay)
    [-57.5720, -25.5050], # 5. Puerto Villeta (Paraguay)
    [-58.1200, -26.8500], # 6. Humaitá / Paso de Patria
    [-58.8500, -27.4580], # 7. Confluencia Ríos Paraguay y Paraná / Corrientes
    [-59.1000, -28.4700], # 8. Bella Vista (Corrientes)
    [-59.2600, -29.1400], # 9. Goya (Corrientes)
    [-59.5500, -30.0500], # 10. La Paz (Entre Ríos)
    [-60.5200, -31.7100], # 11. Paraná / Santa Fe
    [-60.7200, -32.7200], # 12. Polo San Lorenzo / Timbúes
    [-60.6300, -32.9400], # 13. Rosario Rada / Puertos
    [-60.2200, -33.3200], # 14. San Nicolás (Siderurgia)
    [-58.9500, -34.1500], # 15. Campana / Zárate (Delta)
    [-58.4200, -33.8800]  # 16. Nueva Palmira (Uruguay)
]

TRAMO_ALTO_PARANA = [
    [-56.6800, -27.5000], # Esclusa Yacyretá / Ituzaingó (Alto Paraná)
    [-57.8500, -27.4600], # Paso de la Patria
    [-58.8500, -27.4580]  # Confluencia
]

@st.cache_data
def get_cavalier_fleet():
    # Definición de derrotas operativas internacionales con sus orígenes reales
    fleet = [
        {
            "name": "R/E CAVALIER VII",
            "mmsi": 745001007,
            "origin": "Puerto Corumbá (Brasil)",
            "dest": "San Nicolás (Argentina)",
            "cargo": "Mineral de Hierro (Urucum)",
            "indices": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14],
            "custom_path": None,
            "downstream": True,
            "sog": 7.8,
            "draught": 3.2,
            "color_rgb": [52, 211, 153],   # Verde Esmeralda
            "color_hex": "#34d399",
            "status": "Operación Normal"
        },
        {
            "name": "R/E CAVALIER XII",
            "mmsi": 745001012,
            "origin": "Puerto Quijarro (Bolivia)",
            "dest": "Nueva Palmira (Uruguay)",
            "cargo": "Granos y Aceite Vegetal",
            "indices": [0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 13, 15, 16],
            "custom_path": None,
            "downstream": True,
            "sog": 0.5,
            "draught": 3.1,
            "color_rgb": [244, 63, 94],    # Rojo Alerta
            "color_hex": "#f43f5e",
            "status": "Posible Varadura / Alerta Paso Crítico"
        },
        {
            "name": "R/E CAVALIER IV",
            "mmsi": 745001004,
            "origin": "Puerto Villeta (Paraguay)",
            "dest": "San Lorenzo / Timbúes (Argentina)",
            "cargo": "Harina y Pellets de Soja",
            "indices": [5, 6, 7, 8, 9, 10, 11, 12],
            "custom_path": None,
            "downstream": True,
            "sog": 8.4,
            "draught": 3.0,
            "color_rgb": [56, 189, 248],   # Celeste Neón
            "color_hex": "#38bdf8",
            "status": "Operación Normal"
        },
        {
            "name": "R/E CAVALIER XX",
            "mmsi": 745001020,
            "origin": "Puerto Villeta (Paraguay)",
            "dest": "Puerto General San Martín (Argentina)",
            "cargo": "Trigo y Soja Transbordo",
            "indices": [5, 6, 7, 9, 11, 12],
            "custom_path": None,
            "downstream": True,
            "sog": 13.6,
            "draught": 3.0,
            "color_rgb": [251, 146, 60],   # Naranja
            "color_hex": "#fb923c",
            "status": "Exceso de Velocidad en Solera Estrecha"
        },
        {
            "name": "R/E CAVALIER XV",
            "mmsi": 745001015,
            "origin": "Rada Rosario (Argentina)",
            "dest": "Asunción / Guyratĩ (Paraguay)",
            "cargo": "En Lastre (Convoy Vacío)",
            "indices": [13, 12, 11, 10, 8, 7, 6, 5, 4], # Ascendente (aguas arriba)
            "custom_path": None,
            "downstream": False,
            "sog": 9.4,
            "draught": 2.2,
            "color_rgb": [251, 191, 36],   # Amarillo Oro
            "color_hex": "#fbbf24",
            "status": "Operación Normal"
        },
        {
            "name": "R/E CAVALIER XVIII",
            "mmsi": 745001018,
            "origin": "Esclusa Yacyretá / Alto Paraná",
            "dest": "Campana / Zárate (Argentina)",
            "cargo": "Cereales y Madera Fluvial",
            "indices": None,
            "custom_path": TRAMO_ALTO_PARANA + [CANAL_HIDROVIA_PUNTOS[i] for i in [8, 10, 12, 13, 15]],
            "downstream": True,
            "sog": 8.0,
            "draught": 2.9,
            "color_rgb": [168, 85, 247],   # Púrpura Neón
            "color_hex": "#a855f7",
            "status": "Operación Normal"
        }
    ]

    TOTAL_SIM_STEPS = 1000
    for unit in fleet:
        if unit["custom_path"]:
            base_coords = unit["custom_path"]
        else:
            base_coords = [CANAL_HIDROVIA_PUNTOS[i] for i in unit["indices"]]

        n_seg = len(base_coords)
        time_step = TOTAL_SIM_STEPS / (n_seg - 1)
        timestamps = [int(i * time_step) for i in range(n_seg)]

        unit["path"] = base_coords
        unit["timestamps"] = timestamps

    return fleet

fleet_cavalier = get_cavalier_fleet()

# Estados de sesión
if "is_running" not in st.session_state:
    st.session_state.is_running = False
if "current_time" not in st.session_state:
    st.session_state.current_time = 0

# Barra lateral
st.sidebar.title("⚓ Centro VTS Hidrovía")
st.sidebar.markdown("**Monitoreo Flota Cavalier (Atria Logística)**")

col_b1, col_b2 = st.sidebar.columns(2)
if col_b1.button("▶ Iniciar", use_container_width=True):
    st.session_state.is_running = True
if col_b2.button("⏹ Detener", use_container_width=True):
    st.session_state.is_running = False

velocidad_paso = st.sidebar.slider(
    "Velocidad de avance de simulación:",
    min_value=2,
    max_value=30,
    value=8,
    step=2
)

if st.sidebar.button("🔄 Reiniciar Circulación"):
    st.session_state.current_time = 0
    st.session_state.is_running = False

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎨 Identificación de Remolcadores:")
for v in fleet_cavalier:
    st.sidebar.markdown(
        f"<span style='color:{v['color_hex']}; font-weight:bold;'>■ {v['name']}</span><br>"
        f"<small><b>Origen:</b> {v['origin']}<br><b>Destino:</b> {v['dest']}</small>",
        unsafe_allow_html=True
    )

# Incremento continuo del reloj de simulación
if st.session_state.is_running:
    st.session_state.current_time += velocidad_paso
    if st.session_state.current_time >= 1000:
        st.session_state.current_time = 0

t_actual = st.session_state.current_time

# Cálculo cinemático de la posición de cada barco en este instante
active_points = []
for v in fleet_cavalier:
    coords = v["path"]
    times = v["timestamps"]

    if t_actual <= times[0]:
        pos = coords[0]
    elif t_actual >= times[-1]:
        pos = coords[-1]
    else:
        for j in range(len(times) - 1):
            if times[j] <= t_actual <= times[j+1]:
                frac = (t_actual - times[j]) / (times[j+1] - times[j])
                lon = coords[j][0] + (coords[j+1][0] - coords[j][0]) * frac
                lat = coords[j][1] + (coords[j+1][1] - coords[j][1]) * frac
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
        "status": v["status"],
        "direction": "Aguas Abajo (Descendente)" if v["downstream"] else "Aguas Arriba (Ascendente)",
        "color": v["color_rgb"],
        "color_hex": v["color_hex"],
        "position": pos,
        "radius": 14000 # Tamaño visible a escala continental
    })

df_active = pd.DataFrame(active_points)

# Encabezado principal
st.title("⚓ NavSeg Paraná — Monitoreo Flota Cavalier")
st.caption("Sistema de Telemetría Fluvial y Control VTS | Corredor Corumbá - Asunción - Rosario - Nueva Palmira")

m1, m2, m3, m4 = st.columns(4)
m1.metric("Convoyes en Traza", len(df_active))
m2.metric("Navegando Aguas Abajo", len(df_active[df_active["direction"].str.contains("Descendente")]))
m3.metric("Alertas de Seguridad VTS", len(df_active[df_active["status"] != "Operación Normal"]))
m4.metric("Velocidad Media Flota", f"{df_active['sog'].mean():.1f} kts")

st.markdown("---")

# Mapa cenital 2D con visualización de toda la Hidrovía internacional
st.subheader("🗺️ Carta Náutica Digital en Tiempo Real (Vista Cenital 2D)")

view_state = pdk.ViewState(
    latitude=-26.0,
    longitude=-58.5,
    zoom=4.5,    # Encuadre óptimo desde Bolivia/Corumbá hasta Buenos Aires/Uruguay
    pitch=0,
    bearing=0
)

# Línea del canal troncal completo
layer_canal = pdk.Layer(
    "PathLayer",
    data=[
        {"path": CANAL_HIDROVIA_PUNTOS},
        {"path": TRAMO_ALTO_PARANA}
    ],
    get_path="path",
    get_color=[71, 85, 105, 130],
    width_min_pixels=2
)

# Estelas de navegación continuas
layer_estelas = pdk.Layer(
    "TripsLayer",
    data=fleet_cavalier,
    get_path="path",
    get_timestamps="timestamps",
    get_color="color_rgb",
    opacity=0.9,
    width_min_pixels=6,
    rounded=True,
    trail_length=80,
    current_time=t_actual
)

# Puntos de las embarcaciones con aro blanco para contraste
layer_puntos = pdk.Layer(
    "ScatterplotLayer",
    data=df_active,
    get_position="position",
    get_color="color",
    get_radius="radius",
    pickable=True,
    stroked=True,
    filled=True,
    get_line_color=[255, 255, 255, 250],
    line_width_min_pixels=2.5
)

deck = pdk.Deck(
    layers=[layer_canal, layer_estelas, layer_puntos],
    initial_view_state=view_state,
    map_style=pdk.map_styles.CARTO_DARK,
    tooltip={
        "html": "<b>{name}</b><br/>"
                "<b>MMSI:</b> {mmsi} | <b>Bandera:</b> Paraguay<br/>"
                "<b>Puerto Origen:</b> {origin}<br/>"
                "<b>Puerto Destino:</b> {dest}<br/>"
                "<b>Carga Transportada:</b> {cargo}<br/>"
                "<b>Velocidad SOG:</b> {sog} kts | <b>Calado:</b> {draught} m<br/>"
                "<b>Régimen:</b> {direction}<br/>"
                "<b>Estado Operativo:</b> {status}",
        "style": {"backgroundColor": "#0f172a", "color": "#f8fafc", "fontSize": "12px", "padding": "8px"}
    }
)

st.pydeck_chart(deck, use_container_width=True)

st.markdown("---")

# Manifiesto de telemetría y navegación
st.subheader("📋 Manifiesto de Navegación y Telemetría Operativa")
st.dataframe(
    df_active[["name", "origin", "dest", "cargo", "direction", "sog", "draught", "status"]].rename(
        columns={
            "name": "Remolcador",
            "origin": "Puerto Origen",
            "dest": "Puerto Destino",
            "cargo": "Carga Transportada",
            "direction": "Sentido de Navegación",
            "sog": "Velocidad SOG (kts)",
            "draught": "Calado (m)",
            "status": "Estado de Seguridad"
        }
    ),
    use_container_width=True
)

# Bucle continuo fluido
if st.session_state.is_running:
    time.sleep(0.08)
    st.rerun()