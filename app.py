import streamlit as st
from supabase import create_client

# Configuración de la página
st.set_page_config(
    page_title="Sistema GEAVIG", page_icon="🛡️", layout="wide"
)

# Estilos CSS institucionales (Tonos Morados)
st.markdown(
    """
    <style>
    .main {
        background-color: #f8f9fa;
    }
    h1, h2, h3 {
        color: #4A148C !important;
    }
    .stButton>button {
        background-color: #6A1B9A;
        color: white;
        border-radius: 8px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #4A148C;
        color: white;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Inicializar conexión con Supabase
SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_KEY = st.secrets["supabase"]["key"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Control de Autenticación
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.rol = None
    st.session_state.nombre = None

# Encabezado institucional con Logos fijos (Visible también en el login)
col1, col2, col3 = st.columns([1, 3, 1])

with col1:
    st.image("logo_secretaria.png", width=120)

with col2:
    st.markdown(
        "<h2"
        " style='text-align:center; color:#4A148C;"
        " margin-bottom:0;'>GEAVIG</h2>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p"
        " style='text-align:center; color:#6A1B9A; font-weight:bold;"
        " font-size:13px;'>Secretaría Municipal de Seguridad Ciudadana y"
        " Tránsito</p>",
        unsafe_allow_html=True,
    )

with col3:
    st.image("logo_geavig.png", width=120)

st.markdown("---")

if not st.session_state.authenticated:
    st.title("🔐 Acceso al Sistema GEAVIG")
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

    if st.button("Iniciar Sesión"):
        usuarios = st.secrets.get("usuarios", {})
        if username in usuarios and usuarios[username]["password"] == password:
            st.session_state.authenticated = True
            st.session_state.user = username
            st.session_state.nombre = usuarios[username]["nombre"]
            st.session_state.rol = usuarios[username]["rol"]
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos")
    st.stop()

# Barra lateral con información del usuario
st.sidebar.title("Panel GEAVIG")
st.sidebar.write(f"**Usuario:** {st.session_state.nombre}")
st.sidebar.write(f"**Rol:** {st.session_state.rol.capitalize()}")

if st.sidebar.button("Cerrar Sesión"):
    st.session_state.authenticated = False
    st.rerun()

# Formulario principal de captura
with st.form("form_geavig"):
    st.subheader("1. Datos Generales y Control de Tiempos")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        capturista = st.text_input(
            "Nombre del Capturista", value=st.session_state.nombre, disabled=True
        )
        fecha_captura = st.date_input("Fecha de Captura")
        hora_reporte = st.text_input("Hora del Reporte (HH:MM)", value="13:00")
    with col2:
        turno = st.selectbox("Turno", ["A", "B", "C", "D"])
        fecha_reporte = st.date_input("Fecha del Reporte")
        hora_llegada = st.text_input("Hora de Llegada (HH:MM)", value="13:20")
    with col3:
        medio_reporte = st.selectbox(
            "Medio de Reporte", ["AUXILIO DIRECTO", "911", "OFICIO", "OTRO"]
        )
        quien_reporta = st.selectbox(
            "Quién Reporta", ["PARTICULAR", "FAMILIAR", "AUTORIDAD"]
        )
        hora_cierre = st.text_input("Hora de Cierre (HH:MM)", value="18:40")
    with col4:
        folio = st.text_input("Folio / Reporte 911")
        tipo_particular = st.selectbox(
            "Tipo de Particular", ["VICTIMA", "TESTIGO", "TERCERO"]
        )

        # Cálculo automático de tiempo de atención
        tiempo_atencion_str = "0 MIN"
        try:
            h_rep, m_rep = map(int, hora_reporte.split(":"))
            h_cie, m_cie = map(int, hora_cierre.split(":"))
            total_min = (h_cie * 60 + m_cie) - (h_rep * 60 + m_rep)
            if total_min < 0:
                total_min += 24 * 60
            tiempo_atencion_str = f"{total_min} MIN"
        except:
            tiempo_atencion_str = "Error formato"

        tiempo_atencion = st.text_input(
            "Tiempo de Atención (Automático)",
            value=tiempo_atencion_str,
            disabled=True,
        )

    col5, col6 = st.columns(2)
    with col5:
        al_mando = st.text_input("Al Mando")
    with col6:
        unidad = st.text_input("Unidad / Patrulla")

    st.subheader("2. Ubicación de los Hechos")
    u1, u2, u3, u4 = st.columns(4)
    with u1:
        smz = st.text_input("SMZ / Supermanzana / Región *")
    with u2:
        sector = st.text_input("Sector Asignado (Obligatorio) *")
    with u3:
        no_exterior = st.text_input("No. Exterior")
    with u4:
        longitud = st.text_input("Longitud *")

    u5, u6, u7 = st.columns(3)
    with u5:
        manzana = st.text_input("Manzana")
    with u6:
        calle = st.text_input("Calle")
    with u7:
        latitud = st.text_input("Latitud *")

    u8, u9 = st.columns(2)
    with u8:
        lote = st.text_input("Lote")
    with u9:
        colonia = st.text_input("Colonia / Fraccionamiento")

    submitted = st.form_submit_button("Guardar Registro")

    if submitted:
        # Validaciones estrictas obligatorias
        errores = []
        if not smz.strip():
            errores.append("La Supermanzana (SMZ) es obligatoria.")
        if not sector.strip():
            errores.append("El Sector Asignado es obligatorio.")
        if not latitud.strip() or not longitud.strip():
            errores.append(
                "La Latitud y la Longitud son obligatorias para continuar."
            )

        if errores:
            for err in errores:
                st.error(err)
        else:
            try:
                data = {
                    "capturista": capturista,
                    "turno": turno,
                    "medio_reporte": medio_reporte,
                    "folio": folio,
                    "fecha_captura": str(fecha_captura),
                    "fecha_reporte": str(fecha_reporte),
                    "quien_reporta": quien_reporta,
                    "tipo_particular": tipo_particular,
                    "hora_reporte": hora_reporte,
                    "hora_llegada": hora_llegada,
                    "hora_cierre": hora_cierre,
                    "al_mando": al_mando,
                    "unidad": unidad,
                    "smz": smz,
                    "sector": sector,
                    "latitud": latitud,
                    "longitud": longitud,
                }
                supabase.table("registros_geavig").insert(data).execute()
                st.success(
                    "¡Registro guardado correctamente en la base de datos!"
                )
            except Exception as e:
                st.error(f"Error al guardar en Supabase: {e}")
