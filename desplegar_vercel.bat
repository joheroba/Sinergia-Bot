@echo off
color 0B
echo =======================================================
echo          SINERGIA BOT - DESPLIEGUE MASIVO A VERCEL     
echo =======================================================
echo.
echo Este script abrira una terminal interactiva para que puedas
echo iniciar sesion en Vercel (si es necesario) y desplegar tu
echo Plan Servilleta Interactivo en 5 segundos.
echo.

cd vercel_deploy
echo [1/2] Refrescando sesion de Vercel en tu navegador...
call npx -y vercel login

echo.
echo [2/2] Desplegando tu aplicacion en Vercel...
call npx -y vercel --prod

echo.
echo =======================================================
echo    ¡PROCESO DE DESPLIEGUE A VERCEL FINALIZADO!
echo =======================================================
pause
