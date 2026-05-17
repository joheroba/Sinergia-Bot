from PIL import Image
import os

def brandear_imagen(ruta_base, ruta_logo="imagenes/logo_autorizado.png", salida=None):
    """
    Toma una imagen base y le estampa el logo oficial en la esquina inferior derecha.
    """
    if not salida:
        nombre, ext = os.path.splitext(ruta_base)
        salida = f"{nombre}_branded{ext}"

    if not os.path.exists(ruta_logo):
        print(f"Advertencia: No se encontró el logo en {ruta_logo}. Se usará la imagen original.")
        return ruta_base

    base = Image.open(ruta_base).convert("RGBA")
    logo = Image.open(ruta_logo).convert("RGBA")
    
    # Redimensionar logo al 20% del ancho de la base para que se vea bien pero no estorbe
    base_w, base_h = base.size
    logo_w, logo_h = logo.size
    nuevo_w = int(base_w * 0.20)
    nuevo_h = int(logo_h * (nuevo_w / logo_w))
    logo = logo.resize((nuevo_w, nuevo_h), Image.Resampling.LANCZOS)
    
    # Calcular posición (Abajo a la derecha con 20px de margen)
    pos_x = base_w - nuevo_w - 20
    pos_y = base_h - nuevo_h - 20
    
    # Estampar
    base.paste(logo, (pos_x, pos_y), logo)
    
    # Guardar como RGB (JPEG/PNG)
    base.convert("RGB").save(salida)
    print(f">> [Brandeo] Imagen guardada con éxito en: {salida}")
    return salida

if __name__ == "__main__":
    # Prueba rápida
    brandear_imagen("imagenes/bebibles/muestra.jpg")
