import os
import random
import textwrap
import asyncio
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageOps

# Hooks y Base
HOOKS_SALUD = [
    "No es magia, es nutrición celular.\nEmpieza el día con Ganoderma.",
    "Refuerza tus defensas de forma\nnatural y conquista tu rutina diaria.",
    "¿Fatiga a media tarde? Eleva tu\nvitalidad mental sin azúcar añadida.",
    "Si cuidas el motor de tu carro,\n¿por qué no hidratas tu sistema inmune?",
    "Más energía, menos estrés.\nEl aliado diario de los que no se detienen.",
    "Sabor intenso. 100% equilibrio orgánico.\nDale a tu cuerpo lo que exige.",
    "Cambia la cafeína común por\nvitalidad funcional. Siente la diferencia."
]

HOOKS_NEGOCIO = [
    "¿Y si tu bebida de cada mañana\ncomenzara a pagarte grandes dividendos?",
    "Construye autonomía financiera\nrepartiendo bienestar al mundo.",
    "El negocio perfecto existe:\nAquel que haces mientras ayudas a otros.",
    "De empleado a diseñador de vida.\nConstruye tu propio pilar en Network Marketing.",
    "Tus redes sociales no deben quitarte\ntiempo. Deben generar ingresos residuales.",
    "Apoyando una línea de talla mundial.\nLa oportunidad Gano iTouch.",
    "Un emprendimiento sólido desde\ntu hogar. Descubre cómo ser socio directo."
]

def dibujar_word_wrap(draw, texto_largo, fuente, x_caja, y_caja, ancho_caja, alto_caja):
    """Calcula los saltos de línea matemáticamente para que nada se salga por el borde derecho/izquierdo."""
    # Modulador seguro de cantidad de letras (approx 34 letras para nuestro font size)
    caracteres_maximos = int(ancho_caja / 30) 
    
    # Limpiamos el texto original (quitamos \n de prueba) y lo envolvemos
    texto_limpio = texto_largo.replace('\n', ' ')
    lineas = textwrap.wrap(texto_limpio, width=caracteres_maximos)
    
    # Calcular centro 'Y' para que todo el párrafo flote al medio
    interlineado = 85
    y_text = y_caja + (alto_caja // 2) - (len(lineas) * interlineado // 2)
    
    for linea in lineas:
        try:
            bbox = draw.textbbox((0, 0), linea, font=fuente)
            ancho_linea = bbox[2] - bbox[0]
        except Exception:
            # Fallback seguro para fuentes que no soportan getbbox (como la default en Linux)
            ancho_linea = len(linea) * 22
            
        x_alineado = x_caja + (ancho_caja - ancho_linea) / 2
        
        # Efecto Parallax en las letras (Sombra Negra dura de contraste)
        draw.text((x_alineado + 5, y_text + 5), linea, font=fuente, fill=(0, 0, 0, 200))
        # Frontal Inmaculado White
        draw.text((x_alineado, y_text), linea, font=fuente, fill=(255, 255, 255))
        y_text += interlineado

def redimensionar_con_fondo_borroso(imagen_base, ancho_salida=1080, alto_salida=1080):
    """
    Toma una imagen y la ajusta al tamaño cuadrado deseado preservando su aspecto.
    Rellena los bordes vacíos con una copia súper borrosa y elegante de la misma imagen.
    Garantiza que los rostros (como el CEO Mr. Leow Soon Seng) nunca sean cortados.
    """
    from PIL import ImageFilter
    
    # 1. Crear el lienzo de fondo con la imagen base muy estirada y borrosa
    fondo = imagen_base.resize((ancho_salida, alto_salida), Image.Resampling.LANCZOS)
    fondo = fondo.filter(ImageFilter.GaussianBlur(radius=30)) # Desenfoque premium de 30px
    
    # 2. Agregar una capa oscura translúcida sobre el fondo borroso para dar contraste de fondo
    capa_oscura = Image.new('RGBA', (ancho_salida, alto_salida), (15, 10, 5, 120))
    fondo.alpha_composite(capa_oscura)
    
    # 3. Ajustar la imagen real manteniendo la proporción exacta
    img_w, img_h = imagen_base.size
    ratio = min(ancho_salida / img_w, alto_salida / img_h)
    nuevo_w = int(img_w * ratio)
    nuevo_h = int(img_h * ratio)
    
    img_redimensionada = imagen_base.resize((nuevo_w, nuevo_h), Image.Resampling.LANCZOS)
    
    # 4. Pegar la imagen real en el centro del fondo borroso
    pos_x = (ancho_salida - nuevo_w) // 2
    pos_y = (alto_salida - nuevo_h) // 2
    
    if img_redimensionada.mode != 'RGBA':
        img_redimensionada = img_redimensionada.convert('RGBA')
        
    fondo.paste(img_redimensionada, (pos_x, pos_y), img_redimensionada)
    return fondo

def crear_tarjeta_viral(texto, categoria, index):
    ancho, alto = 1080, 1080
    
    # 1. MONTAR FOTOGRAFÍA FÍSICA A LA PANTALLA (CON FILTRADO HD Y SELECCIÓN INTELIGENTE)
    carpeta_assets = "assets_oficiales"
    if os.path.exists(os.path.join(carpeta_assets, "assets_oficiales")):
        carpeta_assets = os.path.join(carpeta_assets, "assets_oficiales")
        
    try:
        # Filtrar imágenes que pesen más de 200 KB para evitar iconos pixelados extraídos de los PDF
        fotos_grandes = []
        for f in os.listdir(carpeta_assets):
            if f.endswith(('.jpg', '.png', '.jpeg')):
                ruta_temp = os.path.join(carpeta_assets, f)
                if os.path.getsize(ruta_temp) >= 200000: # 200 KB mínimo para HD
                     fotos_grandes.append(f)
                     
        if not fotos_grandes:
            raise Exception("No hay fotos grandes en assets_oficiales")
            
        # Selección inteligente por categoría para garantizar variedad (Anti-Baneo y mayor conversión)
        foto_elegida = None
        if categoria == "salud":
            # Obtener productos de salud específicos (3en1, cafe negro, chocolate, cereal, pasta dental, etc.)
            productos_salud = [f for f in fotos_grandes if f.startswith("producto_") and "jabon" not in f]
            if productos_salud:
                foto_elegida = productos_salud[index % len(productos_salud)]
            else:
                # Fallback de salud
                afines = [f for f in fotos_grandes if any(k in f.lower() for k in ["health", "salud", "cafe", "coffee", "nutri", "lucidum"])]
                if afines:
                    foto_elegida = afines[index % len(afines)]
        else: # negocio
            # Obtener infografías de negocio, plan servilleta, fotos corporativas y láminas del plan oficial (excluyendo 'image' genérico para mayor variedad)
            fotos_negocio = [f for f in fotos_grandes if any(k in f.lower() for k in ["business", "plan_", "onetoone", "mr_leow", "pioir", "negocio", "gold", "jabon"])]
            if fotos_negocio:
                foto_elegida = fotos_negocio[index % len(fotos_negocio)]
            else:
                if "gano_business_gold.png" in fotos_grandes:
                    foto_elegida = "gano_business_gold.png"
                    
        # Fallback 3: Si no hay específicos, elegir secuencialmente de las fotos grandes
        if not foto_elegida:
            foto_elegida = fotos_grandes[index % len(fotos_grandes)]
            
        img_ruta = os.path.join(carpeta_assets, foto_elegida)
        print(f">> [Fábrica Visual] Seleccionada imagen premium: {img_ruta} ({os.path.getsize(img_ruta)//1024} KB)")
        
        fondo_base = Image.open(img_ruta).convert('RGBA')
        
        # Calcular aspecto ratio y verificar si contiene personas como Mr. Leow o infografías clave
        base_w, base_h = fondo_base.size
        aspect_ratio = base_w / base_h
        
        if aspect_ratio < 0.95 or aspect_ratio > 1.05 or any(k in foto_elegida.lower() for k in ["mr_leow", "plan_", "servilleta", "compensacion", "gold", "ceos", "soon_seng"]):
            print(f">> [Fábrica Visual] Aplicando encuadre inteligente con fondo borroso para evitar cortes de rostros (ej: CEO o infografía).")
            img = redimensionar_con_fondo_borroso(fondo_base, ancho, alto)
        else:
            # Crop Inteligente a cuadrado de Instagram 1:1 sin deformar
            img = ImageOps.fit(fondo_base, (ancho, alto), method=Image.Resampling.LANCZOS)
    except Exception as e:
        print(f">> [Fábrica Visual] Alerta al cargar imagen: {e}. Usando fondo de respaldo.")
        try:
            import notifications
            chat_id = os.getenv("TELEGRAM_CHAT_ID")
            if chat_id:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(notifications.enviar_alerta(f"⚠️ <b>[Fábrica Visual]</b> Error al procesar imagen: <code>{e}</code>. Se usó el fondo de respaldo marrón.", chat_id=chat_id))
        except Exception:
            pass
        # Backup Background en caso de falla
        img = Image.new('RGBA', (ancho, alto), (54, 25, 11, 255))

    draw = ImageDraw.Draw(img, 'RGBA')
    
    # Fuentes Premium High-Res para centrado y renderizado estético de alta definición
    if os.name != "nt":
        fuentes_elegantes = [
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        ]
    else:
        fuentes_elegantes = ["seguibl.ttf", "calibrib.ttf", "trebucbd.ttf", "arialbd.ttf"]
    
    fuente = fuente_logo = None
    for f in fuentes_elegantes:
        try:
            fuente = ImageFont.truetype(f, 65)
            fuente_logo = ImageFont.truetype(f, 32)
            break
        except IOError:
            continue
            
    if not fuente:
        fuente = fuente_logo = ImageFont.load_default()

    # 2. ALTERNAR CEREBROS DE DISEÑO ENTRE MINIMALISTA MASCULINO Y GLASS CORPORATE
    estilo = random.choice(["DISENO_ROLEX", "DISENO_CRISTAL"])
    
    if estilo == "DISENO_ROLEX":
        # Apagón General: Filtro humo oscuro al 60% sobre TODA la caja para exaltar la tipografía
        draw.rectangle([(0,0), (ancho, alto)], fill=(10, 10, 10, 170))
        dibujar_word_wrap(draw, texto, fuente, 80, 0, ancho-160, alto - 100)
    else:
        # Modo Cristal: Fondo iluminado y letras dentro del recuadro transparente en medio
        padding = 70
        caja_ancho = ancho - (padding * 2)
        caja_alto = 450
        y_caja = (alto - caja_alto) // 2 - 50
        
        # Placa Glass
        draw.rounded_rectangle(
            [(padding, y_caja), (ancho - padding, y_caja + caja_alto)],
            radius=20, fill=(0, 0, 0, 160), outline=(255, 215, 0, 200), width=5
        )
        draw.ellipse([(ancho//2 - 15, y_caja - 30), (ancho//2 + 15, y_caja)], fill=(255, 215, 0))
        dibujar_word_wrap(draw, texto, fuente, padding + 20, y_caja, caja_ancho - 40, caja_alto)

    # 3. FIRMA CORPORATIVA Y LOGO DEL DISTRIBUIDOR (Watermark Superior)
    
    # Motor de Incrustación de Logo Oficial
    ruta_logo = "logo_distribuidor.png"
    if os.path.exists(ruta_logo):
        try:
            logo_img = Image.open(ruta_logo).convert("RGBA")
            # Escalar estéticamente para que no abrume el arte (200x200 max)
            logo_img.thumbnail((220, 220), Image.Resampling.LANCZOS)
            
            # UBICACIÓN: Esquina Superior Derecha (como un escudo oficial de canal)
            pos_x = ancho - logo_img.width - 40
            pos_y = 40
            
            # Pegar respetando el canal Alfa (transparencia de tu logo para no sobreponer fondos blancos)
            img.paste(logo_img, (pos_x, pos_y), logo_img)
        except Exception as d:
            print(f"Alerta: El logo oficial se encontró pero no pudo inyectarse ({d})")

    # Pie de Página Base
    draw.line([(0, 1020), (ancho, 1020)], fill=(255, 215, 0, 255), width=5)
    bbox_logo = draw.textbbox((0, 0), "Gano iTouch Oficial • Red de Mercadeo • Bienestar", font=fuente_logo)
    x_logo = (ancho - (bbox_logo[2] - bbox_logo[0])) / 2
    # Fondo solido diminuto en la base
    draw.rectangle([(0, 1020), (ancho, alto)], fill=(15, 15, 15, 255))
    draw.text((x_logo, 1035), "Gano iTouch Oficial • Red de Mercadeo • Bienestar", font=fuente_logo, fill=(240, 240, 240))

    # EXPORTACIÓN GIGANTE (Calidad 98 sobre 100)
    carpeta_destino = os.path.join("imagenes", categoria)
    os.makedirs(carpeta_destino, exist_ok=True)
    ruta = os.path.join(carpeta_destino, f"post_{index}.jpg")
    
    img_final = img.convert("RGB")
    img_final.save(ruta, quality=98)
    return ruta

def arrancar_la_fabrica():
    print("==================================================")
    print("  SINERGIA AUTO-CREATOR (FABRICA DE CONTENIDOS)   ")
    print("==================================================\n")
    
    # Sanación: Limpieza completa de cualquier archivo duplicado anterior de estilo viejo
    print(">> [Sanación] Limpiando archivos duplicados con marcas de tiempo antiguas...")
    for cat in ["salud", "negocio"]:
        dir_cat = os.path.join("imagenes", cat)
        if os.path.exists(dir_cat):
            for file in os.listdir(dir_cat):
                if file.startswith("hq_dynamic_post_") or file.endswith(".temp"):
                    try:
                        os.remove(os.path.join(dir_cat, file))
                    except Exception:
                        pass
                        
    print("\nGenerando material de Salud Inmunológica (Anti-Baneo Facebook)...")
    for idx, gancho_salud in enumerate(HOOKS_SALUD):
        ruta = crear_tarjeta_viral(gancho_salud, "salud", idx)
        print(f" [OK] Gráfico Salud creado: {ruta}")
        
    print("\nGenerando material de Libertad Financiera (Network Marketing)...")
    for idx, gancho_negocio in enumerate(HOOKS_NEGOCIO):
        ruta = crear_tarjeta_viral(gancho_negocio, "negocio", idx)
        print(f" [OK] Gráfico Negocio creado: {ruta}")
        
    print("\n[ÉXITO] ¡14 Nuevos Archivos Publicitarios inyectados en la base rotativa!")
    print("Ahora Sinergia Bot (publisher.py) los agarrará y programará sin que muevas un dedo.")

if __name__ == "__main__":
    arrancar_la_fabrica()
