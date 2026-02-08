import streamlit as st
import requests
from supabase import create_client
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 1. CONFIGURACIÓN
st_autorefresh(interval=60000, key="sorteo_api_update")
st.set_page_config(page_title="Progol Live Elite", layout="wide")

# 2. CREDENCIALES
URL_SUPABASE = "https://xavzjoyjausutoscosaw.supabase.co"
KEY_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhhdnpqb3lqYXVzdXRvc2Nvc2F3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjAwNzksImV4cCI6MjA4NTUzNjA3OX0.YjHw-NVeuVpK5l4XkM3hft1vSrERRBXEWZl2wPNjZ0k"
API_KEY = "GQM8r3pQM1JZSH4Z"
SECRET = "9pNSRVoddsshE1elR1tj4TaRVTRNBVNL"

supabase = create_client(URL_SUPABASE, KEY_SUPABASE)

# 3. ESTILOS CSS
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    .header-sorteo { background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%); padding: 10px; border-radius: 10px; text-align: center; margin-bottom: 20px; border: 1px solid #3e5f8a; }
    .match-card { background: #1c2531; border-radius: 15px; padding: 20px; margin-bottom: 15px; border-left: 5px solid #2e7d32; }
    .score-box { font-size: 32px; font-weight: 900; background: #000; padding: 10px; border-radius: 8px; min-width: 110px; text-align: center; color: #00ff88; border: 1px solid #333; }
    .status-live { color: #ff4b4b; font-weight: bold; animation: blinker 1.5s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }
    .logo-container { background: white; border-radius: 50%; width: 60px; height: 60px; display: flex; align-items: center; justify-content: center; margin: 0 auto; }
    .team-logo { width: 42px; height: 42px; object-fit: contain; }
    </style>
""", unsafe_allow_html=True)

# 4. BARRIDO DE API (LIVE + HISTORY)
def obtener_datos_api():
    bolsa = []
    hoy = datetime.now().strftime('%Y-%m-%d')
    # Consultamos ambos endpoints
    urls = [
        f"https://livescore-api.com/api-client/scores/live.json?key={API_KEY}&secret={SECRET}",
        f"https://livescore-api.com/api-client/scores/history.json?key={API_KEY}&secret={SECRET}&from={hoy}"
    ]
    for url in urls:
        try:
            r = requests.get(url, timeout=10).json()
            if r.get('success'):
                matches = r.get('data', {}).get('match', [])
                if isinstance(matches, list): bolsa.extend(matches)
        except: continue
    return bolsa

# 5. LÓGICA PRINCIPAL
try:
    res = supabase.table("quinielas_activas").select("sorteo_numero").order("sorteo_numero", desc=True).limit(1).execute()
    
    if res.data:
        num_sorteo = res.data[0]['sorteo_numero']
        st.markdown(f'<div class="header-sorteo">🏆 <b>PROGOL - SORTEO {num_sorteo}</b></div>', unsafe_allow_html=True)

        partidos_db = supabase.table("quinielas_activas").select("*").eq("sorteo_numero", num_sorteo).order("casilla").execute().data
        api_data = obtener_datos_api()

        for p in partidos_db:
            # ID de referencia de tu base de datos
            target_id = str(p['fixture_id']).strip()
            name_local = p['local_nombre'].upper().strip()
            
            match_found = None
            # BUSCAMOS EL PARTIDO EN EL RESULTADO DE LA API
            for m in api_data:
                # 1. Intentamos por fixture_id (el campo que aparece en tu JSON)
                api_fixture_id = str(m.get('fixture_id', ''))
                # 2. Intentamos por id normal
                api_id = str(m.get('id', ''))
                # 3. Intentamos por nombre dentro del objeto 'home'
                api_home_name = str(m.get('home', {}).get('name', m.get('home_name', ''))).upper()

                if target_id == api_fixture_id or target_id == api_id or name_local in api_home_name:
                    match_found = m
                    break
            
            marcador = "0 - 0"
            status_html = f'<span style="color: #aaa;">🕒 {p["hora_mx"]}</span>'

            if match_found:
                # EXTRAER MARCADOR (Según tu JSON: scores -> score)
                s_obj = match_found.get('scores', {})
                if isinstance(s_obj, dict):
                    marcador = s_obj.get('score') or s_obj.get('ft_score') or match_found.get('score', "0 - 0")
                else:
                    marcador = match_found.get('score', "0 - 0")

                # ESTADO Y TIEMPO
                t = str(match_found.get('time', '')).upper()
                s = str(match_found.get('status', '')).upper()

                if t == "FT" or s in ["FINISHED", "FT"]:
                    status_html = '<span style="color: #00ff88;">✅ FINALIZADO</span>'
                elif s == "HT":
                    status_html = '<span class="status-live">🔴 MEDIO TIEMPO</span>'
                else:
                    status_html = f'<span class="status-live">🔴 {t}\'</span>' if t.replace("'", "").isdigit() else f'<span class="status-live">🔴 {t}</span>'

            # Logos e Interfaz
            l_logo = f"https://tse1.mm.bing.net/th?q={p['local_nombre']}+football+logo&w=100&h=100&c=7"
            v_logo = f"https://tse1.mm.bing.net/th?q={p['visita_nombre']}+football+logo&w=100&h=100&c=7"

            st.markdown(f"""
                <div class="match-card">
                    <div style="display:flex; justify-content:space-between; align-items:center; text-align:center;">
                        <div style="width:35%;">
                            <div class="logo-container"><img src="{l_logo}" class="team-logo"></div>
                            <div style="margin-top:10px; font-weight:bold;">{p['local_nombre']}</div>
                        </div>
                        <div style="width:30%;">
                            <div class="score-box">{marcador}</div>
                            <div style="margin-top:10px; font-size:13px;">{status_html}</div>
                        </div>
                        <div style="width:35%;">
                            <div class="logo-container"><img src="{v_logo}" class="team-logo"></div>
                            <div style="margin-top:10px; font-weight:bold;">{p['visita_nombre']}</div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("No hay sorteos activos.")
except Exception as e:
    st.error(f"Error: {e}")
