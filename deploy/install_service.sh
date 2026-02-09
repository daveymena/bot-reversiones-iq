#!/bin/bash

# Script de instalación automática para el servicio del Bot
# Ejecutar con: sudo bash deploy/install_service.sh

echo "🚀 Configurando Bot como Servicio del Sistema..."

# 1. Obtener directorio actual
current_dir=$(pwd)
echo "📂 Directorio detectado: $current_dir"

# 2. Instalar dependencias si faltan
echo "📦 Verificando dependencias Python..."
pip3 install telethon groq

# 3. Crear archivo de servicio dinámico
echo "⚙️  Generando configuración systemd..."
cat > /etc/systemd/system/tradingbot.service <<EOF
[Unit]
Description=Trading Bot Telegram - Auto Signals
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$current_dir
ExecStart=$(which python3) main_telegram_bot.py
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

# 4. Recargar demonio y activar
echo "🔄 Recargando systemd..."
systemctl daemon-reload
systemctl enable tradingbot.service
systemctl start tradingbot.service

echo "✅ ¡INSTALACIÓN COMPLETADA!"
echo "📊 Para ver el estado: systemctl status tradingbot"
echo "📜 Para ver logs: journalctl -u tradingbot -f"
