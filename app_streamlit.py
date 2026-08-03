"""
SISTEMA DE DETECCIÓ DE BIAIX I DESINFORMACIÓ
Interfície web - Versió professional i minimalista
Treball de Recerca - Arantxa Ruiz-Ruano Pedreira, 2026
"""

import streamlit as st
import pandas as pd
import re
import os
import sys
from pathlib import Path

# ============================================================================
# CONFIGURACIÓ DE PÀGINA
# ============================================================================

st.set_page_config(
    page_title="Sistema de Detecció de Biaix | TR",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============================================================================
# ESTILOS PERSONALIZADOS - DISSENY PROFESSIONAL EN ROSA
# ============================================================================

st.markdown(
    """
    <style>
    /* Fons limpi */
    .stApp {
        background-color: #fafbfc;
    }
    
    /* Eliminar marges */
    .st-emotion-cache-1y4p8pa {
        padding: 0;
    }
    
    /* ====== TÍTOLS ====== */
    h1 {
        color: #1f2937;
        font-size: 2em;
        font-weight: 600;
        margin-bottom: 0.3em;
        border-bottom: 2px solid #d9a8c8;
        padding-bottom: 0.5em;
    }
    
    h2 {
        color: #374151;
        font-size: 1.2em;
        font-weight: 600;
        margin-top: 1.2em;
        margin-bottom: 0.6em;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        font-size: 0.9em;
    }
    
    h3 {
        color: #4b5563;
        font-size: 0.95em;
        font-weight: 600;
        margin-top: 0.8em;
    }
    
    /* ====== TEXT GENERAL ====== */
    body, p {
        color: #374151;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
        line-height: 1.6;
    }
    
    /* ====== BOTONS ====== */
    .stButton > button {
        background-color: #d9a8c8;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 0.6em 1.5em;
        font-weight: 500;
        font-size: 0.95em;
        cursor: pointer;
        transition: background-color 0.2s;
    }
    
    .stButton > button:hover {
        background-color: #c989ba;
    }
    
    /* ====== TEXTAREA ====== */
    .stTextArea textarea {
        border: 1px solid #d1d5db !important;
        border-radius: 4px;
        font-size: 0.95em;
    }
    
    .stTextArea textarea:focus {
        border-color: #d9a8c8 !important;
    }
    
    /* ====== CAIXES INFORMACIÓ ====== */
    .stWarning {
        background-color: #fce4ec;
        border: 1px solid #f48fb1;
        color: #c2185b;
        border-radius: 4px;
    }
    
    .stSuccess {
        background-color: #e8f5e9;
        border: 1px solid #81c784;
        color: #2e7d32;
        border-radius: 4px;
    }
    
    .stError {
        background-color: #ffebee;
        border: 1px solid #ef5350;
        color: #c62828;
        border-radius: 4px;
    }
    
    /* ====== TARGES RESULTATS ====== */
    .result-card {
        background-color: white;
        border: 1px solid #e5e7eb;
        border-left: 4px solid;
        border-radius: 4px;
        padding: 1.2em;
        margin: 0.5em 0;
    }
    
    .result-header {
        font-weight: 600;
        color: #1f2937;
        margin-bottom: 0.6em;
        font-size: 0.85em;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .result-value {
        font-size: 1.6em;
        font-weight: 600;
        margin: 0.3em 0;
    }
    
    /* ====== EXPANDERS ====== */
    .streamlit-expanderHeader {
        background-color: white;
        border: 1px solid #e5e7eb;
        border-radius: 4px;
        padding: 0.8em;
        font-weight: 500;
    }
    
    .streamlit-expanderContent {
        background-color: #f9fafb;
        border: 1px solid #e5e7eb;
        border-top: none;
        padding: 1em;
    }
    
    /* ====== DIVIDERS ====== */
    .stDivider {
        margin: 1.5em 0;
        border: none;
        border-top: 1px solid #e5e7eb;
    }
    
    /* ====== COMPARACIÓ DIFERENCIES ====== */
    .comparison-header {
        background-color: #fbeaf0;
        padding: 0.8em;
        border-radius: 4px;
        margin-bottom: 1em;
        font-weight: 600;
        color: #6a0572;
    }
    .criteri-box {
        background-color: #fbeaf0;
        border-left: 3px solid #d9a8c8;
        padding: 0.8em 1em;
        border-radius: 4px;
        margin-bottom: 1em;
        font-size: 0.9em;
        color: #374151;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================================
# CARGAR MÓDULOS
# ============================================================================

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from datetime import datetime
    from config_b import DIMENSIONS, TEXTOS_TEST, RUBRICA, INDICADORES
    from detector_claude import analizar_texto_claude, generar_titol
    from generador_pdf import (
        generar_pdf,
        crear_grafic_comparatiu,
        generar_pdf_comparatiu,
    )
except ImportError as e:
    st.error(f"Error al carregar mòduls: {str(e)}")
    st.stop()

# ============================================================================
# INICIALIZAR SESSION STATE
# ============================================================================

if "texto_input" not in st.session_state:
    st.session_state.texto_input = ""

if "comparacion_1" not in st.session_state:
    st.session_state.comparacion_1 = ""

if "comparacion_2" not in st.session_state:
    st.session_state.comparacion_2 = ""

if "resultado_1" not in st.session_state:
    st.session_state.resultado_1 = None

if "resultado_2" not in st.session_state:
    st.session_state.resultado_2 = None

if "resultado_simple" not in st.session_state:
    st.session_state.resultado_simple = None

# ============================================================================
# FUNCIONS AUXILIARS
# ============================================================================


def netejar_nom_fitxer(text):
    """Converteix un títol en un nom de fitxer segur"""
    text = text.strip().lower()
    text = re.sub(r"\s+", "_", text)  # espais -> _
    text = re.sub(r"[^\w\-]", "", text)  # treu caràcters il·legals (/ : ? " etc.)
    return text[:40] if text else "informe"


def formatear_intensitat(intensitat):
    """Mapeja intensitat a format llegible"""
    mapeo = {"nul·la": "Nul·la", "lleu": "Lleu", "moderada": "Moderada", "alta": "Alta"}
    return mapeo.get(intensitat, intensitat)


def nom_dimensio(dim_key):
    """Retorna el nom de la dimensió en català per mostrar"""
    noms = {
        "biaix": "Biaix",
        "desinformacio": "Desinformació",
        "emocional": "Emocional",
    }
    return noms.get(dim_key, dim_key)


def get_color_intensitat(intensitat):
    """Retorna color segons intensitat"""
    colores = {
        "nul·la": "#10b981",  # Verd
        "lleu": "#f59e0b",  # Groc
        "moderada": "#f97316",  # Taronja
        "alta": "#ef4444",  # Vermell
    }
    return colores.get(intensitat, "#6b7280")


def mostrar_targes_resultats(data, titulo="Resultats"):
    """Muestra las 3 tarjetas de resultados"""
    st.subheader(titulo)

    col1, col2, col3 = st.columns(3)

    with col1:
        biaix_data = data.get("biaix", {})
        biaix_int = biaix_data.get("intensitat", "nul·la")
        color = get_color_intensitat(biaix_int)

        # Intentar obtener confianza, con manejo de errores
        try:
            biaix_conf = biaix_data.get("confianca")
            if biaix_conf is not None:
                confianza_text = f'<div style="font-size: 0.85em; color: #7f8c8d; margin-top: 0.5em;">({int(biaix_conf)}% confiança)</div>'
            else:
                confianza_text = ""
        except (ValueError, TypeError):
            confianza_text = ""

        st.markdown(
            f"""
        <div class="result-card" style="border-left-color: {color}">
            <div class="result-header">Biaix Ideològic</div>
            <div class="result-value" style="color: {color}">
                {formatear_intensitat(biaix_int)}
            </div>
            {confianza_text}
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        desinf_data = data.get("desinformacio", {})
        desinf_int = desinf_data.get("intensitat", "nul·la")
        color = get_color_intensitat(desinf_int)

        # Intentar obtener confianza, con manejo de errores
        try:
            desinf_conf = desinf_data.get("confianca")
            if desinf_conf is not None:
                confianza_text = f'<div style="font-size: 0.85em; color: #7f8c8d; margin-top: 0.5em;">({int(desinf_conf)}% confiança)</div>'
            else:
                confianza_text = ""
        except (ValueError, TypeError):
            confianza_text = ""

        st.markdown(
            f"""
        <div class="result-card" style="border-left-color: {color}">
            <div class="result-header">Desinformació</div>
            <div class="result-value" style="color: {color}">
                {formatear_intensitat(desinf_int)}
            </div>
            {confianza_text}
        </div>
        """,
            unsafe_allow_html=True,
        )

    with col3:
        emoc_data = data.get("emocional", {})
        emoc_int = emoc_data.get("intensitat", "nul·la")
        color = get_color_intensitat(emoc_int)

        # Intentar obtener confianza, con manejo de errores
        try:
            emoc_conf = emoc_data.get("confianca")
            if emoc_conf is not None:
                confianza_text = f'<div style="font-size: 0.85em; color: #7f8c8d; margin-top: 0.5em;">({int(emoc_conf)}% confiança)</div>'
            else:
                confianza_text = ""
        except (ValueError, TypeError):
            confianza_text = ""

        st.markdown(
            f"""
        <div class="result-card" style="border-left-color: {color}">
            <div class="result-header">Llenguatge Emocional</div>
            <div class="result-value" style="color: {color}">
                {formatear_intensitat(emoc_int)}
            </div>
            {confianza_text}
        </div>
        """,
            unsafe_allow_html=True,
        )


def mostrar_detalles(data, titulo="Detalls"):
    """Muestra los detalles expandibles"""
    if titulo:
        st.subheader(titulo)

    for dim_key in DIMENSIONS:
        dim_data = data.get(dim_key, {})
        intensitat = dim_data.get("intensitat", "nul·la")
        fragment = dim_data.get("fragment", "N/A")
        explicacio = dim_data.get("explicacio", "")

        # Criteri de la rúbrica per aquest nivell
        criteri = RUBRICA.get(dim_key, {}).get(intensitat, "")

        with st.expander(
            f"{nom_dimensio(dim_key).upper()} — {formatear_intensitat(intensitat)}",
            expanded=False,
        ):
            if criteri:
                st.markdown(
                    f"<div class='criteri-box'><strong>Criteri de la rúbrica "
                    f"({formatear_intensitat(intensitat)}):</strong> {criteri}</div>",
                    unsafe_allow_html=True,
                )

            st.write("**Fragment detectat:**")
            st.code(fragment, language="text")
            st.write(f"**Anàlisi:** {explicacio}")


def get_color_ideologia(puntuacio):
    """Retorna color segons la puntuació ideològica (-100 a 100)"""
    if puntuacio <= -20:
        return "#3b82f6"  # Blau (esquerra)
    elif puntuacio >= 20:
        return "#ef4444"  # Vermell (dreta)
    return "#9ca3af"  # Gris (centre)


def mostrar_barra_ideologia(data, titulo="Orientació ideològica detectada"):
    """Mostra una barra horitzontal esquerra-dreta amb un marcador de posició"""
    ideologia = data.get("ideologia", {})

    try:
        puntuacio = float(ideologia.get("puntuacio", 0))
    except (ValueError, TypeError):
        puntuacio = 0
    puntuacio = max(-100, min(100, puntuacio))

    etiqueta = ideologia.get("etiqueta", "centre")
    explicacio = ideologia.get("explicacio", "")
    posicio_pct = (puntuacio + 100) / 2
    color = get_color_ideologia(puntuacio)

    if titulo:
        st.markdown(f"**{titulo}**")

    st.markdown(
        f"""
        <div style="margin: 0.5em 0 1.2em 0;">
            <div style="display:flex; justify-content:space-between; font-size:0.75em;
                        font-weight:600; color:#6b7280; text-transform:uppercase;
                        letter-spacing:0.5px; margin-bottom:0.5em;">
                <span>Esquerra</span>
                <span>Centre</span>
                <span>Dreta</span>
            </div>
            <div style="position:relative; height:8px; border-radius:4px;
                        background:linear-gradient(to right, #3b82f6, #d1d5db, #ef4444);
                        margin-bottom:0.7em;">
                <div style="position:absolute; top:50%; left:{posicio_pct}%;
                            transform:translate(-50%, -50%); width:18px; height:18px;
                            border-radius:50%; background:white; border:3px solid {color};
                            box-shadow:0 1px 3px rgba(0,0,0,0.25);"></div>
            </div>
            <div style="text-align:center; font-weight:600; color:{color}; font-size:0.95em;
                        text-transform:capitalize;">
                {etiqueta.replace('-', ' ')} ({puntuacio:+.0f})
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if explicacio:
        st.markdown(
            f"<div class='criteri-box'>{explicacio}</div>",
            unsafe_allow_html=True,
        )


def mostrar_barra_ideologia_comparativa(data1, data2, nom1="Notícia 1", nom2="Notícia 2"):
    """Mostra una única barra esquerra-dreta amb un marcador per a cada notícia"""
    ideologia1 = data1.get("ideologia", {})
    ideologia2 = data2.get("ideologia", {})

    def _puntuacio(ideologia):
        try:
            p = float(ideologia.get("puntuacio", 0))
        except (ValueError, TypeError):
            p = 0
        return max(-100, min(100, p))

    punt1 = _puntuacio(ideologia1)
    punt2 = _puntuacio(ideologia2)
    pos1 = (punt1 + 100) / 2
    pos2 = (punt2 + 100) / 2
    etiqueta1 = ideologia1.get("etiqueta", "centre").replace("-", " ")
    etiqueta2 = ideologia2.get("etiqueta", "centre").replace("-", " ")

    color1 = "#c989ba"  # rosa - notícia 1 (mateix to que els botons de l'app)
    color2 = "#4b5563"  # gris fosc - notícia 2

    st.markdown(
        f"""
        <div style="margin: 0.5em 0 1em 0;">
            <div style="display:flex; justify-content:space-between; font-size:0.75em;
                        font-weight:600; color:#6b7280; text-transform:uppercase;
                        letter-spacing:0.5px; margin-bottom:0.5em;">
                <span>Esquerra</span>
                <span>Centre</span>
                <span>Dreta</span>
            </div>
            <div style="position:relative; height:12px; border-radius:6px;
                        background:linear-gradient(to right, #3b82f6, #d1d5db, #ef4444);
                        margin-bottom:0.8em;">
                <div style="position:absolute; top:25%; left:{pos1}%;
                            transform:translate(-50%, -50%); width:17px; height:17px;
                            border-radius:50%; background:{color1}; border:3px solid white;
                            box-shadow:0 1px 3px rgba(0,0,0,0.35); z-index:2;"></div>
                <div style="position:absolute; top:75%; left:{pos2}%;
                            transform:translate(-50%, -50%); width:17px; height:17px;
                            border-radius:50%; background:{color2}; border:3px solid white;
                            box-shadow:0 1px 3px rgba(0,0,0,0.35); z-index:1;"></div>
            </div>
            <div style="display:flex; justify-content:center; gap:1.8em; font-size:0.85em;
                        color:#374151;">
                <span><span style="display:inline-block; width:10px; height:10px;
                      border-radius:50%; background:{color1}; margin-right:5px;"></span>
                      {nom1}: <strong>{etiqueta1}</strong> ({punt1:+.0f})</span>
                <span><span style="display:inline-block; width:10px; height:10px;
                      border-radius:50%; background:{color2}; margin-right:5px;"></span>
                      {nom2}: <strong>{etiqueta2}</strong> ({punt2:+.0f})</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        expl1 = ideologia1.get("explicacio", "")
        if expl1:
            st.markdown(
                f"<div class='criteri-box'><strong>{nom1}:</strong> {expl1}</div>",
                unsafe_allow_html=True,
            )
    with col2:
        expl2 = ideologia2.get("explicacio", "")
        if expl2:
            st.markdown(
                f"<div class='criteri-box'><strong>{nom2}:</strong> {expl2}</div>",
                unsafe_allow_html=True,
            )


def mostrar_reescriptura_neutral(data, titulo="Versió alternativa objectiva", key_suffix="default"):
    """Mostra la reescriptura neutral generada per Claude com a proposta d'explicació objectiva"""
    reescriptura = data.get("reescriptura_neutral", "")
    if not reescriptura:
        return

    if titulo:
        st.markdown(f"**{titulo}**")

    st.write(
        "Proposta de Claude per explicar el mateix contingut de manera "
        "descriptiva i equilibrada, mantenint els fets originals:"
    )
    st.code(reescriptura, language="text")


# ============================================================================
# HEADER
# ============================================================================

col1, col2 = st.columns([3, 1])

with col1:
    st.title("Detecció de biaix, llenguatge emocional i desinformació")
    st.caption("Sistema automàtic basat en Claude API | Treball de Recerca 2026")

with col2:
    st.caption("**Institut:** Vall d'Arús")
    st.caption("**Alumna:** Arantxa Ruiz-Ruano Pedreira")
    st.caption("**Curs:** 1r Batxillerat B")

st.divider()

# ============================================================================
# SECCIÓ: CÓMO FUNCIONA
# ============================================================================

with st.expander("Com funciona el sistema?", expanded=False):
    st.write("""
    Aquest sistema analitza textos polítics en tres dimensions. Per cada una,
    assigna un nivell d'intensitat segons els indicadors que hi detecta.
    """)

    noms = {
        "biaix": "Biaix Ideològic",
        "desinformacio": "Desinformació",
        "emocional": "Llenguatge Emocional",
    }

    descripcions = {
        "biaix": "Presentar la realitat de forma tendenciosa, afavorint una ideologia i denigrant-ne una altra.",
        "desinformacio": "Presentar informació falsa, no verificable o descontextualitzada com si fos certa.",
        "emocional": "Ús deliberat de paraules i recursos retòrics per apel·lar a les emocions del lector.",
    }

    for dim_key in DIMENSIONS:
        st.markdown(f"### {noms.get(dim_key, dim_key)}")
        st.write(descripcions.get(dim_key, ""))

        st.markdown("**Nivells d'intensitat:**")
        for nivell in ["nul·la", "lleu", "moderada", "alta"]:
            descripcio = RUBRICA.get(dim_key, {}).get(nivell, "")
            color = get_color_intensitat(nivell)
            st.markdown(
                f"<span style='color:{color}; font-weight:600'>"
                f"{formatear_intensitat(nivell)}</span> — {descripcio}",
                unsafe_allow_html=True,
            )

        st.markdown("**Indicadors que es busquen:**")
        for indicador in INDICADORES.get(dim_key, []):
            st.markdown(f"- {indicador}")

        st.write("")

    st.info(
        "Aquest sistema és una eina per detectar patrons, no la veritat absoluta. "
        "Sempre és recomanable contrastar la informació amb múltiples fonts."
    )

# ============================================================================
# NAVEGACIÓ - TABS
# ============================================================================

tab1, tab2 = st.tabs(["Analitzar un text", "Comparar dues notícies"])

# ============================================================================
# TAB 1: ANÁLISIS SIMPLE
# ============================================================================

with tab1:
    st.subheader("Anàlisi de Text Polític")

    st.write("""
    Introduïu un text polític per analitzar el seu contingut en termes de **biaix ideològic**, 
    **desinformació** i **llenguatge emocional**. El sistema utilitzarà Claude API per a l'anàlisi.
    """)

    # ===== EXEMPLES PRECARREGATS =====
    def carregar_exemple(id_text):
        try:
            df = pd.read_csv("corpus.csv", encoding="utf-8")
            fila = df[df["Id"] == id_text]
            if not fila.empty:
                st.session_state.texto_input = fila.iloc[0]["Text"]
        except Exception:
            pass

    st.write("**Proveu-ho amb un exemple:**")

    col_e1, col_e2, col_e3 = st.columns(3)

    with col_e1:
        st.button(
            "Exemple amb biaix",
            use_container_width=True,
            key="ex_biaix",
            on_click=carregar_exemple,
            args=(1,),
        )

    with col_e2:
        st.button(
            "Exemple emocional",
            use_container_width=True,
            key="ex_emocional",
            on_click=carregar_exemple,
            args=(17,),
        )

    with col_e3:
        st.button(
            "Exemple neutre",
            use_container_width=True,
            key="ex_neutre",
            on_click=carregar_exemple,
            args=(3,),
        )

    st.write("")

    # Input de text
    texto_input = st.text_area(
        "Introduïu el text a analitzar:",
        height=300,
        placeholder="Enganxeu aquí el text polític a analitzar...",
        label_visibility="collapsed",
        value=st.session_state.texto_input,
        key="texto_input",
    )

    # Definir funció de limpiar
    def limpiar():
        st.session_state.texto_input = ""

    # Botons d'acció
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        btn_analizar = st.button(
            "Analitzar", use_container_width=True, key="btn_analizar_tab1"
        )

    with col2:
        btn_limpiar = st.button(
            "Netejar",
            use_container_width=True,
            on_click=limpiar,
            key="btn_limpiar_tab1",
        )

    with col3:
        pass

    st.divider()

    # ANÀLISIS
    if btn_analizar:
        if not texto_input.strip():
            st.warning("Introduïu un text per analitzar.")
        else:
            with st.spinner("Analitzant text..."):
                resultado = analizar_texto_claude(texto_input, verbose=False)

                if not resultado.get("success"):
                    st.error(f"Error en l'anàlisi: {resultado.get('error')}")
                    st.session_state.resultado_simple = None
                else:
                    st.session_state.resultado_simple = resultado.get("data", {})
                    st.session_state.text_analitzat = texto_input
                    st.session_state.titol = generar_titol(texto_input)

    # Els resultats es mostren fora del boto perque no desapareguin
    if st.session_state.resultado_simple:
        data = st.session_state.resultado_simple

        st.success("Anàlisi completat")
        st.divider()
        mostrar_targes_resultats(data)
        st.divider()
        mostrar_detalles(data)
        st.divider()
        mostrar_barra_ideologia(data)
        st.divider()
        mostrar_reescriptura_neutral(data, key_suffix="simple")
        st.divider()

        titol_net = netejar_nom_fitxer(st.session_state.get("titol", "informe"))
        data_avui = datetime.now().strftime("%y-%m-%d")
        pdf_bytes = generar_pdf(
            data,
            st.session_state.get("text_analitzat", ""),
            st.session_state.get("titol", ""),
        )
        st.download_button(
            label="Descarregar informe (PDF)",
            data=pdf_bytes,
            file_name=f"anàlisi_{titol_net}_{data_avui}.pdf",
            mime="application/pdf",
        )


# ============================================================================
# TAB 2: COMPARACIÓ DE DOS TEXTOS
# ============================================================================

with tab2:
    st.subheader("Comparar dues notícies")

    st.write("""
    Enganxeu dues notícies sobre el mateix tema de diferents fonts i compareu el seu biaix i desinformació.
    Útil per veure com els medis cobreixen la mateixa notícia de manera diferent.
    """)

    # Dos columns para los inputs
    col1, col2 = st.columns(2)

    with col1:
        st.write("**Notícia 1**")
        text1 = st.text_area(
            "Primera notícia:",
            height=180,
            placeholder="Enganxeu la primera notícia...",
            label_visibility="collapsed",
            value=st.session_state.comparacion_1,
            key="comparacion_1",
        )

    with col2:
        st.write("**Notícia 2**")
        text2 = st.text_area(
            "Segona notícia:",
            height=180,
            placeholder="Enganxeu la segona notícia...",
            label_visibility="collapsed",
            value=st.session_state.comparacion_2,
            key="comparacion_2",
        )

    # Definir funciones para limpiar comparación
    def limpiar_comparacion():
        st.session_state.comparacion_1 = ""
        st.session_state.comparacion_2 = ""
        st.session_state.resultado_1 = None
        st.session_state.resultado_2 = None

    def analizar_comparacion():
        if not text1.strip() or not text2.strip():
            st.warning("Introduïu ambdós textos per comparar.")
            return

        col_left, col_right = st.columns(2)

        with col_left:
            with st.spinner("Analizant notícia 1..."):
                resultado1 = analizar_texto_claude(text1, verbose=False)
                if resultado1.get("success"):
                    st.session_state.resultado_1 = resultado1.get("data", {})

        with col_right:
            with st.spinner("Analizant notícia 2..."):
                resultado2 = analizar_texto_claude(text2, verbose=False)
                if resultado2.get("success"):
                    st.session_state.resultado_2 = resultado2.get("data", {})

        if not st.session_state.resultado_1 or not st.session_state.resultado_2:
            st.error("Error en l'anàlisi de una o ambdós notícies.")

    # Botons
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        btn_comparar = st.button(
            "Comparar notícies", use_container_width=True, key="btn_comparar"
        )

    with col2:
        btn_limpiar_comp = st.button(
            "Netejar",
            use_container_width=True,
            on_click=limpiar_comparacion,
            key="btn_limpiar_comp",
        )

    with col3:
        pass

    if btn_comparar:
        analizar_comparacion()

    # Mostrar resultados de comparación si existen
    if st.session_state.resultado_1 and st.session_state.resultado_2:
        st.divider()
        st.success("Anàlisis completats. Comparació:")
        st.divider()

        # Mostrar lado a lado
        st.markdown(
            "<div class='comparison-header'>Comparació de puntuacions</div>",
            unsafe_allow_html=True,
        )

        col1, col2 = st.columns(2)

        with col1:
            st.write("**Notícia 1**")
            mostrar_targes_resultats(st.session_state.resultado_1, titulo="")

        with col2:
            st.write("**Notícia 2**")
            mostrar_targes_resultats(st.session_state.resultado_2, titulo="")

        st.divider()

        # ===== DETALLS AMPLIATS =====
        col1, col2 = st.columns(2)

        with col1:
            st.write("### Detalls Notícia 1")
            mostrar_detalles(st.session_state.resultado_1, titulo="")

        with col2:
            st.write("### Detalls Notícia 2")
            mostrar_detalles(st.session_state.resultado_2, titulo="")

        st.divider()

        # ===== DIFERENCIES CLAU =====
        st.subheader("Diferencies clau")

        # Biaix
        biaix1 = st.session_state.resultado_1.get("biaix", {}).get(
            "intensitat", "nul·la"
        )
        biaix2 = st.session_state.resultado_2.get("biaix", {}).get(
            "intensitat", "nul·la"
        )

        if biaix1 != biaix2:
            st.info(
                f"Biaix: Notícia 1 = **{formatear_intensitat(biaix1)}** | Notícia 2 = **{formatear_intensitat(biaix2)}**"
            )
        else:
            st.success(
                f"Biaix: Ambdós texts mostren mateixa intensitat (**{formatear_intensitat(biaix1)}**)"
            )

        # Desinformació
        desinf1 = st.session_state.resultado_1.get("desinformacio", {}).get(
            "intensitat", "nul·la"
        )
        desinf2 = st.session_state.resultado_2.get("desinformacio", {}).get(
            "intensitat", "nul·la"
        )

        if desinf1 != desinf2:
            st.info(
                f"Desinformació: Notícia 1 = **{formatear_intensitat(desinf1)}** | Notícia 2 = **{formatear_intensitat(desinf2)}**"
            )
        else:
            st.success(
                f"Desinformació: Ambdós texts mostren mateixa intensitat (**{formatear_intensitat(desinf1)}**)"
            )

        # Emocional
        emoc1 = st.session_state.resultado_1.get("emocional", {}).get(
            "intensitat", "nul·la"
        )
        emoc2 = st.session_state.resultado_2.get("emocional", {}).get(
            "intensitat", "nul·la"
        )

        if emoc1 != emoc2:
            st.info(
                f"Llenguatge emocional: Notícia 1 = **{formatear_intensitat(emoc1)}** | Notícia 2 = **{formatear_intensitat(emoc2)}**"
            )
        else:
            st.success(
                f"Llenguatge emocional: Ambdós texts mostren mateixa intensitat (**{formatear_intensitat(emoc1)}**)"
            )

        st.divider()

        # ===== ORIENTACIÓ IDEOLÒGICA =====
        st.subheader("Orientació ideològica")
        mostrar_barra_ideologia_comparativa(
            st.session_state.resultado_1, st.session_state.resultado_2
        )

        st.divider()

        # ===== VERSIONS ALTERNATIVES OBJECTIVES =====
        st.subheader("Versions alternatives objectives")
        col1, col2 = st.columns(2)
        with col1:
            mostrar_reescriptura_neutral(
                st.session_state.resultado_1, titulo="Notícia 1", key_suffix="comp1"
            )
        with col2:
            mostrar_reescriptura_neutral(
                st.session_state.resultado_2, titulo="Notícia 2", key_suffix="comp2"
            )

        st.divider()

        # ===== GRÀFIC COMPARATIU =====
        st.subheader("Resum visual comparatiu")
        st.image(
            crear_grafic_comparatiu(
                st.session_state.resultado_1, st.session_state.resultado_2
            ),
            use_container_width=True,
        )
        st.divider()

        # ===== DESCÀRREGA PDF COMPARATIU =====
        data_avui = datetime.now().strftime("%y-%m-%d")
        pdf_bytes = generar_pdf_comparatiu(
            st.session_state.resultado_1, st.session_state.resultado_2
        )
        st.download_button(
            label="Descarregar comparació (PDF)",
            data=pdf_bytes,
            file_name=f"comparació_{data_avui}.pdf",
            mime="application/pdf",
            key="btn_download_comp",
        )

# ============================================================================
# FOOTER
# ============================================================================

st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.caption("**Rúbrica:** Biaix Ideològic | Desinformació | Llenguatge Emocional")

with col2:
    st.caption("**Model:** Claude 4.6 Opus")

with col3:
    st.caption("**Any:** 2026")
