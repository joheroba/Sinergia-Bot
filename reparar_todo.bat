@echo off
color 0A
echo =======================================================
echo          LIMPIEZA DE CACHE Y REINICIO FINAL
echo =======================================================
echo.
echo Se borraran las caches de afiliados para forzar el
echo nuevo enlace con Gano Excel.
echo.

echo 1. Limpiando afiliados.json en el servidor...
ssh -o StrictHostKeyChecking=no root@45.55.92.211 "rm -f /root/GanoiTouch/afiliados.json"

echo.
echo 2. Subiendo logica reparada y configuracion .env...
scp -o StrictHostKeyChecking=no c:\GanoiTouch\telegram_manager.py c:\GanoiTouch\.env c:\GanoiTouch\restart_ninja.sh root@45.55.92.211:/root/GanoiTouch/

echo.
echo 3. Reiniciando servidor sin borrar parches...
ssh -o StrictHostKeyChecking=no root@45.55.92.211 "cd /root/GanoiTouch && bash restart_ninja.sh"

echo.
echo =======================================================
echo    TODO LISTO. Ve a Telegram y escribe /start
echo =======================================================
pause
