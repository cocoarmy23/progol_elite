import streamlit as st
import requests
from supabase import create_client
from datetime import datetime

# ==========================================
# 1. CONFIGURACIÓN Y CONEXIÓN
# ==========================================
URL_SUPABASE = "https://xavzjoyjausutoscosaw.supabase.co"
KEY_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhhdnpqb3lqYXVzdXRvc2Nvc2F3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjAwNzksImV4cCI6MjA4NTUzNjA3OX0.YjHw-NVeuVpK5l4XkM3hft1vSrERRBXEWZl2wPNjZ0k"
API_KEY = "GQM8r3pQM1JZSH4Z"
SECRET = "9pNSRVoddsshE1elR1tj4TaRVTRNBVNL"

supabase = create_client(URL_SUPABASE, KEY_SUPABASE)

# ==========================================
# 2. ESTILO PREMIUM (FOCO EN EL MARCADOR VIVO)
# ==========================================
st.set_page_config(page_title="Progol Live Elite", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117 !important; color: white !important; }
    .match-card {
        background: #1c2531;
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 12px;
        border-left: 6px solid #2e7d32; /* Verde por defecto */
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }
    .live-card { 
        border-left: 6px solid #ff4b4b !important; 
        background: linear-gradient(90deg, #1c2531 0%, #2b1b1b 100%);
    }
    .score-box { 
        font-size: 30px; font-weight: 900; color: #00ff88; 
        background: rgba(0,0,0,0.6); padding: 8px 18px; 
        border-radius: 10px; display: inline-block;
        min-width: 90px; text-align: center;
        border: 1px solid #333;
    }
    .score-live { 
        color: #ffffff !important; 
        background: #ff4b4b !important; 
        border: 1px solid #ffffff;
        box-shadow: 0 0 10px rgba(255, 75, 75, 0.6);
    }
    .team-name { font-size: 15px; font-weight: bold; margin-top: 8px; color: white; }
    .blink { animation: blinker 1.5s linear infinite; color: #ff4b4b; font-weight: bold; }
    @keyframes blinker { 50% { opacity: 0; } }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. LÓGICA DE DATOS
# ==========================================
try:
    # Obtener el sorteo más reciente (el último que registraste)
    res_db = supabase.table("quinielas_activas").select("sorteo_numero").order("sorteo_numero", desc=True).limit(1).execute()
    
    if res_db.data:
        sorteo_actual = res_db.data[0]['sorteo_numero']
        st.markdown(f"<h1 style='text-align: center;'>🏆 SORTEO #{sorteo_actual}</h1>", unsafe_allow_html=True)
        
        partidos_db = supabase.table("quinielas_activas").select("*").eq("sorteo_numero", sorteo_actual).order("casilla").execute()
        
        # Consultar API de marcadores en vivo
        live_map = {}
        try:
            live_res = requests.get(f"https://livescore-api.com/api-client/scores/live.json?key={API_KEY}&secret={SECRET}", timeout=5).json()
            if live_res.get('success'):
                matches = live_res.get('data', {}).get('match', [])
                live_map = {str(m['id']): m for m in matches}
        except: pass

        # ==========================================
        # 4. RENDERIZADO DE CARTELERA
        # ==========================================
        for p in partidos_db.data:
            f_id = str(p['fixture_id'])
            esta_en_vivo = f_id in live_map
            
            # Si está en vivo sacamos marcador y minuto de la API, si no, valores base
            marcador = live_map[f_id]['score'] if esta_en_vivo else "0 - 0"
            minuto_val = live_map[f_id]['time'] if esta_en_vivo else p['hora_mx']
            
            # Clases visuales dinámicas
            card_class = "match-card live-card" if esta_en_vivo else "match-card"
            score_class = "score-box score-live" if esta_en_vivo else "score-box"
            tiempo_html = f"<span class='blink'>● {minuto_val}'</span>" if esta_en_vivo else f"<span style='color:#888;'>🕒 {minuto_val}</span>"

            # Logos dinámicos
            logo_l = f"https://tse1.mm.bing.net/th?q={p['local_nombre']}+football+logo&w=60&h=60&c=7"
            logo_v = f"https://tse1.mm.bing.net/th?q={p['visita_nombre']}+football+logo&w=60&h=60&c=7"

            # Construcción HTML
            card_html = f'''
            <div class="{card_class}">
                <div style="font-size:11px; color:#888; font-weight:bold; margin-bottom:5px;">CASILLA {p["casilla"]}</div>
                <div style="display:flex; justify-content:space-between; align-items:center; text-align:center;">
                    <div style="width:35%;">
                        <img src="{logo_l}" style="height:45px; width:45px; object-fit:contain;">
                        <div class="team-name">{p["local_nombre"]}</div>
                    </div>
                    <div style="width:30%;">
                        <div class="{score_class}">{marcador}</div>
                        <div style="margin-top:8px; font-size:13px;">{tiempo_html}</div>
                    </div>
                    <div style="width:35%;">
                        <img src="{logo_v}" style="height:45px; width:45px; object-fit:contain;">
                        <div class="team-name">{p["visita_nombre"]}</div>
                    </div>
                </div>
            </div>
            '''
            st.markdown(card_html, unsafe_allow_html=True)
    else:
        st.info("No hay partidos registrados en el sorteo actual.")

except Exception as e:
    st.error(f"Error de conexión: {e}")
