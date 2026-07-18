# analizar_tot.py
# Analiza los DOS corpus (el original y el nuevo) y marca de cuál viene cada texto.
# Esto es lo que permite medir el SOBREAJUSTE: comparar cómo se comporta el
# detector con textos que se usaron para ajustarlo vs textos que nunca ha visto.

import pandas as pd
from detector import analizar_texto


def analizar_corpus(archivo, origen):
    """Analiza un CSV y devuelve una lista de resultados marcados con su origen."""
    corpus = pd.read_csv(archivo, encoding="utf-8-sig")
    filas = []

    for _, fila in corpus.iterrows():
        texto = str(fila["Text"])
        if not texto.strip() or "[PENDENT]" in texto:
            continue

        a = analizar_texto(texto)
        filas.append(
            {
                "Id": fila["Id"],
                "origen": origen,
                "Categoria": fila["Categoria"],
                "Ideologia": fila["Ideologia"],
                "num_palabras": a["num_palabras"],
                "densidad": a["densidad_senales"],
                "biaix": a["biaix_ideologic"]["intensitat"],
                "emocional": a["llenguatge_emocional"]["intensitat"],
                "desinfo": a["desinformacio"]["intensitat"],
            }
        )

    print(f"  {archivo}: {len(filas)} textos analitzats")
    return filas


def main():
    print("Analitzant...")
    filas = analizar_corpus("corpus.csv", "original")
    filas += analizar_corpus("corpus_nou.csv", "nou")

    resultados = pd.DataFrame(filas)
    resultados.to_csv("resultados_complet.csv", index=False, encoding="utf-8-sig")

    # Convertimos las intensidades a números para poder hacer medias.
    valores = {"nul·la": 0, "lleu": 1, "moderada": 2, "alta": 3}
    for col in ["biaix", "emocional", "desinfo"]:
        resultados[col + "_n"] = resultados[col].map(valores)

    print()
    print("=" * 55)
    print("LA PROVA DEL SOBREAJUSTAMENT")
    print("=" * 55)
    print("Intensitat mitjana detectada (0=nul·la, 3=alta):")
    print()
    tabla = (
        resultados.groupby("origen")[["biaix_n", "emocional_n", "desinfo_n"]]
        .mean()
        .round(2)
    )
    print(tabla.to_string())
    print()
    print("Si els textos NOUS puntuen molt més baix, vol dir que el detector")
    print("estava ajustat als textos originals i generalitza pitjor.")
    print()
    print("Densitat mitjana de senyals (per 100 paraules):")
    print(resultados.groupby("origen")["densidad"].mean().round(2).to_string())
    print()
    print("Guardat a resultados_complet.csv")


if __name__ == "__main__":
    main()
