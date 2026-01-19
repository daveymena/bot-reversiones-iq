#!/usr/bin/env python3
"""
Bot de Trading Headless (Consola) - Versión Actualizada
Ejecuta la estrategia completa sin interfaz gráfica.
"""
import sys
import time
import signal
from datetime import datetime
import os

# Asegurar que el directorio raíz está en el path
sys.path.append(os.getcwd())

from PySide6.QtCore import QCoreApplication
from core.trader import LiveTrader
from data.market_data import MarketDataHandler # Usar la clase correcta
from core.agent import RLAgent
from core.risk import RiskManager
from core.asset_manager import AssetManager
from strategies.technical import FeatureEngineer
from ai.llm_client import LLMClient
from config import Config

# Variable global para control de shutdown
running = True
trader = None

def signal_handler(sig, frame):
    """Manejo de señales para shutdown graceful"""
    global running
    print("\n🛑 Señal de shutdown recibida. Cerrando bot...")
    running = False
    if trader:
        trader.stop()

def main():
    global running, trader
    app = QCoreApplication(sys.argv)
    
    # Registrar handlers de señales
    signal.signal(signal.SIGINT, signal_handler)
    
    print("=" * 60)
    print("🤖 BOT DE TRADING EXNOVA - MODO CONSOLA AVANZADO")
    print("=" * 60)
    print(f"📅 Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🏦 Broker: Exnova / IQ Option")
    print(f"💰 Capital: ${Config.CAPITAL_PER_TRADE}")
    print(f"🎯 Estrategias: Tendencia + Reversión + Estructura + Micro-Validación")
    print("=" * 60)
    
    # Inicializar componentes
    try:
        print("🧠 Cargando módulos de IA...")
        llm_client = LLMClient()
        agent = RLAgent()
        
        print("📊 Cargando gestores de datos...")
        market_data = MarketDataHandler(broker_name="exnova", account_type="PRACTICE")
        feature_engineer = FeatureEngineer()
        
        print("🛡️ Inicializando gestores de riesgo...")
        risk_manager = RiskManager(
            capital_per_trade=Config.CAPITAL_PER_TRADE,
            stop_loss_pct=Config.STOP_LOSS_PERCENT,
            take_profit_pct=Config.TAKE_PROFIT_PERCENT
        )
        asset_manager = AssetManager(market_data)
        
        # Conectar al broker
        email = os.getenv("EXNOVA_EMAIL", "") 
        password = os.getenv("EXNOVA_PASSWORD", "")
        
        if not email or not password:
            print("❌ Falta EXNOVA_EMAIL o EXNOVA_PASSWORD en variables de entorno o .env")
            # Intentar fallback a input manual si es interactivo
            if sys.stdin.isatty():
                email = input("Email: ")
                import getpass
                password = getpass.getpass("Password: ")
            else:
                print("   (Usa 'set EXNOVA_EMAIL=...' antes de ejecutar)")
                return 1

        print(f"\n🔌 Conectando a Exnova como {email}...")
        if not market_data.connect(email, password):
            print("❌ Error: No se pudo conectar al broker")
            print("   (Verifica credenciales y conexión a internet)")
            return 1
        
        print("✅ Conectado exitosamente - MODO PRÁCTICA")
        
        # Crear trader con TODOS los argumentos modernos
        trader = LiveTrader(
            market_data=market_data,
            feature_engineer=feature_engineer,
            agent=agent,
            risk_manager=risk_manager,
            asset_manager=asset_manager,
            llm_client=llm_client
        )
        
        # Conectar señales a impresoras de consola
        # Esto es clave para ver qué pasa
        trader.signals.log_message.connect(lambda msg: print(f"[BOT] {msg}"))
        trader.signals.error_message.connect(lambda msg: print(f"❌ {msg}"))
        trader.signals.trade_signal.connect(lambda action, asset: print(f"\n🚨 SEÑAL: {action} en {asset} 🚨\n"))
        
        # Iniciar trading
        print("\n🚀 Iniciando motor de trading...")
        trader.start()
        
        # Loop principal que mantiene vivo el script principal
        while running:
            # En modo headless no necesitamos hacer mucho, el hilo del trader hace el trabajo
            # Solo vigilamos que el hilo siga vivo
            if not trader.isRunning():
                print("⚠️ El hilo del trader se detuvo inesperadamente.")
                break
                
            time.sleep(1)
            app.processEvents()
            
            # Cada cierto tiempo podemos imprimir un heartbeat
            # if int(time.time()) % 60 == 0:
            #     print("❤️ Bot sigue operando...")
        
        # Shutdown graceful
        print("\n🛑 Deteniendo trader...")
        trader.stop()
        trader.wait()
        
        market_data.disconnect()
        print("✅ Bot detenido correctamente")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error fatal en main: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    # Bucle infinito de re-ejecución anti-crash
    while True:
        try:
            exit_code = main()
            # Si salió limpio (0) o por Ctrl+C, terminamos el bucle
            if exit_code == 0 or not running:
                break
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"🔥 CRASH GLOBAL: {e}")
        
        print("🔄 Reiniciando bot automáticamente en 5 segundos...")
        time.sleep(5)
