import base64
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


# Función auxiliar para convertir imágenes a base64 de manera segura
def get_image_base64(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except Exception:
        return None


# Control de Autenticación - Estado inicial
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
    st.session_state["usuario_actual"] = ""
    st.session_state["nombre_usuario"] = ""
    st.session_state["rol_usuario"] = ""
    st.session_state["registro_exitoso"] = False
    st.session_state["registros_capturados"] = []

USUARIOS = st.secrets.get("usuarios", {})


def mostrar_login():
    st.markdown(
        """
        <style>
            .stApp {
                background: linear-gradient(135deg, #2A0835 0%, #4A1259 50%, #170320 100%) !important;
                background-attachment: fixed !important;
            }
            header, footer, #MainMenu { visibility: hidden; }

            .inst-header { text-align: center; margin-top: 5px; margin-bottom: 25px; }
            .inst-title {
                color: #FFFFFF; font-family: 'Montserrat', Arial, sans-serif;
                font-weight: 700; font-size: 26px; line-height: 1.15;
                text-transform: uppercase; margin-bottom: 12px;
            }
            .inst-subtitle {
                color: rgba(255, 255, 255, 0.95); font-family: 'Montserrat', Arial, sans-serif;
                font-weight: 700; font-size: 24px; text-transform: uppercase; margin-bottom: 10px;
            }
            div[data-testid="stForm"] {
                background: rgba(255, 255, 255, 0.08) !important;
                backdrop-filter: blur(14px) !important;
                border: 1px solid rgba(255, 255, 255, 0.18) !important;
                border-radius: 16px !important; padding: 30px 28px !important;
            }
            div[data-testid="stForm"] label { color: #FFFFFF !important; font-weight: 600 !important; }
            div[data-baseweb="input"] { background-color: rgba(255, 255, 255, 0.95) !important; border-radius: 8px !important; }
            div[data-baseweb="input"] input { color: #111827 !important; }
            div.stButton > button {
                background: linear-gradient(90deg, #801538 0%, #A31E48 100%) !important;
                color: #FFFFFF !important; font-weight: 700 !important; height: 48px !important;
                border-radius: 10px !important; text-transform: uppercase !important;
            }
            .login-card-title { color: #FFFFFF; font-weight: 700; font-size: 20px; text-align: center; margin-bottom: 22px; }
            .logo-container { display: flex; justify-content: center; align-items: center; gap: 24px; margin-bottom: 12px; }
            .logo-container img { width: 105px; height: auto; }
        </style>
    """,
        unsafe_allow_html=True,
    )

    col_left, col_center, col_right = st.columns([1, 1.8, 1])

    with col_center:
        b64_sec = get_image_base64("logo_secretaria.png")
        b64_gea = get_image_base64("logo_geavig.png")

        img_sec_html = (
            f'<img src="data:image/png;base64,{b64_sec}" alt="Logo">'
            if b64_sec
            else '<span style="font-size:45px;">🛡️</span>'
        )
        img_gea_html = (
            f'<img src="data:image/png;base64,{b64_gea}" alt="Logo">'
            if b64_gea
            else '<span style="font-size:45px;">⚖️</span>'
        )

        st.markdown(
            f'<div class="logo-container">{img_sec_html}{img_gea_html}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div class="inst-header">
                <div class="inst-title">SECRETARÍA MUNICIPAL DE SEGURIDAD CIUDADANA Y TRÁNSITO DE BENITO JUÁREZ</div>
                <div class="inst-subtitle">GEAVIG</div>
            </div>
        """,
            unsafe_allow_html=True,
        )

        with st.form("form_login_geavig", clear_on_submit=False):
            st.markdown(
                "<div class='login-card-title'>Iniciar Sesión</div>",
                unsafe_allow_html=True,
            )
            usuario_input = (
                st.text_input("Usuario", placeholder="Ingrese su usuario")
                .lower()
                .strip()
            )
            password_input = st.text_input(
                "Contraseña", type="password", placeholder="••••••••••••"
            )
            submitted = st.form_submit_button(
                "INGRESAR AL SISTEMA", use_container_width=True
            )

            if submitted:
                if (
                    usuario_input in USUARIOS
                    and USUARIOS[usuario_input]["password"] == password_input
                ):
                    st.session_state["autenticado"] = True
                    st.session_state["usuario_actual"] = usuario_input
                    st.session_state["nombre_usuario"] = USUARIOS[
                        usuario_input
                    ]["nombre"]
                    st.session_state["rol_usuario"] = USUARIOS[usuario_input][
                        "rol"
                    ]
                    st.success(
                        f"Bienvenido(a), {st.session_state['nombre_usuario']}"
                    )
                    st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos")


if not st.session_state["autenticado"]:
    mostrar_login()
    st.stop()

# ---------------------------------------------------------
# BARRA LATERAL (CERRAR SESIÓN Y PERFIL)
# ---------------------------------------------------------
with st.sidebar:
    st.markdown(f"👤 **Usuario:** {st.session_state['nombre_usuario']}")
    st.markdown(f"🏷️ **Rol:** {st.session_state['rol_usuario'].upper()}")
    st.divider()
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state["autenticado"] = False
        st.session_state["usuario_actual"] = ""
        st.session_state["nombre_usuario"] = ""
        st.session_state["rol_usuario"] = ""
        st.session_state["registro_exitoso"] = False
        st.session_state["registros_capturados"] = []
        st.rerun()

# ---------------------------------------------------------
# FORMULARIO PRINCIPAL DE CAPTURA GEAVIG
# ---------------------------------------------------------
st.title("Sistema GEAVIG - Registro de Servicios")

with st.form("form_geavig"):
    st.subheader("1. Datos Generales y Control de Tiempos")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        capturista = st.text_input(
            "Nombre del Capturista",
            value=st.session_state["nombre_usuario"],
            disabled=True,
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

    submitted_registro = st.form_submit_button("Guardar Registro")

    if submitted_registro:
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
