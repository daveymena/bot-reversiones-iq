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

# Importar PySide6 de forma opcional
try:
    from PySide6.QtCore import QCoreApplication
    PYSIDE_AVAILABLE = True
except ImportError:
    PYSIDE_AVAILABLE = False
    print("⚠️ PySide6 no detectado. Usando modo consola puro.")

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
    app = None
    if PYSIDE_AVAILABLE:
        # Solo crear QCoreApplication si no existe una
        if QCoreApplication.instance() is None:
            app = QCoreApplication(sys.argv)
        else:
            app = QCoreApplication.instance()
    else:
        print("ℹ️ Iniciando sin QCoreApplication (Modo Servidor)")
    
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
    
    # Crear flag file para health check
    os.makedirs('data', exist_ok=True)
    with open('data/bot_running.flag', 'w') as f:
        f.write(str(datetime.now()))
    
    # Inicializar componentes
    try:
        print("🧠 Cargando módulos de IA...")
        llm_client = LLMClient()
        agent = RLAgent()
        
        print("📊 Cargando gestores de datos...")
        market_data = MarketDataHandler(broker_name="exnova", account_type="PRACTICE")
        feature_engineer = FeatureEngineer()
        
        print("🛡️ Inicializando gestores de riesgo...")
        print(f"   - Capital Base: ${Config.CAPITAL_PER_TRADE}")
        print(f"   - Martingala Max Pasos: {Config.MAX_MARTINGALE} (0 = Desactivado)")
        risk_manager = RiskManager(
            capital_per_trade=Config.CAPITAL_PER_TRADE,
            stop_loss_pct=Config.STOP_LOSS_PERCENT,
            take_profit_pct=Config.TAKE_PROFIT_PERCENT,
            max_martingale_steps=Config.MAX_MARTINGALE
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
        
        # Verificar si existe el análisis profundo de horarios
        if not os.path.exists('data/market_deep_dive.json'):
            print("\n💡 TIP: Ejecuta 'python scripts/market_deep_dive.py' para activar el filtro de ELITE HOURS.")
        else:
            print("\n✅ Filtro de ELITE HOURS activado (Usando datos de análisis profundo)")
        
        # Iniciar trading
        print("\n🚀 Iniciando motor de trading...")
        trader.start()
        
        # Loop principal que mantiene vivo el script principal
        while running:
            # En modo headless no necesitamos hacer mucho, el hilo del trader hace el trabajo
            # Solo vigilamos que el hilo siga vivo
            # Solo vigilamos que el hilo siga vivo y lo reiniciamos si cae
            if not trader.isRunning():
                print("⚠️ El hilo del trader se detuvo inesperadamente. REINICIANDO...")
                try:
                    trader.start()
                except Exception as e:
                    print(f"❌ Error reiniciando hilo: {e}")
                    break
                
            time.sleep(1)
            if PYSIDE_AVAILABLE and app:
                app.processEvents()
            
            # Cada cierto tiempo podemos imprimir un heartbeat
            # if int(time.time()) % 60 == 0:
            #     print("❤️ Bot sigue operando...")
        
        # Shutdown graceful
        print("\n🛑 Deteniendo trader...")
        trader.stop()
        trader.wait()
        
        market_data.disconnect()
        
        # Eliminar flag file
        if os.path.exists('data/bot_running.flag'):
            os.remove('data/bot_running.flag')
        
        print("✅ Bot detenido correctamente")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error fatal en main: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    # Bucle de re-ejecución anti-crash con límite
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            exit_code = main()
            # Si salió limpio (0) o por Ctrl+C, terminamos el bucle
            if exit_code == 0 or not running:
                break
            retry_count += 1
        except KeyboardInterrupt:
            print("\n🛑 Detenido por el usuario")
            break
        except Exception as e:
            print(f"🔥 CRASH GLOBAL: {e}")
            retry_count += 1
        
        if retry_count < max_retries:
            print(f"🔄 Reiniciando bot automáticamente en 5 segundos... (Intento {retry_count}/{max_retries})")
            time.sleep(5)
        else:
            print(f"❌ Máximo de reintentos alcanzado ({max_retries}). Deteniendo bot.")
            print("💡 Verifica tu conexión a internet y credenciales en .env")
