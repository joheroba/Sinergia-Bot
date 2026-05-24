#!/bin/bash
echo "====================================================="
echo "      REINICIO NINJA (SIN GIT RESET)                 "
echo "====================================================="
echo ""
echo ">> 1. Deteniendo procesos antiguos..."
pkill -f telegram_manager.py
pkill -f api_mobile.py
pkill -f whatsapp_bot.py
sleep 2

echo ""
echo ">> 2. Iniciando Servidor API y Telegram..."
nohup python3 -u api_mobile.py > api_mobile.log 2>&1 &
sleep 2

echo ">> 3. Iniciando Bot de WhatsApp (Playwright)..."
nohup python3 -u whatsapp_bot.py > whatsapp.log 2>&1 &

echo ""
echo ">> ¡PROCESO DE REINICIO CON COMPLETO ÉXITO! 🚀"
