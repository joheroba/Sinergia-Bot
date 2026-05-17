@echo off
color 0B
echo =======================================================
echo          SINERGIA BOT - ACTUALIZACION VELOZ (NINJA)    
echo =======================================================
echo.
echo Enviando SOLO la logica y configuracion (archivos livianos)...
echo Servidor Destino: 45.55.92.211
echo.

:: Enviamos solo archivos sueltos .py, .json, .html y el .env de la raiz
scp -o StrictHostKeyChecking=no *.py *.json *.html .env root@45.55.92.211:/root/GanoiTouch/

echo.
echo =======================================================
echo    LOGICA ACTUALIZADA INSTANTANEAMENTE.
echo =======================================================
pause
