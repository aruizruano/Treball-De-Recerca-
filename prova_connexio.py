from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic()

respuesta = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=100,
    messages=[
        {"role": "user", "content": "Responde solo con: 'Conexión correcta, Arantxa!'"}
    ],
)

print(respuesta.content[0].text)
