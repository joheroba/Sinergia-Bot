import asyncio
import json
import os
import random
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
LOGO_PATH = "imagenes/logo_autorizado.png"

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
        # Los selectores de Meta cambian frecuentemente. Buscamos por texto y roles comunes.
        selectors = [
            'div[role="button"]:has-text("WhatsApp")',
            'div[aria-label="Recibir mensajes de WhatsApp"]',
            'i[style*="background-image"][class*="whatsapp"]' # Icono de WhatsApp
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

async def publicar_en_meta(context, post):
    page = await context.new_page()
    whatsapp_phone = os.getenv("WHATSAPP_PHONE", "tu-numero")
    
    # Generar texto con IA si está vacío
    if not post.get("texto") or post.get("texto") == "":
        print(f">> [IA] Generando texto para {post['id']}...")
        post["texto"] = ai_agent.generar_copy_ia(post.get("id"), whatsapp_phone)

    await page.goto("https://business.facebook.com/latest/composer", wait_until="networkidle")
    
    if "login" in page.url:
        print(">> Esperando login manual en monitor web...")
        await notifications.enviar_alerta("⚠️ *ATENCIÓN:* Facebook solicita Login Manual en el Monitor Web. Por favor entra a Chrome y pon tu clave.")
        await page.wait_for_url("**/latest/composer**", timeout=0)

    try:
        # 1. Escribir texto
        caja_texto = page.locator('div[contenteditable="true"]').first
        await caja_texto.wait_for(state="visible", timeout=20000)
        await caja_texto.fill(post["texto"])
        
        # 2. Brandeo e Imagen
        ruta_original = None
        if "categoria_imagen" in post:
            ruta_original = obtener_media_rotativa(post["categoria_imagen"])
        
        if ruta_original:
            print(f">> [Brandeo] Procesando {ruta_original}...")
            ruta_branded = branding_tool.brandear_imagen(ruta_original, LOGO_PATH)
            
            async with page.expect_file_chooser() as fc_info:
                await page.locator('div[role="button"]:has-text("Agregar foto/video")').first.click()
            file_chooser = await fc_info.value
            await file_chooser.set_files(ruta_branded)
            await page.wait_for_timeout(5000)
            
            # 3. Intentar activar botón de WhatsApp CTA
            await activar_boton_whatsapp(page)

        # 4. Publicar
        btn_publicar = page.locator('div[aria-label="Publicar"], button:has-text("Publicar")').last
        await btn_publicar.click()
        print(f">> [OK] Publicación {post['id']} enviada con éxito.")
        await notifications.enviar_alerta(f"✅ *ÉXITO:* He publicado el producto `{post['id']}` con IA y Brandeo. ¡Listos para recibir prospectos!")
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

    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            headless=False,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
        )
        
        for post in posts_pendientes:
            exito = await publicar_en_meta(context, post)
            if exito:
                post["fecha_publicacion"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                await guardar_contenido(contenido)
            await asyncio.sleep(10)
            
        await context.close()

if __name__ == "__main__":
    asyncio.run(main())
