# analisis_discrepancias.py
# Anàlisi qualitativa: on discrepen A i B i per què?

import pandas as pd

print("=" * 70)
print("ANÀLISI DE DISCREPÀNCIES A vs B")
print("=" * 70)

# Mapa d'intensitat a número (per calcular diferències)
mapa = {"nul·la": 0, "lleu": 1, "moderada": 2, "alta": 3}

# ========================
# LLEGIR DADES
# ========================
merged_original = pd.read_csv("comparativa_original.csv")
merged_nou = pd.read_csv("comparativa_nou.csv")
corpus_original = pd.read_csv("corpus.csv")
corpus_nou = pd.read_csv("corpus_nou.csv")


# ========================
# CALCULAR MAGNITUD DE DISCREPÀNCIA
# ========================
def calcular_discrepancia(df):
    df = df.copy()
    for dim in ["biaix", "desinfo", "emocional"]:
        col_a = f"{dim}_intensitat_A"
        col_b = f"{dim}_intensitat_B"
        df[f"{dim}_num_A"] = df[col_a].map(mapa)
        df[f"{dim}_num_B"] = df[col_b].map(mapa)
        df[f"{dim}_diff"] = df[f"{dim}_num_B"] - df[f"{dim}_num_A"]

    # Discrepància total (suma absoluta de diferències)
    df["discrepancia_total"] = (
        df[["biaix_diff", "desinfo_diff", "emocional_diff"]].abs().sum(axis=1)
    )
    return df


merged_original = calcular_discrepancia(merged_original)
merged_nou = calcular_discrepancia(merged_nou)

# ========================
# TOP 5 DISCREPÀNCIES EN TEXTOS ORIGINALS
# ========================
print("\n" + "=" * 70)
print("TOP 5 TEXTOS ON A i B DIVERGEIXEN MÉS (Textos originals)")
print("=" * 70)

top_original = merged_original.nlargest(5, "discrepancia_total")

for idx, row in top_original.iterrows():
    id_text = row["Id"]
    texto = corpus_original[corpus_original["Id"] == id_text].iloc[0]["Text"]

    print(f"\n--- TEXT ID {id_text} ---")
    print(f"Text: {texto[:150]}...")
    print(f"Discrepància total: {row['discrepancia_total']}")
    print(
        f"BIAIX:      A={row['biaix_intensitat_A']:10} | B={row['biaix_intensitat_B']:10} | Diff: {row['biaix_diff']:+d}"
    )
    print(
        f"DESINFO:    A={row['desinfo_intensitat_A']:10} | B={row['desinfo_intensitat_B']:10} | Diff: {row['desinfo_diff']:+d}"
    )
    print(
        f"EMOCIONAL:  A={row['emocional_intensitat_A']:10} | B={row['emocional_intensitat_B']:10} | Diff: {row['emocional_diff']:+d}"
    )

# ========================
# ANÀLISI: OU DETECTA MÉS QUÈ?
# ========================
print("\n" + "=" * 70)
print("PATRÓ GENERAL: QUI DETECTA MÉS?")
print("=" * 70)

for dim in ["biaix", "desinfo", "emocional"]:
    diff_original = merged_original[f"{dim}_diff"].mean()
    diff_nou = merged_nou[f"{dim}_diff"].mean()

    print(f"\n{dim.upper()}:")
    print(
        f"   Textos originals: {'B > A' if diff_original > 0 else 'A > B'} (diferència mitjana: {diff_original:+.2f})"
    )
    print(
        f"   Textos nous:      {'B > A' if diff_nou > 0 else 'A > B'} (diferència mitjana: {diff_nou:+.2f})"
    )

# ========================
# EL GRAN CONTRAST: TEXTOS ON A DIU "NUL·LA" PERO B DIU "ALTA"
# ========================
print("\n" + "=" * 70)
print("CASOS EXTREMS: A diu NUL·LA pero B diu MODERADA o ALTA")
print("=" * 70)

print("\nEN TEXTOS ORIGINALS:")
extrems_orig = merged_original[
    (merged_original["biaix_num_A"] == 0) & (merged_original["biaix_num_B"] >= 2)
]
if len(extrems_orig) > 0:
    for idx, row in extrems_orig.iterrows():
        texto = corpus_original[corpus_original["Id"] == row["Id"]].iloc[0]["Text"]
        print(f"   Id {row['Id']}: A=nul·la, B={row['biaix_intensitat_B']}")
        print(f"      '{texto[:120]}...'")
else:
    print("   Cap cas.")

print("\nEN TEXTOS NOUS:")
extrems_nou = merged_nou[
    (merged_nou["biaix_num_A"] == 0) & (merged_nou["biaix_num_B"] >= 2)
]
if len(extrems_nou) > 0:
    for idx, row in extrems_nou.iterrows():
        texto = corpus_nou[corpus_nou["Id"] == row["Id"]].iloc[0]["Text"]
        print(f"   Id {row['Id']}: A=nul·la, B={row['biaix_intensitat_B']}")
        print(f"      '{texto[:120]}...'")
else:
    print("   Cap cas.")

# ========================
# GUARDAR RESULTATS PER AL TR
# ========================
print("\n" + "=" * 70)
print("GUARDANT ANÀLISI EN CSV")
print("=" * 70)

top_original.to_csv("discrepancias_originales_top5.csv", index=False, encoding="utf-8")
merged_nou.to_csv("discrepancias_nuevos_todos.csv", index=False, encoding="utf-8")

print("\nArxius generats:")
print("   - discrepancias_originales_top5.csv")
print("   - discrepancias_nuevos_todos.csv")

print("\n" + "=" * 70)
print("ANÀLISI COMPLETADA!")
print("=" * 701)
