# detector_claude.py - VERSIÓN MEJORADA FINAL
# Maneja JSON malformado, caracteres especiales, errores de parsing Y CONFIANCA

import json
import time
import re
from typing import Dict, Any
from anthropic import Anthropic
from config_b import (
    ANTHROPIC_API_KEY,
    MODEL,
    MAX_TOKENS,
    PROMPTS,
    INTENSITATS_VALIDES,
    DIMENSIONS,
)

client = Anthropic(api_key=ANTHROPIC_API_KEY)


def _reparar_json_truncat(fragment: str) -> str:
    """
    Repara un JSON truncat a mitja resposta (típicament perquè s'ha arribat
    al límit de max_tokens abans d'acabar la "reescriptura_neutral").
    Talla el text al darrer camp complet i tanca les claus/claudàtors oberts.
    """
    text = fragment.rstrip()

    # Si el text acaba enmig d'un string obert (nombre imparell de cometes
    # dobles no escapades), retallem fins a l'última cometa "segura".
    cometes = len(re.findall(r'(?<!\\)"', text))
    if cometes % 2 != 0:
        pos_segura = text.rfind('",')
        if pos_segura == -1:
            pos_segura = text.rfind('"')
        if pos_segura != -1:
            text = text[: pos_segura + 1]

    # Eliminem coma final solta si en queda una
    text = re.sub(r",\s*$", "", text.rstrip())

    # Tanquem claudàtors i claus que hagin quedat oberts
    oberts_claudators = text.count("[") - text.count("]")
    oberts_claus = text.count("{") - text.count("}")

    text += "]" * max(oberts_claudators, 0)
    text += "}" * max(oberts_claus, 0)

    return text


def extraer_json_robusto(respuesta_raw: str, verbose: bool = False) -> Dict[str, Any]:
    """
    Extrae JSON de forma EXTREMADAMENTE robusta.
    Si todo falla, reconstruye la estructura desde el texto.
    AHORA TAMBIÉN BUSCA Y EXTRAE CONFIANCA
    """

    # ========== INTENTO 1: Parseo directo ==========
    try:
        return json.loads(respuesta_raw)
    except json.JSONDecodeError:
        pass

    # ========== INTENTO 2: Buscar JSON entre llaves ==========
    inicio = respuesta_raw.find("{")
    fin = respuesta_raw.rfind("}")

    if inicio != -1 and fin != -1 and fin > inicio:
        json_extraido = respuesta_raw[inicio : fin + 1]

        try:
            return json.loads(json_extraido)
        except json.JSONDecodeError:
            pass

    # ========== INTENTO 3: Limpiar caracteres problemáticos ==========
    try:
        # Estrategia: reemplazar saltos de línea mal colocados dentro de strings
        json_limpio = (
            respuesta_raw[inicio : fin + 1]
            if (inicio != -1 and fin != -1)
            else respuesta_raw
        )

        # Reemplazar secuencias problemáticas
        json_limpio = json_limpio.replace("\n", " ").replace("\r", "")

        # Intentar parsear
        resultado = json.loads(json_limpio)
        return resultado
    except json.JSONDecodeError:
        pass

    # ========== INTENTO 3.5: Reparar JSON truncat (resposta tallada per max_tokens) ==========
    # Si Claude s'ha quedat sense tokens a mitja resposta (típic quan la
    # "reescriptura_neutral" és llarga), el JSON queda obert. Aquí es talla
    # al darrer camp complet i es tanquen les claus/claudàtors pendents.
    try:
        base = respuesta_raw[inicio:] if inicio != -1 else respuesta_raw
        reparat = _reparar_json_truncat(base)
        resultado = json.loads(reparat)
        return resultado
    except (json.JSONDecodeError, Exception):
        pass

    # ========== INTENTO 4: Buscar "intensitat" en el texto y reconstruir ==========
    try:
        resultado = {}

        for dimension in DIMENSIONS:
            intensitat_encontrada = None

            # Buscar qué intensidad aparece después del nombre de la dimensión
            for intensidad_valida in INTENSITATS_VALIDES:
                # Patrón: cualquier mención de la intensidad para esta dimensión
                patron = rf'"{dimension}".*?({"|".join(INTENSITATS_VALIDES)})'
                match = re.search(patron, respuesta_raw, re.IGNORECASE | re.DOTALL)

                if match and intensidad_valida.lower() in match.group(0).lower():
                    intensitat_encontrada = intensidad_valida
                    break

            # Si no encontramos, buscar solo en el contexto de esa dimensión
            if not intensitat_encontrada:
                for intensidad in INTENSITATS_VALIDES:
                    if intensidad.lower() in respuesta_raw.lower():
                        intensitat_encontrada = intensidad
                        break

            intensitat = intensitat_encontrada if intensitat_encontrada else "moderada"

            # ===== NUEVO: Buscar confianca (número entre 0-100) =====
            confianca_match = re.search(
                rf'"{dimension}"[^}}]*?"confianca"\s*:\s*(\d+)',
                respuesta_raw,
                re.IGNORECASE | re.DOTALL,
            )
            confianca = int(confianca_match.group(1)) if confianca_match else None

            # Buscar fragment (entre comillas después de "fragment")
            fragment_match = re.search(
                rf'"{dimension}"[^}}]*?"fragment"\s*:\s*"([^"]*?)"',
                respuesta_raw,
                re.IGNORECASE | re.DOTALL,
            )
            fragment = fragment_match.group(1)[:100] if fragment_match else "N/A"

            # Buscar explicacio
            explicacio_match = re.search(
                rf'"{dimension}"[^}}]*?"explicacio"\s*:\s*"([^"]*?)"',
                respuesta_raw,
                re.IGNORECASE | re.DOTALL,
            )
            explicacio = (
                explicacio_match.group(1)[:300]
                if explicacio_match
                else respuesta_raw[:300]
            )

            resultado[dimension] = {
                "intensitat": intensitat,
                "fragment": fragment,
                "explicacio": explicacio.strip(),
            }

            # ===== NUEVO: Añadir confianca si se encontró =====
            if confianca is not None:
                resultado[dimension]["confianca"] = confianca

        # ===== NUEVO: valores por defecto de ideologia i reescriptura_neutral =====
        resultado["ideologia"] = {
            "puntuacio": 0,
            "etiqueta": "centre",
            "explicacio": "No s'ha pogut determinar l'orientació ideològica a partir de la resposta.",
        }
        resultado["reescriptura_neutral"] = ""

        return resultado
    except Exception as e:
        pass

    # ========== INTENTO 5: Última opción - análisis superficial ==========
    try:
        # Solo buscar intensidades mencionadas
        resultado = {}

        for dimension in DIMENSIONS:
            # Buscar cualquier intensidad válida en el texto
            intensitat = "moderada"  # default

            for intens in INTENSITATS_VALIDES:
                if intens.lower() in respuesta_raw.lower():
                    intensitat = intens
                    break

            resultado[dimension] = {
                "intensitat": intensitat,
                "fragment": (
                    respuesta_raw[:80] + "..."
                    if len(respuesta_raw) > 80
                    else respuesta_raw
                ),
                "explicacio": (
                    respuesta_raw[:300] + "..."
                    if len(respuesta_raw) > 300
                    else respuesta_raw
                ),
            }

        # ===== NUEVO: valores por defecto de ideologia i reescriptura_neutral =====
        resultado["ideologia"] = {
            "puntuacio": 0,
            "etiqueta": "centre",
            "explicacio": "No s'ha pogut determinar l'orientació ideològica a partir de la resposta.",
        }
        resultado["reescriptura_neutral"] = ""

        return resultado
    except:
        pass

    # ========== FALLBACK FINAL ==========
    return {
        "biaix": {
            "intensitat": "moderada",
            "fragment": "Error al procesar",
            "explicacio": "No se pudo extraer el JSON. Intenta de nuevo.",
        },
        "desinformacio": {
            "intensitat": "nul·la",
            "fragment": "Error",
            "explicacio": "Error al procesar",
        },
        "emocional": {
            "intensitat": "nul·la",
            "fragment": "Error",
            "explicacio": "Error al procesar",
        },
        "ideologia": {
            "puntuacio": 0,
            "etiqueta": "centre",
            "explicacio": "No s'ha pogut determinar l'orientació ideològica.",
        },
        "reescriptura_neutral": "",
    }


def validar_resposta_json(resposta_json: dict) -> bool:
    """Valida la estructura del JSON"""
    try:
        for dim in DIMENSIONS:
            if dim not in resposta_json:
                return False
            dim_data = resposta_json[dim]
            if (
                "intensitat" not in dim_data
                or "fragment" not in dim_data
                or "explicacio" not in dim_data
            ):
                return False
            if dim_data["intensitat"] not in INTENSITATS_VALIDES:
                return False
        return True
    except:
        return False


def analizar_texto_claude(
    texto: str, version_prompt: str = "v1", verbose: bool = False
) -> dict:
    """
    Analiza un texto político usando Claude API.
    VERSIÓN MEJORADA FINAL - totalmente robusta contra JSON malformado.
    AHORA INCLUYE CONFIANCA
    """

    if not ANTHROPIC_API_KEY:
        return {"success": False, "error": "API key no configurada en .env"}

    try:
        if version_prompt not in PROMPTS:
            return {
                "success": False,
                "error": f"Versión de prompt no válida: {version_prompt}",
            }

        # Truncar si es muy largo (economy)
        if len(texto) > 4000:
            texto = texto[:4000]

        prompt_template = PROMPTS[version_prompt]
        prompt_final = prompt_template.format(text=texto)

        if verbose:
            print(f"📤 Llamando a Claude {MODEL}...")

        # Llamar a Claude
        message = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            messages=[{"role": "user", "content": prompt_final}],
        )

        resposta_raw = message.content[0].text

        if verbose:
            print(f"📨 Respuesta recibida ({len(resposta_raw)} caracteres)")

        # ========== USAR EXTRACCIÓN ROBUSTA ==========
        resposta_json = extraer_json_robusto(resposta_raw, verbose=verbose)

        # Validar
        if not validar_resposta_json(resposta_json):
            if verbose:
                print("⚠️  Estructura incompleta, completando...")

            # Asegurar que tiene todos los campos
            for dim in DIMENSIONS:
                if dim not in resposta_json:
                    resposta_json[dim] = {
                        "intensitat": "nul·la",
                        "fragment": "N/A",
                        "explicacio": "No disponible",
                    }

        # ===== NUEVO: garantizar ideologia i reescriptura_neutral pase lo que pase =====
        if "ideologia" not in resposta_json:
            resposta_json["ideologia"] = {
                "puntuacio": 0,
                "etiqueta": "centre",
                "explicacio": "No disponible.",
            }
        if "reescriptura_neutral" not in resposta_json:
            resposta_json["reescriptura_neutral"] = ""

        if verbose:
            print("✅ Análisis completado correctamente")

        return {"success": True, "data": resposta_json}

    except Exception as e:
        if verbose:
            print(f"❌ ERROR: {str(e)}")

        return {"success": False, "error": f"Error en análisis: {str(e)[:100]}"}


def test_5_textos():
    """Test con los 5 textos exemplares."""
    from config_b import TEXTOS_TEST

    print("=" * 70)
    print("TEST - 5 TEXTOS EXEMPLARES (VERSIÓN MEJORADA CON CONFIANCA)")
    print("=" * 70)

    for key, info in TEXTOS_TEST.items():
        print(f"\n📝 {key} (Id: {info['id']})")

        resultado = analizar_texto_claude(info["text"], verbose=True)

        if resultado["success"]:
            data = resultado["data"]
            for dim in DIMENSIONS:
                confianca_text = ""
                if "confianca" in data[dim]:
                    confianca_text = f" ({data[dim]['confianca']}%)"
                print(f"   • {dim}: {data[dim]['intensitat']}{confianca_text}")
        else:
            print(f"   ❌ ERROR: {resultado['error']}")

        time.sleep(1)


if __name__ == "__main__":
    print("✅ detector_claude.py MEJORADO cargado y listo")


def generar_titol(texto: str) -> str:
    """
    Genera un títol curt (màx. 6 paraules) en català a partir del text.
    Si el text ja té un titular llarg, el sintetitza; si no en té, el crea
    amb paraules clau. Retorna només el títol.
    """
    if not ANTHROPIC_API_KEY:
        return "informe"

    prompt = (
        "A partir del següent text polític, dona'm un títol curt en català de "
        "com a màxim 6 paraules que resumeixi el tema. Si el text ja té un "
        "titular llarg, sintetitza'l. Si no en té cap, crea'n un amb les "
        "paraules clau. Respon NOMÉS amb el títol, sense cometes, sense punt "
        "final i sense cap explicació.\n\nTEXT:\n" + texto[:2000]
    )

    try:
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=30,
            messages=[{"role": "user", "content": prompt}],
        )
        titol = (
            message.content[0].text.strip().strip('"').strip("'").rstrip(".").strip()
        )
        return titol if titol else "informe"
    except Exception:
        return "informe"
