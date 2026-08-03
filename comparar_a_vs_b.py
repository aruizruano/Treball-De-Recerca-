# comparar_a_vs_b.py
# Comparativa Sistema A (regles) vs Sistema B (Claude API)

import pandas as pd

print("=" * 70)
print("COMPARATIVA SISTEMA A vs SISTEMA B")
print("=" * 70)

# ========================
# LLEGIR ARXIUS
# ========================
print("\n1. Llegint arxius...")

# Sistema A
df_a_original = pd.read_csv("resultados.csv")
df_a_complet = pd.read_csv("resultados_complet.csv")

# Sistema B
df_b_original = pd.read_csv("resultados_b.csv")
df_b_nou = pd.read_csv("resultados_b_nou.csv")

print(f"   Sistema A original: {len(df_a_original)} textos")
print(f"   Sistema A complet: {len(df_a_complet)} textos")
print(f"   Sistema B original: {len(df_b_original)} textos")
print(f"   Sistema B nou: {len(df_b_nou)} textos")

# ========================
# NORMALITZAR NOMS DE COLUMNES
# ========================
# Sistema B usa "desinformacio_intensitat", Sistema A usa "desinfo_intensitat"
# Renombrem al Sistema B per fer-los coincidir

df_b_original = df_b_original.rename(
    columns={"desinformacio_intensitat": "desinfo_intensitat"}
)
df_b_nou = df_b_nou.rename(columns={"desinformacio_intensitat": "desinfo_intensitat"})

# ========================
# COMPARATIVA 1: TEXTOS ORIGINALS (24 textos)
# ========================
print("\n" + "=" * 70)
print("COMPARATIVA 1: TEXTOS ORIGINALS (24 textos)")
print("=" * 70)

# Fusionem A i B per Id
merged_original = pd.merge(
    df_a_original[
        [
            "Id",
            "Categoria",
            "biaix_intensitat",
            "desinfo_intensitat",
            "emocional_intensitat",
        ]
    ],
    df_b_original[
        ["Id", "biaix_intensitat", "desinfo_intensitat", "emocional_intensitat"]
    ],
    on="Id",
    suffixes=("_A", "_B"),
)

print(f"\nTextos comparats: {len(merged_original)}")

# Calcular acord per dimensió
for dim in ["biaix", "desinfo", "emocional"]:
    col_a = f"{dim}_intensitat_A"
    col_b = f"{dim}_intensitat_B"

    acord = (merged_original[col_a] == merged_original[col_b]).sum()
    total = len(merged_original)
    pct = (acord / total) * 100

    print(f"\n{dim.upper()}:")
    print(f"   Acord total: {acord}/{total} ({pct:.1f}%)")

    # Distribució de discrepàncies
    discrepancies = merged_original[merged_original[col_a] != merged_original[col_b]]
    if len(discrepancies) > 0:
        print(f"   Discrepàncies: {len(discrepancies)}")

# ========================
# COMPARATIVA 2: TEXTOS NOUS (9 textos)
# ========================
print("\n" + "=" * 70)
print("COMPARATIVA 2: TEXTOS NOUS (9 textos) - GENERALITZACIÓ")
print("=" * 70)

# Extreure textos nous del Sistema A complet (ids >= 100)
df_a_nou = df_a_complet[df_a_complet["Id"] >= 100].copy()

# Renombrar columnas de resultados_complet.csv (que tenen noms diferents)
df_a_nou = df_a_nou.rename(
    columns={
        "biaix": "biaix_intensitat",
        "emocional": "emocional_intensitat",
        "desinfo": "desinfo_intensitat",
    }
)

print(f"\nTextos nous a Sistema A: {len(df_a_nou)}")
print(f"Textos nous a Sistema B: {len(df_b_nou)}")

# Fusionar
merged_nou = pd.merge(
    df_a_nou[
        [
            "Id",
            "Categoria",
            "biaix_intensitat",
            "desinfo_intensitat",
            "emocional_intensitat",
        ]
    ],
    df_b_nou[["Id", "biaix_intensitat", "desinfo_intensitat", "emocional_intensitat"]],
    on="Id",
    suffixes=("_A", "_B"),
)

print(f"Textos comparats: {len(merged_nou)}")

for dim in ["biaix", "desinfo", "emocional"]:
    col_a = f"{dim}_intensitat_A"
    col_b = f"{dim}_intensitat_B"

    acord = (merged_nou[col_a] == merged_nou[col_b]).sum()
    total = len(merged_nou)
    pct = (acord / total) * 100

    print(f"\n{dim.upper()}:")
    print(f"   Acord total: {acord}/{total} ({pct:.1f}%)")

    # Comparativa clau: quants textos ha detectat cada sistema?
    detectats_a = (merged_nou[col_a] != "nul·la").sum()
    detectats_b = (merged_nou[col_b] != "nul·la").sum()
    print(f"   Sistema A detecta indicis en: {detectats_a}/{total} textos")
    print(f"   Sistema B detecta indicis en: {detectats_b}/{total} textos")

# ========================
# GUARDAR RESULTATS
# ========================
print("\n" + "=" * 70)
print("GUARDANT RESULTATS")
print("=" * 70)

merged_original.to_csv("comparativa_original.csv", index=False, encoding="utf-8")
merged_nou.to_csv("comparativa_nou.csv", index=False, encoding="utf-8")

print("\nArxius generats:")
print("   - comparativa_original.csv (24 textos)")
print("   - comparativa_nou.csv (9 textos)")

print("\n" + "=" * 70)
print("COMPARATIVA COMPLETADA!")
print("=" * 70)
