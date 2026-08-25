import io
import os
import base64
import datetime
import unicodedata
import pandas as pd
import streamlit as st
from supabase import create_client, Client

# ---------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA
# ---------------------------------------------------------
st.set_page_config(page_title="Sistema GEAVIG Completo", layout="wide", page_icon="🛡️")

SUPABASE_URL = "https://neivobvldbqrlblrrmyd.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5laXZvYnZsZGJxcmxibHJybXlkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODczMjY0MjMsImV4cCI6MjEwMjkwMjQyM30.9CNcod0le2EtQgFQnxnWxURWfRd-jyF0RaBhblIhEw8"

@st.cache_resource
def init_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

# ---------------------------------------------------------
# SISTEMA DE USUARIOS Y CONTRASEÑAS
# ---------------------------------------------------------
USUARIOS = {
    "cristina98": {"password": "cristinaec", "nombre": "EDITOR / COORDINACIÓN", "rol": "editor"},
    "captura1": {"password": "geavig2026user", "nombre": "CAPTURISTA 1", "rol": "capturista"},
    "captura2": {"password": "geavig2026user", "nombre": "CAPTURISTA 2", "rol": "capturista"},
    "captura3": {"password": "geavig2026user", "nombre": "CAPTURISTA 3", "rol": "capturista"}
}

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
    st.session_state["usuario_actual"] = ""
    st.session_state["nombre_usuario"] = ""
    st.session_state["rol_usuario"] = ""

# ---------------------------------------------------------
# FUNCIÓN AUXILIAR PARA CORDENAR IMÁGENES BASE64
# ---------------------------------------------------------
def get_image_base64(ruta_imagen: str) -> str:
    if os.path.exists(ruta_imagen):
        with open(ruta_imagen, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    return ""

# ---------------------------------------------------------
# PANTALLA DE INICIO DE SESIÓN INSTITUCIONAL Y ELEGANTE
# ---------------------------------------------------------
def mostrar_login():
    st.markdown("""
        <style>
            /* 1. Fondo Púrpura Profundo */
            .stApp {
                background: linear-gradient(135deg, #2A0835 0%, #4A1259 50%, #170320 100%) !important;
                background-attachment: fixed !important;
            }

            header, footer, #MainMenu {
                visibility: hidden;
            }

            /* 2. Encabezado e identidades textuales */
            .inst-header {
                text-align: center;
                margin-top: 5px;
                margin-bottom: 25px;
            }
            .inst-title {
                color: #FFFFFF;
                font-family: 'Montserrat', 'Century Gothic', Arial, sans-serif;
                font-weight: 700;
                font-size: 26px;
                line-height: 1.15; /* Interlineado reducido */
                letter-spacing: 0.8px;
                text-transform: uppercase;
                margin-top: 10px;
                margin-bottom: 12px;
                text-shadow: 0px 2px 4px rgba(0, 0, 0, 0.4);
            }
            .inst-subtitle {
                color: rgba(255, 255, 255, 0.95);
                font-family: 'Montserrat', 'Century Gothic', Arial, sans-serif;
                font-weight: 700;
                font-size: 24px;
                letter-spacing: 2px;
                text-transform: uppercase;
                margin-bottom: 10px;
                text-shadow: 0px 1px 3px rgba(0, 0, 0, 0.3);
            }

            /* 3. Recuadro / Tarjeta de Login (Efecto Cristal) */
            div[data-testid="stForm"] {
                background: rgba(255, 255, 255, 0.08) !important;
                backdrop-filter: blur(14px) !important;
                -webkit-backdrop-filter: blur(14px) !important;
                border: 1px solid rgba(255, 255, 255, 0.18) !important;
                border-radius: 16px !important;
                padding: 30px 28px !important;
                box-shadow: 0 15px 35px rgba(0, 0, 0, 0.4) !important;
            }

            /* 4. Etiquetas de los inputs */
            div[data-testid="stForm"] label {
                color: #FFFFFF !important;
                font-family: 'Century Gothic', Arial, sans-serif !important;
                font-weight: 600 !important;
                font-size: 16px !important;
                letter-spacing: 0.5px !important;
            }

            /* 5. Campos de entrada */
            div[data-baseweb="input"] {
                background-color: rgba(255, 255, 255, 0.95) !important;
                border-radius: 8px !important;
                border: 1px solid rgba(255, 255, 255, 0.3) !important;
                transition: all 0.3s ease !important;
            }
            div[data-baseweb="input"]:focus-within {
                border-color: #D4AF37 !important;
                box-shadow: 0 0 8px rgba(212, 175, 55, 0.4) !important;
            }
            div[data-baseweb="input"] input {
                color: #111827 !important;
                font-size: 15px !important;
            }

            /* 6. Botón de Ingreso */
            div.stButton > button {
                background: linear-gradient(90deg, #801538 0%, #A31E48 100%) !important;
                color: #FFFFFF !important;
                border-radius: 10px !important;
                border: 1px solid rgba(255, 255, 255, 0.2) !important;
                height: 48px !important;
                font-family: 'Segoe UI', Arial, sans-serif !important;
                font-weight: 700 !important;
                font-size: 15px !important;
                letter-spacing: 1px !important;
                text-transform: uppercase !important;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.25) !important;
                transition: all 0.3s ease !important;
                margin-top: 15px !important;
            }

            div.stButton > button:hover {
                background: linear-gradient(90deg, #9A1A44 0%, #C22355 100%) !important;
                box-shadow: 0 6px 20px rgba(163, 30, 72, 0.45) !important;
                transform: translateY(-1px) !important;
                color: #FFFFFF !important;
            }

            .login-card-title {
                color: #FFFFFF;
                font-weight: 700;
                font-size: 20px;
                text-align: center;
                margin-bottom: 22px;
                letter-spacing: 0.5px;
            }

            /* Contenedor flexible de logos para centrado perfecto */
            .logo-container {
                display: flex;
                justify-content: center;
                align-items: center;
                gap: 24px;
                margin-bottom: 12px;
                width: 100%;
            }
            .logo-container img {
                width: 105px;
                height: auto;
                object-fit: contain;
            }
        </style>
    """, unsafe_allow_html=True)

    col_left, col_center, col_right = st.columns([1, 1.8, 1])

    with col_center:
        # --- LOGOS PERFECTAMENTE CENTRADOS MEDIANTE FLEXBOX ---
        b64_sec = get_image_base64("logo_secretaria.png")
        b64_gea = get_image_base64("logo_geavig.png")

        img_sec_html = f'<img src="data:image/png;base64,{b64_sec}" alt="Logo Secretaría">' if b64_sec else '<span style="font-size:45px;">🛡️</span>'
        img_gea_html = f'<img src="data:image/png;base64,{b64_gea}" alt="Logo GEAVIG">' if b64_gea else '<span style="font-size:45px;">⚖️</span>'

        st.markdown(f"""
            <div class="logo-container">
                {img_sec_html}
                {img_gea_html}
            </div>
        """, unsafe_allow_html=True)

        # --- NOMBRES INSTITUCIONALES CON INTERLINEADO AJUSTADO ---
        st.markdown("""
            <div class="inst-header">
                <div class="inst-title">SECRETARÍA MUNICIPAL DE SEGURIDAD CIUDADANA Y TRÁNSITO DE BENITO JUÁREZ</div>
                <div class="inst-subtitle">GEAVIG</div>
            </div>
        """, unsafe_allow_html=True)

        # --- RECUADRO DE CAPTURA DE CREDENCIALES ---
        with st.form("form_login_geavig", clear_on_submit=False):
            st.markdown("<div class='login-card-title'>Iniciar Sesión</div>", unsafe_allow_html=True)
            
            usuario_input = st.text_input("Usuario", placeholder="Ingrese su usuario").lower().strip()
            password_input = st.text_input("Contraseña", type="password", placeholder="••••••••••••")
            
            submitted = st.form_submit_button("INGRESAR AL SISTEMA", use_container_width=True)
            
            if submitted:
                if usuario_input in USUARIOS and USUARIOS[usuario_input]["password"] == password_input:
                    st.session_state["autenticado"] = True
                    st.session_state["usuario_actual"] = usuario_input
                    st.session_state["nombre_usuario"] = USUARIOS[usuario_input]["nombre"]
                    st.session_state["rol_usuario"] = USUARIOS[usuario_input]["rol"]
                    st.success(f"Bienvenido(a), {st.session_state['nombre_usuario']}")
                    st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos")

        # 👈 Presionas ENTER al final del "else:" y pegas esto con 8 espacios a la izquierda (alineado con "with st.form"):
        with st.expander("🔑 Credenciales de Acceso / Demo"):
            st.markdown("""
            | Usuario | Contraseña | Rol | Acceso |
            | :--- | :--- | :--- | :--- |
            | **editor** | `geavig2026admin` | Editor | Captura + Ver Base de Datos y Exportar Excel |
            | **captura1** | `geavig2026user` | Capturista | Únicamente Formulario de Captura |
            | **captura2** | `geavig2026user` | Capturista | Únicamente Formulario de Captura |
            | **captura3** | `geavig2026user` | Capturista | Únicamente Formulario de Captura |
            """)
            
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
        st.rerun()

# ---------------------------------------------------------
# FUNCIÓN AUXILIAR: MAYÚSCULAS Y SIN ACENTOS
# ---------------------------------------------------------
def normalizar(texto) -> str:
    if not texto:
        return ""
    str_texto = str(texto)
    nfd = unicodedata.normalize('NFD', str_texto)
    sin_acentos = ''.join(c for c in nfd if unicodedata.category(c) != 'Mn')
    return sin_acentos.upper().strip()

# ---------------------------------------------------------
# LECTURA DE CATÁLOGOS DESDE EXCEL
# ---------------------------------------------------------
@st.cache_data
def cargar_catalogos():
    archivo_excel = "sectores.xlsx"
    catalogos = {
        "SMZ_SECTOR": {},
        "QUIEN_REPORTA": ["911", "PARTICULAR", "PATRULLAJE", "PUNTO MORADO", "REDES SOCIALES", "AUXILIO DIRECTO", "OTRO"],
        "PARTICULAR": ["VICTIMA / AFECTADO(A)", "FAMILIAR", "VECINO(A)", "TESTIGO", "ANONIMO", "OTRO"],
        "MEDIO_DE_REPORTE": ["911", "AUXILIO DIRECTO", "PATRULLAJE", "PUNTO MORADO", "REDES SOCIALES", "OTRO"],
        "RELACION_CON_EL_AGRESOR": ["CONYUGE", "CONCUBINO(A)", "EXCONYUGE", "EXCONCUBINO(A)", "NOVIO(A)", "EXNOVIO(A)", "PADRE/MADRE", "HIJO(A)", "HERMANO(A)", "PARIENTE", "VECINO(A)", "CONOCIDO(A)", "NINGUNA", "OTRO"],
        "NACIONALIDAD": ["MEXICANA", "EXTRANJERA", "NO ESPECIFICA"],
        "ENTIDAD_DE_ORIGEN": [
            "AGUASCALIENTES", "BAJA CALIFORNIA", "BAJA CALIFORNIA SUR", "CAMPECHE", "CHIAPAS",
            "CHIHUAHUA", "CIUDAD DE MEXICO", "COAHUILA", "COLIMA", "DURANGO", "ESTADO DE MEXICO",
            "GUANAJUATO", "GUERRERO", "HIDALGO", "JALISCO", "MICHOACAN", "MORELOS", "NAYARIT",
            "NUEVO LEON", "OAXACA", "PUEBLA", "QUERETARO", "QUINTANA ROO", "SAN LUIS POTOSI",
            "SINALOA", "SONORA", "TABASCO", "TAMAULIPAS", "TLAXCALA", "VERACRUZ", "YUCATAN", "ZACATECAS"
        ],
        "TIPO_DE_VIOLENCIA": ["PSICOLOGICA", "FISICA", "PATRIMONIAL", "ECONOMICA", "SEXUAL", "VICARIA", "OTRO"],
        "MODALIDAD": ["FAMILIAR", "COMUNITARIA", "LABORAL", "DOCENTE", "INSTITUCIONAL", "DIGITAL", "OTRO"],
        "TIPO_DE_ATENCION": ["PRIMERA VEZ", "SUBSECUENTE", "CANALIZACION", "ASESORIA JURIDICA", "ATENCION PSICOLOGICA", "OTRO"],
        "RED_DE_APOYO": ["FAMILIAR", "INSTITUCIONAL", "VECINAL", "AMIGOS / CONOCIDOS", "NINGUNA", "OTRO"],
        "ES_REITERADO": ["NO", "SI", "SE DESCONOCE"],
        "FACTOR_DE_RIESGO": ["CONSUMO DE ALCOHOL", "CONSUMO DE DROGAS", "USO DE ARMAS", "AMENAZAS DE MUERTE", "ANTECEDENTES DE VIOLENCIA", "NINGUNO", "OTRO"],
        "TURNADO": ["MINISTERIO PUBLICO", "JUEZ CIVICO", "DIF", "INSTANCIA DE LA MUJER", "CENTRO DE JUSTICIA PARA LAS MUJERES", "NO TURNADO", "OTRO"],
        "FISCALIA": ["FISCALIA ESPECIALIZADA EN DELITOS CONTRA LA MUJER Y POR RAZON DE GENERO", "FISCALIA DE DISTRITO", "FISCALIA GENERAL DEL ESTADO", "FISCALIA ESPECIALIZADA EN COMBATE AL NARCOMENUDEO", "OTRA"]
    }

    if os.path.exists(archivo_excel):
        try:
            xls = pd.ExcelFile(archivo_excel)
            for sheet in xls.sheet_names:
                df = pd.read_excel(xls, sheet_name=sheet)
                df.columns = [normalizar(col) for col in df.columns]
                
                col_sector = 'SECTORES' if 'SECTORES' in df.columns else ('SECTOR' if 'SECTOR' in df.columns else None)
                if 'SMZ' in df.columns and col_sector:
                    smz_s = df['SMZ'].dropna().astype(str).apply(normalizar)
                    sec_s = df[col_sector].dropna().astype(str).apply(normalizar)
                    catalogos["SMZ_SECTOR"].update(dict(zip(smz_s, sec_s)))

                mapeo = {
                    "QUIEN REPORTA": "QUIEN_REPORTA",
                    "PARTICULAR": "PARTICULAR",
                    "MEDIO DE REPORTE": "MEDIO_DE_REPORTE",
                    "RELACION CON EL AGRESOR": "RELACION_CON_EL_AGRESOR",
                    "NACIONALIDAD": "NACIONALIDAD",
                    "ENTIDAD DE ORIGEN": "ENTIDAD_DE_ORIGEN",
                    "TIPO DE VIOLENCIA": "TIPO_DE_VIOLENCIA",
                    "MODALIDAD": "MODALIDAD",
                    "MODALIDAD DE VIOLENCIA": "MODALIDAD",
                    "TIPO DE ATENCION": "TIPO_DE_ATENCION",
                    "RED DE APOYO": "RED_DE_APOYO",
                    "ES REITERADO": "ES_REITERADO",
                    "FACTOR DE RIESGO": "FACTOR_DE_RIESGO",
                    "TURNADO": "TURNADO",
                    "FISCALIA": "FISCALIA"
                }

                for col_name, key_cat in mapeo.items():
                    col_norm = normalizar(col_name)
                    if col_norm in df.columns:
                        vals = df[col_norm].dropna().astype(str).apply(normalizar).unique().tolist()
                        vals = [v for v in vals if v and v != "NAN"]
                        if vals:
                            catalogos[key_cat] = vals
        except Exception as e:
            st.error(f"Error al leer catálogos desde sectores.xlsx: {e}")

    for cat_key in catalogos:
        if isinstance(catalogos[cat_key], list):
            catalogos[cat_key] = [normalizar(v) for v in catalogos[cat_key]]

    return catalogos

catalogos = cargar_catalogos()
mapa_sectores = catalogos["SMZ_SECTOR"]
lista_smz = ["SELECCIONAR..."] + sorted(list(mapa_sectores.keys())) if mapa_sectores else ["SELECCIONAR..."]

# ---------------------------------------------------------
# VISTA PRINCIPAL SEGÚN EL ROL DEL USUARIO
# ---------------------------------------------------------
st.title("🛡️ SISTEMA INTEGRAL DE REGISTRO - GEAVIG")

if st.session_state["rol_usuario"] == "editor":
    tab1, tab2 = st.tabs(["📋 Formulario Completo", "📊 Coordinación y Exportación"])
else:
    tab1 = st.container()

with tab1:
    st.header("1. Datos Generales y Control de Tiempos")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        capturista = normalizar(st.text_input("Nombre del Capturista", value=st.session_state["nombre_usuario"]))
        fecha_captura = st.date_input("Fecha de Captura", datetime.date.today())
        fecha_reporte = st.date_input("Fecha del Reporte", datetime.date.today())
    
    with c2:
        turno = st.selectbox("Turno", ["A", "B", "C", "ATENCION A VICTIMAS", "OTRO"])
        unidad = normalizar(st.text_input("Unidad / Patrulla"))
        
        quien_rep_sel = st.selectbox("Quién Reporta", catalogos["QUIEN_REPORTA"])
        if quien_rep_sel == "PARTICULAR":
            particular_sel = st.selectbox("Tipo de Particular", catalogos["PARTICULAR"])
            if particular_sel == "OTRO":
                part_esp = normalizar(st.text_input("Especifique Particular"))
                quien_reporta = f"PARTICULAR - {part_esp}" if part_esp else "PARTICULAR"
            else:
                quien_reporta = f"PARTICULAR - {particular_sel}"
        elif quien_rep_sel == "OTRO":
            quien_esp = normalizar(st.text_input("Especifique Quién Reporta"))
            quien_reporta = quien_esp if quien_esp else "OTRO"
        else:
            quien_reporta = quien_rep_sel

    with c3:
        medio_sel = st.selectbox("Medio de Reporte", catalogos["MEDIO_DE_REPORTE"])
        if medio_sel == "OTRO":
            medio_reporte = normalizar(st.text_input("Especifique Medio"))
        else:
            medio_reporte = medio_sel

        hora_reporte = st.time_input("Hora del Reporte", datetime.time(0, 0))
        hora_llegada = st.time_input("Hora de Llegada", datetime.time(0, 0))

    with c4:
        hora_cierre = st.time_input("Hora de Cierre", datetime.time(0, 0))
        
        dt_llegada = datetime.datetime.combine(datetime.date.today(), hora_llegada)
        dt_cierre = datetime.datetime.combine(datetime.date.today(), hora_cierre)
        if dt_cierre < dt_llegada:
            dt_cierre += datetime.timedelta(days=1)

        minutos_totales = int((dt_cierre - dt_llegada).total_seconds() / 60)
        horas_calc = minutos_totales // 60
        mins_calc = minutos_totales % 60
        tiempo_calculado = f"{horas_calc} HRS {mins_calc} MIN" if horas_calc > 0 else f"{mins_calc} MIN"

        tiempo_atencion = st.text_input("Tiempo de Atención (Automático)", value=tiempo_calculado, disabled=True)
        al_mando = normalizar(st.text_input("Al Mando"))
        reporte_911 = normalizar(st.text_input("Folio / Reporte 911"))

    st.divider()

    st.header("2. Ubicación de los Hechos")
    u1, u2, u3, u4 = st.columns(4)
    with u1:
        if mapa_sectores:
            smz_seleccionada = st.selectbox("SMZ / Supermanzana / Región", lista_smz)
            sector_calculado = mapa_sectores.get(smz_seleccionada, "") if smz_seleccionada != "SELECCIONAR..." else ""
        else:
            smz_seleccionada = normalizar(st.text_input("SMZ / Supermanzana"))
            sector_calculado = ""

        manzana = normalizar(st.text_input("Manzana"))
        lote = normalizar(st.text_input("Lote"))

    with u2:
        sector = st.text_input("Sector Asignado (Automático)", value=sector_calculado, disabled=True)
        calle = normalizar(st.text_input("Calle"))
        colonia = normalizar(st.text_input("Colonia / Fraccionamiento"))

    with u3:
        no_ext = normalizar(st.text_input("No. Exterior"))
        referencia = normalizar(st.text_input("Referencia del lugar"))

    with u4:
        longitud = normalizar(st.text_input("Longitud"))
        latitud = normalizar(st.text_input("Latitud"))

    st.divider()

    st.header("3. Datos de la Víctima")
    v1, v2 = st.columns(2)
    
    with v1:
        vic_nombre = normalizar(st.text_input("Nombre Completo de la Víctima"))
        
        f1_1, f1_2 = st.columns(2)
        with f1_1:
            vic_edad = st.number_input("Edad Víctima", min_value=0, max_value=120, value=0)
        with f1_2:
            vic_sexo = st.selectbox("Sexo Víctima", ["FEMENINO", "MASCULINO", "NO ESPECIFICA"])
            
        vic_rel_sel = st.selectbox("Relación con el Agresor", catalogos["RELACION_CON_EL_AGRESOR"])
        if vic_rel_sel == "OTRO":
            vic_relacion_agresor = normalizar(st.text_input("Especifique Relación con Agresor"))
        else:
            vic_relacion_agresor = vic_rel_sel

        vic_nac_sel = st.selectbox("Nacionalidad Víctima", catalogos["NACIONALIDAD"], key="vic_nac_sel")
        if vic_nac_sel == "EXTRANJERA":
            vic_nac_ext = normalizar(st.text_input("Especifique País / Nacionalidad Extranjera (Víctima)", key="vic_nac_ext"))
            vic_nacionalidad = f"EXTRANJERA - {vic_nac_ext}" if vic_nac_ext else "EXTRANJERA"
            vic_entidad_origen = "NO APLICA"
        elif vic_nac_sel == "MEXICANA":
            vic_entidad_origen = st.selectbox("Entidad de Origen (Víctima)", ["SELECCIONAR..."] + catalogos["ENTIDAD_DE_ORIGEN"], key="vic_ent_sel")
            vic_nacionalidad = "MEXICANA"
        else:
            vic_nacionalidad = vic_nac_sel
            vic_entidad_origen = "NO ESPECIFICA"

    with v2:
        f2_1, f2_2 = st.columns(2)
        with f2_1:
            vic_empleada = st.selectbox("¿Es empleada / Trabaja?", ["NO", "SI"])
        with f2_2:
            if vic_empleada == "SI":
                vic_ocupacion = normalizar(st.text_input("¿A qué se dedica / Ocupación?"))
            else:
                vic_ocupacion = "NO TRABAJA"

        vic_gv_sel = st.selectbox("Grupo Vulnerable", ["NINGUNO", "ADULTO MAYOR", "NISA (NINA/NINO/ADOLESCENTE)", "DISCAPACIDAD", "INDIGENA", "LGBTTTIQ+", "OTRO"])
        if vic_gv_sel == "DISCAPACIDAD":
            tipo_disc = normalizar(st.text_input("Especifique Tipo de Discapacidad"))
            vic_grupo_vulnerable = f"DISCAPACIDAD - {tipo_disc}" if tipo_disc else "DISCAPACIDAD"
        elif vic_gv_sel == "OTRO":
            especifique_gv = normalizar(st.text_input("Especifique Grupo Vulnerable"))
            vic_grupo_vulnerable = especifique_gv if especifique_gv else "OTRO"
        else:
            vic_grupo_vulnerable = vic_gv_sel

        vic_esc_sel = st.selectbox("Escolaridad Víctima", ["SIN ESCOLARIDAD", "PRIMARIA", "SECUNDARIA", "PREPARATORIA", "LICENCIATURA", "POSGRADO", "NO ESPECIFICA", "OTRO"])
        if vic_esc_sel == "OTRO":
            vic_escolaridad = normalizar(st.text_input("Especifique Escolaridad Víctima"))
        else:
            vic_escolaridad = vic_esc_sel

        tiene_hijos = st.selectbox("¿Tiene Hijos?", ["NO", "SI"])

    hijos_list = []
    hijos_resumen = "SIN HIJOS"
    num_hijos_val = 0

    if tiene_hijos == "SI":
        st.markdown("#### 👶 Registro de Hijos")
        num_hijos_val = st.number_input("Número de Hijos", min_value=1, max_value=15, value=1, step=1)
        
        for i in range(int(num_hijos_val)):
            st.markdown(f"**Hijo(a) #{i+1}**")
            hc1, hc2, hc3 = st.columns(3)
            with hc1:
                h_nombre = normalizar(st.text_input(f"Nombre del Hijo(a) #{i+1}", key=f"hijo_nombre_{i}"))
            with hc2:
                h_edad = st.number_input(f"Edad del Hijo(a) #{i+1}", min_value=0, max_value=100, value=0, key=f"hijo_edad_{i}")
            with hc3:
                h_sexo = st.selectbox(f"Sexo del Hijo(a) #{i+1}", ["FEMENINO", "MASCULINO", "OTRO"], key=f"hijo_sexo_{i}")
            
            h_nac_sel = st.selectbox(f"Nacionalidad Hijo(a) #{i+1}", catalogos["NACIONALIDAD"], key=f"hijo_nac_{i}")
            if h_nac_sel == "EXTRANJERA":
                h_nac_ext = normalizar(st.text_input(f"Especifique Nacionalidad Extranjera Hijo(a) #{i+1}", key=f"hijo_ext_{i}"))
                h_nac_final = f"EXTRANJERA - {h_nac_ext}" if h_nac_ext else "EXTRANJERA"
                h_entidad = "NO APLICA"
            elif h_nac_sel == "MEXICANA":
                h_entidad = st.selectbox(f"Entidad Origen Hijo(a) #{i+1}", ["SELECCIONAR..."] + catalogos["ENTIDAD_DE_ORIGEN"], key=f"hijo_ent_{i}")
                h_nac_final = "MEXICANA"
            else:
                h_nac_final = h_nac_sel
                h_entidad = "NO ESPECIFICA"

            nombre_txt = h_nombre if h_nombre else f"HIJO #{i+1}"
            hijos_list.append(f"{nombre_txt} ({h_edad} ANOS, {h_sexo}, NAC: {h_nac_final}, ENTIDAD: {h_entidad})")

        hijos_resumen = " | ".join(hijos_list)

    st.divider()

    st.header("4. Datos del Agresor(a)")
    a1, a2 = st.columns(2)
    
    with a1:
        agr_nombre = normalizar(st.text_input("Nombre Completo del Agresor(a)"))
        
        fa1_1, fa1_2 = st.columns(2)
        with fa1_1:
            agr_edad = st.number_input("Edad Agresor", min_value=0, max_value=120, value=0)
        with fa1_2:
            agr_sexo = st.selectbox("Sexo Agresor", ["MASCULINO", "FEMENINO", "OTRO", "SE DESCONOCE"])

        agr_nac_sel = st.selectbox("Nacionalidad Agresor", catalogos["NACIONALIDAD"], key="agr_nac_sel")
        if agr_nac_sel == "EXTRANJERA":
            agr_nac_ext = normalizar(st.text_input("Especifique País / Nacionalidad Extranjera (Agresor)", key="agr_nac_ext"))
            agr_nacionalidad = f"EXTRANJERA - {agr_nac_ext}" if agr_nac_ext else "EXTRANJERA"
            agr_entidad_origen = "NO APLICA"
        elif agr_nac_sel == "MEXICANA":
            agr_entidad_origen = st.selectbox("Entidad de Origen Agresor", ["SELECCIONAR..."] + catalogos["ENTIDAD_DE_ORIGEN"], key="agr_ent_sel")
            agr_nacionalidad = "MEXICANA"
        else:
            agr_nacionalidad = agr_nac_sel
            agr_entidad_origen = "NO ESPECIFICA"

        fa2_1, fa2_2 = st.columns(2)
        with fa2_1:
            agr_empleado = st.selectbox("¿El Agresor trabaja?", ["NO", "SI", "SE DESCONOCE"])
        with fa2_2:
            if agr_empleado == "SI":
                agr_ocupacion = normalizar(st.text_input("¿A qué se dedica / Ocupación Agresor?"))
            else:
                agr_ocupacion = "NO TRABAJA" if agr_empleado == "NO" else "SE DESCONOCE"

    with a2:
        agr_detenido = st.selectbox("¿Agresor Detenido?", ["NO", "SI", "SE DIO A LA FUGA"])

        agr_esc_sel = st.selectbox("Escolaridad Agresor", ["SIN ESCOLARIDAD", "PRIMARIA", "SECUNDARIA", "PREPARATORIA", "LICENCIATURA", "POSGRADO", "SE DESCONOCE", "OTRO"])
        if agr_esc_sel == "OTRO":
            agr_escolaridad = normalizar(st.text_input("Especifique Escolaridad Agresor"))
        else:
            agr_escolaridad = agr_esc_sel

    st.divider()

    st.header("5. Clasificación e IPH")

    se_elaboro_iph_val = st.session_state.get("se_elaboro_iph", "SI")
    iph_bloqueado = (se_elaboro_iph_val == "NO")

    i1, i2, i3, i4 = st.columns(4)
    
    with i1:
        resolucion_geavig = normalizar(st.text_input("Resolución GEAVIG"))
        estatus_reporte = st.selectbox("Estatus del Reporte", ["CONCLUIDO", "PENDIENTE", "CANALIZADO", "EN PROCESO"])
        reporte_fue = st.selectbox("El Reporte fue", ["POSITIVO", "FALSO", "NO LOCALIZADO", "CANCELADO"])
        hubo_victimas = st.selectbox("¿Hubo Víctimas?", ["SI", "NO"])
        cuantas_victimas = st.number_input("¿Cuántas Víctimas?", min_value=0, max_value=50, value=1)

    with i2:
        tv_sel = st.selectbox("Tipo de Violencia", catalogos["TIPO_DE_VIOLENCIA"])
        if tv_sel == "OTRO":
            tipo_violencia = normalizar(st.text_input("Especifique Violencia"))
        else:
            tipo_violencia = tv_sel

        accion = normalizar(st.text_input("Acción"))
        es_reiterado = st.selectbox("¿Es Reiterado?", catalogos["ES_REITERADO"])

        fr_sel = st.selectbox("Factor de Riesgo", catalogos["FACTOR_DE_RIESGO"])
        if fr_sel == "OTRO":
            factor_riesgo = normalizar(st.text_input("Especifique Factor de Riesgo"))
        else:
            factor_riesgo = fr_sel

    with i3:
        ta_sel = st.selectbox("Tipo de Atención", catalogos["TIPO_DE_ATENCION"])
        if ta_sel == "OTRO":
            tipo_atencion = normalizar(st.text_input("Especifique Tipo de Atención"))
        else:
            tipo_atencion = ta_sel

        mod_sel = st.selectbox("Modalidad", catalogos["MODALIDAD"])
        if mod_sel == "OTRO":
            modalidad = normalizar(st.text_input("Especifique Modalidad"))
        else:
            modalidad = mod_sel

        conducta = normalizar(st.text_input("Conducta"))
        nivel_riesgo = st.selectbox("Nivel de Riesgo", ["BAJO", "MEDIO", "ALTO", "CRITICO"])

        if iph_bloqueado:
            probable_delito = st.text_input("Probable Delito", value="N/A", disabled=True)
        else:
            probable_delito = normalizar(st.text_input("Probable Delito"))

    with i4:
        cuenta_red_apoyo = st.selectbox("¿Cuenta con Red de Apoyo?", ["NO", "SI"])
        if cuenta_red_apoyo == "SI":
            red_apoyo_sel = st.selectbox("Red de Apoyo Canalizado", catalogos["RED_DE_APOYO"])
            if red_apoyo_sel == "OTRO":
                red_apoyo_esp = normalizar(st.text_input("Especifique Red de Apoyo"))
                red_de_apoyo_canalizado = red_apoyo_esp if red_apoyo_esp else "OTRO"
            else:
                red_de_apoyo_canalizado = red_apoyo_sel
        else:
            red_de_apoyo_canalizado = "NO APLICA"

        primer_respondiente = normalizar(st.text_input("Primer Respondiente"))

        se_elaboro_iph = st.selectbox("¿Se elaboró IPH?", ["SI", "NO"], key="se_elaboro_iph")

        if iph_bloqueado:
            num_iph = st.text_input("Número de IPH", value="N/A", disabled=True)
            turnado = "NO TURNADO"
            st.selectbox("Turnado a", ["NO TURNADO"], disabled=True)
        else:
            num_iph = normalizar(st.text_input("Número de IPH"))
            turnado_sel = st.selectbox("Turnado a", catalogos["TURNADO"])
            if turnado_sel == "OTRO":
                turnado_esp = normalizar(st.text_input("Especifique Turnado"))
                turnado = turnado_esp if turnado_esp else "OTRO"
            else:
                turnado = turnado_sel

    if not iph_bloqueado and turnado == "MINISTERIO PUBLICO":
        st.markdown("**Fiscalía que Recibe:**")
        fiscalia_sel = st.selectbox("Seleccione Fiscalía que recibe el caso", catalogos["FISCALIA"], key="fiscalia_full")
        if fiscalia_sel in ["OTRA", "OTRO"]:
            fiscalia_recibe = normalizar(st.text_input("Especifique Fiscalía", key="fiscalia_esp_full"))
        else:
            fiscalia_recibe = fiscalia_sel
    else:
        fiscalia_recibe = "N/A"

    st.divider()
    if st.button("💾 GUARDAR REGISTRO EN EL SISTEMA", use_container_width=True):
        st.success("✅ Registro validado y listo para sincronizar.")

# ---------------------------------------------------------
# PESTAÑA DE COORDINACIÓN (SOLO EDITOR)
# ---------------------------------------------------------
if st.session_state["rol_usuario"] == "editor":  
    with tab2:
        st.header("📊 Panel de Coordinación y Exportación de Datos")
        st.info("Vista para consulta general, métricas y descarga de reportes consolidado.")   
        
        st.divider()
        
        # --- TABLA DE USUARIOS Y ROLES ---
        st.markdown("""
        | Usuario | Contraseña | Rol | Permisos y Acceso |
        | :--- | :--- | :--- | :--- |
        | **editor** | `geavig2026admin` | Editor | Captura + Ver Base de Datos y Exportar Excel |
        | **captura1** | `geavig2026user` | Capturista | Únicamente Formulario de Captura |
        | **captura2** | `geavig2026user` | Capturista | Únicamente Formulario de Captura |
        | **captura3** | `geavig2026user` | Capturista | Únicamente Formulario de Captura |
        """)
