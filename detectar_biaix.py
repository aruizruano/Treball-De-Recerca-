# detectar_biaix.py  (versión 3)
# Detector de BIAIX IDEOLÒGIC basado en reglas. No usa ninguna IA.

from utils_deteccio import quitar_citas, buscar

# NIVEL 1: adjetivos valorativos explícitos (insultos, juicios directos).
PALABRAS_VALORATIVAS = [
    "corrupto",
    "corruptos",
    "traidor",
    "traidores",
    "salvador",
    "reaccionario",
    "reaccionarias",
    "retrógradas",
    "terrible",
    "asqueroso",
    "tirano",
    "cobardes",
    "mentiroso",
    "criminal",
    "vergonzoso",
    "nefasto",
    "desastroso",
    "fanática",
    "fanático",
]

# NIVEL 2: palabras de ENMARCADO. No insultan, pero pintan la realidad
# de forma negativa sin decirlo abiertamente. Es el "sesgo elegante".
PALABRAS_ENMARCADO = [
    "sin rumbo",
    "sin fuste",
    "menguado",
    "menguada",
    "debilidad",
    "vacío de liderazgo",
    "fuga",
    "asedio",
    "herida",
    "crisis",
    "caos",
    "fracaso",
    "desgaste",
    "incógnita",
    "sumido",
    "acorralado",
    "cercado",
    "no logra",
    "ni tan siquiera",
    "apenas",
    "desorientación",
    "de trámite",
    "sin oposición",
]

# NIVEL 3: verbos de atribución cargados. "Dice" es neutro;
# "admite" o "reconoce" dan por hecho que hay algo que ocultar.
VERBOS_CARGADOS = [
    "admite",
    "admitió",
    "reconoce",
    "reconoció",
    "confiesa",
    "arremete",
    "arremetió",
    "carga contra",
    "se aferra",
    "se aferran",
    "no quiso",
    "evitó",
    "se limitó",
]


def detectar_biaix(texto):
    texto_autor = quitar_citas(texto)
    texto_min = texto_autor.lower()

    valorativas = buscar(PALABRAS_VALORATIVAS, texto_min)
    enmarcado = buscar(PALABRAS_ENMARCADO, texto_min)
    verbos = buscar(VERBOS_CARGADOS, texto_min)

    # "Nosotros vs ellos": hacen falta los dos para que haya bandos.
    bandos = ("nosotros" in texto_min or "nosotras" in texto_min) and (
        "ellos" in texto_min or "ellas" in texto_min
    )

    total_senales = (
        len(valorativas) + len(enmarcado) + len(verbos) + (1 if bandos else 0)
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
        "palabras_valorativas": valorativas,
        "palabras_enmarcado": enmarcado,
        "verbos_cargados": verbos,
        "bandos_enfrentados": bandos,
        "total_senales": total_senales,
    }


if __name__ == "__main__":
    # Sesgo ELEGANTE: ni un insulto, pero pinta al partido como un desastre.
    elegante = (
        "Sumar sigue sin rumbo tras la fuga de sus líderes. "
        "Admite el desgaste y no logra resolver su vacío de liderazgo."
    )
    r = detectar_biaix(elegante)
    print(
        "Sesgo elegante ->",
        r["intensitat"],
        "| enmarcado:",
        r["palabras_enmarcado"],
        "| verbos:",
        r["verbos_cargados"],
    )

    # Texto neutro de verdad.
    neutro = "La asamblea eligió a las dos coordinadoras con el 95,92% de los votos."
    print("Texto neutro   ->", detectar_biaix(neutro)["intensitat"])
