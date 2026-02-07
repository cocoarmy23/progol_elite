import streamlit as st
import requests
from supabase import create_client
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 1. CONFIGURACIÓN Y REFRESCO (Cada 1 minuto)
st_autorefresh(interval=60000, key="api_update")
st.set_page_config(page_title="Progol Live Elite", layout="wide")

# 2. CREDENCIALES
URL_SUPABASE = "https://xavzjoyjausutoscosaw.supabase.co"
KEY_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhhdnpqb3lqYXVzdXRvc2Nvc2F3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjAwNzksImV4cCI6MjA4NTUzNjA3OX0.YjHw-NVeuVpK5l4XkM3hft1vSrERRBXEWZl2wPNjZ0k"
API_KEY = "GQM8r3pQM1JZSH4Z"
SECRET = "9pNSRVoddsshE1elR1tj4TaRVTRNBVNL"

supabase = create_client(URL_SUPABASE, KEY_SUPABASE)

# 3. ESTILOS CSS
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    .match-card { background: #1c2531; border-radius: 15px; padding: 20px; margin-bottom: 15px; border-left: 5px solid #2e7d32; }
    .score-box { font-size: 32px; font-weight: 900; background: #000; padding: 10px; border-radius: 8px; min-width: 110px; text-align: center; color: #00ff88; border: 1px solid #333; }
    .logo-container { background: white; border-radius: 50%; width: 60px; height: 60px; display: flex; align-items: center; justify-content: center; margin: 0 auto; }
    .team-logo { width: 40px; height: 40px; object-fit: contain; }
    </style>
""", unsafe_allow_html=True)

# 4. FUNCIÓN MAESTRA DE BÚSQUEDA
def obtener_data_api():
    # Usamos la fecha actual para el parámetro 'from' según tus pruebas exitosas
    fecha_consulta = datetime.now().strftime('%Y-%m-%d')
    url = f"https://livescore-api.com/api-client/scores/history.json?key={API_KEY}&secret={SECRET}&from={fecha_consulta}"
    
    try:
        response = requests.get(url, timeout=15).json()
        if response.get('success'):
            # Retornamos la lista de partidos (la 'página 1' del historial reciente)
            return response.get('data', {}).get('match', [])
    except:
        return []
    return []

# 5. LÓGICA PRINCIPAL
try:
    # Traer partidos de tu DB
    partidos_db = supabase.table("quinielas_activas").select("*").order("casilla").execute().data
    
    # Traer todos los partidos de hoy de la API
    partidos_api = obtener_data_api()

    for p in partidos_db:
        id_buscado = str(p['fixture_id']).strip()
        nombre_local_db = p['local_nombre'].upper()
        
        # Buscamos el partido dentro de la respuesta de la API
        match_encontrado = None
        for m in partidos_api:
            id_api = str(m.get('id')).strip()
            nombre_api_local = str(m.get('home_name')).upper()
            
            # CRITERIO DE BÚSQUEDA: Que coincida el ID O que el nombre esté contenido
            if id_api == id_buscado or nombre_local_db in nombre_api_local:
                match_encontrado = m
                break
        
        # Asignar marcador y estado
        if match_encontrado:
            marcador = match_encontrado.get('score', '0 - 0')
            tiempo = str(match_encontrado.get('time', '')).upper()
            status_txt = "✅ FINALIZADO" if tiempo == "FT" else f"🔴 EN VIVO {tiempo}'"
        else:
            marcador = f"{p.get('marcador_local', 0)} - {p.get('marcador_visita', 0)}"
            status_txt = f"🕒 {p['hora_mx']}"

        # RENDERIZADO DE TARJETA
        l_logo = f"https://tse1.mm.bing.net/th?q={p['local_nombre']}+logo+football&w=100&h=100&c=7"
        v_logo = f"https://tse1.mm.bing.net/th?q={p['visita_nombre']}+logo+football&w=100&h=100&c=7"

        st.markdown(f"""
            <div class="match-card">
                <div style="display:flex; justify-content:space-between; align-items:center; text-align:center;">
                    <div style="width:35%;">
                        <div class="logo-container"><img src="{l_logo}" class="team-logo"></div>
                        <div style="margin-top:10px; font-weight:bold;">{p['local_nombre']}</div>
                    </div>
                    <div style="width:30%;">
                        <div class="score-box">{marcador}</div>
                        <div style="margin-top:10px; font-size:12px; font-weight:bold; color:#aaa;">{status_txt}</div>
                    </div>
                    <div style="width:35%;">
                        <div class="logo-container"><img src="{v_logo}" class="team-logo"></div>
                        <div style="margin-top:10px; font-weight:bold;">{p['visita_nombre']}</div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"Error cargando datos: {e}")
