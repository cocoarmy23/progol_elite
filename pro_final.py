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

supabase = create_client(URL_SUPABASE, KEY_SUPABASE)

st.set_page_config(page_title="Progol Live Elite", layout="wide")

# ==========================================
# 2. ESTILO CSS "ULTRA PREMIUM"
# ==========================================
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; color: white; }
    
    /* Contenedor de la Tarjeta */
    .match-card {
        background: linear-gradient(145deg, #161b22, #1f2630);
        border-radius: 20px;
        padding: 25px;
        margin-bottom: 20px;
        border: 1px solid rgba(255,255,255,0.05);
        box-shadow: 10px 10px 20px #080a0d, -5px -5px 15px #1e252e;
    }
    
    /* Efecto para los Logos */
    .logo-container {
        filter: drop-shadow(0px 4px 8px rgba(0,0,0,0.8));
        transition: transform 0.3s ease;
    }
    .logo-container:hover {
        transform: scale(1.1);
    }
    
    /* Marcador Estilizado */
    .score-box { 
        font-size: 36px; font-weight: 900; 
        color: #00ff88; 
        background: #0b0e14; 
        padding: 12px 25px; 
        border-radius: 15px; 
        display: inline-block;
        border: 2px solid #1f2630;
        box-shadow: inset 2px 2px 5px #000;
        font-family: 'Monaco', monospace;
    }
    
    .score-live { 
        color: #ffffff !important; 
        background: #e91e63 !important; 
        border-color: #ff6090;
        box-shadow: 0 0 20px rgba(233, 30, 99, 0.4);
    }

    .team-name { 
        font-size: 17px; 
        font-weight: 700; 
        margin-top: 15px; 
        color: #e1e1e1;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .blink { animation: blinker 1.2s infinite; color: #ff4b4b; }
    @keyframes blinker { 50% { opacity: 0.3; } }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. LÓGICA DE DATOS
# ==========================================
@st.cache_data(ttl=60)
def get_live_data():
    try:
        url = f"https://livescore-api.com/api-client/scores/live.json?key={API_KEY}&secret={SECRET}"
        r = requests.get(url, timeout=10).json()
        if r.get('success'):
            return {str(m['id']): m for m in r['data']['match']}
    except: return {}
    return {}

try:
    res_db = supabase.table("quinielas_activas").select("sorteo_numero").order("sorteo_numero", desc=True).limit(1).execute()
    
    if res_db.data:
        sorteo_actual = res_db.data[0]['sorteo_numero']
        st.markdown(f"<h1 style='text-align: center; letter-spacing: 3px; color: #00ff88;'>PROGOL ELITE #{sorteo_actual}</h1>", unsafe_allow_html=True)
        
        partidos = supabase.table("quinielas_activas").select("*").eq("sorteo_numero", sorteo_actual).order("casilla").execute()
        live_map = get_live_data()

        for p in partidos.data:
            f_id = str(p['fixture_id'])
            en_vivo = f_id in live_map
            marcador = live_map[f_id]['score'] if en_vivo else "0 - 0"
            tiempo = f"<span class='blink'>● VIVO {live_map[f_id]['time']}'</span>" if en_vivo else f"<span style='color:#666;'>🕒 {p['hora_mx']}</span>"
            
            card_style = "match-card live-card" if en_vivo else "match-card"
            score_style = "score-box score-live" if en_vivo else "score-box"

            # Búsqueda mejorada de logos (Busca archivos transparentes y de fútbol)
            query_local = f"{p['local_nombre'].replace(' ', '+')}+football+logo+transparent+png"
            query_visita = f"{p['visita_nombre'].replace(' ', '+')}+football+logo+transparent+png"
            
            logo_l = f"https://tse1.mm.bing.net/th?q={query_local}&w=120&h=120&c=7&rs=1&p=0"
            logo_v = f"https://tse1.mm.bing.net/th?q={query_visita}&w=120&h=120&c=7&rs=1&p=0"

            st.markdown(f'''
            <div class="{card_style}">
                <div style="font-size:12px; color:#555; font-weight:900; margin-bottom:10px;">CASILLA {p['casilla']}</div>
                <div style="display:flex; justify-content:space-between; align-items:center; text-align:center;">
                    
                    <div style="width:35%;">
                        <img src="{logo_l}" class="logo-container" width="70" height="70" style="object-fit:contain;">
                        <div class="team-name">{p['local_nombre']}</div>
                    </div>

                    <div style="width:30%;">
                        <div class="{score_style}">{marcador}</div>
                        <div style="margin-top:15px; font-weight:bold;">{tiempo}</div>
                    </div>

                    <div style="width:35%;">
                        <img src="{logo_v}" class="logo-container" width="70" height="70" style="object-fit:contain;">
                        <div class="team-name">{p['visita_nombre']}</div>
                    </div>

                </div>
            </div>
            ''', unsafe_allow_html=True)
    else:
        st.warning("Sin datos.")
except Exception as e:
    st.error(f"Error: {e}")
