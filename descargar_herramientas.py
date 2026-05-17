import os
import requests

URLS = {
    "mr_leow1.jpg": "https://gano-itouch.com.pe/wp-content/uploads/2021/03/Mr.-Leow1-scaled.jpg",
    "mr_leow2.jpg": "https://gano-itouch.com.pe/wp-content/uploads/2021/03/Mr.-Leow2-scaled.jpg",
    "mr_leow3.jpg": "https://gano-itouch.com.pe/wp-content/uploads/2021/03/Mr.-Leow3-scaled.jpg",
    "banner_pioir.jpg": "https://gano-itouch.com.pe/wp-content/uploads/2023/03/BannerPioir-scaled.jpg",
    "producto_3en1.jpg": "https://gano-itouch.com.pe/wp-content/uploads/2021/03/3en1-scaled.jpg",
    "producto_blackcoffee.jpg": "https://gano-itouch.com.pe/wp-content/uploads/2021/03/blackcoffee-scaled.jpg",
    "producto_chocolate.jpg": "https://gano-itouch.com.pe/wp-content/uploads/2021/03/Chocolate-scaled.jpg",
    "producto_cereal.jpg": "https://gano-itouch.com.pe/wp-content/uploads/2021/03/Creal-scaled.jpg",
    "producto_rooibos.jpg": "https://gano-itouch.com.pe/wp-content/uploads/2023/03/TeRooibos-scaled.jpg",
    "producto_mocharico.jpg": "https://gano-itouch.com.pe/wp-content/uploads/2023/03/MochaRico-scaled.jpg",
    "producto_latterico.jpg": "https://gano-itouch.com.pe/wp-content/uploads/2023/07/Banner-LatteRico-scaled.jpg",
    "producto_shokorico.jpg": "https://gano-itouch.com.pe/wp-content/uploads/2023/07/Banner-ShokoRico-scaled.jpg",
    "producto_rico.jpg": "https://gano-itouch.com.pe/wp-content/uploads/2023/07/RICO-scaled.jpg",
    "producto_jabon.jpg": "https://gano-itouch.com.pe/wp-content/uploads/2021/04/jabon-scaled.jpg",
    "producto_pastadental.jpg": "https://gano-itouch.com.pe/wp-content/uploads/2021/04/pastadental-scaled.jpg",
    "producto_kibnabalu.jpg": "https://gano-itouch.com.pe/wp-content/uploads/2021/03/KIBNABALU-scaled.jpg",
    "producto_p8b.jpg": "https://gano-itouch.com.pe/wp-content/uploads/2023/03/BannerP8B-scaled.jpg",
    "calendario_2026.jpg": "https://gano-itouch.com.pe/wp-content/uploads/Calendario2026.jpg",
    "onetoone_es.jpg": "https://gano-itouch.com.pe/wp-content/uploads/2023/01/OnetoOneEspanol-scaled.jpg",
    "onetoone_en.jpg": "https://gano-itouch.com.pe/wp-content/uploads/2023/01/OnetoOneIngles-scaled.jpg",
    "onetoone_qu.jpg": "https://gano-itouch.com.pe/wp-content/uploads/2023/01/OnetoOneQuechua-scaled.jpg",
    "logo_distribuidor_h.png": "https://gano-itouch.com.pe/wp-content/uploads/2021/03/LogoDistribuidor.png",
    "logo_distribuidor_c.png": "https://gano-itouch.com.pe/wp-content/uploads/2021/03/LogoDistribuidor2.png"
}

def descargar_recursos():
    carpeta = "assets_oficiales"
    os.makedirs(carpeta, exist_ok=True)
    
    print("==================================================")
    # Codificar salida a consola
    print("  DESCARGADOR DE HERRAMIENTAS OFICIALES GANO ITOUCH")
    print("==================================================\n")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    exito = 0
    for nombre, url in URLS.items():
        ruta = os.path.join(carpeta, nombre)
        print(f"Descargando {nombre}...")
        try:
            res = requests.get(url, headers=headers, timeout=20)
            if res.status_code == 200:
                with open(ruta, "wb") as f:
                    f.write(res.content)
                print(f"   [+] ¡Completado! ({len(res.content)//1024} KB)")
                exito += 1
            else:
                print(f"   [x] Error HTTP: {res.status_code}")
        except Exception as e:
            print(f"   [x] Error al descargar: {e}")
            
    print(f"\n==================================================")
    print(f"  DESCARGA COMPLETADA: {exito}/{len(URLS)} recursos oficiales en HD")
    print("==================================================")

if __name__ == "__main__":
    descargar_recursos()
