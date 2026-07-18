# app.py
# Interfaz web del detector. Se ejecuta con:  streamlit run app.py
# No usa ninguna IA: por dentro llama a mi propio detector de reglas.

import streamlit as st
import pandas as pd
from detector import analizar_texto

st.set_page_config(page_title="Detector de biaix", page_icon="🔍")

st.title("🔍 Detector de biaix i desinformació")
st.caption("Sistema de detecció basat en regles · Treball de Recerca · Arantxa")


def mostrar_barra(intensitat):
    """Muestra la intensidad con un color según el nivel."""
    niveles = ["nul·la", "lleu", "moderada", "alta"]
    pos = niveles.index(intensitat)
    st.progress((pos + 1) / 4)
    if intensitat == "nul·la":
        st.success(f"Intensitat: {intensitat}")
    elif intensitat == "lleu":
        st.info(f"Intensitat: {intensitat}")
    elif intensitat == "moderada":
        st.warning(f"Intensitat: {intensitat}")
    else:
        st.error(f"Intensitat: {intensitat}")


def mostrar_dimension(titulo, datos, detalles):
    st.subheader(titulo)
    mostrar_barra(datos["intensitat"])

    encontrado = False
    for etiqueta, clave in detalles:
        valores = datos.get(clave, [])
        if valores:
            encontrado = True
            st.write(f"**{etiqueta}:** {', '.join(valores)}")

    if not encontrado:
        st.write("_No s'han trobat indicadors._")

    if "confianza" in datos:
        st.caption(f"Confiança de la detecció: {datos['confianza']}")


tab1, tab2 = st.tabs(["Analitzar un text", "Analitzar un CSV"])

with tab1:
    texto = st.text_area(
        "Enganxa aquí el text polític que vols analitzar:",
        height=200,
        placeholder="Per exemple, una publicació de TikTok, un tuit o un titular...",
    )

    if st.button("Analitzar", type="primary"):
        if not texto.strip():
            st.warning("Cal enganxar algun text primer.")
        else:
            r = analizar_texto(texto)

            col1, col2 = st.columns(2)
            col1.metric("Paraules", r["num_palabras"])
            col2.metric("Densitat", f'{r["densidad_senales"]} / 100 paraules')

            if r["num_palabras"] < 40:
                st.info("Text molt curt: les conclusions són poc sòlides.")

            st.divider()

            mostrar_dimension(
                "Biaix ideològic",
                r["biaix_ideologic"],
                [
                    ("Adjectius valoratius", "palabras_valorativas"),
                    ("Paraules d'emmarcament", "palabras_enmarcado"),
                    ("Verbs carregats", "verbos_cargados"),
                ],
            )

            st.divider()

            mostrar_dimension(
                "Llenguatge emocional",
                r["llenguatge_emocional"],
                [
                    ("Paraules emocionals", "palabras_encontradas"),
                    ("Apel·lacions a la identitat", "apelaciones_identidad"),
                    ("Frases d'urgència", "frases_urgencia"),
                    ("Repeticions (anàfora)", "repeticiones"),
                ],
            )

            st.divider()

            d = r["desinformacio"]
            st.subheader("Desinformació")
            mostrar_barra(d["intensitat"])
            if d["indicios"]:
                for i in d["indicios"]:
                    st.write(f"- {i}")
                st.warning(d["mensaje"])
            else:
                st.write(f"_{d['mensaje']}_")
            st.caption(
                "Aquest sistema no pot verificar si una dada és certa o falsa: "
                "només detecta senyals dins del text."
            )

with tab2:
    archivo = st.file_uploader("Puja el teu corpus.csv", type="csv")

    if archivo is not None:
        corpus = pd.read_csv(archivo, encoding="utf-8-sig")
        st.success(f"{len(corpus)} textos carregats.")

        filas = []
        for _, fila in corpus.iterrows():
            texto = str(fila["Text"])
            if not texto.strip():
                continue
            a = analizar_texto(texto)
            filas.append(
                {
                    "Id": fila["Id"],
                    "Categoria": fila["Categoria"],
                    "Paraules": a["num_palabras"],
                    "Densitat": a["densidad_senales"],
                    "Biaix": a["biaix_ideologic"]["intensitat"],
                    "Emocional": a["llenguatge_emocional"]["intensitat"],
                    "Desinformació": a["desinformacio"]["intensitat"],
                }
            )

        st.dataframe(pd.DataFrame(filas))
