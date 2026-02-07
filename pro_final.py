import streamlit as st
import requests
from supabase import create_client
from streamlit_autorefresh import st_autorefresh

# 1. FORZAR ACTUALIZACIÓN CADA MINUTO
st_autorefresh(interval=60000, key="datarefresh")

# 2. CONEXIÓN
URL_SUPABASE = "https://xavzjoyjausutoscosaw.supabase.co"
KEY_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhhdnpqb3lqYXVzdXRvc2Nvc2F3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjAwNzksImV4cCI6MjA4NTUzNjA3OX0.YjHw-NVeuVpK5l4XkM3hft1vSrERRBXEWZl2wPNjZ0k"
API_KEY = "GQM8r3pQM1JZSH4Z"
SECRET = "9pNSRVoddsshE1elR1tj4TaRVTRNBVNL"

supabase = create_client(URL_SUPABASE, KEY_SUPABASE)

st.set_page_config(page_title="Progol Live Elite", layout="wide")

# 3. DISEÑO
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    .match-card { background: #1c2531; border-radius: 15px; padding: 20px; margin-bottom: 15px; border-left: 5px solid #2e7d32; }
    .live-card { border-left: 5px solid #ff4b4b !important; background: #251616; }
    .logo-container { background: white; border-radius: 50%; width: 60px; height: 60px; display: flex; align-items: center; justify-content: center; margin: 0 auto; }
    .team-logo { width: 40px; height: 40px; object-fit: contain; }
    .score-box { font-size: 30px; font-weight: 900; background: #000; padding: 10px; border-radius: 8px; min-width: 100px; text-align: center; color: #00ff88; }
    .score-live { color: #fff; background: #ff4b4b; box-shadow: 0 0 10px #ff4b4b; }
    .blink { animation: blinker 1.5s linear infinite; color: #ff4b4b; }
    @keyframes blinker { 50% { opacity: 0; } }
    </style>
""", unsafe_allow_html=True)

# 4. OBTENER DATOS
try:
    # Traer partidos de Supabase
    res = supabase.table("quinielas_activas").select("*").order("casilla").execute()
    partidos_db = res.data

    # Traer datos de la API
    live_data = []
    try:
        api_url = f"https://livescore-api.com/api-client/scores/live.json?key={API_KEY}&secret={SECRET}"
        response = requests.get(api_url, timeout=10).json()
        if response.get('success'):
            live_data = response['data']['match']
    except:
        st.error("Error conectando con la API de resultados.")

    for p in partidos_db:
        # Buscamos este partido en lo que nos mandó la API
        match_api = None
        id_buscado = str(p['fixture_id']).strip()
        
        for m in live_data:
            if str(m['id']).strip() == id_buscado:
                match_api = m
                break
        
        # LÓGICA DE VISUALIZACIÓN
        if match_api:
            # SI ESTÁ EN VIVO (Manda la API)
            marcador = match_api['score']
            tiempo = f"<span class='blink'>● {match_api['time']}'</span>"
            estilo_card = "match-card live-card"
            estilo_score = "score-box score-live"
        else:
            # SI NO ESTÁ EN VIVO (Manda Supabase)
            # Usamos marcador_local y marcador_visita que ya tienes en tus columnas
            ml = p.get('marcador_local', 0)
            mv = p.get('marcador_visita', 0)
            marcador = f"{ml} - {mv}"
            tiempo = "FINALIZADO / PENDIENTE"
            estilo_card = "match-card"
            estilo_score = "score-box"

        # LOGOS
        l_logo = f"https://tse1.mm.bing.net/th?q={p['local_nombre']}+logo+football&w=100&h=100&c=7"
        v_logo = f"https://tse1.mm.bing.net/th?q={p['visita_nombre']}+logo+football&w=100&h=100&c=7"

        # HTML
        st.markdown(f"""
            <div class="{estilo_card}">
                <div style="display:flex; justify-content:space-between; align-items:center; text-align:center;">
                    <div style="width:35%;">
                        <div class="logo-container"><img src="{l_logo}" class="team-logo"></div>
                        <div style="margin-top:10px; font-weight:bold;">{p['local_nombre']}</div>
                    </div>
                    <div style="width:30%;">
                        <div class="{estilo_score}">{marcador}</div>
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
    st.error(f"Error general: {e}")
