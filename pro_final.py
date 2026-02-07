import streamlit as st
import requests
from supabase import create_client
from streamlit_autorefresh import st_autorefresh

# 1. AUTO-REFRESCO
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
    .score-box { font-size: 32px; font-weight: 900; background: #000; padding: 10px; border-radius: 8px; min-width: 110px; text-align: center; color: #00ff88; }
    .score-live { color: #fff; background: #ff4b4b; border: 1px solid white; }
    .logo-container { background: white; border-radius: 50%; width: 65px; height: 65px; display: flex; align-items: center; justify-content: center; margin: 0 auto; }
    .team-logo { width: 45px; height: 45px; object-fit: contain; }
    </style>
""", unsafe_allow_html=True)

# 4. PROCESAMIENTO DE JSON DE LA API
try:
    partidos_db = supabase.table("quinielas_activas").select("*").order("casilla").execute().data

    # Diccionario para guardar lo que encontremos en los JSON
    resultados_api = {}

    # URLs de los JSON (History y Live)
    urls = [
        f"https://livescore-api.com/api-client/matches/history.json?key={API_KEY}&secret={SECRET}",
        f"https://livescore-api.com/api-client/scores/live.json?key={API_KEY}&secret={SECRET}"
    ]

    for url in urls:
        try:
            r = requests.get(url, timeout=10).json()
            # Navegamos el JSON: ['data']['match']
            if r.get('success') and 'data' in r and 'match' in r['data']:
                lista_partidos = r['data']['match']
                for m in lista_partidos:
                    m_id = str(m.get('id')).strip()
                    resultados_api[m_id] = m
        except:
            continue

    # 5. DIBUJAR PARTIDOS
    for p in partidos_db:
        id_progol = str(p['fixture_id']).strip()
        
        # ¿El ID de Supabase está en el JSON de la API?
        datos_encontrados = resultados_api.get(id_progol)

        if datos_encontrados:
            # Extraer marcador del JSON
            marcador = datos_encontrados.get('score', '0 - 0')
            if marcador == '?': marcador = "0 - 0"
            
            # Determinar si es en vivo
            tiempo = str(datos_encontrados.get('time', '')).upper()
            es_live = tiempo != "" and tiempo != "FT" and "FINISHED" not in tiempo
            status_txt = f"🔴 EN VIVO {tiempo}'" if es_live else "✅ FINALIZADO"
        else:
            # Si NO está en el JSON, usar lo que haya en Supabase
            ml = p.get('marcador_local', 0)
            mv = p.get('marcador_visita', 0)
            marcador = f"{ml} - {mv}"
            status_txt = f"🕒 {p['hora_mx']}"
            es_live = False

        # Renderizado
        c_card = "match-card live-card" if es_live else "match-card"
        c_score = "score-box score-live" if es_live else "score-box"
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
                        <div style="margin-top:10px; font-size:12px; font-weight:bold;">{status_txt}</div>
                    </div>
                    <div style="width:35%;">
                        <div class="logo-container"><img src="{v_logo}" class="team-logo"></div>
                        <div style="margin-top:10px; font-weight:bold;">{p['visita_nombre']}</div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"Error al leer los datos: {e}")
