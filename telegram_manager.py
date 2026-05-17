import asyncio
import os
import json
import random
import aiohttp
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Importar la suite Sinergia
import ai_agent
import auto_creator
import publisher
import notifications

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
WHATSAPP_PHONE = os.getenv("WHATSAPP_PHONE", "51947347666")

JSON_PATH = "contenido_ganoderma.json"

# Estado de la sesión del usuario (para flujos interactivos de texto como agendar fechas)
USER_STATES = {}

def cargar_json():
    if not os.path.exists(JSON_PATH):
        return []
    try:
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error al cargar JSON: {e}")
        return []

def guardar_json(data):
    try:
        with open(JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error al guardar JSON: {e}")
        return False

async def obtener_menu_principal():
    """Genera el teclado interactivo del menú principal con opción de Imagen o Solo Texto."""
    return {
        "inline_keyboard": [
            [
                {"text": "📢 Generar Post Salud", "callback_data": "cmd_generar_salud"},
                {"text": "💼 Generar Post Negocio", "callback_data": "cmd_generar_negocio"}
            ],
            [
                {"text": "📝 Solo Texto Salud", "callback_data": "cmd_texto_salud"},
                {"text": "📝 Solo Texto Negocio", "callback_data": "cmd_texto_negocio"}
            ],
            [
                {"text": "📋 Ver Cola de Publicaciones", "callback_data": "cmd_ver_cola"},
                {"text": "❓ Ayuda", "callback_data": "cmd_ayuda"}
            ]
        ]
    }

async def enviar_menu_inicio():
    mensaje = (
        "🤖 <b>BIENVENIDO AL PANEL INTERACTIVO DE SINERGIA PRO</b>\n\n"
        "Desde este búnker en tu celular puedes controlar todas las publicaciones de tu FanPage. "
        "Usa los botones táctiles de abajo para crear y programar material con Inteligencia Artificial."
    )
    markup = await obtener_menu_principal()
    await notifications.enviar_mensaje_interactivo(mensaje, markup)

async def manejar_generar_post(categoria, solo_texto=False):
    """
    Genera un borrador completo:
    - Con imagen: Imagen HD + Copy + Botones.
    - Solo texto: Copy + Botones.
    """
    if solo_texto:
        await notifications.enviar_alerta(f"⏳ <b>Generando copy de {categoria.upper()} (Solo Texto)...</b> Esto tomará unos segundos. Activando a Gemini.")
    else:
        await notifications.enviar_alerta(f"⏳ <b>Generando borrador de {categoria.upper()}...</b> Esto tomará unos segundos. Activando la fábrica visual y a Gemini.")
    
    # 1. Crear el borrador en la base de datos
    contenido = cargar_json()
    nuevo_id = f"pub_telegram_{int(datetime.now().timestamp())}"
    
    # Elegir frase/hook rotativo (solo si se necesita imagen, para la estampa)
    hooks = auto_creator.HOOKS_SALUD if categoria == "salud" else auto_creator.HOOKS_NEGOCIO
    frase_elegida = random.choice(hooks)
    
    # 2. Fabricar Imagen Brandeada en alta definición (omitir si es solo_texto)
    ruta_imagen = None
    if not solo_texto:
        idx = random.randint(10, 99)
        try:
            ruta_imagen = auto_creator.crear_tarjeta_viral(frase_elegida, categoria, idx)
        except Exception as e:
            print(f"Error al crear tarjeta viral: {e}")
            ruta_imagen = "imagenes/logo_autorizado.png"
            
        # Verificar existencia y aplicar salvaguarda de imagen sólida al vuelo si no existe
        if not os.path.exists(ruta_imagen):
            try:
                from PIL import Image
                os.makedirs("imagenes", exist_ok=True)
                img_backup = Image.new("RGB", (1080, 1080), (54, 25, 11))
                ruta_imagen = "imagenes/backup_temp.jpg"
                img_backup.save(ruta_imagen)
                print(">> [Salvaguarda] Imagen no encontrada. Generado fondo sólido temporal de respaldo.")
            except Exception as e_img:
                print(f">> [Salvaguarda] Fallo al crear imagen de respaldo: {e_img}")
        
    # 3. Generar Copy Persuasivo con IA de Gemini
    try:
        copy_ia = ai_agent.generar_copy_ia(nuevo_id, WHATSAPP_PHONE)
    except Exception as e:
        copy_ia = (
            f"¡Descubre el poder del bienestar natural con Gano iTouch! ☕🍄\n"
            f"Adquiérelo aquí: {os.getenv('AFFILIATE_LINK')}\n#Bienestar"
        )
        
    # Guardar en base de datos en estado de borrador
    nuevo_post = {
        "id": nuevo_id,
        "estado": "borrador",
        "texto": copy_ia,
        "categoria_imagen": categoria,
        "ruta_imagen_local": ruta_imagen,
        "solo_texto": solo_texto,
        "fecha_publicacion": None
    }
    
    contenido.append(nuevo_post)
    guardar_json(contenido)
    
    # Escapar contenido de texto para compatibilidad perfecta con HTML de Telegram
    copy_ia_escaped = copy_ia.replace("<", "&lt;").replace(">", "&gt;")
    
    # 4. Enviar a Telegram
    if not solo_texto:
        # Enviar la Fotografía Brandeada primero
        caption_foto = (
            f"📷 <b>DISEÑO BRANDRADO DE {categoria.upper()}</b>\n"
            f"<i>Archivo: {os.path.basename(ruta_imagen)} (estampado con tu logo oficial)</i>"
        )
        await notifications.enviar_foto_interactiva(ruta_imagen, caption_foto)
    
    # Enviar el Copy persuasivo completo como mensaje de texto dedicado (soporta 4096 caracteres)
    mensaje_copy = (
        f"✍️ <b>BORRADOR DE COPY CREADO POR LA IA ({categoria.upper()}){' [SÓLO TEXTO]' if solo_texto else ''}</b>\n\n"
        f"{copy_ia_escaped}\n\n"
        f"👇 <b>¿Qué deseas hacer con esta publicación?</b>"
    )
    
    markup = {
        "inline_keyboard": [
            [
                {"text": "✅ Publicar Ahora", "callback_data": f"act_pub_{nuevo_id}"},
                {"text": "📅 Programar", "callback_data": f"act_prog_{nuevo_id}"}
            ],
            [
                {"text": "🤖 Auto-Piloto", "callback_data": f"act_auto_{nuevo_id}"},
                {"text": "❌ Descartar", "callback_data": f"act_desc_{nuevo_id}"}
            ]
        ]
    }
    
    await notifications.enviar_mensaje_interactivo(mensaje_copy, markup)

async def procesar_publicacion_inmediata(post_id, message_id):
    """Ejecuta Playwright de forma inmediata en la nube para publicar en Facebook."""
    await notifications.enviar_alerta("🚀 <b>INICIANDO PUBLICACIÓN:</b> Abriendo Meta Business Suite en Nueva York. Mantente al tanto...")
    
    contenido = cargar_json()
    post = next((p for p in contenido if p["id"] == post_id), None)
    
    if not post:
        await notifications.enviar_alerta("❌ Error: No se encontró el borrador en el servidor.")
        return
        
    # Cambiar estado para que sea publicable
    post["estado"] = "aprobado"
    guardar_json(contenido)
    
    # Iniciar Playwright
    from playwright.async_api import async_playwright
    
    exito = False
    try:
        async with async_playwright() as p:
            context = await p.chromium.launch_persistent_context(
                user_data_dir="./playwright_profile",
                headless=False,
                args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
            )
            exito = await publisher.publicar_en_meta(context, post)
            await context.close()
    except Exception as e:
        print(f"Error al publicar por Telegram: {e}")
        
    if exito:
        post["fecha_publicacion"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        guardar_json(contenido)
        
        caption_exito = (
            f"✅ <b>¡PUBLICACIÓN ENVIADA CON ÉXITO!</b> 🚀\n\n"
            f"Este post sobre <code>{post.get('categoria_imagen')}</code> ya se encuentra publicado en tu FanPage oficial de Facebook.\n"
            f"¡Listos para recibir prospectos de WhatsApp!"
        )
        await notifications.editar_mensaje(message_id, caption_exito, {"inline_keyboard": []})
    else:
        await notifications.enviar_alerta("❌ <b>ERROR:</b> No se pudo publicar. Entra a tu monitor VNC para revisar si Facebook te pidió clave.")

async def manejar_callback(callback):
    """Procesa los toques en los botones interactivos."""
    data = callback.get("data")
    message = callback.get("message", {})
    message_id = message.get("message_id")
    callback_id = callback.get("id")
    
    url_resp = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/answerCallbackQuery"
    try:
        async with aiohttp.ClientSession() as session:
            await session.post(url_resp, json={"callback_query_id": callback_id})
    except Exception as e:
        print(f"Error respondiendo callback: {e}")
        
    if not data:
        return
        
    print(f">> [Callback] Procesando toque: {data}")
    
    # Menú Principal
    if data == "cmd_generar_salud":
        await manejar_generar_post("salud", solo_texto=False)
    elif data == "cmd_generar_negocio":
        await manejar_generar_post("negocio", solo_texto=False)
    elif data == "cmd_texto_salud":
        await manejar_generar_post("salud", solo_texto=True)
    elif data == "cmd_texto_negocio":
        await manejar_generar_post("negocio", solo_texto=True)
    elif data == "cmd_ver_cola":
        contenido = cargar_json()
        pendientes = [p for p in contenido if p.get("estado") == "aprobado" and not p.get("fecha_publicacion")]
        if not pendientes:
            await notifications.enviar_alerta("📋 <b>COLA VACÍA:</b> No tienes publicaciones agendadas para el futuro. ¡Prueba a generar una ahora!")
        else:
            txt = "📋 <b>COLA DE PUBLICACIONES AGENDADAS:</b>\n\n"
            for idx, p in enumerate(pendientes):
                txt += f"{idx+1}. <code>{p['id']}</code> - Categoría: <b>{p.get('categoria_imagen')}</b> (Programado)\n"
            await notifications.enviar_alerta(txt)
    elif data == "cmd_ayuda":
        txt = (
            "📖 <b>GUÍA RÁPIDA DE COMANDOS SINERGIA:</b>\n\n"
            "• <code>/generar_salud</code>: Crea borrador con imagen sobre Ganoderma.\n"
            "• <code>/generar_negocio</code>: Crea borrador con imagen sobre Redes.\n"
            "• <code>/texto_salud</code>: Borrador de SOLO texto sobre Ganoderma.\n"
            "• <code>/texto_negocio</code>: Borrador de SOLO texto sobre Redes.\n"
            "• <code>/cola</code>: Muestra posts agendados.\n"
            "• <code>/start</code>: Abre el menú principal con botones interactivos."
        )
        await notifications.enviar_alerta(txt)
        
    # Acciones de Borrador (Ahora editan el mensaje de texto dedicado, no la foto)
    elif data.startswith("act_pub_"):
        post_id = data.replace("act_pub_", "")
        await procesar_publicacion_inmediata(post_id, message_id)
        
    elif data.startswith("act_prog_"):
        post_id = data.replace("act_prog_", "")
        USER_STATES[TELEGRAM_CHAT_ID] = f"esperando_fecha_{post_id}_{message_id}"
        await notifications.enviar_alerta(
            "📅 <b>PROGRAMACIÓN MANUAL:</b>\n\n"
            "Escribe y envíame la fecha y hora en la que quieres que se publique en este formato exacto:\n"
            "👉 <code>AAAA-MM-DD HH:MM</code>\n\n"
            "*(Ejemplo: 2026-05-18 15:30)*"
        )
        
    elif data.startswith("act_auto_"):
        post_id = data.replace("act_auto_", "")
        contenido = cargar_json()
        post = next((p for p in contenido if p["id"] == post_id), None)
        
        if post:
            fecha_auto = (datetime.now() + timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S")
            post["estado"] = "aprobado"
            post["fecha_programada"] = fecha_auto
            guardar_json(contenido)
            
            caption_auto = (
                f"🤖 <b>¡PILOTO AUTOMÁTICO ACTIVADO!</b> 📅\n\n"
                f"El post sobre <code>{post.get('categoria_imagen')}</code> se ha aprobado y se publicará de forma totalmente automática el:\n"
                f"👉 <b>{fecha_auto}</b>\n\n"
                f"¡Puedes relajarte, Sinergia se encarga!"
            )
            await notifications.editar_mensaje(message_id, caption_auto, {"inline_keyboard": []})
            
    elif data.startswith("act_desc_"):
        post_id = data.replace("act_desc_", "")
        contenido = cargar_json()
        contenido = [p for p in contenido if p["id"] != post_id]
        guardar_json(contenido)
        
        caption_desc = "❌ <b>Borrador cancelado y eliminado de la cola del servidor.</b>"
        await notifications.editar_mensaje(message_id, caption_desc, {"inline_keyboard": []})

async def manejar_mensaje_texto(text):
    """Procesamiento de comandos normales o de flujos conversacionales."""
    text_strip = text.strip()
    user_state = USER_STATES.get(TELEGRAM_CHAT_ID)
    
    if user_state and user_state.startswith("esperando_fecha_"):
        parts = user_state.split("_")
        post_id = "_".join(parts[2:-1])
        message_id = parts[-1]
        
        try:
            fecha_valida = datetime.strptime(text_strip, "%Y-%m-%d %H:%M")
            fecha_str = fecha_valida.strftime("%Y-%m-%d %H:%M:%S")
            
            contenido = cargar_json()
            post = next((p for p in contenido if p["id"] == post_id), None)
            
            if post:
                post["estado"] = "aprobado"
                post["fecha_programada"] = fecha_str
                guardar_json(contenido)
                
                USER_STATES[TELEGRAM_CHAT_ID] = None
                
                caption_confirmado = (
                    f"📅 <b>¡POST PROGRAMADO CON ÉXITO!</b> ✅\n\n"
                    f"Tu publicación sobre <code>{post.get('categoria_imagen')}</code> ha sido agendada para:\n"
                    f"👉 <b>{fecha_str}</b>\n\n"
                    f"Se subirá de forma 100% automática a tu FanPage en esa fecha."
                )
                await notifications.editar_mensaje(message_id, caption_confirmado, {"inline_keyboard": []})
                await notifications.enviar_alerta("👍 ¡Listo! Fecha agendada y guardada en el bunker.")
            else:
                await notifications.enviar_alerta("❌ Error: No se encontró el post correspondiente en el JSON.")
                USER_STATES[TELEGRAM_CHAT_ID] = None
        except ValueError:
            await notifications.enviar_alerta(
                "⚠️ <b>Formato incorrecto.</b> Por favor escribe la fecha exactamente así:\n"
                "<code>AAAA-MM-DD HH:MM</code> (Ejemplo: <code>2026-05-18 16:45</code>)\n\n"
                "Inténtalo de nuevo o escribe `/cancelar`:"
            )
        return

    # Comandos Generales
    if text_strip == "/start":
        await enviar_menu_inicio()
    elif text_strip == "/ayuda":
        txt = (
            "📖 <b>GUÍA RÁPIDA DE COMANDOS SINERGIA:</b>\n\n"
            "• <code>/generar_salud</code>: Borrador con imagen de Ganoderma.\n"
            "• <code>/generar_negocio</code>: Borrador con imagen de Redes.\n"
            "• <code>/texto_salud</code>: Borrador de SOLO texto de Ganoderma.\n"
            "• <code>/texto_negocio</code>: Borrador de SOLO texto de Redes.\n"
            "• <code>/cola</code>: Muestra la cola de posts agendados.\n"
            "• <code>/start</code>: Abre el panel principal interactivo."
        )
        await notifications.enviar_alerta(txt)
    elif text_strip == "/generar_salud":
        await manejar_generar_post("salud", solo_texto=False)
    elif text_strip == "/generar_negocio":
        await manejar_generar_post("negocio", solo_texto=False)
    elif text_strip == "/texto_salud":
        await manejar_generar_post("salud", solo_texto=True)
    elif text_strip == "/texto_negocio":
        await manejar_generar_post("negocio", solo_texto=True)
    elif text_strip == "/cola":
        contenido = cargar_json()
        pendientes = [p for p in contenido if p.get("estado") == "aprobado" and not p.get("fecha_publicacion")]
        if not pendientes:
            await notifications.enviar_alerta("📋 <b>COLA VACÍA:</b> No tienes publicaciones agendadas para el futuro.")
        else:
            txt = "📋 <b>COLA DE PUBLICACIONES AGENDADAS:</b>\n\n"
            for idx, p in enumerate(pendientes):
                txt += f"{idx+1}. <code>{p['id']}</code> - Categoría: <b>{p.get('categoria_imagen')}</b> (Programado)\n"
            await notifications.enviar_alerta(txt)
    elif text_strip == "/cancelar":
        USER_STATES[TELEGRAM_CHAT_ID] = None
        await notifications.enviar_alerta("👍 Flujo cancelado. Volvemos al inicio.")
    else:
        await notifications.enviar_alerta(
            "🤖 <b>Sinergia Guardián:</b> No entendí ese comando. Escribe <code>/start</code> para abrir el panel de control táctil de tu bot."
        )

async def bucle_escucha_telegram():
    if not TELEGRAM_TOKEN:
        print(">> [Telegram Engine] Error crucial: Falta TELEGRAM_TOKEN en el .env")
        return
        
    print("==================================================")
    print("   INICIANDO MÓDULO INTERACTIVO DE TELEGRAM       ")
    print("==================================================")
    print(">> Buscando actualizaciones en tiempo real...")
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
    offset = 0
    
    try:
        await enviar_menu_inicio()
    except Exception as e:
        print(f"Error al enviar menú inicial: {e}")
        
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                params = {"timeout": 30, "offset": offset}
                async with session.get(url, params=params, timeout=40) as response:
                    if response.status == 200:
                        res = await response.json()
                        updates = res.get("result", [])
                        
                        for update in updates:
                            offset = update["update_id"] + 1
                            
                            if "callback_query" in update:
                                await manejar_callback(update["callback_query"])
                            elif "message" in update:
                                msg = update["message"]
                                text = msg.get("text")
                                chat = msg.get("chat", {})
                                chat_id = str(chat.get("id"))
                                
                                if chat_id == str(TELEGRAM_CHAT_ID) and text:
                                    await manejar_mensaje_texto(text)
                                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f">> [Telegram Engine] Alerta de red o reconexión: {e}")
                await asyncio.sleep(5)
                
            await asyncio.sleep(0.5)

if __name__ == "__main__":
    try:
        asyncio.run(bucle_escucha_telegram())
    except KeyboardInterrupt:
        print("\nMódulo de Telegram detenido.")
