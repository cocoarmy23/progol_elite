import streamlit as st
import requests
from supabase import create_client

# ==========================================
# 1. CONFIGURACIÓN
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
# 2. ESTILO CSS (CON INDICADORES L-E-V)
# ==========================================
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: white; }
    .match-card { background: #1c2531; border-radius: 15px; padding: 15px; margin-bottom: 15px; border: 1px solid #2d3848; position: relative; }
    .logo-frame { background: #ffffff; border-radius: 10px; padding: 5px; width: 60px; height: 60px; margin: 0 auto; border: 2px solid #3e4b5b; }
    .logo-img { width: 100%; height: 100%; object-fit: contain; }
    .score-box { font-size: 28px; font-weight: 900; color: #00ff88; background: #000; padding: 5px 15px; border-radius: 10px; border: 1px solid #333; display: inline-block; min-width: 80px;}
    .score-live { background: #ff4b4b !important; color: white !important; border: 1px solid white; box-shadow: 0 0 10px rgba(255,75,75,0.5); }
    .team-name { font-size: 13px; font-weight: bold; margin-top: 8px; text-transform: uppercase; color: #e1e1e1; }
    .live-text { color: #ff4b4b; font-size: 12px; font-weight: bold; animation: blinker 1.5s infinite; }
    @keyframes blinker { 50% { opacity: 0.3; } }
    .status-bar { font-size: 10px; color: #444; text-align: center; margin-bottom: 10px; }
    /* Etiquetas L E V */
    .badge { padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: bold; margin-top: 5px; display: inline-block; }
    .badge-win { background: #00ff88; color: #000; }
    .badge-draw { background: #555; color: white; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. FUNCIÓN DE DATOS INTELIGENTE
# ==========================================
@st.cache_data(ttl=120)
def fetch_live_data(necesita_actualizar):
    if not necesita_actualizar:
        return {}, "MODO AHORRO: Mostrando resultados de Base de Datos"
    try:
        url = f"https://livescore-api.com/api-client/scores/live.json?key={API_KEY}&secret={SECRET}"
        r = requests.get(url, timeout=5).json()
        if r.get('success'):
            return {str(m['id']): m for m in r['data']['match']}, "API ACTIVA: Actualizando en vivo"
    except: pass
    return {}, "API EN ESPERA"

# ==========================================
# 4. LÓGICA DE NEGOCIO Y RENDER
# ==========================================
try:
    res_db = supabase.table("quinielas_activas").select("*").order("sorteo_numero", desc=True).execute()
    
    if res_db.data:
        sorteo_id = res_db.data[0]['sorteo_numero']
        partidos = [p for p in res_db.data if p['sorteo_numero'] == sorteo_id]
        partidos.sort(key=lambda x: x['casilla'])

        st.markdown(f"<h2 style='text-align:center; color:#00ff88;'>PROGOL #{sorteo_id}</h2>", unsafe_allow_html=True)
        
        # LÓGICA DE AHORRO: ¿Hay partidos que NO estén "Finalizados"?
        # Ajusta "Finalizado" al texto exacto que uses en tu columna
        necesita_api = any(p.get('estado_partido') != "Finalizado" for p in partidos)
        
        live_map, status_msg = fetch_live_data(necesita_api)
        st.markdown(f"<div class='status-bar'>{status_msg}</div>", unsafe_allow_html=True)

        for p in partidos:
            f_id = str(p['fixture_id'])
            esta_en_vivo = f_id in live_map
            
            # 1. Obtener Marcador y Tiempo
            if esta_en_vivo:
                marcador_str = live_map[f_id]['score']
                tiempo_html = f"<div class='live-text'>● EN VIVO {live_map[f_id]['time']}'</div>"
                clase_score = "score-box score-live"
            else:
                marcador_str = p.get('marcador_final') if p.get('marcador_final') else "0 - 0"
                estado_txt = p.get('estado_partido', p['hora_mx'])
                tiempo_html = f"<div style='color:#666; font-size:11px;'>{estado_txt}</div>"
                clase_score = "score-box"

            # 2. Lógica L-E-V (Para resaltar quién gana)
            res_lev = ""
            try:
                goles = marcador_str.replace(" ", "").split("-")
                gl, gv = int(goles[0]), int(goles[1])
                if gl > gv: res_lev = "<div class='badge badge-win'>LOCAL</div>"
                elif gv > gl: res_lev = "<div class='badge badge-win'>VISITA</div>"
                else: res_lev = "<div class='badge badge-draw'>EMPATE</div>"
            except: res_lev = ""

            # 3. Logos
            url_l = f"https://tse1.mm.bing.net/th?q={p['local_nombre'].replace(' ', '+')}+logo&w=80&h=80&c=7"
            url_v = f"https://tse1.mm.bing.net/th?q={p['visita_nombre'].replace(' ', '+')}+logo&w=80&h=80&c=7"

            # 4. HTML Final
            card_html = (
                f"<div class='match-card'>"
                f"<div style='font-size:10px; color:#555; margin-bottom:10px; font-weight:bold;'>CASILLA {p['casilla']}</div>"
                f"<div style='display:flex; align-items:center; text-align:center;'>"
                f"<div style='flex:1;'><div class='logo-frame'><img src='{url_l}' class='logo-img'></div><div class='team-name'>{p['local_nombre']}</div></div>"
                f"<div style='flex:1;'><div class='{clase_score}'>{marcador_str}</div><div style='margin-top:5px;'>{tiempo_html}</div>{res_lev}</div>"
                f"<div style='flex:1;'><div class='logo-frame'><img src='{url_v}' class='logo-img'></div><div class='team-name'>{p['visita_nombre']}</div></div>"
                f"</div></div>"
            )
            st.markdown(card_html, unsafe_allow_html=True)
    else:
        st.info("No hay sorteos activos.")
except Exception as e:
    st.error(f"Error: {e}")

st.button("ACTUALIZAR")
