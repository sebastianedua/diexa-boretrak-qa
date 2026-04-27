from __future__ import annotations

import io
import re
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['font.family'] = 'sans-serif'
matplotlib.rcParams['font.sans-serif'] = ['Segoe UI', 'Calibri', 'Arial', 'DejaVu Sans']
import PyPDF2

try:
    import pdfplumber
    PDFPLUMBER_OK = True
except Exception:
    PDFPLUMBER_OK = False

OCR_OK = False
OCR_IMPORT_ERROR = ""
TESSERACT_PATH = ""
try:
    import fitz  # PyMuPDF
    import pytesseract
    from PIL import Image, ImageOps, ImageFilter

    # Auto-detección de Tesseract en rutas comunes de Windows
    import os as _os
    _tesseract_candidates = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        _os.path.expandvars(r"%LOCALAPPDATA%\Programs\Tesseract-OCR\tesseract.exe"),
        _os.path.expandvars(r"%USERPROFILE%\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"),
        r"C:\Tesseract-OCR\tesseract.exe",
        r"D:\Program Files\Tesseract-OCR\tesseract.exe",
    ]
    for _path in _tesseract_candidates:
        if _os.path.isfile(_path):
            pytesseract.pytesseract.tesseract_cmd = _path
            TESSERACT_PATH = _path
            break

    # Verificar que Tesseract realmente funciona
    try:
        pytesseract.get_tesseract_version()
        OCR_OK = True
    except Exception as _te:
        OCR_OK = False
        OCR_IMPORT_ERROR = f"Tesseract no encontrado. Instale desde https://github.com/UB-Mannheim/tesseract/wiki"
except Exception as e:
    OCR_IMPORT_ERROR = str(e)
    OCR_OK = False

# =============================================================================
# VERSIÓN Y CONSTANTES
# =============================================================================
APP_VERSION = "10.0"
APP_NAME = "DIEXA · Boretrak QA"
APP_FULL_NAME = "Análisis de Chimeneas y Control de Calidad Boretrak"
APP_CREDIT = "Herramienta creada por Sebastián Zúñiga Leyton – Ingeniero Civil de Minas"

# =============================================================================
# PALETA CORPORATIVA DIEXA
# =============================================================================
DIEXA = {
    "primary":       "#00275d",   # Azul corporativo oscuro
    "primary_light": "#00a2e5",   # Azul corporativo claro
    "dark":          "#071529",   # Fondo muy oscuro
    "teal":          "#014768",   # Teal oscuro
    "blue":          "#0d60b9",   # Azul medio
    "blue_link":     "#0077ca",   # Azul enlaces
    "blue_bright":   "#21a5ff",   # Azul brillante / acento
    "neutral_dark":  "#333333",   # Texto principal
    "neutral_mid":   "#505760",   # Texto secundario
    "neutral_light": "#d8d9db",   # Bordes y fondos claros
    "white":         "#ffffff",
    "bg_page":       "#f4f6f8",   # Fondo general
    "bg_card":       "#ffffff",   # Fondo tarjetas
    "success":       "#1a7a3a",   # Verde sobrio
    "warning":       "#b8860b",   # Ámbar oscuro
    "danger":        "#a22020",   # Rojo sobrio
    "gray_light":    "#e9ecef",   # Fondo sutil
}

# =============================================================================
# ESTILOS CSS CORPORATIVOS
# =============================================================================
CORPORATE_CSS = f"""
<style>
    /* ── Fuentes ── */
    @import url('https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@300;400;600;700&display=swap');

    html, body, [class*="st-"] {{
        font-family: 'Source Sans 3', 'Segoe UI', Calibri, Arial, sans-serif;
    }}

    /* ── Fondo general ── */
    .stApp {{
        background-color: {DIEXA['bg_page']};
    }}

    /* ── Header corporativo ── */
    .diexa-header {{
        background: linear-gradient(135deg, {DIEXA['primary']} 0%, {DIEXA['dark']} 100%);
        padding: 1.5rem 2rem;
        border-radius: 0 0 12px 12px;
        margin: -1rem -1rem 1.5rem -1rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 1rem;
    }}
    .diexa-header-title {{
        color: {DIEXA['white']};
        font-size: 1.6rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        margin: 0;
        line-height: 1.3;
    }}
    .diexa-header-subtitle {{
        color: {DIEXA['primary_light']};
        font-size: 0.92rem;
        font-weight: 400;
        margin: 0.15rem 0 0 0;
        letter-spacing: 0.3px;
    }}
    .diexa-header-badge {{
        background: rgba(255,255,255,0.12);
        color: {DIEXA['primary_light']};
        font-size: 0.75rem;
        font-weight: 600;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        border: 1px solid rgba(255,255,255,0.15);
        letter-spacing: 0.5px;
    }}

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {DIEXA['primary']} 0%, {DIEXA['dark']} 100%);
    }}
    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] .stCaption,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] p {{
        color: {DIEXA['white']} !important;
    }}
    section[data-testid="stSidebar"] .stSlider label {{
        color: {DIEXA['neutral_light']} !important;
    }}
    section[data-testid="stSidebar"] hr {{
        border-color: rgba(255,255,255,0.15);
    }}
    section[data-testid="stSidebar"] .stNumberInput label,
    section[data-testid="stSidebar"] .stCheckbox label {{
        color: {DIEXA['neutral_light']} !important;
    }}

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 0;
        background: {DIEXA['white']};
        border-radius: 8px;
        padding: 4px;
        border: 1px solid {DIEXA['neutral_light']};
    }}
    .stTabs [data-baseweb="tab"] {{
        border-radius: 6px;
        padding: 0.5rem 1.2rem;
        font-weight: 600;
        font-size: 0.88rem;
        color: {DIEXA['neutral_mid']};
        background: transparent;
        border: none;
    }}
    .stTabs [aria-selected="true"] {{
        background: {DIEXA['primary']} !important;
        color: {DIEXA['white']} !important;
    }}
    .stTabs [data-baseweb="tab-highlight"] {{
        display: none;
    }}
    .stTabs [data-baseweb="tab-border"] {{
        display: none;
    }}

    /* ── Métricas ── */
    [data-testid="stMetric"] {{
        background: {DIEXA['white']};
        border: 1px solid {DIEXA['neutral_light']};
        border-radius: 8px;
        padding: 0.8rem 1rem;
        border-left: 4px solid {DIEXA['primary_light']};
        box-shadow: 0 1px 3px rgba(0,39,93,0.06);
    }}
    [data-testid="stMetricLabel"] {{
        color: {DIEXA['neutral_mid']} !important;
        font-size: 0.78rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    [data-testid="stMetricValue"] {{
        color: {DIEXA['primary']} !important;
        font-size: 1.4rem !important;
        font-weight: 700 !important;
    }}

    /* ── Botones ── */
    .stDownloadButton > button {{
        background: {DIEXA['primary']} !important;
        color: {DIEXA['white']} !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        padding: 0.5rem 1.5rem !important;
        transition: all 0.2s ease;
        letter-spacing: 0.3px;
    }}
    .stDownloadButton > button:hover {{
        background: {DIEXA['teal']} !important;
        box-shadow: 0 2px 8px rgba(0,39,93,0.2);
    }}

    /* ── DataFrames / tablas ── */
    .stDataFrame {{
        border: 1px solid {DIEXA['neutral_light']};
        border-radius: 8px;
        overflow: hidden;
    }}

    /* ── Subheaders ── */
    .section-title {{
        color: {DIEXA['primary']};
        font-size: 1.15rem;
        font-weight: 700;
        border-bottom: 2px solid {DIEXA['primary_light']};
        padding-bottom: 0.4rem;
        margin-bottom: 1rem;
        letter-spacing: 0.3px;
    }}

    /* ── Selectbox ── */
    .stSelectbox label {{
        color: {DIEXA['neutral_dark']} !important;
        font-weight: 600 !important;
    }}

    /* ── Info boxes ── */
    .tolerance-card {{
        background: {DIEXA['white']};
        border: 1px solid {DIEXA['neutral_light']};
        border-left: 4px solid {DIEXA['blue']};
        border-radius: 6px;
        padding: 0.7rem 1rem;
        font-size: 0.9rem;
        color: {DIEXA['neutral_dark']};
        margin-bottom: 0.5rem;
    }}
    .tolerance-card strong {{
        color: {DIEXA['primary']};
    }}

    /* ── Footer ── */
    .diexa-footer {{
        background: {DIEXA['primary']};
        color: rgba(255,255,255,0.7);
        text-align: center;
        padding: 0.8rem 1rem;
        border-radius: 8px 8px 0 0;
        margin-top: 2rem;
        font-size: 0.78rem;
        letter-spacing: 0.3px;
    }}
    .diexa-footer strong {{
        color: {DIEXA['white']};
    }}

    /* ── Alertas ── */
    .stAlert {{
        border-radius: 6px;
    }}

    /* ── File uploader ── */
    [data-testid="stFileUploader"] {{
        border: 2px dashed {DIEXA['primary_light']};
        border-radius: 10px;
        padding: 1rem;
        background: {DIEXA['white']};
    }}

    /* ── Ocultar menú y footer de Streamlit ── */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
</style>
"""

# =============================================================================
# APP CONFIG
# =============================================================================
st.set_page_config(
    page_title=APP_NAME,
    page_icon="⛏️",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(CORPORATE_CSS, unsafe_allow_html=True)

# ── Header corporativo ──
st.markdown(f"""
<div class="diexa-header">
    <div>
        <p class="diexa-header-title">⛏️ {APP_NAME}</p>
        <p class="diexa-header-subtitle">{APP_FULL_NAME}</p>
    </div>
    <div class="diexa-header-badge">v{APP_VERSION}</div>
</div>
""", unsafe_allow_html=True)

# ── Sidebar corporativo ──
with st.sidebar:
    st.markdown(f"""
    <div style="text-align:center; padding:0.5rem 0 1rem 0;">
        <span style="font-size:1.8rem;">⛏️</span><br>
        <span style="color:{DIEXA['white']}; font-size:1.1rem; font-weight:700; letter-spacing:1px;">DIEXA</span><br>
        <span style="color:{DIEXA['primary_light']}; font-size:0.7rem; letter-spacing:0.5px;">Distribuidora de Explosivos y Accesorios S.A.</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(f"<p style='color:{DIEXA['primary_light']}; font-weight:600; font-size:0.95rem; margin-bottom:0.3rem;'>Configuración de análisis</p>", unsafe_allow_html=True)

    use_ocr_fallback = st.checkbox(
        "Usar OCR de respaldo",
        value=True,
        help="Activa el reconocimiento óptico (OCR) cuando la extracción nativa de texto no logra obtener todos los datos del PDF. Recomendado mantener activado."
    )
    render_zoom = st.slider(
        "Resolución OCR",
        min_value=2.0, max_value=5.0, value=3.0, step=0.5,
        help="Factor de ampliación para la imagen OCR. Mayor valor = mejor lectura, pero más lento."
    )

    st.markdown("---")
    st.markdown(f"<p style='color:{DIEXA['primary_light']}; font-weight:600; font-size:0.95rem; margin-bottom:0.3rem;'>Tolerancias de desviación</p>", unsafe_allow_html=True)

    thr_dev_m = st.number_input(
        "Desviación máxima permitida (m)",
        min_value=0.0, value=2.0, step=0.1, format="%.2f",
        help="Desviación en metros considerada aceptable. Los tiros que excedan este valor se marcarán como no conformes."
    )
    thr_dev_deg = st.number_input(
        "Desviación angular máxima (°)",
        min_value=0.0, value=2.0, step=0.1, format="%.2f",
        help="Desviación de inclinación considerada aceptable. Los tiros que excedan este valor se marcarán como no conformes."
    )
    st.caption("Estos valores determinan el semáforo de conformidad de cada tiro.")

    st.markdown("---")
    st.markdown(f"""
    <div style="background:rgba(255,255,255,0.08); border-radius:6px; padding:0.6rem 0.8rem; margin-top:0.5rem;">
        <p style="color:{DIEXA['neutral_light']}; font-size:0.72rem; margin:0; font-weight:600;">Estado de módulos</p>
        <p style="color:{DIEXA['neutral_light']}; font-size:0.72rem; margin:0.2rem 0 0 0;">
            PyPDF2: ✅ &nbsp;·&nbsp; pdfplumber: {'✅' if PDFPLUMBER_OK else '❌'} &nbsp;·&nbsp; OCR: {'✅' if OCR_OK else '❌'}
        </p>
    </div>
    """, unsafe_allow_html=True)
    if (not OCR_OK) and OCR_IMPORT_ERROR:
        st.warning(f"OCR no disponible: {OCR_IMPORT_ERROR}")
    elif OCR_OK and TESSERACT_PATH:
        st.markdown(f"""
        <div style="background:rgba(33,165,255,0.1); border-radius:6px; padding:0.4rem 0.6rem; margin-top:0.3rem;">
            <p style="color:{DIEXA['primary_light']}; font-size:0.65rem; margin:0;">
                ✓ Tesseract detectado en:<br>
                <span style="opacity:0.7;">{TESSERACT_PATH}</span>
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background:rgba(255,255,255,0.08); border-radius:6px; padding:0.5rem 0.8rem; margin-top:0.8rem;">
        <p style="color:{DIEXA['neutral_light']}; font-size:0.7rem; margin:0; font-weight:600;">Semáforo de conformidad</p>
        <p style="color:{DIEXA['neutral_light']}; font-size:0.7rem; margin:0.15rem 0 0 0;">
            🟢 Conforme &nbsp;·&nbsp; 🟡 Parcial &nbsp;·&nbsp; 🔴 No conforme &nbsp;·&nbsp; ⚪ Sin datos
        </p>
    </div>
    """, unsafe_allow_html=True)


# =============================================================================
# UTILIDADES BÁSICAS
# =============================================================================

def _normalize_text(t: str) -> str:
    if not t:
        return ""
    for old in ('º', '\u00b0', '\u2070', '\u00ba', '˚'):
        t = t.replace(old, '°')
    return t


def _clean_spaces(text: str) -> str:
    if not text:
        return ""
    text = _normalize_text(text)
    text = text.replace("\xa0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\s*\n\s*", "\n", text)
    return text.strip()


def _collapse_text(text: str) -> str:
    if not text:
        return ""
    return re.sub(r"\s+", " ", _clean_spaces(text)).strip()


def _safe_num(token: str):
    if token is None:
        return np.nan
    t = str(token).strip()
    t = t.replace("°", "").replace("%", "").replace("m", "").replace("…", "")
    t = t.replace("−", "-")
    if re.match(r'^\d{1,3}(?:,\d{3})+(?:\.\d+)?$', t):
        return np.nan
    try:
        if t.count(",") == 1 and t.count(".") == 0:
            t = t.replace(",", ".")
        return float(t)
    except Exception:
        return np.nan


def _extract_between(text: str, start_pat: str, end_pat: str, flags=re.IGNORECASE | re.DOTALL):
    if not text:
        return ""
    m1 = re.search(start_pat, text, flags)
    if not m1:
        return ""
    start = m1.end()
    m2 = re.search(end_pat, text[start:], flags)
    if not m2:
        return text[start:]
    end = start + m2.start()
    return text[start:end]


def _distance(a, b):
    return abs(a - b)


def _fmt_metric(v, fmt="{:.2f}"):
    return fmt.format(v) if pd.notna(v) else "N/A"

# =============================================================================
# OCR HELPERS
# =============================================================================

OCR_ROIS = {
    "top_right": (0.50, 0.10, 0.985, 0.38),
    "bottom_left": (0.40, 0.41, 0.985, 0.70),
}


def _render_pdf_page_to_pil(pdf_bytes: bytes, page_num: int, zoom: float = 3.0):
    if not OCR_OK:
        return None
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        page = doc.load_page(page_num - 1)
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        return img
    except Exception:
        return None


def _crop_rel(img, box_rel):
    if img is None:
        return None
    w, h = img.size
    x0 = int(box_rel[0] * w)
    y0 = int(box_rel[1] * h)
    x1 = int(box_rel[2] * w)
    y1 = int(box_rel[3] * h)
    x0 = max(0, min(x0, w - 1))
    y0 = max(0, min(y0, h - 1))
    x1 = max(x0 + 1, min(x1, w))
    y1 = max(y0 + 1, min(y1, h))
    return img.crop((x0, y0, x1, y1))


def _prep_ocr_image(img):
    if img is None or not OCR_OK:
        return None
    gray = ImageOps.grayscale(img)
    gray = ImageOps.autocontrast(gray)
    gray = gray.filter(ImageFilter.SHARPEN)
    w, h = gray.size
    gray = gray.resize((int(w * 1.5), int(h * 1.5)))
    return gray


def _ocr_image_text(img, psm: int = 6):
    if not OCR_OK or img is None:
        return ""
    try:
        config = f"--oem 3 --psm {psm}"
        txt = pytesseract.image_to_string(img, lang="eng", config=config)
        return _clean_spaces(txt)
    except Exception:
        return ""


def _ocr_region_from_pdf_page(pdf_bytes: bytes, page_num: int, region_key: str, zoom: float = 3.0):
    if not OCR_OK:
        return ""
    img = _render_pdf_page_to_pil(pdf_bytes, page_num, zoom=zoom)
    if img is None:
        return ""
    crop = _crop_rel(img, OCR_ROIS[region_key])
    crop = _prep_ocr_image(crop)
    return _ocr_image_text(crop, psm=6)

# =============================================================================
# EXTRACCIÓN TEXTO PDF
# =============================================================================

def extract_pages_text_from_pdf_bytes(pdf_bytes: bytes, filename: str = "") -> list[str]:
    page_texts = []
    if PDFPLUMBER_OK:
        try:
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                for page in pdf.pages:
                    txt = page.extract_text() or ""
                    page_texts.append(_normalize_text(txt))
            if any(t.strip() for t in page_texts):
                return page_texts
        except Exception as e:
            print(f"[WARN] pdfplumber falló en '{filename}': {e}")
    page_texts = []
    try:
        reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
        for page in reader.pages:
            txt = page.extract_text() or ""
            page_texts.append(_normalize_text(txt))
    except Exception as e:
        st.error(f"Error al leer el PDF '{filename}': {e}")
        return []
    return page_texts

# =============================================================================
# SHOT NAME / CHIMENEA
# =============================================================================

_SHOT_TOKEN_RE = re.compile(
    r"Informe\s+de\s+implementaci[oó]n\s+(?:TIRO\s+)?([A-Za-zÑñ]{1,3}\d{0,2})\b",
    re.IGNORECASE,
)

_SHOT_BLACKLIST = {
    'TO', 'TOP', 'PRO', 'COL', 'AZ', 'INC', 'AGS', 'TIRO',
    'TOPOGRAFO', 'PROYECTO', 'COLLAR', 'ARRIBA', 'ATRAS',
    'LADO', 'MEDIDO', 'PLANIFICADO', 'DESVIACION',
    'INCLINACION', 'ACIMUT', 'LARGO',
    'ESTE', 'NORTE', 'ELEVACION', 'FECHA',
    'EXTREMO', 'PROFUNDIDAD', 'ARCHIVO', 'NOMBRE',
    'TIEMPO', 'ANGULO', 'CALIBRACION',
}


def extract_shot_name(page_text: str):
    if not page_text:
        return None
    text = _normalize_text(page_text)
    for ln in text.splitlines()[:25]:
        m = _SHOT_TOKEN_RE.search(ln)
        if m:
            raw = m.group(1).strip()
            if raw.upper() not in _SHOT_BLACKLIST:
                return raw
    m = _SHOT_TOKEN_RE.search(text[:600])
    if m:
        raw = m.group(1).strip()
        if raw.upper() not in _SHOT_BLACKLIST:
            return raw
    return None


def normalize_shot_name(raw: str) -> str:
    if raw is None or raw == "":
        return ""
    r = str(raw).strip()
    if r in ('Ñ', 'ñ'):
        return 'Ñ'
    if r.lower() == 'nn':
        return 'NN'
    return r.upper()


def extract_chimney_name(filename: str) -> str:
    stem = Path(filename).stem
    stem = re.sub(r"^\d+\.\s*", "", stem).strip()
    return stem

# =============================================================================
# BLOQUE SUPERIOR
# =============================================================================

def _extract_desv_final(page_text: str) -> float:
    text = _collapse_text(page_text)
    m = re.search(r"Desviaci[oó]n\s+final\s+.*?\s(\d+(?:[.,]\d+)?)m", text, re.IGNORECASE)
    if m:
        v = _safe_num(m.group(1))
        if not np.isnan(v) and 0 <= v <= 50:
            return float(v)
    return np.nan


def _get_upper_right_block_text(page_text: str) -> str:
    text = _collapse_text(page_text)
    block = _extract_between(text, r"Fecha\s+de\s+la\s+encuesta", r"Medido\s+Planificado\s+Desviaci[oó]n")
    return _collapse_text(block)


def extract_top_right_dev_inclination_from_text(page_text: str):
    block = _get_upper_right_block_text(page_text)
    if not block:
        return np.nan
    angle_tokens = re.findall(r"\d+(?:[.,]\d+)?°", block)
    if len(angle_tokens) < 2:
        return np.nan
    vals = [_safe_num(t) for t in angle_tokens[-2:]]
    vals = [v for v in vals if not np.isnan(v)]
    if len(vals) >= 2:
        val = min(vals)
        if 0 <= val <= 30:
            return float(val)
    smalls = sorted(v for v in [_safe_num(t) for t in angle_tokens] if not np.isnan(v) and 0 <= v <= 30)
    if smalls:
        return float(smalls[-1])
    return np.nan


def extract_top_right_dev_inclination(page_text: str, pdf_bytes: bytes = None, page_num: int = None, use_ocr=False, zoom=3.0):
    val = extract_top_right_dev_inclination_from_text(page_text)
    if not np.isnan(val):
        return val, "native"
    if use_ocr and pdf_bytes is not None and page_num is not None and OCR_OK:
        ocr_text = _ocr_region_from_pdf_page(pdf_bytes, page_num, "top_right", zoom=zoom)
        val = extract_top_right_dev_inclination_from_text(ocr_text)
        if not np.isnan(val):
            return val, "ocr"
    return np.nan, "none"

# =============================================================================
# BLOQUE INFERIOR: LARGO / DESV / DESV% / AZ / INC
# =============================================================================

def _get_bottom_impl_block_text(page_text: str) -> str:
    text = _collapse_text(page_text)
    idx_arriba = text.find("Arriba")
    if idx_arriba != -1:
        text = text[idx_arriba:]
    m_start = re.search(r"Implementaci[oó]n-1\s+Planificar", text, re.IGNORECASE)
    if not m_start:
        return ""
    start = m_start.end()
    candidates = []
    for pat in [r"AZ\s+INC\s+Largo\s+DESV\s+DESV\s*%\s+Elevaci[oó]n", r"Atr[aá]s"]:
        m_end = re.search(pat, text[start:], re.IGNORECASE)
        if m_end:
            candidates.append(start + m_end.start())
    end = min(candidates) if candidates else len(text)
    return _collapse_text(text[start:end])


def _pick_inc_az_from_angles(angle_values: list[float]):
    vals = [v for v in angle_values if pd.notna(v)]
    if len(vals) < 2:
        if len(vals) == 1:
            return (np.nan, vals[0]) if abs(vals[0] - 180) > 20 else (vals[0], np.nan)
        return np.nan, np.nan
    a, b = vals[0], vals[1]
    if abs(a - 180) <= abs(b - 180):
        return a, b
    return b, a


def _parse_bottom_block_semantic(block_text: str, source_label="native") -> pd.DataFrame:
    cols = ["L_m", "dev_m", "dev_pct", "az_deg", "inc_deg", "source"]
    if not block_text:
        return pd.DataFrame(columns=cols)
    text = _collapse_text(block_text)
    length_matches = list(re.finditer(r"(?<!\d)(2|4|6|8|10|12|14|16|18|20)\.00m\b", text))
    if not length_matches:
        return pd.DataFrame(columns=cols)
    rows = []
    for i, m in enumerate(length_matches):
        L = _safe_num(m.group(0))
        if np.isnan(L):
            continue
        prev_edge = length_matches[i - 1].end() if i > 0 else max(0, m.start() - 120)
        next_edge = length_matches[i + 1].start() if i + 1 < len(length_matches) else min(len(text), m.end() + 130)
        window = text[prev_edge:next_edge]
        local_len_pos = m.start() - prev_edge

        pct_cands = []
        for pm in re.finditer(r"(\d+(?:[.,]\d+)?)%", window):
            val = _safe_num(pm.group(1))
            if not np.isnan(val):
                pct_cands.append((_distance(pm.start(), local_len_pos), val))
        pct_val = np.nan
        if pct_cands:
            pct_cands.sort(key=lambda x: x[0])
            pct_val = pct_cands[0][1]

        dev_cands = []
        for mm in re.finditer(r"(\d+(?:[.,]\d+)?)m\b", window):
            val = _safe_num(mm.group(1))
            if np.isnan(val):
                continue
            if abs(val - L) < 1e-6:
                continue
            if val > 50:
                continue
            if 0 <= val < 5.0:
                dev_cands.append((_distance(mm.start(), local_len_pos), val))
        dev_val = np.nan
        if dev_cands:
            dev_cands.sort(key=lambda x: x[0])
            dev_val = dev_cands[0][1]

        angle_cands = []
        for am in re.finditer(r"(\d+(?:[.,]\d+)?)°", window):
            val = _safe_num(am.group(1))
            if not np.isnan(val):
                angle_cands.append((_distance(am.start(), local_len_pos), val))
        angle_vals = []
        if angle_cands:
            angle_cands.sort(key=lambda x: x[0])
            angle_vals = [v for _, v in angle_cands[:2]]
        inc_deg, az_deg = _pick_inc_az_from_angles(angle_vals)

        rows.append({
            "L_m": float(L),
            "dev_m": float(dev_val) if not np.isnan(dev_val) else np.nan,
            "dev_pct": float(pct_val) if not np.isnan(pct_val) else np.nan,
            "az_deg": float(az_deg) if not np.isnan(az_deg) else np.nan,
            "inc_deg": float(inc_deg) if not np.isnan(inc_deg) else np.nan,
            "source": source_label,
        })
    if not rows:
        return pd.DataFrame(columns=cols)
    return pd.DataFrame(rows).drop_duplicates(subset=["L_m"]).sort_values("L_m").reset_index(drop=True)


def extract_bottom_left_metraje_from_text(page_text: str) -> pd.DataFrame:
    block = _get_bottom_impl_block_text(page_text)
    return _parse_bottom_block_semantic(block, source_label="native")


def _merge_metraje_tables(df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
    base_cols = ["L_m", "dev_m", "dev_pct", "az_deg", "inc_deg", "source"]
    if df1 is None or df1.empty:
        return df2 if df2 is not None else pd.DataFrame(columns=base_cols)
    if df2 is None or df2.empty:
        return df1
    merged = pd.merge(df1, df2, on="L_m", how="outer", suffixes=("_a", "_b"))
    out = pd.DataFrame()
    out["L_m"] = merged["L_m"]
    for col in ["dev_m", "dev_pct", "az_deg", "inc_deg"]:
        out[col] = merged[f"{col}_a"].combine_first(merged[f"{col}_b"])
    out["source"] = np.where(merged[[c for c in merged.columns if c.endswith('_a')]].notna().any(axis=1), "native", "ocr")
    return out.sort_values("L_m").reset_index(drop=True)


def extract_bottom_left_metraje(page_text: str, pdf_bytes: bytes = None, page_num: int = None, use_ocr=False, zoom=3.0) -> pd.DataFrame:
    df_native = extract_bottom_left_metraje_from_text(page_text)
    need_ocr = df_native.empty or df_native["dev_m"].notna().sum() < 3 or df_native["dev_pct"].notna().sum() < 3
    if use_ocr and need_ocr and pdf_bytes is not None and page_num is not None and OCR_OK:
        ocr_text = _ocr_region_from_pdf_page(pdf_bytes, page_num, "bottom_left", zoom=zoom)
        df_ocr = _parse_bottom_block_semantic(ocr_text, source_label="ocr")
        return _merge_metraje_tables(df_native, df_ocr)
    return df_native

# =============================================================================
# LÓGICA QA / SEMÁFORO
# =============================================================================

def eval_status(dev_m_eff, dev_deg, thr_m, thr_deg):
    ok_m = pd.notna(dev_m_eff) and dev_m_eff <= thr_m
    ok_deg = pd.notna(dev_deg) and dev_deg <= thr_deg
    has_m = pd.notna(dev_m_eff)
    has_deg = pd.notna(dev_deg)
    if not has_m and not has_deg:
        return "⚪", np.nan, np.nan
    if ok_m and ok_deg:
        return "🟢", ok_m, ok_deg
    if (has_m and ok_m) or (has_deg and ok_deg):
        return "🟡", ok_m if has_m else np.nan, ok_deg if has_deg else np.nan
    return "🔴", ok_m if has_m else np.nan, ok_deg if has_deg else np.nan


def _compute_qc(row_summary: dict, df_metraje: pd.DataFrame):
    warnings_list = []
    if np.isnan(row_summary.get("Desv Inc Sup (°)", np.nan)):
        warnings_list.append("Sin Desv. Inc. superior")
    if np.isnan(row_summary.get("Desv m Efectiva (m)", np.nan)):
        warnings_list.append("Sin desviación efectiva en metros")
    if df_metraje is None or df_metraje.empty:
        warnings_list.append("Sin tabla Implementación-1")
    else:
        if df_metraje["dev_m"].notna().sum() == 0:
            warnings_list.append("Sin DESV en tabla inferior")
        if df_metraje["dev_pct"].notna().sum() == 0:
            warnings_list.append("Sin DESV% en tabla inferior")
        if df_metraje["az_deg"].notna().sum() == 0:
            warnings_list.append("Sin azimut para gráfico polar")
        bad = 0
        for _, r in df_metraje.dropna(subset=["L_m", "dev_m", "dev_pct"]).iterrows():
            if r["L_m"] > 0:
                calc = r["dev_m"] / r["L_m"] * 100.0
                if abs(calc - r["dev_pct"]) > 2.5:
                    bad += 1
        if bad > 0:
            warnings_list.append(f"{bad} fila(s) con dev% inconsistente")
    return warnings_list


def process_shot(shot_dict: dict, thr_m: float, thr_deg: float, use_ocr=False, zoom=3.0) -> dict:
    page_text = shot_dict["shot_text"]
    pdf_bytes = shot_dict.get("pdf_bytes")
    page_num = shot_dict.get("page_num")

    dev_final_superior_m = _extract_desv_final(page_text)
    dev_inc_sup, source_dev_inc = extract_top_right_dev_inclination(
        page_text, pdf_bytes=pdf_bytes, page_num=page_num, use_ocr=use_ocr, zoom=zoom
    )
    df_metraje = extract_bottom_left_metraje(
        page_text, pdf_bytes=pdf_bytes, page_num=page_num, use_ocr=use_ocr, zoom=zoom
    )

    largo_final = np.nan
    dev_final_tab_m = np.nan
    dev_final_tab_pct = np.nan
    az_final = np.nan
    fuente_metraje = "none"
    n_filas = 0
    if df_metraje is not None and not df_metraje.empty:
        n_filas = len(df_metraje)
        fuente_metraje = ",".join(sorted(df_metraje["source"].dropna().astype(str).unique()))
        r = df_metraje.sort_values("L_m").iloc[-1]
        largo_final = r.get("L_m", np.nan)
        dev_final_tab_m = r.get("dev_m", np.nan)
        dev_final_tab_pct = r.get("dev_pct", np.nan)
        az_final = r.get("az_deg", np.nan)

    dev_m_efectiva = dev_final_tab_m if pd.notna(dev_final_tab_m) else dev_final_superior_m
    semaforo, ok_m, ok_deg = eval_status(dev_m_efectiva, dev_inc_sup, thr_m, thr_deg)

    summary = {
        "Tiro": shot_dict["shot_name"],
        "Chimenea": extract_chimney_name(shot_dict["filename"]),
        "Archivo": shot_dict["filename"],
        "Página": shot_dict.get("page_num"),
        "Desv Final Sup (m)": dev_final_superior_m,
        "Desv Final Tabla (m)": dev_final_tab_m,
        "Desv m Efectiva (m)": dev_m_efectiva,
        "Desv Inc Sup (°)": dev_inc_sup,
        "Fuente Desv Inc": source_dev_inc,
        "Largo Final (m)": largo_final,
        "DESV Final Tabla (%)": dev_final_tab_pct,
        "AZ Final (°)": az_final,
        "N filas metraje": n_filas,
        "Fuente Metraje": fuente_metraje,
        "Cumple m": ok_m,
        "Cumple °": ok_deg,
        "Estado": semaforo,
    }
    qc_warnings = _compute_qc(summary, df_metraje)
    summary["QC Warnings"] = len(qc_warnings)
    summary["QC Detalle"] = " | ".join(qc_warnings)

    return {
        "summary": summary,
        "pdf_metraje": df_metraje,
        "shot_name": shot_dict["shot_name"],
        "chimenea": extract_chimney_name(shot_dict["filename"]),
        "archivo": shot_dict["filename"],
        "page_num": shot_dict.get("page_num"),
        "page_text": page_text,
    }

# =============================================================================
# EXPORT EXCEL
# =============================================================================

def dataframe_to_excel_bytes(df_shots: pd.DataFrame, df_metraje: pd.DataFrame, df_chim: pd.DataFrame) -> bytes:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_shots.to_excel(writer, index=False, sheet_name="Resumen tiros")
        df_chim.to_excel(writer, index=False, sheet_name="Resumen chimeneas")
        df_metraje.to_excel(writer, index=False, sheet_name="Metraje detalle")
    output.seek(0)
    return output.getvalue()

# =============================================================================
# GRÁFICOS CORPORATIVOS
# =============================================================================

def _apply_diexa_style(fig, ax):
    """Aplica estilo corporativo DIEXA a un gráfico matplotlib."""
    fig.patch.set_facecolor(DIEXA['white'])
    if hasattr(ax, 'set_facecolor'):
        ax.set_facecolor(DIEXA['white'])
    ax.title.set_color(DIEXA['primary'])
    ax.title.set_fontsize(11)
    ax.title.set_fontweight('bold')
    for spine in ax.spines.values():
        spine.set_color(DIEXA['neutral_light'])
        spine.set_linewidth(0.8)
    ax.tick_params(colors=DIEXA['neutral_mid'], labelsize=8)
    if hasattr(ax, 'xaxis'):
        ax.xaxis.label.set_color(DIEXA['neutral_dark'])
        ax.xaxis.label.set_fontsize(9)
    if hasattr(ax, 'yaxis'):
        ax.yaxis.label.set_color(DIEXA['neutral_dark'])
        ax.yaxis.label.set_fontsize(9)


def plot_metraje(df: pd.DataFrame, title="DESV y DESV% vs Largo"):
    fig, ax1 = plt.subplots(figsize=(8, 4.5))
    _apply_diexa_style(fig, ax1)
    if df is None or df.empty or df["dev_m"].notna().sum() == 0:
        ax1.text(0.5, 0.5, "Sin datos disponibles", ha='center', va='center',
                 transform=ax1.transAxes, color=DIEXA['neutral_mid'], fontsize=11)
        return fig
    d = df.sort_values("L_m")
    ax1.plot(d["L_m"], d["dev_m"], 'o-', label='DESV (m)', color=DIEXA['primary'],
             linewidth=2, markersize=5)
    ax1.set_xlabel("Largo (m)")
    ax1.set_ylabel("DESV (m)")
    ax1.grid(True, alpha=0.2, color=DIEXA['neutral_light'])
    if "dev_pct" in d.columns and d["dev_pct"].notna().sum() > 0:
        ax2 = ax1.twinx()
        ax2.plot(d["L_m"], d["dev_pct"], 's--', label='DESV (%)', color=DIEXA['primary_light'],
                 linewidth=2, markersize=5)
        ax2.set_ylabel("DESV (%)")
        ax2.yaxis.label.set_color(DIEXA['neutral_dark'])
        lines, labels = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines + lines2, labels + labels2, loc='best', framealpha=0.9,
                   edgecolor=DIEXA['neutral_light'], fontsize=8)
    else:
        ax1.legend(loc='best', framealpha=0.9, edgecolor=DIEXA['neutral_light'], fontsize=8)
    ax1.set_title(title)
    plt.tight_layout()
    return fig


def plot_shot_polar(df: pd.DataFrame, title="Gráfico polar por tiro"):
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(projection='polar'))
    fig.patch.set_facecolor(DIEXA['white'])
    ax.set_facecolor(DIEXA['white'])
    if df is None or df.empty or df["az_deg"].notna().sum() == 0 or df["dev_m"].notna().sum() == 0:
        ax.text(0.5, 0.5, "Sin datos suficientes\n(azimut/desviación)", ha='center', va='center',
                transform=ax.transAxes, color=DIEXA['neutral_mid'], fontsize=10)
        ax.set_title(title, pad=20, color=DIEXA['primary'], fontweight='bold', fontsize=11)
        return fig
    d = df.dropna(subset=["az_deg", "dev_m"]).sort_values("L_m")
    theta = np.deg2rad(d["az_deg"].values)
    r = d["dev_m"].values
    ax.plot(theta, r, 'o-', linewidth=2, markersize=5, color=DIEXA['primary'], label='Desviación')
    ax.plot([0], [0], 'o', color=DIEXA['primary_light'], markersize=8, label='Centro')
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)
    ax.grid(True, alpha=0.3)
    ax.set_title(title, pad=20, color=DIEXA['primary'], fontweight='bold', fontsize=11)
    ax.legend(loc='upper right', bbox_to_anchor=(1.25, 1.1), fontsize=8,
              framealpha=0.9, edgecolor=DIEXA['neutral_light'])
    return fig


def plot_chimney_polar_overlay(df_metraje_chim: pd.DataFrame, title="Gráfico polar por chimenea"):
    fig, ax = plt.subplots(figsize=(6.5, 6.5), subplot_kw=dict(projection='polar'))
    fig.patch.set_facecolor(DIEXA['white'])
    ax.set_facecolor(DIEXA['white'])
    if df_metraje_chim is None or df_metraje_chim.empty or df_metraje_chim["az_deg"].notna().sum() == 0:
        ax.text(0.5, 0.5, "Sin datos suficientes\npara gráfico polar", ha='center', va='center',
                transform=ax.transAxes, color=DIEXA['neutral_mid'], fontsize=10)
        ax.set_title(title, pad=20, color=DIEXA['primary'], fontweight='bold', fontsize=11)
        return fig
    # Colores de la paleta DIEXA para series
    series_colors = [DIEXA['primary'], DIEXA['primary_light'], DIEXA['blue'],
                     DIEXA['teal'], DIEXA['blue_bright'], DIEXA['blue_link']]
    plotted = 0
    for idx, tiro in enumerate(sorted(df_metraje_chim["Tiro"].astype(str).unique())):
        sub = df_metraje_chim[(df_metraje_chim["Tiro"] == tiro)].dropna(subset=["az_deg", "dev_m"]).sort_values("L_m")
        if sub.empty:
            continue
        color = series_colors[idx % len(series_colors)]
        theta = np.deg2rad(sub["az_deg"].values)
        r = sub["dev_m"].values
        ax.plot(theta, r, 'o-', alpha=0.75, linewidth=1.8, markersize=4, label=f"Tiro {tiro}", color=color)
        plotted += 1
    ax.plot([0], [0], 'o', color=DIEXA['primary_light'], markersize=8)
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)
    ax.grid(True, alpha=0.3)
    ax.set_title(title, pad=20, color=DIEXA['primary'], fontweight='bold', fontsize=11)
    if plotted > 0:
        ax.legend(loc='upper right', bbox_to_anchor=(1.45, 1.1), fontsize=7,
                  framealpha=0.9, edgecolor=DIEXA['neutral_light'])
    return fig


def plot_summary_bars(df: pd.DataFrame, category_col: str, value_col: str, tol: float, ylabel: str, title: str):
    fig, ax = plt.subplots(figsize=(9, 4.8))
    _apply_diexa_style(fig, ax)
    if df is None or df.empty or value_col not in df.columns:
        ax.text(0.5, 0.5, "Sin datos disponibles", ha='center', va='center',
                transform=ax.transAxes, color=DIEXA['neutral_mid'], fontsize=11)
        return fig
    vals = pd.to_numeric(df[value_col], errors='coerce').values
    cats = df[category_col].astype(str).values
    safe_vals = np.where(np.isnan(vals), 0, vals)
    bars = ax.bar(range(len(cats)), safe_vals, edgecolor=DIEXA['neutral_light'], linewidth=0.8, width=0.65)
    ax.axhline(y=tol, color=DIEXA['danger'], linestyle='--', linewidth=1.8,
               label=f'Tolerancia = {tol:.2f}', alpha=0.8)
    for bar, v in zip(bars, vals):
        if np.isnan(v):
            bar.set_color(DIEXA['gray_light'])
            label = 'N/A'
        else:
            if v > tol * 1.2:
                bar.set_color(DIEXA['danger'])
            elif v > tol:
                bar.set_color(DIEXA['warning'])
            else:
                bar.set_color(DIEXA['success'])
            label = f"{v:.2f}"
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(safe_vals.max() * 0.02, 0.02), label,
                ha='center', va='bottom', fontsize=8, color=DIEXA['neutral_dark'])
    ax.set_xticks(range(len(cats)))
    ax.set_xticklabels(cats, rotation=45, ha='right', fontsize=8)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(axis='y', alpha=0.2, color=DIEXA['neutral_light'])
    ax.legend(loc='upper right', fontsize=8, framealpha=0.9, edgecolor=DIEXA['neutral_light'])
    ymax = max(np.nanmax(safe_vals) * 1.25 if len(safe_vals) else tol * 1.5, tol * 1.5)
    ax.set_ylim(0, ymax if ymax > 0 else 1)
    plt.tight_layout()
    return fig

# =============================================================================
# MAIN APP – CARGA DE ARCHIVOS
# =============================================================================

st.markdown('<p class="section-title">Carga de archivos PDF</p>', unsafe_allow_html=True)
uploaded_files = st.file_uploader(
    "Seleccione los informes Boretrak/Carlson en formato PDF",
    type=['pdf'],
    accept_multiple_files=True,
    key='pdf_uploader',
    help="Puede cargar múltiples archivos PDF simultáneamente. Cada página del PDF se interpreta como un tiro independiente."
)

if not uploaded_files:
    st.markdown(f"""
    <div style="background:{DIEXA['white']}; border:1px solid {DIEXA['neutral_light']};
         border-left:4px solid {DIEXA['primary_light']}; border-radius:6px;
         padding:1.5rem 2rem; text-align:center; margin:2rem 0;">
        <p style="color:{DIEXA['primary']}; font-size:1.1rem; font-weight:600; margin:0 0 0.5rem 0;">
            Cargue archivos PDF para comenzar el análisis
        </p>
        <p style="color:{DIEXA['neutral_mid']}; font-size:0.88rem; margin:0;">
            Utilice el selector de archivos o arrastre los PDF directamente sobre el área de carga.
        </p>
    </div>
    """, unsafe_allow_html=True)
    # Footer aún con mensaje vacío
    st.markdown(f"""
    <div class="diexa-footer">
        <strong>DIEXA</strong> · Distribuidora de Explosivos y Accesorios S.A. · {APP_CREDIT}
    </div>
    """, unsafe_allow_html=True)
    st.stop()

all_shots = []
with st.spinner("Procesando archivos PDF..."):
    for pdf_file in uploaded_files:
        pdf_bytes = pdf_file.getvalue()
        page_texts = extract_pages_text_from_pdf_bytes(pdf_bytes, pdf_file.name)
        if not page_texts:
            st.warning(f"No se pudo extraer texto desde: {pdf_file.name}")
            continue
        name_counts = {}
        for page_num, page_text in enumerate(page_texts, start=1):
            if not page_text or not page_text.strip():
                continue
            raw_shot_name = extract_shot_name(page_text)
            base_name = normalize_shot_name(raw_shot_name) if raw_shot_name else f"PAG_{page_num}"
            if base_name not in name_counts:
                name_counts[base_name] = 1
                unique_name = base_name
            else:
                name_counts[base_name] += 1
                unique_name = f"{base_name}_{name_counts[base_name]}"
            all_shots.append({
                "shot_name": unique_name,
                "shot_text": page_text,
                "filename": pdf_file.name,
                "page_num": page_num,
                "pdf_bytes": pdf_bytes,
            })

if not all_shots:
    st.error("No se detectó ningún tiro en los PDFs cargados. Verifique que los archivos contengan informes Boretrak/Carlson válidos.")
    st.stop()

processed = [process_shot(s, thr_dev_m, thr_dev_deg, use_ocr=(use_ocr_fallback and OCR_OK), zoom=render_zoom) for s in all_shots]

df_shots = pd.DataFrame([p["summary"] for p in processed])
for c in ["Desv Final Sup (m)", "Desv Final Tabla (m)", "Desv m Efectiva (m)", "Desv Inc Sup (°)", "Largo Final (m)", "DESV Final Tabla (%)", "AZ Final (°)"]:
    if c in df_shots.columns:
        df_shots[c] = pd.to_numeric(df_shots[c], errors='coerce')

metraje_rows = []
for p in processed:
    dfm = p["pdf_metraje"]
    if dfm is not None and not dfm.empty:
        tmp = dfm.copy()
        tmp.insert(0, "Tiro", p["shot_name"])
        tmp.insert(0, "Página", p["page_num"])
        tmp.insert(0, "Archivo", p["archivo"])
        tmp.insert(0, "Chimenea", p["chimenea"])
        metraje_rows.append(tmp)
df_metraje = pd.concat(metraje_rows, ignore_index=True) if metraje_rows else pd.DataFrame(columns=["Chimenea","Archivo","Página","Tiro","L_m","dev_m","dev_pct","az_deg","inc_deg","source"])

chim_rows = []
for chim in sorted(df_shots["Chimenea"].dropna().astype(str).unique()):
    sub = df_shots[df_shots["Chimenea"] == chim].copy()
    n = len(sub)
    ok = int((sub["Estado"] == "🟢").sum()) if "Estado" in sub.columns else 0
    chim_rows.append({
        "Chimenea": chim,
        "N tiros": n,
        "Conformes": ok,
        "Pass Rate (%)": round(ok / n * 100.0, 1) if n > 0 else np.nan,
        "Prom Desv (m)": sub["Desv m Efectiva (m)"].mean(),
        "Prom Desv Inc (°)": sub["Desv Inc Sup (°)"].mean(),
        "Máx Desv (m)": sub["Desv m Efectiva (m)"].max(),
        "Máx Desv Inc (°)": sub["Desv Inc Sup (°)"].max(),
        ">Tol m": int((sub["Desv m Efectiva (m)"] > thr_dev_m).sum()),
        ">Tol °": int((sub["Desv Inc Sup (°)"] > thr_dev_deg).sum()),
    })
df_chim = pd.DataFrame(chim_rows)

n_files = len(uploaded_files)
n_shots = len(df_shots)
pass_total = int((df_shots["Estado"] == "🟢").sum()) if "Estado" in df_shots.columns else 0
n_with_metraje = int(df_shots["N filas metraje"].fillna(0).astype(int).gt(0).sum()) if "N filas metraje" in df_shots.columns else 0
avg_dev_m_global = df_shots["Desv m Efectiva (m)"].mean() if "Desv m Efectiva (m)" in df_shots.columns else np.nan
avg_dev_deg_global = df_shots["Desv Inc Sup (°)"].mean() if "Desv Inc Sup (°)" in df_shots.columns else np.nan

xlsx_bytes = dataframe_to_excel_bytes(df_shots, df_metraje, df_chim)

# =============================================================================
# UI – PESTAÑAS PRINCIPALES
# =============================================================================

tab1, tab2, tab3, tab4 = st.tabs(["Resumen General", "Detalle por Tiro", "Análisis por Chimenea", "Diagnóstico"])

with tab1:
    st.markdown('<p class="section-title">Indicadores globales</p>', unsafe_allow_html=True)
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Archivos cargados", n_files)
    c2.metric("Tiros analizados", n_shots)
    c3.metric("Conformes", f"{pass_total}/{n_shots}")
    c4.metric("Prom. Desv. (m)", _fmt_metric(avg_dev_m_global))
    c5.metric("Prom. Desv. Inc. (°)", _fmt_metric(avg_dev_deg_global))
    c6.metric("Con metraje", n_with_metraje)

    st.markdown('<p class="section-title">Tolerancias activas</p>', unsafe_allow_html=True)
    t1, t2 = st.columns(2)
    t1.markdown(f'<div class="tolerance-card">Desviación en metros tolerada: <strong>{thr_dev_m:.2f} m</strong></div>', unsafe_allow_html=True)
    t2.markdown(f'<div class="tolerance-card">Desviación angular tolerada: <strong>{thr_dev_deg:.2f}°</strong></div>', unsafe_allow_html=True)

    st.markdown('<p class="section-title">Resumen por chimenea</p>', unsafe_allow_html=True)
    st.dataframe(df_chim, use_container_width=True, hide_index=True)

    g1, g2 = st.columns(2)
    with g1:
        fig = plot_summary_bars(df_chim, "Chimenea", "Prom Desv (m)", thr_dev_m, "Promedio desviación (m)", "Promedio de desviación en metros por chimenea")
        st.pyplot(fig)
    with g2:
        fig = plot_summary_bars(df_chim, "Chimenea", "Prom Desv Inc (°)", thr_dev_deg, "Promedio desviación (°)", "Promedio de desviación angular por chimenea")
        st.pyplot(fig)

    st.markdown('<p class="section-title">Resumen por tiro</p>', unsafe_allow_html=True)
    st.dataframe(df_shots, use_container_width=True, hide_index=True)
    st.download_button(
        "Descargar reporte Excel",
        data=xlsx_bytes,
        file_name=f"DIEXA_Boretrak_QA_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

with tab2:
    st.markdown('<p class="section-title">Detalle por tiro</p>', unsafe_allow_html=True)
    chim_opts = sorted(df_shots["Chimenea"].dropna().astype(str).unique().tolist())
    chim_sel = st.selectbox("Seleccione la chimenea", chim_opts, help="Filtre por chimenea para ver los tiros asociados.")
    sub = df_shots[df_shots["Chimenea"] == chim_sel].copy()
    tiro_sel = st.selectbox("Seleccione el tiro", sub["Tiro"].astype(str).unique().tolist(), help="Seleccione un tiro específico para ver su detalle.")
    row = sub[sub["Tiro"] == tiro_sel].iloc[0]

    st.markdown('<p class="section-title">Indicadores del tiro seleccionado</p>', unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Estado", row["Estado"])
    c2.metric("Desv. efectiva (m)", _fmt_metric(row['Desv m Efectiva (m)']))
    c3.metric("Desv. Inc. Sup. (°)", _fmt_metric(row['Desv Inc Sup (°)']))
    c4.metric("Largo final (m)", _fmt_metric(row['Largo Final (m)']))
    c5.metric("DESV tabla (%)", _fmt_metric(row['DESV Final Tabla (%)']))

    # Info del tiro en tarjetas
    info_col1, info_col2, info_col3 = st.columns(3)
    info_col1.markdown(f'<div class="tolerance-card">Fuente Desv. Inc.: <strong>{row["Fuente Desv Inc"]}</strong></div>', unsafe_allow_html=True)
    info_col2.markdown(f'<div class="tolerance-card">Fuente metraje: <strong>{row["Fuente Metraje"]}</strong></div>', unsafe_allow_html=True)
    qc_text = row['QC Detalle'] if row['QC Detalle'] else 'Sin observaciones'
    info_col3.markdown(f'<div class="tolerance-card">Control de calidad: <strong>{qc_text}</strong></div>', unsafe_allow_html=True)

    df_tiro = df_metraje[(df_metraje["Chimenea"] == chim_sel) & (df_metraje["Tiro"] == tiro_sel)].copy()

    g1, g2 = st.columns(2)
    with g1:
        fig = plot_shot_polar(df_tiro, title=f"Polar de desviación · {tiro_sel}")
        st.pyplot(fig)
    with g2:
        fig = plot_metraje(df_tiro, title=f"DESV y DESV% vs Largo · {tiro_sel}")
        st.pyplot(fig)

    st.markdown('<p class="section-title">Tabla de metraje</p>', unsafe_allow_html=True)
    st.dataframe(df_tiro, use_container_width=True, hide_index=True)

with tab3:
    st.markdown('<p class="section-title">Análisis por chimenea</p>', unsafe_allow_html=True)
    chim_opts = sorted(df_shots["Chimenea"].dropna().astype(str).unique().tolist())
    chim_graf = st.selectbox("Seleccione chimenea para análisis", chim_opts, key="graf_chim",
                             help="Seleccione una chimenea para ver su dashboard completo con indicadores y gráficos.")
    sub_shots = df_shots[df_shots["Chimenea"] == chim_graf].copy().sort_values('Tiro')
    df_m_chim = df_metraje[df_metraje["Chimenea"] == chim_graf].copy()

    # Dashboard por chimenea
    n_tiros = len(sub_shots)
    n_conformes = int((sub_shots['Estado'] == '🟢').sum()) if not sub_shots.empty else 0
    pass_rate = (n_conformes / n_tiros * 100.0) if n_tiros > 0 else np.nan
    prom_m = sub_shots['Desv m Efectiva (m)'].mean() if 'Desv m Efectiva (m)' in sub_shots.columns and not sub_shots.empty else np.nan
    prom_deg = sub_shots['Desv Inc Sup (°)'].mean() if 'Desv Inc Sup (°)' in sub_shots.columns and not sub_shots.empty else np.nan
    sobre_tol_m = int((sub_shots['Desv m Efectiva (m)'] > thr_dev_m).sum()) if not sub_shots.empty else 0
    sobre_tol_deg = int((sub_shots['Desv Inc Sup (°)'] > thr_dev_deg).sum()) if not sub_shots.empty else 0

    st.markdown(f'<p class="section-title">Dashboard · {chim_graf}</p>', unsafe_allow_html=True)
    d1, d2, d3, d4, d5, d6 = st.columns(6)
    d1.metric("N° tiros", n_tiros)
    d2.metric("Conformes", n_conformes)
    d3.metric("Tasa conformidad", _fmt_metric(pass_rate, "{:.1f}%"))
    d4.metric("Prom. Desv. (m)", _fmt_metric(prom_m))
    d5.metric("Prom. Desv. Inc. (°)", _fmt_metric(prom_deg))
    d6.metric("Sobre tolerancia (m / °)", f"{sobre_tol_m} / {sobre_tol_deg}")

    g1, g2 = st.columns(2)
    with g1:
        fig = plot_chimney_polar_overlay(df_m_chim, title=f"Polar de desviaciones · {chim_graf}")
        st.pyplot(fig)
    with g2:
        fig = plot_summary_bars(
            sub_shots, "Tiro", "Desv m Efectiva (m)", thr_dev_m,
            "Desviación en metros (m)", f"Desviación en metros por tiro · {chim_graf}"
        )
        st.pyplot(fig)

    g3, g4 = st.columns(2)
    with g3:
        fig = plot_summary_bars(
            sub_shots, "Tiro", "Desv Inc Sup (°)", thr_dev_deg,
            "Desviación angular (°)", f"Desviación angular por tiro · {chim_graf}"
        )
        st.pyplot(fig)
    with g4:
        if not df_m_chim.empty:
            avg_len = df_m_chim.groupby("L_m", as_index=False).agg({"dev_m":"mean", "dev_pct":"mean"})
            fig = plot_metraje(avg_len, title=f"Promedio metraje por largo · {chim_graf}")
            st.pyplot(fig)
        else:
            st.info("Sin datos de metraje para esta chimenea")

with tab4:
    st.markdown('<p class="section-title">Diagnóstico y verificación de datos</p>', unsafe_allow_html=True)
    st.caption("Esta sección permite verificar la extracción de texto de cada página para resolver problemas de lectura o datos faltantes.")
    sel_file = st.selectbox("Archivo", sorted(df_shots["Archivo"].astype(str).unique().tolist()))
    df_file = df_shots[df_shots["Archivo"] == sel_file].sort_values("Página")
    sel_page = st.selectbox("Página", df_file["Página"].tolist())
    p = next(x for x in processed if x["archivo"] == sel_file and x["page_num"] == sel_page)
    st.markdown('<p class="section-title">Texto extraído de la página</p>', unsafe_allow_html=True)
    st.text_area("page_text", value=p["page_text"], height=320, label_visibility="collapsed")
    st.markdown('<p class="section-title">Bloque superior detectado</p>', unsafe_allow_html=True)
    st.text_area("upper_block", value=_get_upper_right_block_text(p["page_text"]), height=100, label_visibility="collapsed")
    st.markdown('<p class="section-title">Bloque inferior detectado</p>', unsafe_allow_html=True)
    st.text_area("bottom_block", value=_get_bottom_impl_block_text(p["page_text"]), height=140, label_visibility="collapsed")
    if use_ocr_fallback and OCR_OK:
        pdf_bytes = next(s["pdf_bytes"] for s in all_shots if s["filename"] == sel_file and s["page_num"] == sel_page)
        st.markdown('<p class="section-title">OCR región superior</p>', unsafe_allow_html=True)
        st.text_area("ocr_top", value=_ocr_region_from_pdf_page(pdf_bytes, sel_page, "top_right", zoom=render_zoom), height=100, label_visibility="collapsed")
        st.markdown('<p class="section-title">OCR región inferior</p>', unsafe_allow_html=True)
        st.text_area("ocr_bottom", value=_ocr_region_from_pdf_page(pdf_bytes, sel_page, "bottom_left", zoom=render_zoom), height=140, label_visibility="collapsed")

# =============================================================================
# FOOTER CORPORATIVO
# =============================================================================
st.markdown(f"""
<div class="diexa-footer">
    <strong>DIEXA</strong> · Distribuidora de Explosivos y Accesorios S.A.<br>
    {APP_CREDIT}<br>
    <span style="opacity:0.6;">{APP_NAME} v{APP_VERSION} · Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} · OCR: {'Activo' if (use_ocr_fallback and OCR_OK) else 'Inactivo'}</span>
</div>
""", unsafe_allow_html=True)
