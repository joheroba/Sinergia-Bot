#!/bin/bash
# =======================================================
#    INICIADOR DE PANTALLA WEB (noVNC) - SINERGIA CLOUD   
# =======================================================
#
# Este script levanta una pantalla virtual persistente en tu servidor
# y crea un puente web seguro para que puedas ver el navegador del bot
# directamente desde tu Google Chrome o Microsoft Edge.

echo "=== 1. Verificando e instalando componentes visuales ==="
apt-get update -y
apt-get install -y xvfb x11vnc novnc websockify

# Matar procesos antiguos de visualización si quedaron colgados
echo ">> Limpiando sesiones previas..."
killall -9 Xvfb x11vnc websockify 2>/dev/null
sleep 2

echo ""
echo "=== 2. Iniciando Monitor Virtual Persistente (Display :99) ==="
# Creamos la pantalla virtual con una resolución estándar estable
Xvfb :99 -screen 0 1280x720x24 &
export DISPLAY=:99
sleep 2

echo ""
echo "=== 3. Lanzando Transmisor de Pantalla (x11vnc) ==="
# Compartimos la pantalla virtual sin requerir claves engorrosas por red local
x11vnc -display :99 -forever -nopw -shared -bg -rfbport 5900 &
sleep 2

echo ""
echo "=== 4. Activando el Puente Web Seguro (noVNC en puerto 6080) ==="
# Levantamos el servidor web que traduce la señal para tu navegador
websockify --web /usr/share/novnc/ 6080 localhost:5900 &
sleep 3

echo ""
echo "======================================================="
echo "   ¡PANTALLA WEB SINERGIA INICIADA CORRECTAMENTE!      "
echo "======================================================="
echo ""
echo "Para ver la pantalla de tu bot en tu navegador Chrome:"
echo ""
echo "1. En tu computadora local, abre una terminal de PowerShell y corre este Túnel:"
echo "   👉 ssh -L 6081:localhost:6080 root@45.55.92.211"
echo "   (e ingresa la contraseña de tu servidor)"
echo ""
echo "2. En tu navegador web, entra a esta dirección:"
echo "   👉 http://localhost:6081/vnc.html"
echo ""
echo "3. Haz clic en el botón azul 'Connect' y ¡LISTO! Verás la pantalla en vivo."
echo "======================================================="
