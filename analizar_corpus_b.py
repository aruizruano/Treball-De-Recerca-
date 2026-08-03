# analizar_corpus_b.py
# Script para analizar todos los textos del corpus.csv con Claude

import csv
import json
import time
import pandas as pd
from detector_claude import analizar_texto_claude

print("=" * 70)
print("ANALIZANDO CORPUS COMPLETO CON SISTEMA B (PROMPT v3)")
print("=" * 70)

# Leer corpus.csv
print("\n Leyendo corpus.csv...")
try:
    df = pd.read_csv("corpus.csv")
    print(f" Corpus cargado: {len(df)} textos")
except Exception as e:
    print(f" Error al leer corpus.csv: {e}")
    exit(1)

# Preparar resultados
resultados = []
errores = []

# Procesar cada texto
print("\n Analizando textos...\n")

for idx, row in df.iterrows():
    texto_id = row["Id"]
    texto = row["Text"]
    categoria = row["Categoria"]

    print(
        f"[{idx+1}/{len(df)}] Analizando Id {texto_id} ({categoria[:20]}...)...",
        end=" ",
    )

    try:
        # Llamar a Claude
        resultado = analizar_texto_claude(texto, verbose=False)

        if resultado["success"]:
            # Extraer datos
            data = resultado["data"]

            # Guardar resultado
            fila = {
                "Id": texto_id,
                "Categoria": categoria,
                "Ideologia": row.get("Ideologia", "N/A"),
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
            resultados.append(fila)
            print("✅")
        else:
            print(f" Error: {resultado['error']}")
            errores.append({"Id": texto_id, "error": resultado["error"]})

    except Exception as e:
        print(f" Excepción: {str(e)}")
        errores.append({"Id": texto_id, "error": str(e)})

    # Esperar 1 segundo (rate limit de Claude)
    time.sleep(1)

# Guardar resultados en CSV
print(f"\n Guardando resultados en resultados_b.csv...")

try:
    df_resultados = pd.DataFrame(resultados)
    df_resultados.to_csv("resultados_b.csv", index=False, encoding="utf-8")
    print(f" {len(resultados)}/24 textos guardados correctamente")
except Exception as e:
    print(f" Error guardando CSV: {e}")

# Reporte de errores
if errores:
    print(f"\n  {len(errores)} errores detectados:")
    for err in errores:
        print(f"   - Id {err['Id']}: {err['error']}")
else:
    print(f"\n SIN ERRORES - Todo procesado correctamente")

print("\n" + "=" * 70)
print("SEMANA 2 COMPLETADA!")
print("=" * 70)
print(f"\n Resultados guardados en: resultados_b.csv")
print(f" Total procesados: {len(resultados)}")
