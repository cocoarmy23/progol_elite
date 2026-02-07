import streamlit as st
import requests
from supabase import create_client
from datetime import datetime, timedelta

# ==========================================
# 1. CREDENCIALES (UNIFICADAS)
# ==========================================
URL_SUPABASE = "https://xavzjoyjausutoscosaw.supabase.co"
KEY_SUPABASE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhhdnpqb3lqYXVzdXRvc2Nvc2F3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk5NjAwNzksImV4cCI6MjA4NTUzNjA3OX0.YjHw-NVeuVpK5l4XkM3hft1vSrERRBXEWZl2wPNjZ0k"
# Usaremos Livescore-API que es la que te funcionó para guardar
API_KEY = "GQM8r3pQM1JZSH4Z"
SECRET = "9pNSRVoddsshE1elR1tj4TaRVTRNBVNL"

supabase = create_client(URL_SUPABASE, KEY_SUPABASE)

# ==========================================
# 2. UI Y ESTILO
# ==========================================
st.set_page_config(page_title="Admin Progol Premium", layout="wide")
st.title("🏆 Panel Administrador: Quinielas Activas")
st.markdown("---")

# --- PASO 1: BÚSQUEDA DE IDS ---
st.header("🔍 1. Localizar IDs (País/Liga)")
col1, col2 = st.columns(2)
with col1:
    p_busqueda = st.text_input("Nombre del País", "Mexico")
    if st.button("Buscar ID de País"):
        r = requests.get(f"https://livescore-api.com/api-client/countries/list.json?key={API_KEY}&secret={SECRET}").json()
        if r.get('success'):
            st.table([p for p in r['data']['countries'] if p_busqueda.lower() in p['name'].lower()])

with col2:
    l_busqueda = st.text_input("Nombre de la Liga", "")
    if st.button("Buscar ID de Liga"):
        r = requests.get(f"https://livescore-api.com/api-client/competitions/list.json?key={API_KEY}&secret={SECRET}").json()
        if r.get('success'):
            st.table([l for l in r['data']['competitions'] if l_busqueda.lower() in l['name'].lower()])

st.divider()

# --- PASO 2: BUSCAR PARTIDOS ---
st.header("⚽ 2. Buscar Partidos en la API")
c1, c2, c3 = st.columns(3)
with c1: id_p = st.text_input("ID País", "46")
with c2: id_l = st.text_input("ID Liga (Opcional)", "")
with c3: fecha = st.date_input("Fecha de Partidos")

url_api = f"https://livescore-api.com/api-client/fixtures/matches.json?key={API_KEY}&secret={SECRET}&date={fecha}&country_id={id_p}"
if id_l: url_api += f"&competition_id={id_l}"

if st.button("🚀 Cargar Partidos Disponibles"):
    res = requests.get(url_api).json()
    if res.get('success'):
        partidos = res.get('data', {}).get('fixtures', [])
        if partidos:
            for f in partidos:
                # Ajuste de hora a México
                try:
                    h_mx = (datetime.strptime(f['time'], "%H:%M:%S") - timedelta(hours=6)).strftime("%H:%M:%S")
                except: h_mx = f['time']
                
                with st.container(border=True):
                    ca1, ca2, ca3, ca4 = st.columns([1, 2, 2, 1])
                    ca1.text_input("ID", f['id'], key=f"id_{f['id']}")
                    ca2.text_input("Local", f['home_name'], key=f"h_{f['id']}")
                    ca3.text_input("Visita", f['away_name'], key=f"a_{f['id']}")
                    ca4.text_input("Hora MX", h_mx, key=f"t_{f['id']}")
        else: st.warning("No hay partidos.")

st.divider()

# --- PASO 3: REGISTRO ---
st.header("💾 3. Guardar en Base de Datos")
with st.form("registro_supabase"):
    cc1, cc2, cc3 = st.columns(3)
    with cc1:
        f_id = st.number_input("Fixture ID", step=1)
        sorteo = st.number_input("Sorteo #", min_value=1, value=1)
    with cc2:
        local = st.text_input("Nombre Local")
        visita = st.text_input("Nombre Visita")
    with cc3:
        casilla = st.number_input("Casilla (1-21)", 1, 21)
        hora_mx = st.text_input("Hora (HH:MM:SS)")

    if st.form_submit_button("✅ Registrar Partido"):
        payload = {
            "sorteo_numero": sorteo, "casilla": casilla, "fixture_id": f_id,
            "local_nombre": local, "visita_nombre": visita, "hora_mx": hora_mx,
            "estado_partido": "Programado"
        }
        try:
            supabase.table("quinielas_activas").insert(payload).execute()
            st.success(f"¡Casilla {casilla} registrada!")
            st.balloons()
        except Exception as e:
            st.error(f"Error: {e}")

# --- MONITOR ---
st.divider()
if st.button("📊 Ver lo que ya está guardado"):
    data = supabase.table("quinielas_activas").select("*").eq("sorteo_numero", sorteo).order("casilla").execute()
    st.write(data.data)
st.set_page_config(page_title="Progol Élite", page_icon="⚽", layout="centered")

st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle, #1a1c23 0%, #050505 100%) !important; }
    .match-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px; padding: 15px; margin-bottom: 12px;
    }
    .team-name { color: white !important; font-weight: 700; font-size: 14px; text-transform: uppercase; width: 40%; }
    .score-box {
        background: #000; color: #00FF41; font-size: 24px; font-weight: bold;
        padding: 5px 12px; border-radius: 8px; border: 1px solid #00FF41;
        min-width: 75px; text-align: center;
        box-shadow: 0px 0px 10px rgba(0, 255, 65, 0.1);
    }
    .status-tag { text-align: center; color: #666; font-size: 10px; margin-top: 8px; font-weight: bold; }
    h1 { color: white !important; font-family: 'Arial Black'; text-align: center; margin-bottom: 30px; letter-spacing: -1px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. FUNCIONES DE DATOS
# ==========================================

@st.cache_data(ttl=600)
def consultar_partido(f_id):
    if not f_id: return None
    url = f"https://v3.football.api-sports.io/fixtures?id={f_id}"
    try:
        r = requests.get(url, headers=headers).json()
        if r.get('response') and len(r['response']) > 0:
            return r['response'][0]
    except:
        return None
    return None

# ==========================================
# 4. INTERFAZ PRINCIPAL
# ==========================================
st.markdown("<h1>⚽ PROGOL ÉLITE</h1>", unsafe_allow_html=True)

try:
    # Traer datos de Supabase
    respuesta = supabase.table("quinielas_activas").select("*").order("casilla").execute()
    partidos_db = respuesta.data
    
    if partidos_db:
        for p in partidos_db:
            info = consultar_partido(p['fixture_id'])
            
            # --- VALIDACIÓN DE GOLES (Cero si es None) ---
            g_l = 0
            g_v = 0
            if info and info.get('goals'):
                g_l = info['goals'].get('home') if info['goals'].get('home') is not None else 0
                g_v = info['goals'].get('away') if info['goals'].get('away') is not None else 0
            
            # Datos visuales
            logo_l = info.get('teams', {}).get('home', {}).get('logo', '') if info else ""
            logo_v = info.get('teams', {}).get('away', {}).get('logo', '') if info else ""
            status_api = info.get('fixture', {}).get('status', {}).get('short', 'NS') if info else "NS"
            
            # Estatus y Fecha Local (México UTC-6)
            st_txt = "PENDIENTE"
            if info:
                dt_utc = datetime.strptime(info['fixture']['date'], "%Y-%m-%dT%H:%M:%S+00:00")
                dt_mx = dt_utc - timedelta(hours=6)
                fecha_formateada = dt_mx.strftime("%d/%m %H:%M")
                
                if status_api in ["1H", "2H", "HT"]:
                    st_txt = "EN VIVO"
                elif status_api == "FT":
                    st_txt = "FINAL"
                else:
                    st_txt = fecha_formateada

            # Dibujar Tarjeta
            st.markdown(f"""
                <div class="match-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div class="team-name" style="text-align: right;">
                            {p['local_nombre']} <img src="{logo_l}" width="24" style="margin-left:8px">
                        </div>
                        <div class="score-box" style="color: {'#00FF41' if st_txt == 'EN VIVO' else 'white'};">
                            {g_l} - {g_v}
                        </div>
                        <div class="team-name" style="text-align: left;">
                            <img src="{logo_v}" width="24" style="margin-right:8px"> {p['visita_nombre']}
                        </div>
                    </div>
                    <div class="status-tag">
                        CASILLA {p['casilla']} | {st_txt} | {p['liga']}
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
    else:
        st.markdown("<p style='text-align:center; color:gray;'>Cargando quiniela...</p>", unsafe_allow_html=True)
            
except Exception as e:
    pass

st.markdown("<p style='text-align: center; color: #444; font-size: 11px; margin-top: 30px;'>Resultados actualizados cada 10 min</p>", unsafe_allow_html=True)

