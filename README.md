# ⚓ NavSeg Paraná — Servicio de Tráfico Marítimo (VTS) y Telemetría AIS

Sistema interactivo de monitoreo geoespacial, visualización cinemática y análisis de seguridad náutica fluvial enfocado en el eje troncal de la **Hidrovía Paraguay-Paraná** (Corumbá / Quijarro ➔ Asunción ➔ Gran Rosario ➔ Nueva Palmira).

El proyecto simula y supervisa en tiempo real la cinemática de navegación de la flota de remolcadores de empuje de gran porte (**Flota Cavalier - Atria Logística / UABL**), evaluando velocidades, calados operativos y condiciones de maniobra en pasos críticos y soleras estrechas.

---

## 🚀 Características Principales

* **Visualización Cartográfica Cenital 2D:** Renderizado continuo a 60 FPS acelerado por hardware (WebGL) mediante **PyDeck** (`TripsLayer` y `ScatterplotLayer`), permitiendo evaluar la separación entre convoyes y el canal balizado sin distorsión de perspectiva.
* **Telemetría Operativa Fluvial Real:**
  * Despachos y derrotas desde orígenes reales: **Puerto Corumbá (Brasil)**, **Puerto Quijarro (Bolivia)**, **Puerto Villeta (Paraguay)** y **Alto Paraná / Esclusa de Yacyretá** hacia terminales del Gran Rosario, Campana y Nueva Palmira.
  * Trazado dinámico de estelas de navegación proporcionales a la derrota y velocidad de avance.
* **Detección de Anomalías Náuticas (Reglas VTS):**
  * Alerta por pérdida de gobierno / posible varadura en pasos críticos de bajo calado.
  * Control de velocidad máxima permitida (SOG) en pasos estrechos.
  * Identificación por pabellón, MMSI y tipo de carga transportada (mineral de hierro, granos, subproductos).
* **Controles de Reproducción Dinámica:** Inicio/pausa del flujo cinemático, regulador de velocidad de simulación y reinicio de derrota.

---

## 🛠️ Stack Tecnológico

* **Lenguaje:** Python 3.10+
* **Frontend / Framework Web:** Streamlit
* **Motor Geoespacial:** PyDeck (Deck.gl / WebGL)
* **Procesamiento de Datos:** Pandas, NumPy
* **Cartografía Base:** Mapas vectoriales oscuros libres de CartoDB

---

## 📦 Instalación y Ejecución Local

1. **Clonar el repositorio:**
   ```bash
   git clone [https://github.com/Blfr2024/navseg-parana.git](https://github.com/Blfr2024/navseg-parana.git)
   cd navseg-parana
