import streamlit as st
import requests
from supabase import create_client
from datetime import datetime

# --- CONFIGURACIÓN ---
URL_SUPABASE = "https://xavzjoyjausutoscosaw.supabase.co"
KEY_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhhdnpqb3lqYXVzdXRvc2Nvc2F3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjAwNzksImV4cCI6MjA4NTUzNjA3OX0.YjHw-NVeuVpK5l4XkM3hft1vSrERRBXEWZl2wPNjZ0k"
API_KEY = "GQM8r3pQM1JZSH4Z"
SECRET = "9pNSRVoddsshE1elR1tj4TaRVTRNBVNL"

supabase = create_client(URL_SUPABASE, KEY_SUPABASE)

st.set_page_config(page_title="Resultados Progol en Vivo", layout="centered")

# --- ESTILO ---
st.markdown("""
    <style>
    .live-card { padding: 15px; border-radius: 10px; border: 1px solid #ff4b4b; margin-bottom: 10px; background-color: #1e1e1e; }
    .minute { color: #ff4b4b; font-weight: bold; font-size: 20px; }
    .score { font-size: 24px; font-weight: bold; letter-spacing: 5px; }
    </style>
""", unsafe_allow_html=True)

st.title("🏆 Resultados en Vivo")

# 1. Obtener el Sorteo más actual automáticamente
try:
    res_sorteo = supabase.table("quinielas_activas").select("sorteo_numero").order("sorteo_numero", desc=True).limit(1).execute()
    sorteo_actual = res_sorteo.data[0]['sorteo_numero'] if res_sorteo.data else 0
except:
    sorteo_actual = 0

if sorteo_actual > 0:
    st.subheader(f"📍 Sorteo Actual: #{sorteo_actual}")
    
    # 2. Traer los partidos de ese sorteo
    partidos_db = supabase.table("quinielas_activas").select("*").eq("sorteo_numero", sorteo_actual).order("casilla").execute()

    if partidos_db.data:
        # 3. Consultar la API para ver cuáles están en vivo ahora
        # Usamos el endpoint 'scores' que da los marcadores actuales
        url_live = f"https://livescore-api.com/api-client/scores/live.json?key={API_KEY}&secret={SECRET}"
        live_data = requests.get(url_live).json()
        live_list = live_data.get('data', {}).get('match', []) if live_data.get('success') else []

        # Crear un mapa de partidos en vivo por ID para acceso rápido
        live_map = {str(m['id']): m for m in live_list}

        for p in partidos_db.data:
            f_id = str(p['fixture_id'])
            
            with st.container():
                # Si el partido está en el mapa de "En Vivo"
                if f_id in live_map:
                    m = live_map[f_id]
                    st.markdown(f"""
                    <div class="live-card">
                        <div style="display: flex; justify-content: space-between;">
                            <span>Casilla {p['casilla']}</span>
                            <span class="minute">● {m['time']}'</span>
                        </div>
                        <div style="text-align: center;">
                            <p style="margin:0;">{p['local_nombre']} vs {p['visita_nombre']}</p>
                            <p class="score">{m['score']}</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # Partido no iniciado o ya finalizado (buscamos en fixtures pasados si es necesario)
                    st.info(f"Casilla {p['casilla']}: {p['local_nombre']} vs {p['visita_nombre']} - 🕒 {p['hora_mx']}")

    else:
        st.write("No hay partidos registrados para el sorteo actual.")
else:
    st.error("No se encontró ninguna quiniela activa.")

if st.button("🔄 Actualizar Marcadores"):
    st.rerun()
