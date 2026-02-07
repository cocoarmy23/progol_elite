import streamlit as st
import requests
from supabase import create_client
from streamlit_autorefresh import st_autorefresh

# 1. AUTO-REFRESCO: Se actualiza cada 60 segundos para mantener la app viva y los goles al día
st_autorefresh(interval=60000, key="datarefresh")

# 2. CREDENCIALES
URL_SUPABASE = "https://xavzjoyjausutoscosaw.supabase.co"
KEY_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhhdnpqb3lqYXVzdXRvc2Nvc2F3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjAwNzksImV4cCI6MjA4NTUzNjA3OX0.YjHw-NVeuVpK5l4XkM3hft1vSrERRBXEWZl2wPNjZ0k"
API_KEY = "GQM8r3pQM1JZSH4Z"
SECRET = "9pNSRVoddsshE1elR1tj4TaRVTRNBVNL"

supabase = create_client(URL_SUPABASE, KEY_SUPABASE)

# CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Progol Live Elite", layout="wide", page_icon="🏆")

# 3. ESTILO CSS PROFESIONAL
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
    .live-card { 
        border-bottom: 4px solid #ff4b4b !important; 
        background: linear-gradient(180deg, #1c2531 0%, #251616 100%);
    }
    .logo-container {
        background: white;
        border-radius: 50%;
        width: 70px;
        height: 70px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto;
        border: 2px solid #444;
    }
    .team-logo { width: 48px; height: 48px; object-fit: contain; }
    .score-box { 
        font-size: 32px; font-weight: 900; color: #00ff88; 
        background: #000; padding: 8px 15px; 
        border-radius: 10px; display: inline-block;
        min-width: 105px; text-align: center;
        border: 1px solid #333;
    }
    .score-live { background: #ff4b4b !important; color: white !important; border: 1px solid white; box-shadow: 0 0 15px rgba(255, 75, 75, 0.4); }
    .team-name { font-size: 14px; font-weight: 700; margin-top: 10px; color: white; text-transform: uppercase; }
    .blink { animation: blinker 1.5s linear infinite; color: #ff4b4b; font-weight: bold; }
    @keyframes blinker { 50% { opacity: 0; } }
    </style>
""", unsafe_allow_html=True)

# 4. LÓGICA DE DATOS Y RENDERIZADO
try:
    # Obtener el sorteo más reciente basándose en el número mayor
    res_db = supabase.table("quinielas_activas").select("sorteo_numero").order("sorteo_numero", desc=True).limit(1).execute()
    
    if res_db.data:
        sorteo_actual = res_db.data[0]['sorteo_numero']
        st.markdown(f"<h1 style='text-align: center; margin-bottom: 25px;'>🏆 PROGOL SORTEO {sorteo_actual}</h1>", unsafe_allow_html=True)
        
        # Traer partidos del sorteo
        partidos = supabase.table("quinielas_activas").select("*").eq("sorteo_numero", sorteo_actual).order("casilla").execute()
        
        # Consultar API de Marcadores en Vivo
        live_map = {}
        try:
            live_res = requests.get(f"https://livescore-api.com/api-client/scores/live.json?key={API_KEY}&secret={SECRET}", timeout=10).json()
            if live_res.get('success'):
                matches = live_res.get('data', {}).get('match', [])
                # Creamos el mapa usando strings para evitar errores de tipo de dato
                live_map = {str(m['id']).strip(): m for m in matches}
        except:
            st.warning("Señal de marcadores en vivo inestable... reconectando.")

        # Iterar sobre los partidos de la base de datos
        for p in partidos.data:
            f_id_db = str(p['fixture_id']).strip()
            
            # Buscamos si este ID está en el mapa de la API
            datos_api = live_map.get(f_id_db)

            if datos_api:
                # --- CASO A: EL PARTIDO ESTÁ EN VIVO ---
                marcador = datos_api.get('score', '0 - 0')
                minuto = datos_api.get('time', '0')
                info_tiempo = f"<span class='blink'>● EN VIVO {minuto}'</span>"
                c_card = "match-card live-card"
                c_score = "score-box score-live"
            else:
                # --- CASO B: EL PARTIDO NO ESTÁ EN VIVO (Programado o Terminado) ---
                m_local = p.get('marcador_local', 0)
                m_visita = p.get('marcador_visita', 0)
                
                # Si en Supabase ambos son 0, asumimos que no ha empezado
                if m_local == 0 and m_visita == 0:
                    marcador = "0 - 0"
                    info_tiempo = f"<span>🕒 {p['hora_mx']}</span>"
                else:
                    # Si ya hay datos en Supabase, es resultado final
                    marcador = f"{m_local} - {m_visita}"
                    info_tiempo = "<span style='color:#00ff88;'>FINALIZADO</span>"
                
                c_card = "match-card"
                c_score = "score-box"
            
            # Logos dinámicos
            log_l = f"https://tse1.mm.bing.net/th?q={p['local_nombre']}+logo+football&w=100&h=100&c=7"
            log_v = f"https://tse1.mm.bing.net/th?q={p['visita_nombre']}+logo+football&w=100&h=100&c=7"

            # Construcción del HTML final
            html_final = "".join([
                f'<div class="{c_card}">',
                f'<div style="font-size:11px; color:#666; font-weight:bold; margin-bottom:10px;">CASILLA {p["casilla"]}</div>',
                '<div style="display:flex; justify-content:space-between; align-items:center; text-align:center;">',
                f'<div style="width:35%;"><div class="logo-container"><img src="{log_l}" class="team-logo"></div><div class="team-name">{p["local_nombre"]}</div></div>',
                f'<div style="width:30%;"><div class="{c_score}">{marcador}</div><div style="margin-top:10px; font-size:13px;">{info_tiempo}</div></div>',
                f'<div style="width:35%;"><div class="logo-container"><img src="{log_v}" class="team-logo"></div><div class="team-name">{p["visita_nombre"]}</div></div>',
                '</div></div>'
            ])
            st.markdown(html_final, unsafe_allow_html=True)
    else:
        st.info("No se encontraron quinielas activas en la base de datos.")

except Exception as e:
    st.error("Sincronizando con el servidor de datos...")
