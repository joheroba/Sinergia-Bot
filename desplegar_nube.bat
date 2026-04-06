@echo off
color 0A
echo =======================================================
echo          SINERGIA BOT - MOTOR DE DESPLIEGUE CLOUD      
echo =======================================================
echo.
echo Transfiriendo toda la base de datos visual y el codigo fuente...
echo Hacia el Servidor Primario: 45.55.92.211
echo.
echo ATENCION PELIGRO: 
echo El servidor te va a pedir tu contraseña maestra justo abajo.
echo Escribela despacio y dale ENTER. (Recuerda: NO se veran asteriscos *).
echo.

scp -o StrictHostKeyChecking=no -r C:\GanoiTouch root@45.55.92.211:/root/

echo.
echo =======================================================
echo    MIGRACION FINALIZADA. VERIFICA SI HUBO ALGUN ERROR.
echo =======================================================
pause
