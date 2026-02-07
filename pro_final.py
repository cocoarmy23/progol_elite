import streamlit as st
import requests
from supabase import create_client
from streamlit_autorefresh import st_autorefresh

# 1. AUTO-REFRESCO (Cada 60s)
st_autorefresh(interval=60000, key="datarefresh")

# 2. CREDENCIALES
URL_SUPABASE = "https://xavzjoyjausutoscosaw.supabase.co"
KEY_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhhdnpqb3lqYXVzdXRvc2Nvc2F3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjAwNzksImV4cCI6MjA4NTUzNjA3OX0.YjHw-NVeuVpK5l4XkM3hft1vSrERRBXEWZl2wPNjZ0k"
API_KEY = "GQM8r3pQM1JZSH4Z"
SECRET = "9pNSRVoddsshE1elR1tj4TaRVTRNBVNL"

supabase = create_client(URL_SUPABASE, KEY_SUPABASE)

st.set_page_config(page_title="Progol Live Elite", layout="wide")

# 3. ESTILO CSS (MEJORADO)
st.markdown("""
    <style>
    .stApp { background-color: #0e1117 !important; color: white !important; }
    .match-card {
        background: #1c2531;
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 15px;
        border-bottom: 4px solid #2e7d32;
        box-shadow: 0 8px 16px rgba(0,0,0,0.4);
    }
    .live-card { border-bottom: 4px solid #ff4b4b !important; background: linear-gradient(180deg, #1c2531 0%, #251616 100%); }
    .finished-card { border-bottom: 4px solid #555 !important; opacity: 0.9; }
    .logo-container { background: white; border-radius: 50%; width: 70px; height: 70px; display: flex; align-items: center; justify-content: center; margin: 0 auto; border: 2px solid #444; }
    .team-logo { width: 50px; height: 50px; object-fit: contain; }
    .score-box { font-size: 32px; font-weight: 900; color: #00ff88; background: #000; padding: 8px 15px; border-radius: 10px; display: inline-block; min-width: 100px; text-align: center; }
    .score-live { background: #ff4b4b !important; color: white !important; border: 1px solid white; }
    .score-final { color: #aaa; background: #222; }
    .team-name { font-size: 14px; font-weight: 700; margin-top: 10px; color: white; }
    .blink { animation: blinker 1.5s linear infinite; color: #ff4b4b; font-weight: bold; }
    @keyframes blinker { 50% { opacity: 0; } }
    </style>
""", unsafe_allow_html=True)

# 4. LÓGICA DE DATOS
try:
    res_db = supabase.table("quinielas_activas").select("sorteo_numero").order("sorteo_numero", desc=True).limit(1).execute()
    if res_db.data:
        sorteo_actual = res_db.data[0]['sorteo_numero']
        st.markdown(f"<h1 style='text-align: center;'>🏆 RESULTADOS SORTEO {sorteo_actual}</h1>", unsafe_allow_html=True)
        
        partidos = supabase.table("quinielas_activas").select("*").eq("sorteo_numero", sorteo_actual).order("casilla").execute()
        
        # Consultar API para lo que esté pasando en este momento
        live_map = {}
        try:
            live_res = requests.get(f"https://livescore-api.com/api-client/scores/live.json?key={API_KEY}&secret={SECRET}", timeout=5).json()
            if live_res.get('success'):
                matches = live_res.get('data', {}).get('match', [])
                live_map = {str(m['id']): m for m in matches}
        except: pass

        for p in partidos.data:
            f_id = str(p['fixture_id'])
            en_vivo = f_id in live_map
            
            # LÓGICA DE MARCADOR: 
            # 1. Si el partido está en vivo, usar marcador de la API.
            # 2. Si el partido ya terminó y hay marcador en DB, usar ese.
            # 3. Si no, poner 0 - 0.
            if en_vivo:
                marcador = live_map[f_id]['score']
                tiempo = f"<span class='blink'>● {live_map[f_id]['time']}'</span>"
                c_card = "match-card live-card"
                c_score = "score-box score-live"
            elif p.get('marcador_final') and p['marcador_final'] != "0-0":
                marcador = p['marcador_final']
                tiempo = "<span style='color:#888;'>FINALIZADO</span>"
                c_card = "match-card finished-card"
                c_score = "score-box score-final"
            else:
                marcador = "0 - 0"
                tiempo = f"<span>🕒 {p['hora_mx']}</span>"
                c_card = "match-card"
                c_score = "score-box"
            
            log_l = f"https://tse1.mm.bing.net/th?q={p['local_nombre']}+logo+football&w=100&h=100&c=7"
            log_v = f"https://tse1.mm.bing.net/th?q={p['visita_nombre']}+logo+football&w=100&h=100&c=7"

            html_final = "".join([
                f'<div class="{c_card}">',
                f'<div style="font-size:10px; color:#666; font-weight:bold;">CASILLA {p["casilla"]}</div>',
                '<div style="display:flex; justify-content:space-between; align-items:center; text-align:center;">',
                f'<div style="width:35%;"><div class="logo-container"><img src="{log_l}" class="team-logo"></div><div class="team-name">{p["local_nombre"]}</div></div>',
                f'<div style="width:30%;"><div class="{c_score}">{marcador}</div><div style="margin-top:10px;">{tiempo}</div></div>',
                f'<div style="width:35%;"><div class="logo-container"><img src="{log_v}" class="team-logo"></div><div class="team-name">{p["visita_nombre"]}</div></div>',
                '</div></div>'
            ])
            st.markdown(html_final, unsafe_allow_html=True)
except Exception as e:
    st.write("Cargando resultados...")
