import streamlit as st
import requests
from supabase import create_client
import time

# ==========================================
# 1. CONFIGURACIÓN
# ==========================================
URL_SUPABASE = "https://xavzjoyjausutoscosaw.supabase.co"
KEY_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhhdnpqb3lqYXVzdXRvc2Nvc2F3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjAwNzksImV4cCI6MjA4NTUzNjA3OX0.YjHw-NVeuVpK5l4XkM3hft1vSrERRBXEWZl2wPNjZ0k"
API_KEY = "GQM8r3pQM1JZSH4Z"
SECRET = "9pNSRVoddsshE1elR1tj4TaRVTRNBVNL"

# Conexión Segura
@st.cache_resource
def init_connection():
    return create_client(URL_SUPABASE, KEY_SUPABASE)

supabase = init_connection()

st.set_page_config(page_title="Progol Live Elite", layout="wide")

# ==========================================
# 2. ESTILO CSS MEJORADO
# ==========================================
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; color: white; }
    
    .match-card {
        background: linear-gradient(145deg, #161b22, #1f2630);
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 20px;
        border: 1px solid rgba(255,255,255,0.05);
        box-shadow: 5px 5px 15px rgba(0,0,0,0.5);
    }
    
    .logo-img {
        filter: drop-shadow(0px 4px 6px rgba(0,0,0,0.6));
        object-fit: contain;
        max-height: 70px;
        width: auto;
    }
    
    .score-box { 
        font-size: 32px; font-weight: 900; 
        color: #00ff88; 
        background: #000000; 
        padding: 10px 20px; 
        border-radius: 12px; 
        display: inline-block;
        border: 1px solid #333;
        min-width: 110px;
    }
    
    .score-live { 
        background: #ff4b4b !important; 
        color: white !important;
        box-shadow: 0 0 15px rgba(255, 75, 75, 0.4);
        border: 1px solid white;
    }

    .team-text { 
        font-size: 15px; 
        font-weight: 700; 
        margin-top: 10px; 
        color: #ffffff;
        text-transform: uppercase;
    }
    
    .live-dot { color: #ff4b4b; animation: blinker 1.2s infinite; font-weight: bold; }
    @keyframes blinker { 50% { opacity: 0; } }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. FUNCIONES DE DATOS
# ==========================================
@st.cache_data(ttl=60)
def get_live_data():
    try:
        url = f"https://livescore-api.com/api-client/scores/live.json?key={API_KEY}&secret={SECRET}"
        r = requests.get(url, timeout=10).json()
        if r.get('success'):
            matches = r['data']['match']
            return {str(m['id']): m for m in matches}
    except:
        return {}
    return {}

# ==========================================
# 4. RENDERIZADO PRINCIPAL
# ==========================================
try:
    # 1. Obtener Sorteo
    res_db = supabase.table("quinielas_activas").select("sorteo_numero").order("sorteo_numero", desc=True).limit(1).execute()
    
    if res_db.data:
        num_sorteo = res_db.data[0]['sorteo_numero']
        st.markdown(f"<h1 style='text-align: center; color: #00ff88;'>🏆 PROGOL ELITE #{num_sorteo}</h1>", unsafe_allow_html=True)
        
        # 2. Obtener Partidos
        partidos = supabase.table("quinielas_activas").select("*").eq("sorteo_numero", num_sorteo).order("casilla").execute()
        live_data = get_live_data()

        # 3. Dibujar Tarjetas
        for p in partidos.data:
            f_id = str(p['fixture_id'])
            es_vivo = f_id in live_data
            
            val_score = live_data[f_id]['score'] if es_vivo else "0 - 0"
            val_time = f"<span class='live-dot'>● EN VIVO {live_data[f_id]['time']}'</span>" if es_vivo else f"🕒 {p['hora_mx']}"
            
            clase_score = "score-box score-live" if es_vivo else "score-box"
            
            # Logos dinámicos
            url_l = f"https://tse1.mm.bing.net/th?q={p['local_nombre'].replace(' ', '+')}+logo+football&w=100&h=100&c=7"
            url_v = f"https://tse1.mm.bing.net/th?q={p['visita_nombre'].replace(' ', '+')}+logo+football&w=100&h=100&c=7"

            # Construcción del Bloque HTML
            html_card = f"""
            <div class="match-card">
                <div style="font-size:11px; color:#777; margin-bottom:10px; font-weight:bold;">CASILLA {p['casilla']}</div>
                <table style="width:100%; border-collapse:collapse; border:none;">
                    <tr>
                        <td style="width:35%; text-align:center; vertical-align:middle;">
                            <img src="{url_l}" class="logo-img">
                            <div class="team-text">{p['local_nombre']}</div>
                        </td>
                        <td style="width:30%; text-align:center; vertical-align:middle;">
                            <div class="{clase_score}">{val_score}</div>
                            <div style="margin-top:10px; font-size:13px;">{val_time}</div>
                        </td>
                        <td style="width:35%; text-align:center; vertical-align:middle;">
                            <img src="{url_v}" class="logo-img">
                            <div class="team-text">{p['visita_nombre']}</div>
                        </td>
                    </tr>
                </table>
            </div>
            """
            st.markdown(html_card, unsafe_allow_html=True)

    else:
        st.info("Esperando datos de la quiniela...")

except Exception as e:
    st.error(f"Error de visualización: {e}")

# Botón de refresco al final
if st.button("ACTUALIZAR MARCADORES"):
    st.rerun()
