import os
import subprocess
import base64
import sys

# Configuración y Rutas
BASE_DIR = r"C:\Users\Usuario1\.gemini\antigravity\scratch\AethelOS\marketing"
INKSCAPE_PATH = r"C:\Program Files\Inkscape\bin\inkscape.exe"

# Simulamos la carpeta segura del VPS
VPS_ASSETS_DIR = os.path.join(BASE_DIR, "official_assets_vps_mock")

# --- MOTOR DE CUMPLIMIENTO (COMPLIANCE ENGINE) ---
class MotorCumplimiento:
    PALABRAS_PROHIBIDAS = ["cura", "medicina", "enfermedad", "remedio", "milagroso", "sana"]
    
    @staticmethod
    def validar_texto(contexto):
        """Revisa que el copy del anuncio no contenga lenguaje no permitido."""
        textos = " ".join([str(v).lower() for v in contexto.values()])
        for palabra in MotorCumplimiento.PALABRAS_PROHIBIDAS:
            if palabra in textos:
                raise ValueError(f"Violacion de Compliance: El texto contiene la palabra prohibida '{palabra}'.")
        print(">> Compliance OK: Textos validados. Cero afirmaciones curativas.")

    @staticmethod
    def validar_origen_imagen(ruta_imagen):
        """Revisa que la imagen provenga estrictamente del repositorio oficial aprobado."""
        ruta_absoluta_img = os.path.abspath(ruta_imagen)
        ruta_absoluta_vps = os.path.abspath(VPS_ASSETS_DIR)
        
        if not ruta_absoluta_img.startswith(ruta_absoluta_vps):
            raise ValueError("Violacion de Compliance: La imagen no proviene del repositorio oficial VPS aprobado.")
        print(">> Compliance OK: Asset visual originario del servidor oficial.")

# --- GENERADOR ---
def image_to_base64(img_path):
    with open(img_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    return f"data:image/png;base64,{encoded_string}"

def generar_svg(contexto, img_base64):
    """Genera el codigo SVG inyectando el sello obligatorio de Distribuidor Independiente."""
    
    svg_template = f"""<svg width="1080" height="1080" viewBox="0 0 1080 1080" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <linearGradient id="bg-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#1e293b" />
                <stop offset="50%" stop-color="#0f172a" />
                <stop offset="100%" stop-color="#54190b" />
            </linearGradient>
            
            <filter id="glow">
                <feGaussianBlur stdDeviation="5" result="coloredBlur"/>
                <feMerge>
                    <feMergeNode in="coloredBlur"/>
                    <feMergeNode in="SourceGraphic"/>
                </feMerge>
            </filter>
        </defs>

        <!-- Fondo -->
        <rect width="1080" height="1080" fill="url(#bg-grad)" />

        <!-- Círculo decorativo -->
        <circle cx="800" cy="200" r="400" fill="#d4af37" opacity="0.1" />

        <!-- Imagen del Producto -->
        <rect x="500" y="250" width="500" height="600" rx="30" fill="rgba(255,255,255,0.05)" stroke="rgba(255,255,255,0.2)" stroke-width="2"/>
        <image href="{img_base64}" x="520" y="270" width="460" height="560" preserveAspectRatio="xMidYMid slice" />

        <!-- Textos Promocionales -->
        <text x="80" y="300" font-family="Arial, sans-serif" font-size="40" font-weight="bold" fill="#d4af37" letter-spacing="2">
            {contexto.get('empresa', '').upper()}
        </text>

        <text x="80" y="400" font-family="Arial, sans-serif" font-size="80" font-weight="900" fill="#ffffff">
            DESCUBRE EL
        </text>
        <text x="80" y="490" font-family="Arial, sans-serif" font-size="80" font-weight="900" fill="#d4af37" filter="url(#glow)">
            VERDADERO PODER
        </text>

        <text x="80" y="580" font-family="Arial, sans-serif" font-size="35" fill="#94a3b8" width="400">
            <tspan x="80" dy="0">{contexto.get('producto', '')}</tspan>
            <tspan x="80" dy="50">Mas de 200 fitonutrientes y</tspan>
            <tspan x="80" dy="50">150 antioxidantes en cada taza.</tspan>
        </text>

        <!-- SELLO DE CUMPLIMIENTO OBLIGATORIO (HARDCODED) -->
        <rect x="700" y="40" width="350" height="50" rx="10" fill="#ffffff" opacity="0.9" />
        <text x="875" y="73" font-family="Arial, sans-serif" font-size="20" font-weight="bold" fill="#cc0000" text-anchor="middle">
            DISTRIBUIDOR INDEPENDIENTE
        </text>

        <!-- Insignia Sinergia Pro -->
        <rect x="80" y="700" width="400" height="80" rx="40" fill="#6366f1" />
        <text x="280" y="750" font-family="Arial, sans-serif" font-size="30" font-weight="bold" fill="#ffffff" text-anchor="middle">
            {contexto.get('eslogan_proyecto', '')}
        </text>

        <!-- CTA -->
        <rect x="80" y="850" width="920" height="100" rx="20" fill="rgba(255,255,255,0.1)" stroke="rgba(255,255,255,0.3)" />
        <text x="540" y="910" font-family="Arial, sans-serif" font-size="40" font-weight="bold" fill="#ffffff" text-anchor="middle">
            {contexto.get('llamado_accion', '')}
        </text>
    </svg>"""
    return svg_template

def ejecutar_motor(modo_prueba="exito"):
    print(f"\n--- INICIANDO GANOIBOT (Modo: {modo_prueba}) ---")
    
    # Contexto por defecto
    contexto_proyecto = {
        "empresa": "Gano iTouch",
        "producto": "Cafe Saludable con Ganoderma Lucidum",
        "eslogan_proyecto": "Sinergia Pro - El Sistema de Duplicacion",
        "llamado_accion": "Envia 'INFO' por DM"
    }
    
    imagen_a_usar = os.path.join(VPS_ASSETS_DIR, "pioir_coffee.png")

    # Forzar errores si estamos probando el Compliance Engine
    if modo_prueba == "fallo_texto":
        contexto_proyecto["producto"] = "El cafe que cura cualquier enfermedad."
    elif modo_prueba == "fallo_imagen":
        # Usamos una imagen fuera del VPS (ej: descargas del usuario)
        imagen_a_usar = r"C:\Users\Usuario1\Downloads\cafe_falso.png"

    try:
        # 1. PASAR POR EL MOTOR DE CUMPLIMIENTO
        print("Auditando con Motor de Cumplimiento...")
        MotorCumplimiento.validar_texto(contexto_proyecto)
        MotorCumplimiento.validar_origen_imagen(imagen_a_usar)
        
        # 2. PROCESAR SI TODO ESTA OK
        print("Auditoria Superada. Procediendo al renderizado...")
        img_base64 = image_to_base64(imagen_a_usar)
        svg_code = generar_svg(contexto_proyecto, img_base64)
        svg_filename = os.path.join(BASE_DIR, "post_compliance.svg")
        
        with open(svg_filename, "w", encoding="utf-8") as f:
            f.write(svg_code)
            
        png_filename = os.path.join(BASE_DIR, "post_compliance.png")
        
        comando = [
            INKSCAPE_PATH,
            svg_filename,
            "--export-type=png",
            f"--export-filename={png_filename}",
            "-w", "1080",
            "-h", "1080"
        ]
        subprocess.run(comando, check=True, capture_output=True, text=True)
        print(f"EXITO: Imagen renderizada y protegida por politicas corporativas en -> {png_filename}")

    except Exception as e:
        print(f"!!! ALERTA DE SEGURIDAD (EJECUCION ABORTADA) !!!\nMotivo: {str(e)}")

if __name__ == "__main__":
    modo = "exito"
    if len(sys.argv) > 1:
        modo = sys.argv[1]
    ejecutar_motor(modo)
