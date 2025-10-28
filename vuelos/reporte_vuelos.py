import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random

# ===============================
# FUNCIÓN PARA SIMULAR VUELOS
# ===============================
def buscar_vuelos(pais_origen, fecha_salida):
    aeropuertos = {
        "Argentina": "EZE (Buenos Aires)",
        "Paraguay": "ASU (Asunción)",
        "Uruguay": "MVD (Montevideo)"
    }
    origen = aeropuertos.get(pais_origen, "Desconocido")

    vuelos_simulados = [
        {"aerolinea": "Aerolíneas Argentinas", "precio_usd": random.randint(800, 1200), "duracion": "20h", "escalas": 1},
        {"aerolinea": "LATAM", "precio_usd": random.randint(750, 1100), "duracion": "18h", "escalas": 1},
        {"aerolinea": "Gol", "precio_usd": random.randint(700, 1000), "duracion": "22h", "escalas": 2},
    ]
    
    for vuelo in vuelos_simulados:
        vuelo["origen"] = origen
        vuelo["destino"] = "BKK (Bangkok, Tailandia)"
        vuelo["fecha"] = fecha_salida.strftime("%Y-%m-%d")
        vuelo["precio_thb"] = vuelo["precio_usd"] * 36
        vuelo["pais"] = pais_origen
        # 🔗 Link simulado (abre Google Flights con la ruta y fecha)
        vuelo["link"] = f"[✈️ Ver vuelo](https://www.google.com/flights?hl=es#flt={origen.split()[0]}.BKK.{fecha_salida.strftime('%Y-%m-%d')})"
    return vuelos_simulados

# ===============================
# FUNCIÓN PARA GENERAR REPORTE DIARIO
# ===============================
def generar_reporte_comparativo():
    fecha_inicio = datetime(2026, 9, 1)
    fecha_fin = datetime(2026, 9, 30)
    dias = (fecha_fin - fecha_inicio).days + 1

    paises = ["Argentina", "Paraguay", "Uruguay"]
    vuelos_totales = []

    for i in range(dias):
        fecha = fecha_inicio + timedelta(days=i)
        for pais in paises:
            vuelos_totales.extend(buscar_vuelos(pais, fecha))
    
    df = pd.DataFrame(vuelos_totales)

    # Mejor precio por país y fecha
    df_mejores = df.loc[df.groupby(["pais", "fecha"])["precio_usd"].idxmin()].reset_index(drop=True)
    
    return df, df_mejores

# ===============================
# INTERFAZ STREAMLIT
# ===============================
st.set_page_config(page_title="Reporte de Vuelos", page_icon="✈️", layout="wide")
st.title("🌏 Reporte comparativo de vuelos a Bangkok – Septiembre 2026")

st.write("""
Este panel simula precios diarios de vuelos desde **Argentina**, **Paraguay** y **Uruguay** hacia **Bangkok (BKK)** durante septiembre de 2026.  
Los precios se generan aleatoriamente a modo de ejemplo y pueden descargarse en CSV.
""")

if st.button("🧾 Generar reporte"):
    with st.spinner("Simulando vuelos y generando reporte..."):
        df_todos, df_mejores = generar_reporte_comparativo()

    st.subheader("📊 Mejores precios diarios por país")
    df_links = df_mejores[["fecha", "pais", "aerolinea", "precio_usd", "duracion", "escalas", "link"]]
    st.markdown(df_links.to_markdown(index=False), unsafe_allow_html=True)

    st.subheader("💰 Promedio de precios por país (USD)")
    promedio = df_todos.groupby("pais")["precio_usd"].mean().reset_index()
    st.bar_chart(data=promedio, x="pais", y="precio_usd")

    st.subheader("📈 Evolución diaria de precios mínimos (USD)")
    minimos_diarios = df_todos.groupby(["fecha", "pais"])["precio_usd"].min().reset_index()
    pivot = minimos_diarios.pivot(index="fecha", columns="pais", values="precio_usd")
    st.line_chart(pivot)

    st.subheader("⬇️ Descargar reporte completo (CSV)")
    csv = df_todos.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Descargar CSV",
        data=csv,
        file_name="reporte_vuelos_septiembre2026.csv",
        mime="text/csv"
    )

    st.success("✅ Reporte generado exitosamente.")
