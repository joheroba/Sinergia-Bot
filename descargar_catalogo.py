import requests
import re
import os

def descargar_catalogo():
    url = 'https://peru.ganoitouch.biz/Ordering.aspx'
    print(f'Navegando a la zona de Pedidos: {url}')
    try:
        res = requests.get(url, timeout=15)
        html = res.text
        
        # Extraccion segura de imagenes
        img_urls = re.findall(r'<img\s+[^>]*src="([^"]+)"', html, re.IGNORECASE)
        print(f'Detectadas {len(img_urls)} etiquetas img base.')
        
        carpeta = 'C:/GanoiTouch/assets_oficiales'
        os.makedirs(carpeta, exist_ok=True)
        count = 0
        
        for i in img_urls:
            # Ignorar iconos base
            if 'logo' in i.lower() or 'icon' in i.lower() or 'button' in i.lower() or 'loading' in i.lower():
                continue
            
            # Construir URL Absoluta
            img_url = i if i.startswith('http') else 'https://peru.ganoitouch.biz/' + i.lstrip('/')
            
            try:
                r2 = requests.get(img_url, timeout=5)
                # Bajar solo si peso > 5KB (Para capturar los frascos de Kibnabalu, PIOIR, etc)
                if r2.status_code == 200 and len(r2.content) >= 5000:
                    nombre = os.path.join(carpeta, f'producto_oficial_biz_{count}.jpg')
                    with open(nombre, 'wb') as f:
                        f.write(r2.content)
                    print(f'[+] Guardado ({len(r2.content)//1024} KB) -> {nombre}')
                    count += 1
            except Exception as d:
                print(f"Error bajando {img_url}: {d}")
                
        print(f'\n====\nFINALIZADO: {count} Imagenes de tu tienda GanoITouch.biz guardadas en la boveda!')
    except Exception as e:
        print('Fallo de Conexion Global:', e)

if __name__ == '__main__':
    descargar_catalogo()
