import asyncio
import os
import random
from datetime import datetime
from dotenv import load_dotenv
from playwright.async_api import async_playwright
import notifications
import crm_local
import ai_agent
import database_manager

load_dotenv()

if os.name == "posix" and "DISPLAY" not in os.environ:
    os.environ["DISPLAY"] = ":99"

URL_TIENDA_GLOBAL = os.getenv("GANO_ITOUCH_STORE", "https://peru.ganoitouch.biz/")

async def atender_afiliado(p, afiliado):
    afiliado_id = afiliado["id"]
    nombre_lider = afiliado["nombre"]
    telefono = afiliado["whatsapp"]
    
    wp_data_dir = f"./playwright_whatsapp_{afiliado_id}"
    print(f"[{nombre_lider}] Iniciando bot de WhatsApp para {telefono}...")
    
    is_headless = os.getenv("HEADLESS_MODE", "False").lower() == "true"
    user_agent_disfraz = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    
    context = await p.chromium.launch_persistent_context(
        user_data_dir=wp_data_dir,
        headless=is_headless,
        user_agent=user_agent_disfraz,
        viewport={"width": 1280, "height": 720},
        locale="es-ES",
        timezone_id="America/Lima",
        args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
    )
    page = context.pages[0] if context.pages else await context.new_page()

    await page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
    """)
    
    await page.goto("https://web.whatsapp.com/", wait_until="domcontentloaded", timeout=120000)
    
    print(f"[{nombre_lider}] Esperando autenticación...")
    
    try:
        # En modo multi-tenant dependemos del QR manual o sesión guardada
        print(f"[{nombre_lider}] Buscando panel de chats o código QR...")
        for i in range(120): # 6 minutos total
            try:
                if await page.locator('#pane-side').count() > 0:
                    print(f"[{nombre_lider}] [INFO] ¡CONEXIÓN EXITOSA! Entrando al panel de control...")
                    break
                await page.screenshot(path=f"qr_login_{afiliado_id}.png", timeout=3000)
            except: pass
            await asyncio.sleep(3)

        await page.wait_for_selector('#pane-side', timeout=360000)
        print(f"\\n[{nombre_lider}] [OK] !Sesion capturada con exito!")
        await notifications.enviar_alerta(f"[CONECTADO]: El Bot de {nombre_lider} esta ACTIVO.")
        if os.path.exists(f"qr_login_{afiliado_id}.png"): os.remove(f"qr_login_{afiliado_id}.png")
    except Exception as e:
        print(f"[{nombre_lider}] [X] No se pudo capturar la sesión: {str(e)}")
        await page.screenshot(path=f"error_autenticacion_{afiliado_id}.png")
        return

    print(f"[{nombre_lider}] Entra en MODO VIGÍA...")
    
    while True:
        try:
            chats_no_leidos_loc = page.locator('span[aria-label*="no leíd"], span[aria-label*="no leid"]')
            cantidad = await chats_no_leidos_loc.count()
            if cantidad > 0:
                print(f"[{nombre_lider} - {datetime.now().strftime('%H:%M:%S')}] [ALERTA] !Detectamos {cantidad} prospectos!")
                await chats_no_leidos_loc.first.click(force=True)
                await page.wait_for_timeout(2000)
                
                header_loc = page.locator('header span[dir="auto"]').first
                nombre_chat = await header_loc.inner_text() if await header_loc.count() > 0 else "Desconocido"
                
                ultimos_mensajes_loc = page.locator('div[class*="message-in"] span.selectable-text[dir="ltr"]')
                texto_recibido = ""
                media_base64 = None
                tipo_media = None
                
                if await ultimos_mensajes_loc.count() > 0:
                    texto_recibido = await ultimos_mensajes_loc.last.inner_text()
                else:
                    js_code = '''async () => {
                        let lastMsg = document.querySelectorAll('div[class*="message-in"]');
                        if(lastMsg.length > 0) {
                            let msg = lastMsg[lastMsg.length - 1];
                            let audio = msg.querySelector('audio');
                            if(audio && audio.src.startsWith('blob:')) {
                                let r = await fetch(audio.src); let b = await r.blob();
                                return await new Promise((res) => {
                                    let reader = new FileReader();
                                    reader.onloadend = () => res("audio|" + reader.result);
                                    reader.readAsDataURL(b);
                                });
                            }
                            let img = msg.querySelector('img[src^="blob:"]');
                            if(img) {
                                let r = await fetch(img.src); let b = await r.blob();
                                return await new Promise((res) => {
                                    let reader = new FileReader();
                                    reader.onloadend = () => res("image|" + reader.result);
                                    reader.readAsDataURL(b);
                                });
                            }
                            let textSpan = msg.querySelector('span.selectable-text, span.copyable-text');
                            if(textSpan && textSpan.innerText.trim() !== "") {
                                return "text|" + textSpan.innerText.trim();
                            }
                        }
                        return null;
                    }'''
                    media_resultado = await page.evaluate(js_code)
                    if media_resultado:
                        tipo, contenido = media_resultado.split("|", 1)
                        if tipo == "text":
                            texto_recibido = contenido
                        else:
                            tipo_media = tipo
                            media_base64 = contenido
                            texto_recibido = f"[{tipo.upper()} RECIBIDO]"

                print(f"[{nombre_lider}] DEBUG: texto_recibido='{texto_recibido}', media_base64={'Yes' if media_base64 else 'No'}")

                if texto_recibido or media_base64:
                    texto_limpio = str(texto_recibido).strip().lower()
                    
                    teclado_wa = page.locator('div[title="Escribe un mensaje"], div[contenteditable="true"][role="textbox"]').last
                    is_visible = await teclado_wa.is_visible()
                    print(f"[{nombre_lider}] DEBUG: teclado visible? {is_visible}")
                    if is_visible:
                        print(f"[{nombre_lider}] => [IA] Pensando respuesta para {nombre_chat}...")
                        respuesta_inyeccion = ai_agent.conversar_prospecto_ia(
                            mensaje_nuevo=texto_recibido, 
                            link_tienda=URL_TIENDA_GLOBAL, 
                            whatsapp=telefono,
                            media_b64=media_base64,
                            tipo_media=tipo_media
                        )
                        
                        if "[IGNORAR]" in respuesta_inyeccion:
                            print(f"[{nombre_lider}] => [IA] Mensaje ignorado por filtro de SPAM.")
                            await page.keyboard.press('Escape')
                            continue

                        nivel_interes = ai_agent.calificar_prospecto(texto_recibido)
                        crm_local.registrar_lead(nombre_chat, texto_recibido, nivel_interes)
                        
                        if "CIERRE LISTO" in respuesta_inyeccion or "DNI" in texto_limpio:
                            await notifications.enviar_alerta(f"[POSIBLE CIERRE ({nombre_lider})]: {nombre_chat} esta enviando datos.")
                        elif nivel_interes == "Alto":
                            await notifications.enviar_alerta(f"[LEAD CALIENTE ({nombre_lider})]: {nombre_chat} interesado.")

                        enviar_yape = "[ENVIAR_QR_YAPE]" in respuesta_inyeccion
                        enviar_plin = "[ENVIAR_QR_PLIN]" in respuesta_inyeccion
                        
                        respuesta_inyeccion = respuesta_inyeccion.replace("[ENVIAR_QR_YAPE]", "").replace("[ENVIAR_QR_PLIN]", "").strip()

                        await teclado_wa.click()
                        await page.keyboard.insert_text(respuesta_inyeccion)
                        await page.wait_for_timeout(500)
                        await page.keyboard.press("Enter")
                        print(f"[{nombre_lider}] => [✓] Respuesta enviada a {nombre_chat}")
                        
                        if enviar_yape or enviar_plin:
                            print(f"[{nombre_lider}] => [!] Comando QR detectado. Adjuntando imagen...")
                            try:
                                img_path = f"c:\\\\GanoiTouch\\\\qrs\\\\user_{afiliado_id}\\\\yape.png" if enviar_yape else f"c:\\\\GanoiTouch\\\\qrs\\\\user_{afiliado_id}\\\\plin.png"
                                if os.path.exists(img_path):
                                    await page.wait_for_timeout(1000)
                                    await page.locator('div[title="Adjuntar"], span[data-icon="clip"]').click()
                                    await page.wait_for_timeout(1000)
                                    input_file = page.locator('input[accept="image/*,video/mp4,video/3gpp,video/quicktime"]')
                                    await input_file.set_input_files(img_path)
                                    btn_send = page.locator('span[data-icon="send"]')
                                    await btn_send.wait_for(timeout=10000)
                                    await page.wait_for_timeout(500)
                                    await btn_send.click()
                                    print(f"[{nombre_lider}] => [✓] ¡QR enviado exitosamente!")
                                else:
                                    print(f"[{nombre_lider}] => [X] Error: No se encontró la imagen en {img_path}")
                            except Exception as img_e:
                                print(f"[{nombre_lider}] => [X] Error al enviar imagen QR: {img_e}")
                                
        except Exception as loop_error:
             pass
        await page.wait_for_timeout(10000)

async def orquestador_principal():
    print("==================================================")
    print("  SINERGIA ORCHESTRATOR (MULTI-TENANT WHATSAPP)   ")
    print("==================================================")
    afiliados = database_manager.obtener_todos_activos()
    if not afiliados:
        print("[!] No hay afiliados activos en la base de datos.")
        return
        
    print(f">> Iniciando orquestador para {len(afiliados)} afiliados en paralelo...")
    async with async_playwright() as p:
        tareas = []
        for afiliado in afiliados:
            tareas.append(atender_afiliado(p, afiliado))
        
        # Ejecutar todos los bots en paralelo
        await asyncio.gather(*tareas)

if __name__ == "__main__":
    asyncio.run(orquestador_principal())
