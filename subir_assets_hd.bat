@echo off
color 0E
echo =======================================================
echo          SINERGIA BOT - SINCRONIZADOR DE ASSETS HD     
echo =======================================================
echo.
echo Enviando carpeta de imagenes de alta calidad y logos oficiales...
echo Servidor Destino: 45.55.92.211
echo.

scp -o StrictHostKeyChecking=no -r assets_oficiales root@45.55.92.211:/root/GanoiTouch/

echo.
echo =======================================================
echo    ¡TODOS LOS ASSETS HD ACTUALIZADOS EN EL SERVIDOR!
echo =======================================================
pause
