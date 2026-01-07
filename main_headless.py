#!/usr/bin/env python3
"""
Bot de Trading Headless (sin GUI) para deployment en servidores
"""
import sys
import time
import signal
from datetime import datetime
from core.trader import LiveTrader
from data.market_data import MarketDataManager
import config

# Variable global para control de shutdown
running = True

def signal_handler(sig, frame):
    """Manejo de señales para shutdown graceful"""
    global running
    print("\n🛑 Señal de shutdown recibida. Cerrando bot...")
    running = False

def main():
    global running
    
    # Registrar handlers de señales
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("=" * 60)
    print("🤖 BOT DE TRADING EXNOVA - MODO HEADLESS")
    print("=" * 60)
    print(f"📅 Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🏦 Broker: {config.BROKER_NAME}")
    print(f"💼 Cuenta: {config.ACCOUNT_TYPE}")
    print(f"💰 Capital por trade: ${config.CAPITAL_PER_TRADE}")
    print(f"🎯 Activo: {config.DEFAULT_ASSET}")
    print("=" * 60)
    
    # Inicializar componentes
    try:
        market_data = MarketDataManager()
        
        # Conectar al broker
        print("\n🔌 Conectando al broker...")
        if not market_data.connect():
            print("❌ Error: No se pudo conectar al broker")
            return 1
        
        print("✅ Conectado exitosamente")
        
        # Crear trader
        trader = LiveTrader(market_data)
        
        # Iniciar trading
        print("\n🚀 Iniciando trading automático...")
        print("💡 Presiona Ctrl+C para detener\n")
        
        trader.start()
        
        # Loop principal
        while running:
            time.sleep(1)
            
            # Mostrar estado cada 60 segundos
            if int(time.time()) % 60 == 0:
                balance = market_data.get_balance()
                print(f"💰 Balance: ${balance:.2f} | Activo: {trader.current_asset}")
        
        # Shutdown graceful
        print("\n🛑 Deteniendo trader...")
        trader.stop()
        trader.wait()
        
        market_data.disconnect()
        print("✅ Bot detenido correctamente")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
