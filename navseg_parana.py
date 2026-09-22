import streamlit as st
import pydeck as pdk
import time
from src.config import CANAL_HIDROVIA, TRAMO_ALTO_PARANA, TOTAL_SIM_STEPS
from src.fleet_data import get_base_fleet, compute_instant_position
from src.safety_engine import evaluate_vts_safety

# Configuración de página
st.set_page_config(
    page_title="NavSeg Paraná | Control VTS Fluvial",
    page_icon="⚓",
    layout="wide"
)

# Inicialización de estado
if "is_running" not in st.session_state:
    st.session_state.is_running = False
if "current_time" not in st.session_state:
    st.session_state.current_time = 0

fleet_cavalier = get_base_fleet()

# Barra lateral
st.sidebar.title("⚓ Centro VTS Hidrovía")
st.sidebar.markdown("**Control Operativo Flota Cavalier**")

col1, col2 = st.sidebar.columns(2)
if col1.button("▶ Iniciar", use_container_width=True):
    st.session_state.is_running = True
if col2.button("⏹ Detener", use_container_width=True):
    st.session_state.is_running = False

velocidad_paso = st.sidebar.number_input("Velocidad de simulación:", min_value=2, max_value=30, value=8, step=2)
umbral_ukc = st.sidebar.number_input("Umbral UKC Crítico (m):", min_value=0.20, max_value=1.50, value=0.60, step=0.05)

if st.sidebar.button("🔄 Reiniciar Traza"):
    st.session_state.current_time = 0
    st.session_state.is_running = False

# Avance temporal
if st.session_state.is_running:
    st.session_state.current_time += velocidad_paso
    if st.session_state.current_time >= TOTAL_SIM_STEPS:
        st.session_state.current_time = 0

t_actual = st.session_state.current_time

# Procesamiento de cinemática y telemetría
raw_points = compute_instant_position(fleet_cavalier, t_actual)
df_active = evaluate_vts_safety(raw_points, umbral_ukc_critico=umbral_ukc)

# Encabezado
st.title("⚓ NavSeg Paraná — Centro de Control VTS Fluvial")
st.caption("Monitoreo Operativo en Tiempo Real | Hidrovía Paraguay-Paraná | Análisis Cinemático y Margen Bajo Quilla (UKC)")

# Indicadores de nivel de servicio
m1, m2, m3, m4 = st.columns(4)
m1.metric("Convoyes en Traza", len(df_active))
m2.metric("Alertas de Seguridad VTS", len(df_active[df_active["status"] != "Operación Normal"]))
m3.metric("Convoyes con UKC Crítico", len(df_active[df_active["ukc_alert"]]), delta_color="inverse")
m4.metric("Velocidad Media SOG", f"{df_active['sog'].mean():.1f} nudos")

st.markdown("---")

# Mapa Táctico 2D
st.subheader("🗺️ Carta Náutica Digital y Situación Táctica")

view_state = pdk.ViewState(
    latitude=-26.5,
    longitude=-58.5,
    zoom=4.8,
    pitch=0,
    bearing=0
)

layer_canal = pdk.Layer(
    "PathLayer",
    data=[{"path": CANAL_HIDROVIA}, {"path": TRAMO_ALTO_PARANA}],
    get_path="path",
    get_color=[100, 116, 139, 180],
    width_min_pixels=3
)

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

layer_puntos = pdk.Layer(
    "ScatterplotLayer",
    data=df_active,
    get_position="position",
    get_color="color",
    get_radius="radius",
    pickable=True,
    stroked=True,
    filled=True,
    get_line_color=[255, 255, 255, 255],
    line_width_min_pixels=2.5
)

deck = pdk.Deck(
    layers=[layer_canal, layer_estelas, layer_puntos],
    initial_view_state=view_state,
    map_style=pdk.map_styles.CARTO_DARK,
    tooltip={
        "html": "<b>{name}</b> ({direction})<br/>"
                "<b>MMSI:</b> {mmsi} | <b>Carga:</b> {cargo}<br/>"
                "<b>SOG:</b> {sog} kts | <b>Calado:</b> {draught} m<br/>"
                "<b>Prof. Paso:</b> {channel_depth} m | <b>UKC:</b> {ukc} m<br/>"
                "<b>Estado VTS:</b> {status}",
        "style": {"backgroundColor": "#0f172a", "color": "#f8fafc", "padding": "8px", "fontSize": "12px"}
    }
)

st.pydeck_chart(deck, use_container_width=True)

st.markdown("---")

# Matriz Operativa
st.subheader("📋 Matriz Operativa de Tráfico y Márgenes de Seguridad (UKC)")

df_display = df_active[[
    "name", "origin", "dest", "cargo", "direction", "sog", "draught", "channel_depth", "ukc", "status"
]].rename(
    columns={
        "name": "Remolcador",
        "origin": "Puerto Origen",
        "dest": "Puerto Destino",
        "cargo": "Carga Transportada",
        "direction": "Sentido",
        "sog": "SOG (kts)",
        "draught": "Calado (m)",
        "channel_depth": "Prof. Paso (m)",
        "ukc": "Margen UKC (m)",
        "status": "Evaluación Operativa VTS"
    }
)

st.dataframe(df_display, use_container_width=True)

if st.session_state.is_running:
    time.sleep(0.08)
    st.rerun()