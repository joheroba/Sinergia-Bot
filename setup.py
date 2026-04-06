import os
import time

def limpiar_pantalla():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    limpiar_pantalla()
    print("==========================================================")
    print("   BIENVENIDO A SINERGIA GANO ITOUCH (BOT AUTOMATIZADO)   ")
    print("==========================================================")
    print("Preparando el entorno comercial de tu computadora.\n")
    
    print("[1] SEGURIDAD: FANPAGE OBLIGATORIA")
    print("Meta/Facebook castiga estrictamente la venta en perfiles personales normales.")
    print("El Bot está entrenado para publicar en la seguridad de Meta Business Suite (Páginas Oficiales).")
    resp = input("¿Ya tienes una Página (FanPage) creada y activa en Facebook? (si/no): ").strip().lower()

    if resp != 'si' and resp != 's':
        print("\n=> ACCIÓN OBLIGATORIA REQUERIDA:")
        print("Antes de usar el Sinergia Bot, debes crear tu Página de Negocios gratuitamente aquí:")
        print("----> https://www.facebook.com/pages/create/?ref_type=launch_point")
        print("Termina el proceso de Facebook y vuelve a encender este asistente.")
        print("Saliendo en 15 segundos...")
        time.sleep(15)
        return
        
    print("\n[2] EL NOMBRE EXACTO DE TU FANPAGE")
    print("Escribe el nombre EXACTO de la página tal cual aparece arriba a la izquierda en tu Business Suite.")
    print("El bot usará este nombre para buscarla visualmente. (Ejemplo: Gano Excel)")
    nombre_pagina = input("Escribe el Nombre de tu Negocio en FB: ").strip()
    
    print("\n[3] DIRECCIÓN DE TU TIENDA OFICIAL (PÁGINA REPLICADA)")
    print("Aquí redireccionaremos el llamado a la acción. Pegarás el link Gano iTouch tuyo.")
    print("Ejemplo: https://peru.ganoitouch.biz/joherobacafe")
    url_tienda = input("Tu Enlace Replicado: ").strip()
    
    # Escribir el .env (configuración oculta del sistema)
    try:
        with open(".env", "w", encoding="utf-8") as env_file:
            # Sobrescribe el .env para dejar listo a este afiliado de forma personalizada
            env_file.write(f"FACEBOOK_PAGE_NAME={nombre_pagina}\n")
            env_file.write(f"GANO_ITOUCH_STORE={url_tienda}\n")
        
        print("\n==========================================================")
        print("  ¡ÉXITO DIAMANTE! TU BOT AHORA ES ÚNICO.                 ")
        print("==========================================================")
        print("Ve a la carpeta 'imagenes' y llena las subcarpetas con tus fotitos.")
        print("Ya puedes iniciar las publicaciones automáticas con 'python publisher.py'.")
    except Exception as e:
        print(f"\nHubo un error guardándolo: {e}")
        
    input("\nPresiona la tecla Enter para cerrar este programa asistente...")

if __name__ == "__main__":
    main()
