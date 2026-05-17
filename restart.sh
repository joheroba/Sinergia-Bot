#!/bin/bash
echo "====================================================="
echo "      REINICIADOR AUTOMÁTICO DE SINERGIA BOT         "
echo "====================================================="
echo ""
echo ">> 1. Jalando la última lógica desde GitHub..."
git pull origin main

echo ""
echo ">> 2. Deteniendo procesos antiguos de Telegram..."
pkill -f telegram_manager.py
sleep 1

echo ""
echo ">> 3. Iniciando Sinergia Bot Multi-Afiliado en segundo plano..."
nohup python3 -u telegram_manager.py > telegram.log 2>&1 &

echo ""
echo ">> ¡PROCESO DE REINICIO CON COMPLETO ÉXITO! 🚀"
echo "Para monitorear los logs del bot en tiempo real, corre:"
echo "tail -f telegram.log"
