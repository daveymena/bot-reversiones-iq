# 🤖 Bot de Trading - Módulo Telegram

Este módulo permite que tu bot escuche automáticamente señales de grupos o canales de Telegram (incluso si no eres administrador) y opere en Exnova/IQ Option al instante.

## 📋 Requisitos Previos

1. Tener una cuenta de Telegram.
2. Obtener tus credenciales de API (es gratis y oficial de Telegram).

### ¿Cómo obtener API_ID y API_HASH?
1. Ve a **[my.telegram.org](https://my.telegram.org)** e inicia sesión con tu número de teléfono.
2. Ve a la sección **"API development tools"**.
3. Crea una nueva aplicación (si no tienes una):
   - **App title:** TradingBot (o lo que quieras)
   - **Short name:** tradingbot
   - **Platform:** Desktop
   - **Description:** Bot para automatizar trading personal
4. Copia el **App api_id** y el **App api_hash**.

## ⚙️ Configuración

Abre el archivo `.env` en la carpeta del proyecto y agrega (o edita) estas líneas:

```env
# Telegram
TELEGRAM_API_ID=12345678              <-- Tu API ID
TELEGRAM_API_HASH=tucodigolargo...    <-- Tu API HASH
TELEGRAM_PHONE=+573001234567          <-- Tu número con código de país
TELEGRAM_SESSION_NAME=trading_session 
TELEGRAM_CHATS=@canal_señales,-100123456789   <-- Lista separada por comas
```

## 🚀 Ejecución

### Opción 1: Modo Prueba de Señales (Recomendado primero)
Ejecuta este script para ver si el bot está leyendo bien los mensajes de tu grupo sin operar dinero real.

```bash
python test_telegram_signals.py
```

### Opción 2: Bot Automático (Operaciones Reales/Demo)
Ejecuta el bot principal que escucha y opera.

**En Windows:** Haz doble clic en `EJECUTAR_BOT_TELEGRAM.bat`

**En Terminal:**
```bash
python main_telegram_bot.py
```

## ⚠️ Primera vez que conectas
La primera vez que ejecutes el bot, te pedirá en la consola que ingreses el código de inicio de sesión que Telegram te enviará a tu app (en el celular o PC). Esto crea un archivo de sesión (`trading_session.session`) y no te lo volverá a pedir.

## 📝 Formatos de Señales Soportados
El bot entiende mensajes como:
- `EURUSD-OTC CALL 5 MIN`
- `VENTA GBPJPY 1M`
- `AUD/CAD PUT 3`
- `🟢 COMPRA USDJPY-OTC M5`

Si tu grupo usa un formato muy raro, avísame para ajustar el `core/signal_parser.py`.
