# detectar_desinformacio.py  (versión 2)
# Detector de DESINFORMACIÓ basado en reglas. No usa ninguna IA.
#
# LÍMITE FUNDAMENTAL: leyendo solo el texto NO se puede saber si un dato es
# cierto o falso. Por eso este detector NUNCA afirma que algo sea falso:
# solo señala indicios y recomienda comprobarlo.

from utils_deteccio import buscar

# Señales de que el texto SÍ atribuye lo que dice a alguien o a algún sitio.
PALABRAS_FUENTE = [
    "según",
    "fuente",
    "fuentes",
    "datos de",
    "informe",
    "estudio",
    "encuesta",
    "publicó",
    "expertos",
    "informa",
    "recoge",
    "recogió",
    "advirtió",
    "advirtieron",
    "aseguró",
    "asegura",
    "confirmó",
    "confirman",
    "denunció",
    "denuncia",
    "afirmó",
    "declaró",
    "explicó",
    "señalan",
    "de acuerdo con",
    "citado por",
    "reveló",
    "indica",
]

# Señales de dar cifras o datos concretos.
INDICIOS_CIFRAS = ["%", "millones", "millón", "por ciento", "euros", "cifra"]

# Señales de convertir una anécdota en ley general.
# La rúbrica lo pide: "presenta com a fet general un cas anecdòtic".
GENERALIZACIONES = [
    "siempre son los mismos",
    "siempre son",
    "todos los días",
    "cada día",
    "pan de cada día",
    "todo el mundo",
    "nadie",
    "ninguno",
    "todos ellos",
    "es lo de siempre",
    "como siempre",
    "la mayoría de",
    "muchos de ellos",
]


def detectar_desinformacio(texto):
    texto_min = texto.lower()

    # ¿Da cifras o datos concretos?
    cifras = buscar(INDICIOS_CIFRAS, texto_min)
    tiene_cifras = len(cifras) > 0 or any(c.isdigit() for c in texto_min)

    # ¿Atribuye lo que dice a alguna fuente?
    fuentes = buscar(PALABRAS_FUENTE, texto_min)
    cita_fuente = len(fuentes) > 0

    # ¿Generaliza a partir de casos sueltos?
    generaliza = buscar(GENERALIZACIONES, texto_min)

    # Indicios: dar datos sin atribuirlos, o generalizar sin apoyo.
    indicios = []
    if tiene_cifras and not cita_fuente:
        indicios.append("dóna dades concretes sense citar cap font")
    if generaliza and not cita_fuente:
        indicios.append("generalitza a partir de casos solts")

    if len(indicios) == 0:
        intensitat = "nul·la"
        mensaje = "No es detecten indicis clars mitjançant regles."
    elif len(indicios) == 1:
        intensitat = "lleu"
        mensaje = "Hi ha indicis de desinformació, es recomana investigar a fons."
    else:
        intensitat = "moderada"
        mensaje = "Hi ha indicis de desinformació, es recomana investigar a fons."

    return {
        "intensitat": intensitat,
        "tiene_cifras": tiene_cifras,
        "cita_fuente": cita_fuente,
        "fuentes_detectadas": fuentes,
        "generalizaciones": generaliza,
        "indicios": indicios,
        "mensaje": mensaje,
    }


if __name__ == "__main__":
    pruebas = [
        (
            "Bulo (texto 21)",
            "El ministerio se gasta 68.000 euros en churros y bollería industrial.",
        ),
        (
            "Noticia con fuente",
            "Los procesos crecieron un 14,4%, según informa Efe, hasta alcanzar 926.394.",
        ),
        (
            "Generalización (texto 20)",
            "Cada día una historia nueva. Y siempre son los mismos.",
        ),
    ]
    for nombre, t in pruebas:
        r = detectar_desinformacio(t)
        print(f"{nombre}: {r['intensitat']} | {r['indicios']}")
