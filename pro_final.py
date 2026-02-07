import streamlit as st
import requests
from supabase import create_client
from streamlit_autorefresh import st_autorefresh

# ==========================================
# 1. CONFIGURACIÓN Y AUTO-REFRESCO
# ==========================================
# Se actualiza sola cada 60 segundos
st_autorefresh(interval=60000, key="datarefresh")

URL_SUPABASE = "https://xavzjoyjausutoscosaw.supabase.co"
KEY_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhhdnpqb3lqYXVzdXRvc2Nvc2F3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjAwNzksImV4cCI6MjA4NTUzNjA3OX0.YjHw-NVeuVpK5l4XkM3hft1vSrERRBXEWZl2wPNjZ0k"
API_KEY = "GQM8r3pQM1JZSH4Z"
SECRET = "9pNSRVoddsshE1elR1tj4TaRVTRNBVNL"

supabase = create_client(URL_SUPABASE, KEY_SUPABASE)

# ==========================================
# 2. ESTILO PREMIUM (LOGOS CIRCULARES)
# ==========================================
st.set_page_config(page_title="Progol Live Elite", layout="wide")

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

    /* Contenedor Circular para el Logo */
    .logo-container {
        background: white;
        border-radius: 50%;
        width: 75px;
        height: 75px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto;
        box-shadow: 0 4px 10px rgba(0,0,0,0.5);
        border: 3px solid #333;
    }

    .team-logo {
        width: 55px;
        height: 55px;
        object-fit: contain;
    }

    .score-box { 
        font-size: 34px; font-weight: 900; color: #00ff88; 
        background: #000; padding: 10px 20px; 
        border-radius: 12px; display: inline-block;
        min-width: 120px; text-align: center;
        border: 1px solid #333;
    }

    .score-live { 
        background: #ff4b4b !important; 
        color: white !important;
        box-shadow: 0 0 20px rgba(255, 75, 75, 0.5);
        border: 1px solid white;
    }

    .team-name { font-size: 15px; font-weight: 700; margin-top: 12px; color: #ffffff; text-shadow: 1px 1px 2px black; }
    .blink { animation: blinker 1.5s linear infinite; color: #ff4b4b; font-weight: bold; font-size: 14px; }
    @keyframes blinker { 50% { opacity: 0; } }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. LÓGICA DE DATOS
# ==========================================
try:
    # Traer el número del sorteo más reciente
    res_db = supabase.table("quinielas_activas").select("sorteo_numero").order("sorteo_numero", desc=True).limit(1).execute()
    
    if res_db.data:
        sorteo_actual = res_db.data[0]['sorteo_numero']
        st.markdown(f"<h1 style='text-align: center; margin-bottom: 25px;'>🏆 PROGOL SORTEO {sorteo_actual}</h1>", unsafe_allow_html=True)
        
        # Traer todos los partidos de ese sorteo
        partidos = supabase.table("quinielas_activas").select("*").eq("sorteo_numero", sorteo_actual).order("casilla").execute()
        
        # Consultar la API para marcadores en vivo
        live_map = {}
        try:
            live_res = requests.get(f"https://livescore-api.com/api-client/scores/live.json?key={API_KEY}&secret={SECRET}", timeout=5).json()
            if live_res.get('success'):
                matches = live_res.get('data', {}).get('match', [])
                live_map = {str(m['id']): m for m in matches}
        except: pass

        # ==========================================
        # 4. RENDERIZADO DE CARTELERA
        # ==========================================
        for p in partidos.data:
            f_id = str(p['fixture_id'])
            en_vivo = f_id in live_map
            
            # Marcador dinámico: 0-0 si no ha empezado
            marcador = live_map[f_id]['score'] if en_vivo else "0 - 0"
            
            # Tiempo dinámico: Minuto si está en vivo, hora si está programado
            info_tiempo = f"<span class='blink'>● EN VIVO {live_map[f_id]['time']}'</span>" if en_vivo else f"<span style='color:#888;'>🕒 {p['hora_mx']}</span>"
            
            card_class = "match-card live-card" if en_vivo else "match-card"
            score_class = "score-box score-live" if en_vivo else "score-box"

            # Logos: Búsqueda dinámica de alta calidad
            logo_l = f"https://tse1.mm.bing.net/th?q={p['local_nombre']}+logo+football+transparent&w=120&h=120&c=7"
            logo_v = f"https://tse1.mm.bing.net/th?q={p['visita_nombre']}+logo+football+transparent&w=120&h=120&c=7"

            # Construcción HTML
            card_html = f'''
            <div class="{card_class}">
                <div style="font-size:11px; color:#666; font-weight:800; margin-bottom:10px; letter-spacing:1px;">CASILLA {p["casilla"]}</div>
                <div style="display:flex; justify-content:space-between; align-items:center; text-align:center;">
                    <div style="width:35%;">
                        <div class="logo-container"><img src="{logo_l}" class="team-logo"></div>
                        <div class="team-name">{p["local_nombre"]}</div>
                    </div>
                    
                    <div style="width:30%;">
                        <div class="{score_class}">{marcador}</div>
                        <div style="margin-top:12px;">{info_tiempo}</div>
                    </div>
                    
                    <div style="width:35%;">
                        <div class="logo-container"><img src="{logo_v}" class="team-logo"></div>
                        <div class="team-name">{p["visita_nombre"]}</div>
                    </div>
                </div>
            </div>
            '''
            st.markdown(card_html, unsafe_allow_html=True)
    else:
        st.warning("No hay sorteos activos registrados.")

except Exception as e:
    st.error(f"Error cargando datos: {e}")
