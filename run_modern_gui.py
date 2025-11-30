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
    # Inicializar componentes
    market_data = MarketDataHandler(broker_name=Config.BROKER_NAME, account_type=Config.ACCOUNT_TYPE)
    feature_engineer = FeatureEngineer()
    risk_manager = RiskManager(Config.CAPITAL_PER_TRADE, Config.STOP_LOSS_PCT, Config.TAKE_PROFIT_PCT)
    asset_manager = AssetManager(market_data)
    llm_client = LLMClient()
    
    # Agente RL
    agent = RLAgent(model_path=Config.MODEL_PATH)
    agent.load()

    # Crear Hilo del Trader
    trader_thread = LiveTrader(market_data, feature_engineer, agent, risk_manager, asset_manager, llm_client)

    # Iniciar GUI MODERNA
    app = QApplication(sys.argv)
    window = ModernMainWindow(trader_thread)
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
