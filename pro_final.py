import streamlit as st
import requests
from supabase import create_client
from datetime import datetime

# ==========================================
# 1. CONFIGURACIÓN
# ==========================================
URL_SUPABASE = "https://xavzjoyjausutoscosaw.supabase.co"
KEY_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhhdnpqb3lqYXVzdXRvc2Nvc2F3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjAwNzksImV4cCI6MjA4NTUzNjA3OX0.YjHw-NVeuVpK5l4XkM3hft1vSrERRBXEWZl2wPNjZ0k"
API_KEY = "GQM8r3pQM1JZSH4Z"
SECRET = "9pNSRVoddsshE1elR1tj4TaRVTRNBVNL"

supabase = create_client(URL_SUPABASE, KEY_SUPABASE)

# ==========================================
# 2. ESTILO PREMIUM CON ESCUDOS
# ==========================================
st.set_page_config(page_title="Progol Live Premium", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117 !important; color: white !important; }
    .match-card {
        background: linear-gradient(90deg, #1c2531 0%, #253142 100%);
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 15px;
        border-left: 6px solid #00ff88;
        box-shadow: 0 10px 20px rgba(0,0,0,0.5);
    }
    .live-border { border-left-color: #ff4b4b !important; }
    .team-box { width: 35%; display: flex; flex-direction: column; align-items: center; }
    .team-logo { width: 60px; height: 60px; object-fit: contain; margin-bottom: 8px; }
    .team-name { font-size: 16px; font-weight: bold; text-align: center; color: #fff; }
    .score-container { width: 30%; text-align: center; }
    .score-box { 
        font-size: 36px; 
        font-weight: 900; 
        color: #00ff88; 
        background: rgba(0,0,0,0.3); 
        padding: 5px 15px; 
        border-radius: 10px;
        display: inline-block;
        margin-bottom: 5px;
    }
    .live-score { color: #ff4b4b !important; }
    .blink { animation: blinker 1.5s linear infinite; color: #ff4b4b; font-weight: bold; font-size: 14px; }
    @keyframes blinker { 50% { opacity: 0; } }
    .casilla-tag { font-size: 12px; color: #888; text-transform: uppercase; letter-spacing: 1px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. LÓGICA DE DATOS
# ==========================================

try:
    # Obtener último sorteo
    res_db = supabase.table("quinielas_activas").select("sorteo_numero").order("sorteo_numero", desc=True).limit(1).execute()
    
    if res_db.data:
        sorteo_actual = res_db.data[0]['sorteo_numero']
        st.markdown(f"<h1 style='text-align: center;'>🏆 Sorteo #{sorteo_actual}</h1>", unsafe_allow_html=True)
        
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
        # 4. RENDERIZADO DE CARTELERA
        # ==========================================
        for p in partidos_db.data:
            f_id = str(p['fixture_id'])
            esta_en_vivo = f_id in live_map
            
            marcador = live_map[f_id]['score'] if esta_en_vivo else "VS"
            tiempo = f"<span class='blink'>● {live_map[f_id]['time']}'</span>" if esta_en_vivo else f"<span style='color:gray;'>{p['hora_mx']}</span>"
            estilo_vivo = "live-border" if esta_en_vivo else ""
            color_marcador = "live-score" if esta_en_vivo else ""

            # URLs de Escudos (Usando un servicio de imágenes por nombre o ID)
            # Nota: Sustituimos espacios por %20 para la URL
            logo_local = f"https://api.sofascore.app/api/v1/team/{p['fixture_id']}/image" # Intento por ID
            # Si prefieres una opción más segura por nombre:
            logo_local = f"https://tse1.mm.bing.net/th?q={p['local_nombre']}+logo+football&w=100&h=100&c=7&rs=1&qlt=90&o=6&pid=3.1"
            logo_visita = f"https://tse1.mm.bing.net/th?q={p['visita_nombre']}+logo+football&w=100&h=100&c=7&rs=1&qlt=90&o=6&pid=3.1"

            st.markdown(f"""
                <div class="match-card {estilo_vivo}">
                    <div class="casilla-tag">Casilla {p['casilla']}</div>
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 10px;">
                        <div class="team-box">
                            <img src="{logo_local}" class="team-logo">
                            <div class="team-name">{p['local_nombre']}</div>
                        </div>
                        
                        <div class="score-container">
                            <div class="score-box {color_marcador}">{marcador}</div>
                            <div style="margin-top: 5px;">{tiempo}</div>
                        </div>
                        
                        <div class="team-box">
                            <img src="{logo_visita}" class="team-logo">
                            <div class="team-name">{p['visita_nombre']}</div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Cargando cartelera...")

except Exception as e:
    st.error(f"Error: {e}")

st.button("🔄 Actualizar en Vivo")
