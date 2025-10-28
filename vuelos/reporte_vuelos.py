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
        vuelo["]()
