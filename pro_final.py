import streamlit as st
import requests
from supabase import create_client

# ==========================================
# 1. CONFIGURACIÓN Y CREDENCIALES
# ==========================================
URL_SUPABASE = "https://xavzjoyjausutoscosaw.supabase.co"
KEY_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhhdnpqb3lqYXVzdXRvc2Nvc2F3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjAwNzksImV4cCI6MjA4NTUzNjA3OX0.YjHw-NVeuVpK5l4XkM3hft1vSrERRBXEWZl2wPNjZ0k"
API_KEY = "7ec8e70df61e8ff10111253b825be068" # <-- Pon tu clave de 32 caracteres

supabase = create_client(URL_SUPABASE, KEY_SUPABASE)
headers = {'x-apisports-key': API_KEY.strip()}

st.set_page_config(page_title="Progol Élite", page_icon="⚽", layout="centered")

# ==========================================
# 2. DISEÑO PREMIUM (CSS INYECTADO)
# ==========================================
st.markdown("""
    <style>
    .stApp {
        background: radial-gradient(circle, #1a1c23 0%, #050505 100%) !important;
    }
    
    .fijo-card {
        background: linear-gradient(135deg, #FF4B4B 0%, #8B0000 100%);
        padding: 25px;
        border-radius: 20px;
        text-align: center;
        border: 2px solid #FF7676;
        box-shadow: 0px 0px 25px rgba(255, 75, 75, 0.4);
        margin-bottom: 30px;
    }

    .match-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 15px;
        transition: 0.3s;
    }

    .team-name {
        color: white !important;
        font-weight: 800;
        font-size: 18px;
        text-transform: uppercase;
        width: 40%;
    }

    .score-box {
        background: #000;
        color: #00FF41;
        font-size: 28px;
        font-weight: bold;
        padding: 8px 18px;
        border-radius: 10px;
        border: 2px solid #00FF41;
        box-shadow: 0px 0px 15px rgba(0, 255, 65, 0.4);
    }

    h1, h2, h3 { color: white !important; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. CABECERA Y EL FIJO
# ==========================================
st.markdown("<h1 style='text-align: center;'>PROGOL ÉLITE</h1>", unsafe_allow_html=True)

st.markdown("""
    <div class="fijo-card">
        <div style="font-size: 14px; letter-spacing: 2px; color: #FFD700; font-weight: bold;">📍 FIJO DE LA SEMANA</div>
        <div style="font-size: 32px; font-weight: 900; margin: 10px 0; color: white;">VALENCIA CF</div>
        <div style="font-size: 14px; opacity: 0.9;">Probabilidad de éxito: 82%</div>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# ==========================================
# 4. LÓGICA DE PARTIDOS (CON MARCADORES REALES)
# ==========================================
@st.cache_data(ttl=300) # Guarda los resultados por 5 minutos para ahorrar API
def obtener_marcadores(ids):
    url = f"https://v3.football.api-sports.io/fixtures?ids={ids}"
    try:
        res = requests.get(url, headers=headers).json()
        return {f['fixture']['id']: f for f in res.get('response', [])}
    except:
        return {}

try:
    res_db = supabase.table("quinielas_activas").select("*").order("casilla").execute()
    partidos = res_db.data

    if partidos:
        # Extraemos todos los IDs para hacer una sola consulta a la API
        ids_cadena = ",".join([str(p['fixture_id']) for p in partidos])
        datos_api = obtener_marcadores(ids_cadena)

        for p in partidos:
            f_id = p['fixture_id']
            info = datos_api.get(f_id, {})
            
            # Extraer goles y estado
            gl = info.get('goals', {}).get('home', 0) if info.get('goals', {}).get('home') is not None else 0
            gv = info.get('goals', {}).get('away', 0) if info.get('goals', {}).get('away') is not None else 0
            status = info.get('fixture', {}).get('status', {}).get('short', 'NS')
            tiempo = info.get('fixture', {}).get('status', {}).get('elapsed', '')

            # Color del marcador: Verde si está en vivo, Blanco si no
            color_marcador = "#00FF41" if status in ["1H", "2H", "HT"] else "white"
            status_display = f"EN VIVO {tiempo}'" if status in ["1H", "2H", "HT"] else ("FINALIZADO" if status == "FT" else "PENDIENTE")

            st.markdown(f"""
                <div class="match-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div class="team-name" style="text-align: right;">{p['local_nombre']}</div>
                        <div class="score-box" style="color: {color_marcador} !important;">{gl} - {gv}</div>
                        <div class="team-name" style="text-align: left;">{p['visita_nombre']}</div>
                    </div>
                    <div style="text-align: center; color: #555; font-size: 10px; margin-top: 10px; letter-spacing: 1px;">
                        CASILLA {p['casilla']} | {status_display} | {p['liga']}
                    </div>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No se encontraron partidos guardados.")
except Exception as e:
    st.error(f"Error cargando marcadores: {e}")