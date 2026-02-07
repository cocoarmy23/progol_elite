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

# Forzar configuración de página y tema
st.set_page_config(page_title="Progol Live Elite", layout="wide")

# ==========================================
# 2. ESTILO CSS (FORZANDO MODO OSCURO)
# ==========================================
st.markdown("""
<style>
    /* Forzar fondo oscuro en toda la app */
    .stApp { background-color: #0e1117 !important; color: white !important; }
    
    .match-card {
        background: #1c2531;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
        border: 1px solid #2d3848;
        box-shadow: 0 4px 12px rgba(0,0,0,0.5);
    }
    
    .logo-frame {
        background: #ffffff;
        border-radius: 12px;
        padding: 6px;
        width: 65px;
        height: 65px;
        margin: 0 auto;
        border: 2px solid #3e4b5b;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .logo-img { max-width: 100%; max-height: 100%; object-fit: contain; }
    
    .score-box { 
        font-size: 30px; font-weight: 900; color: #00ff88; 
        background: #000; padding: 8px 18px; border-radius: 12px; 
        border: 1px solid #333; display: inline-block; min-width: 90px;
    }
    
    .score-live { 
        background: #ff4b4b !important; 
        color: white !important; 
        border: 1px solid white;
        box-shadow: 0 0 15px rgba(255, 75, 75, 0.4);
    }
    
    .team-name { font-size: 14px; font-weight: bold; margin-top: 10px; color: #ffffff; text-transform: uppercase; }
    .live-text { color: #ff4b4b; font-size: 12px; font-weight: bold; animation: blinker 1.5s infinite; }
    @keyframes blinker { 50% { opacity: 0.3; } }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. LÓGICA DE ACTUALIZACIÓN AUTOMÁTICA
# ==========================================
def check_and_update_db(p_db, m_api):
    # Si la API dice que terminó (FT, Finished, etc) y en DB aún no dice Finalizado
    status_api = m_api.get('status')
    if status_api in ['FT', 'Finished', 'AP', 'AET']:
        try:
            supabase.table("quinielas_activas").update({
                "marcador_final": m_api.get('score'),
                "estado_partido": "Finalizado"
            }).eq("fixture_id", p_db['fixture_id']).execute()
        except: pass

@st.cache_data(ttl=120)
def fetch_api(necesita_api):
    if not necesita_api: return {}
    try:
        url = f"https://livescore-api.com/api-client/scores/live.json?key={API_KEY}&secret={SECRET}"
        r = requests.get(url, timeout=5).json()
        return {str(m['id']): m for m in r['data']['match']} if r.get('success') else {}
    except: return {}

# ==========================================
# 4. RENDERIZADO
# ==========================================
try:
    res_db = supabase.table("quinielas_activas").select("*").order("sorteo_numero", desc=True).execute()
    
    if res_db.data:
        sorteo_id = res_db.data[0]['sorteo_numero']
        partidos = [p for p in res_db.data if p['sorteo_numero'] == sorteo_id]
        partidos.sort(key=lambda x: x['casilla'])

        st.markdown(f"<h1 style='text-align:center; color:#00ff88; margin-bottom:30px;'>PROGOL ELITE #{sorteo_id}</h1>", unsafe_allow_html=True)
        
        necesita_api = any(p.get('estado_partido') != "Finalizado" for p in partidos)
        live_map = fetch_api(necesita_api)

        for p in partidos:
            f_id = str(p['fixture_id'])
            
            # Decidir qué mostrar
            if f_id in live_map:
                m_api = live_map[f_id]
                marcador = m_api['score']
                tiempo = f"<div class='live-text'>● VIVO {m_api['time']}'</div>"
                clase_score = "score-box score-live"
                # Intentar actualización automática en DB si ya terminó
                check_and_update_db(p, m_api)
            else:
                marcador = p.get('marcador_final') if p.get('marcador_final') else "0 - 0"
                estado_display = p.get('estado_partido', p['hora_mx'])
                tiempo = f"<div style='color:#666; font-size:11px;'>{estado_display}</div>"
                clase_score = "score-box"

            # Logos
            u_l = f"https://tse1.mm.bing.net/th?q={p['local_nombre'].replace(' ', '+')}+logo+football&w=100&h=100&c=7"
            u_v = f"https://tse1.mm.bing.net/th?q={p['visita_nombre'].replace(' ', '+')}+logo+football&w=100&h=100&c=7"

            # Renderizado HTML Robusto
            card_html = (
                f"<div class='match-card'>"
                f"<div style='font-size:10px; color:#555; margin-bottom:12px; font-weight:bold;'>CASILLA {p['casilla']}</div>"
                f"<div style='display:flex; align-items:center; text-align:center; justify-content:space-between;'>"
                f"<div style='flex:1;'><div class='logo-frame'><img src='{u_l}' class='logo-img'></div><div class='team-name'>{p['local_nombre']}</div></div>"
                f"<div style='flex:1;'><div class='{clase_score}'>{marcador}</div><div style='margin-top:8px;'>{tiempo}</div></div>"
                f"<div style='flex:1;'><div class='logo-frame'><img src='{u_v}' class='logo-img'></div><div class='team-name'>{p['visita_nombre']}</div></div>"
                f"</div></div>"
            )
            st.markdown(card_html, unsafe_allow_html=True)

except Exception as e:
    st.error(f"Error crítico: {e}")

st.button("🔄 ACTUALIZAR MARCADORES")
