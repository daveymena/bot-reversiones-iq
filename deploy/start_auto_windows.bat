@echo off
title TRADING BOT - AUTO RESTART
:loop
echo =================================================
echo   INICIANDO BOT DE TELEGRAM - MODO PERSISTENTE
echo =================================================
echo.
python main_telegram_bot.py
echo.
echo ⚠️ El bot se ha cerrado. Reiniciando en 5 segundos...
timeout /t 5
goto loop
