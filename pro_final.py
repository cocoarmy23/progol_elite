import streamlit as st
import requests
from supabase import create_client

# ==========================================
# 1. CONFIGURACIÓN Y CONEXIÓN
# ==========================================
URL_SUPABASE = "https://xavzjoyjausutoscosaw.supabase.co"
KEY_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhhdnpqb3lqYXVzdXRvc2Nvc2F3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjAwNzksImV4cCI6MjA4NTUzNjA3OX0.YjHw-NVeuVpK5l4XkM3hft1vSrERRBXEWZl2wPNjZ0k"
API_KEY = "GQM8r3pQM1JZSH4Z"
SECRET = "9pNSRVoddsshE1elR1tj4TaRVTRNBVNL"

@st.cache_resource
def get_supabase():
    return create_client(URL_SUPABASE, KEY_SUPABASE)

supabase = get_supabase()

st.set_page_config(page_title="Progol Live Elite", layout="wide")

# ==========================================
# 2. ESTILO CSS: LOGOS CON BORDE SUTIL
# ==========================================
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    
    /* Tarjeta principal */
    .match-card {
        background: #1c2531;
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 20px;
        border: 1px solid #2d3848;
        box-shadow: 0 10px 25px rgba(0,0,0,0.3);
    }
    
    /* Contenedor circular del Logo */
    .logo-frame {
        background: white; /* Fondo blanco para que resalte el logo */
        border: 3px solid #2d3848; /* Borde sutil oscuro */
        border-radius: 50%; /* Forma circular */
        width: 80px;
        height: 80px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto;
        padding: 8px;
        box-shadow: inset 0 0 10px rgba(0,0,0,0.1), 0 4px 8px rgba(0,0,0,0.2);
    }

    .logo-img {
        max-width: 100%;
        max-height: 100%;
        object-fit: contain;
    }
    
    .score-box { 
        font-size: 34px; font-weight: 900; 
        color: #00ff88; 
        background: #000; 
        padding: 10px 20px; 
        border-radius: 12px; 
        display: inline-block;
        border: 1px solid #333;
        min-width: 100px;
    }
    
    .score-live { 
        background: #ff4b4b !important; 
        color: white !important;
        border: 2px solid white;
    }

    .team-name { 
        font-size: 14px; 
        font-weight: 800; 
        margin-top: 12px; 
        color: #ffffff;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .live-text { color: #ff4b4b; font-weight: bold; animation: blinker 1.5s infinite; }
    @keyframes blinker { 50% { opacity: 0; } }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. LÓGICA DE DATOS
# ==========================================
@st.cache_data(ttl=60)
def fetch_live():
    try:
        url = f"https://livescore-api.com/api-client/scores/live.json?key={API_KEY}&secret={SECRET}"
        r = requests.get(url, timeout=10).json()
        if r.get('success'):
            return {str(m['id']): m for m in r['data']['match']}
    except: return {}
    return {}

# ==========================================
# 4. RENDERIZADO
# ==========================================
try:
    res_db = supabase.table("quinielas_activas").select("sorteo_numero").order("sorteo_numero", desc=True).limit(1).execute()
    
    if res_db.data:
        sorteo = res_db.data[0]['sorteo_numero']
        st.markdown(f"<h1 style='text-align: center;'>🏆 PROGOL #{sorteo}</h1>", unsafe_allow_html=True)
        
        partidos = supabase.table("quinielas_activas").select("*").eq("sorteo_numero", sorteo).order("casilla").execute()
        live_data = fetch_live()

        for p in partidos.data:
            f_id = str(p['fixture_id'])
            vivo = f_id in live_data
            
            marcador = live_data[f_id]['score'] if vivo else "0 - 0"
            tiempo = f"<div class='live-text'>● EN VIVO {live_data[f_id]['time']}'</div>" if vivo else f"<div style='color:#777;'>🕒 {p['hora_mx']}</div>"
            clase_score = "score-box score-live" if vivo else "score-box"
            
            # Logos con búsqueda mejorada
            url_l = f"https://tse1.mm.bing.net/th?q={p['local_nombre'].replace(' ', '+')}+logo+football&w=100&h=100&c=7"
            url_v = f"https://tse1.mm.bing.net/th?q={p['visita_nombre'].replace(' ', '+')}+logo+football&w=100&h=100&c=7"

            # Renderizado de tarjeta con marcos sutiles
            st.markdown(f"""
            <div class="match-card">
                <div style="font-size:11px; color:#555; margin-bottom:15px; font-weight:bold;">CASILLA {p['casilla']}</div>
                <div style="display: flex; align-items: center; justify-content: space-between; text-align: center;">
                    
                    <div style="flex: 1;">
                        <div class="logo-frame">
                            <img src="{url_l}" class="logo-img">
                        </div>
                        <div class="team-name">{p['local_nombre']}</div>
                    </div>

                    <div style="flex: 1;">
                        <div class="{clase_score}">{marcador}</div>
                        <div style="margin-top:10px;">{tiempo}</div>
                    </div>

                    <div style="flex: 1;">
                        <div class="logo-frame">
                            <img src="{url_v}" class="logo-img">
                        </div>
                        <div class="team-name">{p['visita_nombre']}</div>
                    </div>
                    
                </div>
            </div>
            """, unsafe_allow_html=True)

    else:
        st.write("No hay sorteos activos.")

except Exception as e:
    st.error(f"Error: {e}")

if st.button("ACTUALIZAR"):
    st.rerun()
