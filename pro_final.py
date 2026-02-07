import streamlit as st
import requests
from supabase import create_client
from datetime import datetime

# ==========================================
# 1. CREDENCIALES
# ==========================================
URL_SUPABASE = "https://xavzjoyjausutoscosaw.supabase.co"
KEY_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhhdnpqb3lqYXVzdXRvc2Nvc2F3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjAwNzksImV4cCI6MjA4NTUzNjA3OX0.YjHw-NVeuVpK5l4XkM3hft1vSrERRBXEWZl2wPNjZ0k"
API_KEY = "GQM8r3pQM1JZSH4Z"
SECRET = "9pNSRVoddsshE1elR1tj4TaRVTRNBVNL"

supabase = create_client(URL_SUPABASE, KEY_SUPABASE)

# ==========================================
# 2. ESTILO COMPACTO Y LIMPIO
# ==========================================
st.set_page_config(page_title="Progol Live", layout="wide")

st.markdown("""
    <style>
    .match-card {
        background: #1c2531;
        border-radius: 10px;
        padding: 12px;
        margin-bottom: 10px;
        border-left: 4px solid #00ff88;
        color: white;
    }
    .live-border { border-left-color: #ff4b4b !important; }
    .score { font-size: 22px; font-weight: bold; color: #fff; }
    .team { font-size: 16px; color: #e0e0e0; font-weight: 500; }
    .minute { background: #ff4b4b; color: white; padding: 1px 6px; border-radius: 4px; font-size: 12px; }
    .blink { animation: blinker 1.5s linear infinite; color: #ff4b4b; font-weight: bold; }
    @keyframes blinker { 50% { opacity: 0; } }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. LÓGICA DE FILTRADO (SOLO EL ÚLTIMO SORTEO)
# ==========================================

# Buscamos el sorteo más alto registrado
res_max = supabase.table("quinielas_activas").select("sorteo_numero").order("sorteo_numero", desc=True).limit(1).execute()

if res_max.data:
    sorteo_actual = res_max.data[0]['sorteo_numero']
    st.title(f"🏆 Resultados Sorteo #{sorteo_actual}")
    
    # Traer solo partidos de ESE sorteo
    partidos_db = supabase.table("quinielas_activas").select("*").eq("sorteo_numero", sorteo_actual).order("casilla").execute()
    
    # Consultar API Live
    live_map = {}
    try:
        live_res = requests.get(f"https://livescore-api.com/api-client/scores/live.json?key={API_KEY}&secret={SECRET}").json()
        if live_res.get('success'):
            matches = live_res.get('data', {}).get('match', [])
            live_map = {str(m['id']): m for m in matches}
    except: pass

    # ==========================================
    # 4. RENDERIZADO SIN ERRORES DE ETIQUETAS
    # ==========================================
    for p in partidos_db.data:
        f_id = str(p['fixture_id'])
        esta_en_vivo = f_id in live_map
        
        # Valores dinámicos
        score = live_map[f_id]['score'] if esta_en_vivo else "vs"
        time_display = f"<span class='blink'>● {live_map[f_id]['time']}'</span>" if esta_en_vivo else f"<span style='color:gray;'>{p['hora_mx']}</span>"
        card_class = "match-card live-border" if esta_en_vivo else "match-card"

        # Usamos f-strings limpios para evitar el error de "texto en pantalla"
        st.markdown(f"""
            <div class="{card_class}">
                <div style="display: flex; justify-content: space-between; align-items: center; text-align: center;">
                    <div style="width: 35%; text-align: right;" class="team">{p['local_nombre']}</div>
                    <div style="width: 30%;">
                        <div class="score">{score}</div>
                        {time_display}
                    </div>
                    <div style="width: 35%; text-align: left;" class="team">{p['visita_nombre']}</div>
                </div>
                <div style="font-size: 10px; color: #888; margin-top: 5px;">Casilla {p['casilla']}</div>
            </div>
        """, unsafe_allow_html=True)

else:
    st.error("No se encontraron quinielas en la base de datos.")

st.button("🔄 Actualizar")
