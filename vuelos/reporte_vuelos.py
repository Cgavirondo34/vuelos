import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import requests
import os

# ===============================
# CONFIGURACIÓN DE CREDENCIALES
# ===============================
CLIENT_ID = "sbKAsw4mqHHqT5AocOyjcScHldW0xCx1"
CLIENT_SECRET = "5htTldQeWUr48sr4"

# ===============================
# FUNCIÓN: OBTENER TOKEN
# ===============================
def get_amadeus_token():
    url = "https://test.api.amadeus.com/v1/security/oauth2/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    resp = requests.post(url, data=data)
    if resp.status_code == 200:
        return resp.json()["access_token"]
    else:
        st.error("❌ Error al obtener token de Amadeus.")
        return None

# ===============================
# FUNCIÓN: BUSCAR VUELOS REALES
# ===============================
def buscar_vuelos(pais_origen, fecha_salida, token):
    aeropuertos = {
        "Argentina": "EZE",  # Buenos Aires
        "Paraguay": "ASU",   # Asunción
        "Uruguay": "MVD"     # Montevideo
    }
    origen = aeropuertos.get(pais_origen, "EZE")
    destino_code = "BKK"  # 🔹 Bangkok fijo

    url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "originLocationCode": origen,
        "destinationLocationCode": destino_code,
        "departureDate": fecha_salida.strftime("%Y-%m-%d"),
        "adults": 1,
        "max": 5
    }

    resp = requests.get(url, headers=headers, params=params)
    if resp.status_code != 200:
        return []

    data = resp.json().get("data", [])
    vuelos = []
    for v in data:
        vuelos.append({
            "aerolinea": v.get("validatingAirlineCodes", ["Desconocida"])[0],
            "precio_usd": float(v["price"]["total"]),
            "duracion": v["itineraries"][0]["duration"].replace("PT", "").lower(),
            "escalas": len(v["itineraries"][0]["segments"]) - 1,
            "origen": origen,
            "destino": destino_code,
            "fecha": fecha_salida.strftime("%Y-%m-%d"),
            "pais": pais_origen,
            "link": f"https://www.google.com/travel/flights?q={origen}+to+{destino_code}+on+{fecha_salida.strftime('%Y-%m-%d')}"
        })
    return vuelos

# ===============================
# FUNCIÓN: GENERAR REPORTE COMPLETO
# ===============================
def generar_reporte_comparativo(fecha_inicio, fecha_fin):
    token = get_amadeus_token()
    if not token:
        return None, None

    dias = (fecha_fin - fecha_inicio).days + 1
    paises = ["Argentina", "Paraguay", "Uruguay"]
    vuelos_totales = []

    for i in range(dias):
        fecha = fecha_inicio + timedelta(days=i)
        for pais in paises:
            vuelos_totales.extend(buscar_vuelos(pais, fecha, token))

    df = pd.DataFrame(vuelos_totales)
    if df.empty:
        st.warning("No se encontraron vuelos reales en el rango consultado.")
        return None, None

    df_mejores = df.loc[df.groupby(["pais", "fecha"])["precio_usd"].idxmin()].reset_index(drop=True)
    return df, df_mejores

# ===============================
# INTERFAZ STREAMLIT
# ===============================
st.set_page_config(page_title="Reporte de Vuelos Reales", page_icon="✈️", layout="wide")
st.title("🌏 Reporte de vuelos reales a Bangkok – Amadeus API")

st.write("""
Consulta precios **reales** desde **Argentina**, **Paraguay** y **Uruguay** hacia  
**Bangkok (BKK)** usando la API de **Amadeus (modo test)**.  
El rango máximo permitido es de **5 días posteriores** a la fecha seleccionada.
""")

# 🔹 Fecha de inicio (el usuario elige)
fecha_inicio = st.date_input("📅 Fecha de inicio", value=datetime(2026, 9, 1))
# 🔹 Fecha final automática = fecha_inicio + 5 días
fecha_fin = fecha_inicio + timedelta(days=5)

st.info(f"📆 El rango de búsqueda será del {fecha_inicio.strftime('%d/%m/%Y')} al {fecha_fin.strftime('%d/%m/%Y')} (máx. 5 días).")

if st.button("🧾 Generar reporte real"):
    with st.spinner("Consultando Amadeus y generando reporte..."):
        df_todos, df_mejores = generar_reporte_comparativo(fecha_inicio, fecha_fin)

    if df_todos is not None:
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
            file_name="reporte_vuelos_bangkok.csv",
            mime="text/csv"
        )

        st.success("✅ Reporte generado exitosamente con datos reales.")
