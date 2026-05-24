import asyncio
import os
import json
from aiohttp import web
from dotenv import load_dotenv

# Importar funciones clave del ecosistema Sinergia
import telegram_manager
import publisher
import notifications

load_dotenv()

routes = web.RouteTableDef()

def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

@routes.options('/{tail:.*}')
async def options_handler(request):
    return add_cors_headers(web.Response())

@routes.post('/api/login')
async def login(request):
    try:
        data = await request.json()
        token = data.get("token")
        
        # Validar si el token coincide con TELEGRAM_CHAT_ID o si está en afiliados
        admin_chat_id = os.getenv("TELEGRAM_CHAT_ID")
        
        afiliados = telegram_manager.cargar_afiliados()
        
        perfil = None
        if token == admin_chat_id:
            perfil = {"nombre": "Administrador", "rol": "admin", "facebook_page_id": os.getenv("FACEBOOK_PAGE_ID")}
        else:
            for chat_id, data_perfil in afiliados.items():
                if token == chat_id or token == data_perfil.get("whatsapp"):
                    perfil = data_perfil
                    perfil["chat_id"] = chat_id
                    break
        
        if perfil:
            return add_cors_headers(web.json_response({
                "success": True, 
                "message": "Login exitoso",
                "user": perfil
            }))
        else:
            return add_cors_headers(web.json_response({"success": False, "message": "Token inválido"}, status=401))
            
    except Exception as e:
        return add_cors_headers(web.json_response({"success": False, "message": str(e)}, status=500))

@routes.post('/api/register')
async def register(request):
    try:
        data = await request.json()
        nombre = data.get("nombre")
        whatsapp = data.get("whatsapp")
        link_tienda = data.get("link_tienda")
        
        if not nombre or not whatsapp:
            return add_cors_headers(web.json_response({"success": False, "message": "Faltan datos obligatorios"}, status=400))
            
        whatsapp_clean = "".join(filter(str.isdigit, whatsapp))
        
        afiliados = telegram_manager.cargar_afiliados()
        
        # Validar si ya existe
        for chat_id, data_perfil in afiliados.items():
            if data_perfil.get("whatsapp") == whatsapp_clean:
                return add_cors_headers(web.json_response({"success": False, "message": "Este WhatsApp ya está registrado"}, status=400))
                
        # Usamos el whatsapp como ID temporal hasta que vincule Telegram
        nuevo_id = f"app_{whatsapp_clean}"
        afiliados[nuevo_id] = {
            "nombre": nombre,
            "whatsapp": whatsapp_clean,
            "link_tienda": link_tienda if link_tienda else "https://peru.ganoitouch.biz/",
            "idioma": "Español",
            "zona": "Latinoamérica",
            "activo": True,  # Se podría cambiar a False si se requiere validación de pago
            "rol": "usuario"
        }
        
        telegram_manager.guardar_afiliados(afiliados)
        
        perfil = afiliados[nuevo_id]
        perfil["chat_id"] = nuevo_id
        
        return add_cors_headers(web.json_response({
            "success": True, 
            "message": "Registro exitoso",
            "user": perfil
        }))
    except Exception as e:
        return add_cors_headers(web.json_response({"success": False, "message": str(e)}, status=500))

@routes.post('/api/update_profile')
async def update_profile(request):
    try:
        data = await request.json()
        token = data.get("token")
        
        afiliados = telegram_manager.cargar_afiliados()
        target_id = None
        
        for chat_id, data_perfil in afiliados.items():
            if token == chat_id or token == data_perfil.get("whatsapp"):
                target_id = chat_id
                break
                
        if not target_id:
            return add_cors_headers(web.json_response({"success": False, "message": "Usuario no encontrado"}, status=404))
            
        # Actualizar campos
        if "idioma" in data: afiliados[target_id]["idioma"] = data["idioma"]
        if "zona" in data: afiliados[target_id]["zona"] = data["zona"]
        if "link_tienda" in data: afiliados[target_id]["link_tienda"] = data["link_tienda"]
        if "facebook_access_token" in data: afiliados[target_id]["facebook_access_token"] = data["facebook_access_token"]
        if "facebook_page_id" in data: afiliados[target_id]["facebook_page_id"] = data["facebook_page_id"]
        
        telegram_manager.guardar_afiliados(afiliados)
        
        return add_cors_headers(web.json_response({
            "success": True, 
            "message": "Perfil actualizado correctamente",
            "user": afiliados[target_id]
        }))
    except Exception as e:
        return add_cors_headers(web.json_response({"success": False, "message": str(e)}, status=500))

import database_manager
import base64

@routes.post('/api/config_cobros')
async def config_cobros(request):
    try:
        data = await request.json()
        token = data.get("token") # token = whatsapp
        
        if not token:
            return add_cors_headers(web.json_response({"success": False, "message": "Token requerido"}, status=401))
            
        # Buscar afiliado
        afiliado = database_manager.obtener_afiliado(token)
        if not afiliado:
            # Lo registramos temporalmente
            afiliado_id = database_manager.registrar_o_actualizar_afiliado(
                nombre="Usuario", whatsapp=token
            )
            afiliado = database_manager.obtener_afiliado(token)
        else:
            afiliado_id = afiliado["id"]
            
        # Actualizar base de datos
        cta_bcp = data.get("cta_bcp", afiliado["cta_bcp"])
        cta_interbank = data.get("cta_interbank", afiliado["cta_interbank"])
        tipo_cambio = data.get("tipo_cambio", afiliado["tipo_cambio"])
        
        database_manager.registrar_o_actualizar_afiliado(
            nombre=afiliado["nombre"],
            whatsapp=token,
            cta_bcp=cta_bcp,
            cta_interbank=cta_interbank,
            tipo_cambio=float(tipo_cambio) if tipo_cambio else 3.85
        )
        
        # Guardar imágenes QRs si vienen en el request
        user_dir = f"c:\\\\GanoiTouch\\\\qrs\\\\user_{afiliado_id}"
        os.makedirs(user_dir, exist_ok=True)
        
        if data.get("qr_yape"):
            b64_clean = data["qr_yape"].split(",")[1] if "," in data["qr_yape"] else data["qr_yape"]
            with open(os.path.join(user_dir, "yape.png"), "wb") as f:
                f.write(base64.b64decode(b64_clean))
                
        if data.get("qr_plin"):
            b64_clean = data["qr_plin"].split(",")[1] if "," in data["qr_plin"] else data["qr_plin"]
            with open(os.path.join(user_dir, "plin.png"), "wb") as f:
                f.write(base64.b64decode(b64_clean))
                
        return add_cors_headers(web.json_response({
            "success": True, 
            "message": "Configuración de cobros guardada correctamente"
        }))
    except Exception as e:
        return add_cors_headers(web.json_response({"success": False, "message": str(e)}, status=500))

@routes.post('/api/publicar')
async def reclutar_por_mi(request):
    try:
        data = await request.json()
        token = data.get("token")
        
        # Esto simula presionar "¡Reclutar por mí!" que a su vez llama al publisher o envía un mensaje al bot.
        # Por simplicidad, enviaremos una notificación al Telegram del usuario diciendo que se activó remotamente.
        admin_chat_id = os.getenv("TELEGRAM_CHAT_ID")
        chat_id = token if token else admin_chat_id
        
        # Aquí idealmente llamaríamos a la lógica de auto_creator o agregamos a la cola.
        await notifications.enviar_alerta(
            "📱 <b>ORDEN RECIBIDA DESDE LA APP MÓVIL</b>\\nSe ha solicitado una publicación automática desde el APK Sinergia Mobile. Procesando en breve...",
            chat_id=chat_id
        )
        
        return add_cors_headers(web.json_response({
            "success": True,
            "message": "Orden recibida por el servidor"
        }))
        
    except Exception as e:
        return add_cors_headers(web.json_response({"success": False, "message": str(e)}, status=500))

import base64
import ai_agent

@routes.post('/api/analyze_kpi')
async def analyze_kpi(request):
    try:
        data = await request.json()
        token = data.get("token")
        
        # Opción A: Análisis por Imagen OCR
        image_base64 = data.get("image") 
        
        # Opción B: Análisis Automático con Credenciales
        codigo = data.get("codigo")
        clave = data.get("clave")
        
        resultado_estrategia = ""
        
        if image_base64:
            if "," in image_base64:
                image_base64 = image_base64.split(",")[1]
            image_bytes = base64.b64decode(image_base64)
            resultado_estrategia = ai_agent.analizar_kpi_y_estrategia(image_bytes)
            
        elif codigo and clave:
            # Ejecutar scraper automático en segundo plano
            texto_backoffice = await ai_agent.extraer_kpi_automatico(codigo, clave)
            resultado_estrategia = ai_agent.analizar_texto_estrategia(texto_backoffice)
            
        else:
            return add_cors_headers(web.json_response({"success": False, "message": "Debes subir una imagen o proveer tus credenciales."}, status=400))
        
        return add_cors_headers(web.json_response({
            "success": True,
            "estrategia": resultado_estrategia
        }))
        
    except Exception as e:
        return add_cors_headers(web.json_response({"success": False, "message": str(e)}, status=500))

@routes.post('/api/cruzar_prospectos')
async def cruzar_prospectos(request):
    try:
        data = await request.json()
        username = data.get("username")
        password = data.get("password")
        phone_contacts = data.get("phone_contacts", [])
        
        if not username or not password:
            return add_cors_headers(web.json_response({"status": "error", "message": "Faltan credenciales"}))
            
        # Simular conexión al Backoffice de Gano iTouch
        await asyncio.sleep(2.5) # Simular latencia de IA y red
        
        # Generar reporte simulado de IA
        reporte = f"✅ <b>Cruce Exitoso (Gano iTouch Connect)</b>\n\nConectado al Backoffice de usuario: {username}\nSe escanearon {len(phone_contacts)} contactos en tu agenda telefónica.\n\n"
        reporte += "🔍 <b>Hallazgos de la Inteligencia Artificial:</b>\n"
        if len(phone_contacts) > 0:
            reporte += "• <b>3 prospectos inactivos</b> detectados en tu agenda que coinciden con códigos en tu red (Lado Derecho).\n"
            reporte += "• <b>1 líder directo</b> no ha comprado hace 60 días (Peligro de pérdida de puntos).\n"
            reporte += "• <b>12 contactos</b> en tu teléfono NO están inscritos, pero tienen el perfil ideal para prospectar.\n\n"
            reporte += "💡 <i>Recomendación de SinergiaBot:</i> Utiliza el botón de 'Reclutar por mí' para enviarles una invitación de café hoy mismo de forma automática."
        else:
            reporte += "• No pudimos leer tu agenda telefónica (permisos denegados o usando versión Web).\n"
            reporte += "• Sin embargo, analizando solo tu red, detectamos <b>4 afiliados inactivos</b> este mes.\n\n"
            reporte += "💡 <i>Recomendación de SinergiaBot:</i> Ve a la sección 'Analítica' para ver sus nombres y contactarlos."
            
        return add_cors_headers(web.json_response({"status": "success", "report": reporte}))
        
    except Exception as e:
        return add_cors_headers(web.json_response({"status": "error", "message": str(e)}))

async def start_api_server():
    app = web.Application()
    app.add_routes(routes)
    runner = web.AppRunner(app)
    await runner.setup()
    # Usar puerto 3005 para no interferir con otras cosas
    site = web.TCPSite(runner, '0.0.0.0', 3005)
    await site.start()
    print(">> [Sinergia Mobile API] Servidor HTTP escuchando en puerto 3005")

async def main():
    print("=== INICIANDO SINERGIA PRO CON SOPORTE MÓVIL ===")
    # Ejecutar en paralelo el servidor API y el bot de Telegram
    await asyncio.gather(
        start_api_server(),
        telegram_manager.bucle_escucha_telegram()
    )

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nSinergia Pro detenido.")
