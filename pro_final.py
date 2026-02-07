import streamlit as st
import requests
from supabase import create_client
from streamlit_autorefresh import st_autorefresh

# 1. ACTUALIZACIÓN AUTOMÁTICA
st_autorefresh(interval=60000, key="datarefresh")

# 2. CONEXIONES
URL_SUPABASE = "https://xavzjoyjausutoscosaw.supabase.co"
KEY_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhhdnpqb3lqYXVzdXRvc2Nvc2F3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjAwNzksImV4cCI6MjA4NTUzNjA3OX0.YjHw-NVeuVpK5l4XkM3hft1vSrERRBXEWZl2wPNjZ0k"
API_KEY = "GQM8r3pQM1JZSH4Z"
SECRET = "9pNSRVoddsshE1elR1tj4TaRVTRNBVNL"

supabase = create_client(URL_SUPABASE, KEY_SUPABASE)

st.set_page_config(page_title="Progol Live Elite", layout="wide")

# 3. ESTILOS CSS
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    .match-card { background: #1c2531; border-radius: 15px; padding: 20px; margin-bottom: 15px; border-left: 5px solid #2e7d32; }
    .live-card { border-left: 5px solid #ff4b4b !important; background: #251616; }
    .score-box { font-size: 30px; font-weight: 900; background: #000; padding: 10px; border-radius: 8px; min-width: 100px; text-align: center; color: #00ff88; }
    .score-live { color: #fff; background: #ff4b4b; box-shadow: 0 0 10px #ff4b4b; }
    .logo-container { background: white; border-radius: 50%; width: 60px; height: 60px; display: flex; align-items: center; justify-content: center; margin: 0 auto; }
    .team-logo { width: 40px; height: 40px; object-fit: contain; }
    </style>
""", unsafe_allow_html=True)

# 4. OBTENCIÓN DE DATOS (DOBLE VÍA)
try:
    # Traer partidos de DB
    partidos_db = supabase.table("quinielas_activas").select("*").order("casilla").execute().data

    # Obtener partidos EN VIVO
    live_matches = []
    try:
        r_live = requests.get(f"https://livescore-api.com/api-client/scores/live.json?key={API_KEY}&secret={SECRET}").json()
        if r_live.get('success'): live_matches = r_live['data']['match']
    except: pass

    # Obtener partidos de AYER/HOY (Histórico para terminados)
    history_matches = []
    try:
        # Consultamos los resultados de hoy para capturar los que ya terminaron
        r_hist = requests.get(f"https://livescore-api.com/api-client/scores/history.json?key={API_KEY}&secret={SECRET}").json()
        if r_hist.get('success'): history_matches = r_hist['data']['match']
    except: pass

    for p in partidos_db:
        id_buscado = str(p['fixture_id']).strip()
        marcador = "0 - 0"
        tiempo = f"🕒 {p['hora_mx']}"
        es_live = False

        # 1. BUSCAR EN VIVO
        match_data = next((m for m in live_matches if str(m['id']) == id_buscado), None)
        if match_data:
            marcador = match_data['score']
            tiempo = f"🔴 EN VIVO {match_data['time']}'"
            es_live = True
        else:
            # 2. BUSCAR EN HISTÓRICO (Si ya terminó)
            match_data = next((m for m in history_matches if str(m['id']) == id_buscado), None)
            if match_data:
                marcador = match_data['score']
                tiempo = "✅ FINALIZADO"

        # Clases de estilo
        c_card = "match-card live-card" if es_live else "match-card"
        c_score = "score-box score-live" if es_live else "score-box"

        # LOGOS
        l_logo = f"https://tse1.mm.bing.net/th?q={p['local_nombre']}+logo+football&w=100&h=100&c=7"
        v_logo = f"https://tse1.mm.bing.net/th?q={p['visita_nombre']}+logo+football&w=100&h=100&c=7"

        st.markdown(f"""
            <div class="{c_card}">
                <div style="display:flex; justify-content:space-between; align-items:center; text-align:center;">
                    <div style="width:35%;">
                        <div class="logo-container"><img src="{l_logo}" class="team-logo"></div>
                        <div style="margin-top:10px; font-weight:bold;">{p['local_nombre']}</div>
                    </div>
                    <div style="width:30%;">
                        <div class="{c_score}">{marcador}</div>
                        <div style="margin-top:10px; font-size:12px;">{tiempo}</div>
                    </div>
                    <div style="width:35%;">
                        <div class="logo-container"><img src="{v_logo}" class="team-logo"></div>
                        <div style="margin-top:10px; font-weight:bold;">{p['visita_nombre']}</div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

except Exception as e:
    st.error("Sincronizando marcadores...")
