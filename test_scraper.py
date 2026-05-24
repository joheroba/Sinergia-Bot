import asyncio
import os
from playwright.async_api import async_playwright

async def run_test(username, password):
    print("Iniciando prueba de extracción del Backoffice de Gano iTouch...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True) # Ejecutar en modo headless para servidor
        page = await browser.new_page()
        
        try:
            url_login = "https://peru.ganoitouch.biz/Login"
            print(f"Navegando a {url_login}")
            await page.goto(url_login, timeout=60000)
            
            await page.screenshot(path="backoffice_paso1_inicio.png")
            print("Captura inicial guardada: backoffice_paso1_inicio.png")
            
            try:
                print("Buscando campos de usuario y contraseña...")
                user_input = page.locator('input[type="text"], input[name*="user"], input[name*="login"]').first
                pass_input = page.locator('input[type="password"]').first
                
                await user_input.wait_for(timeout=15000)
                await user_input.fill(username)
                await pass_input.fill(password)
                
                await pass_input.press("Enter")
                print("Credenciales enviadas. Esperando carga del Dashboard...")
                
                await page.wait_for_timeout(10000)
                await page.screenshot(path="backoffice_paso2_dashboard.png")
                print("Captura del Dashboard guardada: backoffice_paso2_dashboard.png")
                
                texto_pagina = await page.inner_text("body")
                print("\n--- TEXTO EXTRAIDO DEL DASHBOARD ---")
                print(texto_pagina[:800] + "...\n(Mostrando primeros caracteres)")
                
            except Exception as inner_e:
                print(f"No se pudo completar el login automático: {inner_e}")
                
        except Exception as e:
            print(f"Error general en la navegación: {e}")
        finally:
            await browser.close()
            print("Prueba finalizada.")

if __name__ == "__main__":
    print("=== TEST DE EXTRACCIÓN GANO ITOUCH ===")
    asyncio.run(run_test("4408926", "5365"))
