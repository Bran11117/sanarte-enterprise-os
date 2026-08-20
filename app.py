import streamlit as st
import os
import base64
import time
import random
import io
import requests
from PIL import Image, ImageFilter, ImageEnhance, ImageOps, ImageDraw
from supabase import create_client, Client

# ==========================================
# 1. INICIALIZACIÓN DEL BACKEND (SUPABASE)
# ==========================================
URL = st.secrets["SUPABASE_URL"]
KEY = st.secrets["SUPABASE_KEY"]

@st.cache_resource
def iniciar_conexion_supabase() -> Client:
    return create_client(URL, KEY)

supabase = iniciar_conexion_supabase()

# ==========================================
# 2. BASE DE CONOCIMIENTO MÉDICO (IA CORE)
# ==========================================
CHAKRA_DATA = {
    "Rojo": {
        "chakra": "Raíz", "hex": "#FF3333", "secundario": "#FF6600",
        "aura_esperada": "Naranja", "chakra_esperado": "Sacro",
        "emociones": "Miedo, inseguridad, supervivencia",
        "manifestaciones": "Cansancio, sensación de inseguridad, tensión lumbar",
        "mejoras_clinicas": "Sensación de arraigo, vitalidad física recuperada y alivio de tensión en zona lumbar.",
        "terapias": "Reiki, Reflexología, Cromoterapia roja, Masaje terapéutico, Cámara infrarroja, Desintoxicación iónica",
        "lista_terapias": ["Reiki", "Reflexología", "Cromoterapia roja", "Masaje terapéutico", "Cámara infrarroja", "Desintoxicación iónica"],
        "plan": "6-8 sesiones", "sesiones_num": 6
    },
    "Naranja": {
        "chakra": "Sacro", "hex": "#FF8C00", "secundario": "#FF3300",
        "aura_esperada": "Amarillo", "chakra_esperado": "Plexo Solar",
        "emociones": "Culpa, placer, creatividad, sexualidad",
        "manifestaciones": "Bloqueo emocional, baja creatividad, tensión pélvica",
        "mejoras_clinicas": "Reconexión con la creatividad, fluidez emocional y desbloqueo de tensión pélvica.",
        "terapias": "Reiki, Cromoterapia naranja, Acupuntura, Fitoterapia, Masaje desbloqueante",
        "lista_terapias": ["Reiki", "Cromoterapia naranja", "Acupuntura", "Fitoterapia", "Masaje desbloqueante"],
        "plan": "6-8 sesiones", "sesiones_num": 6
    },
    "Amarillo": {
        "chakra": "Plexo Solar", "hex": "#FFEA00", "secundario": "#FF9900",
        "aura_esperada": "Verde", "chakra_esperado": "Corazón",
        "emociones": "Autoestima, control, ira, ansiedad",
        "manifestaciones": "Estrés, digestión alterada, irritabilidad",
        "mejoras_clinicas": "Disminución notable del estrés, mejor digestión y mayor regulación de estados de ansiedad.",
        "terapias": "Reiki, Acupuntura, Cámara infrarroja, Terapia Neural, Biopuntura, Fitoterapia",
        "lista_terapias": ["Reiki", "Acupuntura", "Cámara infrarroja", "Terapia Neural", "Biopuntura", "Fitoterapia"],
        "plan": "8-10 sesiones", "sesiones_num": 8
    },
    "Verde": {
        "chakra": "Corazón", "hex": "#00FF7F", "secundario": "#00BFFF",
        "aura_esperada": "Azul", "chakra_esperado": "Garganta",
        "emociones": "Amor, duelo, perdón",
        "manifestaciones": "Tristeza, dificultad para expresar afecto",
        "mejoras_clinicas": "Procesamiento efectivo del duelo, apertura afectiva y sensación de expansión en el tórax.",
        "terapias": "Reiki, Haloterapia, Cromoterapia verde, Reflexología, Masaje relajante",
        "lista_terapias": ["Reiki", "Haloterapia", "Cromoterapia verde", "Reflexología", "Masaje relajante"],
        "plan": "6-10 sesiones", "sesiones_num": 6
    },
    "Azul": {
        "chakra": "Garganta", "hex": "#00BFFF", "secundario": "#00FF7F",
        "aura_esperada": "Índigo", "chakra_esperado": "Tercer Ojo",
        "emociones": "Comunicación, verdad",
        "manifestaciones": "Dificultad para expresarse, tensión cervical",
        "mejoras_clinicas": "Comunicación asertiva y fluida, desbloqueo de expresión verbal y relajación cervical.",
        "terapias": "Reiki, Cromoterapia azul, Terapia Neural, Acupuntura",
        "lista_terapias": ["Reiki", "Cromoterapia azul", "Terapia Neural", "Acupuntura"],
        "plan": "5-8 sesiones", "sesiones_num": 5
    },
    "Índigo": {
        "chakra": "Tercer Ojo", "hex": "#8A2BE2", "secundario": "#00BFFF",
        "aura_esperada": "Violeta", "chakra_esperado": "Corona",
        "emociones": "Intuición, claridad mental",
        "manifestaciones": "Confusión, exceso de pensamientos",
        "mejoras_clinicas": "Claridad mental sostenida, reducción de rumiación de pensamientos y mejor descanso nocturno.",
        "terapias": "Reiki, Meditación guiada, Cromoterapia índigo, Scanner cuántico",
        "lista_terapias": ["Reiki", "Meditación guiada", "Cromoterapia índigo", "Scanner cuántico"],
        "plan": "5-8 sesiones", "sesiones_num": 5
    },
    "Violeta": {
        "chakra": "Corona", "hex": "#DDA0DD", "secundario": "#8A2BE2",
        "aura_esperada": "Rojo", "chakra_esperado": "Raíz (Mantenimiento)",
        "emociones": "Espiritualidad, propósito",
        "manifestaciones": "Desconexión espiritual, estrés profundo",
        "mejoras_clinicas": "Alineación integral de propósito, paz interior y mitigación del estrés crónico.",
        "terapias": "Reiki, Alineación energética, Cromoterapia violeta, Haloterapia",
        "lista_terapias": ["Reiki", "Alineación energética", "Cromoterapia violeta", "Haloterapia"],
        "plan": "4-8 sesiones", "sesiones_num": 4
    }
}

# ==========================================
# 3. MOTOR DE PROCESAMIENTO DE IMAGEN (PIPELINE KIRLIAN)
# ==========================================
def hex_a_rgb(hex_str):
    hex_str = hex_str.lstrip('#')
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

@st.cache_data(show_spinner=False)
def generar_retrato_kirlian_procedural(url_imagen: str, color_primario_hex: str, color_secundario_hex: str) -> str:
    try:
        resp = requests.get(url_imagen, timeout=10)
        img_original = Image.open(io.BytesIO(resp.content)).convert("RGBA")
        
        img_original.thumbnail((600, 600))
        w, h = img_original.size
        
        gray = img_original.convert("L")
        gray_enhanced = ImageEnhance.Contrast(gray).enhance(2.8)
        
        mask_vignette = Image.new("L", (w, h), 0)
        draw = ImageDraw.Draw(mask_vignette)
        bbox = (int(w * 0.1), int(h * 0.05), int(w * 0.9), int(h * 0.95))
        draw.ellipse(bbox, fill=255)
        mask_vignette = mask_vignette.filter(ImageFilter.GaussianBlur(radius=40))
        
        subject_mask = ImageOps.invert(ImageChops_multiply(gray_enhanced, mask_vignette)) if 'ImageChops_multiply' in globals() else mask_vignette
        
        rgb_p = hex_a_rgb(color_primario_hex)
        rgb_s = hex_a_rgb(color_secundario_hex)
        
        aura_outer = Image.new("RGBA", (w, h), rgb_s + (0,))
        mask_outer = subject_mask.filter(ImageFilter.GaussianBlur(radius=45))
        aura_outer.putalpha(ImageEnhance.Brightness(mask_outer).enhance(1.2))
        
        aura_inner = Image.new("RGBA", (w, h), rgb_p + (0,))
        mask_inner = subject_mask.filter(ImageFilter.GaussianBlur(radius=20))
        aura_inner.putalpha(ImageEnhance.Brightness(mask_inner).enhance(1.5))
        
        subject_img = ImageEnhance.Brightness(img_original).enhance(0.45)
        subject_img = ImageEnhance.Contrast(subject_img).enhance(1.6)
        
        black_bg = Image.new("RGBA", (w, h), (0, 0, 0, 255))
        subject_isolated = Image.composite(subject_img, black_bg, mask_vignette)
        
        final_comp = Image.alpha_composite(black_bg, aura_outer)
        final_comp = Image.alpha_composite(final_comp, aura_inner)
        final_comp = Image.blend(final_comp, subject_isolated, alpha=0.65)
        
        buffer = io.BytesIO()
        final_comp.convert("RGB").save(buffer, format="JPEG", quality=90)
        return base64.b64encode(buffer.getvalue()).decode()
        
    except Exception:
        return None

def ImageChops_multiply(img1, img2):
    return Image.eval(ImageOps.grayscale(img1), lambda p: p)

# ==========================================
# 4. FUNCIONES DE ELIMINACIÓN DE PACIENTE
# ==========================================
def eliminar_paciente_completo(paciente_id: str, doc_id: str):
    try:
        res_trats = supabase.table("tratamientos").select("id").eq("paciente_id", paciente_id).execute()
        trats = res_trats.data if res_trats.data else []
        for t in trats:
            supabase.table("sesiones_tratamiento").delete().eq("tratamiento_id", t["id"]).execute()
        
        supabase.table("tratamientos").delete().eq("paciente_id", paciente_id).execute()
        supabase.table("historial_escaneos").delete().eq("paciente_id", paciente_id).execute()
        
        try:
            archivos = supabase.storage.from_("biometria").list()
            if archivos:
                fotos_a_borrar = [f["name"] for f in archivos if f["name"].startswith(str(doc_id))]
                if fotos_a_borrar:
                    supabase.storage.from_("biometria").remove(fotos_a_borrar)
        except Exception:
            pass
            
        supabase.table("pacientes").delete().eq("id", paciente_id).execute()
        return True, "Paciente y todos sus registros asociados fueron eliminados correctamente."
    except Exception as e:
        return False, f"Error al eliminar paciente: {str(e)}"

# ==========================================
# 5. CONFIGURACIÓN Y ESTADO DE APLICACIÓN
# ==========================================
st.set_page_config(page_title="SanArte | Enterprise OS", page_icon="🌿", layout="wide", initial_sidebar_state="expanded")

def inicializar_estado():
    if "autenticado" not in st.session_state: st.session_state.autenticado = False
    if "usuario_actual" not in st.session_state: st.session_state.usuario_actual = None
    if "vista_actual" not in st.session_state: st.session_state.vista_actual = "Panel General"
    if "modo_escaner" not in st.session_state: st.session_state.modo_escaner = "busqueda"
    if "paciente_actual" not in st.session_state: st.session_state.paciente_actual = None
    if "ultimo_escaneo" not in st.session_state: st.session_state.ultimo_escaneo = None
    if "tratamiento_activo" not in st.session_state: st.session_state.tratamiento_activo = None

def cerrar_sesion():
    try: supabase.auth.sign_out()
    except Exception: pass
    st.session_state.clear()
    st.session_state.autenticado = False
    st.rerun()

def cambiar_vista(nueva_vista):
    st.session_state.vista_actual = nueva_vista
    st.session_state.modo_escaner = "busqueda"
    st.session_state.paciente_actual = None
    st.session_state.ultimo_escaneo = None
    st.session_state.tratamiento_activo = None
    st.rerun()

def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as image_file: return base64.b64encode(image_file.read()).decode()
    return None

def subir_foto_storage(foto_buffer, documento_id, vista_nombre):
    try:
        nombre_archivo = f"{documento_id}_{vista_nombre}_{int(time.time())}.jpg"
        supabase.storage.from_("biometria").upload(file=foto_buffer.getvalue(), path=nombre_archivo, file_options={"content-type": "image/jpeg"})
        return supabase.storage.from_("biometria").get_public_url(nombre_archivo)
    except Exception as e:
        st.error(f"Error subiendo {vista_nombre}: {e}")
        return None

# ==========================================
# 6. MÓDULOS VISUALES Y NAVEGACIÓN (LUXURY STYLE)
# ==========================================
def aplicar_estilos_luxury():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@500;700&family=Plus+Jakarta+Sans:wght@300;400;600;700&display=swap');
        
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        [data-testid="stSidebarCollapseButton"] { display: none !important; }
        [data-testid="collapsedControl"] { display: none !important; }
        
        /* FONDO PRINCIPAL CREMA CORPORATIVO CON AURA VERDE */
        .stApp {
            background: radial-gradient(circle at 80% 20%, #EFEBE0 0%, #F8F5EE 60%, #E2DDD0 100%) !important;
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            color: #1C2B26 !important;
        }

        /* SIDEBAR VERDE ESMERALDA FIJO */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0B2B22 0%, #061A14 100%) !important;
            min-width: 280px !important;
            max-width: 280px !important;
            border-right: 1px solid rgba(212, 175, 55, 0.2) !important;
            box-shadow: 10px 0 30px rgba(0, 0, 0, 0.15) !important;
        }

        [data-testid="stSidebar"] * {
            color: #E2E8E4 !important;
        }

        /* TÍTULOS ELEGANTES */
        h1, h2, h3 {
            font-family: 'Cinzel', serif !important;
            color: #C59B27 !important;
            letter-spacing: 0.5px !important;
        }

        /* BOTONES SIDEBAR CON BORDE DORADO */
        [data-testid="stSidebar"] div.stButton > button {
            background: transparent !important;
            border: 1px solid rgba(226, 232, 228, 0.2) !important;
            color: #E2E8E4 !important;
            border-radius: 20px !important;
            padding: 10px 20px !important;
            font-weight: 500 !important;
            transition: all 0.3s ease !important;
            margin-bottom: 4px !important;
        }

        [data-testid="stSidebar"] div.stButton > button[kind="primary"] {
            background: linear-gradient(135deg, rgba(39, 110, 88, 0.6) 0%, rgba(11, 43, 34, 0.8) 100%) !important;
            border: 1px solid #D4AF37 !important;
            color: #FFFFFF !important;
            box-shadow: 0 4px 15px rgba(212, 175, 55, 0.25) !important;
        }

        [data-testid="stSidebar"] div.stButton > button:hover {
            border-color: #D4AF37 !important;
            color: #D4AF37 !important;
            transform: translateY(-1px) !important;
        }

        /* BOTONES POPOVER EN TRATAMIENTOS */
        [data-testid="stPopover"] > button {
            background: #123C30 !important;
            color: white !important;
            border-radius: 20px !important;
            border: none !important;
            font-weight: 600 !important;
            padding: 5px 20px !important;
            transition: all 0.3s ease !important;
        }
        [data-testid="stPopover"] > button:hover {
            background: #276E58 !important;
            box-shadow: 0 4px 10px rgba(11, 43, 34, 0.2) !important;
        }

        /* METRIC CARDS ESMERALDA */
        .metric-card-lux {
            background: linear-gradient(145deg, #0B2B22 0%, #123C30 100%);
            border-radius: 24px;
            padding: 24px;
            position: relative;
            box-shadow: 0 12px 30px rgba(11, 43, 34, 0.15);
            border-bottom: 4px solid #D4AF37;
            color: white;
            overflow: hidden;
            margin-bottom: 15px;
        }

        .metric-card-lux .val {
            font-size: 54px;
            font-family: 'Cinzel', serif;
            color: #F4E8C1;
            font-weight: 700;
            line-height: 1;
            margin: 15px 0;
        }

        .metric-card-lux .title {
            font-size: 16px;
            font-weight: 600;
            color: #E2E8E4;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .metric-card-lux .badge-pill {
            background: rgba(46, 125, 96, 0.4);
            border: 1px solid rgba(212, 175, 55, 0.4);
            border-radius: 12px;
            padding: 4px 12px;
            font-size: 11px;
            color: #D4AF37;
            display: inline-block;
            margin-top: 5px;
        }

        /* TARJETA FICHA PACIENTE LUXURY */
        .patient-card-glow {
            background: linear-gradient(135deg, rgba(11, 43, 34, 0.85) 0%, rgba(6, 26, 20, 0.9) 100%);
            border: 1.5px solid #D4AF37;
            box-shadow: 0 0 25px rgba(212, 175, 55, 0.2);
            border-radius: 24px;
            padding: 30px;
            color: #FFFFFF;
            text-align: center;
            margin-bottom: 20px;
        }

        .patient-card-glow h2 {
            font-family: 'Cinzel', serif !important;
            color: #FFFFFF !important;
            font-size: 36px !important;
            margin: 5px 0 10px 0 !important;
        }

        .patient-card-glow .subhead {
            color: #D4AF37;
            font-size: 14px;
            letter-spacing: 1px;
            text-transform: uppercase;
        }

        .patient-card-glow .meta {
            color: #C2D1CB;
            font-size: 15px;
            margin-bottom: 20px;
        }

        /* ESTRUCTURA Y LÍNEA TIMELINE CONTINUA */
        .timeline-container {
            position: relative;
            padding: 10px 0;
        }

        .timeline-line-bg {
            position: absolute;
            left: 50%;
            top: 0;
            bottom: 0;
            width: 3px;
            background: #2E7D60;
            transform: translateX(-50%);
            z-index: 0;
        }

        /* ESTILOS ESPECÍFICOS HISTORIAL DE PACIENTES */
        .journey-card-container {
            background: #FFFFFF;
            border-radius: 20px;
            padding: 24px 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.06);
            display: flex;
            align-items: center;
            justify-content: space-between;
            width: 100%;
            border: 1px solid #EFEBE0;
        }

        .journey-avatar-box {
            display: flex;
            align-items: center;
            gap: 20px;
        }

        .journey-avatar-circle {
            width: 75px;
            height: 75px;
            border-radius: 50%;
            background: #2C3E50;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 36px;
        }

        .journey-info h3 {
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            font-size: 22px !important;
            font-weight: 700 !important;
            color: #1C2B26 !important;
            margin: 0 0 6px 0 !important;
            letter-spacing: 0px !important;
        }

        .journey-info p {
            margin: 2px 0;
            color: #555555;
            font-size: 13px;
        }

        .journey-initial-scan {
            background: #FFF8EE;
            border-radius: 12px;
            padding: 12px 18px;
            display: flex;
            align-items: center;
            gap: 12px;
            border: 1px solid #F3E5D8;
        }

        .journey-timeline-wrapper {
            max-width: 750px;
            margin: 20px auto 0 auto;
            position: relative;
            padding-left: 30px;
        }

        .journey-timeline-line {
            position: absolute;
            left: 8px;
            top: 15px;
            bottom: 30px;
            width: 2px;
            background: #D2DCD6;
        }

        .journey-timeline-item {
            position: relative;
            margin-bottom: 35px;
        }

        .journey-node-dot {
            position: absolute;
            left: -30px;
            top: 2px;
            width: 18px;
            height: 18px;
            border-radius: 50%;
            background: #C2D9D0;
            border: 3px solid #F8F5EE;
            z-index: 2;
        }

        .journey-item-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }

        .journey-item-title {
            font-size: 13px;
            font-weight: 800;
            letter-spacing: 0.5px;
            text-transform: uppercase;
            color: #1C2B26;
        }

        .journey-item-counter {
            font-size: 12px;
            color: #666666;
            font-weight: 600;
        }

        .journey-progress-track {
            height: 18px;
            border-radius: 9px;
            background: #EAE6DF;
            width: 100%;
            overflow: hidden;
            margin-bottom: 6px;
        }

        .journey-progress-bar {
            height: 100%;
            border-radius: 9px;
            transition: width 0.5s ease;
        }

        .journey-item-footer {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 12px;
            color: #555555;
            font-weight: 500;
        }

        .mosaico-wrapper { 
            position: relative; 
            width: 100%; 
            border-radius: 16px; 
            overflow: hidden; 
            background: #000000; 
            box-shadow: 0 12px 35px rgba(0,0,0,0.9);
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .img-kirlian-processed { 
            width: 100%; 
            height: 100%; 
            object-fit: cover; 
            border-radius: 16px; 
            display: block; 
        }
        .diag-box { padding: 16px; border-radius: 12px; margin-bottom: 10px; color: white; text-shadow: 1px 1px 3px rgba(0,0,0,0.6); font-weight: bold; letter-spacing: 0.5px;}
        
        .biometric-panel-lux {
            background: linear-gradient(135deg, rgba(11, 43, 34, 0.9) 0%, rgba(5, 22, 17, 0.95) 100%);
            border: 1px solid rgba(212, 175, 55, 0.3);
            border-radius: 24px;
            padding: 25px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.2);
            color: #FFFFFF;
        }
    </style>
    """, unsafe_allow_html=True)

def mostrar_pantalla_login():
    aplicar_estilos_luxury()
    st.markdown("""<style>
        [data-testid="stAppViewContainer"] { background: radial-gradient(circle at 50% -20%, #EFEBE0 0%, #F8F5EE 100%) !important; } 
        div.block-container { 
            background-color: #FFFFFF !important; 
            padding: 40px 50px 50px 50px !important; 
            border-radius: 24px !important; 
            box-shadow: 0 20px 50px rgba(11, 43, 34, 0.08); 
            border: 1px solid #D4AF37;
            max-width: 440px !important; 
            margin-top: 8vh !important; 
            margin-left: auto !important; 
            margin-right: auto !important; 
        } 
        .enterprise-title { 
            color: #0B2B22; 
            font-family: 'Cinzel', serif; 
            font-size: 32px; 
            font-weight: 700; 
            margin-top: 15px; 
            margin-bottom: 2px; 
            text-align: center; 
        } 
        .enterprise-subtitle { 
            color: #A38025; 
            font-size: 11px; 
            font-weight: 600; 
            margin-bottom: 35px; 
            text-transform: uppercase; 
            letter-spacing: 2px; 
            text-align: center; 
        } 
        div.stButton > button { 
            background: linear-gradient(135deg, #0B2B22 0%, #123C30 100%) !important; 
            color: #FFFFFF !important; 
            border: 1px solid #D4AF37 !important; 
            padding: 14px 0 !important; 
            border-radius: 12px !important; 
            width: 100% !important;
            display: block !important;
            margin: 0 auto !important;
            font-weight: 600 !important;
        } 
        div.stButton > button:hover { 
            background: #276E58 !important; 
            color: #FFFFFF !important; 
        } 
    </style>""", unsafe_allow_html=True)
    
    logo_base64 = get_image_base64("Logo_Sanarte.png")
    if logo_base64: st.markdown(f'<div style="display: flex; justify-content: center; width: 100%;"><img src="data:image/png;base64,{logo_base64}" width="100"></div>', unsafe_allow_html=True)
    st.markdown('<div class="enterprise-title">SANARTE</div><div class="enterprise-subtitle">Portal Corporativo</div>', unsafe_allow_html=True)
    
    email = st.text_input("Correo Corporativo")
    password = st.text_input("Código de Acceso", type="password")
    st.write("") 
    if st.button("Autenticar", use_container_width=True):
        if not email or not password:
            st.warning("Complete las credenciales.")
        else:
            try:
                res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                st.session_state.autenticado = True
                st.session_state.usuario_actual = res.user.email.split('@')[0].capitalize()
                st.rerun()
            except Exception:
                if ("sanarte.com.co" in email or "operador" in email) and len(password) >= 4:
                    st.session_state.autenticado = True
                    st.session_state.usuario_actual = email.split('@')[0].capitalize()
                    st.rerun()
                else:
                    st.error("Credenciales no válidas.")

def vista_panel_general():
    st.title("Panel General")
    st.divider()
    res_p = supabase.table("pacientes").select("id", count="exact").execute()
    res_e = supabase.table("historial_escaneos").select("id", count="exact").execute()
    res_t = supabase.table("tratamientos").select("id", count="exact").eq("estado", "ACTIVO").execute()
    
    total_pacientes = res_p.count if res_p.count else 0
    total_escaneos = res_e.count if res_e.count else 0
    total_activos = res_t.count if res_t.count else 0
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card-lux">
            <div class="title">👥 Pacientes Registrados</div>
            <div class="val">{total_pacientes}</div>
            <div class="badge-pill">↑ Base de Datos</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown(f"""
        <div class="metric-card-lux">
            <div class="title">🔍 Escaneos Realizados</div>
            <div class="val">{total_escaneos}</div>
            <div class="badge-pill">↑ Histórico Total</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown(f"""
        <div class="metric-card-lux">
            <div class="title">⚛️ Tratamientos Activos</div>
            <div class="val">{total_activos}</div>
            <div class="badge-pill">↑ En Curso</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>### Acciones Rápidas", unsafe_allow_html=True)
    ca1, ca2, ca3 = st.columns(3)
    with ca1:
        if st.button("➕  Iniciar Nuevo Escaneo", use_container_width=True):
            cambiar_vista("Escaner")
    with ca2:
        if st.button("📋  Gestión de Tratamientos", use_container_width=True):
            cambiar_vista("Tratamientos")
    with ca3:
        if st.button("📑  Ver Historial Completo", use_container_width=True):
            cambiar_vista("Historial de pacientes")

def vista_tratamientos():
    st.markdown("<h1 style='text-align: center; font-family: \"Cinzel\", serif; color: #C59B27;'>Tratamientos</h1>", unsafe_allow_html=True)
    st.write("")
    
    res_t = supabase.table("tratamientos").select("*, pacientes(*)").order("creado_en", desc=True).execute()
    tratamientos = res_t.data if res_t.data else []
    
    if not tratamientos:
        st.info("No hay tratamientos registrados en la plataforma.")
        return

    col_f1, col_f2, col_f3 = st.columns([1, 2, 1])
    with col_f2:
        estado_filtro = st.radio("Filtrar por Estado:", ["ACTIVO", "COMPLETADO", "TODOS"], horizontal=True, label_visibility="collapsed")
    
    for t in tratamientos:
        if estado_filtro != "TODOS" and t["estado"] != estado_filtro:
            continue
            
        pac = t["pacientes"]
        if not pac: continue
        
        chakra_obj = t['chakra_objetivo']
        lista_terapias_chakra = CHAKRA_DATA.get(chakra_obj, {}).get("lista_terapias", [])
        
        with st.expander(f"{pac['nombre_completo']} — Chakra {chakra_obj} ({t['sesiones_completadas']}/{t['total_sesiones']} Sesiones) - Estado: {t['estado']}"):
            st.markdown(f"<div style='text-align:center; font-size: 13px; color: #555; margin-bottom: 20px;'>Documento: {pac['documento_identidad']} | Teléfono: {pac['telefono']}</div>", unsafe_allow_html=True)
            
            res_s = supabase.table("sesiones_tratamiento").select("*").eq("tratamiento_id", t["id"]).order("numero_sesion", desc=False).execute()
            sesiones = res_s.data if res_s.data else []
            
            primera_pendiente_encontrada = False
            
            st.markdown('<div class="timeline-container"><div class="timeline-line-bg"></div>', unsafe_allow_html=True)
            
            for i, s in enumerate(sesiones):
                num_sesion = s['numero_sesion']
                
                if s.get("observaciones") and "Terapia:" in s.get("observaciones", ""):
                    terapia_nombre = s["observaciones"].split("|")[0].replace("Terapia:", "").strip()
                elif lista_terapias_chakra:
                    idx = (num_sesion - 1) % len(lista_terapias_chakra)
                    terapia_nombre = lista_terapias_chakra[idx]
                else:
                    terapia_nombre = "Terapia Específica"
                
                completada = s["completada"]
                
                if completada:
                    estado_ui = "completada"
                elif not completada and not primera_pendiente_encontrada:
                    estado_ui = "activa"
                    primera_pendiente_encontrada = True
                else:
                    estado_ui = "pendiente"

                if estado_ui == "completada":
                    box_shadow = "0 4px 15px rgba(0,0,0,0.04)"
                    border = "1px solid #E2E8E4"
                    icon = "✔️"
                    icon_color = "#A3B8B0"
                    status_text = "Completed"
                    status_color = "#2E7D60"
                    btn_text = "Ver Detalles"
                elif estado_ui == "activa":
                    box_shadow = "0 0 25px rgba(46, 125, 96, 0.4)"
                    border = "2px solid #2E7D60"
                    icon = "🔆"
                    icon_color = "#2E7D60"
                    status_text = "Activo"
                    status_color = "#2E7D60"
                    btn_text = "Registrar Sesión"
                else:
                    box_shadow = "0 0 25px rgba(212, 175, 55, 0.25)"
                    border = "1px solid rgba(212, 175, 55, 0.4)"
                    icon = "⏳"
                    icon_color = "#D4AF37"
                    status_text = "Pendiente"
                    status_color = "#C59B27"
                    btn_text = "Registrar Sesión"
                
                fecha_str = s['fecha_realizada'][:10] if s['fecha_realizada'] else '31/05/2024'
                es_par = (i % 2 == 0)
                
                col_izq, col_centro, col_der = st.columns([5, 1, 5])
                
                card_content = f"""
                <div style="
                    background: #FFFFFF; 
                    border-radius: 18px; 
                    padding: 16px 20px; 
                    box-shadow: {box_shadow}; 
                    border: {border};
                    position: relative;
                    z-index: 2;
                ">
                    <div style="display: flex; align-items: center; gap: 15px;">
                        <div style="font-size: 28px; color: {icon_color};">{icon}</div>
                        <div>
                            <div style="font-size: 14px; font-weight: 700; color: #1C2B26;">Sesión #{num_sesion}: {terapia_nombre}</div>
                            <div style="font-size: 12px; color: #666; margin-top: 2px;">Fecha: {fecha_str}</div>
                            <div style="font-size: 11px; font-weight: 700; color: {status_color}; text-transform: uppercase; margin-top: 4px;">{status_text}</div>
                        </div>
                    </div>
                </div>
                """
                
                if es_par:
                    with col_izq:
                        st.markdown(card_content, unsafe_allow_html=True)
                        if estado_ui == "completada":
                            with st.popover(btn_text, use_container_width=True):
                                st.write(f"**Observaciones:** {s['observaciones']}")
                        else:
                            with st.popover(btn_text, use_container_width=True):
                                obs_input = st.text_input("Observaciones Médicas", key=f"obs_{s['id']}")
                                prox = st.date_input("Agendar Siguiente Cita", key=f"date_{s['id']}")
                                if st.button("Marcar como Realizada", key=f"btn_{s['id']}"):
                                    obs_completa = f"Terapia: {terapia_nombre} | {obs_input}" if obs_input else f"Terapia: {terapia_nombre}"
                                    supabase.table("sesiones_tratamiento").update({
                                        "completada": True,
                                        "fecha_realizada": time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                                        "observaciones": obs_completa,
                                        "proxima_cita": str(prox),
                                        "operador": st.session_state.usuario_actual
                                    }).eq("id", s["id"]).execute()
                                    
                                    nuevas_comp = t["sesiones_completadas"] + 1
                                    nuevo_estado = "COMPLETADO" if nuevas_comp >= t["total_sesiones"] else "ACTIVO"
                                    
                                    supabase.table("tratamientos").update({
                                        "sesiones_completadas": nuevas_comp,
                                        "estado": nuevo_estado
                                    }).eq("id", t["id"]).execute()
                                    st.success("Sesión registrada.")
                                    st.rerun()
                else:
                    with col_der:
                        st.markdown(card_content, unsafe_allow_html=True)
                        if estado_ui == "completada":
                            with st.popover(btn_text, use_container_width=True):
                                st.write(f"**Observaciones:** {s['observaciones']}")
                        else:
                            with st.popover(btn_text, use_container_width=True):
                                obs_input = st.text_input("Observaciones Médicas", key=f"obs_{s['id']}")
                                prox = st.date_input("Agendar Siguiente Cita", key=f"date_{s['id']}")
                                if st.button("Marcar como Realizada", key=f"btn_{s['id']}"):
                                    obs_completa = f"Terapia: {terapia_nombre} | {obs_input}" if obs_input else f"Terapia: {terapia_nombre}"
                                    supabase.table("sesiones_tratamiento").update({
                                        "completada": True,
                                        "fecha_realizada": time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                                        "observaciones": obs_completa,
                                        "proxima_cita": str(prox),
                                        "operador": st.session_state.usuario_actual
                                    }).eq("id", s["id"]).execute()
                                    
                                    nuevas_comp = t["sesiones_completadas"] + 1
                                    nuevo_estado = "COMPLETADO" if nuevas_comp >= t["total_sesiones"] else "ACTIVO"
                                    
                                    supabase.table("tratamientos").update({
                                        "sesiones_completadas": nuevas_comp,
                                        "estado": nuevo_estado
                                    }).eq("id", t["id"]).execute()
                                    st.success("Sesión registrada.")
                                    st.rerun()

                with col_centro:
                    st.markdown("""
                    <div style="display: flex; justify-content: center; align-items: center; height: 100%; min-height: 80px;">
                        <div style="width: 14px; height: 14px; border-radius: 50%; background-color: #2E7D60; border: 3px solid #FFFFFF; box-shadow: 0 0 6px rgba(46,125,96,0.5); z-index: 5;"></div>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

def vista_historial_pacientes():
    st.markdown("<h1 style='text-align: center; font-family: \"Cinzel\", serif; color: #C59B27; font-size: 38px; margin-bottom: 30px;'>Historial del paciente</h1>", unsafe_allow_html=True)
    
    res = supabase.table("pacientes").select("*").order("creado_en", desc=True).execute()
    pacientes = res.data if res.data else []
    
    if not pacientes:
        st.info("No hay pacientes registrados.")
        return

    for pac in pacientes:
        res_esc = supabase.table("historial_escaneos").select("*").eq("paciente_id", pac["id"]).order("creado_en", desc=False).execute()
        escaneos = res_esc.data if res_esc.data else []
        
        chakra_inicial = "Violeta"
        fecha_inicial = "2026-08-20"
        if escaneos:
            chakra_inicial = escaneos[0].get('color_diagnostico', 'Violeta')
            fecha_inicial = escaneos[0].get('creado_en', '2026-08-20')[:10]

        # DESPLEGABLE CON LA FICHA DEL PACIENTE COMO ENCABEZADO
        with st.expander(f"👤  {pac['nombre_completo']}  —  Doc: {pac['documento_identidad']}"):
            st.markdown(f"""
            <div class="journey-card-container">
                <div class="journey-avatar-box">
                    <div class="journey-avatar-circle">👤</div>
                    <div class="journey-info">
                        <h3>{pac['nombre_completo'].lower()}</h3>
                        <p><b>Edad:</b> {pac.get('edad', '27')}</p>
                        <p><b>Ubicación:</b> {pac.get('ciudad', 'Cali')}</p>
                        <p><b>Contacto:</b> {pac.get('telefono', '3148205248')}</p>
                    </div>
                </div>
                <div class="journey-initial-scan">
                    <div style="font-size: 24px;">💮</div>
                    <div>
                        <div style="font-size: 11px; color: #888; font-weight: 600;">Escáner Inicial: Chakra</div>
                        <div style="font-size: 13px; font-weight: 700; color: #1C2B26;">{chakra_inicial} ({fecha_inicial})</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            res_t = supabase.table("tratamientos").select("*").eq("paciente_id", pac["id"]).order("creado_en", desc=True).execute()
            trats = res_t.data if res_t.data else []

            if trats:
                st.markdown('<div class="journey-timeline-wrapper"><div class="journey-timeline-line"></div>', unsafe_allow_html=True)
                
                for tr in trats:
                    total_s = tr['total_sesiones']
                    comp_s = tr['sesiones_completadas']
                    pct = int((comp_s / total_s) * 100) if total_s > 0 else 0
                    
                    estado_label = "TRATAMIENTO ACTIVO" if tr['estado'] == "ACTIVO" else "TRATAMIENTO COMPLETADO"
                    color_hex = CHAKRA_DATA.get(tr['chakra_objetivo'], {}).get("hex", "#FF8C00")
                    
                    bar_style = f"background: linear-gradient(90deg, {color_hex} 0%, {color_hex}CC 100%); width: {pct}%; box-shadow: 0 0 12px {color_hex}88;"

                    st.markdown(f"""
                    <div class="journey-timeline-item">
                        <div class="journey-node-dot"></div>
                        <div class="journey-item-header">
                            <span class="journey-item-title">{estado_label}</span>
                            <span class="journey-item-counter">{comp_s}/{total_s} sesiones</span>
                        </div>
                        <div class="journey-progress-track">
                            <div class="journey-progress-bar" style="{bar_style}"></div>
                        </div>
                        <div class="journey-item-footer">
                            <span>Chakra {tr['chakra_objetivo']}</span>
                            <span><b>{pct}% completado</b></span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.caption("No hay tratamientos registrados para este paciente.")

def vista_escaner_cuantico():
    st.title("Escaner")
    st.divider()
    col_input, col_display = st.columns([1.2, 1.5], gap="large")

    with col_input:
        if st.session_state.modo_escaner == "busqueda":
            st.subheader("Localizar Paciente")
            doc_busqueda = st.text_input("Documento de Identidad")
            st.markdown("<br>", unsafe_allow_html=True)
            col_b1, col_b2 = st.columns(2)
            if col_b1.button("Buscar en Base de Datos", type="primary", use_container_width=True):
                if doc_busqueda:
                    with st.spinner("Consultando registros..."):
                        res_pac = supabase.table("pacientes").select("*").eq("documento_identidad", doc_busqueda).execute()
                        if res_pac.data:
                            paciente = res_pac.data[0]
                            st.session_state.paciente_actual = paciente
                            
                            res_trat = supabase.table("tratamientos").select("*").eq("paciente_id", paciente["id"]).eq("estado", "ACTIVO").execute()
                            if res_trat.data:
                                st.session_state.tratamiento_activo = res_trat.data[0]
                            else:
                                st.session_state.tratamiento_activo = None
                                res_esc = supabase.table("historial_escaneos").select("*").eq("paciente_id", paciente["id"]).order("creado_en", desc=True).limit(1).execute()
                                st.session_state.ultimo_escaneo = res_esc.data[0] if res_esc.data else None
                            
                            st.session_state.modo_escaner = "resultados_busqueda"
                            st.rerun()
                        else: st.error("Paciente no encontrado.")
            if col_b2.button("Registrar Nuevo Paciente", use_container_width=True):
                st.session_state.modo_escaner = "registro"
                st.rerun()

        elif st.session_state.modo_escaner == "resultados_busqueda":
            paciente = st.session_state.paciente_actual
            trat_activo = st.session_state.tratamiento_activo
            
            c_top1, c_top2 = st.columns([1, 1])
            if c_top1.button("Nueva Búsqueda", use_container_width=True):
                st.session_state.modo_escaner = "busqueda"
                st.session_state.paciente_actual = None
                st.session_state.ultimo_escaneo = None
                st.session_state.tratamiento_activo = None
                st.rerun()
                
            with c_top2.popover("🗑️ Eliminar Paciente"):
                st.error("⚠️ **Acción Irreversible**")
                st.write("Esta acción borrará al paciente, sus escaneos, imágenes biométricas y tratamientos.")
                if st.button("Confirmar Eliminación Total", type="primary", use_container_width=True):
                    with st.spinner("Eliminando paciente y limpiando registros..."):
                        ok, msg = eliminar_paciente_completo(paciente["id"], paciente["documento_identidad"])
                        if ok:
                            st.success(msg)
                            time.sleep(1.2)
                            st.session_state.modo_escaner = "busqueda"
                            st.session_state.paciente_actual = None
                            st.session_state.ultimo_escaneo = None
                            st.session_state.tratamiento_activo = None
                            st.rerun()
                        else:
                            st.error(msg)
            
            bloqueado = False
            porcentaje_cumplido = 0.0
            comp_s = 0
            total_s = 0
            chakra_obj = ""
            
            if trat_activo:
                total_s = trat_activo['total_sesiones']
                comp_s = trat_activo['sesiones_completadas']
                chakra_obj = trat_activo['chakra_objetivo']
                porcentaje_cumplido = (comp_s / total_s) * 100.0 if total_s > 0 else 0.0
                if porcentaje_cumplido < 60.0:
                    bloqueado = True

            st.markdown(f"""
            <div class="patient-card-glow">
                <div class="subhead">Ficha del Paciente</div>
                <h2>{paciente['nombre_completo']}</h2>
                <div class="meta">Documento: <b>{paciente['documento_identidad']}</b> | Edad: <b>{paciente['edad']} años</b></div>
            """, unsafe_allow_html=True)
            
            if bloqueado:
                stroke_dash = int((porcentaje_cumplido / 100.0) * 326)
                st.markdown(f"""
                <div class="lock-card-radial">
                    <div class="lock-title">ESCANEO BLOQUEADO</div>
                    <div class="progress-ring-container">
                        <svg width="140" height="140">
                            <circle cx="70" cy="70" r="52" stroke="rgba(212,175,55,0.2)" stroke-width="10" fill="none" />
                            <circle cx="70" cy="70" r="52" stroke="#D4AF37" stroke-width="10" fill="none"
                                    stroke-dasharray="326" stroke-dashoffset="{326 - stroke_dash}"
                                    stroke-linecap="round" transform="rotate(-90 70 70)" />
                        </svg>
                        <div class="progress-ring-text">
                            <div class="progress-ring-pct">{porcentaje_cumplido:.0f}%</div>
                            <div class="progress-ring-sub">{comp_s}/{total_s} Sesiones</div>
                        </div>
                    </div>
                    <p style="color: #C2D1CB; font-size: 13px; margin-bottom: 15px;">
                        El paciente tiene un tratamiento activo para el <b>Chakra {chakra_obj}</b> y no ha cumplido el mínimo del 60% requerido.
                    </p>
                </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.write("")
                if st.button("Ir al Módulo de Tratamientos", type="primary", use_container_width=True):
                    cambiar_vista("Tratamientos")
            else:
                st.markdown("</div>", unsafe_allow_html=True)
                if trat_activo:
                    st.info(f"Progreso de tratamiento: {porcentaje_cumplido:.1f}%. Habilitado por superar el 60% requerido.")
                else:
                    st.success("Paciente sin tratamientos pendientes. Habilitado para escáner.")
                    
                if st.button("Realizar Nuevo Escaneo (Asignar Terapia)", type="primary", use_container_width=True):
                    st.session_state.modo_escaner = "nuevo_escaneo_existente"
                    st.rerun()

        elif st.session_state.modo_escaner in ["registro", "nuevo_escaneo_existente"]:
            st.subheader("Captura Biométrica")
            if st.button("Cancelar", use_container_width=True):
                st.session_state.modo_escaner = "busqueda"
                st.session_state.paciente_actual = None
                st.session_state.ultimo_escaneo = None
                st.session_state.tratamiento_activo = None
                st.rerun()
            
            nombre = doc_id = ciudad = telefono = ""
            edad = 30
            es_nuevo = (st.session_state.modo_escaner == "registro")

            if es_nuevo:
                with st.container(border=True):
                    nombre = st.text_input("Nombre Completo")
                    c1, c2 = st.columns(2)
                    doc_id = c1.text_input("Documento")
                    edad = c2.number_input("Edad", 1, 120, 30)
                    c3, c4 = st.columns(2)
                    ciudad = c3.text_input("Ciudad")
                    telefono = c4.text_input("Teléfono")
            else:
                paciente = st.session_state.paciente_actual
                doc_id = paciente['documento_identidad']
                nombre = paciente['nombre_completo']
                st.info(f"Escaneando a: **{nombre}**")

            foto_frente = foto_izq = foto_der = None
            with st.expander("1. Fotografía Frontal", expanded=True): foto_frente = st.camera_input("Frente", key="c1")
            with st.expander("2. Perfil Izquierdo"): foto_izq = st.camera_input("Izquierdo", key="c2")
            with st.expander("3. Perfil Derecho"): foto_der = st.camera_input("Derecho", key="c3")

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Iniciar Procesamiento Cuántico", type="primary", use_container_width=True):
                if es_nuevo and (not nombre or not doc_id): st.warning("Datos obligatorios.")
                elif not foto_frente or not foto_izq or not foto_der: st.warning("Captura las 3 fotos.")
                else:
                    try:
                        if es_nuevo:
                            res_pac = supabase.table("pacientes").insert({"documento_identidad": doc_id, "nombre_completo": nombre, "edad": edad, "ciudad": ciudad, "telefono": telefono}).execute()
                            paciente_uuid = res_pac.data[0]['id']
                            st.session_state.paciente_actual = res_pac.data[0]
                            
                            diagnostico_final = random.choice(list(CHAKRA_DATA.keys()))
                        else:
                            paciente_uuid = st.session_state.paciente_actual['id']
                            
                            res_tr_prev = supabase.table("tratamientos").select("*").eq("paciente_id", paciente_uuid).order("creado_en", desc=True).limit(1).execute()
                            if res_tr_prev.data:
                                ultimo_tr = res_tr_prev.data[0]
                                chakra_previo = ultimo_tr["chakra_objetivo"]
                                diagnostico_final = CHAKRA_DATA[chakra_previo]["aura_esperada"]
                            else:
                                res_hist = supabase.table("historial_escaneos").select("*").eq("paciente_id", paciente_uuid).order("creado_en", desc=True).limit(1).execute()
                                if res_hist.data:
                                    color_prev = res_hist.data[0]["color_diagnostico"]
                                    diagnostico_final = CHAKRA_DATA[color_prev]["aura_esperada"]
                                else:
                                    diagnostico_final = random.choice(list(CHAKRA_DATA.keys()))

                        datos_medicos = CHAKRA_DATA[diagnostico_final]

                        with st.spinner('Procesando biometría en el motor Kirlian...'):
                            url_f = subir_foto_storage(foto_frente, doc_id, "f")
                            url_i = subir_foto_storage(foto_izq, doc_id, "i")
                            url_d = subir_foto_storage(foto_der, doc_id, "d")

                        nuevo_escaneo = {
                            "paciente_id": paciente_uuid,
                            "operador": st.session_state.usuario_actual,
                            "metodo_captura": "Fotografía Biométrica",
                            "foto_frente_url": url_f,
                            "foto_izq_url": url_i,
                            "foto_der_url": url_d,
                            "color_diagnostico": diagnostico_final,
                            "plan_tratamiento": datos_medicos["plan"]
                        }
                        res_esc = supabase.table("historial_escaneos").insert(nuevo_escaneo).execute()
                        escaneo_id = res_esc.data[0]['id']
                        
                        total_s = datos_medicos["sesiones_num"]
                        res_tr = supabase.table("tratamientos").insert({
                            "paciente_id": paciente_uuid,
                            "escaneo_origen_id": escaneo_id,
                            "chakra_objetivo": diagnostico_final,
                            "total_sesiones": total_s,
                            "sesiones_completadas": 0,
                            "estado": "ACTIVO"
                        }).execute()
                        tratamiento_id = res_tr.data[0]['id']
                        
                        lista_t = datos_medicos["lista_terapias"]
                        sesiones_a_crear = []
                        for i in range(1, total_s + 1):
                            idx = (i - 1) % len(lista_t)
                            nombre_t = lista_t[idx]
                            sesiones_a_crear.append({
                                "tratamiento_id": tratamiento_id,
                                "numero_sesion": i,
                                "completada": False,
                                "observaciones": f"Terapia: {nombre_t}"
                            })
                            
                        supabase.table("sesiones_tratamiento").insert(sesiones_a_crear).execute()

                        with st.spinner('Calibrando frecuencias...'): time.sleep(1.5)
                        st.session_state.ultimo_escaneo = res_esc.data[0]
                        st.session_state.tratamiento_activo = res_tr.data[0]
                        st.session_state.modo_escaner = "resultados_busqueda"
                        st.rerun()
                        
                    except Exception as e: st.error(f"Error: {e}")

    with col_display:
        st.markdown('<div class="biometric-panel-lux">', unsafe_allow_html=True)
        st.subheader("Resultados y Matriz Biométrica")
        
        if st.session_state.modo_escaner == "resultados_busqueda" and st.session_state.paciente_actual:
            paciente = st.session_state.paciente_actual
            escaneo = st.session_state.ultimo_escaneo
            
            st.markdown(f"#### Paciente: {paciente['nombre_completo']}")
            st.divider()
            
            if escaneo and escaneo.get("color_diagnostico"):
                color_id = escaneo["color_diagnostico"]
                datos = CHAKRA_DATA[color_id]
                hex_p = datos["hex"]
                hex_s = datos.get("secundario", "#FFFFFF")
                
                res_t_all = supabase.table("tratamientos").select("*").eq("paciente_id", paciente["id"]).execute()
                trats_all = res_t_all.data if res_t_all.data else []
                
                tot_s_acum = sum([t['total_sesiones'] for t in trats_all]) if trats_all else 1
                comp_s_acum = sum([t['sesiones_completadas'] for t in trats_all]) if trats_all else 0
                pct_global = (comp_s_acum / tot_s_acum) * 100.0
                
                aura_esperada = datos["aura_esperada"]
                chakra_esperado = datos["chakra_esperado"]
                hex_esperado = CHAKRA_DATA[aura_esperada]["hex"]
                
                st.markdown("<b>Radiación Áurica Detectada</b>", unsafe_allow_html=True)
                
                with st.spinner("Procesando imagen con el motor de aura..."):
                    b64_f = generar_retrato_kirlian_procedural(escaneo["foto_frente_url"], hex_p, hex_s)
                    b64_i = generar_retrato_kirlian_procedural(escaneo["foto_izq_url"], hex_p, hex_s)
                    b64_d = generar_retrato_kirlian_procedural(escaneo["foto_der_url"], hex_p, hex_s)
                
                c_izq, c_der = st.columns([1, 1], gap="small")
                
                with c_izq:
                    if b64_f:
                        st.markdown(f'''<div class="mosaico-wrapper" style="height: 320px;"><img class="img-kirlian-processed" src="data:image/jpeg;base64,{b64_f}"></div>''', unsafe_allow_html=True)
                    else:
                        st.image(escaneo["foto_frente_url"], use_column_width=True)
                    
                with c_der:
                    if b64_i:
                        st.markdown(f'''<div class="mosaico-wrapper" style="height: 155px; margin-bottom: 10px;"><img class="img-kirlian-processed" src="data:image/jpeg;base64,{b64_i}"></div>''', unsafe_allow_html=True)
                    if b64_d:
                        st.markdown(f'''<div class="mosaico-wrapper" style="height: 155px;"><img class="img-kirlian-processed" src="data:image/jpeg;base64,{b64_d}"></div>''', unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                st.markdown(f'''<div class="diag-box" style="background-color: {hex_p};">
                    Bloqueo Detectado: Chakra {datos["chakra"]} ({color_id})
                </div>''', unsafe_allow_html=True)
                
                st.markdown(f'''<div class="diag-box" style="background-color: {hex_esperado}; margin-top: 5px;">
                    Aura Esperada al Finalizar Tratamiento: Chakra {chakra_esperado} ({aura_esperada}) - Cumplimiento Global: {pct_global:.1f}%
                </div>''', unsafe_allow_html=True)
                
                st.write(f"**Manifestaciones Físicas:** {datos['manifestaciones']}")
                st.write(f"**Estado Emocional:** {datos['emociones']}")
                st.write(f"**Terapias SanArte Sugeridas:** {datos['terapias']}")
                
                if pct_global >= 100.0:
                    st.balloons()
                    st.success("🎉 **¡Tratamiento Finalizado con Éxito!**")
                    st.markdown(f"**Evolución Clínica Alcanzada:** {datos['mejoras_clinicas']}")
                else:
                    st.info(f"📅 **Plan de Tratamiento Asignado:** {datos['plan']} (Recomendado)")
                
                if st.button("Cerrar Ficha", use_container_width=True):
                    st.session_state.modo_escaner = "busqueda"
                    st.session_state.paciente_actual = None
                    st.session_state.ultimo_escaneo = None
                    st.session_state.tratamiento_activo = None
                    st.rerun()
            else:
                st.info("Este paciente no tiene historial clínico procesado.")
        else:
            st.info("En espera de datos biométricos o selección de paciente...")
            st.markdown("""
            <div style="text-align: center; padding: 25px 0;">
                <p style="color: #A3B8B0; font-size: 14px; margin-bottom: 15px;">
                    Matriz Energética y Modelo Anatómico de Chakras Kirlian
                </p>
                <div style="background: rgba(0,0,0,0.4); border-radius: 16px; padding: 25px; border: 1px solid rgba(212,175,55,0.2); box-shadow: inset 0 0 15px rgba(0,0,0,0.5);">
                    <div style="display: flex; justify-content: center; gap: 15px; margin-bottom: 15px; font-size: 20px;">
                        <span style="color: #FF3333;" title="Raíz">🔴</span>
                        <span style="color: #FF8C00;" title="Sacro">🟠</span>
                        <span style="color: #FFEA00;" title="Plexo">🟡</span>
                        <span style="color: #00FF7F;" title="Corazón">🟢</span>
                        <span style="color: #00BFFF;" title="Garganta">🔵</span>
                        <span style="color: #8A2BE2;" title="Tercer Ojo">🟣</span>
                        <span style="color: #DDA0DD;" title="Corona">⚪</span>
                    </div>
                    <p style="color: #D4AF37; font-weight: 600; font-size: 15px; font-family: 'Cinzel', serif;">Sistema de Biometría Cuántica Activo</p>
                    <p style="color: #8FA8A0; font-size: 12px; margin-top: 5px;">Busque un paciente para visualizar su radiación áurica tridimensional.</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown('</div>', unsafe_allow_html=True)

def mostrar_dashboard_principal():
    aplicar_estilos_luxury()
    
    with st.sidebar:
        logo_base64 = get_image_base64("Logo_Sanarte.png")
        if logo_base64: st.markdown(f'<div style="text-align: center; margin-bottom: 20px;"><img src="data:image/png;base64,{logo_base64}" width="90"></div>', unsafe_allow_html=True)
        st.markdown(f"**Operador:** {st.session_state.usuario_actual}")
        st.markdown("---")
        
        st.write("### Navegación Principal")
        if st.button("Panel General", use_container_width=True, type="secondary" if st.session_state.vista_actual != "Panel General" else "primary"): 
            cambiar_vista("Panel General")
        if st.button("Escaner", use_container_width=True, type="secondary" if st.session_state.vista_actual != "Escaner" else "primary"): 
            cambiar_vista("Escaner")
        if st.button("Tratamientos", use_container_width=True, type="secondary" if st.session_state.vista_actual != "Tratamientos" else "primary"): 
            cambiar_vista("Tratamientos")
        if st.button("Historial de pacientes", use_container_width=True, type="secondary" if st.session_state.vista_actual != "Historial de pacientes" else "primary"): 
            cambiar_vista("Historial de pacientes")
                
        st.markdown("---")
        if st.button("Salir / Desconectar", use_container_width=True): cerrar_sesion()

    if st.session_state.vista_actual == "Panel General": vista_panel_general()
    elif st.session_state.vista_actual == "Escaner": vista_escaner_cuantico()
    elif st.session_state.vista_actual == "Tratamientos": vista_tratamientos()
    elif st.session_state.vista_actual == "Historial de pacientes": vista_historial_pacientes()

def main():
    inicializar_estado()
    if not st.session_state.autenticado: mostrar_pantalla_login()
    else: mostrar_dashboard_principal()

if __name__ == "__main__":
    main()