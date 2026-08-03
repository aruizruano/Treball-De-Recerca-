# recuperar_errores_b.py
# Re-procesar los 4 textos que fallaron

import pandas as pd
import time
from detector_claude import analizar_texto_claude

print("=" * 70)
print("RECUPERANDO TEXTOS CON ERROR")
print("=" * 70)

# Leer corpus original
df_corpus = pd.read_csv("corpus.csv")

# Leer resultados actuales
df_resultados = pd.read_csv("resultados_b.csv")
ids_procesados = set(df_resultados["Id"].values)

# IDs con error
ids_error = [6, 7, 10, 16]

print(f"\n Reprocesando {len(ids_error)} textos con error...\n")

for id_texto in ids_error:
    print(f"Reprocesando Id {id_texto}...", end=" ")

    # Buscar el texto en el corpus
    fila_corpus = df_corpus[df_corpus["Id"] == id_texto]

    if fila_corpus.empty:
        print(" No encontrado en corpus")
        continue

    texto = fila_corpus.iloc[0]["Text"]
    categoria = fila_corpus.iloc[0]["Categoria"]
    ideologia = fila_corpus.iloc[0].get("Ideologia", "N/A")

    # Intentar procesar
    try:
        resultado = analizar_texto_claude(texto, verbose=False)

        if resultado["success"]:
            data = resultado["data"]

            # Crear fila
            nueva_fila = {
                "Id": id_texto,
                "Categoria": categoria,
                "Ideologia": ideologia,
                "biaix_intensitat": data["biaix"]["intensitat"],
                "biaix_fragment": data["biaix"]["fragment"],
                "biaix_explicacio": data["biaix"]["explicacio"],
                "desinformacio_intensitat": data["desinformacio"]["intensitat"],
                "desinformacio_fragment": data["desinformacio"]["fragment"],
                "desinformacio_explicacio": data["desinformacio"]["explicacio"],
                "emocional_intensitat": data["emocional"]["intensitat"],
                "emocional_fragment": data["emocional"]["fragment"],
                "emocional_explicacio": data["emocional"]["explicacio"],
            }

            # Agregar al dataframe
            df_resultados = pd.concat(
                [df_resultados, pd.DataFrame([nueva_fila])], ignore_index=True
            )
            print("✅")
        else:
            print(f" {resultado['error']}")

    except Exception as e:
        print(f" {str(e)}")

    time.sleep(1)

# Ordenar por Id y guardar
df_resultados = df_resultados.sort_values("Id").reset_index(drop=True)
df_resultados.to_csv("resultados_b.csv", index=False, encoding="utf-8")

print(f"\n Archivo actualizado: {len(df_resultados)} textos totales")
print("=" * 70)
