# detectar_emocional.py  (versión 3)
# Detector de LLENGUATGE EMOCIONAL basado en reglas. No usa ninguna IA.

import re
from collections import Counter

# 1. Palabras con carga emocional.
PALABRAS_EMOCIONALES = [
    "alarmante",
    "amenaza",
    "peligro",
    "miedo",
    "temor",
    "traición",
    "traidor",
    "vergüenza",
    "escándalo",
    "indignante",
    "mentira",
    "destruir",
    "destrucción",
    "catástrofe",
    "invasión",
    "miseria",
    "ruina",
    "esclavos",
    "sumisos",
    "desgarra",
    "duele",
    "tristeza",
    "llorando",
    "sufrir",
    "imparable",
    "asqueroso",
    "cobardes",
    "profanar",
    "denigran",
    "cáncer",
    "furia",
    "lucha",
    "dignidad",
    "degradando",
    "paliza",
]

# 2. APELACIONES A LA IDENTIDAD ("nosotros los X").
# La rúbrica las pide: "apel·lació a les emocions o a la IDENTITAT".
# IMPORTANTE: incluimos las de TODAS las ideologías a propósito.
# Si solo pusiéramos las de un lado, el detector estaría trucado para
# encontrar más sesgo en ese lado, y las conclusiones no valdrían nada.
APELACIONES_IDENTIDAD = [
    # Identidad nacional / patriótica
    "los españoles",
    "nuestro país",
    "nuestra nación",
    "la españa de",
    "el pueblo",
    "los ciudadanos",
    "nuestra tierra",
    "nuestra patria",
    # Identidad de clase / trabajadora
    "la gente trabajadora",
    "la clase trabajadora",
    "los trabajadores",
    "la gente humilde",
    "las personas más humildes",
    "la gente de",
    # Identidad de género / colectivos
    "las mujeres",
    "nosotras las",
    "nuestras hijas",
    "las víctimas",
    # Identidad familiar / generacional
    "nuestros hijos",
    "nuestras familias",
    "nuestros abuelos",
    "los jóvenes",
]

# 3. Frases de URGENCIA (la rúbrica las pide: "última oportunitat").
FRASES_URGENCIA = [
    "antes de que sea tarde",
    "última oportunidad",
    "no podemos permitir",
    "no lo podemos permitir",
    "basta ya",
    "ahora o nunca",
    "hay que actuar",
    "no vamos a parar",
    "ya es tarde",
    "se nos acaba el tiempo",
    "es el momento",
    "no hay marcha atrás",
    "pan de cada día",
]


def quitar_citas(texto):
    """Analiza la voz del autor. Si el texto es casi todo cita, es un discurso: va entero."""
    patron = r'[«"“](.*?)[»"”]'
    citas = re.findall(patron, texto, re.S)
    if sum(len(c) for c in citas) > len(texto) * 0.5:
        return texto
    return re.sub(patron, " ", texto, flags=re.S)


def detectar_repeticiones(texto_min):
    """Detecta ANÁFORA: empezar 3+ frases seguidas con las mismas palabras.
    Ej: "que viva la furia, que viva el orgullo, que viva la lucha".
    Esto SÍ es retórica. Contar pares sueltos ("de la") no servía:
    en un texto largo salen por casualidad."""
    # Partimos el texto en frases (por comas, puntos y puntos suspensivos).
    frases = re.split(r"[,.;:!?]+", texto_min)
    inicios = []
    for f in frases:
        palabras = f.split()
        if len(palabras) >= 3:
            inicios.append(palabras[0] + " " + palabras[1])
    contador = Counter(inicios)
    return [frase for frase, veces in contador.items() if veces >= 3]


def detectar_mayusculas(texto):
    """Busca GRITOS: 2 o más palabras seguidas TODO EN MAYÚSCULAS.
    Pedimos 2+ seguidas porque una sola casi siempre es una sigla
    (PSOE, OTAN, COEM...), no un grito."""
    return re.findall(r"\b[A-ZÁÉÍÓÚÑ]{3,}\s+[A-ZÁÉÍÓÚÑ]{3,}\b", texto)


def detectar_emocional(texto):
    texto_autor = quitar_citas(texto)
    texto_min = texto_autor.lower()

    palabras = [p for p in PALABRAS_EMOCIONALES if p in texto_min]
    identidad = [a for a in APELACIONES_IDENTIDAD if a in texto_min]
    urgencia = [f for f in FRASES_URGENCIA if f in texto_min]
    repeticiones = detectar_repeticiones(texto_min)
    mayusculas = detectar_mayusculas(texto_autor)
    exclamaciones = texto_autor.count("!") + texto_autor.count("¡")

    total_senales = (
        len(palabras)
        + len(identidad)
        + len(urgencia)
        + len(repeticiones)
        + len(mayusculas)
        + exclamaciones
    )

    if total_senales == 0:
        intensitat = "nul·la"
    elif total_senales <= 2:
        intensitat = "lleu"
    elif total_senales <= 5:
        intensitat = "moderada"
    else:
        intensitat = "alta"

    return {
        "intensitat": intensitat,
        "palabras_encontradas": palabras,
        "apelaciones_identidad": identidad,
        "frases_urgencia": urgencia,
        "repeticiones": repeticiones,
        "mayusculas": mayusculas,
        "num_exclamaciones": exclamaciones,
        "total_senales": total_senales,
    }


if __name__ == "__main__":
    t17 = "EEUU piensa que el mundo es suyo... No lo podemos permitir... Rompamos relaciones con EEUU y salgamos de la OTAN antes de que sea tarde"
    t18 = "España ya es otra, España ya ha cambiado y no vamos a parar hasta que la dignidad se haga costumbre... que viva la furia trans, que viva el orgullo LGTBI... que viva la lucha antiracista y que viva la lucha de las mujeres"
    for nombre, t in [("Texto 17 (Belarra)", t17), ("Texto 18 (Montero)", t18)]:
        r = detectar_emocional(t)
        print(f"{nombre}: {r['intensitat']}")
        print(f"   urgencia: {r['frases_urgencia']}")
        print(f"   repeticiones: {r['repeticiones']}")
