# comparativa_ia_manual.py
# Script interactiu per registrar respostes de ChatGPT i Gemini

import pandas as pd
import webbrowser
import os

print("=" * 70)
print("COMPARATIVA MANUAL AMB ChatGPT I Gemini")
print("=" * 70)

# Carregar textos del dossier
df_dossier = pd.read_csv("textos_dossier.csv")

# Carregar (o crear) el CSV de respostes
if os.path.exists("respuestas_chatgpt_gemini.csv"):
    df_respuestas = pd.read_csv("respuestas_chatgpt_gemini.csv")
else:
    df_respuestas = df_dossier.copy()
    df_respuestas["chatgpt_biaix"] = ""
    df_respuestas["chatgpt_desinfo"] = ""
    df_respuestas["chatgpt_emocional"] = ""
    df_respuestas["gemini_biaix"] = ""
    df_respuestas["gemini_desinfo"] = ""
    df_respuestas["gemini_emocional"] = ""

# FIX: Convertir totes les columnes de respostes a text (per evitar error de float)
for col in [
    "chatgpt_biaix",
    "chatgpt_desinfo",
    "chatgpt_emocional",
    "gemini_biaix",
    "gemini_desinfo",
    "gemini_emocional",
]:
    df_respuestas[col] = df_respuestas[col].astype("object")

# PROMPT que copiem als models
PROMPT = """Analitza aquest text polític segons la següent rúbrica.

DIMENSIONS A AVALUAR:
1. BIAIX IDEOLÒGIC: Presentar la realitat de forma tendenciosa favorint una ideologia.
2. DESINFORMACIÓ: Presentar informació falsa o enganyosa com si fos veritat.
3. LLENGUATGE EMOCIONAL: Ús de recursos retòrics per manipular emocions.

ESCALA (per a cada dimensió):
- nul·la: Cap indici
- lleu: 1-2 indicis aïllats
- moderada: 3-5 indicis coordinats
- alta: 6+ indicis, patró sistemàtic

TEXT A ANALITZAR:
{text}

RESPOSTA (només JSON, sense explicacions):
{{
  "biaix": "nul·la|lleu|moderada|alta",
  "desinformacio": "nul·la|lleu|moderada|alta",
  "emocional": "nul·la|lleu|moderada|alta"
}}"""

# INTENSITATS VÀLIDES
INTENSITATS = ["nul·la", "lleu", "moderada", "alta"]


def demanar_intensitat(nom_dim):
    """Demana intensitat validant que sigui correcta."""
    while True:
        resp = input(f"   {nom_dim}: ").strip().lower()
        if resp in INTENSITATS:
            return resp
        elif resp == "nula":
            return "nul·la"
        elif resp == "":
            return ""
        else:
            print(f"   ! Resposta invàlida. Opcions: {', '.join(INTENSITATS)}")


# Detectar textos pendents
completats_chatgpt = df_respuestas["chatgpt_biaix"].notna().sum()
completats_gemini = df_respuestas["gemini_biaix"].notna().sum()

print(f"   ChatGPT: {completats_chatgpt}/14 completats")
print(f"   Gemini:  {completats_gemini}/14 completats")

# Menú
print("\nQuè vols fer?")
print("   1. Processar TOTS els textos (ChatGPT + Gemini)")
print("   2. Processar només ChatGPT")
print("   3. Processar només Gemini")
print("   4. Processar un text específic")
print("   0. Sortir")

opcio = input("\nOpció: ").strip()

if opcio == "0":
    print("Fins la propera!")
    exit()

# Determinar quins models processar
models = []
if opcio == "1":
    models = ["chatgpt", "gemini"]
elif opcio == "2":
    models = ["chatgpt"]
elif opcio == "3":
    models = ["gemini"]
elif opcio == "4":
    num = int(input("Número de text (1-14): "))
    df_dossier = df_dossier[df_dossier["num_dossier"] == num]
    models = ["chatgpt", "gemini"]

# URLs dels models
URLS = {"chatgpt": "https://chat.openai.com", "gemini": "https://gemini.google.com"}

# Processar cada text
for _, fila in df_dossier.iterrows():
    num = fila["num_dossier"]
    id_real = fila["Id_real"]
    text = fila["Text"]

    print("\n" + "=" * 70)
    print(f"TEXT {num}/14 (Id real: {id_real})")
    print("=" * 70)
    print(f"\nText: {text[:200]}...")

    # Preparar prompt amb el text
    prompt_final = PROMPT.format(text=text)

    # Guardar prompt en un arxiu temporal per copiar fàcilment
    with open("prompt_actual.txt", "w", encoding="utf-8") as f:
        f.write(prompt_final)

    print(f"\n>>> Prompt guardat a 'prompt_actual.txt' <<<")
    print(">>> Obre l'arxiu i copia'l al model <<<")

    for model in models:
        # Comprovar si ja està omplert
        col_biaix = f"{model}_biaix"
        val_actual = str(
            df_respuestas.loc[df_respuestas["num_dossier"] == num, col_biaix].values[0]
        )

        if val_actual != "" and val_actual != "nan" and val_actual.lower() != "nan":

            skip = (
                input(f"\n{model.upper()} ja té resposta. Sobreescriure? (s/n): ")
                .strip()
                .lower()
            )
            if skip != "s":
                continue

        print(f"\n--- {model.upper()} ---")
        obrir = input(f"Obrir {URLS[model]}? (s/n): ").strip().lower()
        if obrir == "s":
            webbrowser.open(URLS[model])

        print(
            f"\nCopia el prompt (està a 'prompt_actual.txt') i enganxa'l a {model.upper()}"
        )
        print(f"Després enganxa aquí les 3 intensitats:")

        biaix = demanar_intensitat("biaix")
        desinfo = demanar_intensitat("desinformació")
        emocional = demanar_intensitat("emocional")

        # Guardar
        idx = df_respuestas[df_respuestas["num_dossier"] == num].index[0]
        df_respuestas.loc[idx, f"{model}_biaix"] = biaix
        df_respuestas.loc[idx, f"{model}_desinfo"] = desinfo
        df_respuestas.loc[idx, f"{model}_emocional"] = emocional

        # Guardar al CSV després de cada resposta (per si falla)
        df_respuestas.to_csv(
            "respuestas_chatgpt_gemini.csv", index=False, encoding="utf-8"
        )
        print(f"OK, guardat a respuestas_chatgpt_gemini.csv")

# Eliminar arxiu temporal
if os.path.exists("prompt_actual.txt"):
    os.remove("prompt_actual.txt")

print("\n" + "=" * 70)
print("COMPARATIVA COMPLETADA!")
print("=" * 70)
print("\nArxiu final: respuestas_chatgpt_gemini.csv")
