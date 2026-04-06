import os
import asyncio
import requests
from playwright.async_api import async_playwright

async def extraer():
    os.makedirs('assets_oficiales', exist_ok=True)
    print("==================================================")
    print("  SCRAPER: DESCARGA DE CAJAS OFICIALES GANO ITOUCH")
    print("==================================================")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("1. Accediendo a gano-itouch.com.pe/productos/ ...")
        
        try:
            await page.goto("https://gano-itouch.com.pe/productos/", timeout=60000, wait_until="domcontentloaded")
            await page.wait_for_timeout(3000) # Dejar que procesen fotos diferidas
            
            # Buscar links de imagenes
            imagenes = await page.evaluate('''() => {
                let imgs = Array.from(document.querySelectorAll("img"));
                return imgs.map(img => img.src || img.getAttribute('data-src')).filter(src => src && (src.includes("jpg") || src.includes("jpeg") || src.includes("png")));
            }''')
            
            urls_unicas = list(set(imagenes))
            print(f"2. Interceptamos {len(urls_unicas)} enlaces fotográficos. Filtrando...")
            
            count = 0
            for url in urls_unicas:
                try:
                    res = requests.get(url, timeout=10)
                    # Consideramos que las cajas / fotos HD pesan mas de 15KB (ignorando iconos web)
                    if len(res.content) > 15000:
                        ruta = f"assets_oficiales/asset_gano_{count}.jpg"
                        with open(ruta, "wb") as f:
                            f.write(res.content)
                        count += 1
                        print(f"   [+] Foto bajada: {ruta}")
                except Exception as e:
                    pass
                
                # Rescatar las 10 mejores
                if count >= 10:
                    break
            
            print(f"✅ ¡Operación Exitosa! {count} Fondos corporativos guardados en /assets_oficiales.")
        except Exception as e:
            print(f"Error raspando la web: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(extraer())
