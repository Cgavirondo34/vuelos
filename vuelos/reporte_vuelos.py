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

    # Lista ampliada de aerolíneas (latinoamericanas, europeas, asiáticas y globales)
    aerolineas = [
        ("Aerolíneas Argentinas", 850, 1200),
        ("LATAM Airlines", 800, 1150),
        ("Gol Linhas Aéreas", 750, 1050),
        ("Copa Airlines", 900, 1250),
        ("Avianca", 850, 1200),
        ("Sky Airline", 780, 1100),
        ("Azul Brazilian Airlines", 780, 1150),
        ("American Airlines", 950, 1350),
        ("Delta Airlines", 980, 1400),
        ("United Airlines", 980, 1450),
        ("Air France", 1100, 1500),
        ("KLM Royal Dutch", 1050, 1450),
        ("Lufthansa", 1050, 1500),
        ("British Airways", 1100, 1550),
        ("Iberia", 1000, 1400),
        ("Swiss International", 1050, 1500),
        ("Turkish Airlines", 900, 1300),
        ("Qatar Airways", 950, 1350),
        ("Emirates", 1000, 1450),
        ("Etihad Airways", 1000, 1450),
        ("Singapore Airlines", 950, 1300),
        ("Cathay Pacific", 950, 1350),
        ("Thai Airways", 900, 1300),
        ("Japan Airlines", 970, 1400),
        ("Korean Air", 970, 1400),
        ("China Airlines", 900, 1300),
        ("Air China", 880, 1250),
        ("ANA All Nippon Airways", 950, 1400),
        ("Qantas Airways", 950, 1350),
        ("Air Canada", 950, 1400),
        ("Air Europa", 950, 1350),
        ("Scandinavian Airlines", 1000, 1450),
        ("Finnair", 1000, 1450),
    ]

    # Generar vuelos simulados
    vuelos_simulados = []
    for aerolinea, min_precio, max_precio in aerolineas:
        vuelos_simulados.append({
            "aerolinea": aerolinea,
            "precio_usd": random.randint(min_precio, max_precio),
            "duracion": f"{random.randint(18, 30)}h",
            "escalas": random.choice([0, 1, 2]),
        })

    # Agregar detalles comunes
    for vuelo in vuelos_simulados:
        vuelo["origen"] = origen
        vuelo["destino"] = "BKK (Bangkok, Tailandia)"
        vuelo["fecha"] = fecha_salida.strftime("%Y-%m-%d")
        vuelo["precio_thb"] = vuelo["precio_usd"] * 36
        vuelo["pais"] = pais_origen
        # 🔗 Enlace simulado a Google Flights
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
Los precios se generan aleatoriamente con más de **30 aerolíneas internacionales** y pueden descargarse en CSV.
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
