import asyncio
import os
import random
from datetime import datetime
from dotenv import load_dotenv
from playwright.async_api import async_playwright
import notifications
import crm_local
import ai_agent

load_dotenv()

# Configuración automática de Display para servidores Linux sin monitor físico (noVNC)
if os.name == "posix" and "DISPLAY" not in os.environ:
    os.environ["DISPLAY"] = ":99"

# Carpeta de cookies independiente para que tu Facebook siga funcionando tranquilo
# en su propia dimensión, y WhatsApp se aloje pacíficamente aquí.
WP_DATA_DIR = "./playwright_whatsapp"
URL_TIENDA = os.getenv("GANO_ITOUCH_STORE", "https://peru.ganoitouch.biz/")
LIDER_NAME = os.getenv("FACEBOOK_PAGE_NAME", "Johero")

MENSAJE_BIENVENIDA = f"""*🤖 ¡Hola! Soy el asistente virtual oficial de {LIDER_NAME} (Gano iTouch).* ☕🍄

Tu bienestar es nuestra prioridad. Por favor envíame únicamente *el número* de lo que buscas para poder guiarte velozmente:

1️⃣. *Comprar Productos* (Café Ganoderma, Espirulina, etc.)
2️⃣. *Oportunidad de Afiliación* (Generar Ingresos con Nosotros)
3️⃣. *Agendar una Cita Contigo*
4️⃣. *¿Para qué sirven los productos?* (Dudas de Salud)
5️⃣. *¿Qué es una Red de Mercadeo / Duplicación?* (Dudas de Negocio)

_(Si no respondo de inmediato, ten un poquito de paciencia, estoy atendiendo a varios prospectos)_."""

MENSAJE_COMPRA = f"""*🛒 INSTRUCCIONES PARA TU PEDIDO SEGURO:*

1. Dale click aquí para ir a mi Tienda Oficial:
👉 {URL_TIENDA}
2. Arriba a la derecha presiona en *"Iniciar sesión o crear una cuenta"*. (¡Es obligatorio para proteger tus datos de envío!)
3. Llena tus datos, elige tus productos favoritos de Gano Excel y ve a tu carrito.
4. Escoge tu dirección o elige *"Recojo en Sede Central"* (Av. Angamos Oeste).
5. Podrás pagar de forma segura. ¡Envíame una fotito/captura por este chat cuando termines para darle seguimiento prioritario!"""

MENSAJE_AFILIACION = f"""*🤝 ¡BIENVENIDO A LAS LIGAS MAYORES!*

Construir un negocio heredable apoyado en Gano Excel es la mejor decisión que puedes tomar. Al afiliarte adquieres tus productos a precio de distribuidor y puedes formar tu propio imperio.

Pasos para unirte a nuestro árbol de distribuidores:
1. Entra al mismo enlace y sigue el protocolo de Creación de Cuenta (Elige un kit de prosperidad):
👉 {URL_TIENDA}
2. Si prefieres hacerlo juntos por Zoom o llamada para explicarte los bonos, envíame la palabra clave: *CITA*"""

MENSAJE_CITA = f"""*📅 AGENDAMIENTO DIRECTO*

Perfecto. Por favor, déjame en un solo mensaje:
- *Tu Nombre Completo*
- *Día y hora de preferencia para llamarte*

Anotaré esto y me comunicaré personalmente contigo a la brevedad. ¡Fuerte abrazo!"""

MENSAJE_FAQ_PRODUCTO = """*🍄 EL PODER DEL GANODERMA*

Nuestros productos no son simples cafés o chocolates. Son "Súper Alimentos" enriquecidos con el extracto hidrosoluble de *Ganoderma Lucidum*, el hongo asiático más premiado del mundo.

¿Sus beneficios comprobados?
🔋 *Eleva tu Energía Mantenida:* Sin el choque de la cafeína tradicional.
🛡️ *Refuerza Escudos:* Altísimos antioxidantes para tu sistema inmunológico.
🧠 *Claridad Mental:* Apoyo a la oxigenación celular (PIOIR, Espirulina, Classic).

Para ver todo el catálogo online, marca *1*."""

MENSAJE_FAQ_NEGOCIO = """*📈 EL PODER DE LA DUPLICACIÓN (Gano iTouch)*

En el Network Marketing no vendes puerta a puerta; eres un *Constructor de Franquicias* de un gigante malayo con 100% capital propio y presencia en más de 75 países.

Las ventajas de nuestro Plan de Compensación (12 Formas de Ganar) son colosales:

1️⃣ *Bonos de Inicio Rápido (Gen 5):* Puedes generar picos de hasta $2,140 dólares al duplicar tu base con socios bajo el formato *ESP 3*.
2️⃣ *Bono Binario por Compensación:* Te pagamos un asombroso *17%* de comisiones residuales igualadas cada vez que tus ramas izquierda y derecha consumen o se afilian.
3️⃣ *Inversión Flexible:* Tú eliges cómo entrar: Paquete Básico (50 PV) o los rentables ESP 1, 2 y 3.

Para unirte a nuestra red oficial y posicionarte, marca *2*."""

MENSAJE_ERROR = "⚠️ No logré entender. Por favor envíame solamente un número: *1, 2, 3, 4 o 5*."


async def atender_prospectos():
    print("==================================================")
    print("      SINERGIA SALES BOT (WHATSAPP CANALIZADO)    ")
    print("==================================================")
    async with async_playwright() as p:
        # Leemos si queremos ver el navegador (False) o no (True) desde el .env
        is_headless = os.getenv("HEADLESS_MODE", "False").lower() == "true"
        
        # --- CONFIGURACIÓN "MONITOR DE MENTIRA" (Xvfb) ---
        user_agent_disfraz = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        
        context = await p.chromium.launch_persistent_context(
            user_data_dir=WP_DATA_DIR,
            headless=False, # ¡Forzado a False para que trabaje sobre Xvfb!
            user_agent=user_agent_disfraz,
            viewport={"width": 1280, "height": 720}, # Tamaño estándar para que el QR sea visible
            locale="es-ES",
            timezone_id="America/Lima",
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox"
            ]
        )
        page = context.pages[0] if context.pages else await context.new_page()

        # Inyección de ADN Humano: Borramos rastros de automatización dinámicamente
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
        print(">> Entrando a WhatsApp Web...")
        await page.goto("https://web.whatsapp.com/", wait_until="domcontentloaded", timeout=120000)
        
        print(">> Esperando autenticación. (¡Si te pide escanear el Código QR, saca tu celular y hazlo ahora!)")
        
        try:
             # --- SISTEMA DE VINCULACIÓN POR CÓDIGO (NÚMERO DE TELÉFONO) ---
             phone_number = os.getenv("WHATSAPP_PHONE")
             if phone_number:
                 phone_number = phone_number.replace(" ", "").replace("-", "")
                 print(f">> [PASO 1] Iniciando vinculación por número: {phone_number}")
                 try:
                     # Hacer clic en "Iniciar sesión con número de teléfono"
                     btn_phone = page.locator('span:has-text("Iniciar sesión con número de teléfono"), [role="button"]:has-text("Inici")')
                     await btn_phone.first.wait_for(timeout=60000) # 60 segundos de paciencia extrema
                     await btn_phone.first.click()
                     
                     # Ingresar el número
                     print(">> [PASO 3] Esperando casilla de número...")
                     input_phone = page.locator('input[dir="ltr"], input[aria-label*="número de teléfono"]')
                     await input_phone.wait_for(timeout=60000)
                     await input_phone.fill(phone_number)
                     
                     print(f">> [PASO 3] Número {phone_number} ingresado. Presionando 'Siguiente'...")
                     btn_next = page.locator('button:has-text("Siguiente"), [role="button"]:has-text("Siguiente")')
                     await btn_next.wait_for(timeout=20000)
                     await btn_next.click()

                     # Esperar a que aparezca el código
                     print(">> [PASO 4] Generando código de 8 dígitos...")
                     code_container = page.locator('div[data-link-code]')
                     await code_container.wait_for(timeout=60000) 
                     
                     await page.screenshot(path="qr_login.png")
                     
                     pairing_code = await code_container.inner_text()
                     print("\n" + "!"*45)
                     print(f"  TU CÓDIGO DE VINCULACIÓN ES: {pairing_code}")
                     print("!"*45)
                     print(">> [PASO 5] Código listo. Ingrésalo en tu celular.")
                     
                 except Exception as e:
                     print(f">> [!] Error en flujo de número: {e}. Intentando QR normal...")
                     await page.screenshot(path="error_vinculacion.png") 

             # --- SISTEMA DE CAPTURA DE QR (BACKUP) ---
             print(">> Buscando panel de chats o código QR...")
             for i in range(120): # 6 minutos total
                 try:
                    if await page.locator('#pane-side').count() > 0:
                        print(">> [INFO] ¡CONEXIÓN EXITOSA! Entrando al panel de control...")
                        break
                    await page.screenshot(path="qr_login.png", timeout=3000)
                 except: pass
                 await asyncio.sleep(3)

             await page.wait_for_selector('#pane-side', timeout=360000)
             print("\n>> [✓] ¡Sesión capturada con éxito!")
             await notifications.enviar_alerta("🟢 *CONECTADO:* El Bot de WhatsApp de Sinergia está ACTIVO y atendiendo prospectos en el servidor.")
             if os.path.exists("qr_login.png"): os.remove("qr_login.png")
        except Exception as e:
             print(f">> [X] No se pudo capturar la sesión: {str(e)}")
             await page.screenshot(path="error_autenticacion.png")
             return

        print(">> El sistema de Inbound Marketing entra en MODO VIGÍA...")
        memoria_prospectos = {}

        while True:
            try:
                chats_no_leidos_loc = page.locator('span[aria-label*="no leíd"], span[aria-label*="no leid"]')
                cantidad = await chats_no_leidos_loc.count()
                if cantidad > 0:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🚨 ¡Detectamos {cantidad} prospectos!")
                    await chats_no_leidos_loc.first.click(force=True)
                    await page.wait_for_timeout(2000)
                    
                    header_loc = page.locator('header span[dir="auto"]').first
                    nombre_chat = await header_loc.inner_text() if await header_loc.count() > 0 else "Desconocido"
                    
                    ultimos_mensajes_loc = page.locator('div[class*="message-in"] span.selectable-text[dir="ltr"]')
                    if await ultimos_mensajes_loc.count() > 0:
                        texto_recibido = await ultimos_mensajes_loc.last.inner_text()
                        texto_limpio = str(texto_recibido).strip().lower()
                        
                        teclado_wa = page.locator('div[title="Escribe un mensaje"], div[contenteditable="true"][role="textbox"]').last
                        if await teclado_wa.is_visible():
                            respuesta_inyeccion = ""
                            if texto_limpio in ["1", "uno", "comprar", "productos"]:
                                respuesta_inyeccion = MENSAJE_COMPRA
                            elif texto_limpio in ["2", "dos", "afiliarse", "negocio"]:
                                respuesta_inyeccion = MENSAJE_AFILIACION
                            elif texto_limpio in ["3", "tres", "cita", "agendar"]:
                                respuesta_inyeccion = MENSAJE_CITA
                            elif texto_limpio in ["4", "cuatro", "salud"]:
                                respuesta_inyeccion = MENSAJE_FAQ_PRODUCTO
                            elif texto_limpio in ["5", "cinco", "duplicacion"]:
                                respuesta_inyeccion = MENSAJE_FAQ_NEGOCIO
                            else:
                                if nombre_chat not in memoria_prospectos:
                                    respuesta_inyeccion = MENSAJE_BIENVENIDA
                                    memoria_prospectos[nombre_chat] = True
                                else:
                                    respuesta_inyeccion = MENSAJE_ERROR
                            
                            # --- NUEVA LÓGICA CRM FASE A ---
                            print(f"   => [CRM] Procesando lead: {nombre_chat}")
                            nivel_interes = ai_agent.calificar_prospecto(texto_recibido)
                            crm_local.registrar_lead(nombre_chat, texto_recibido, nivel_interes)
                            
                            if nivel_interes == "Alto":
                                await notifications.enviar_alerta(f"🔥 *LEAD CALIENTE:* {nombre_chat} está muy interesado. \n\nMensaje: _{texto_recibido}_")

                            await teclado_wa.click()
                            await page.keyboard.insert_text(respuesta_inyeccion)
                            await page.wait_for_timeout(500)
                            await page.keyboard.press("Enter")
                            print(f"   => [✓] Respuesta enviada a {nombre_chat}")
            except Exception as loop_error:
                 pass
            await page.wait_for_timeout(10000)

if __name__ == "__main__":
    asyncio.run(atender_prospectos())
