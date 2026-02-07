import streamlit as st
import requests
from supabase import create_client
from streamlit_autorefresh import st_autorefresh

# ==========================================
# 1. CONFIGURACIÓN Y CONEXIÓN
# ==========================================
# Nota: En producción, usa st.secrets para mayor seguridad
URL_SUPABASE = "https://xavzjoyjausutoscosaw.supabase.co"
KEY_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhhdnpqb3lqYXVzdXRvc2Nvc2F3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjAwNzksImV4cCI6MjA4NTUzNjA3OX0.YjHw-NVeuVpK5l4XkM3hft1vSrERRBXEWZl2wPNjZ0k"
API_KEY = "GQM8r3pQM1JZSH4Z"
SECRET = "9pNSRVoddsshE1elR1tj4TaRVTRNBVNL"

# Inicializar clientes
supabase = create_client(URL_SUPABASE, KEY_SUPABASE)

# Configuración de página
st.set_page_config(page_title="Progol Live Elite", layout="wide")

# Auto-refresco: La página se actualizará sola cada 60 segundos
st_autorefresh(interval=60000, key="datarefresh")

# ==========================================
# 2. ESTILO CSS PERSONALIZADO (PREMIUM)
# ==========================================
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    .match-card {
        background: #1c2531;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 15px;
        border-left: 6px solid #2e7d32;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }
    .live-card { 
        border-left: 6px solid #ff4b4b !important; 
        background: linear-gradient(90deg, #1c2531 0%, #2b1b1b 100%);
    }
    .score-box { 
        font-size: 32px; font-weight: 900; color: #00ff88; 
        background: rgba(0,0,0,0.6); padding: 10px 20px; 
        border-radius: 12px; display: inline-block;
        min-width: 100px; text-align: center;
        border: 1px solid #333;
        font-family: 'Courier New', monospace;
    }
    .score-live { 
        color: #ffffff !important; 
        background: #ff4b4b !important; 
        box-shadow: 0 0 15px rgba(255, 75, 75, 0.4);
    }
    .team-name { font-size: 16px; font-weight: bold; margin-top: 10px; }
    .blink { animation: blinker 1.5s linear infinite; color: #ff4b4b; font-weight: bold; }
    @keyframes blinker { 50% { opacity: 0; } }
    .casilla-label { font-size: 12px; color: #888; letter-spacing: 1px; margin-bottom: 8px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. FUNCIONES DE DATOS CON CACHÉ
# ==========================================
@st.cache_data(ttl=60)
def fetch_live_scores():
    try:
        url = f"https://livescore-api.com/api-client/scores/live.json?key={API_KEY}&secret={SECRET}"
        res = requests.get(url, timeout=10).json()
        if res.get('success'):
            matches = res.get('data', {}).get('match', [])
            return {str(m['id']): m for m in matches}
    except Exception as e:
        st.warning(f"Error al conectar con Livescore API: {e}")
    return {}

# ==========================================
# 4. LÓGICA PRINCIPAL
# ==========================================
try:
    # 1. Obtener último sorteo de Supabase
    res_db = supabase.table("quinielas_activas").select("sorteo_numero").order("sorteo_numero", desc=True).limit(1).execute()
    
    if res_db.data:
        sorteo_actual = res_db.data[0]['sorteo_numero']
        st.markdown(f"<h1 style='text-align: center; color: #00ff88;'>🏆 PROGOL #{sorteo_actual}</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #888;'>Actualización automática cada 60s</p>", unsafe_allow_html=True)
        
        # 2. Obtener partidos del sorteo
        partidos_db = supabase.table("quinielas_activas").select("*").eq("sorteo_numero", sorteo_actual).order("casilla").execute()
        
        # 3. Obtener marcadores en vivo
        live_map = fetch_live_scores()

        # 4. Renderizar Cartelera
        for p in partidos_db.data:
            f_id = str(p['fixture_id'])
            esta_en_vivo = f_id in live_map
            
            # Datos dinámicos
            marcador = live_map[f_id]['score'] if esta_en_vivo else "0 - 0"
            minuto_val = live_map[f_id]['time'] if esta_en_vivo else p['hora_mx']
            
            # Estilos dinámicos
            card_class = "match-card live-card" if esta_en_vivo else "match-card"
            score_class = "score-box score-live" if esta_en_vivo else "score-box"
            tiempo_html = f"<span class='blink'>● EN VIVO {minuto_val}'</span>" if esta_en_vivo else f"<span>🕒 {minuto_val}</span>"

            # Logos (Usando Bing como fallback dinámico)
            logo_l = f"https://tse1.mm.bing.net/th?q={p['local_nombre'].replace(' ', '+')}+football+logo&w=80&h=80&c=7"
            logo_v = f"https://tse1.mm.bing.net/th?q={p['visita_nombre'].replace(' ', '+')}+football+logo&w=80&h=80&c=7"

            # HTML de la tarjeta
            st.markdown(f'''
            <div class="{card_class}">
                <div class="casilla-label">CASILLA {p["casilla"]}</div>
                <div style="display:flex; justify-content:space-between; align-items:center; text-align:center;">
                    <div style="width:35%;">
                        <img src="{logo_l}" style="height:55px; width:55px; object-fit:contain; filter: drop-shadow(0 0 5px rgba(0,0,0,0.5));">
                        <div class="team-name">{p["local_nombre"]}</div>
                    </div>
                    
                    <div style="width:30%;">
                        <div class="{score_class}">{marcador}</div>
                        <div style="margin-top:12px; font-size:14px; font-weight: bold; color: #aaa;">{tiempo_html}</div>
                    </div>
                    
                    <div style="width:35%;">
                        <img src="{logo_v}" style="height:55px; width:55px; object-fit:contain; filter: drop-shadow(0 0 5px rgba(0,0,0,0.5));">
                        <div class="team-name">{p["visita_nombre"]}</div>
                    </div>
                </div>
            </div>
            ''', unsafe_allow_html=True)
    else:
        st.info("No hay sorteos activos en la base de datos.")

except Exception as e:
    st.error(f"Hubo un error al cargar los datos: {e}")

# Pie de página
st.markdown("---")
st.markdown("<p style='text-align: center; color: #444;'>Progol Live Elite v2.0 • Data via Livescore API</p>", unsafe_allow_html=True)
