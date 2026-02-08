import streamlit as st
import requests
from supabase import create_client
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# 1. CONFIGURACIÓN Y REFRESCO
st_autorefresh(interval=60000, key="progol_elite_final")
st.set_page_config(page_title="Progol Live Elite", layout="wide")

# 2. CREDENCIALES
URL_SUPABASE = "https://xavzjoyjausutoscosaw.supabase.co"
KEY_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhhdnpqb3lqYXVzdXRvc2Nvc2F3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjAwNzksImV4cCI6MjA4NTUzNjA3OX0.YjHw-NVeuVpK5l4XkM3hft1vSrERRBXEWZl2wPNjZ0k"
API_KEY = "GQM8r3pQM1JZSH4Z"
SECRET = "9pNSRVoddsshE1elR1tj4TaRVTRNBVNL"

supabase = create_client(URL_SUPABASE, KEY_SUPABASE)

# 3. ESTILOS CSS (DISEÑO ELITE RECUPERADO)
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    .header-sorteo { background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%); padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 20px; border: 1px solid #3e5f8a; font-size: 20px; font-weight: bold; }
    .match-card { background: #1c2531; border-radius: 15px; padding: 20px; margin-bottom: 15px; border-left: 5px solid #2e7d32; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
    .score-box { font-size: 32px; font-weight: 900; background: #000; padding: 10px; border-radius: 8px; min-width: 110px; text-align: center; color: #00ff88; border: 1px solid #333; }
    .status-live { color: #ff4b4b; font-weight: bold; animation: blinker 1.5s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }
    .logo-container { background: white; border-radius: 50%; width: 60px; height: 60px; display: flex; align-items: center; justify-content: center; margin: 0 auto; }
    .team-logo { width: 42px; height: 42px; object-fit: contain; }
    .team-name { margin-top: 10px; font-weight: bold; font-size: 15px; }
    </style>
""", unsafe_allow_html=True)

# 4. BARRIDO ROBUSTO (ÚLTIMOS 3 DÍAS + LIVE)
def obtener_datos_api():
    bolsa = []
    # 1. Traer partidos EN VIVO
    try:
        r_live = requests.get(f"https://livescore-api.com/api-client/scores/live.json?key={API_KEY}&secret={SECRET}", timeout=10).json()
        if r_live.get('success'):
            bolsa.extend(r_live.get('data', {}).get('match', []))
    except: pass

    # 2. Traer HISTORIAL (Hoy, Ayer, Antier)
    for i in range(3):
        fecha = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        try:
            r_hist = requests.get(f"https://livescore-api.com/api-client/scores/history.json?key={API_KEY}&secret={SECRET}&from={fecha}", timeout=10).json()
            if r_hist.get('success'):
                bolsa.extend(r_hist.get('data', {}).get('match', []))
        except: continue
    return bolsa

# 5. LÓGICA DE PANTALLA
try:
    res = supabase.table("quinielas_activas").select("sorteo_numero").order("sorteo_numero", desc=True).limit(1).execute()
    
    if res.data:
        num_sorteo = res.data[0]['sorteo_numero']
        st.markdown(f'<div class="header-sorteo">🏆 PROGOL - SORTEO {num_sorteo}</div>', unsafe_allow_html=True)

        partidos_db = supabase.table("quinielas_activas").select("*").eq("sorteo_numero", num_sorteo).order("casilla").execute().data
        api_data = obtener_datos_api()

        for p in partidos_db:
            target_fid = str(p['fixture_id']).strip()
            local_db = p['local_nombre'].upper().strip()
            
            match_api = None
            for m in api_data:
                # Prioridad 1: fixture_id | Prioridad 2: id | Prioridad 3: Nombre Local
                api_fid = str(m.get('fixture_id', '')).strip()
                api_id = str(m.get('id', '')).strip()
                api_home = str(m.get('home', {}).get('name', m.get('home_name', ''))).upper()

                if target_fid == api_fid or target_fid == api_id or local_db in api_home:
                    match_api = m
                    break
            
            marcador = "0 - 0"
            status_text = f'<span style="color: #aaa;">🕒 {p["hora_mx"]}</span>'

            if match_api:
                # MARCADOR (Navegación correcta en el JSON)
                scores = match_api.get('scores', {})
                if isinstance(scores, dict):
                    marcador = scores.get('score') or scores.get('ft_score') or match_api.get('score', "0 - 0")
                else:
                    marcador = match_api.get('score', "0 - 0")

                # TIEMPO Y ESTADO
                t = str(match_api.get('time', '')).upper()
                s = str(match_api.get('status', '')).upper()

                if t == "FT" or s in ["FINISHED", "FT"]:
                    status_text = '<span style="color: #00ff88;">✅ FINALIZADO</span>'
                elif s == "HT":
                    status_text = '<span class="status-live">🔴 MEDIO TIEMPO</span>'
                else:
                    # Recuperación del minuto en vivo (con comilla)
                    min_limpio = t.replace("'", "")
                    if min_limpio.isdigit() or "+" in min_limpio:
                        status_text = f'<span class="status-live">🔴 {t}\'</span>'
                    else:
                        status_text = f'<span class="status-live">🔴 {t}</span>'

            # Logos
            l_logo = f"https://tse1.mm.bing.net/th?q={p['local_nombre']}+football+logo&w=100&h=100&c=7"
            v_logo = f"https://tse1.mm.bing.net/th?q={p['visita_nombre']}+football+logo&w=100&h=100&c=7"

            st.markdown(f"""
                <div class="match-card">
                    <div style="display:flex; justify-content:space-between; align-items:center; text-align:center;">
                        <div style="width:35%;">
                            <div class="logo-container"><img src="{l_logo}" class="team-logo"></div>
                            <div class="team-name">{p['local_nombre']}</div>
                        </div>
                        <div style="width:30%;">
                            <div class="score-box">{marcador}</div>
                            <div style="margin-top:10px; font-size:13px;">{status_text}</div>
                        </div>
                        <div style="width:35%;">
                            <div class="logo-container"><img src="{v_logo}" class="team-logo"></div>
                            <div class="team-name">{p['visita_nombre']}</div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("No hay sorteos activos.")
except Exception as e:
    st.error(f"Error: {e}")
