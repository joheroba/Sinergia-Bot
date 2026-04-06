import asyncio
import os
import random
from datetime import datetime
from dotenv import load_dotenv
from playwright.async_api import async_playwright

load_dotenv()

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
    print("Iniciando motor Playwright en modo visible. WhatsApp Web tomará control.\n")
    
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=WP_DATA_DIR,
            headless=False, # Obligatoriamente visible para que vincules con QR si es cuenta nueva
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = context.pages[0] if context.pages else await context.new_page()
        
        print(">> Entrando a WhatsApp Web...")
        # Cambiado load por domcontentloaded para que arranque rapido en conexiones de Peru, y se eleva el timeout.
        await page.goto("https://web.whatsapp.com/", wait_until="domcontentloaded", timeout=120000)
        
        print(">> Esperando autenticación. (¡Si te pide escanear el Código QR, saca tu celular y hazlo ahora!)")
        
        # WhatsApp tarda en cargar una vez que pasas el QR. El panel de mensajes tiene la palabra "Chats" normalmente.
        try:
             # Selector dinámico universal: #pane-side es el bloque a la izquierda de todos los chats
             await page.wait_for_selector('#pane-side', timeout=300000) # 5 minutos para que escanees tranquilo
             print("\n>> [✓] ¡Sesión capturada con éxito! Las líneas telefónicas están vivas.")
        except:
             print(">> [X] Parece que tardaste mucho en escanear o el internet está lento. Vuelve a correr el script.")
             await context.close()
             return

        print(">> El sistema de Inbound Marketing entra en MODO VIGÍA...")
        print(">> (Revisaremos nuevos leads cada 15 segundos)")
        
        # Diccionario para "recordar" a quién le dimos bienvenida.
        # En una arquitectura masiva se guardaría en json, por ahora en RAM temporal sirve para una corrida.
        memoria_prospectos = {}

        # Loop infinito cuidando tu red. "Ctrl+C" en la terminal apagará todo.
        while True:
            try:
                # 1. Detectar banderas de no leídos. WhatsApp usa span elements con 'label' o texto plano con numeros enteros.
                # Esta tactica busca el nodo que alberga el título del chat y da clicks a los [!No leidos].
                # Usaremos xpath que agarra el boton de chat si contiene un "span" con atributo aria-label que dice 'no leíd'
                chats_no_leidos_loc = page.locator('span[aria-label*="no leíd"], span[aria-label*="no leid"]')
                
                cantidad = await chats_no_leidos_loc.count()
                if cantidad > 0:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🚨 ¡Detectamos {cantidad} prospectos exigiendo respuesta!")
                    
                    # Vamos a entrar al PRIMER chat no leído (por FIFO inverso o LIFO)
                    await chats_no_leidos_loc.first.click(force=True)
                    await page.wait_for_timeout(2000) # Dejar que cargue el hilo 
                    
                    # 2. Extraer el contexto (Nombre u Origen de quien nos habla)
                    # El nombre suele estar arriba en el encabezado
                    header_loc = page.locator('header span[dir="auto"]').first
                    nombre_chat = await header_loc.inner_text() if await header_loc.count() > 0 else "Desconocido"
                    
                    # 3. Leer el último mensaje recibido para ver si puso "1", "2" o es primerizo
                    ultimos_mensajes_loc = page.locator('div[class*="message-in"] span.selectable-text[dir="ltr"]')
                    if await ultimos_mensajes_loc.count() > 0:
                        texto_recibido = await ultimos_mensajes_loc.last.inner_text()
                        texto_limpio = str(texto_recibido).strip().lower()
                        print(f"   => [{nombre_chat}] Dijo: '{texto_limpio}'")
                        
                        teclado_wa = page.locator('div[contenteditable="true"][data-tab="10"]').first
                        if not await teclado_wa.is_visible():
                             # A veces WP cambia tab ids. Agarramos por rol genérico
                             teclado_wa = page.locator('div[title="Escribe un mensaje"], div[contenteditable="true"][role="textbox"]').last

                        if teclado_wa:
                            # Lógica Cerebro (State Machine básico)
                            respuesta_inyeccion = ""
                            if texto_limpio in ["1", "uno", "comprar", "productos"]:
                                respuesta_inyeccion = MENSAJE_COMPRA
                            elif texto_limpio in ["2", "dos", "afiliarse", "negocio", "información"]:
                                respuesta_inyeccion = MENSAJE_AFILIACION
                            elif texto_limpio in ["3", "tres", "cita", "agendar", "hablar"]:
                                respuesta_inyeccion = MENSAJE_CITA
                            elif texto_limpio in ["4", "cuatro", "salud", "ganoderma"]:
                                respuesta_inyeccion = MENSAJE_FAQ_PRODUCTO
                            elif texto_limpio in ["5", "cinco", "duplicacion", "red"]:
                                respuesta_inyeccion = MENSAJE_FAQ_NEGOCIO
                            else:
                                # Es un texto nuevo, probablemente un "Hola que tal info".
                                # Miremos la memoria.
                                if nombre_chat not in memoria_prospectos:
                                    respuesta_inyeccion = MENSAJE_BIENVENIDA
                                    memoria_prospectos[nombre_chat] = True
                                else:
                                    respuesta_inyeccion = MENSAJE_ERROR
                                
                            # Mecánica Inyección (Teclado) -> Usar insert_text simula paste a portapapeles y envía rápido sin errores multilínea
                            print("   => Canalizando el embudo con mensaje estructurado...")
                            await teclado_wa.click()
                            await page.wait_for_timeout(500)
                            await page.keyboard.insert_text(respuesta_inyeccion)
                            await page.wait_for_timeout(500)
                            await page.keyboard.press("Enter")
                            
                            print("   => [✓] Respuesta de conversión enviada y chat limpiado del radar.")
                            await page.wait_for_timeout(3000) # Respiro antes de saltar a otro cliente
            
            except Exception as loop_error:
                 # Errores DOM o desincronización
                 print(f"   [Sistema] Recalibrando sensores de UI (Cambio de página WhatsApp detectado o lag).")
                 
            # Vigilancia de ahorro de CPU
            await page.wait_for_timeout(10000)

if __name__ == "__main__":
    asyncio.run(atender_prospectos())
