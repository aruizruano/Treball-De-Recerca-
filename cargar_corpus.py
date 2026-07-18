import pandas as pd

# encoding="utf-8-sig" evita que se rompan los acentos (á, é, ñ, ¿...)
corpus = pd.read_csv("corpus.csv", encoding="utf-8-sig")

print("Número total de textos:", len(corpus))

print("\nTextos por categoría:")
print(corpus["Categoria"].value_counts())

# Preparamos una versión "limpia" del texto: sin espacios sobrantes.
# .fillna("") convierte los vacíos (NaN) en "" para poder tratarlos como texto.
texto_limpio = corpus["Text"].fillna("").str.strip()

# Ahora "vacío" incluye tanto las celdas NaN como los textos que solo tienen espacios.
textos_vacios = corpus[texto_limpio == ""]
print("\nTextos vacíos encontrados:", len(textos_vacios))

# Comparamos en minúsculas para pillar también los duplicados "casi iguales".
duplicados = corpus[texto_limpio.str.lower().duplicated()]
print("Textos duplicados encontrados:", len(duplicados))

print("\nEjemplo del primer texto:")
print(corpus.iloc[0]["Text"][:200], "...")
