import streamlit as st
import requests
from supabase import create_client
from streamlit_autorefresh import st_autorefresh

# 1. CONFIGURACIÓN
st_autorefresh(interval=60000, key="progol_fix")
st.set_page_config(page_title="Progol Live Elite", layout="wide")

# 2. CREDENCIALES
URL_SUPABASE = "https://xavzjoyjausutoscosaw.supabase.co"
KEY_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhhdnpqb3lqYXVzdXRvc2Nvc2F3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjAwNzksImV4cCI6MjA4NTUzNjA3OX0.YjHw-NVeuVpK5l4XkM3hft1vSrERRBXEWZl2wPNjZ0k"
API_KEY = "GQM8r3pQM1JZSH4Z"
SECRET = "9pNSRVoddsshE1elR1tj4TaRVTRNBVNL"

supabase = create_client(URL_SUPABASE, KEY_SUPABASE)

# 3. FUNCIÓN DE BARRIDO SIN FILTRO DE FECHA (Para encontrar partidos pasados)
def obtener_datos_api():
    bolsa = []
    # Quitamos el filtro de fecha específico para que el History traiga lo más reciente disponible
    urls = [
        f"https://livescore-api.com/api-client/scores/live.json?key={API_KEY}&secret={SECRET}",
        f"https://livescore-api.com/api-client/scores/history.json?key={API_KEY}&secret={SECRET}" # Sin fecha fija
    ]
    for url in urls:
        try:
            r = requests.get(url, timeout=10).json()
            if r.get('success'):
                matches = r.get('data', {}).get('match', [])
                if isinstance(matches, list): bolsa.extend(matches)
        except: continue
    return bolsa

# 4. LÓGICA PRINCIPAL
try:
    res = supabase.table("quinielas_activas").select("sorteo_numero").order("sorteo_numero", desc=True).limit(1).execute()
    
    if res.data:
        num_sorteo = res.data[0]['sorteo_numero']
        st.markdown(f'<h2 style="text-align:center;">🏆 SORTEO {num_sorteo}</h2>', unsafe_allow_html=True)

        partidos_db = supabase.table("quinielas_activas").select("*").eq("sorteo_numero", num_sorteo).order("casilla").execute().data
        api_data = obtener_datos_api()

        for p in partidos_db:
            # Buscamos por fixture_id que es el que coincide en tu JSON
            fid_buscado = str(p['fixture_id']).strip()
            match_found = next((m for m in api_data if str(m.get('fixture_id')) == fid_buscado or str(m.get('id')) == fid_buscado), None)
            
            marcador = "0 - 0"
            estado = f"🕒 {p['hora_mx']}"
            color_marcador = "#aaa"

            if match_found:
                # Extraemos el marcador según la estructura del JSON que diste
                scores = match_found.get('scores', {})
                if isinstance(scores, dict):
                    marcador = scores.get('score', "0 - 0")
                else:
                    marcador = match_found.get('score', "0 - 0")
                
                # Identificación de finalizado o vivo
                t = str(match_found.get('time')).upper()
                s = str(match_found.get('status')).upper()

                if t == "FT" or s == "FINISHED":
                    estado = "✅ FINALIZADO"
                    color_marcador = "#00ff88"
                elif s == "HT":
                    estado = "🔴 MEDIO TIEMPO"
                    color_marcador = "#ff4b4b"
                else:
                    estado = f"🔴 {t}'"
                    color_marcador = "#ff4b4b"

            # Renderizado simple para depurar
            st.markdown(f"""
                <div style="background:#1c2531; padding:15px; border-radius:10px; margin-bottom:10px; border-left: 5px solid {color_marcador};">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div style="width:35%; text-align:right;"><b>{p['local_nombre']}</b></div>
                        <div style="width:30%; text-align:center;">
                            <div style="font-size:24px; font-weight:bold; color:{color_marcador};">{marcador}</div>
                            <div style="font-size:12px;">{estado}</div>
                        </div>
                        <div style="width:35%; text-align:left;"><b>{p['visita_nombre']}</b></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("No hay datos.")
except Exception as e:
    st.error(f"Error: {e}")
