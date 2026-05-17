import aiohttp
import os
import json
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

async def enviar_alerta(mensaje):
    """
    Envía un mensaje a Telegram en formato HTML de forma asíncrona.
    """
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print(">> [Telegram] Error: Faltan credenciales en el .env")
        return False
        
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    
    # Reemplazar posibles marcas markdown básicas a HTML para mantener compatibilidad
    mensaje_html = mensaje.replace("🤖 *ALERTA SINERGIA BOT*", "🤖 <b>ALERTA SINERGIA BOT</b>")
    mensaje_html = mensaje_html.replace("⏳ *", "⏳ <b>").replace("🚀 *", "🚀 <b>").replace("✅ *", "✅ <b>")
    mensaje_html = mensaje_html.replace("❌ *", "❌ <b>").replace("⚠️ *", "⚠️ <b>").replace("📋 *", "📋 <b>")
    mensaje_html = mensaje_html.replace("📅 *", "📅 <b>").replace("👍 *", "👍 <b>")
    mensaje_html = mensaje_html.replace("*", "</b>", 1) # Cierre básico
    
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": f"🤖 <b>ALERTA SINERGIA BOT</b>\n\n{mensaje}",
        "parse_mode": "HTML"
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

async def enviar_mensaje_interactivo(mensaje, reply_markup=None):
    """
    Envía un mensaje de texto HTML con botones interactivos opcionales.
    """
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return None
        
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mensaje,
        "parse_mode": "HTML"
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
        
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    res_json = await response.json()
                    return res_json.get("result", {}).get("message_id")
    except Exception as e:
        print(f">> [Telegram] Error interactivo: {e}")
    return None

async def enviar_foto_interactiva(foto_path, caption, reply_markup=None):
    """
    Envía una fotografía con una descripción HTML y botones interactivos.
    """
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return None
        
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    
    data = aiohttp.FormData()
    data.add_field('chat_id', str(TELEGRAM_CHAT_ID))
    data.add_field('caption', caption)
    data.add_field('parse_mode', 'HTML')
    if reply_markup:
        data.add_field('reply_markup', json.dumps(reply_markup))
        
    if not os.path.exists(foto_path):
        print(f">> [Telegram] Error: La imagen {foto_path} no existe.")
        return None
        
    try:
        async with aiohttp.ClientSession() as session:
            with open(foto_path, 'rb') as f:
                data.add_field('photo', f, filename=os.path.basename(foto_path))
                async with session.post(url, data=data) as response:
                    if response.status == 200:
                        res_json = await response.json()
                        return res_json.get("result", {}).get("message_id")
                    else:
                        print(f">> [Telegram] Error al enviar foto: {await response.text()}")
    except Exception as e:
        print(f">> [Telegram] Error interactivo de foto: {e}")
    return None

async def editar_mensaje(message_id, nuevo_texto, reply_markup=None):
    """
    Modifica un mensaje de texto enviado anteriormente usando HTML.
    """
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return False
        
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/editMessageText"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "message_id": message_id,
        "text": nuevo_texto,
        "parse_mode": "HTML"
    }
    if reply_markup is not None:
        payload["reply_markup"] = reply_markup
        
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                return response.status == 200
    except Exception as e:
        print(f">> [Telegram] Error al editar mensaje: {e}")
    return False

async def editar_caption(message_id, nuevo_caption, reply_markup=None):
    """
    Modifica la descripción HTML y botones de una fotografía enviada anteriormente.
    """
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return False
        
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/editMessageCaption"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "message_id": message_id,
        "caption": nuevo_caption,
        "parse_mode": "HTML"
    }
    if reply_markup is not None:
        payload["reply_markup"] = reply_markup
        
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                return response.status == 200
    except Exception as e:
        print(f">> [Telegram] Error al editar caption: {e}")
    return False
