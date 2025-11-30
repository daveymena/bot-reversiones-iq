import sys
import argparse
from PySide6.QtWidgets import QApplication
from gui.main_window import MainWindow
from core.trader import LiveTrader
from data.market_data import MarketDataHandler
from strategies.technical import FeatureEngineer
from core.agent import RLAgent
from core.risk import RiskManager
from core.asset_manager import AssetManager
from core.auto_trainer import AutoTrainer
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
    # Intentar cargar modelo, si no existe, el AutoTrainer debería encargarse o el usuario entrenar
    agent.load()

    # Auto-Entrenamiento al inicio (opcional)
    # auto_trainer = AutoTrainer(market_data, feature_engineer)
    # auto_trainer.train_on_recent_data("EURUSD")

    # Crear Hilo del Trader
    trader_thread = LiveTrader(market_data, feature_engineer, agent, risk_manager, asset_manager, llm_client)

    # Iniciar GUI
    app = QApplication(sys.argv)
    window = MainWindow(trader_thread)
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
