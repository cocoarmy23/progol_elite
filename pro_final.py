import streamlit as st
# Importa esto para el autorefresh
from streamlit_autorefresh import st_autorefresh 

# 1. Agregar auto-refresh cada 60 segundos
count = st_autorefresh(interval=60000, key="fustats_refresh")

# ... (tus credenciales y estilos se mantienen igual) ...

@st.cache_data(ttl=60) # Bajamos a 1 minuto para ver cambios reales
def fetch_match(f_id):
    # Eliminamos la restricción de hora aquí para que al menos 
    # traiga la info inicial o final del partido siempre.
    url = f"https://v3.football.api-sports.io/fixtures?id={f_id}"
    try:
        r = requests.get(url, headers=headers, timeout=10).json()
        if r.get('response') and len(r['response']) > 0:
            return r['response'][0]
        return None
    except Exception as e:
        return None

# --- UI ---
st.title("⚽ PROGOL ÉLITE")

tab1, tab2 = st.tabs(["📊 QUINIELA", "💎 EL FIJO"])

with tab1:
    try:
        # Consulta a Supabase
        partidos = supabase.table("quinielas_activas").select("*").order("casilla").execute().data
        
        for p in partidos:
            info = fetch_match(p['fixture_id'])
            
            if info:
                # Extraer datos reales de la API
                g_l = info['goals']['home'] if info['goals']['home'] is not None else 0
                g_v = info['goals']['away'] if info['goals']['away'] is not None else 0
                status = info['fixture']['status']['short']
                elapsed = info['fixture']['status']['elapsed']
                logo_l = info['teams']['home']['logo']
                logo_v = info['teams']['away']['logo']
                
                # Lógica de estados
                if status in ["1H", "2H", "HT", "P", "BT"]:
                    card_class = "card-live"
                    st_txt = f"<span class='live-dot'>● EN VIVO {elapsed}'</span>"
                elif status in ["FT", "AET", "PEN"]:
                    card_class = "card-finished"
                    st_txt = "Finalizado"
                else:
                    card_class = "card-pending"
                    dt = datetime.strptime(info['fixture']['date'], "%Y-%m-%dT%H:%M:%S+00:00") - timedelta(hours=6)
                    st_txt = dt.strftime("%d/%m %H:%M")
            else:
                # Si falla la API, mostrar datos locales de Supabase (si los tienes)
                card_class = "card-pending"
                st_txt = "Datos no disponibles"
                g_l, g_v, logo_l, logo_v = 0, 0, "", ""

            # ... (Tu bloque de st.markdown se mantiene igual) ...
