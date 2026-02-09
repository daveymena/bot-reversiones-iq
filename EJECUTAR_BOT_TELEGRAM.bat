@echo off
title TRADING BOT PRO - AUTO TELEGRAM
echo ===================================================
echo   INICIANDO BOT DE TRADING CON SEÑALES TELEGRAM
echo ===================================================
:: Verificar si Telethon está instalado
python -c "import telethon" 2>nul
if %errorlevel% neq 0 (
    echo Instalando Telethon...
    pip install telethon
)

:: Ejecutar el bot
python main_telegram_bot.py
pause
