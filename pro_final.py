import streamlit as st
import requests
from supabase import create_client
from datetime import datetime

# ==========================================
# 1. CREDENCIALES Y CONEXIÓN
# ==========================================
URL_SUPABASE = "https://xavzjoyjausutoscosaw.supabase.co"
KEY_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhhdnpqb3lqYXVzdXRvc2Nvc2F3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjAwNzksImV4cCI6MjA4NTUzNjA3OX0.YjHw-NVeuVpK5l4XkM3hft1vSrERRBXEWZl2wPNjZ0k"
API_KEY = "GQM8r3pQM1JZSH4Z"
SECRET = "9pNSRVoddsshE1elR1tj4TaRVTRNBVNL"

supabase = create_client(URL_SUPABASE, KEY_SUPABASE)

# ==========================================
# 2. CONFIGURACIÓN Y ESTILO PREMIUM (TU DISEÑO)
# ==========================================
st.set_page_config(page_title="Progol Live Premium", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stApp { background: linear-gradient(135deg, #0e1117 0%, #1c2531 100%); }
    .match-card {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 20px;
        border-left: 5px solid #00ff88;
        margin-bottom: 15px;
        transition: transform 0.3s;
    }
    .match-card:hover { transform: scale(1.02); background: rgba(255, 255, 255, 0.08); }
    .live-indicator { color: #ff4b4b; font-weight: bold; animation: blinker 1.5s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }
    .score-text { font-size: 28px; font-weight: 800; color: #ffffff; }
    .team-name { font-size: 18px; font-weight: 500; color: #e0e0e0; }
    .minute-badge { background: #ff4b4b; color: white; padding: 2px 8px; border-radius: 5px; font-size: 14px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. LÓGICA DE DATOS
# ==========================================

# A. Obtener automáticamente el sorteo más reciente para no mostrar los viejos
try:
    res_sorteo = supabase.table("quinielas_activas").select("sorteo_numero").order("sorteo_numero", desc=True).limit(1).execute()
    sorteo_actual = res_sorteo.data[0]['sorteo_numero'] if res_sorteo.data else 0
except:
    sorteo_actual = 0

st.title("🏆 Resultados Progol en Vivo")
if sorteo_actual:
    st.markdown(f"### 📍 Sorteo Actual: **#{sorteo_actual}**")
else:
    st.warning("No se encontraron sorteos activos.")

# B. Consultar partidos de la DB y datos en vivo de la API
if sorteo_actual > 0:
    # Traer partidos de la DB
    partidos_db = supabase.table("quinielas_activas").select("*").eq("sorteo_numero", sorteo_actual).order("casilla").execute()
    
    # Traer datos en vivo de la API
    url_live = f"https://livescore-api.com/api-client/scores/live.json?key={API_KEY}&secret={SECRET}"
    live_list = []
    try:
        live_res = requests.get(url_live).json()
        if live_res.get('success'):
            live_list = live_res.get('data', {}).get('match', [])
    except: pass
    
    live_map = {str(m['id']): m for m in live_list}

    # ==========================================
    # 4. RENDERIZADO DE CARTELERA
    # ==========================================
    for p in partidos_db.data:
        f_id = str(p['fixture_id'])
        esta_en_vivo = f_id in live_map
        
        # Datos a mostrar
        marcador = live_map[f_id]['score'] if esta_en_vivo else "vs"
        minuto = live_map[f_id]['time'] if esta_en_vivo else p['hora_mx']
        status_color = "#ff4b4b" if esta_en_vivo else "#00ff88"

        st.markdown(f"""
            <div class="match-card" style="border-left-color: {status_color}">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="flex: 1; text-align: right;" class="team-name">{p['local_nombre']}</div>
                    <div style="flex: 1; text-align: center;">
                        <div class="score-text">{marcador}</div>
                        {"<span class='live-indicator'>● EN VIVO</span>" if esta_en_vivo else f"<span style='color:gray;'>{minuto}</span>"}
                        {f"<br><span class='minute-badge'>{minuto}'</span>" if esta_en_vivo else ""}
                    </div>
                    <div style="flex: 1; text-align: left;" class="team-name">{p['visita_nombre']}</div>
                </div>
                <div style="font-size: 12px; color: gray; margin-top: 10px;">Casilla {p['casilla']} | Sorteo {p['sorteo_numero']}</div>
            </div>
        """, unsafe_allow_html=True)

st.button("🔄 Actualizar Marcadores")
