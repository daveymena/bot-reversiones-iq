"""
Trading Bot Pro - Telegram Signal Integrator
Escucha señales de Telegram y las ejecuta automáticamente en el broker
"""

import sys
import asyncio
import time
import signal
from datetime import datetime, timedelta
from config import Config
from data.market_data import MarketDataHandler
from core.telegram_listener import TelegramListener
from core.risk import RiskManager

# Variable global para manejo de cierre
running = True

def signal_handler(sig, frame):
    """Maneja Ctrl+C para cerrar limpiamente"""
    global running
    print("\n\n🛑 Deteniendo bot de señales...")
    running = False

async def main():
    """Función principal asíncrona"""
    global running
    
    print("\n" + "="*60)
    print("🚀 TRADING BOT PRO - TELEGRAM AUTO-TRADE")
    print("="*60)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Broker: {Config.BROKER_NAME.upper()}")
    print(f"Modo: {Config.ACCOUNT_TYPE}")
    print("="*60 + "\n")

    # 1. Inicializar componentes de Trading
    print("📦 Inicializando componentes de trading...")
    market_data = MarketDataHandler(
        broker_name=Config.BROKER_NAME,
        account_type=Config.ACCOUNT_TYPE
    )
    
    risk_manager = RiskManager(
        Config.CAPITAL_PER_TRADE, 
        Config.STOP_LOSS_PERCENT, 
        Config.TAKE_PROFIT_PERCENT, 
        max_martingale_steps=Config.MAX_MARTINGALE
    )

    # 2. Conectar al broker
    print(f"🔌 Conectando a {Config.BROKER_NAME.upper()}...")
    email = Config.EXNOVA_EMAIL if Config.BROKER_NAME == "exnova" else Config.IQ_OPTION_EMAIL
    password = Config.EXNOVA_PASSWORD if Config.BROKER_NAME == "exnova" else Config.IQ_OPTION_PASSWORD
    
    if not market_data.connect(email, password):
        print("❌ Error fatal: No se pudo conectar al broker. Verifica tu .env")
        return

    balance = market_data.get_balance()
    print(f"✅ Conectado | Balance actual: ${balance:.2f}\n")

    # 3. Definir Callback para señales INTELIGENTE
    from core.smart_signal_parser import SmartSignalParser
    
    # Intentar cargar parser inteligente
    try:
        smart_parser = SmartSignalParser()
        print("🧠 Cerebro IA (Groq) ACTIVADO para análisis de señales")
    except Exception as e:
        print(f"⚠️ No se pudo cargar IA: {e}")
        smart_parser = None

    async def process_telegram_signal(signal_data):
        """Procesa la señal usando, si es posible, el cerebro inteligente"""
        try:
            # Si tenemos parser inteligente, re-analizamos el mensaje completo
            # para capturar matices como "Hora exacta: 21:11"
            if smart_parser and 'raw_message' in signal_data:
                print("🧠 Analizando mensaje con IA...")
                ai_signal = smart_parser.parse_with_ai(signal_data['raw_message'])
                
                if ai_signal:
                    print(f"🔍 IA detectó: {ai_signal}")
                    
                    # Usar datos de la IA si son válidos
                    if ai_signal.get('asset'): signal_data['asset'] = ai_signal['asset']
                    if ai_signal.get('direction'): signal_data['direction'] = ai_signal['direction']
                    if ai_signal.get('expiration'): signal_data['expiration'] = ai_signal['expiration']
                    
                    # Lógica de espera inteligente
                    wait_seconds = ai_signal.get('seconds_to_wait', 0)
                    if wait_seconds > 0:
                        target_time = datetime.now() + timedelta(seconds=wait_seconds)
                        print(f"⏳ SEÑAL PROGRAMADA: Esperando {wait_seconds}s hasta las {target_time.strftime('%H:%M:%S')}...")
                        await asyncio.sleep(wait_seconds)
                        print("⏰ TIEMPO CUMPLIDO: Ejecutando ahora!")
            
            # Ejecución normal (ahora o después de la espera)
            asset = signal_data['asset']
            direction = signal_data['direction']
            expiration = signal_data['expiration']
            
            print(f"\n⚡ EJECUTANDO: {asset} | {direction.upper()} | {expiration} min")
            
            amount = risk_manager.get_trade_amount()
            
            # Ejecutar en broker
            success, order_id = market_data.api.buy(
                amount,
                asset,
                direction,
                expiration
            )
            
            if success:
                print(f"✅ OPERACIÓN ABIERTA - ID: {order_id}")
            else:
                print(f"❌ Error al abrir operación: {order_id}")
                
        except Exception as e:
            print(f"❌ Error procesando señal: {e}")

    # 4. Inicializar Telegram Listener
    if Config.TELEGRAM_API_ID == 0 or not Config.TELEGRAM_API_HASH:
        print("❌ ERROR: No has configurado las credenciales de Telegram en el archivo .env")
        print("Necesitas TELEGRAM_API_ID y TELEGRAM_API_HASH de https://my.telegram.org")
        return

    print("📱 Iniciando cliente de Telegram...")
    listener = TelegramListener(
        api_id=Config.TELEGRAM_API_ID,
        api_hash=Config.TELEGRAM_API_HASH,
        phone=Config.TELEGRAM_PHONE,
        session_name=Config.TELEGRAM_SESSION_NAME,
        signal_callback=process_telegram_signal
    )

    try:
        # Iniciar conexión a Telegram
        await listener.start()
        
        # Iniciar escucha de mensajes
        # Usamos Config.TELEGRAM_CHATS que definimos antes
        await listener.listen(Config.TELEGRAM_CHATS)
        
    except Exception as e:
        print(f"❌ Error en el listener de Telegram: {e}")
    finally:
        await listener.stop()
        print("👋 Bot de señales finalizado.")

if __name__ == "__main__":
    # Configurar cierre limpio
    import signal
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("\n👋 Cerrando por usuario...")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
