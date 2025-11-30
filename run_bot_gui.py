"""
Ejecutar Bot con Interfaz Grafica - Version Estable
Sin bloqueos ni congelamientos
"""
import sys
import os

# Configurar encoding para Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
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
    market_data = MarketDataHandler(
        broker_name=Config.BROKER_NAME,
        account_type=Config.ACCOUNT_TYPE
    )
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
    
    # Configurar para evitar congelamientos
    app.setAttribute(Qt.AA_DontUseNativeMenuBar, True)
    
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
    
    # Pre-seleccionar tipo de cuenta
    window.combo_account.setCurrentText(Config.ACCOUNT_TYPE)
    
    window.show()
    
    print("Interfaz iniciada")
    print("\n" + "=" * 60)
    print("Bot listo para operar")
    print("Modo:", Config.ACCOUNT_TYPE)
    print("=" * 60)
    print("\nINSTRUCCIONES:")
    print("1. Haz clic en 'CONECTAR' para conectarte al broker")
    print("2. Haz clic en 'INICIAR BOT' para comenzar a operar")
    print("3. Monitorea las operaciones en tiempo real")
    print("=" * 60)
    
    sys.exit(app.exec())

if __name__ == "__main__":
    import sys
    import traceback
    import logging
    
    # Configurar logging a archivo
    logging.basicConfig(
        filename='bot_errors.log',
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Configurar para capturar TODOS los errores
    def exception_hook(exctype, value, tb):
        error_msg = f"\nERROR CAPTURADO:\nTipo: {exctype.__name__}\nMensaje: {value}\n"
        print("="*60)
        print(error_msg)
        traceback.print_exception(exctype, value, tb)
        print("="*60)
        
        # Guardar en log
        logging.error(error_msg)
        logging.error(''.join(traceback.format_exception(exctype, value, tb)))
        
        # Mantener consola abierta
        try:
            input("\nPresiona Enter para salir...")
        except:
            pass
    
    sys.excepthook = exception_hook
    
    # Suprimir warnings de Qt que no son críticos
    import warnings
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    
    try:
        main()
    except Exception as e:
        print("\n" + "="*60)
        print("ERROR EN MAIN:")
        print("="*60)
        print(f"Error: {e}")
        traceback.print_exc()
        print("="*60)
        logging.error(f"Error en main: {e}")
        logging.error(traceback.format_exc())
        try:
            input("\nPresiona Enter para salir...")
        except:
            pass
