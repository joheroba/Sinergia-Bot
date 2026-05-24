@echo off
color 0A
echo =======================================================
echo          DESPLIEGUE A PRODUCCION (DIGITALOCEAN)
echo =======================================================
echo.
echo 1. Subiendo ultimos cambios a GitHub (Backup local)...
git add .
git commit -m "Auto-Deploy a Produccion"
git push

echo.
echo 2. Conectando al servidor VPS para descargar los cambios...
ssh -o StrictHostKeyChecking=no root@45.55.92.211 "cd /root/GanoiTouch && git pull origin main && pip install -r requirements.txt"

echo.
echo 3. Reiniciando los servicios (API, WhatsApp, Telegram)...
ssh -o StrictHostKeyChecking=no root@45.55.92.211 "cd /root/GanoiTouch && bash restart_ninja.sh"

echo.
echo =======================================================
echo    DESPLIEGUE COMPLETADO. SISTEMA EN PRODUCCION.
echo =======================================================
pause
