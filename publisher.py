import asyncio
import json
import os
import random
from datetime import datetime
from dotenv import load_dotenv
from playwright.async_api import async_playwright

# Cargar variables de entorno locales
load_dotenv()

JSON_PATH = "contenido_ganoderma.json"
USER_DATA_DIR = "./playwright_profile"

async def cargar_contenido():
    if not os.path.exists(JSON_PATH):
        print(f"Error: No se encontró {JSON_PATH}")
        return []
    with open(JSON_PATH, "r", encoding="utf-8") as file:
        return json.load(file)

async def guardar_contenido(data):
    with open(JSON_PATH, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

def obtener_media_rotativa(categoria):
    target_dir = os.path.join("imagenes", categoria)
    os.makedirs(target_dir, exist_ok=True)
    archivos_disponibles = [f for f in os.listdir(target_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.mp4', '.gif'))]
    if not archivos_disponibles:
        return None
    hist_file = "historial_multimedia.json"
    historial = json.load(open(hist_file, "r")) if os.path.exists(hist_file) else {}
    menor_usos = float('inf')
    archivo_elegido = archivos_disponibles[0]
    for arc in archivos_disponibles:
        key_uso = f"{categoria}_{arc}"
        usos = historial.get(key_uso, 0)
        if usos < menor_usos:
            menor_usos = usos
            archivo_elegido = arc
    historial[f"{categoria}_{archivo_elegido}"] = menor_usos + 1
    with open(hist_file, "w") as f:
        json.dump(historial, f, indent=4)
    return os.path.join(target_dir, archivo_elegido)

async def publicar_en_meta(context, post):
    """
    Intenta publicar el contenido usando Meta Business Suite.
    Al ser una automatización de navegador de UI en vivo, los selectores 
    pueden variar y deben ajustarse con las etiquetas exactas de la interfaz.
    """
    page = await context.new_page()
    
    # Navegamos directamente al Composer (Creador de Publicaciones) del Business Suite
    # Requiere que la sesión actual ya te tenga logueado.
    await page.goto("https://business.facebook.com/latest/composer", wait_until="networkidle")
    
    # Comprobar si nos re-dirigieron al login
    if "login" in page.url:
        print(">> No hay una sesión activa o ha caducado. Por favor, inicia sesión ahora y resuelve cualquier 2FA en la ventana del navegador.")
        print(">> El script pausará hasta que navegues exitosamente a Meta Business Suite (business.facebook.com).")
        # Esperará hasta que la URL deje de ser la de login
        await page.wait_for_url("**/latest/composer**", timeout=0)  # timeout 0 = Espera infinita manual.
        print(">> ¡Login detectado con éxito! Continuando con la publicación de manera automática...")
    else:
        print(">> Sesión validada. Ya estás dentro de Meta Business Suite.")
        
    try:
        # Esperamos a que la caja de texto central aparezca. 
        print(">> Esperando a que cargue la interfaz de creación...")
        await page.wait_for_timeout(3000) # Dejamos estabilizar Meta
        
        try:
            # RUTINA DE CAMBIO DE PÁGINA (Meta Business Suite Selector)
            # Facebook buscará literalmente esta cadena exacta dentro del panel
            nombre_pagina = "Gano Excel"
            print(f">> Verificando la cuenta en el selector: Debe ser '{nombre_pagina}'...")
            
            # Si el nombre de la página objetivo no está visible de entrada, abriremos el menú desplegable
            contenido = await page.content()
            if nombre_pagina not in contenido:
                print(">> Detectamos que estás en otra página (ej. Viajes y Aventura). Abriendo selector...")
                # Buscamos el combobox de selección de perfiles en el área 'Publicar en'
                selector_perfil = page.locator('div[role="combobox"]').first
                await selector_perfil.click(force=True)
                await page.wait_for_timeout(2000)
                
                # Una vez abierta la lista, le damos click al nombre de Gano Excel
                print(f">> Seleccionando '{nombre_pagina}'...")
                await page.locator(f'text="{nombre_pagina}"').first.click(force=True)
                print(">> [OK] Página correcta seleccionada.")
            else:
                 print(">> Ya estás posicionado en la página correcta.")
        except Exception as sel_err:
             print(">> [ADVERTENCIA] No se pudo cambiar de página automáticamente. Puede que ya estuvieras en la correcta o Meta cambió su diseño.")
        
        try:
            # Meta usa varios selectores dinámicos. Usaremos uno múltiple que agarre el primero visible.
            caja_texto = page.locator('div[contenteditable="true"], div[role="textbox"], [data-testid="composer-text-input"]').first
            await caja_texto.wait_for(state="visible", timeout=25000)
            
            print(">> Escribiendo el texto de la publicación...")
            await caja_texto.click()
            await page.wait_for_timeout(1000)
            await page.keyboard.insert_text(post["texto"])
            await page.wait_for_timeout(2000)
        except Exception as e:
            # Si el elemento no se encuentra, tomamos foto de la pantalla para "ver" tu Meta
            await page.screenshot(path=f"fallo_debug_{post['id']}.png", full_page=True)
            print(f">> [!] Se agotó el tiempo buscando la caja de texto.")
            print(f">> [!] He guardado una foto 'fallo_debug_{post['id']}.png'. ¡Ábrela para ver en qué pantalla se quedó Meta!")
            raise e
        
        # GESTOR MULTIMEDIA INTELIGENTE: Busca si hay categoría rotativa de fotos o ruta fija
        ruta_evaluada = None
        if "categoria_imagen" in post:
             ruta_evaluada = obtener_media_rotativa(post["categoria_imagen"])
        elif "ruta_imagen" in post and os.path.exists(post["ruta_imagen"]):
             ruta_evaluada = post["ruta_imagen"]

        # Click para abrir input de archivo
        if ruta_evaluada:
            print(f">> Subiendo la imagen o video del gestor ({ruta_evaluada})...")
            try:
                # Táctica Visual Revisada (Vía Clic exacto):
                # La estructura actual de Meta Business Suite en tu cuenta pide primero dar clic a "Agregar foto/video"
                # y luego parece desplegarse un minidropdown o abrir el file_chooser.
                
                async with page.expect_file_chooser(timeout=20000) as fc_info:
                    # En la foto veo claramente un botón que dice "Agregar foto/video" con ese slash exacto.
                    btn_agregar = page.locator('div[role="button"]:has-text("Agregar foto/video"), button:has-text("Agregar foto/video")').first
                    await btn_agregar.wait_for(state="visible", timeout=10000)
                    
                    # Le damos click directamente
                    await btn_agregar.click()
                    
                    # Si Meta abre un submenú que dice "Subir desde computadora", tratamos de agarrarlo.
                    # Si abre el selector de archivos de Windows directamente, esto no interfiere gracias al expect_file_chooser.
                    try: 
                        btn_subir_pc = page.locator('div[role="menuitem"]:has-text(" computadora")').first
                        await btn_subir_pc.wait_for(state="visible", timeout=2000)
                        await btn_subir_pc.click()
                    except:
                        pass # No hubo menú desplegable
                    
                file_chooser = await fc_info.value
                await file_chooser.set_files(ruta_evaluada)
                
                # Tiempo seguro para que la imagen suba la barra azul del centro
                await page.wait_for_timeout(7000)
                print(">> [OK] Imagen procesada.")
            except Exception as e_media:
                await page.screenshot(path=f"fallo_imagen_{post['id']}.png", full_page=True)
                print(f">> [!] Falló la inyección de imagen. He tomado una captura: fallo_imagen_{post['id']}.png")
                raise e_media
        else:
            print(">> No se encontró imagen o no está definida, se publicará solo el texto.")
            
        print(">> Presionando Publicar...")
        # En tu foto vimos el botón azul "Publicar" abajo a la derecha. Meta Suite usa complejos divs apilados.
        # Buscamos primero el botón oficial por rol, y si no, su texto directo en el último elemento (el de hasta abajo).
        btn_publicar = page.locator('div[aria-label="Publicar"], button:has-text("Publicar"), div[role="button"]:has-text("Publicar")').last
        
        await btn_publicar.wait_for(state="visible", timeout=15000)
        await btn_publicar.click(force=True)
        
        # Darle tiempo para procesar el subido antes de cerrar/validar 
        print(">> ¡Click en Publicar enviado! Esperando confirmación de la red...")
        await page.wait_for_timeout(10000)
        
        return True
    
    except Exception as e:
        # Tomar siempre pantalla en el error general para debugear fácilmente
        await page.screenshot(path=f"fallo_general_{post['id']}.png", full_page=True)
        print(f"Error durante el flujo de publicación automatizada en UI: {str(e)}")
        print(f">> [!] Se ha guardado la foto del error: fallo_general_{post['id']}.png")
        # Para debug, podríamos dejar el navegador abierto:
        print(">> Causando pausa para que revises qué falló. Presiona Enter en la consola para cerrar y abortar...")
        return False
    finally:
         await page.close()

async def publicar_en_grupo_facebook(context, grupo_info, post):
    page = await context.new_page()
    try:
        print(f"\n--- => Viajando al Grupo: [ {grupo_info['nombre']} ] ---")
        await page.goto(grupo_info["url"], wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(random.randint(4000, 7000)) # Pausa orgánica para engañar a FB

        # 1. Localizar y Clicar "Escribe algo..."
        click_escribir = page.locator('div[role="button"]:has-text("Escribe algo"), div:has-text("Escribe algo...")').last
        await click_escribir.wait_for(state="visible", timeout=15000)
        await click_escribir.click(force=True)
        await page.wait_for_timeout(2000)
        
        # 2. Insertar Texto 
        caja_texto = page.locator('div[contenteditable="true"][role="textbox"]').first
        await caja_texto.wait_for(state="visible", timeout=10000)
        await caja_texto.fill(post["texto"])
        await page.wait_for_timeout(1000)
        
        ruta_evaluada = None
        if "categoria_imagen" in post:
             ruta_evaluada = obtener_media_rotativa(post["categoria_imagen"])
        elif "ruta_imagen" in post and os.path.exists(post["ruta_imagen"]):
             ruta_evaluada = post["ruta_imagen"]

        # 3. Subir Imagen Oficial (Opcion A)
        if ruta_evaluada:
            print(">> Subiendo multimedia al grupo...")
            file_input = page.locator('input[type="file"]')
            if await file_input.count() > 0:
                await file_input.first.set_input_files(ruta_evaluada)
            else:
                async with page.expect_file_chooser(timeout=20000) as fc_info:
                    await page.locator('div[aria-label="Foto/video"], div[aria-label="Foto/vídeo"], div[aria-label="Agregar a tu publicación"]').first.click()
                file_chooser = await fc_info.value
                await file_chooser.set_files(ruta_evaluada)
            await page.wait_for_timeout(6000)
            print(">> [OK] Multimedia cargada.")

        # 4. Enviar a Publicar
        print(">> Disparando post al grupo ('Publicar')...")
        # En grupos FB, suele haber un boton directo
        btn_publicar = page.locator('div[aria-label="Publicar"][role="button"], span:has-text("Publicar")').last
        await btn_publicar.wait_for(state="visible", timeout=15000)
        await btn_publicar.click(force=True)
        
        print(f">> ¡Publicación exitosa en grupo {grupo_info['nombre']}!")
        await page.wait_for_timeout(5000) # Tiempo para el cierre de JS
        return True
        
    except Exception as e:
        await page.screenshot(path=f"fallo_grupo_{grupo_info['id']}.png", full_page=True)
        print(f">> [!] Error subiendo al grupo {grupo_info['nombre']}: {str(e)}")
        print(f"      Se guardó captura de depuración: fallo_grupo_{grupo_info['id']}.png")
        return False
    finally:
        await page.close()

async def main():
    contenido = await cargar_contenido()
    if not contenido:
        return

    # Cargar Grupos
    try:
        with open("grupos_facebook.json", "r", encoding="utf-8") as fG:
            lista_grupos = json.load(fG)
    except Exception:
        lista_grupos = []

    # Filtramos la lista a los post 'aprobados' que no tienen 'fecha_publicacion'
    posts_pendientes = [p for p in contenido if p.get("estado") == "aprobado" and not p.get("fecha_publicacion")]
    
    if not posts_pendientes:
        print("No hay entradas aprobadas pendientes por publicar en contenido_ganoderma.json.")
        return

    print("Iniciando Playwright en modo Contexto Persistente...")
    async with async_playwright() as p:
        # launch_persistent_context conserva nuestra sesión y 2FA
        context = await p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            headless=False,  # ¡Debe ser False para que puedas resolver el 2FA o el Captcha si Meta lo pide!
            viewport={"width": 1280, "height": 720},
            args=["--disable-notifications"]
        )
        
        exitosas = 0
        for i, post in enumerate(posts_pendientes):
            print(f"\n--- Procesando Publicación ID: {post['id']} ---")
            
            # Ejecutar bot en la UI de Meta para este post
            exito = await publicar_en_meta(context, post)
            
            if exito:
                # Marcamos como publicado en la data estructurada
                post["fecha_publicacion"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[{post['id']}] ¡Publicación de fanpage exitosa!")
                exitosas += 1
                
                # --- PUBLICACIÓN EXPANSIVA: GRUPOS LOCALES ---
                if len(lista_grupos) > 0:
                     print(f">> [EXPANSIÓN] Inyectando contenido en Grupos de La Molina...")
                     for g_idx, grupo in enumerate(lista_grupos):
                          ex_grupo = await publicar_en_grupo_facebook(context, grupo, post)
                          if ex_grupo:
                              retraso = random.randint(30, 60) # Testeo (Cambiar a 150-180 después)
                              print(f">> [ANTI-SPAM] Retraso de seguridad por {retraso} segundos. Pausado...")
                              await asyncio.sleep(retraso)
            else:
                 print(f"[{post['id']}] Hubo un error, omitiendo...")
            
            # Guardamos el JSON después de cada post por seguridad (si cae la red o algo)
            await guardar_contenido(contenido)
            
            # Espera simulando comportamiento humano entre publicaciones (si es más de 1 post)
            if i < len(posts_pendientes) - 1:
                print(">> Esperando 10 segundos antes del siguiente post para evitar flags de spam...")
                await asyncio.sleep(10)
        
        await context.close()
        print(f"\nProceso finalizado. Total posts publicados: {exitosas}")


if __name__ == "__main__":
    asyncio.run(main())
