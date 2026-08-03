# generar_pdf_comparativa.py
# Generar PDF professional amb la comparativa de totes les fonts

import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak,
    Table,
    TableStyle,
    KeepTogether,
)
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT

print("=" * 70)
print("GENERANT PDF COMPARATIU")
print("=" * 70)

# ========================
# CARREGAR DADES
# ========================
print("\nCarregant dades...")

df_textos = pd.read_csv("textos_dossier.csv")
df_respuestas = pd.read_csv("respuestas_chatgpt_gemini.csv")
df_a_original = pd.read_csv("resultados.csv")
df_a_complet = pd.read_csv("resultados_complet.csv")
df_b_original = pd.read_csv("resultados_b.csv")
df_b_nou = pd.read_csv("resultados_b_nou.csv")

# Normalitzar noms de columnes de B
df_b_original = df_b_original.rename(
    columns={"desinformacio_intensitat": "desinfo_intensitat"}
)
df_b_nou = df_b_nou.rename(columns={"desinformacio_intensitat": "desinfo_intensitat"})

# Renombrar columnes de resultados_complet.csv
df_a_complet = df_a_complet.rename(
    columns={
        "biaix": "biaix_intensitat",
        "emocional": "emocional_intensitat",
        "desinfo": "desinfo_intensitat",
    }
)


# ========================
# FUNCIÓ: OBTENIR RESULTATS PER Id
# ========================
def obtenir_resultats(id_real):
    """Obté els resultats de les 4 fonts per un Id concret."""
    resultats = {
        "A": {"biaix": "-", "desinfo": "-", "emocional": "-"},
        "B": {"biaix": "-", "desinfo": "-", "emocional": "-"},
        "ChatGPT": {"biaix": "-", "desinfo": "-", "emocional": "-"},
        "Gemini": {"biaix": "-", "desinfo": "-", "emocional": "-"},
    }

    # Sistema A
    if id_real in df_a_original["Id"].values:
        fila = df_a_original[df_a_original["Id"] == id_real].iloc[0]
        resultats["A"]["biaix"] = fila["biaix_intensitat"]
        resultats["A"]["desinfo"] = fila["desinfo_intensitat"]
        resultats["A"]["emocional"] = fila["emocional_intensitat"]
    elif id_real in df_a_complet["Id"].values:
        fila = df_a_complet[df_a_complet["Id"] == id_real].iloc[0]
        resultats["A"]["biaix"] = fila["biaix_intensitat"]
        resultats["A"]["desinfo"] = fila["desinfo_intensitat"]
        resultats["A"]["emocional"] = fila["emocional_intensitat"]

    # Sistema B
    if id_real in df_b_original["Id"].values:
        fila = df_b_original[df_b_original["Id"] == id_real].iloc[0]
        resultats["B"]["biaix"] = fila["biaix_intensitat"]
        resultats["B"]["desinfo"] = fila["desinfo_intensitat"]
        resultats["B"]["emocional"] = fila["emocional_intensitat"]
    elif id_real in df_b_nou["Id"].values:
        fila = df_b_nou[df_b_nou["Id"] == id_real].iloc[0]
        resultats["B"]["biaix"] = fila["biaix_intensitat"]
        resultats["B"]["desinfo"] = fila["desinfo_intensitat"]
        resultats["B"]["emocional"] = fila["emocional_intensitat"]

    # ChatGPT i Gemini
    fila_resp = df_respuestas[df_respuestas["Id_real"] == id_real]
    if len(fila_resp) > 0:
        fila_resp = fila_resp.iloc[0]
        resultats["ChatGPT"]["biaix"] = str(fila_resp.get("chatgpt_biaix", "-"))
        resultats["ChatGPT"]["desinfo"] = str(fila_resp.get("chatgpt_desinfo", "-"))
        resultats["ChatGPT"]["emocional"] = str(fila_resp.get("chatgpt_emocional", "-"))
        resultats["Gemini"]["biaix"] = str(fila_resp.get("gemini_biaix", "-"))
        resultats["Gemini"]["desinfo"] = str(fila_resp.get("gemini_desinfo", "-"))
        resultats["Gemini"]["emocional"] = str(fila_resp.get("gemini_emocional", "-"))

    return resultats


# ========================
# GENERAR PDF
# ========================
print("\nGenerant PDF...")

doc = SimpleDocTemplate(
    "Comparativa_IA_TR.pdf",
    pagesize=A4,
    rightMargin=2 * cm,
    leftMargin=2 * cm,
    topMargin=2 * cm,
    bottomMargin=2 * cm,
)

styles = getSampleStyleSheet()

# Estils personalitzats
titol_principal = ParagraphStyle(
    "TitolPrincipal",
    parent=styles["Heading1"],
    fontSize=20,
    textColor=colors.HexColor("#2c3e50"),
    alignment=TA_CENTER,
    spaceAfter=20,
)

subtitol = ParagraphStyle(
    "Subtitol",
    parent=styles["Heading2"],
    fontSize=14,
    textColor=colors.HexColor("#34495e"),
    spaceAfter=12,
)

text_style = ParagraphStyle(
    "TextStyle",
    parent=styles["Normal"],
    fontSize=10,
    alignment=TA_JUSTIFY,
    spaceAfter=8,
)

text_petit = ParagraphStyle(
    "TextPetit",
    parent=styles["Normal"],
    fontSize=9,
    alignment=TA_JUSTIFY,
    leftIndent=10,
    rightIndent=10,
    spaceAfter=6,
)

story = []

# ========================
# PORTADA
# ========================
story.append(Paragraph("COMPARATIVA D'ANÀLISI IA", titol_principal))
story.append(Paragraph("Treball de Recerca", styles["Heading2"]))
story.append(Spacer(1, 20))
story.append(
    Paragraph(
        "Detecció de biaix ideològic, desinformació i llenguatge emocional en textos polítics",
        text_style,
    )
)
story.append(Spacer(1, 30))

info = """
<b>Autora:</b> Arantxa Ruiz-Ruano Pedreira<br/>
<b>Tutora:</b> Elena Vaquerizo<br/>
<b>Centre:</b> Institut Vall d'Arús<br/>
<b>Curs:</b> 2026-2027<br/><br/>

<b>Textos analitzats:</b> 14 (els mateixos que enviats a l'expert)<br/>
<b>Fonts d'anàlisi:</b> 4 sistemes automàtics + expert humà<br/>
"""
story.append(Paragraph(info, text_style))
story.append(Spacer(1, 40))

metodologia = """
<b>Metodologia</b><br/><br/>
Aquest document recull les respostes de quatre fonts d'anàlisi diferents sobre els mateixos 14 textos polítics:
<br/><br/>
1. <b>Sistema A:</b> Detector propi basat en regles i llistes de paraules clau.<br/>
2. <b>Sistema B:</b> Detector basat en Claude API (Anthropic) amb prompt engineering.<br/>
3. <b>ChatGPT:</b> Anàlisi manual amb el model GPT (OpenAI).<br/>
4. <b>Gemini:</b> Anàlisi manual amb el model Gemini (Google).<br/>
5. <b>Expert humà:</b> A completar amb la valoració del grup POLCOM-GRP de la UPF.<br/><br/>

Totes les fonts avaluen tres dimensions: <b>biaix ideològic</b>, <b>desinformació</b> i <b>llenguatge emocional</b>, 
puntuant amb la mateixa escala: <i>nul·la, lleu, moderada, alta</i>.
"""
story.append(Paragraph(metodologia, text_style))
story.append(PageBreak())

# ========================
# TAULA RESUM GENERAL
# ========================
story.append(Paragraph("Taula resum general", titol_principal))
story.append(Spacer(1, 20))

# Crear taula resum
capsalera_resum = ["Text", "Dim.", "Sist. A", "Sist. B", "ChatGPT", "Gemini", "Expert"]
dades_resum = [capsalera_resum]

for _, fila in df_textos.iterrows():
    num = fila["num_dossier"]
    id_real = fila["Id_real"]
    resultats = obtenir_resultats(id_real)

    # 3 files per text (una per dimensió)
    dades_resum.append(
        [
            str(num) if num else "",
            "Biaix",
            resultats["A"]["biaix"],
            resultats["B"]["biaix"],
            resultats["ChatGPT"]["biaix"],
            resultats["Gemini"]["biaix"],
            "",
        ]
    )
    dades_resum.append(
        [
            "",
            "Desinf.",
            resultats["A"]["desinfo"],
            resultats["B"]["desinfo"],
            resultats["ChatGPT"]["desinfo"],
            resultats["Gemini"]["desinfo"],
            "",
        ]
    )
    dades_resum.append(
        [
            "",
            "Emoc.",
            resultats["A"]["emocional"],
            resultats["B"]["emocional"],
            resultats["ChatGPT"]["emocional"],
            resultats["Gemini"]["emocional"],
            "",
        ]
    )

taula_resum = Table(
    dades_resum,
    colWidths=[1.2 * cm, 1.8 * cm, 2.2 * cm, 2.2 * cm, 2.2 * cm, 2.2 * cm, 2.2 * cm],
)
taula_resum.setStyle(
    TableStyle(
        [
            # Capçalera
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c3e50")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 10),
            ("ALIGN", (0, 0), (-1, 0), "CENTER"),
            # Cos
            ("FONTSIZE", (0, 1), (-1, -1), 8),
            ("ALIGN", (0, 1), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            # Bordes
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            # Alternar colors
            (
                "ROWBACKGROUNDS",
                (0, 1),
                (-1, -1),
                [colors.white, colors.HexColor("#ecf0f1")],
            ),
            # Padding
            ("LEFTPADDING", (0, 0), (-1, -1), 3),
            ("RIGHTPADDING", (0, 0), (-1, -1), 3),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]
    )
)

story.append(taula_resum)
story.append(PageBreak())

# ========================
# DETALL DE CADA TEXT
# ========================
story.append(Paragraph("Detall per text", titol_principal))
story.append(Spacer(1, 15))

for _, fila in df_textos.iterrows():
    num = fila["num_dossier"]
    id_real = fila["Id_real"]
    text = fila["Text"]
    categoria = fila["Categoria"]

    # Truncar text si és molt llarg
    text_mostrat = text if len(text) < 800 else text[:800] + "..."

    resultats = obtenir_resultats(id_real)

    # Contingut del text
    contingut = []
    contingut.append(
        Paragraph(f"<b>Text {num}</b> (Id: {id_real}) — <i>{categoria}</i>", subtitol)
    )
    contingut.append(Paragraph(text_mostrat, text_petit))
    contingut.append(Spacer(1, 10))

    # Taula de resultats per aquest text
    dades_text = [
        ["Font", "Biaix", "Desinformació", "Emocional"],
        [
            "Sistema A (regles)",
            resultats["A"]["biaix"],
            resultats["A"]["desinfo"],
            resultats["A"]["emocional"],
        ],
        [
            "Sistema B (Claude)",
            resultats["B"]["biaix"],
            resultats["B"]["desinfo"],
            resultats["B"]["emocional"],
        ],
        [
            "ChatGPT (GPT)",
            resultats["ChatGPT"]["biaix"],
            resultats["ChatGPT"]["desinfo"],
            resultats["ChatGPT"]["emocional"],
        ],
        [
            "Gemini (Google)",
            resultats["Gemini"]["biaix"],
            resultats["Gemini"]["desinfo"],
            resultats["Gemini"]["emocional"],
        ],
        ["Expert humà", "", "", ""],
    ]

    taula_text = Table(dades_text, colWidths=[4 * cm, 3 * cm, 3 * cm, 3 * cm])
    taula_text.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#34495e")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 10),
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                ("FONTSIZE", (0, 1), (-1, -1), 9),
                ("ALIGN", (1, 1), (-1, -1), "CENTER"),
                ("ALIGN", (0, 1), (0, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [colors.white, colors.HexColor("#ecf0f1")],
                ),
                # Ressaltar fila d'expert
                ("BACKGROUND", (0, 5), (-1, 5), colors.HexColor("#fff3cd")),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )

    contingut.append(taula_text)
    contingut.append(Spacer(1, 20))

    story.append(KeepTogether(contingut))

# ========================
# CONSTRUIR PDF
# ========================
doc.build(story)

print("\n" + "=" * 70)
print("PDF GENERAT CORRECTAMENT!")
print("=" * 70)
print("\nArxiu: Comparativa_IA_TR.pdf")
print("Ubicació: TreballDeRecerca/")
