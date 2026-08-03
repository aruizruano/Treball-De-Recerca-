# analizar_corpus_nou_b.py
# Procesar corpus_nou.csv (10 textos nuevos) - TEST DE GENERALIZACIÓN

import csv
import pandas as pd
import time
from detector_claude import analizar_texto_claude

print("=" * 70)
print("ANALIZANDO CORPUS NUEVO (10 TEXTOS) - TEST GENERALIZACIÓN")
print("=" * 70)

# Leer corpus_nou.csv
print("\n📖 Leyendo corpus_nou.csv...")
try:
    df = pd.read_csv("corpus_nou.csv")
    print(f"✅ Corpus nuevo cargado: {len(df)} textos")
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

# Preparar resultados
resultados = []
errores = []

# Procesar cada texto
print("\n🔄 Analizando textos...\n")

for idx, row in df.iterrows():
    texto_id = row["Id"]
    texto = row["Text"]
    categoria = row["Categoria"]

    print(
        f"[{idx+1}/{len(df)}] Analizando Id {texto_id} ({categoria[:20]}...)...",
        end=" ",
    )

    try:
        resultado = analizar_texto_claude(texto, verbose=False)

        if resultado["success"]:
            data = resultado["data"]

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
            print("OK")
        else:
            print(f"Error: {resultado['error']}")
            errores.append({"Id": texto_id, "error": resultado["error"]})

    except Exception as e:
        print(f"Exception: {str(e)}")
        errores.append({"Id": texto_id, "error": str(e)})

    time.sleep(1)

# Guardar
print(f"\n Guardando en resultados_b_nou.csv...")

try:
    df_resultados = pd.DataFrame(resultados)
    df_resultados.to_csv("resultados_b_nou.csv", index=False, encoding="utf-8")
    print(f"OK: {len(resultados)}/10 textos guardados")
except Exception as e:
    print(f"Error: {e}")

if errores:
    print(f"\nErrores: {len(errores)}")
    for err in errores:
        print(f"  Id {err['Id']}: {err['error']}")
else:
    print(f"\nSin errores - Generalizacion validada!")

print("\n" + "=" * 70)
print("SEMANA 3 COMPLETADA!")
print("=" * 70)
