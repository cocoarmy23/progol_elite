import streamlit as st
import requests
from supabase import create_client
import time

# ==========================================
# 1. CONFIGURACIÓN Y CONEXIÓN
# ==========================================
URL_SUPABASE = "https://xavzjoyjausutoscosaw.supabase.co"
KEY_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhhdnpqb3lqYXVzdXRvc2Nvc2F3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjAwNzksImV4cCI6MjA4NTUzNjA3OX0.YjHw-NVeuVpK5l4XkM3hft1vSrERRBXEWZl2wPNjZ0k"
API_KEY = "GQM8r3pQM1JZSH4Z"
SECRET = "9pNSRVoddsshE1elR1tj4TaRVTRNBVNL"

supabase = create_client(URL_SUPABASE, KEY_SUPABASE)

st.set_page_config(page_title="Progol Live Elite", layout="wide")

# ==========================================
# 2. LÓGICA DE AUTO-REFRESCO NATIVO
# ==========================================
# Esto recargará la app cada 60 segundos sin librerías extras
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()

# Botón manual y contador invisible
col_refresh, col_title = st.columns([1, 5])
with col_refresh:
    if st.button("🔄 Actualizar"):
        st.rerun()

# ==========================================
# 3. ESTILO CSS (PREMIUM)
# ==========================================
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    .match-card {
        background: #1c2531;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 15px;
        border-left: 6px solid #2e7d32;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }
    .live-card { 
        border-left: 6px solid #ff4b4b !important; 
        background: linear-gradient(90deg, #1c2531 0%, #2b1b1b 100%);
    }
    .score-box { 
        font-size: 32px; font-weight: 900; color: #00ff88; 
        background: rgba(0,0,0,0.6); padding: 10px 20px; 
        border-radius: 12px; display: inline-block;
        min-width: 100px; text-align: center;
        border: 1px solid #333;
    }
    .score-live { 
        color: #ffffff !important; 
        background: #ff4b4b !important; 
    }
    .team-name { font-size: 16px; font-weight: bold; margin-top: 10px; }
    .blink { animation: blinker 1.5s linear infinite; color: #ff4b4b; font-weight: bold; }
    @keyframes blinker { 50% { opacity: 0; } }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 4. LÓGICA DE DATOS
# ==========================================
@st.cache_data(ttl=60)
def get_live_data():
    try:
        url = f"https://livescore-api.com/api-client/scores/live.json?key={API_KEY}&secret={SECRET}"
        r = requests.get(url, timeout=10).json()
        if r.get('success'):
            return {str(m['id']): m for m in r['data']['match']}
    except:
        return {}
    return {}

try:
    # Obtener sorteo
    res_db = supabase.table("quinielas_activas").select("sorteo_numero").order("sorteo_numero", desc=True).limit(1).execute()
    
    if res_db.data:
        sorteo_actual = res_db.data[0]['sorteo_numero']
        st.markdown(f"<h1 style='text-align: center;'>🏆 PROGOL #{sorteo_actual}</h1>", unsafe_allow_html=True)
        
        partidos = supabase.table("quinielas_activas").select("*").eq("sorteo_numero", sorteo_actual).order("casilla").execute()
        live_map = get_live_data()

        for p in partidos.data:
            f_id = str(p['fixture_id'])
            en_vivo = f_id in live_map
            
            marcador = live_map[f_id]['score'] if en_vivo else "0 - 0"
            tiempo = f"<span class='blink'>● {live_map[f_id]['time']}'</span>" if en_vivo else f"🕒 {p['hora_mx']}"
            
            card_style = "match-card live-card" if en_vivo else "match-card"
            score_style = "score-box score-live" if en_vivo else "score-box"

            logo_l = f"https://tse1.mm.bing.net/th?q={p['local_nombre'].replace(' ', '+')}+logo&w=60&h=60&c=7"
            logo_v = f"https://tse1.mm.bing.net/th?q={p['visita_nombre'].replace(' ', '+')}+logo&w=60&h=60&c=7"

            st.markdown(f'''
            <div class="{card_style}">
                <div style="font-size:10px; color:#888;">CASILLA {p['casilla']}</div>
                <div style="display:flex; justify-content:space-between; align-items:center; text-align:center;">
                    <div style="width:35%;">
                        <img src="{logo_l}" width="50">
                        <div class="team-name">{p['local_nombre']}</div>
                    </div>
                    <div style="width:30%;">
                        <div class="{score_style}">{marcador}</div>
                        <div style="margin-top:10px;">{tiempo}</div>
                    </div>
                    <div style="width:35%;">
                        <img src="{logo_v}" width="50">
                        <div class="team-name">{p['visita_nombre']}</div>
                    </div>
                </div>
            </div>
            ''', unsafe_allow_html=True)
    else:
        st.warning("No hay datos en Supabase.")
except Exception as e:
    st.error(f"Error: {e}")
