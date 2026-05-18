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

# Configuración automática de Display para servidores Linux sin monitor físico (noVNC)
if os.name == "posix" and "DISPLAY" not in os.environ:
    os.environ["DISPLAY"] = ":99"

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
WHATSAPP_PHONE = os.getenv("WHATSAPP_PHONE", "51947347666")

JSON_PATH = "contenido_ganoderma.json"
AFILIADOS_PATH = "afiliados.json"

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

def cargar_afiliados():
    default_data = {
        str(TELEGRAM_CHAT_ID): {
            "nombre": "Jorge Rodríguez (Admin)",
            "link_tienda": f"https://peru.ganoitouch.biz/{os.getenv('GANO_ITOUCH_STORE', 'joherobacafe')}",
            "whatsapp": WHATSAPP_PHONE,
            "activo": True,
            "rol": "admin"
        }
    }
    if not os.path.exists(AFILIADOS_PATH):
        guardar_afiliados(default_data)
        return default_data
    try:
        with open(AFILIADOS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error al cargar afiliados: {e}")
        return default_data

def guardar_afiliados(data):
    try:
        with open(AFILIADOS_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error al guardar afiliados: {e}")
        return False

async def obtener_menu_principal(chat_id):
    """Genera el teclado interactivo del menú principal con opción de Imagen o Solo Texto."""
    afiliados = cargar_afiliados()
    perfil = afiliados.get(str(chat_id), {})
    rol = perfil.get("rol", "usuario")
    
    keyboard = [
        [
            {"text": "📢 Generar Post Salud", "callback_data": "cmd_generar_salud"},
            {"text": "💼 Generar Post Negocio", "callback_data": "cmd_generar_negocio"}
        ],
        [
            {"text": "📝 Solo Texto Salud", "callback_data": "cmd_texto_salud"},
            {"text": "📝 Solo Texto Negocio", "callback_data": "cmd_texto_negocio"}
        ],
        [
            {"text": "🚀 Impulsar en Equipo (Sinergia Boost)", "callback_data": "cmd_sinergia_boost"}
        ]
    ]
    
    # Mostrar la opción de cola de publicación solo al Admin (dueño del Fanpage)
    if rol == "admin":
        keyboard.append([
            {"text": "📋 Ver Cola de Publicaciones", "callback_data": "cmd_ver_cola"},
            {"text": "❓ Ayuda", "callback_data": "cmd_ayuda"}
        ])
    else:
        keyboard.append([
            {"text": "❓ Ayuda e Instrucciones", "callback_data": "cmd_ayuda"}
        ])
        
    return {"inline_keyboard": keyboard}

async def manejar_sinergia_boost(chat_id):
    """Muestra el panel Sinergia Boost con las últimas publicaciones oficiales para interactuar en masa."""
    contenido = cargar_json()
    
    # Filtrar posts publicados (aprobados y con fecha de publicación)
    publicados = [p for p in contenido if p.get("estado") == "aprobado" and p.get("fecha_publicacion")]
    # Ordenar por fecha de publicación descendente (más recientes primero)
    publicados.sort(key=lambda x: x.get("fecha_publicacion", ""), reverse=True)
    
    page_id = os.getenv("FACEBOOK_PAGE_ID", "100080372792708")
    page_url = f"https://www.facebook.com/{page_id}"
    
    mensaje = (
        f"🚀 <b>SINERGIA BOOST: IMPULSO COLECTIVO</b> 🔥\n\n"
        f"Líder, aquí tienes las últimas publicaciones oficiales de nuestra FanPage.\n"
        f"<b>¡Ayuda a darles likes, comentar y compartirlas en tu muro!</b> Esto posiciona la marca y atrae prospectos a todo el equipo.\n\n"
    )
    
    keyboard = []
    
    if not publicados:
        mensaje += "📭 <i>Aún no hay publicaciones oficiales registradas para impulsar esta semana. ¡Vuelve pronto!</i>"
        keyboard.append([{"text": "🔄 Volver al Inicio", "callback_data": "cmd_menu_inicio"}])
    else:
        for idx, post in enumerate(publicados[:3]):
            cat = post.get("categoria_imagen", "General").upper()
            fecha = post.get("fecha_publicacion", "")[:10]
            texto_prev = post.get("texto", "")[:60].replace("<", "&lt;").replace(">", "&gt;") + "..."
            
            mensaje += (
                f"<b>{idx+1}️⃣ Post de {cat}</b> ({fecha})\n"
                f"📝 <i>{texto_prev}</i>\n\n"
            )
            
            # Botones para interactuar con este post
            compartir_url = f"https://www.facebook.com/sharer/sharer.php?u={page_url}"
            keyboard.append([
                {"text": f"💬 Like y Comentar ({cat})", "url": page_url},
                {"text": f"📢 Compartir en 1 Clic", "url": compartir_url}
            ])
            
        keyboard.append([{"text": "🔄 Volver al Inicio", "callback_data": "cmd_menu_inicio"}])
        
    markup = {"inline_keyboard": keyboard}
    await notifications.enviar_mensaje_interactivo(mensaje, markup, chat_id=chat_id)

async def enviar_menu_inicio(chat_id):
    afiliados = cargar_afiliados()
    perfil = afiliados.get(str(chat_id), {})
    nombre = perfil.get("nombre", "Líder Gano iTouch")
    link = perfil.get("link_tienda", "No registrado")
    
    mensaje = (
        f"🤖 <b>PANEL INTERACTIVO DE SINERGIA BOT</b>\n\n"
        f"Hola <b>{nombre}</b>. Tu Robot de Prospección está listo.\n"
        f"🔗 Enlace activo: <code>{link}</code>\n"
        f"📱 WhatsApp: <code>+{perfil.get('whatsapp', WHATSAPP_PHONE)}</code>\n\n"
        f"Usa los botones táctiles de abajo para crear imágenes premium y copias persuasivas personalizadas."
    )
    markup = await obtener_menu_principal(chat_id)
    await notifications.enviar_mensaje_interactivo(mensaje, markup, chat_id=chat_id)

async def manejar_generar_post(chat_id, categoria, solo_texto=False):
    """
    Genera un borrador completo personalizado para el distribuidor solicitante.
    """
    afiliados = cargar_afiliados()
    perfil = afiliados.get(str(chat_id), {})
    
    if not perfil or not perfil.get("activo"):
        await notifications.enviar_alerta("❌ Tu suscripción a Sinergia Bot no está activa.", chat_id=chat_id)
        return
        
    custom_whatsapp = perfil.get("whatsapp", WHATSAPP_PHONE)
    custom_link = perfil.get("link_tienda")
    
    if solo_texto:
        await notifications.enviar_alerta(f"⏳ <b>Generando copy de {categoria.upper()} (Solo Texto)...</b> Esto tomará unos segundos. Conectando con la IA.", chat_id=chat_id)
    else:
        await notifications.enviar_alerta(f"⏳ <b>Generando borrador de {categoria.upper()}...</b> Esto tomará unos segundos. Diseñando banner HD y copy persuasivo.", chat_id=chat_id)
    
    # 1. Crear el borrador en la base de datos
    contenido = cargar_json()
    nuevo_id = f"pub_tg_{chat_id}_{int(datetime.now().timestamp())}"
    
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
            
        if not os.path.exists(ruta_imagen):
            try:
                from PIL import Image
                os.makedirs("imagenes", exist_ok=True)
                img_backup = Image.new("RGB", (1080, 1080), (54, 25, 11))
                ruta_imagen = "imagenes/backup_temp.jpg"
                img_backup.save(ruta_imagen)
            except Exception as e_img:
                print(f">> [Salvaguarda] Fallo al crear imagen: {e_img}")
        
    # 3. Generar Copy Persuasivo con IA (inyectando el link del distribuidor)
    try:
        copy_ia = ai_agent.generar_copy_ia(nuevo_id, custom_whatsapp, custom_link)
    except Exception as e:
        copy_ia = (
            f"¡Descubre el poder del bienestar natural con Gano iTouch! ☕🍄\n"
            f"Adquiérelo aquí: {custom_link or 'https://peru.ganoitouch.biz/joherobacafe'}\n#Bienestar"
        )
        
    # Guardar en base de datos en estado de borrador
    nuevo_post = {
        "id": nuevo_id,
        "chat_id": str(chat_id),
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
        caption_foto = (
            f"📷 <b>DISEÑO BRANDRADO DE {categoria.upper()}</b>\n"
            f"<i>Descarga esta imagen y compártela en tus redes.</i>"
        )
        await notifications.enviar_foto_interactiva(ruta_imagen, caption_foto, chat_id=chat_id)
    
    # Si es Admin (Jorge), mostrar botones de publicación automática. Si es Downline, mostrar menú de cierre
    es_admin = perfil.get("rol") == "admin"
    
    mensaje_copy = (
        f"✍️ <b>BORRADOR DE COPY PERSONALIZADO ({categoria.upper()})</b>\n\n"
        f"{copy_ia_escaped}\n\n"
    )
    
    if es_admin:
        mensaje_copy += f"👇 <b>¿Qué deseas hacer con esta publicación en tu FanPage?</b>"
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
    else:
        mensaje_copy += (
            f"💡 <b>¡Todo listo!</b> Copia el texto de arriba manteniendo presionado, "
            f"guarda la imagen y súbelo a tus estados de WhatsApp o Facebook para captar prospectos con tu enlace."
        )
        markup = {
            "inline_keyboard": [
                [
                    {"text": "🔄 Crear Otro Post", "callback_data": "cmd_menu_inicio"}
                ]
            ]
        }
    
    await notifications.enviar_mensaje_interactivo(mensaje_copy, markup, chat_id=chat_id)

async def procesar_publicacion_inmediata(post_id, message_id, chat_id):
    """Ejecuta Playwright de forma inmediata en la nube para publicar en Facebook (Solo Admin)."""
    await notifications.enviar_alerta("🚀 <b>INICIANDO PUBLICACIÓN:</b> Abriendo Meta Business Suite en Nueva York. Mantente al tanto...", chat_id=chat_id)
    
    contenido = cargar_json()
    post = next((p for p in contenido if p["id"] == post_id), None)
    
    if not post:
        await notifications.enviar_alerta("❌ Error: No se encontró el borrador en el servidor.", chat_id=chat_id)
        return
        
    post["estado"] = "aprobado"
    guardar_json(contenido)
    
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
        await notifications.editar_mensaje(message_id, caption_exito, {"inline_keyboard": []}, chat_id=chat_id)
    else:
        error_img = f"error_{post_id}.png"
        if os.path.exists(error_img):
            await notifications.enviar_foto_interactiva(
                foto_path=error_img,
                caption=f"❌ <b>ERROR DE PUBLICACIÓN:</b> No se pudo concretar en Meta.\n\nAquí tienes la captura de pantalla de lo que vio el bot en noVNC para diagnosticar el problema.",
                chat_id=chat_id
            )
            try:
                os.remove(error_img) # Limpiar después de enviar
            except Exception:
                pass
        else:
            await notifications.enviar_alerta("❌ <b>ERROR:</b> No se pudo publicar. Entra a tu monitor VNC para revisar si Facebook te pidió clave.", chat_id=chat_id)

async def manejar_callback(callback):
    """Procesa los toques en los botones interactivos."""
    data = callback.get("data")
    message = callback.get("message", {})
    message_id = message.get("message_id")
    callback_id = callback.get("id")
    chat_id = str(message.get("chat", {}).get("id"))
    
    url_resp = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/answerCallbackQuery"
    try:
        async with aiohttp.ClientSession() as session:
            await session.post(url_resp, json={"callback_query_id": callback_id})
    except Exception as e:
        print(f"Error respondiendo callback: {e}")
        
    if not data:
        return
        
    print(f">> [Callback User {chat_id}] Procesando toque: {data}")
    
    # Menú Principal
    if data == "cmd_generar_salud":
        await manejar_generar_post(chat_id, "salud", solo_texto=False)
    elif data == "cmd_generar_negocio":
        await manejar_generar_post(chat_id, "negocio", solo_texto=False)
    elif data == "cmd_texto_salud":
        await manejar_generar_post(chat_id, "salud", solo_texto=True)
    elif data == "cmd_texto_negocio":
        await manejar_generar_post(chat_id, "negocio", solo_texto=True)
    elif data == "cmd_menu_inicio":
        await enviar_menu_inicio(chat_id)
    elif data == "cmd_sinergia_boost":
        await manejar_sinergia_boost(chat_id)
    elif data == "cmd_ver_cola":
        contenido = cargar_json()
        pendientes = [p for p in contenido if p.get("estado") == "aprobado" and not p.get("fecha_publicacion")]
        if not pendientes:
            await notifications.enviar_alerta("📋 <b>COLA VACÍA:</b> No tienes publicaciones agendadas para el futuro. ¡Prueba a generar una ahora!", chat_id=chat_id)
        else:
            txt = "📋 <b>COLA DE PUBLICACIONES AGENDADAS:</b>\n\n"
            for idx, p in enumerate(pendientes):
                txt += f"{idx+1}. <code>{p['id']}</code> - Categoría: <b>{p.get('categoria_imagen')}</b> (Programado)\n"
            await notifications.enviar_alerta(txt, chat_id=chat_id)
    elif data == "cmd_ayuda":
        txt = (
            "📖 <b>GUÍA DE COMANDOS SINERGIA BOT:</b>\n\n"
            "• <code>/generar_salud</code>: Borrador con imagen de Ganoderma.\n"
            "• <code>/generar_negocio</code>: Borrador con imagen de Redes.\n"
            "• <code>/texto_salud</code>: Borrador de SOLO texto de Ganoderma.\n"
            "• <code>/texto_negocio</code>: Borrador de SOLO texto de Redes.\n"
            "• <code>/link [enlace]</code>: Registra tu enlace de afiliado.\n"
            "• <code>/whatsapp [numero]</code>: Registra tu WhatsApp corporativo.\n"
            "• <code>/start</code>: Abre el panel interactivo principal."
        )
        await notifications.enviar_mensaje_interactivo(txt, chat_id=chat_id)
        
    # Acciones de Borrador (Solo Admin)
    elif data.startswith("act_pub_"):
        post_id = data.replace("act_pub_", "")
        await procesar_publicacion_inmediata(post_id, message_id, chat_id)
        
    elif data.startswith("act_prog_"):
        post_id = data.replace("act_prog_", "")
        USER_STATES[chat_id] = f"esperando_fecha_{post_id}_{message_id}"
        await notifications.enviar_alerta(
            "📅 <b>PROGRAMACIÓN MANUAL:</b>\n\n"
            "Escribe y envíame la fecha y hora en la que quieres que se publique en este formato exacto:\n"
            "👉 <code>AAAA-MM-DD HH:MM</code>\n\n"
            "*(Ejemplo: 2026-05-18 15:30)*",
            chat_id=chat_id
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
                f"El post se ha aprobado y se publicará de forma totalmente automática el:\n"
                f"👉 <b>{fecha_auto}</b>\n\n"
                f"¡Puedes relajarte, Sinergia se encarga!"
            )
            await notifications.editar_mensaje(message_id, caption_auto, {"inline_keyboard": []}, chat_id=chat_id)
            
    elif data.startswith("act_desc_"):
        post_id = data.replace("act_desc_", "")
        contenido = cargar_json()
        contenido = [p for p in contenido if p["id"] != post_id]
        guardar_json(contenido)
        
        caption_desc = "❌ <b>Borrador cancelado y eliminado de la cola del servidor.</b>"
        await notifications.editar_mensaje(message_id, caption_desc, {"inline_keyboard": []}, chat_id=chat_id)

async def manejar_mensaje_texto(chat_id, text, from_user):
    """Procesamiento de comandos normales o de flujos conversacionales (Multi-Usuario)."""
    text_strip = text.strip()
    user_state = USER_STATES.get(chat_id)
    afiliados = cargar_afiliados()
    perfil = afiliados.get(str(chat_id))
    
    if user_state and isinstance(user_state, dict) and user_state.get("state") == "ESPERANDO_PROMPT_CUSTOM":
        ruta_imagen_temp = user_state.get("ruta_imagen")
        prompt_usuario = text_strip
        
        USER_STATES[chat_id] = None
        
        await notifications.enviar_alerta("✍️ <b>Generando Copy persuasivo con IA y brandeando tu imagen...</b>\nEsto tomará solo unos segundos.", chat_id=chat_id)
        
        import branding_tool
        LOGO_PATH = "logo_distribuidor.png"
        ruta_branded = ruta_imagen_temp
        if os.path.exists(LOGO_PATH) and os.path.exists(ruta_imagen_temp):
            try:
                ruta_branded = branding_tool.brandear_imagen(ruta_imagen_temp, LOGO_PATH)
            except Exception as e_brand:
                print(f"Error branding custom image: {e_brand}")
                
        user_phone = perfil.get("whatsapp", WHATSAPP_PHONE) if perfil else WHATSAPP_PHONE
        user_store = perfil.get("link_tienda") if perfil else None
        
        if prompt_usuario.lower() == "/omitir":
            prompt_usuario = "General, destaca la energía celular, los antioxidantes y la delicia de las bebidas de Ganoderma Lucidum."
            
        try:
            texto_ia = ai_agent.generar_copy_personalizado_ia(prompt_usuario, user_phone, user_store)
        except Exception as e_ia:
            print(f"Error generating custom copy: {e_ia}")
            texto_ia = (
                f"☕️ ¡Sabor y bienestar garantizado en cada taza! 🌟\n\n"
                f"Disfruta hoy de los beneficios profundos del Ganoderma Lucidum soluble en mi portal oficial:\n"
                f"👉 {user_store if user_store else 'https://peru.ganoitouch.biz/joherobacafe'}\n\n"
                f"Consultas al WhatsApp: +{user_phone}"
            )
            
        contenido = cargar_json()
        post_id = f"custom_post_{datetime.now().strftime('%m%d_%H%M%S')}"
        nuevo_post = {
            "id": post_id,
            "texto": texto_ia,
            "ruta_imagen_local": ruta_branded,
            "categoria_imagen": "custom",
            "fecha_creacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "fecha_programada": (datetime.now() + timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S"),
            "estado": "aprobado",
            "chat_id": chat_id
        }
        contenido.append(nuevo_post)
        guardar_json(contenido)
        
        msg_victoria = (
            f"🎉 <b>¡PUBLICACIÓN PERSONALIZADA CREADA Y AGENDADA!</b>\n\n"
            f"✍️ <b>Texto redactado con IA:</b>\n"
            f"<i>\"{texto_ia[:250]}...\"</i>\n\n"
            f"📸 <b>Imagen brandeada con tu logotipo:</b>\n"
            f"<code>{os.path.basename(ruta_branded)}</code>\n\n"
            f"👉 <i>Esta publicación se enviará a tu FanPage automáticamente en 2 minutos. O puedes presionar <b>`✅ Publicar Ahora`</b> desde el menú interactivo para enviarla en este instante de forma supersónica.</i> 🚀"
        )
        await notifications.enviar_alerta(msg_victoria, chat_id=chat_id)
        return
    # --- COMANDOS PÚBLICOS DE ONBOARDING ---
    if text_strip.startswith("/link"):
        parts = text_strip.split()
        if len(parts) < 2:
            await notifications.enviar_mensaje_interactivo(
                "⚠️ <b>Uso correcto del comando:</b>\n"
                "<code>/link [tu_enlace_oficial_gano_itouch]</code>\n\n"
                "Ejemplo:\n"
                "<code>/link https://peru.ganoitouch.biz/mariacafe</code>",
                chat_id=chat_id
            )
            return
            
        link_usuario = parts[1]
        if not (link_usuario.startswith("https://") or link_usuario.startswith("http://")):
            await notifications.enviar_mensaje_interactivo("⚠️ El enlace debe comenzar con <code>https://</code>", chat_id=chat_id)
            return
            
        nombre_completo = f"{from_user.get('first_name', '')} {from_user.get('last_name', '')}".strip() or "Distribuidor"
        
        if not perfil:
            afiliados[str(chat_id)] = {
                "nombre": nombre_completo,
                "link_tienda": link_usuario,
                "whatsapp": WHATSAPP_PHONE, # Defecto inicial
                "activo": True,
                "rol": "usuario",
                "fecha_registro": datetime.now().strftime("%Y-%m-%d")
            }
        else:
            afiliados[str(chat_id)]["link_tienda"] = link_usuario
            afiliados[str(chat_id)]["nombre"] = nombre_completo
            
        guardar_afiliados(afiliados)
        
        await notifications.enviar_mensaje_interactivo(
            f"🎉 <b>¡PORTAL REGISTRADO CON ÉXITO!</b>\n\n"
            f"Hola <b>{nombre_completo}</b>, hemos guardado tus credenciales:\n"
            f"🔗 Tienda: <code>{link_usuario}</code>\n\n"
            f"Para personalizar al máximo tus copies persuasivos, te recomendamos hacer esto:\n"
            f"1️⃣ Registra tu número de WhatsApp corporativo usando:\n"
            f"👉 <code>/whatsapp [tu_numero_con_codigo_de_pais]</code> (ejemplo: <code>/whatsapp 51987654321</code>)\n\n"
            f"2️⃣ ¡Comienza a generar imágenes premium personalizadas!\n"
            f"👉 Envía <code>/start</code> para abrir tu menú interactivo.",
            chat_id=chat_id
        )
        return

    elif text_strip.startswith("/whatsapp"):
        if not perfil:
            await notifications.enviar_mensaje_interactivo("⚠️ Primero debes registrar tu enlace con el comando: `/link [tu_enlace]`", chat_id=chat_id)
            return
            
        parts = text_strip.split()
        if len(parts) < 2:
            await notifications.enviar_mensaje_interactivo("⚠️ <b>Uso correcto:</b> <code>/whatsapp [numero]</code>\nEjemplo: <code>/whatsapp 51987654321</code>", chat_id=chat_id)
            return
            
        numero = "".join(filter(str.isdigit, parts[1]))
        afiliados[str(chat_id)]["whatsapp"] = numero
        guardar_afiliados(afiliados)
        
        await notifications.enviar_mensaje_interactivo(f"✅ <b>WhatsApp Actualizado:</b> +{numero}. Todo listo para tus copies de prospección.", chat_id=chat_id)
        return

    # --- CONTROL DE ACCESO ---
    if not perfil or not perfil.get("activo"):
        await notifications.enviar_mensaje_interactivo(
            "🤖 <b>¡Hola! Bienvenido a Sinergia Bot Gano iTouch.</b>\n\n"
            "Para poder crear publicaciones persuasivas y banners premium personalizados con tu marca y enlace oficial, "
            "necesitas registrarte en nuestro bunker digital.\n\n"
            "Es sumamente fácil, solo envíame el siguiente comando:\n"
            "👉 <code>/link [tu_enlace_oficial_de_tienda]</code>",
            chat_id=chat_id
        )
        return

    # --- FLUJOS DE ESTADOS INTERACTIVOS (Solo Admin) ---
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
                
                USER_STATES[chat_id] = None
                
                caption_confirmado = (
                    f"📅 <b>¡POST PROGRAMADO CON ÉXITO!</b> ✅\n\n"
                    f"Tu publicación sobre <code>{post.get('categoria_imagen')}</code> ha sido agendada para:\n"
                    f"👉 <b>{fecha_str}</b>\n\n"
                    f"Se subirá de forma 100% automática a tu FanPage en esa fecha."
                )
                await notifications.editar_mensaje(message_id, caption_confirmado, {"inline_keyboard": []}, chat_id=chat_id)
                await notifications.enviar_alerta("👍 ¡Listo! Fecha agendada y guardada en el bunker.", chat_id=chat_id)
            else:
                await notifications.enviar_alerta("❌ Error: No se encontró el post correspondiente en el JSON.", chat_id=chat_id)
                USER_STATES[chat_id] = None
        except ValueError:
            await notifications.enviar_alerta(
                "⚠️ <b>Formato incorrecto.</b> Por favor escribe la fecha exactamente así:\n"
                "<code>AAAA-MM-DD HH:MM</code> (Ejemplo: <code>2026-05-18 16:45</code>)\n\n"
                "Inténtalo de nuevo o escribe `/cancelar`:",
                chat_id=chat_id
            )
        return

    # --- COMANDOS PRIVADOS AUTORIZADOS ---
    if text_strip == "/start":
        await enviar_menu_inicio(chat_id)
    elif text_strip == "/ayuda":
        txt = (
            "📖 <b>GUÍA RÁPIDA DE COMANDOS SINERGIA:</b>\n\n"
            "• <code>/generar_salud</code>: Borrador con imagen de Ganoderma.\n"
            "• <code>/generar_negocio</code>: Borrador con imagen de Redes.\n"
            "• <code>/texto_salud</code>: Borrador de SOLO texto de Ganoderma.\n"
            "• <code>/texto_negocio</code>: Borrador de SOLO texto de Redes.\n"
            "• <code>/boost</code> o <code>/impulsar</code>: Panel de viralización en equipo.\n"
            "• <code>/link [enlace]</code>: Actualiza tu enlace de Gano iTouch.\n"
            "• <code>/whatsapp [numero]</code>: Actualiza tu WhatsApp.\n"
            "• <code>/start</code>: Abre el panel principal interactivo."
        )
        await notifications.enviar_mensaje_interactivo(txt, chat_id=chat_id)
    elif text_strip == "/boost" or text_strip == "/impulsar":
        await manejar_sinergia_boost(chat_id)
    elif text_strip == "/generar_salud":
        await manejar_generar_post(chat_id, "salud", solo_texto=False)
    elif text_strip == "/generar_negocio":
        await manejar_generar_post(chat_id, "negocio", solo_texto=False)
    elif text_strip == "/texto_salud":
        await manejar_generar_post(chat_id, "salud", solo_texto=True)
    elif text_strip == "/texto_negocio":
        await manejar_generar_post(chat_id, "negocio", solo_texto=True)
    elif text_strip == "/cola" and perfil.get("rol") == "admin":
        contenido = cargar_json()
        pendientes = [p for p in contenido if p.get("estado") == "aprobado" and not p.get("fecha_publicacion")]
        if not pendientes:
            await notifications.enviar_alerta("📋 <b>COLA VACÍA:</b> No tienes publicaciones agendadas para el futuro.", chat_id=chat_id)
        else:
            txt = "📋 <b>COLA DE PUBLICACIONES AGENDADAS:</b>\n\n"
            for idx, p in enumerate(pendientes):
                txt += f"{idx+1}. <code>{p['id']}</code> - Categoría: <b>{p.get('categoria_imagen')}</b> (Programado)\n"
            await notifications.enviar_alerta(txt, chat_id=chat_id)
    elif text_strip == "/debug_assets" and perfil.get("rol") == "admin":
        import os
        carpeta = "assets_oficiales"
        if not os.path.exists(carpeta):
            await notifications.enviar_alerta("❌ La carpeta <code>assets_oficiales</code> NO existe en el servidor.", chat_id=chat_id)
            return
        archivos = os.listdir(carpeta)
        if not archivos:
            await notifications.enviar_alerta("📁 La carpeta <code>assets_oficiales</code> está VACÍA en el servidor.", chat_id=chat_id)
            return
        
        msg_debug = f"📁 <b>CONTENIDO DE assets_oficiales ({len(archivos)} archivos):</b>\n\n"
        fotos_grandes = []
        for f in archivos[:30]:
            ruta_temp = os.path.join(carpeta, f)
            size = os.path.getsize(ruta_temp)
            msg_debug += f"• {f} ({size // 1024} KB)\n"
            if f.lower().endswith(('.jpg', '.png', '.jpeg')) and size >= 200000:
                fotos_grandes.append(f)
                
        msg_debug += f"\n👉 <b>Fotos grandes (&gt;= 200KB) encontradas:</b> {len(fotos_grandes)}"
        if len(archivos) > 30:
            msg_debug += f"\n<i>...y {len(archivos) - 30} archivos más.</i>"
        await notifications.enviar_alerta(msg_debug, chat_id=chat_id)
    elif text_strip == "/cancelar":
        USER_STATES[chat_id] = None
        await notifications.enviar_alerta("👍 Flujo cancelado. Volvemos al inicio.", chat_id=chat_id)
    else:
        await notifications.enviar_alerta(
            "🤖 <b>Sinergia Guardián:</b> No entendí ese comando. Escribe <code>/start</code> para abrir el panel de control interactivo de tu bot.",
            chat_id=chat_id
        )

async def descargar_foto_telegram(file_id, destino_local):
    """Descarga una foto de los servidores de Telegram de forma asíncrona."""
    url_file_info = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getFile?file_id={file_id}"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url_file_info) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    file_path = data.get("result", {}).get("file_path")
                    if file_path:
                        url_download = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_path}"
                        async with session.get(url_download) as file_resp:
                            if file_resp.status == 200:
                                os.makedirs(os.path.dirname(destino_local), exist_ok=True)
                                with open(destino_local, "wb") as f:
                                    f.write(await file_resp.read())
                                return True
        except Exception as e:
            print(f"Error descargando foto de Telegram: {e}")
    return False

async def manejar_foto_recibida(chat_id, photos):
    """Procesa una foto subida por el usuario para branding y copy personalizado con IA."""
    photo = photos[-1]
    file_id = photo["file_id"]
    
    hoy = datetime.now().strftime("%Y%m%d%H%M%S")
    destino = os.path.join("imagenes", "personalizadas", f"custom_{chat_id}_{hoy}.jpg")
    
    await notifications.enviar_alerta("📥 <b>Procesando tu imagen...</b>\nDescargando archivo en alta definición desde los servidores de Telegram...", chat_id=chat_id)
    
    exito = await descargar_foto_telegram(file_id, destino)
    if exito:
        USER_STATES[chat_id] = {
            "state": "ESPERANDO_PROMPT_CUSTOM",
            "ruta_imagen": destino
        }
        
        mensaje = (
            "📸 <b>¡FOTO RECIBIDA Y PROCESADA CON ÉXITO!</b>\n\n"
            "Ya tengo tu foto guardada. Ahora, por favor dime:\n"
            "👉 <b>¿Qué tema, beneficio o enfoque te gustaría que tenga el texto de esta publicación?</b>\n\n"
            "<i>Escribe tu prompt o instrucción personalizada detallada (ej: 'Habla de los beneficios del café de Ganoderma para tener energía matutina').\n"
            "O escribe /omitir para que la IA genere un copy general de forma automática.</i>"
        )
        await notifications.enviar_alerta(mensaje, chat_id=chat_id)
    else:
        await notifications.enviar_alerta("❌ <b>ERROR:</b> No se pudo descargar tu imagen. Por favor inténtalo de nuevo.", chat_id=chat_id)

async def auto_exchange_facebook_token():
    app_id = os.getenv("FACEBOOK_APP_ID")
    app_secret = os.getenv("FACEBOOK_APP_SECRET")
    short_token = os.getenv("FACEBOOK_SHORT_TOKEN")
    
    if not (app_id and app_secret and short_token):
        return
        
    print(">> [Meta Auto-Exchanger] Detectadas credenciales de intercambio. Iniciando...")
    try:
        # 1. Obtener token de larga duración del usuario
        url = f"https://graph.facebook.com/v20.0/oauth/access_token?grant_type=fb_exchange_token&client_id={app_id}&client_secret={app_secret}&fb_exchange_token={short_token}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                res_data = await response.json()
                if response.status != 200:
                    print(f">> [Meta Auto-Exchanger] Error obteniendo long token: {res_data}")
                    return
                long_token = res_data.get("access_token")
                
                # 2. Obtener lista de páginas
                pages_url = f"https://graph.facebook.com/v20.0/me/accounts?access_token={long_token}"
                async with session.get(pages_url) as pages_response:
                    pages_data = await pages_response.json()
                    if pages_response.status != 200:
                        print(f">> [Meta Auto-Exchanger] Error obteniendo páginas: {pages_data}")
                        return
                    
                    pages_list = pages_data.get("data", [])
                    if not pages_list:
                        print(">> [Meta Auto-Exchanger] No se encontraron páginas asociadas a este token.")
                        return
                        
                    # Buscar la página "Gano Excel"
                    target_page = None
                    for page in pages_list:
                        if "gano excel" in page.get("name", "").lower():
                            target_page = page
                            break
                            
                    if not target_page:
                        # Fallback a la primera página si no encuentra "Gano Excel"
                        target_page = pages_list[0]
                        print(f">> [Meta Auto-Exchanger] No se encontró 'Gano Excel'. Usando primera página disponible: {target_page.get('name')}")
                    
                    page_name = target_page.get("name")
                    page_id = target_page.get("id")
                    page_access_token = target_page.get("access_token")
                    
                    print(f">> [Meta Auto-Exchanger] ¡Éxito! Página vinculada: {page_name} (ID: {page_id})")
                    
                    # 3. Actualizar archivo .env local/servidor
                    env_path = ".env"
                    env_lines = []
                    if os.path.exists(env_path):
                        with open(env_path, "r", encoding="utf-8") as f:
                            env_lines = f.readlines()
                            
                    new_lines = []
                    keys_to_update = {
                        "FACEBOOK_PAGE_ID": page_id,
                        "FACEBOOK_ACCESS_TOKEN": page_access_token
                    }
                    keys_seen = set()
                    
                    for line in env_lines:
                        # Ignorar el short token viejo para limpiar
                        if line.startswith("FACEBOOK_SHORT_TOKEN") or line.startswith("FACEBOOK_APP_ID") or line.startswith("FACEBOOK_APP_SECRET"):
                            continue
                        
                        matched = False
                        for key in keys_to_update:
                            if line.startswith(f"{key}="):
                                new_lines.append(f"{key}={keys_to_update[key]}\n")
                                keys_seen.add(key)
                                matched = True
                                break
                        if not matched:
                            new_lines.append(line)
                            
                    for key in keys_to_update:
                        if key not in keys_seen:
                            new_lines.append(f"{key}={keys_to_update[key]}\n")
                            
                    with open(env_path, "w", encoding="utf-8") as f:
                        f.writelines(new_lines)
                        
                    # 4. Actualizar afiliados.json para Jorge
                    afiliados = cargar_afiliados()
                    admin_chat_id = os.getenv("TELEGRAM_CHAT_ID")
                    if str(admin_chat_id) in afiliados:
                        afiliados[str(admin_chat_id)]["facebook_page_id"] = page_id
                        afiliados[str(admin_chat_id)]["facebook_access_token"] = page_access_token
                        guardar_afiliados(afiliados)
                        
                    # Recargar variables de entorno locales
                    os.environ["FACEBOOK_PAGE_ID"] = page_id
                    os.environ["FACEBOOK_ACCESS_TOKEN"] = page_access_token
                        
                    # 5. Enviar mensaje de victoria en Telegram
                    await notifications.enviar_alerta(
                        f"⚡️ <b>CONFIGURACIÓN EXITOSA (API MÁSTER):</b>\n\n"
                        f"He enlazado la API oficial de Facebook directamente con tu FanPage: <b>{page_name}</b> (ID: <code>{page_id}</code>).\n\n"
                        f"👉 <i>A partir de ahora, todas tus publicaciones automáticas se harán en menos de 1 segundo sin necesidad de abrir Playwright. ¡Es 100% robusto y no expira jamás!</i> 🚀",
                        chat_id=admin_chat_id
                    )
                    
    except Exception as e:
        print(f">> [Meta Auto-Exchanger] Excepción crítica: {e}")

async def bucle_escucha_telegram():
    if not TELEGRAM_TOKEN:
        print(">> [Telegram Engine] Error crucial: Falta TELEGRAM_TOKEN en el .env")
        return
        
    try:
        await auto_exchange_facebook_token()
    except Exception as e_exch:
        print(f"Error en auto_exchange_facebook_token: {e_exch}")

        
    print("==================================================")
    print("   INICIANDO MÓDULO INTERACTIVO DE TELEGRAM       ")
    print("==================================================")
    print(">> Buscando actualizaciones en tiempo real...")
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
    offset = 0
    
    try:
        await enviar_menu_inicio(TELEGRAM_CHAT_ID)
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
                                chat = msg.get("chat", {})
                                chat_id = str(chat.get("id"))
                                
                                if "photo" in msg:
                                    await manejar_foto_recibida(chat_id, msg["photo"])
                                elif "text" in msg:
                                    await manejar_mensaje_texto(chat_id, msg["text"], msg.get("from", {}))
                                    
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
