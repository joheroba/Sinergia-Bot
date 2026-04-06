@echo off
title Asistente Gano iTouch [Onboarding - Fase 3]
color 1F
echo Validando entorno vital de Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python no esta instalado en tu maquina. Pidele ayuda a tu lider para instalarlo.
    pause
    exit /b
)
python setup.py
