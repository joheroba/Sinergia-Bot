#!/bin/bash
echo "====================================================="
echo "      REINICIO NINJA (SIN GIT RESET)                 "
echo "====================================================="
echo ""
echo ">> 1. Deteniendo procesos antiguos de Telegram..."
pkill -f telegram_manager.py
sleep 1

echo ""
echo ">> 2. Iniciando Sinergia Bot Multi-Afiliado en segundo plano..."
nohup python3 -u telegram_manager.py > telegram.log 2>&1 &

echo ""
echo ">> ¡PROCESO DE REINICIO CON COMPLETO ÉXITO! 🚀"
