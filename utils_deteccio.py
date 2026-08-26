# utils_deteccio.py
# Funcions compartides pels tres detectors de Sistema A
# (detectar_biaix.py, detectar_desinformacio.py, detectar_emocional.py).
# Abans estaven copiades i enganxades a cada arxiu per separat.

import re


def quitar_citas(texto):
    """Analiza la voz del autor, no la de los citados.
    Excepción: si el texto es casi todo cita, es un discurso y va entero."""
    patron = r'[«"“](.*?)[»"”]'
    citas = re.findall(patron, texto, re.S)
    if sum(len(c) for c in citas) > len(texto) * 0.5:
        return texto
    return re.sub(patron, " ", texto, flags=re.S)


def buscar(lista, texto_min):
    """Devuelve las palabras de la lista que aparecen en el texto."""
    return [p for p in lista if p in texto_min]
