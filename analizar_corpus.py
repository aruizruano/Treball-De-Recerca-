# analizar_corpus.py
# Recorre todo el corpus, analiza cada texto y guarda los resultados en resultados.csv

import pandas as pd
from detector import analizar_texto

# 1. Cargar el corpus
corpus = pd.read_csv("corpus.csv", encoding="utf-8-sig")
print("Textos cargados:", len(corpus))

# 2. Recorrer fila por fila y analizar
filas_resultado = []

for indice, fila in corpus.iterrows():
    texto = fila["Text"]

    # Control de errores: si el texto está vacío, lo saltamos
    if pd.isna(texto) or str(texto).strip() == "":
        print("Texto", fila["Id"], "vacío -> saltado")
        continue

    analisis = analizar_texto(str(texto))

    # Aplanamos el resultado en una fila de tabla
    filas_resultado.append(
        {
            "Id": fila["Id"],
            "Categoria": fila["Categoria"],
            "Ideologia": fila["Ideologia"],
            "num_palabras": analisis["num_palabras"],
            "densidad_senales": analisis["densidad_senales"],
            "biaix_intensitat": analisis["biaix_ideologic"]["intensitat"],
            "biaix_confianza": analisis["biaix_ideologic"]["confianza"],
            "biaix_palabras": ", ".join(
                analisis["biaix_ideologic"]["palabras_valorativas"]
            ),
            "biaix_enmarcado": ", ".join(
                analisis["biaix_ideologic"]["palabras_enmarcado"]
            ),
            "biaix_verbos": ", ".join(analisis["biaix_ideologic"]["verbos_cargados"]),
            "emocional_intensitat": analisis["llenguatge_emocional"]["intensitat"],
            "emocional_confianza": analisis["llenguatge_emocional"]["confianza"],
            "emocional_identidad": ", ".join(
                analisis["llenguatge_emocional"]["apelaciones_identidad"]
            ),
            "emocional_palabras": ", ".join(
                analisis["llenguatge_emocional"]["palabras_encontradas"]
            ),
            "emocional_urgencia": ", ".join(
                analisis["llenguatge_emocional"]["frases_urgencia"]
            ),
            "emocional_repeticiones": ", ".join(
                analisis["llenguatge_emocional"]["repeticiones"]
            ),
            "emocional_mayusculas": ", ".join(
                analisis["llenguatge_emocional"]["mayusculas"]
            ),
            "desinfo_intensitat": analisis["desinformacio"]["intensitat"],
            "desinfo_indicios": " | ".join(analisis["desinformacio"]["indicios"]),
            "desinfo_generaliza": ", ".join(
                analisis["desinformacio"]["generalizaciones"]
            ),
            "desinfo_mensaje": analisis["desinformacio"]["mensaje"],
        }
    )

    print("Texto", fila["Id"], "analizado")

# 3. Guardar todo en un CSV nuevo
resultados = pd.DataFrame(filas_resultado)
resultados.to_csv("resultados.csv", index=False, encoding="utf-8-sig")

print("\nListo. Guardado en resultados.csv")
print(
    resultados[["Id", "biaix_intensitat", "emocional_intensitat", "desinfo_intensitat"]]
)
