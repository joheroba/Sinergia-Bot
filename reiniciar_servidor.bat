@echo off
color 0B
echo =======================================================
echo    REINICIANDO MOTOR DE SINERGIA BOT EN EL SERVIDOR CLOUD
echo =======================================================
echo.
echo Conectando con el servidor primario: 45.55.92.211...
echo Escribe tu contrasena maestra del servidor cuando te la solicite y dale ENTER.
echo.

ssh -o StrictHostKeyChecking=no root@45.55.92.211 "cd /root/GanoiTouch && bash restart.sh"

echo.
echo =======================================================
echo       COMANDO DE REINICIO REMOTO FINALIZADO 🚀
echo =======================================================
echo El bot ya esta operando en segundo plano en la nube.
echo.
pause
