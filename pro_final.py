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
# 2. ESTILO PREMIUM OSCURO (FORZADO)
# ==========================================
st.set_page_config(page_title="Progol Live", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117 !important; color: white !important; }
    .match-card {
        background: #1c2531;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 12px;
        border-left: 5px solid #00ff88;
    }
    .live-border { border-left-color: #ff4b4b !important; }
    .score { font-size: 26px; font-weight: bold; color: #ffffff; margin: 0; }
    .team { font-size: 16px; color: #ffffff; font-weight: 600; width: 40%; }
    .blink { animation: blinker 1.5s linear infinite; color: #ff4b4b; font-weight: bold; font-size: 14px; }
    @keyframes blinker { 50% { opacity: 0; } }
    .info-footer { font-size: 11px; color: #888; margin-top: 8px; border-top: 1px solid #2d3748; padding-top: 5px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. LÓGICA DE FILTRADO (SIN ERROR DE COLUMNA)
# ==========================================

try:
    # Cambiamos el orden a 'sorteo_numero' para evitar el error de 'created_at'
    res_db = supabase.table("quinielas_activas").select("sorteo_numero").order("sorteo_numero", desc=True).limit(1).execute()
    
    if res_db.data:
        sorteo_actual = res_db.data[0]['sorteo_numero']
        st.markdown(f"<h1 style='text-align: center; color: white;'>🏆 Sorteo #{sorteo_actual}</h1>", unsafe_allow_html=True)
        
        # Traer partidos
        partidos_db = supabase.table("quinielas_activas").select("*").eq("sorteo_numero", sorteo_actual).order("casilla").execute()
        
        # Consultar API Live
        live_map = {}
        try:
            live_res = requests.get(f"https://livescore-api.com/api-client/scores/live.json?key={API_KEY}&secret={SECRET}", timeout=5).json()
            if live_res.get('success'):
                matches = live_res.get('data', {}).get('match', [])
                live_map = {str(m['id']): m for m in matches}
        except: pass

        # ==========================================
        # 4. RENDERIZADO
        # ==========================================
        for p in partidos_db.data:
            f_id = str(p['fixture_id'])
            esta_en_vivo = f_id in live_map
            
            score_display = live_map[f_id]['score'] if esta_en_vivo else "vs"
            time_info = f"<span class='blink'>● EN VIVO {live_map[f_id]['time']}'</span>" if esta_en_vivo else f"<span style='color:#888;'>{p['hora_mx']}</span>"
            card_style = "match-card live-border" if esta_en_vivo else "match-card"

            st.markdown(f"""
                <div class="{card_style}">
                    <div style="display: flex; justify-content: space-between; align-items: center; text-align: center;">
                        <div class="team" style="text-align: right;">{p['local_nombre']}</div>
                        <div style="width: 20%;">
                            <div class="score">{score_display}</div>
                            {time_info}
                        </div>
                        <div class="team" style="text-align: left;">{p['visita_nombre']}</div>
                    </div>
                    <div class="info-footer">Casilla {p['casilla']}</div>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No hay sorteos registrados.")

except Exception as e:
    st.error("Error de conexión con la base de datos.")
    # Opción de rescate si el orden falla:
    if st.button("Intentar cargar sin orden"):
        st.rerun()

st.button("🔄 Actualizar Resultados")
