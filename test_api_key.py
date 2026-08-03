#!/usr/bin/env python3
# test_api_key.py
# Script para verificar que la API key de Anthropic funciona

import os
from dotenv import load_dotenv
from anthropic import Anthropic

print("=" * 70)
print("TEST: API KEY DE ANTHROPIC")
print("=" * 70)

# Cargar .env
load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")

if not api_key:
    print("\n ERROR: No se encontró ANTHROPIC_API_KEY en el archivo .env")
    print("\nSolución:")
    print("1. Crea un archivo .env en la carpeta TreballDeRecerca")
    print("2. Añade la línea: ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxx")
    print("3. Guarda el archivo")
    exit(1)

print(f"\n API key encontrada: {api_key[:20]}...")

# Intentar hacer una llamada simple
print("\n Intentando conectar con la API de Claude...")

try:
    client = Anthropic(api_key=api_key)

    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=100,
        messages=[{"role": "user", "content": "Di 'Hola, funciono!' en español."}],
    )

    respuesta = message.content[0].text
    print(f"\n ¡ÉXITO! Claude responde:")
    print(f"   {respuesta}")

    print("\n" + "=" * 70)
    print(" TODO FUNCIONA CORRECTAMENTE")
    print("=" * 70)
    print("\nAhora puedes ejecutar:")
    print("  python detector_claude.py")

except Exception as e:
    print(f"\n ERROR en la llamada a la API:")
    print(f"   {str(e)}")
    print("\nVerifica que:")
    print("1. La API key es correcta")
    print("2. Tienes conexión a internet")
    print("3. Tu cuenta de Anthropic tiene saldo/créditos")
    exit(1)
