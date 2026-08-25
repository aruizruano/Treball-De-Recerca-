# config_b.py
# Configuración del Sistema B (Claude API)
# Rúbrica, prompts y constants

import os
from dotenv import load_dotenv

# Cargar .env
load_dotenv()

# API Configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
MODEL = "claude-opus-4-6"
MAX_TOKENS = 8192

# ========================
# RÚBRICA OFICIAL
# ========================

RUBRICA = {
    "biaix": {
        "nul·la": "Cap indici de biaix",
        "lleu": "1-2 indicis aïllats",
        "moderada": "3-5 indicis combinats",
        "alta": "6+ indicis, biaix evident",
    },
    "desinformacio": {
        "nul·la": "Cap indici de desinformació",
        "lleu": "1 indici (ex: cifra sense font)",
        "moderada": "2+ indicis (dades sense font + generalitzacions)",
        "alta": "Narrativa coordinada enganyosa amb múltiples indicis",
    },
    "emocional": {
        "nul·la": "Cap recurs emocional",
        "lleu": "1-2 recursos emocionals aïllats",
        "moderada": "3-5 recursos (paraules, urgència, identitat)",
        "alta": "6+ recursos: grits, urgència extrema, anàfora, saturació",
    },
}

# ========================
# INDICADORS PER DETECTAR
# ========================

INDICADORES = {
    "biaix": [
        "Adjectius valoratius (corrupto, traidor, salvador, nefasto, etc.)",
        "Framing negre (sin rumbo, vacío de liderazgo, crisis, caos, desgaste)",
        "Verbos carregats (admite, reconoce, arremete, se aferra, evitó)",
        "Bandos enfrontats (nosaltres vs ells, poble vs élite)",
        "Analogies deformants i dog whistles",
        "Comparacions tendencioses o parallelismes enganyosos",
    ],
    "desinformacio": [
        "Cifres/dades concrectes sense atribució a font",
        "Generalitzacions abusives (todos, siempre, nadie) sense suport",
        "Narratives contradictòries o omissió deliberada de context",
        "Claims que contradixen hechos públics verificables",
        "Statements presentadas como faits que són opinions",
        "Anécdotes presentadas como problemes sistémics",
    ],
    "emocional": [
        "Paraules emocionals (peligro, amenaza, traición, dignidad, lucha, cáncer)",
        "Apelacions a identitat (nosaltres els X, la gent de, les mares de)",
        "Frases d'urgència (antes de que sea tarde, ahora o nunca, última oportunidad)",
        "Retòrica: anàfora, MAYÚSCULAS per grits, exclamacions (!)",
        "Hipèrboles i exageracions",
        "Apel·lacions a emocions primes (por, ira, dignitat)",
    ],
}

# ========================
# PROMPT PRINCIPAL (v1)
# ========================

PROMPT_V3 = """Analitza aquest text polític dirigit a joves Catalans. Detecta BIAIX IDEOLÒGIC, DESINFORMACIÓ i LLENGUATGE EMOCIONAL.

RÚBRICA I DEFINICIONS (MÉS DETALLAT):

**BIAIX IDEOLÒGIC**: Presentar la realitat de forma tendenciosa, favorecendo una ideologia i denigrant l'altra.

NIVELLS D'INTENSITAT:

🔴 NULA (0): Cap indici. Text purament descriptiu, factual, objectiu.
   Exemples: "La reunió va durar 2 hores amb 15 assistents"

🟡 LLEU (1): 1-2 indicis aïllats, sutilment biaixats pero no coordinats.
   Exemples: Una sola paraula valorativa ("critica", "reclama") SENSE framing negatiu sistemàtic.
   
🟠 MODERADA (2): 3-5 indicis coordinats O combinació de 2+ indicis AMPLIFICATS.
   Exemples: 
   - "El govern ha fracassat repetidament en..." (framing negatiu + verbs carregats)
   - "El drama dels autònoms: 1,5 milions no poden coger baixes" (framing negatiu "drama" + cifra concreta = amplificació deliberada)
   - "La catástrofe de la sanitat: 500.000 pacients en llista d'espera" (paraula intense "catástrofe" + número per dramatitzar)
   Pero NO és polarització extrema ni insultos directes ni bandos enfrontats.
   
🔴 ALTA (3): 6+ indicis coordinats. Biaix evident, polaritzant, sistemàtic.
   - Framing negatiu REFORÇAT: "sin rumbo", "caos", "crisis" + paraules valoratives intensas
   - Paraules carregades fortment: "traidor", "corrupto", "mentira descarada"
   - Bandos enfrontats explícitament: "nosaltres" vs "ells/enemics"
   - Insultos o denigració directa
   - Analogies deformants que comparen amb dictadura/malvolats
   
INDICADORS DE BIAIX (ORDENATS PER POTÈNCIA):
   1. Framing negatiu ESTRUCTURAL: "sin rumbo", "caos", "crisis", "desgaste", "fuga", "drama"
      → Si va acompanyat de CIFRES/NOMBRES per amplificar = JA ÉS MODERADA
      Exemple: "El drama dels autònoms: 1,5 milions no poden coger baixes"
      (Framing negatiu "drama" + cifra concreta "1,5 milions" = 2 indicis combinats = moderada mínima)
   
   2. Paraules valoratives intensas: "corrupto", "nefasto", "traidor", "mentira descarada"
      → Soles ja són indicis forts de biaix
   
   3. Verbs carregats: "admite" (culpa), "arremete", "se aferra", "traiciona"
      → Impliquen intenció o culpabilitat moral
   
   4. Framing negativo + paraules valoratives COMBINADES = amplificació deliberada
      Exemple: "Sin rumbo" + "fuga" + "desgaste" en titular = biaix ALTA
   
   5. Bandos enfrontats: "nosaltres vs ells", "poble vs élite", "gent honrada vs corruptos"
      → Polarització explícita = indicador fort
   
   6. Comparacions deformants: "com una dictadura", "com els nazis"
      → Reductio ad absurdum polaritzant

⚠️ CLAU NOVA: "Framing negatiu + números/cifres per amplificar" = INDICADOR DE BIAIX MODERADA
Sempre que vegueu framing (drama, crisis, etc.) RESPALDADA PER CIFRES per amplificar l'efecte, és biaix coordinat.

⚠️ CLAU: "sin rumbo" + "fuga" + "desgaste" en el TITULAR = ja és BIAIX ALT (framing negatiu sistemàtic)

---

**DESINFORMACIÓ**: Presentar informació falsa o enganyosa com si fos veritat.

NIVELLS:
🔴 NULA: Cap indici. Informació verificable o opinió clara.
🟡 LLEU: 1 indici. Cifra sense font O generalització aïllada.
🟠 MODERADA: 2+ indicis. Múltiples dades sense font + generalitzacions.
🔴 ALTA: Narrativa coordinada enganyosa amb múltiples indicis falsos.

INDICADORS:
   1. Cifres/dades concrectes SENSE font: "68.000 euros" però no diu d'on
   2. Generalitzacions abusives sense suport: "todos siempre", "nadie jamás"
   3. Narratives contradictòries o omissió deliberada de context
   4. Claims que contradixen fets públics
   5. Anécdotes presentades com a sistèmiques

---

**LLENGUATGE EMOCIONAL**: Uso deliberat de paraules i recursos retòrics per manipular emocions.

NIVELLS:
🔴 NULA: Cap recurs. Text descriptiu, factual.
🟡 LLEU: 1-2 recursos aïllats.
🟠 MODERADA: 3-5 recursos coordinats.
🔴 ALTA: 6+ recursos. Saturació retòrica.

INDICADORS:
   1. Paraules emocionals: "peligro", "amenaza", "traición", "dignidad", "lucha", "drama"
   2. Apel·lacions a identitat: "nosaltres els X", "la gent de", "les mares de"
   3. Urgència: "antes de que sea tarde", "ahora o nunca", "última oportunidad"
   4. Retòrica: anàfora, MAYÚSCULAS, exclamacions
   5. Hipèrboles: "nada más y nada menos que 68.000"

---

**ORIENTACIÓ IDEOLÒGICA**: A partir dels temes, els marcs (framing) i les postures explícites o implícites del text, situa'l en un eix esquerra-dreta.

ESCALA: puntuació de -100 (esquerra) a +100 (dreta), on 0 és centre absolut o text no classificable ideològicament.

GUIA ORIENTATIVA:
   -100 a -60 → Esquerra: intervenció estatal forta, redistribució, crítica al capitalisme,
                moviments obrers/feministes/ecologistes, regulació estricta de mercats.
   -60 a -20  → Centre-esquerra: socialdemocràcia, regulació moderada, drets socials, estat del benestar.
   -20 a 20   → Centre / no classificable: posicions equilibrades, text purament factual,
                sense marcadors ideològics clars.
   20 a 60    → Centre-dreta: liberalisme econòmic moderat, valors tradicionals moderats,
                èmfasi en l'ordre i la responsabilitat individual.
   60 a 100   → Dreta: nacionalisme, liberalisme econòmic fort, conservadurisme social,
                crítica a la immigració o a l'estat del benestar.

IMPORTANT:
   - Si el text és purament factual sense marcadors ideològics (ex: "La reunió va durar 2 hores"),
     la puntuació ha de ser propera a 0.
   - Basa't NOMÉS en el CONTINGUT i el FRAMING del text, mai en suposicions sobre qui l'ha escrit
     o quin mitjà el publica.
   - Sigues equilibrat: no interpretis com a ideològic allò que és merament informatiu.

---

**REESCRIPTURA NEUTRAL**: A partir del mateix text, redacta una versió alternativa que:
   1. Mantingui tots els fets i dades verificables originals.
   2. Elimini el biaix ideològic, el llenguatge emocional i els indicis de desinformació detectats.
   3. Utilitzi un to descriptiu i equilibrat, sense adjectius valoratius ni framing.
   4. Tingui una longitud similar a l'original (no cal que sigui més llarga).

---

**REESCRIPTURA NEUTRAL**: A partir del mateix text, redacta una versió alternativa que:
   1. Mantingui tots els fets i dades verificables originals.
   2. Elimini el biaix ideològic, el llenguatge emocional i els indicis de desinformació detectats.
   3. Utilitzi un to descriptiu i equilibrat, sense adjectius valoratius ni framing.
   4. Tingui una longitud similar a l'original (no cal que sigui més llarga).

---

TEXT A ANALITZAR:
{text}

---

Per a cada dimensió, indica també la teva CONFIANÇA (0-100) en la classificació:
com de segur estàs de la intensitat assignada segons l'evidència textual.

RESPOSTA (NOMÉS JSON, sense preambles):
{{
  "biaix": {{
    "intensitat": "nul·la|lleu|moderada|alta",
    "confianca": 0,
    "fragment": "cita literal del text",
    "explicacio": "2-3 frases explicant. Específic: quin framing? quines paraules? per què aquesta intensitat?"
  }},
  "desinformacio": {{
    "intensitat": "nul·la|lleu|moderada|alta",
    "confianca": 0,
    "fragment": "cita literal",
    "explicacio": "2-3 frases"
  }},
  "emocional": {{
    "intensitat": "nul·la|lleu|moderada|alta",
    "confianca": 0,
    "fragment": "cita literal",
    "explicacio": "2-3 frases"
  }},
  "ideologia": {{
    "puntuacio": -100,
    "etiqueta": "esquerra|centre-esquerra|centre|centre-dreta|dreta",
    "explicacio": "2-3 frases justificant la puntuació: quins temes, marcs o postures indiquen aquesta orientació"
  }},
  "reescriptura_neutral": "Versió reescrita del text, factual i sense biaix, llenguatge emocional ni desinformació"
}}

RECORDA: Ser EQUILIBRAT pero RIGORÓS. Si ves "sin rumbo" + "fuga" + "desgaste" = BIAIX ALTA (framing negatiu sistemàtic). Si ves només "drama" = BIAIX LLEU (una paraula sola).
"""

PROMPTS = {
    "v1": PROMPT_V3,  # Cambiar de V1 a V1_MEJORADO
}

# ========================
# 5 TEXTOS EXEMPLARS PARA TESTING
# ========================

TEXTOS_TEST = {
    "text_1_alt_biaix": {
        "id": 1,
        "text": "Sumar sigue sin rumbo: elige a Rosa Martínez y Verónica Barbero coordinadoras tras la 'fuga' de sus principales líderes. Admite el desgaste por los casos de corrupción del PSOE...",
        "categoria": "Biaix",
        "nota": "Alto biaix: sin rumbo, fuga, desgaste",
    },
    "text_4_alt_biaix": {
        "id": 4,
        "text": "El drama de los autónomos: 1,5 millones de estos trabajadores no se pueden coger bajas sin cerrar su negocio...",
        "categoria": "Biaix",
        "nota": "Alto: drama, comparativas emotives",
    },
    "text_17_alt_emocional": {
        "id": 17,
        "text": "EEUU piensa que el mundo es suyo... No lo podemos permitir... Rompamos relaciones con EEUU y salgamos de la OTAN antes de que sea tarde",
        "categoria": "Emocional",
        "nota": "Alto emocional: urgència extrema, bandos",
    },
    "text_21_desinfo": {
        "id": 21,
        "text": "Los desayunos de la vicepresidenta del Gobierno, Yolanda Díaz, son todo menos equilibrados porque hay un desequilibrio evidente para la salud y para los bolsillos, en este caso de todos los españoles: su ministerio pasa factura de nada más y nada menos que 68.000 euros destinados a ese primer almuerzo diario.",
        "categoria": "Desinformació",
        "nota": "Bulo: cifra sense font",
    },
    "text_neutral": {
        "id": 3,
        "text": "Verónica Martínez Barbero y Rosa Martínez, nuevas líderes de Sumar La asamblea respalda con un 95,92% a una dirección bicéfala...",
        "categoria": "Central",
        "nota": "Més factual i menys biaix",
    },
}

# ========================
# CONSTANTS
# ========================

INTENSITATS_VALIDES = ["nul·la", "lleu", "moderada", "alta"]
DIMENSIONS = ["biaix", "desinformacio", "emocional"]
ETIQUETES_IDEOLOGIA = ["esquerra", "centre-esquerra", "centre", "centre-dreta", "dreta"]

PROMPTS = {
    "v1": PROMPT_V3,
}

print(" config_b.py cargado correctamente")
