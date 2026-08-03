# generador_pdf.py
# Genera un informe PDF a partir del resultat d'una anàlisi
# Treball de Recerca - Arantxa Ruiz-Ruano Pedreira, 2026

from datetime import datetime
from pathlib import Path
from fpdf import FPDF
from config_b import DIMENSIONS, RUBRICA
import io
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Noms llegibles de cada dimensió
NOMS_DIMENSIONS = {
    "biaix": "Biaix Ideològic",
    "desinformacio": "Desinformació",
    "emocional": "Llenguatge Emocional",
}

# Colors RGB per intensitat
COLORS_INTENSITAT = {
    "nul·la": (16, 185, 129),
    "lleu": (245, 158, 11),
    "moderada": (249, 115, 22),
    "alta": (239, 68, 68),
}

ETIQUETES = {
    "nul·la": "Nul·la",
    "lleu": "Lleu",
    "moderada": "Moderada",
    "alta": "Alta",
}
# Valor numèric de cada intensitat, per al gràfic
VALOR_INTENSITAT = {"nul·la": 0, "lleu": 1, "moderada": 2, "alta": 3}

ROSA = (217, 168, 200)
GRIS = (127, 140, 141)

# Ruta de les fonts del sistema Windows
CARPETA_FONTS = Path("C:/Windows/Fonts")


def registrar_fonts(pdf):
    """
    Carrega la font Arial del sistema, que suporta tots els caràcters
    catalans (à, è, í, ò, ú, ç, ï, ·).

    Les fonts que porta fpdf de sèrie només entenen un joc de caràcters
    molt limitat, i per això els accents es perdien.

    Retorna el nom de la família de font que s'ha de fer servir.
    """
    regular = CARPETA_FONTS / "arial.ttf"
    negreta = CARPETA_FONTS / "arialbd.ttf"
    cursiva = CARPETA_FONTS / "ariali.ttf"

    if regular.exists() and negreta.exists() and cursiva.exists():
        pdf.add_font("ArialTR", "", str(regular))
        pdf.add_font("ArialTR", "B", str(negreta))
        pdf.add_font("ArialTR", "I", str(cursiva))
        return "ArialTR"

    # Si no es troba Arial, es fa servir la font per defecte
    return "Helvetica"


def net(text, font):
    """
    Prepara el text per escriure'l al PDF.

    Amb Arial no cal netejar res: es respecten tots els accents.
    Amb la font de reserva cal substituir els caràcters que no suporta.
    """
    if text is None:
        return ""

    text = str(text)

    if font != "Helvetica":
        return text

    substitucions = {
        "\u2019": "'",
        "\u2018": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "-",
        "\u2026": "...",
        "\u00a0": " ",
    }

    for original, substitut in substitucions.items():
        text = text.replace(original, substitut)

    return text.encode("latin-1", errors="replace").decode("latin-1")


def paragraf(pdf, font, altura, contingut):
    """
    Escriu un bloc de text que ocupa tota l'amplada i deixa el cursor
    al marge esquerre de la línia següent.

    Sense new_x="LMARGIN", fpdf deixa el cursor al marge dret i el bloc
    següent es queda sense espai per dibuixar-se.
    """
    pdf.multi_cell(0, altura, net(contingut, font), new_x="LMARGIN", new_y="NEXT")


def crear_grafic_intensitats(data):
    """
    Crea un gràfic de barres horitzontals amb la intensitat de cada
    dimensió i el retorna com a imatge PNG en memòria (BytesIO).
    """
    noms, valors, colors, etiquetes = [], [], [], []
    for dim in DIMENSIONS:
        intensitat = data.get(dim, {}).get("intensitat", "nul·la")
        noms.append(NOMS_DIMENSIONS.get(dim, dim))
        valors.append(VALOR_INTENSITAT.get(intensitat, 0))
        rgb = COLORS_INTENSITAT.get(intensitat, (107, 114, 128))
        colors.append(tuple(c / 255 for c in rgb))
        etiquetes.append(ETIQUETES.get(intensitat, intensitat))

    fig, ax = plt.subplots(figsize=(7, 2.6))
    barres = ax.barh(noms, valors, color=colors, height=0.55)

    ax.set_xlim(0, 3.4)
    ax.set_xticks([0, 1, 2, 3])
    ax.set_xticklabels(["Nul·la", "Lleu", "Moderada", "Alta"], fontsize=9)
    ax.invert_yaxis()  # la primera dimensió queda a dalt

    for barra, etiqueta, valor in zip(barres, etiquetes, valors):
        ax.text(
            valor + 0.1,
            barra.get_y() + barra.get_height() / 2,
            etiqueta,
            va="center",
            fontsize=9,
            color="#374151",
        )

    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    ax.tick_params(axis="y", length=0, labelsize=10)
    ax.set_axisbelow(True)
    ax.xaxis.grid(True, color="#e5e7eb", linewidth=0.8)
    fig.subplots_adjust(left=0.28, right=0.97, top=0.95, bottom=0.18)

    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=150)  # sense bbox_inches: manté la proporció
    plt.close(fig)
    buffer.seek(0)
    return buffer


def crear_grafic_comparatiu(data1, data2):
    """
    Crea un gràfic de barres agrupades que compara la intensitat de cada
    dimensió entre dues notícies, i el retorna com a imatge PNG en memòria.
    """
    noms = [NOMS_DIMENSIONS.get(dim, dim) for dim in DIMENSIONS]
    posicions = list(range(len(noms)))
    altura = 0.35

    valors1, etiquetes1 = [], []
    valors2, etiquetes2 = [], []
    for dim in DIMENSIONS:
        intensitat1 = data1.get(dim, {}).get("intensitat", "nul·la")
        intensitat2 = data2.get(dim, {}).get("intensitat", "nul·la")
        valors1.append(VALOR_INTENSITAT.get(intensitat1, 0))
        valors2.append(VALOR_INTENSITAT.get(intensitat2, 0))
        etiquetes1.append(ETIQUETES.get(intensitat1, intensitat1))
        etiquetes2.append(ETIQUETES.get(intensitat2, intensitat2))

    color1 = tuple(c / 255 for c in ROSA)
    color2 = tuple(c / 255 for c in GRIS)

    fig, ax = plt.subplots(figsize=(7, 3))
    barres1 = ax.barh(
        [p + altura / 2 for p in posicions],
        valors1,
        height=altura,
        color=color1,
        label="Notícia 1",
    )
    barres2 = ax.barh(
        [p - altura / 2 for p in posicions],
        valors2,
        height=altura,
        color=color2,
        label="Notícia 2",
    )

    ax.set_yticks(posicions)
    ax.set_yticklabels(noms, fontsize=9)
    ax.set_xlim(0, 3.6)
    ax.set_xticks([0, 1, 2, 3])
    ax.set_xticklabels(["Nul·la", "Lleu", "Moderada", "Alta"], fontsize=9)
    ax.invert_yaxis()

    for barra, etiqueta, valor in zip(barres1, etiquetes1, valors1):
        ax.text(
            valor + 0.1,
            barra.get_y() + barra.get_height() / 2,
            etiqueta,
            va="center",
            fontsize=8,
            color="#374151",
        )
    for barra, etiqueta, valor in zip(barres2, etiquetes2, valors2):
        ax.text(
            valor + 0.1,
            barra.get_y() + barra.get_height() / 2,
            etiqueta,
            va="center",
            fontsize=8,
            color="#374151",
        )

    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    ax.tick_params(axis="y", length=0, labelsize=10)
    ax.set_axisbelow(True)
    ax.xaxis.grid(True, color="#e5e7eb", linewidth=0.8)
    ax.legend(loc="lower right", fontsize=8, frameon=False)
    fig.subplots_adjust(left=0.28, right=0.97, top=0.95, bottom=0.15)

    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=150)
    plt.close(fig)
    buffer.seek(0)
    return buffer


def generar_pdf_comparatiu(data1, data2, titol1="", titol2=""):
    """
    Genera un informe en PDF que compara els resultats de dues notícies.

    data1, data2      -> diccionaris amb els resultats de cada anàlisi
    titol1, titol2    -> títols opcionals de cada notícia

    Retorna els bytes del PDF, llestos per al botó de descàrrega.
    """

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    font = registrar_fonts(pdf)

    # ================= CAPÇALERA =================
    pdf.set_font(font, "B", 16)
    pdf.set_text_color(31, 41, 55)
    paragraf(pdf, font, 10, "Informe comparatiu d'anàlisi de biaix")
    pdf.set_draw_color(*ROSA)
    pdf.set_line_width(0.8)
    y = pdf.get_y()
    pdf.line(10, y, 200, y)
    pdf.ln(4)

    pdf.set_font(font, "", 9)
    pdf.set_text_color(*GRIS)
    paragraf(pdf, font, 5, "Sistema automàtic basat en Claude API")
    paragraf(pdf, font, 5, "Data: " + datetime.now().strftime("%d/%m/%Y  %H:%M"))
    pdf.ln(6)

    # ================= GRÀFIC COMPARATIU =================
    pdf.set_font(font, "B", 11)
    pdf.set_text_color(31, 41, 55)
    paragraf(pdf, font, 7, "Resum visual comparatiu")
    grafic = crear_grafic_comparatiu(data1, data2)
    y0 = pdf.get_y()
    pdf.image(grafic, x=10, y=y0, w=190)
    pdf.set_y(y0 + 190 * 3 / 7 + 6)

    def bloc_noticia(nom_noticia, data, titol):
        pdf.set_font(font, "B", 13)
        pdf.set_text_color(*ROSA)
        paragraf(pdf, font, 8, nom_noticia)
        if titol:
            pdf.set_font(font, "", 11)
            pdf.set_text_color(75, 85, 99)
            paragraf(pdf, font, 6, titol)
        pdf.ln(2)

        for dim in DIMENSIONS:
            dim_data = data.get(dim, {})
            intensitat = dim_data.get("intensitat", "nul·la")
            confianca = dim_data.get("confianca")
            fragment = dim_data.get("fragment", "N/A")
            explicacio = dim_data.get("explicacio", "")
            color = COLORS_INTENSITAT.get(intensitat, (107, 114, 128))
            etiqueta = ETIQUETES.get(intensitat, intensitat)

            pdf.set_font(font, "B", 10)
            pdf.set_text_color(31, 41, 55)
            paragraf(pdf, font, 6, NOMS_DIMENSIONS.get(dim, dim))

            pdf.set_font(font, "B", 12)
            pdf.set_text_color(*color)
            linia = etiqueta
            if confianca is not None:
                linia = linia + "   (" + str(confianca) + "% de confiança)"
            paragraf(pdf, font, 7, linia)

            pdf.set_font(font, "I", 9)
            pdf.set_text_color(75, 85, 99)
            paragraf(pdf, font, 5, '"' + str(fragment) + '"')

            pdf.set_font(font, "", 9)
            pdf.set_text_color(75, 85, 99)
            paragraf(pdf, font, 5, explicacio)
            pdf.ln(4)

        pdf.ln(2)

    bloc_noticia("Notícia 1", data1, titol1)

    pdf.set_draw_color(229, 231, 235)
    pdf.set_line_width(0.3)
    y = pdf.get_y()
    pdf.line(10, y, 200, y)
    pdf.ln(4)

    bloc_noticia("Notícia 2", data2, titol2)

    # ================= PEU =================
    pdf.ln(4)
    pdf.set_draw_color(229, 231, 235)
    pdf.set_line_width(0.3)
    y = pdf.get_y()
    pdf.line(10, y, 200, y)
    pdf.ln(3)

    pdf.set_font(font, "", 8)
    pdf.set_text_color(*GRIS)
    paragraf(
        pdf,
        font,
        4,
        "Aquest informe ha estat generat automàticament. El sistema és una eina "
        "per detectar patrons, no la veritat absoluta. És recomanable contrastar "
        "la informació amb múltiples fonts.",
    )
    paragraf(
        pdf,
        font,
        4,
        "Treball de Recerca 2026 - Arantxa Ruiz-Ruano Pedreira - "
        "Institut Vall d'Arús",
    )

    return bytes(pdf.output())


def generar_pdf(data, text_analitzat="", titol=""):
    """
    Genera l'informe en PDF.

    data            -> diccionari amb els resultats de l'anàlisi
    text_analitzat  -> el text original que s'ha analitzat

    Retorna els bytes del PDF, llestos per al botó de descàrrega.
    """

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    font = registrar_fonts(pdf)

    # ================= CAPÇALERA =================
    pdf.set_font(font, "B", 16)
    pdf.set_text_color(31, 41, 55)
    paragraf(pdf, font, 10, "Informe d'anàlisi de biaix")
    if titol:
        pdf.set_font(font, "", 12)
        pdf.set_text_color(75, 85, 99)
        paragraf(pdf, font, 7, titol)
    pdf.set_draw_color(*ROSA)
    pdf.set_line_width(0.8)
    y = pdf.get_y()
    pdf.line(10, y, 200, y)
    pdf.ln(4)

    pdf.set_font(font, "", 9)
    pdf.set_text_color(*GRIS)
    paragraf(pdf, font, 5, "Sistema automàtic basat en Claude API")
    paragraf(pdf, font, 5, "Data: " + datetime.now().strftime("%d/%m/%Y  %H:%M"))
    pdf.ln(6)

    # ================= GRÀFIC RESUM =================
    pdf.set_font(font, "B", 11)
    pdf.set_text_color(31, 41, 55)
    paragraf(pdf, font, 7, "Resum visual")
    grafic = crear_grafic_intensitats(data)
    y0 = pdf.get_y()
    pdf.image(grafic, x=10, y=y0, w=190)
    pdf.set_y(y0 + 190 * 2.6 / 7 + 4)  # avança sota la imatge
    pdf.ln(2)

    # ================= TEXT ANALITZAT =================
    if text_analitzat:
        pdf.set_font(font, "B", 11)
        pdf.set_text_color(31, 41, 55)
        paragraf(pdf, font, 7, "Text analitzat")

        fragment = text_analitzat
        if len(fragment) > 2000:
            fragment = fragment[:2000] + " [...]"

        pdf.set_font(font, "I", 9)
        pdf.set_text_color(75, 85, 99)
        paragraf(pdf, font, 5, fragment)
        pdf.ln(6)

    # ================= RESULTATS =================
    pdf.set_font(font, "B", 11)
    pdf.set_text_color(31, 41, 55)
    paragraf(pdf, font, 7, "Resultats")
    pdf.ln(2)

    for dim in DIMENSIONS:
        dim_data = data.get(dim, {})
        intensitat = dim_data.get("intensitat", "nul·la")
        confianca = dim_data.get("confianca")
        fragment = dim_data.get("fragment", "N/A")
        explicacio = dim_data.get("explicacio", "")
        criteri = RUBRICA.get(dim, {}).get(intensitat, "")

        color = COLORS_INTENSITAT.get(intensitat, (107, 114, 128))
        etiqueta = ETIQUETES.get(intensitat, intensitat)

        # Nom de la dimensió
        pdf.set_font(font, "B", 10)
        pdf.set_text_color(31, 41, 55)
        paragraf(pdf, font, 6, NOMS_DIMENSIONS.get(dim, dim))

        # Intensitat + confiança
        pdf.set_font(font, "B", 13)
        pdf.set_text_color(*color)
        linia = etiqueta
        if confianca is not None:
            linia = linia + "   (" + str(confianca) + "% de confiança)"
        paragraf(pdf, font, 7, linia)

        # Criteri de la rúbrica
        if criteri:
            pdf.set_font(font, "", 9)
            pdf.set_text_color(*GRIS)
            paragraf(pdf, font, 5, "Criteri de la rúbrica: " + criteri)

        # Fragment detectat
        pdf.set_font(font, "B", 9)
        pdf.set_text_color(31, 41, 55)
        paragraf(pdf, font, 6, "Fragment detectat:")

        pdf.set_font(font, "I", 9)
        pdf.set_text_color(75, 85, 99)
        paragraf(pdf, font, 5, '"' + str(fragment) + '"')

        # Explicació
        pdf.set_font(font, "B", 9)
        pdf.set_text_color(31, 41, 55)
        paragraf(pdf, font, 6, "Anàlisi:")

        pdf.set_font(font, "", 9)
        pdf.set_text_color(75, 85, 99)
        paragraf(pdf, font, 5, explicacio)

        pdf.ln(5)

    # ================= PEU =================
    pdf.ln(4)
    pdf.set_draw_color(229, 231, 235)
    pdf.set_line_width(0.3)
    y = pdf.get_y()
    pdf.line(10, y, 200, y)
    pdf.ln(3)

    pdf.set_font(font, "", 8)
    pdf.set_text_color(*GRIS)
    paragraf(
        pdf,
        font,
        4,
        "Aquest informe ha estat generat automàticament. El sistema és una eina "
        "per detectar patrons, no la veritat absoluta. És recomanable contrastar "
        "la informació amb múltiples fonts.",
    )
    paragraf(
        pdf,
        font,
        4,
        "Treball de Recerca 2026 - Arantxa Ruiz-Ruano Pedreira - "
        "Institut Vall d'Arús",
    )

    return bytes(pdf.output())
