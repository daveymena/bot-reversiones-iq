"""
Bot de Trading con Interfaz Moderna
Versión Pro con diseño oscuro profesional
"""
import sys
from PySide6.QtWidgets import QApplication
from gui.modern_main_window import ModernMainWindow
from core.trader import LiveTrader
from data.market_data import MarketDataHandler
from strategies.technical import FeatureEngineer
from core.agent import RLAgent
from core.risk import RiskManager
from core.asset_manager import AssetManager
from ai.llm_client import LLMClient
from config import Config

def main():
    print("=" * 60)
    print("TRADING BOT PRO - AI POWERED")
    print("=" * 60)
    print("\nInicializando componentes...")
    
    # Inicializar componentes
    market_data = MarketDataHandler(broker_name=Config.BROKER_NAME, account_type=Config.ACCOUNT_TYPE)
    feature_engineer = FeatureEngineer()
    risk_manager = RiskManager(
        Config.CAPITAL_PER_TRADE,
        Config.STOP_LOSS_PCT,
        Config.TAKE_PROFIT_PCT
    )
    asset_manager = AssetManager(market_data)
    llm_client = LLMClient()
    
    # Agente RL
    agent = RLAgent(model_path=Config.MODEL_PATH)
    try:
        agent.load()
        print("Modelo RL cargado")
    except:
        print("Modelo RL no encontrado (se creara al entrenar)")
    
    # Crear trader thread
    trader_thread = LiveTrader(
        market_data,
        feature_engineer,
        agent,
        risk_manager,
        asset_manager,
        llm_client
    )
    
    print("Componentes inicializados")
    print("\nIniciando interfaz grafica...")
    
    # Iniciar GUI
    app = QApplication(sys.argv)
    
    # Configurar fuente global
    font = app.font()
    font.setFamily("Segoe UI")
    font.setPointSize(10)
    app.setFont(font)
    
    window = ModernMainWindow(trader_thread)
    
    # Pre-cargar credenciales
    if Config.BROKER_NAME == "exnova":
        window.combo_broker.setCurrentText("Exnova")
        window.txt_email.setText(Config.EX_EMAIL or "")
        window.txt_password.setText(Config.EX_PASSWORD or "")
    else:
        window.combo_broker.setCurrentText("IQ Option")
        window.txt_email.setText(Config.IQ_EMAIL or "")
        window.txt_password.setText(Config.IQ_PASSWORD or "")
    
    window.show()
    
    print("Interfaz iniciada")
    print("\n" + "=" * 60)
    print("Bot listo para operar")
    print("=" * 60)
    print("\nINSTRUCCIONES:")
    print("1. Haz clic en 'CONECTAR' para conectarte al broker")
    print("2. Ve a la pestana 'Entrenamiento' y entrena el modelo")
    print("3. Una vez entrenado, haz clic en 'INICIAR BOT'")
    print("=" * 60)
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
