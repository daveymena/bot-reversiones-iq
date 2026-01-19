import sys
import signal
import time
from PySide6.QtCore import QCoreApplication, QObject, Slot, QTimer

# Imports del Core
from config import Config
from data.market_data import MarketDataHandler
from strategies.technical import FeatureEngineer
from core.agent import RLAgent
from core.risk import RiskManager
from core.asset_manager import AssetManager
from core.trader import LiveTrader
from ai.llm_client import LLMClient

# Logger para ver la salida en consola
class ConsoleLogger(QObject):
    @Slot(str)
    def log(self, message):
        # Limpiar caracteres raros si hay encoding issues
        try:
            print(message)
        except:
            pass

    @Slot(dict)
    def on_trade(self, trade_data):
        print(f"\n🚀 EJECUTANDO OPERACIÓN: {trade_data['action']} en {trade_data['asset']}")
        print(f"   Confianza: {trade_data['confidence']}%")
        print(f"   Monto: ${trade_data['amount']}")

def signal_handler(sig, frame):
    print("\n🛑 Deteniendo bot...")
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, signal_handler)
    
    print("\n" + "="*60)
    print("🤖 TRADING BOT PRO - CONSOLA AVANZADA (BERSERKER MODE)")
    print("="*60)
    print("Inicializando componentes inteligentes...\n")
    
    # 1. Componentes
    # Asegurar broker exnova explícitamente si Config falla
    broker = Config.BROKER_NAME if hasattr(Config, 'BROKER_NAME') else "exnova"
    account = Config.ACCOUNT_TYPE if hasattr(Config, 'ACCOUNT_TYPE') else "PRACTICE"
    
    # Si viene "iq" por defecto en config pero queremos exnova, forzamos
    # (Asumimos exnova por el contexto del usuario)
    if broker == "iq" and "exnova" in Config.EXNOVA_EMAIL: 
        broker = "exnova"

    print(f"⚙️ Configuración: Broker={broker}, Cuenta={account}")
    market_data = MarketDataHandler(broker_name=broker, account_type=account)
    feature_engineer = FeatureEngineer()
    agent = RLAgent()
    
    risk_manager = RiskManager(
        capital_per_trade=Config.CAPITAL_PER_TRADE,
        stop_loss_pct=Config.STOP_LOSS_PERCENT,
        take_profit_pct=Config.TAKE_PROFIT_PERCENT
    )
    asset_manager = AssetManager(market_data)
    
    print("🧠 Cargando IA Visual (Llama 3.2)...")
    llm_client = LLMClient()
    
    # 2. Trader Inteligente
    trader = LiveTrader(
        market_data=market_data,
        feature_engineer=feature_engineer,
        agent=agent,
        risk_manager=risk_manager,
        asset_manager=asset_manager,
        llm_client=llm_client
    )
    
    # 3. Conexión de Señales a Consola
    app = QCoreApplication(sys.argv)
    logger = ConsoleLogger()
    
    trader.signals.log_message.connect(logger.log)
    # trader.signals.trade_executed.connect(logger.on_trade) # Señal no disponible por ahora
    
    print("🔌 Conectando al broker (Exnova)...")
    if not market_data.connect(Config.EXNOVA_EMAIL, Config.EXNOVA_PASSWORD):
        print("❌ Error: No se pudo conectar al broker. Revisa tus credenciales.")
        sys.exit(1)
        
    print("✅ Conexión establecida. Arrancando motor Berserker...")
    
    # Ejecución directa para evitar problemas de hilos ocultos
    trader.run()

if __name__ == "__main__":
    main()
