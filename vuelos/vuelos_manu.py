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
# FUNCIÓN: BUSCAR VUELOS
# ===============================
def buscar_vuelos(origen, destino, fecha_salida, token):
    url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "originLocationCode": origen,
        "destinationLocationCode": destino,
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
        fecha_str = fecha_salida.strftime("%Y-%m-%d")
        fecha_sky = fecha_salida.strftime("%d%m%Y")

        # 🔗 Enlaces de compra / consulta
        link_google = f"https://www.google.com/travel/flights?q={origen}+to+{destino}+on+{fecha_str}"
        link_skyscanner = f"https://www.skyscanner.com/transport/flights/{origen.lower()}/{destino.lower()}/{fecha_sky}/"
        link_kayak = f"https://www.kayak.com/flights/{origen}-{destino}/{fecha_str}"

        vuelos.append({
            "aerolinea": v.get("validatingAirlineCodes", ["Desconocida"])[0],
            "precio_usd": float(v["price"]["total"]),
            "duracion": v["itineraries"][0]["duration"].replace("PT", "").lower(),
            "escalas": len(v["itineraries"][0]["segments"]) - 1,
            "origen": origen,
            "destino": destino,
            "fecha": fecha_str,
            "google_flights": link_google,
            "skyscanner": link_skyscanner,
            "kayak": link_kayak
        })

    return vuelos

# ===============================
# FUNCIÓN: GENERAR REPORTE
# ===============================
def generar_reporte(fecha_inicio, fecha_fin):
    token = get_amadeus_token()
    if not token:
        return None, None

    rutas = [
        ("CMN", "EZE"),  # Marruecos → Buenos Aires
        ("CMN", "GRU"),  # Marruecos → São Paulo
        ("LIS", "GRU"),  # Lisboa → São Paulo
        ("LIS", "EZE"),  # Lisboa → Buenos Aires
    ]

    dias = (fecha_fin - fecha_inicio).days + 1
    vuelos_totales = []

    for i in range(dias):
        fecha = fecha_inicio + timedelta(days=i)
        for origen, destino in rutas:
            vuelos_totales.extend(buscar_vuelos(origen, destino, fecha, token))

    df = pd.DataFrame(vuelos_totales)
    if df.empty:
        st.warning("No se encontraron vuelos en el rango consultado.")
        return None, None

    df_mejores = df.loc[df.groupby(["origen", "destino", "fecha"])["precio_usd"].idxmin()].reset_index(drop=True)
    return df, df_mejores

# ===============================
# INTERFAZ STREAMLIT
# ===============================
st.set_page_config(page_title="Vuelos Marruecos - Lisboa", page_icon="✈️", layout="wide")
st.title("🌍 Comparador de vuelos – Marruecos y Lisboa ✈️ Buenos Aires / São Paulo")

st.write("""
Consulta precios reales usando la API de **Amadeus (modo test)**  
para las rutas:  
- Marruecos 🇲🇦 → Buenos Aires 🇦🇷  
- Marruecos 🇲🇦 → São Paulo 🇧🇷  
- Lisboa 🇵🇹 → São Paulo 🇧🇷  
- Lisboa 🇵🇹 → Buenos Aires 🇦🇷  

El rango máximo permitido es de **5 días posteriores** a la fecha seleccionada.
""")

# Fecha inicial
fecha_inicio = st.date_input("📅 Fecha de inicio", value=datetime.now().date())
fecha_fin = fecha_inicio + timedelta(days=5)
st.info(f"📆 El rango de búsqueda será del {fecha_inicio.strftime('%d/%m/%Y')} al {fecha_fin.strftime('%d/%m/%Y')}.")

# Botón ejecutar
if st.button("🔍 Buscar vuelos"):
    with st.spinner("Buscando ofertas reales..."):
        df_todos, df_mejores = generar_reporte(fecha_inicio, fecha_fin)

    if df_todos is not None:
        st.markdown("## ✈️ Mejores precios por ruta y día (con enlaces de compra)")
        for _, row in df_mejores.iterrows():
            st.markdown(f"""
            **{row['fecha']}** | {row['origen']} → {row['destino']}  
            🏷️ *{row['aerolinea']}* – 💵 **USD {row['precio_usd']}**  
            ⏱️ {row['duracion']} | ✈️ {row['escalas']} escala(s)  
            🔗 [Google Flights]({row['google_flights']}) | [Skyscanner]({row['skyscanner']}) | [Kayak]({row['kayak']})
            ---
            """)

        st.subheader("💰 Promedio de precios por ruta (USD)")
        df_todos["ruta"] = df_todos["origen"] + "→" + df_todos["destino"]
        promedio = df_todos.groupby("ruta")["precio_usd"].mean().reset_index()
        st.bar_chart(data=promedio, x="ruta", y="precio_usd")

        st.subheader("📈 Evolución diaria de precios mínimos")
        minimos_diarios = df_todos.groupby(["fecha", "origen", "destino"])["precio_usd"].min().reset_index()
        minimos_diarios["ruta"] = minimos_diarios["origen"] + "→" + minimos_diarios["destino"]
        pivot = minimos_diarios.pivot(index="fecha", columns="ruta", values="precio_usd")
        st.line_chart(pivot)

        st.subheader("⬇️ Descargar reporte completo (CSV)")
        csv = df_todos.to_csv(index=False).encode("utf-8")
        st.download_button("Descargar CSV", csv, "reporte_vuelos_marruecos_lisboa.csv", "text/csv")

        st.success("✅ Reporte generado correctamente.")
