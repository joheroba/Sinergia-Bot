@echo off
echo ==============================================
echo        INICIADOR DE SINERGIA GANO BOT
echo ==============================================
echo.

echo [1/4] Verificando conexion a internet...
ping -n 1 8.8.8.8 >nul
if errorlevel 1 (
    echo [ERROR] No hay conexion a internet.
    echo Por favor, conéctate a una red Wi-Fi o cableada e intenta de nuevo.
    pause
    exit /b
)
echo [OK] Conexion exitosa.
echo.

echo [2/4] Instalando paquetes de Python (pip)...
pip install -r requirements.txt
echo [OK] Paquetes de Python instalados.
echo.

echo [3/4] Instalando motor de navegador (Chromium)...
playwright install chromium
echo [OK] Navegador instalado.
echo.

echo [4/4] Levantando el Bot automatizador...
echo.
python publisher.py

echo.
echo Procesos finalizados.
pause
