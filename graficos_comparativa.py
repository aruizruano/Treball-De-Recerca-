# graficos_comparativa.py
# Generar gràfics per visualitzar la comparativa A vs B

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

print("Generant gràfics de la comparativa A vs B...")

# ========================
# LLEGIR DADES
# ========================
merged_original = pd.read_csv("comparativa_original.csv")
merged_nou = pd.read_csv("comparativa_nou.csv")

# ========================
# GRÀFIC 1: DETECCIÓ EN TEXTOS NOUS (LA DADA CLAU!)
# ========================
fig, ax = plt.subplots(figsize=(10, 6))

dimensions = ["BIAIX", "DESINFORMACIÓ", "EMOCIONAL"]
sistema_a = [0, 3, 6]  # Detectats per A en textos nous
sistema_b = [9, 7, 9]  # Detectats per B en textos nous

x = np.arange(len(dimensions))
width = 0.35

bars_a = ax.bar(
    x - width / 2, sistema_a, width, label="Sistema A (regles)", color="#e74c3c"
)
bars_b = ax.bar(
    x + width / 2, sistema_b, width, label="Sistema B (Claude)", color="#3498db"
)

ax.set_ylabel("Textos amb indicis detectats (de 9)", fontsize=12)
ax.set_title(
    "Capacitat de detecció en textos NOUS (generalització)",
    fontsize=14,
    fontweight="bold",
)
ax.set_xticks(x)
ax.set_xticklabels(dimensions)
ax.legend(fontsize=11)
ax.set_ylim(0, 10)
ax.grid(axis="y", alpha=0.3)

# Afegir valors sobre les barres
for bars in [bars_a, bars_b]:
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2.0,
            height + 0.1,
            f"{int(height)}/9",
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold",
        )

plt.tight_layout()
plt.savefig("grafic1_deteccio_textos_nous.png", dpi=150, bbox_inches="tight")
print("   Guardat: grafic1_deteccio_textos_nous.png")
plt.close()

# ========================
# GRÀFIC 2: % ACORD EN TEXTOS ORIGINALS vs NOUS
# ========================
fig, ax = plt.subplots(figsize=(10, 6))

dimensions = ["BIAIX", "DESINFORMACIÓ", "EMOCIONAL"]
acord_original = [20.8, 0.0, 25.0]  # % d'acord textos originals
acord_nou = [0.0, 33.3, 0.0]  # % d'acord textos nous

x = np.arange(len(dimensions))
width = 0.35

bars_orig = ax.bar(
    x - width / 2, acord_original, width, label="Textos originals (24)", color="#2ecc71"
)
bars_nou = ax.bar(
    x + width / 2, acord_nou, width, label="Textos nous (9)", color="#f39c12"
)

ax.set_ylabel("% d'acord entre A i B", fontsize=12)
ax.set_title(
    "Percentatge d'acord entre Sistema A i Sistema B", fontsize=14, fontweight="bold"
)
ax.set_xticks(x)
ax.set_xticklabels(dimensions)
ax.legend(fontsize=11)
ax.set_ylim(0, 50)
ax.grid(axis="y", alpha=0.3)

for bars in [bars_orig, bars_nou]:
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2.0,
            height + 0.5,
            f"{height:.1f}%",
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold",
        )

plt.tight_layout()
plt.savefig("grafic2_percentatge_acord.png", dpi=150, bbox_inches="tight")
print("   Guardat: grafic2_percentatge_acord.png")
plt.close()

# ========================
# GRÀFIC 3: DISTRIBUCIÓ DE INTENSITATS (TEXTOS NOUS)
# ========================
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
dimensions = ["biaix", "desinfo", "emocional"]
titols = ["BIAIX", "DESINFORMACIÓ", "EMOCIONAL"]
intensitats = ["nul·la", "lleu", "moderada", "alta"]

for idx, dim in enumerate(dimensions):
    col_a = f"{dim}_intensitat_A"
    col_b = f"{dim}_intensitat_B"

    # Comptar intensitats
    counts_a = merged_nou[col_a].value_counts().reindex(intensitats, fill_value=0)
    counts_b = merged_nou[col_b].value_counts().reindex(intensitats, fill_value=0)

    x = np.arange(len(intensitats))
    width = 0.35

    axes[idx].bar(x - width / 2, counts_a, width, label="Sistema A", color="#e74c3c")
    axes[idx].bar(x + width / 2, counts_b, width, label="Sistema B", color="#3498db")

    axes[idx].set_title(titols[idx], fontsize=12, fontweight="bold")
    axes[idx].set_xticks(x)
    axes[idx].set_xticklabels(intensitats, rotation=0)
    axes[idx].legend()
    axes[idx].set_ylim(0, 10)
    axes[idx].grid(axis="y", alpha=0.3)
    axes[idx].set_ylabel("Nombre de textos")

plt.suptitle(
    "Distribució d'intensitats en TEXTOS NOUS (9 textos)",
    fontsize=14,
    fontweight="bold",
)
plt.tight_layout()
plt.savefig("grafic3_distribucio_intensitats.png", dpi=150, bbox_inches="tight")
print("   Guardat: grafic3_distribucio_intensitats.png")
plt.close()

# ========================
# GRÀFIC 4: EL GRAN CONTRAST - Sistema A cau a 0
# ========================
fig, ax = plt.subplots(figsize=(10, 6))

# Convertir intensitats a valors numèrics per calcular mitjanes
mapa_intensitat = {"nul·la": 0, "lleu": 1, "moderada": 2, "alta": 3}


def intensitat_a_num(serie):
    return serie.map(mapa_intensitat).mean()


dims = ["biaix", "desinfo", "emocional"]
titols = ["BIAIX", "DESINFO", "EMOCIONAL"]

mitjanes_a_original = [
    intensitat_a_num(merged_original[f"{d}_intensitat_A"]) for d in dims
]
mitjanes_a_nou = [intensitat_a_num(merged_nou[f"{d}_intensitat_A"]) for d in dims]
mitjanes_b_original = [
    intensitat_a_num(merged_original[f"{d}_intensitat_B"]) for d in dims
]
mitjanes_b_nou = [intensitat_a_num(merged_nou[f"{d}_intensitat_B"]) for d in dims]

x = np.arange(len(titols))
width = 0.2

ax.bar(
    x - width * 1.5, mitjanes_a_original, width, label="A - Originals", color="#c0392b"
)
ax.bar(
    x - width * 0.5, mitjanes_a_nou, width, label="A - Nous", color="#e74c3c", alpha=0.6
)
ax.bar(
    x + width * 0.5, mitjanes_b_original, width, label="B - Originals", color="#2874a6"
)
ax.bar(
    x + width * 1.5, mitjanes_b_nou, width, label="B - Nous", color="#3498db", alpha=0.6
)

ax.set_ylabel("Intensitat mitjana (0=nul·la, 3=alta)", fontsize=12)
ax.set_title(
    "Comparativa d'intensitats mitjanes: A vs B (originals vs nous)",
    fontsize=14,
    fontweight="bold",
)
ax.set_xticks(x)
ax.set_xticklabels(titols)
ax.legend()
ax.grid(axis="y", alpha=0.3)
ax.set_ylim(0, 3)

plt.tight_layout()
plt.savefig("grafic4_intensitats_mitjanes.png", dpi=150, bbox_inches="tight")
print("   Guardat: grafic4_intensitats_mitjanes.png")
plt.close()

print("\n" + "=" * 60)
print("TOTS ELS GRÀFICS GENERATS!")
print("=" * 60)
print("\nArxius creats:")
print("   1. grafic1_deteccio_textos_nous.png (LA DADA CLAU!)")
print("   2. grafic2_percentatge_acord.png")
print("   3. grafic3_distribucio_intensitats.png")
print("   4. grafic4_intensitats_mitjanes.png")
