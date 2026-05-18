import asyncio
import json
import os
import random
import aiohttp
from datetime import datetime
from dotenv import load_dotenv
from playwright.async_api import async_playwright

# Importar nuevos módulos de Sinergia Pro
import ai_agent
import branding_tool
import notifications

# Cargar variables de entorno
load_dotenv()

# Configuración automática de Display para servidores Linux sin monitor físico (noVNC)
if os.name == "posix" and "DISPLAY" not in os.environ:
    os.environ["DISPLAY"] = ":99"

JSON_PATH = "contenido_ganoderma.json"
USER_DATA_DIR = "./playwright_profile"
LOGO_PATH = "logo_distribuidor.png"

async def cargar_contenido():
    if not os.path.exists(JSON_PATH):
        return []
    with open(JSON_PATH, "r", encoding="utf-8") as file:
        return json.load(file)

async def guardar_contenido(data):
    with open(JSON_PATH, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

def obtener_media_rotativa(categoria):
    target_dir = os.path.join("imagenes", categoria)
    os.makedirs(target_dir, exist_ok=True)
    archivos = [f for f in os.listdir(target_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.mp4'))]
    if not archivos: return None
    
    hist_file = "historial_multimedia.json"
    historial = json.load(open(hist_file, "r")) if os.path.exists(hist_file) else {}
    archivo_elegido = min(archivos, key=lambda x: historial.get(f"{categoria}_{x}", 0))
    
    historial[f"{categoria}_{archivo_elegido}"] = historial.get(f"{categoria}_{archivo_elegido}", 0) + 1
    json.dump(historial, open(hist_file, "w"), indent=4)
    
    return os.path.join(target_dir, archivo_elegido)

async def activar_boton_whatsapp(page):
    """
    Intenta activar el botón de 'Recibir mensajes de WhatsApp' en el composer de Meta.
    """
    try:
        print(">> [Botón CTA] Buscando opción de WhatsApp...")
        selectors = [
            'div[role="button"]:has-text("WhatsApp")',
            'div[aria-label="Recibir mensajes de WhatsApp"]',
            'i[style*="background-image"][class*="whatsapp"]'
        ]
        
        for sel in selectors:
            btn = page.locator(sel).first
            if await btn.is_visible():
                await btn.click()
                print(">> [OK] Botón de WhatsApp activado.")
                await page.wait_for_timeout(2000)
                return True
        
        print(">> [INFO] No se encontró el botón de WhatsApp (¿Página no vinculada?)")
        return False
    except Exception as e:
        print(f">> [Botón CTA] Error u omisión: {e}")
        return False

async def publicar_en_facebook_api(page_id, access_token, texto, ruta_imagen=None):
    """
    Publica en Facebook de forma oficial y ultra-rápida usando la API de Graph de Meta (SaaS).
    """
    if ruta_imagen and os.path.exists(ruta_imagen):
        url = f"https://graph.facebook.com/v18.0/{page_id}/photos"
        data = aiohttp.FormData()
        data.add_field("caption", texto)
        data.add_field("access_token", access_token)
        with open(ruta_imagen, "rb") as f:
            data.add_field("source", f, filename=os.path.basename(ruta_imagen))
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, data=data) as response:
                        res_json = await response.json()
                        if response.status == 200 and "id" in res_json:
                            print(f">> [Meta API] Post con foto publicado exitosamente: {res_json['id']}")
                            return True
                        else:
                            print(f">> [Meta API] Error: {res_json}")
            except Exception as e:
                print(f">> [Meta API] Error de conexión: {e}")
    else:
        url = f"https://graph.facebook.com/v18.0/{page_id}/feed"
        payload = {
            "message": texto,
            "access_token": access_token
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    res_json = await response.json()
                    if response.status == 200 and "id" in res_json:
                        print(f">> [Meta API] Post de texto publicado exitosamente: {res_json['id']}")
                        return True
                    else:
                        print(f">> [Meta API] Error: {res_json}")
        except Exception as e:
            print(f">> [Meta API] Error de conexión: {e}")
            
    return False

async def publicar_en_meta(context, post):
    page = await context.new_page()
    whatsapp_phone = os.getenv("WHATSAPP_PHONE", "tu-numero")
    
    if not post.get("texto") or post.get("texto") == "":
        print(f">> [IA] Generando texto para {post['id']}...")
        post["texto"] = ai_agent.generar_copy_ia(post.get("id"), whatsapp_phone)

    # Detectar si hay un ID de página específico en las variables de entorno
    page_id = os.getenv("FACEBOOK_PAGE_ID")
    if page_id:
        url = f"https://business.facebook.com/latest/composer?asset_id={page_id}"
        print(f">> [Navegador] Abriendo creador de publicaciones para la FanPage con ID: {page_id}")
    else:
        url = "https://business.facebook.com/latest/composer"
        print(">> [Navegador] Abriendo creador de publicaciones por defecto (sin FACEBOOK_PAGE_ID).")

    await page.goto(url, wait_until="networkidle")
    
    if "login" in page.url:
        print(">> Esperando login manual en monitor web...")
        await notifications.enviar_alerta("⚠️ *ATENCIÓN:* Facebook solicita Login Manual en el Monitor Web. Por favor entra a Chrome y pon tu clave.", chat_id=post.get("chat_id"))
        await page.wait_for_url("**/latest/composer**", timeout=0)

    try:
        # 1. Esperar a que el creador cargue por completo (el cuadro de texto editable)
        caja_texto = page.locator('div[contenteditable="true"]').first
        await caja_texto.wait_for(state="visible", timeout=30000)

        # A. Descartar carteles de tutoría/onboarding (como el botón "Listo" de color morado)
        try:
            for selector in ['button:has-text("Listo")', 'div[role="button"]:has-text("Listo")', 'button:has-text("Entendido")', 'div[role="button"]:has-text("Entendido")']:
                btn = page.locator(selector).first
                if await btn.is_visible():
                    await btn.click()
                    print(">> [Meta UI] Cartel informativo descartado.")
                    await page.wait_for_timeout(1500)
        except Exception as e_pop:
            print(f">> [Meta UI] Omitiendo descarte de cartel: {e_pop}")

        # B. Forzar destino exacto (Gano Excel) en el selector "Publicar en"
        try:
            print(">> [Destino Facebook] Configurando página Gano Excel...")
            # Click en dropdown de "Publicar en"
            dropdown_selectors = [
                'div[role="button"]:has-text("Publicar en")',
                'div:has-text("Publicar en") > div[role="button"]',
                'div[role="combobox"]:has-text("Publicar en")'
            ]
            dropdown_found = False
            for sel in dropdown_selectors:
                dropdown = page.locator(sel).first
                if await dropdown.is_visible():
                    await dropdown.click()
                    dropdown_found = True
                    print(">> [Destino Facebook] Dropdown abierto.")
                    break
            
            if dropdown_found:
                await page.wait_for_timeout(2000)
                
                # Buscar y marcar "Gano Excel"
                gano_item = page.locator('div[role="checkbox"]:has-text("Gano Excel"), span:has-text("Gano Excel")').first
                if await gano_item.is_visible():
                    checkbox_gano = page.locator('div[role="checkbox"]:has-text("Gano Excel")').first
                    if await checkbox_gano.is_visible():
                        checked = await checkbox_gano.get_attribute("aria-checked")
                        if checked != "true":
                            await checkbox_gano.click()
                            print(">> [Destino Facebook] Marcado Gano Excel.")
                    else:
                        await gano_item.click()
                        print(">> [Destino Facebook] Clic Gano Excel.")
                
                # Buscar y desmarcar "Viajes y aventura"
                viajes_item = page.locator('div[role="checkbox"]:has-text("Viajes y aventura"), span:has-text("Viajes y aventura")').first
                if await viajes_item.is_visible():
                    checkbox_viajes = page.locator('div[role="checkbox"]:has-text("Viajes y aventura")').first
                    if await checkbox_viajes.is_visible():
                        checked = await checkbox_viajes.get_attribute("aria-checked")
                        if checked == "true":
                            await checkbox_viajes.click()
                            print(">> [Destino Facebook] Desmarcado Viajes y aventura.")
                
                # Cerrar dropdown
                for sel in dropdown_selectors:
                    dropdown = page.locator(sel).first
                    if await dropdown.is_visible():
                        await dropdown.click()
                        break
                await page.wait_for_timeout(1000)
        except Exception as e_dest:
            print(f">> [Destino Facebook] Error forzando destino (se usará el predeterminado): {e_dest}")

        # 2. Escribir texto
        await caja_texto.fill(post["texto"])
        
        # 2. Brandeo e Imagen
        ruta_branded = None
        if not post.get("solo_texto", False):
            if post.get("ruta_imagen_local") and os.path.exists(post["ruta_imagen_local"]):
                ruta_branded = post["ruta_imagen_local"]
                print(f">> [Brandeo] Usando imagen específica del borrador: {ruta_branded}")
            elif "categoria_imagen" in post:
                ruta_original = obtener_media_rotativa(post["categoria_imagen"])
                if ruta_original:
                    print(f">> [Brandeo] Procesando imagen rotativa: {ruta_original}...")
                    ruta_branded = branding_tool.brandear_imagen(ruta_original, LOGO_PATH)
            
            if ruta_branded and os.path.exists(ruta_branded):
                async with page.expect_file_chooser() as fc_info:
                    await page.locator('div[role="button"]:has-text("Agregar foto/video")').first.click()
                file_chooser = await fc_info.value
                await file_chooser.set_files(ruta_branded)
                await page.wait_for_timeout(5000)
                
                # 3. Intentar activar botón de WhatsApp CTA
                await activar_boton_whatsapp(page)
            else:
                print(">> [Composer] Publicando en formato de SOLO TEXTO.")

        # 4. Publicar
        btn_publicar = page.locator('div[aria-label="Publicar"], button:has-text("Publicar")').last
        await btn_publicar.click()
        print(f">> [OK] Publicación {post['id']} enviada con éxito.")
        await notifications.enviar_alerta(f"✅ <b>ÉXITO AUTOMÁTICO:</b> He publicado tu post programado sobre <code>{post.get('categoria_imagen')}</code> directamente en tu FanPage.", chat_id=post.get("chat_id"))
        await page.wait_for_timeout(5000)
        return True

    except Exception as e:
        await page.screenshot(path=f"error_{post['id']}.png")
        print(f"Error en Meta: {e}")
        return False
    finally:
        await page.close()

async def main():
    print("--- SINERGIA BOT PRO: INICIANDO CICLO ---")
    contenido = await cargar_contenido()
    posts_pendientes = [p for p in contenido if p.get("estado") == "aprobado" and not p.get("fecha_publicacion")]
    
    if not posts_pendientes:
        print("No hay posts pendientes.")
        return

    # Cargar base de datos de afiliados
    afiliados = {}
    if os.path.exists("afiliados.json"):
        try:
            with open("afiliados.json", "r", encoding="utf-8") as f:
                afiliados = json.load(f)
        except Exception as e:
            print(f"Error cargando afiliados: {e}")

    # Separar los posts en los que usan API (Graph API) y los que usan Navegador (Playwright)
    posts_api = []
    posts_playwright = []

    for post in posts_pendientes:
        chat_id = post.get("chat_id")
        if not chat_id:
            chat_id = os.getenv("TELEGRAM_CHAT_ID")
            post["chat_id"] = chat_id
            
        perfil = afiliados.get(str(chat_id), {})
        page_id = perfil.get("facebook_page_id")
        access_token = perfil.get("facebook_access_token")
        
        # Verificar si cumple con la fecha de publicación (solo si es programado)
        fecha_prog_str = post.get("fecha_programada")
        if fecha_prog_str:
            try:
                fecha_prog = datetime.strptime(fecha_prog_str, "%Y-%m-%d %H:%M:%S")
                if datetime.now() < fecha_prog:
                    continue # Aún no es la hora
            except Exception as e:
                print(f"Error procesando fecha programada: {e}")
                
        if page_id and access_token:
            posts_api.append((post, page_id, access_token))
        elif perfil.get("rol") == "admin" or str(chat_id) == os.getenv("TELEGRAM_CHAT_ID"):
            env_page_id = os.getenv("FACEBOOK_PAGE_ID")
            env_access_token = os.getenv("FACEBOOK_ACCESS_TOKEN")
            if env_page_id and env_access_token:
                posts_api.append((post, env_page_id, env_access_token))
            else:
                posts_playwright.append(post)
        else:
            print(f">> [Ignorado] El post {post['id']} pertenece al afiliado {perfil.get('nombre', chat_id)} pero no tiene API configurada.")

    # 1. Procesar posts vía API Oficial de Meta (sin abrir navegador, ultra-veloz, en paralelo)
    async def publicar_api_y_actualizar(post, p_id, token):
        exito = await publicar_en_facebook_api(p_id, token, post["texto"], post.get("ruta_imagen_local"))
        if exito:
            post["fecha_publicacion"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            await notifications.enviar_alerta(
                f"✅ <b>ÉXITO AUTOMÁTICO (API):</b> He publicado tu post programado sobre <code>{post.get('categoria_imagen')}</code> directamente en tu FanPage.",
                chat_id=post["chat_id"]
            )
        else:
            await notifications.enviar_alerta(
                f"❌ <b>ALERTA DE ERROR (API):</b> No se pudo publicar tu post programado en tu FanPage. Revisa tu token de Facebook.",
                chat_id=post["chat_id"]
            )

    if posts_api:
        print(f">> [Meta API] Procesando {len(posts_api)} posts de afiliados vía API...")
        tareas = [publicar_api_y_actualizar(post, p_id, token) for post, p_id, token in posts_api]
        await asyncio.gather(*tareas)
        await guardar_contenido(contenido)

    # 2. Procesar posts de Jorge vía Playwright (navegador persistente)
    if posts_playwright:
        print(f">> [Playwright] Procesando {len(posts_playwright)} posts de Jorge Admin vía Navegador...")
        async with async_playwright() as p:
            context = await p.chromium.launch_persistent_context(
                user_data_dir=USER_DATA_DIR,
                headless=False,
                args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
            )
            for post in posts_playwright:
                exito = await publicar_en_meta(context, post)
                if exito:
                    post["fecha_publicacion"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    await guardar_contenido(contenido)
                await asyncio.sleep(10)
            await context.close()

if __name__ == "__main__":
    asyncio.run(main())
