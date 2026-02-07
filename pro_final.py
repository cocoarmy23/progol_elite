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
# 2. LÓGICA DE AUTO-ACTUALIZACIÓN (EL "ROBOT")
# ==========================================
def auto_update_db(p_db, m_api):
    """
    Si la API dice que el partido terminó, actualizamos Supabase 
    para que la próxima vez no gaste créditos de API.
    """
    try:
        # La API de Livescore suele usar 'FT', 'Finished' o 'AP' para partidos terminados
        status_api = m_api.get('status') 
        if status_api in ['FT', 'Finished', 'AP']:
            marcador_final = m_api.get('score')
            
            # Actualizamos la fila en Supabase
            supabase.table("quinielas_activas").update({
                "marcador_final": marcador_final,
                "estado_partido": "Finalizado"
            }).eq("fixture_id", p_db['fixture_id']).execute()
            return True
    except:
        pass
    return False

# ==========================================
# 3. FUNCIÓN DE DATOS
# ==========================================
@st.cache_data(ttl=120)
def fetch_live_data(necesita_api):
    if not necesita_api:
        return {}, "MODO AHORRO: Base de Datos al día"
    try:
        url = f"https://livescore-api.com/api-client/scores/live.json?key={API_KEY}&secret={SECRET}"
        r = requests.get(url, timeout=5).json()
        if r.get('success'):
            return {str(m['id']): m for m in r['data']['match']}, "API SINCRONIZADA"
    except: pass
    return {}, "API EN ESPERA"

# ==========================================
# 4. RENDERIZADO Y LÓGICA
# ==========================================
try:
    res_db = supabase.table("quinielas_activas").select("*").order("sorteo_numero", desc=True).execute()
    
    if res_db.data:
        sorteo_id = res_db.data[0]['sorteo_numero']
        partidos = [p for p in res_db.data if p['sorteo_numero'] == sorteo_id]
        partidos.sort(key=lambda x: x['casilla'])

        st.markdown(f"<h2 style='text-align:center; color:#00ff88;'>PROGOL #{sorteo_id}</h2>", unsafe_allow_html=True)
        
        # ¿Hay partidos pendientes de finalizar?
        necesita_api = any(p.get('estado_partido') != "Finalizado" for p in partidos)
        live_map, status_msg = fetch_live_data(necesita_api)
        
        st.markdown(f"<div style='font-size:10px; color:#444; text-align:center;'>{status_msg}</div>", unsafe_allow_html=True)

        for p in partidos:
            f_id = str(p['fixture_id'])
            
            # Si el partido está en la respuesta de la API
            if f_id in live_map:
                m_api = live_map[f_id]
                marcador = m_api['score']
                tiempo = f"<div style='color:#ff4b4b; font-weight:bold;'>● {m_api['time']}'</div>"
                clase_score = "score-box score-live"
                
                # --- AQUÍ OCURRE LA MAGIA ---
                # Si el partido acaba de terminar en la API, actualizamos la DB automáticamente
                if m_api.get('status') in ['FT', 'Finished', 'AP']:
                    auto_update_db(p, m_api)
            else:
                # Si no está en la API, usamos lo que ya tenemos en DB
                marcador = p.get('marcador_final', "0 - 0")
                tiempo = f"<div style='color:#666;'>{p.get('estado_partido', p['hora_mx'])}</div>"
                clase_score = "score-box"

            # (El resto del código de los logos y HTML L-E-V se mantiene igual)
            url_l = f"https://tse1.mm.bing.net/th?q={p['local_nombre'].replace(' ', '+')}+logo&w=80&h=80&c=7"
            url_v = f"https://tse1.mm.bing.net/th?q={p['visita_nombre'].replace(' ', '+')}+logo&w=80&h=80&c=7"

            st.markdown(f"""
            <div style="background:#1c2531; border-radius:15px; padding:15px; margin-bottom:15px; border:1px solid #2d3848;">
                <div style="display:flex; align-items:center; text-align:center;">
                    <div style="flex:1;"><img src="{url_l}" width="50"><div style="font-size:12px; font-weight:bold;">{p['local_nombre']}</div></div>
                    <div style="flex:1;"><div class="{clase_score}" style="font-size:25px; font-weight:900; background:#000; padding:5px 15px; border-radius:10px; color:#00ff88;">{marcador}</div><div style="margin-top:5px; font-size:11px;">{tiempo}</div></div>
                    <div style="flex:1;"><img src="{url_v}" width="50"><div style="font-size:12px; font-weight:bold;">{p['visita_nombre']}</div></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"Error: {e}")
