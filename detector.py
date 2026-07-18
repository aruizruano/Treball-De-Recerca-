# detector.py
# Junta los tres detectores en un único sistema y añade dos medidas nuevas:
# la longitud del texto y la CONFIANZA de la detección.

from detectar_emocional import detectar_emocional
from detectar_biaix import detectar_biaix
from detectar_desinformacio import detectar_desinformacio


def calcular_confianza(total_senales, num_palabras):
    """¿Cuánta evidencia tengo para lo que estoy diciendo?

    OJO - esto NO es fiabilidad. Fiabilidad = acertar respecto a la verdad,
    y la verdad (el experto) todavía no la tenemos. Esto solo dice cuánta
    evidencia ha encontrado el sistema, que es algo más modesto y honesto.
    """
    if num_palabras < 40:
        # En un texto muy corto casi no hay sitio para indicadores:
        # cualquier conclusión es frágil.
        return "baixa (text molt curt)"
    if total_senales == 0:
        return "baixa (cap indici trobat)"
    if total_senales <= 2:
        return "baixa"
    if total_senales <= 5:
        return "mitjana"
    return "alta"


def analizar_texto(texto):
    """Recibe un texto y devuelve el análisis de las tres dimensiones."""
    num_palabras = len(texto.split())

    biaix = detectar_biaix(texto)
    emocional = detectar_emocional(texto)
    desinfo = detectar_desinformacio(texto)

    # Añadimos la confianza a cada dimensión.
    biaix["confianza"] = calcular_confianza(biaix["total_senales"], num_palabras)
    emocional["confianza"] = calcular_confianza(
        emocional["total_senales"], num_palabras
    )

    # Densidad: señales por cada 100 palabras. Sirve para comparar textos
    # de longitudes muy distintas (un tuit vs un artículo de 1000 palabras).
    total = biaix["total_senales"] + emocional["total_senales"]
    densidad = round(total / num_palabras * 100, 2) if num_palabras else 0

    return {
        "num_palabras": num_palabras,
        "densidad_senales": densidad,
        "biaix_ideologic": biaix,
        "llenguatge_emocional": emocional,
        "desinformacio": desinfo,
    }


if __name__ == "__main__":
    tuit = "¡Nos destruyeron la vida! Es una traición, los españoles no lo podemos permitir."
    articulo = (
        "La asamblea eligió a las coordinadoras con el 95,92% de los votos, según informa Efe. "
        * 20
    )

    for nombre, t in [("Tuit corto", tuit), ("Artículo largo", articulo)]:
        r = analizar_texto(t)
        print(
            f"{nombre}: {r['num_palabras']} palabras | densidad {r['densidad_senales']} señales/100 palabras"
        )
        print(
            f"   emocional: {r['llenguatge_emocional']['intensitat']} (confianza: {r['llenguatge_emocional']['confianza']})"
        )
