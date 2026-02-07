import streamlit as st
import requests
from supabase import create_client
from datetime import datetime, timedelta
import pytz
from streamlit_autorefresh import st_autorefresh 

# --- Configuración de página ---
st.set_page_config(page_title="Progol Élite", page_icon="⚽", layout="centered")

# 1. Autorefresh: La página se actualiza sola cada 60 segundos
st_autorefresh(interval=60000, key="fustats_refresh")

# --- Credenciales ---
URL_SUPABASE = "https://xavzjoyjausutoscosaw.supabase.co"
KEY_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhhdnpqb3lqYXVzdXRvc2Nvc2F3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjAwNzksImV4cCI6MjA4NTUzNjA3OX0.YjHw-NVeuVpK5l4XkM3hft1vSrERRBXEWZl2wPNjZ0k"
API_KEY = "7ec8e70df61e8ff10111253b825be068" 

supabase = create_client(URL_SUPABASE, KEY_SUPABASE)
headers = {'x-apisports-key': API_KEY.strip()}

# --- Estilo Visual ---
st.markdown("""
    <style>
    .stApp { background: #0e1117; }
    .match-card {
        border-radius: 15px; padding: 20px; margin-bottom: 15px;
        border: 1px solid rgba(255,255,255,0.1); font-family: 'sans-serif';
    }
    .card-live { background: rgba(0, 255, 65, 0.07); border: 1px solid #00FF41; box-shadow: 0 0 10px rgba(0,255,65,0.2); }
    .card-finished { background: rgba(255, 255, 255, 0.02); opacity: 0.7; }
    .card-pending { background: rgba(255, 255, 255, 0.05); }
    
    .team-name { color: white; font-weight: 800; font-size: 18px; width: 40%; line-height: 1.2; }
    .score-box { font-size: 32px; font-weight: 900; min-width: 90px; text-align: center; }
    .status-text { text-align: center; font-size: 12px; font-weight: bold; margin-top: 10px; color: #888; text-transform: uppercase; }
    .live-dot { color: #00FF41; animation: blinker 1s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }
    </style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=60)
def fetch_match(f_id):
    url = f"https://v3.football.api-sports.io/fixtures?id={f_id}"
    try:
        r = requests.get(url, headers=headers, timeout=10).json()
        return r['response'][0] if r.get('response') else None
    except:
        return None

# --- UI ---
st.title("⚽ PROGOL ÉLITE")

tab1, tab2 = st.tabs(["📊 QUINIELA", "💎 EL FIJO"])

with tab1:
    try:
        partidos = supabase.table("quinielas_activas").select("*").order("casilla").execute().data
        
        for p in partidos:
            info = fetch_match(p['fixture_id'])
            
            # Valores por defecto si falla la API
            g_l, g_v = 0, 0
            status = "NS"
            elapsed = 0
            logo_l, logo_v = "", ""
            card_class = "card-pending"
            st_txt = "Pendiente"

            if info:
                g_l = info['goals']['home'] if info['goals']['home'] is not None else 0
                g_v = info['goals']['away'] if info['goals']['away'] is not None else 0
                status = info['fixture']['status']['short']
                elapsed = info['fixture']['status']['elapsed']
                logo_l = info['teams']['home']['logo']
                logo_v = info['teams']['away']['logo']

                if status in ["1H", "2H", "HT"]:
                    card_class = "card-live"
                    st_txt = f"<span class='live-dot'>● EN VIVO {elapsed}'</span>"
                elif status == "FT":
                    card_class = "card-finished"
                    st_txt = "Finalizado"
                else:
                    dt = datetime.strptime(info['fixture']['date'], "%Y-%m-%dT%H:%M:%S+00:00") - timedelta(hours=6)
                    st_txt = dt.strftime("%d/%m %H:%M")

            # Renderizado de la tarjeta
            st.markdown(f"""
                <div class="match-card {card_class}">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div class="team-name" style="text-align: right;">
                            {p['local_nombre']} <img src="{logo_l}" width="30" style="margin-left:10px">
                        </div>
                        <div class="score-box" style="color: {'#00FF41' if 'VIVO' in st_txt else 'white'};">
                            {g_l} - {g_v}
                        </div>
                        <div class="team-name" style="text-align: left;">
                            <img src="{logo_v}" width="30" style="margin-right:10px"> {p['visita_nombre']}
                        </div>
                    </div>
                    <div class="status-text">
                        CASILLA {p['casilla']} | {st_txt}
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
    except Exception as e:
        st.error(f"Error al cargar datos: {e}")

with tab2:
    st.subheader("🔥 El Partido de la Semana")
    st.write("Contenido exclusivo del partido fijo.")
