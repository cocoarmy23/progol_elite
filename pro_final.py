import streamlit as st
import requests
from supabase import create_client
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 1. CONFIGURACIÓN Y REFRESCO (60 segundos)
st_autorefresh(interval=60000, key="progol_update")
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
    .logo-container { background: white; border-radius: 50%; width: 50px; height: 50px; display: flex; align-items: center; justify-content: center; margin: 0 auto; }
    .team-logo { width: 35px; height: 35px; object-fit: contain; }
    </style>
""", unsafe_allow_html=True)

# 4. FUNCIÓN DE BARRIDO INTEGRAL (Live + History del día)
def obtener_api_data():
    pool = []
    # Endpoint de partidos en vivo
    url_live = f"https://livescore-api.com/api-client/scores/live.json?key={API_KEY}&secret={SECRET}"
    # Endpoint de resultados de hoy (para los terminados)
    today = datetime.now().strftime('%Y-%m-%d')
    url_hist = f"https://livescore-api.com/api-client/scores/history.json?key={API_KEY}&secret={SECRET}&from={today}"
    
    for url in [url_live, url_hist]:
        try:
            r = requests.get(url, timeout=10).json()
            if r.get('success'):
                data = r.get('data', {}).get('match', [])
                if isinstance(data, list): pool.extend(data)
        except: continue
    return pool

# 5. LOGICA PRINCIPAL
try:
    # A. Obtener último sorteo
    res = supabase.table("quinielas_activas").select("sorteo_numero").order("sorteo_numero", desc=True).limit(1).execute()
    
    if res.data:
        ultimo_sorteo = res.data[0]['sorteo_numero']
        st.markdown(f'<div class="header-sorteo">🏆 <b>PROGOL - SORTEO {ultimo_sorteo}</b></div>', unsafe_allow_html=True)

        # B. Traer partidos de ese sorteo
        partidos_db = supabase.table("quinielas_activas").select("*").eq("sorteo_numero", ultimo_sorteo).order("casilla").execute().data
        
        # C. Obtener datos frescos de la API
        api_matches = obtener_api_data()

        for p in partidos_db:
            f_id = str(p['fixture_id']).strip()
            # Buscamos el partido en la bolsa por ID (que es lo más seguro según la doc)
            m_api = next((m for m in api_matches if str(m.get('id')) == f_id), None)
            
            # Valores por defecto (Partido no empezado)
            marcador = "0 - 0"
            status_text = f'<span style="color: #aaa;">🕒 {p["hora_mx"]}</span>'

            if m_api:
                # Marcador real (campo 'score' de la API)
                marcador = m_api.get('score', '0 - 0')
                
                # Lógica de Tiempo según la documentación de Livescore-API
                status = str(m_api.get('status')).upper() # LIVE, FT, HT, etc.
                time_val = str(m_api.get('time')) # Minuto actual o FT
                
                if status == "FT" or time_val == "FT" or status == "FINISHED":
                    status_text = '<span style="color: #00ff88;">✅ FINALIZADO</span>'
                elif status == "HT":
                    status_text = '<span class="status-live">🔴 MEDIO TIEMPO</span>'
                elif status == "IN PLAY" or status == "LIVE" or time_val.isdigit():
                    # Si 'time' es un número, es el minuto. Si no, usamos el status.
                    minuto = f"{time_val}'" if time_val.isdigit() else "EN VIVO"
                    status_text = f'<span class="status-live">🔴 {minuto}</span>'

            # Logos (Búsqueda por nombre)
            l_logo = f"https://tse1.mm.bing.net/th?q={p['local_nombre']}+football+logo&w=80&h=80&c=7"
            v_logo = f"https://tse1.mm.bing.net/th?q={p['visita_nombre']}+football+logo&w=80&h=80&c=7"

            st.markdown(f"""
                <div class="match-card">
                    <div style="display:flex; justify-content:space-between; align-items:center; text-align:center;">
                        <div style="width:35%;">
                            <div class="logo-container"><img src="{l_logo}" class="team-logo"></div>
                            <div style="margin-top:10px; font-weight:bold; font-size:14px;">{p['local_nombre']}</div>
                        </div>
                        <div style="width:30%;">
                            <div class="score-box">{marcador}</div>
                            <div style="margin-top:10px; font-size:12px;">{status_text}</div>
                        </div>
                        <div style="width:35%;">
                            <div class="logo-container"><img src="{v_logo}" class="team-logo"></div>
                            <div style="margin-top:10px; font-weight:bold; font-size:14px;">{p['visita_nombre']}</div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("No hay datos en Supabase.")

except Exception as e:
    st.error(f"Error técnico: {e}")
