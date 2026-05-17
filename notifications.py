import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

async def enviar_alerta(mensaje):
    """
    Envía un mensaje a Telegram de forma asíncrona.
    """
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print(">> [Telegram] Error: Faltan credenciales en el .env")
        return False
        
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": f"🤖 *ALERTA SINERGIA BOT*\n\n{mensaje}",
        "parse_mode": "Markdown"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    return True
                else:
                    print(f">> [Telegram] Error al enviar: {await response.text()}")
                    return False
    except Exception as e:
        print(f">> [Telegram] Error de conexión: {e}")
        return False

# Prueba rápida si se ejecuta solo
if __name__ == "__main__":
    import asyncio
    asyncio.run(enviar_alerta("¡Prueba de conexión exitosa! 🚀"))
