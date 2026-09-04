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
# ESTADOS DE SESIÓN Y CONTROL DE LIMPIEZA DE FORMULARIO
# ---------------------------------------------------------
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
    st.session_state["usuario_actual"] = ""
    st.session_state["nombre_usuario"] = ""
    st.session_state["rol_usuario"] = ""

if "registro_exitoso" not in st.session_state:
    st.session_state["registro_exitoso"] = False

if "form_id" not in st.session_state:
    st.session_state["form_id"] = 0

if "registros_capturados" not in st.session_state:
    st.session_state["registros_capturados"] = []

if "temp_registro" not in st.session_state:
    st.session_state["temp_registro"] = {}

# ---------------------------------------------------------
# ESTRUCTURA DE CLASIFICACIÓN DE VIOLENCIA (JERARQUÍA)
# ---------------------------------------------------------
TAXONOMIA_VIOLENCIA = {
    "VIOLENCIA EN EL AMBITO FAMILIAR": {
        "VIOLENCIA FAMILIAR": [
            "VIOLENCIA FISICA",
            "VIOLENCIA PSICOLOGICA",
            "VIOLENCIA SEXUAL",
            "VIOLENCIA ECONOMICA",
            "VIOLENCIA PATRIMONIAL",
            "VIOLENCIA MORAL"
        ]
    },
    "VIOLENCIA EN RELACIONES DE HECHO Y NOVIAZGO": {
        "RELACION DE HECHO": [
            "VIOLENCIA FISICA",
            "VIOLENCIA PSICOLOGICA",
            "VIOLENCIA SEXUAL",
            "VIOLENCIA ECONOMICA",
            "VIOLENCIA PATRIMONIAL",
            "VIOLENCIA MORAL"
        ]
    },
    "VIOLENCIA EN EL AMBITO LABORAL Y DOCENTE": {
        "VIOLENCIA LABORAL": [
            "HOSTIGAMIENTO SEXUAL",
            "ACOSO SEXUAL",
            "ACOSO LABORAL",
            "DISCRIMINACION LABORAL",
            "AMENAZAS",
            "INTIMIDACION",
            "HUMILLACIONES",
            "EXPLOTACION LABORAL"
        ],
        "VIOLENCIA DOCENTE": [
            "HOSTIGAMIENTO SEXUAL",
            "ACOSO SEXUAL",
            "DISCRIMINACION",
            "HUMILLACION",
            "ABUSO DE PODER",
            "ABUSO DE AUTORIDAD ESCOLAR"
        ]
    },
    "VIOLENCIA EN LA COMUNIDAD": {
        "ESPACIO PUBLICO": [
            "ACOSO SEXUAL EN ESPACIOS PUBLICOS",
            "DISCRIMINACION",
            "DENIGRACION",
            "MARGINACION",
            "EXCLUSION"
        ]
    },
    "VIOLENCIA INSTITUCIONAL": {
        "INSTITUCIONES PUBLICAS": [
            "DISCRIMINACION INSTITUCIONAL",
            "OMISION",
            "NEGLIGENCIA",
            "DILACION",
            "OBSTACULIZACION DE DERECHOS",
            "NEGACION DE SERVICIOS",
            "REVICTIMIZACION"
        ]
    },
    "VIOLENCIA POLITICA CONTRA LAS MUJERES EN RAZON DE GENERO": {
        "AMBITO POLITICO Y ELECTORAL": [
            "OBSTACULIZACION DE DERECHOS POLITICOS",
            "OBSTACULIZACION DEL EJERCICIO DEL CARGO",
            "AMENAZAS",
            "INTIMIDACION",
            "DISCRIMINACION",
            "DESCALIFICACION",
            "DIFAMACION"
        ]
    },
    "VIOLENCIA DIGITAL": {
        "TECNOLOGIAS DE LA INFORMACION Y COMUNICACION": [
            "DIFUSION DE CONTENIDO INTIMO SIN CONSENTIMIENTO",
            "PUBLICACION DE IMAGENES INTIMAS",
            "ACOSO DIGITAL",
            "AMENAZAS DIGITALES",
            "DANO A LA INTIMIDAD",
            "DANO A LA DIGNIDAD"
        ]
    },
    "VIOLENCIA MEDIATICA": {
        "MEDIOS DE COMUNICACION": [
            "ESTEREOTIPOS SEXISTAS",
            "DISCRIMINACION DE GENERO",
            "COSIFICACION",
            "HIPERSEXUALIZACION",
            "DISCURSO DE ODIO SEXISTA",
            "APOLOGIA DE LA VIOLENCIA"
        ]
    },
    "VIOLENCIA FEMINICIDA": {
        "VIOLENCIA EXTREMA DE GENERO": [
            "CONDUCTAS DE ODIO",
            "DISCRIMINACION",
            "VIOLENCIA EXTREMA",
            "MUERTE VIOLENTA",
            "FEMINICIDIO"
        ]
    },
    "VIOLENCIA VICARIA": {
        "VIOLENCIA A TRAVES DE HIJAS E HIJOS": [
            "SUSTRACCION DE HIJAS E HIJOS",
            "RETENCION DE HIJAS E HIJOS",
            "AMENAZA DE CUSTODIA",
            "IMPEDIMENTO DE CONVIVENCIA",
            "MANIPULACION DE HIJAS E HIJOS"
        ]
    }
}

# ---------------------------------------------------------
# FUNCIONES AUXILIARES
# ---------------------------------------------------------
def tiene_acentos_o_minusculas(texto: str) -> bool:
    if not texto:
        return False
    for char in str(texto):
        if char.islower():
            return True
        nfd = unicodedata.normalize('NFD', char)
        if any(unicodedata.category(c) == 'Mn' for c in nfd):
            return True
    return False

def normalizar(texto) -> str:
    if not texto:
        return ""
    str_texto = str(texto)
    nfd = unicodedata.normalize('NFD', str_texto)
    sin_acentos = ''.join(c for c in nfd if unicodedata.category(c) != 'Mn')
    return sin_acentos.upper().strip()

@st.dialog("⚠️ ALERTA DE FORMATO")
def popup_alerta_formato(campo_nombre: str):
    st.warning("⚠️ VERIFICAR QUE NO LLEVE ACENTUACIÓN Y TODO ESTÉ EN MAYÚSCULAS")
    st.write(f"Se detectaron minúsculas o acentos en el campo: **{campo_nombre}**.")
    st.caption("El texto se convierte automáticamente al formato normado sin acentos y en mayúsculas.")
    if st.button("Verificar y Continuar", key=f"btn_alerta_cont_{campo_nombre}", use_container_width=True):
        st.rerun()

def capturar_texto_validado(label: str, key: str, value: str = "", disabled: bool = False) -> str:
    val_ingresado = st.text_input(label, value=value, key=key, disabled=disabled)
    if not disabled and tiene_acentos_o_minusculas(val_ingresado):
        popup_alerta_formato(label)
    return normalizar(val_ingresado)

def get_image_base64(ruta_imagen: str) -> str:
    if os.path.exists(ruta_imagen):
        with open(ruta_imagen, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    return ""

def generar_excel_bytes(df_datos: pd.DataFrame) -> bytes:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_datos.to_excel(writer, index=False, sheet_name='Capturas_GEAVIG')
    return output.getvalue()

@st.dialog("🚨 ALERTA DE VALIDACIÓN DE INFORMACIÓN")
def popup_confirmacion_guardado():
    st.markdown("""
        <div style="background-color: #FFF3CD; border: 2px solid #FFECB5; border-radius: 10px; padding: 18px; margin-bottom: 15px;">
            <p style="color: #842029; font-size: 15px; font-weight: 700; text-align: center; margin: 0;">
                "Una vez guardada la información no podrá hacerse modificaciones, usted ha validado la información."
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    confirmado_check = st.checkbox("☑️ Confirmo que la información ha sido verificada y es correcta para su registro definitivo.")
    
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        if st.button("✅ CONFIRMAR Y GUARDAR", disabled=not confirmado_check, use_container_width=True):
            if st.session_state["temp_registro"]:
                st.session_state["registros_capturados"].append(st.session_state["temp_registro"])
                st.session_state["temp_registro"] = {}
            
            st.session_state["form_id"] += 1
            st.session_state["registro_exitoso"] = True
            st.rerun()
    with col_b2:
        if st.button("❌ Cerrar / Revisar datos", use_container_width=True):
            st.rerun()

# ---------------------------------------------------------
# PANTALLA DE INICIO DE SESIÓN
# ---------------------------------------------------------
USUARIOS = st.secrets.get("usuarios", {})

def mostrar_login():
    st.markdown("""
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
    """, unsafe_allow_html=True)

    col_left, col_center, col_right = st.columns([1, 1.8, 1])

    with col_center:
        b64_sec = get_image_base64("logo_secretaria.png")
        b64_gea = get_image_base64("logo_geavig.png")

        img_sec_html = f'<img src="data:image/png;base64,{b64_sec}" alt="Logo">' if b64_sec else '<span style="font-size:45px;">🛡️</span>'
        img_gea_html = f'<img src="data:image/png;base64,{b64_gea}" alt="Logo">' if b64_gea else '<span style="font-size:45px;">⚖️</span>'

        st.markdown(f'<div class="logo-container">{img_sec_html}{img_gea_html}</div>', unsafe_allow_html=True)
        st.markdown("""
            <div class="inst-header">
                <div class="inst-title">SECRETARÍA MUNICIPAL DE SEGURIDAD CIUDADANA Y TRÁNSITO DE BENITO JUÁREZ</div>
                <div class="inst-subtitle">GEAVIG</div>
            </div>
        """, unsafe_allow_html=True)

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
                    for _, row in df.iterrows():
                        smz_val = normalizar(str(row['SMZ']))
                        sec_val = normalizar(str(row[col_sector]))
                        if smz_val and smz_val != "NAN":
                            catalogos["SMZ_SECTOR"][smz_val] = sec_val

                mapeo = {
                    "QUIEN REPORTA": "QUIEN_REPORTA",
                    "PARTICULAR": "PARTICULAR",
                    "MEDIO DE REPORTE": "MEDIO_DE_REPORTE",
                    "RELACION CON EL AGRESOR": "RELACION_CON_EL_AGRESOR",
                    "NACIONALIDAD": "NACIONALIDAD",
                    "ENTIDAD DE ORIGEN": "ENTIDAD_DE_ORIGEN",
                    "MODALIDAD": "MODALIDAD",
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
                        vals = ["EXTRANJERA" if v == "EXTRAJERA" else v for v in vals]
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

fid = st.session_state["form_id"]

# ---------------------------------------------------------
# VISTA PRINCIPAL
# ---------------------------------------------------------
st.title("🛡️ SISTEMA INTEGRAL DE REGISTRO - GEAVIG")

if st.session_state.get("registro_exitoso", False):
    st.success("✅ La información se ha guardado exitosamente y el formulario se ha limpiado.")
    st.session_state["registro_exitoso"] = False

# PANEL DE CONTROL INTERNO PARA CAPTURISTA
with st.expander(f"📥 CONTROL INTERNO DE CAPTURAS (`{len(st.session_state['registros_capturados'])}` folios guardados en esta sesión)", expanded=False):
    if st.session_state["registros_capturados"]:
        df_mis_capturas = pd.DataFrame(st.session_state["registros_capturados"])
        st.dataframe(df_mis_capturas, use_container_width=True)
        
        bytes_excel = generar_excel_bytes(df_mis_capturas)
        st.download_button(
            label="📥 Descargar Mi Excel de Capturas (.xlsx)",
            data=bytes_excel,
            file_name=f"mis_capturas_geavig_{st.session_state['usuario_actual']}_{datetime.date.today()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    else:
        st.info("Aún no has guardado registros durante esta sesión activa.")

if st.session_state["rol_usuario"] == "editor":
    tab1, tab2 = st.tabs(["📋 Formulario Completo", "📊 Coordinación y Exportación"])
else:
    tab1 = st.container()

with tab1:
    st.header("1. Datos Generales y Control de Tiempos")
    
    # LÍNEA 1
    r1_col1, r1_col2, r1_col3, r1_col4 = st.columns(4)
    with r1_col1:
        capturista = st.text_input("Nombre del Capturista", value=st.session_state["nombre_usuario"], disabled=True, key=f"txt_capturista_disabled_{fid}")
    with r1_col2:
        turno = st.selectbox("Turno", ["A", "B", "C"], key=f"sel_turno_{fid}")
    with r1_col3:
        medio_sel = st.selectbox("Medio de Reporte", catalogos["MEDIO_DE_REPORTE"], key=f"sel_medio_{fid}")
        if medio_sel == "OTRO":
            medio_reporte = capturar_texto_validado("Especifique Medio", key=f"txt_medio_esp_{fid}")
        else:
            medio_reporte = medio_sel
    with r1_col4:
        reporte_911 = capturar_texto_validado("Folio / Reporte 911", key=f"txt_reporte_911_{fid}")
        
    # LÍNEA 2
    r2_col1, r2_col2, r2_col3 = st.columns([1, 1, 2])
    with r2_col1:
        fecha_captura = st.date_input("Fecha de Captura", value=datetime.date.today(), disabled=True, key=f"f_cap_{fid}")
    with r2_col2:
        fecha_reporte = st.date_input("Fecha del Reporte", datetime.date.today(), key=f"f_rep_{fid}")
    with r2_col3:
        q_col1, q_col2 = st.columns(2)
        with q_col1:
            quien_rep_sel = st.selectbox("Quién Reporta", catalogos["QUIEN_REPORTA"], key=f"sel_qrep_{fid}")
        with q_col2:
            if quien_rep_sel == "PARTICULAR":
                particular_sel = st.selectbox("Tipo de Particular", catalogos["PARTICULAR"], key=f"sel_part_{fid}")
                if particular_sel == "OTRO":
                    part_esp = capturar_texto_validado("Especifique Particular", key=f"txt_part_esp_{fid}")
                    quien_reporta = f"PARTICULAR - {part_esp}" if part_esp else "PARTICULAR"
                else:
                    quien_reporta = f"PARTICULAR - {particular_sel}"
            elif quien_rep_sel == "OTRO":
                quien_esp = capturar_texto_validado("Especifique Quién Reporta", key=f"txt_quien_esp_{fid}")
                quien_reporta = quien_esp if quien_esp else "OTRO"
            else:
                quien_reporta = quien_rep_sel

    # LÍNEA 3 (TIEMPOS)
    r3_col1, r3_col2, r3_col3, r3_col4 = st.columns(4)
    with r3_col1:
        hora_reporte = st.time_input("Hora del Reporte", datetime.time(0, 0), key=f"hr_rep_{fid}")
    with r3_col2:
        hora_llegada = st.time_input("Hora de Llegada", datetime.time(0, 0), key=f"hr_lleg_{fid}")
    with r3_col3:
        hora_cierre = st.time_input("Hora de Cierre", datetime.time(0, 0), key=f"hr_cier_{fid}")
    with r3_col4:
        dt_llegada = datetime.datetime.combine(fecha_reporte, hora_llegada)
        dt_cierre = datetime.datetime.combine(fecha_reporte, hora_cierre)
        if dt_cierre < dt_llegada:
            dt_cierre += datetime.timedelta(days=1)

        minutos_totales = int((dt_cierre - dt_llegada).total_seconds() / 60)
        if minutos_totales < 0:
            minutos_totales = 0
            
        horas_calc = minutos_totales // 60
        mins_calc = minutos_totales % 60
        tiempo_calculado = f"{horas_calc} HRS {mins_calc} MIN" if horas_calc > 0 else f"{mins_calc} MIN"

        tiempo_atencion = st.text_input("Tiempo de Atención (Automático)", value=tiempo_calculado, disabled=True, key=f"txt_tatencion_{fid}")

    # LÍNEA 4
    r4_col1, r4_col2, r4_col3, r4_col4 = st.columns(4)
    with r4_col1:
        al_mando = capturar_texto_validado("Al Mando", key=f"txt_al_mando_{fid}")
    with r4_col2:
        unidad = capturar_texto_validado("Unidad / Patrulla", key=f"txt_unidad_{fid}")

    st.divider()

    st.header("2. Ubicación de los Hechos")
    u1, u2, u3, u4 = st.columns(4)
    with u1:
        if mapa_sectores:
            smz_seleccionada = st.selectbox("SMZ / Supermanzana / Región", lista_smz, key=f"sel_smz_{fid}")
            smz_key_limpia = normalizar(smz_seleccionada)
            sector_calculado = mapa_sectores.get(smz_key_limpia, mapa_sectores.get(smz_seleccionada, "")) if smz_seleccionada != "SELECCIONAR..." else ""
        else:
            smz_seleccionada = capturar_texto_validado("SMZ / Supermanzana", key=f"txt_smz_{fid}")
            sector_calculado = ""

        manzana = capturar_texto_validado("Manzana", key=f"txt_manzana_{fid}")
        lote = capturar_texto_validado("Lote", key=f"txt_lote_{fid}")

    with u2:
        sector = st.text_input("Sector Asignado (Automático)", value=sector_calculado, disabled=True, key=f"txt_sec_{fid}")
        calle = capturar_texto_validado("Calle", key=f"txt_calle_{fid}")
        colonia = capturar_texto_validado("Colonia / Fraccionamiento", key=f"txt_colonia_{fid}")

    with u3:
        no_ext = capturar_texto_validado("No. Exterior", key=f"txt_no_ext_{fid}")
        referencia = capturar_texto_validado("Referencia del lugar", key=f"txt_referencia_{fid}")

    with u4:
        longitud = capturar_texto_validado("Longitud", key=f"txt_longitud_{fid}")
        latitud = capturar_texto_validado("Latitud", key=f"txt_latitud_{fid}")

    st.divider()

    st.header("3. Datos de la Víctima")
    v1, v2 = st.columns(2)
    
    with v1:
        vic_nombre = capturar_texto_validado("Nombre Completo de la Víctima", key=f"txt_vic_nombre_{fid}")
        
        f1_1, f1_2 = st.columns(2)
        with f1_1:
            vic_edad = st.number_input("Edad Víctima", min_value=0, max_value=120, value=0, key=f"num_vic_edad_{fid}")
        with f1_2:
            vic_sexo = st.selectbox("Sexo Víctima", ["FEMENINO", "MASCULINO", "NO ESPECIFICA"], key=f"sel_vic_sexo_{fid}")
            
        vic_rel_sel = st.selectbox("Relación con el Agresor", catalogos["RELACION_CON_EL_AGRESOR"], key=f"sel_vic_rel_{fid}")
        if vic_rel_sel == "OTRO":
            vic_relacion_agresor = capturar_texto_validado("Especifique Relación con Agresor", key=f"txt_vic_rel_esp_{fid}")
        else:
            vic_relacion_agresor = vic_rel_sel

        # NACIONALIDAD VÍCTIMA
        vic_nac_sel = st.selectbox("Nacionalidad Víctima", catalogos["NACIONALIDAD"], key=f"vic_nac_sel_{fid}")
        if "EXTR" in vic_nac_sel:
            vic_nac_ext = capturar_texto_validado("Especifique País / Nacionalidad Extranjera (Víctima)", key=f"vic_nac_ext_{fid}")
            vic_nacionalidad = f"EXTRANJERA - {vic_nac_ext}" if vic_nac_ext else "EXTRANJERA"
            vic_entidad_origen = "NO APLICA"
        elif vic_nac_sel == "MEXICANA":
            vic_entidad_origen = st.selectbox("Entidad de Origen (Víctima)", ["SELECCIONAR..."] + catalogos["ENTIDAD_DE_ORIGEN"], key=f"vic_ent_sel_{fid}")
            vic_nacionalidad = "MEXICANA"
        else:
            vic_nacionalidad = vic_nac_sel
            vic_entidad_origen = "NO ESPECIFICA"
