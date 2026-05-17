#!/bin/bash
# =======================================================
#      RUSTDESK AUTOMATED INSTALLER - SINERGIA CLOUD      
# =======================================================
#
# Este script descarga, instala y configura RustDesk para 
# que puedas conectarte visualmente a la máquina virtual (DigitalOcean)
# sin necesidad de programar servidores VNC ni capturas de pantalla complejas.

echo "=== 1. Actualizando paquetes y dependencias del sistema ==="
apt-get update -y
apt-get install -y wget gdebi-core x11-xserver-utils xdotool

echo ""
echo "=== 2. Descargando paquete oficial de RustDesk ==="
# Descargamos la versión estable de 64 bits para Debian/Ubuntu
wget https://github.com/rustdesk/rustdesk/releases/download/1.2.3-2/rustdesk-1.2.3-2-x86_64.deb -O /tmp/rustdesk.deb

echo ""
echo "=== 3. Instalando RustDesk y reparando dependencias ==="
dpkg -i /tmp/rustdesk.deb
apt-get install -f -y

echo ""
echo "=== 4. Configurando Acceso Seguro y Contraseña Estática ==="
# Configuramos la contraseña estática del Bunker para que no tengas que adivinar claves dinámicas
rustdesk --password "SinergiaBunker2026"

echo ""
echo "======================================================="
echo "   ¡RUSTDESK INSTALADO CON ÉXITO EN LA NUBE!           "
echo "======================================================="
echo ""
echo "Usa estos datos en tu cliente de RustDesk de Windows:"
echo ""
echo "👉 ID de la VM: "
rustdesk --get-id
echo "👉 Contraseña: SinergiaBunker2026"
echo ""
echo "======================================================="
