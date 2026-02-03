import streamlit as st
import requests
from supabase import create_client
from datetime import datetime, timedelta

# ==========================================
# 1. CREDENCIALES
# ==========================================
URL_SUPABASE = "https://xavzjoyjausutoscosaw.supabase.co"
KEY_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhhdnpqb3lqYXVzdXRvc2Nvc2F3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjAwNzksImV4cCI6MjA4NTUzNjA3OX0.YjHw-NVeuVpK5l4XkM3hft1vSrERRBXEWZl2wPNjZ0k"
# Asegúrate de colocar tu API KEY activa aquí:
API_KEY = "7ec8e70df61e8ff10111253b825be068" 

supabase = create_client(URL_SUPABASE, KEY_SUPABASE)
headers = {'x-apisports-key': API_KEY.strip()}

# ==========================================
# 2. UI Y ESTILO PREMIUM
# ==========================================
st.set_page_config(page_title="Progol Élite", page_icon="⚽", layout="centered")

st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle, #1a1c23 0%, #050505 100%) !important; }
    .match-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px; padding: 15px; margin-bottom: 12px;
    }
    .team-name { color: white !important; font-weight: 700; font-size: 14px; text-transform: uppercase; width: 40%; }
    .score-box {
        background: #000; color: #00FF41; font-size: 24px; font-weight: bold;
        padding: 5px 12px; border-radius: 8px; border: 1px solid #00FF41;
        min-width: 75px; text-align: center;
        box-shadow: 0px 0px 10px rgba(0, 255, 65, 0.1);
    }
    .status-tag { text-align: center; color: #666; font-size: 10px; margin-top: 8px; font-weight: bold; }
    h1 { color: white !important; font-family: 'Arial Black'; text-align: center; margin-bottom: 30px; letter-spacing: -1px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. FUNCIONES DE DATOS
# ==========================================

@st.cache_data(ttl=600)
def consultar_partido(f_id):
    if not f_id: return None
    url = f"https://v3.football.api-sports.io/fixtures?id={f_id}"
    try:
        r = requests.get(url, headers=headers).json()
        if r.get('response') and len(r['response']) > 0:
            return r['response'][0]
    except:
        return None
    return None

# ==========================================
# 4. INTERFAZ PRINCIPAL
# ==========================================
st.markdown("<h1>⚽ PROGOL ÉLITE</h1>", unsafe_allow_html=True)

try:
    # Traer datos de Supabase
    respuesta = supabase.table("quinielas_activas").select("*").order("casilla").execute()
    partidos_db = respuesta.data
    
    if partidos_db:
        for p in partidos_db:
            info = consultar_partido(p['fixture_id'])
            
            # --- VALIDACIÓN DE GOLES (Cero si es None) ---
            g_l = 0
            g_v = 0
            if info and info.get('goals'):
                g_l = info['goals'].get('home') if info['goals'].get('home') is not None else 0
                g_v = info['goals'].get('away') if info['goals'].get('away') is not None else 0
            
            # Datos visuales
            logo_l = info.get('teams', {}).get('home', {}).get('logo', '') if info else ""
            logo_v = info.get('teams', {}).get('away', {}).get('logo', '') if info else ""
            status_api = info.get('fixture', {}).get('status', {}).get('short', 'NS') if info else "NS"
            
            # Estatus y Fecha Local (México UTC-6)
            st_txt = "PENDIENTE"
            if info:
                dt_utc = datetime.strptime(info['fixture']['date'], "%Y-%m-%dT%H:%M:%S+00:00")
                dt_mx = dt_utc - timedelta(hours=6)
                fecha_formateada = dt_mx.strftime("%d/%m %H:%M")
                
                if status_api in ["1H", "2H", "HT"]:
                    st_txt = "EN VIVO"
                elif status_api == "FT":
                    st_txt = "FINAL"
                else:
                    st_txt = fecha_formateada

            # Dibujar Tarjeta
            st.markdown(f"""
                <div class="match-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div class="team-name" style="text-align: right;">
                            {p['local_nombre']} <img src="{logo_l}" width="24" style="margin-left:8px">
                        </div>
                        <div class="score-box" style="color: {'#00FF41' if st_txt == 'EN VIVO' else 'white'};">
                            {g_l} - {g_v}
                        </div>
                        <div class="team-name" style="text-align: left;">
                            <img src="{logo_v}" width="24" style="margin-right:8px"> {p['visita_nombre']}
                        </div>
                    </div>
                    <div class="status-tag">
                        CASILLA {p['casilla']} | {st_txt} | {p['liga']}
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
    else:
        st.markdown("<p style='text-align:center; color:gray;'>Cargando quiniela...</p>", unsafe_allow_html=True)
            
except Exception as e:
    pass

st.markdown("<p style='text-align: center; color: #444; font-size: 11px; margin-top: 30px;'>Resultados actualizados cada 10 min</p>", unsafe_allow_html=True)
