import streamlit as st
import requests
from supabase import create_client
from datetime import datetime

# ==========================================
# 1. CONFIGURACIÓN
# ==========================================
URL_SUPABASE = "https://xavzjoyjausutoscosaw.supabase.co"
KEY_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhhdnpqb3lqYXVzdXRvc2Nvc2F3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjAwNzksImV4cCI6MjA4NTUzNjA3OX0.YjHw-NVeuVpK5l4XkM3hft1vSrERRBXEWZl2wPNjZ0k"
API_KEY = "GQM8r3pQM1JZSH4Z"
SECRET = "9pNSRVoddsshE1elR1tj4TaRVTRNBVNL"

supabase = create_client(URL_SUPABASE, KEY_SUPABASE)

# ==========================================
# 2. ESTILO (CSS SEPARADO)
# ==========================================
st.set_page_config(page_title="Progol Live Premium", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117 !important; color: white !important; }
    .match-card {
        background: #1c2531;
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 15px;
        border-left: 6px solid #00ff88;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }
    .live-border { border-left-color: #ff4b4b !important; }
    .score-box { 
        font-size: 32px; font-weight: 900; color: #00ff88; 
        background: rgba(0,0,0,0.5); padding: 5px 15px; 
        border-radius: 8px; display: inline-block;
    }
    .live-text { color: #ff4b4b !important; }
    .team-name { font-size: 14px; font-weight: bold; margin-top: 5px; color: white; }
    .blink { animation: blinker 1.5s linear infinite; color: #ff4b4b; font-weight: bold; }
    @keyframes blinker { 50% { opacity: 0; } }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. LÓGICA DE DATOS
# ==========================================
try:
    # Obtener el sorteo más reciente
    res_db = supabase.table("quinielas_activas").select("sorteo_numero").order("sorteo_numero", desc=True).limit(1).execute()
    
    if res_db.data:
        sorteo_actual = res_db.data[0]['sorteo_numero']
        st.markdown(f"<h1 style='text-align: center;'>Sorteo #{sorteo_actual}</h1>", unsafe_allow_html=True)
        
        partidos_db = supabase.table("quinielas_activas").select("*").eq("sorteo_numero", sorteo_actual).order("casilla").execute()
        
        # Consultar API Live
        live_map = {}
        try:
            live_res = requests.get(f"https://livescore-api.com/api-client/scores/live.json?key={API_KEY}&secret={SECRET}", timeout=5).json()
            if live_res.get('success'):
                matches = live_res.get('data', {}).get('match', [])
                live_map = {str(m['id']): m for m in matches}
        except: pass

        # ==========================================
        # 4. RENDERIZADO (SIN SALTOS DE LÍNEA)
        # ==========================================
        for p in partidos_db.data:
            f_id = str(p['fixture_id'])
            esta_en_vivo = f_id in live_map
            
            marcador = live_map[f_id]['score'] if esta_en_vivo else "VS"
            tiempo = f"<span class='blink'>● {live_map[f_id]['time']}'</span>" if esta_en_vivo else f"<span>{p['hora_mx']}</span>"
            border_class = "live-border" if esta_en_vivo else ""
            score_class = "live-text" if esta_en_vivo else ""

            # Buscador de logos por nombre
            logo_l = f"https://tse1.mm.bing.net/th?q={p['local_nombre']}+logo+football&w=50&h=50&c=7"
            logo_v = f"https://tse1.mm.bing.net/th?q={p['visita_nombre']}+logo+football&w=50&h=50&c=7"

            # CONSTRUCCIÓN EN UNA SOLA LÍNEA PARA EVITAR ERROR HTML
            card_html = f'<div class="match-card {border_class}"><div style="font-size:10px; color:#888;">CASILLA {p["casilla"]}</div><div style="display:flex; justify-content:space-between; align-items:center; text-align:center;"><div style="width:35%;"><img src="{logo_l}" style="width:45px;"><div class="team-name">{p["local_nombre"]}</div></div><div style="width:30%;"><div class="score-box {score_class}">{marcador}</div><div style="margin-top:5px; font-size:12px;">{tiempo}</div></div><div style="width:35%;"><img src="{logo_v}" style="width:45px;"><div class="team-name">{p["visita_nombre"]}</div></div></div></div>'
            
            st.markdown(card_html, unsafe_allow_html=True)
    else:
        st.info("Buscando quinielas activas...")

except Exception as e:
    st.error(f"Error de conexión: {e}")

if st.button("🔄 ACTUALIZAR"):
    st.rerun()
