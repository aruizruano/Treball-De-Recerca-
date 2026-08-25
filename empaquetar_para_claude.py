"""Empaqueta el projecte en un sol fitxer .md per pujar-lo a un Projecte de Claude.

Ús:  python empaquetar_para_claude.py
Surt: TreballDeRecerca_para_Claude.md (a la carpeta pare)

Exclou secrets (.env), cache, binaris i volcats de resultats.
Dels CSV només inclou la capçalera i unes poques files d'exemple.
"""

import csv
import re
from pathlib import Path

ARREL = Path(__file__).resolve().parent
SORTIDA = ARREL.parent / "TreballDeRecerca_para_Claude.md"

# Codi i documentacio -> s'inclouen sencers
EXT_TEXT = {".py", ".md", ".txt", ".json", ".toml", ".cfg", ".gitignore"}
LLENGUATGE = {".py": "python", ".json": "json", ".md": "markdown", ".toml": "toml"}

# Mai s'inclouen
FITXERS_EXCLOSOS = {
    ".env",                      # conte l'API key
    "empaquetar_para_claude.py", # aquest script
    "respuesta_110.txt",         # volcats de sortida, no son codi
    "resultados_test.txt",
}
DIRS_EXCLOSOS = {"__pycache__", ".git", ".venv", "venv", "node_modules"}
EXT_EXCLOSES = {".pyc", ".png", ".jpg", ".jpeg", ".pdf", ".lnk", ".xlsx", ".zip"}

FILES_MOSTRA_CSV = 3
PATRO_SECRET = re.compile(r"sk-[A-Za-z0-9_\-]{12,}")


def es_exclos(cami: Path) -> bool:
    if any(part in DIRS_EXCLOSOS for part in cami.parts):
        return True
    return cami.name in FITXERS_EXCLOSOS or cami.suffix.lower() in EXT_EXCLOSES


def llegir(cami: Path) -> str:
    """Llegeix tolerant encodings de Windows."""
    for codificacio in ("utf-8", "utf-8-sig", "cp1252", "latin-1"):
        try:
            return cami.read_text(encoding=codificacio)
        except UnicodeDecodeError:
            continue
    return cami.read_bytes().decode("utf-8", errors="replace")


def redacta(text: str, cami: str, avisos: list[str]) -> str:
    """Substitueix qualsevol clau API que s'hagi colat al codi."""
    if PATRO_SECRET.search(text):
        avisos.append(cami)
        text = PATRO_SECRET.sub("<CLAU_API_ELIMINADA>", text)
    return text


def resum_csv(cami: Path) -> str:
    """Capcalera + primeres files, per entendre l'esquema sense abocar les dades."""
    text = llegir(cami)
    files = list(csv.reader(text.splitlines()))
    if not files:
        return "(buit)"
    total = len(files) - 1
    mostra = files[: FILES_MOSTRA_CSV + 1]
    linies = [",".join(f'"{c}"' if "," in c else c for c in fila) for fila in mostra]
    if total > FILES_MOSTRA_CSV:
        linies.append(f"... ({total} files de dades en total)")
    return "\n".join(linies)


def main() -> None:
    fitxers = sorted(
        (c for c in ARREL.rglob("*") if c.is_file() and not es_exclos(c)),
        key=lambda c: (c.suffix.lower() != ".py", str(c.relative_to(ARREL)).lower()),
    )
    codi = [c for c in fitxers if c.suffix.lower() in EXT_TEXT]
    csvs = [c for c in fitxers if c.suffix.lower() == ".csv"]

    avisos: list[str] = []
    parts = [
        "# Treball de Recerca — codi font complet\n",
        "Detector de biaix, desinformacio i llenguatge emocional en textos, "
        "amb interficie Streamlit i analisi via API de Claude.\n",
        f"Empaquetat automaticament: {len(codi)} fitxers de codi/documentacio "
        f"i {len(csvs)} CSV (nomes esquema).\n",
        "## Index\n",
    ]
    for cami in codi + csvs:
        rel = cami.relative_to(ARREL).as_posix()
        parts.append(f"- `{rel}` ({cami.stat().st_size:,} bytes)")

    parts.append("\n---\n\n# Codi i documentacio\n")
    for cami in codi:
        rel = cami.relative_to(ARREL).as_posix()
        contingut = redacta(llegir(cami), rel, avisos).rstrip()
        lang = LLENGUATGE.get(cami.suffix.lower(), "text")
        parts.append(f"\n## `{rel}`\n\n```{lang}\n{contingut}\n```\n")

    if csvs:
        parts.append("\n---\n\n# Dades (esquema i mostra)\n")
        for cami in csvs:
            rel = cami.relative_to(ARREL).as_posix()
            parts.append(f"\n## `{rel}`\n\n```csv\n{resum_csv(cami)}\n```\n")

    SORTIDA.write_text("\n".join(parts), encoding="utf-8")

    kb = SORTIDA.stat().st_size / 1024
    print(f"Escrit: {SORTIDA}")
    print(f"Mida:   {kb:,.1f} KB  (~{SORTIDA.stat().st_size // 4:,} tokens aprox.)")
    print(f"Inclos: {len(codi)} fitxers de codi, {len(csvs)} CSV resumits")
    if avisos:
        print("\nATENCIO — s'han redactat claus API trobades dins del codi:")
        for a in sorted(set(avisos)):
            print(f"  - {a}   <- treu la clau del codi i posa-la al .env")


if __name__ == "__main__":
    main()
