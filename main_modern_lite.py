"""
Bot de Trading con Interfaz Moderna - Versión Lite
Versión Pro con diseño oscuro profesional
Sin módulos RL problemáticos (usa análisis técnico + LLM)
"""
import sys
from PySide6.QtWidgets import QApplication
from gui.modern_main_window import ModernMainWindow
from core.trader import LiveTrader
from data.market_data import MarketDataHandler
from strategies.technical import FeatureEngineer
from core.risk import RiskManager
from core.asset_manager import AssetManager
from ai.llm_client import LLMClient
from config import Config

# Agente dummy que usa solo análisis técnico
class TechnicalAgent:
    """Agente que usa solo análisis técnico sin RL"""
    def __init__(self):
        self.model = None
        
    def predict(self, features):
        """Predicción basada en análisis técnico"""
        # Usar indicadores técnicos para decidir
        if len(features) < 10:
            return 0, 0.0  # No operar
            
        # Análisis simple basado en indicadores
        rsi = features.get('rsi', 50)
        macd = features.get('macd', 0)
        bb_position = features.get('bb_position', 0.5)
        
        # Señal de compra (CALL)
        if rsi < 30 and macd > 0 and bb_position < 0.3:
            return 1, 0.75  # CALL con 75% confianza
            
        # Señal de venta (PUT)
        if rsi > 70 and macd < 0 and bb_position > 0.7:
            return 2, 0.75  # PUT con 75% confianza
            
        return 0, 0.0  # No operar
        
    def load(self):
        """Cargar modelo (no hace nada en versión lite)"""
        print("⚠️ Versión Lite: Usando análisis técnico sin RL")
        return True
        
    def save(self):
        """Guardar modelo (no hace nada en versión lite)"""
        pass

def main():
    print("=" * 60)
    print("TRADING BOT PRO - VERSIÓN LITE")
    print("Análisis Técnico + LLM (Sin RL)")
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
    
    # Agente técnico (sin RL)
    agent = TechnicalAgent()
    agent.load()
    
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
    print("\nIniciando interfaz gráfica...")
    
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
    print("2. Haz clic en 'INICIAR BOT' (no requiere entrenamiento)")
    print("3. El bot usará análisis técnico + LLM para operar")
    print("\n⚠️ NOTA: Esta versión no incluye Reinforcement Learning")
    print("   Usa análisis técnico avanzado + validación LLM")
    print("=" * 60)
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
