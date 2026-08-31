import streamlit as datetime_utils  # Solo referencia interna
import streamlit as st
from supabase import create_client

# Configuración de la página
st.set_page_config(
    page_title="Sistema GEAVIG", page_icon="🛡️", layout="wide"
)

# Inicializar conexión con Supabase desde los Secrets de Streamlit
SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_KEY = st.secrets["supabase"]["key"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Control de Autenticación
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.rol = None
    st.session_state.nombre = None

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

st.title("📋 Registro Diario de Atenciones - GEAVIG")

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
                total_min += 24 * 60  # Ajuste por cambio de día
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
        # Validaciones obligatorias exigidas
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
            # Intentar guardar en Supabase
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
