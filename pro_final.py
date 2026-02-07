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

# 3. ESTILO CSS
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    .match-card { background: #1c2531; border-radius: 15px; padding: 20px; margin-bottom: 15px; border-left: 5px solid #2e7d32; }
    .live-card { border-left: 5px solid #ff4b4b !important; background: #251616; }
    .score-box { font-size: 32px; font-weight: 900; background: #000; padding: 10px; border-radius: 8px; min-width: 110px; text-align: center; color: #00ff88; border: 1px solid #333; }
    .score-live { color: #fff; background: #ff4b4b; border: 1px solid white; }
    .logo-container { background: white; border-radius: 50%; width: 65px; height: 65px; display: flex; align-items: center; justify-content: center; margin: 0 auto; }
    .team-logo { width: 45px; height: 45px; object-fit: contain; }
    </style>
""", unsafe_allow_html=True)

# 4. LÓGICA DE DATOS
try:
    # Traer partidos de Supabase
    partidos_db = supabase.table("quinielas_activas").select("*").order("casilla").execute().data

    # BOLSA DE RESULTADOS DE LA API
    all_api_matches = []
    
    try:
        # CONSULTA 1: HISTORIAL (La que tú me pasaste para partidos terminados)
        url_history = f"https://livescore-api.com/api-client/matches/history.json?key={API_KEY}&secret={SECRET}"
        r_hist = requests.get(url_history).json()
        if r_hist.get('success'):
            all_api_matches.extend(r_hist['data']['match'])

        # CONSULTA 2: EN VIVO (Para los que se están jugando ahorita)
        url_live = f"https://livescore-api.com/api-client/scores/live.json?key={API_KEY}&secret={SECRET}"
        r_live = requests.get(url_live).json()
        if r_live.get('success'):
            all_api_matches.extend(r_live['data']['match'])
    except:
        st.warning("Conectando con la central de resultados...")

    for p in partidos_db:
        id_buscado = str(p['fixture_id']).strip()
        marcador_final = "0 - 0"
        status_texto = f"🕒 {p['hora_mx']}"
        es_live = False

        # Buscar el ID en la bolsa de datos combinada
        match_found = next((m for m in all_api_matches if str(m['id']).strip() == id_buscado), None)
        
        if match_found:
            # La API usa 'score' o 'ft_score' para partidos terminados
            marcador_final = match_found.get('score', '0 - 0')
            
            # Detectar si es en vivo o finalizado
            # En history.json el tiempo suele venir como 'FT' o estar vacío
            tiempo_api = str(match_found.get('time', '')).upper()
            
            if tiempo_api in ["FT", "FINISHED", "AET", ""]:
                status_texto = "✅ FINALIZADO"
            else:
                status_texto = f"🔴 EN VIVO {tiempo_api}'"
                es_live = True
        else:
            # Si no hay nada en la API, mostrar lo de Supabase
            ml = p.get('marcador_local', 0)
            mv = p.get('marcador_visita', 0)
            marcador_final = f"{ml} - {mv}"

        # RENDERIZADO HTML
        c_card = "match-card live-card" if es_live else "match-card"
        c_score = "score-box score-live" if es_live else "score-box"
        l_logo = f"https://tse1.mm.bing.net/th?q={p['local_nombre']}+logo+football&w=100&h=100&c=7"
        v_logo = f"https://tse1.mm.bing.net/th?q={p['visita_nombre']}+logo+football&w=100&h=100&c=7"

        st.markdown(f"""
            <div class="{c_card}">
                <div style="display:flex; justify-content:space-between; align-items:center; text-align:center;">
                    <div style="width:35%;">
                        <div class="logo-container"><img src="{l_logo}" class="team-logo"></div>
                        <div style="margin-top:10px; font-weight:bold; font-size:14px;">{p['local_nombre']}</div>
                    </div>
                    <div style="width:30%;">
                        <div class="{c_score}">{marcador_final}</div>
                        <div style="margin-top:10px; font-size:12px; font-weight:bold;">{status_texto}</div>
                    </div>
                    <div style="width:35%;">
                        <div class="logo-container"><img src="{v_logo}" class="team-logo"></div>
                        <div style="margin-top:10px; font-weight:bold; font-size:14px;">{p['visita_nombre']}</div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

except Exception as e:
    st.error("Sincronizando marcadores...")
