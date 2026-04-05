#!/usr/bin/env python3
"""
🤖 Trading Bot - Ejecución por Consola
Con Filtros Obligatorios Integrados
"""
import sys
import io
import time
import signal
from datetime import datetime

# Fix encoding para Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from config import Config
from data.market_data import MarketDataHandler
from strategies.technical import FeatureEngineer
from core.agent import RLAgent
from core.risk import RiskManager
from core.asset_manager import AssetManager
from core.trader import LiveTrader
from ai.llm_client import LLMClient

# Variable global para control de señales
trader = None

def signal_handler(sig, frame):
    """Maneja Ctrl+C para detener el bot limpiamente"""
    print("\n\n🛑 Deteniendo bot...")
    if trader:
        trader.stop()
    print("✅ Bot detenido correctamente")
    sys.exit(0)

def print_banner():
    """Muestra banner de inicio"""
    print("\n" + "="*60)
    print("🤖 TRADING BOT - MODO CONSOLA")
    print("="*60)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🏦 Broker: {Config.BROKER_NAME.upper()}")
    print(f"💼 Cuenta: {Config.ACCOUNT_TYPE}")
    print(f"💰 Capital por operación: ${Config.CAPITAL_PER_TRADE}")
    print("="*60 + "\n")

def main():
    global trader
    
    # Registrar handler para Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    print_banner()
    
    try:
        # 1. Inicializar Market Data
        print("📊 Conectando al broker...")
        market_data = MarketDataHandler(
            broker_name=Config.BROKER_NAME,
            account_type=Config.ACCOUNT_TYPE
        )
        
        # Obtener credenciales del config
        if Config.BROKER_NAME.lower() == 'exnova':
            email = Config.EXNOVA_EMAIL
            password = Config.EXNOVA_PASSWORD
        else:
            email = Config.IQ_OPTION_EMAIL
            password = Config.IQ_OPTION_PASSWORD
        
        if not market_data.connect(email, password):
            print("❌ Error: No se pudo conectar al broker")
            return
        
        print(f"✅ Conectado a {Config.BROKER_NAME.upper()}")
        
        # 2. Inicializar componentes
        print("\n🔧 Inicializando componentes...")
        
        feature_engineer = FeatureEngineer()
        print("   ✅ Feature Engineer")
        
        agent = RLAgent()
        print("   ✅ RL Agent")
        
        risk_manager = RiskManager(
            capital_per_trade=Config.CAPITAL_PER_TRADE,
            stop_loss_pct=Config.STOP_LOSS_PCT,
            take_profit_pct=Config.TAKE_PROFIT_PCT
        )
        print("   ✅ Risk Manager")
        
        asset_manager = AssetManager(market_data)
        print("   ✅ Asset Manager")
        
        # LLM Client (opcional)
        llm_client = None
        if Config.USE_LLM:
            try:
                llm_client = LLMClient()
                print("   ✅ LLM Client (Ollama)")
            except Exception as e:
                print(f"   ⚠️ LLM Client no disponible: {e}")
        
        # 3. Inicializar Trader (con filtros obligatorios integrados)
        print("\n🚀 Inicializando Trading Bot...")
        trader = LiveTrader(
            market_data=market_data,
            feature_engineer=feature_engineer,
            agent=agent,
            risk_manager=risk_manager,
            asset_manager=asset_manager,
            llm_client=llm_client
        )
        
        # Conectar señales a funciones de log
        trader.signals.log_message.connect(lambda msg: print(msg))
        trader.signals.error_message.connect(lambda msg: print(f"❌ {msg}"))
        trader.signals.balance_update.connect(lambda bal: print(f"💰 Balance: ${bal:.2f}"))
        
        print("\n" + "="*60)
        print("✅ BOT INICIADO CORRECTAMENTE")
        print("="*60)
        print("\n🛡️ FILTROS OBLIGATORIOS ACTIVOS:")
        print("   ✅ MACD debe estar alineado")
        print("   ✅ Tendencia (SMA20) debe estar alineada")
        print("   ✅ RSI en zona favorable (advertencia)")
        print("\n💡 Presiona Ctrl+C para detener el bot")
        print("="*60 + "\n")
        
        # 4. Iniciar bot en modo 24/7
        trader.running = True
        
        # Loop infinito para mantener el bot corriendo
        print("🔄 Bot operando 24/7...")
        print("📊 Monitoreando mercados...\n")
        
        while trader.running:
            try:
                # El trader.run() ya tiene su propio loop
                # Solo necesitamos mantener el proceso vivo
                trader.run()
                
                # Si run() termina, esperar un poco y reintentar
                if trader.running:
                    print("\n⚠️ Bot detenido inesperadamente, reiniciando en 5s...")
                    time.sleep(5)
            except Exception as e:
                print(f"\n❌ Error en loop principal: {e}")
                if trader.running:
                    print("⚠️ Reintentando en 10s...")
                    time.sleep(10)
                else:
                    break
        
    except KeyboardInterrupt:
        print("\n\n🛑 Deteniendo bot...")
        if trader:
            trader.stop()
        print("✅ Bot detenido correctamente")
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if market_data and market_data.connected:
            print("\n🔌 Desconectando del broker...")
            market_data.disconnect()
            print("✅ Desconectado")

if __name__ == "__main__":
    main()
