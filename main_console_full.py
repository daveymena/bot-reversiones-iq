#!/usr/bin/env python3
"""
Trading Bot - Versión Consola COMPLETA
Usa EXACTAMENTE la misma lógica que la GUI (LiveTrader)
pero sin interfaz gráfica
"""

import sys
import time
import signal
from datetime import datetime
from config import Config
from data.market_data import MarketDataHandler
from strategies.technical import FeatureEngineer
from core.agent import RLAgent
from core.risk import RiskManager
from core.asset_manager import AssetManager
from core.continuous_learner import ContinuousLearner
from core.decision_validator import DecisionValidator
from core.trade_analyzer import TradeAnalyzer
from core.trade_intelligence import TradeIntelligence
from core.observational_learner import ObservationalLearner
from core.market_structure_analyzer import MarketStructureAnalyzer
from ai.llm_client import LLMClient

# Variable global para manejo de señales
running = True

def signal_handler(sig, frame):
    """Maneja Ctrl+C para cerrar limpiamente"""
    global running
    print("\n\n🛑 Deteniendo bot...")
    running = False
    sys.exit(0)

def print_banner():
    """Imprime banner de inicio"""
    print("\n" + "="*60)
    print("TRADING BOT PRO - VERSIÓN COMPLETA (CONSOLA)")
    print("="*60)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Broker: {Config.BROKER_NAME.upper()}")
    print(f"Modo: {Config.ACCOUNT_TYPE}")
    print("="*60 + "\n")

class ConsoleSignal:
    """Clase para simular una señal individual de Qt"""
    def __init__(self, callback):
        self.callback = callback
    
    def emit(self, *args):
        self.callback(*args)

class ConsoleSignals:
    """Clase para simular las señales de Qt en consola"""
    
    def __init__(self):
        # Señales principales
        self.log_message = ConsoleSignal(self._log_message)
        self.error_message = ConsoleSignal(self._error_message)
        self.balance_update = ConsoleSignal(self._balance_update)
        self.stats_update = ConsoleSignal(self._stats_update)
        
        # Señales de gráficos (no verbose en consola)
        self.price_update = ConsoleSignal(self._noop)
        self.new_candle = ConsoleSignal(self._noop)
        self.trade_signal = ConsoleSignal(self._noop)
        self.chart_update = ConsoleSignal(self._noop)
        
        # Señales adicionales que pueda usar el trader
        self.opportunity_detected = ConsoleSignal(self._noop)
        self.trade_executed = ConsoleSignal(self._noop)
        self.trade_result = ConsoleSignal(self._noop)
    
    def _log_message(self, msg):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")
    
    def _error_message(self, msg):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ {msg}")
    
    def _balance_update(self, balance):
        # Solo mostrar balance cada 10 actualizaciones para no saturar
        if not hasattr(self, '_balance_counter'):
            self._balance_counter = 0
        self._balance_counter += 1
        if self._balance_counter % 10 == 0:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 💰 Balance: ${balance:.2f}")
    
    def _stats_update(self, wins, losses, pnl):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 📊 Stats: {wins}W/{losses}L | PnL: ${pnl:.2f}")
    
    def _noop(self, *args, **kwargs):
        # No hacer nada (para señales de GUI que no necesitamos en consola)
        pass
    
    def __getattr__(self, name):
        # Capturar cualquier señal no definida y crear una señal noop
        if not name.startswith('_'):
            signal = ConsoleSignal(self._noop)
            setattr(self, name, signal)
            return signal
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

def main():
    """Función principal"""
    global running
    
    # Configurar manejo de Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    print_banner()
    
    try:
        # 1. Inicializar componentes (IGUAL QUE LA GUI)
        print("📦 Inicializando componentes...")
        
        # Market Data
        market_data = MarketDataHandler(
            broker_name=Config.BROKER_NAME,
            account_type=Config.ACCOUNT_TYPE
        )
        
        # Feature Engineer
        feature_engineer = FeatureEngineer()
        
        # RL Agent
        agent = RLAgent()
        if agent.load():
            print("✅ Modelo RL cargado")
        else:
            print("⚠️ No se encontró modelo RL")
        
        # Risk Manager
        risk_manager = RiskManager(
            capital_per_trade=1,
            stop_loss_pct=0.8,
            take_profit_pct=0.85,
            max_martingale_steps=3
        )
        
        # Asset Manager
        asset_manager = AssetManager(market_data)
        
        # LLM Client
        llm_client = None
        if Config.USE_LLM:
            try:
                llm_client = LLMClient()
                print("✅ Cliente LLM inicializado")
            except Exception as e:
                print(f"⚠️ LLM no disponible: {e}")
        
        # Continuous Learner
        continuous_learner = ContinuousLearner(agent, feature_engineer, market_data)
        
        # Decision Validator (COMPLETO)
        decision_validator = DecisionValidator()
        
        # Trade Analyzer
        trade_analyzer = TradeAnalyzer()
        
        # Trade Intelligence (con LLM)
        trade_intelligence = TradeIntelligence(llm_client=llm_client)
        
        # Observational Learner
        observational_learner = ObservationalLearner(
            continuous_learner=continuous_learner,
            market_data=market_data,
            feature_engineer=feature_engineer
        )
        
        # Market Structure Analyzer
        market_structure = MarketStructureAnalyzer()
        
        print("✅ Componentes inicializados (VERSIÓN COMPLETA)\n")
        
        # 2. Conectar al broker
        print(f"🔌 Conectando a {Config.BROKER_NAME.upper()}...")
        
        if Config.BROKER_NAME == "exnova":
            email = Config.EX_EMAIL
            password = Config.EX_PASSWORD
        else:
            email = Config.IQ_EMAIL
            password = Config.IQ_PASSWORD
        
        if not market_data.connect(email, password):
            print("❌ Error conectando al broker")
            return 1
        
        print(f"✅ Conectado a {Config.BROKER_NAME.upper()}\n")
        
        # 3. Importar LiveTrader (usa toda la lógica de la GUI)
        from core.trader import LiveTrader
        
        # Crear señales de consola
        signals = ConsoleSignals()
        
        # Crear LiveTrader (MISMA LÓGICA QUE LA GUI)
        trader = LiveTrader(
            market_data=market_data,
            feature_engineer=feature_engineer,
            agent=agent,
            risk_manager=risk_manager,
            asset_manager=asset_manager,
            llm_client=llm_client
        )
        
        # Asignar señales de consola
        trader.signals = signals
        
        # Asignar componentes adicionales
        trader.continuous_learner = continuous_learner
        trader.decision_validator = decision_validator
        trader.trade_analyzer = trade_analyzer
        trader.trade_intelligence = trade_intelligence
        trader.observational_learner = observational_learner
        trader.market_structure = market_structure
        
        print("="*60)
        print("🚀 INICIANDO BOT DE TRADING (VERSIÓN COMPLETA)")
        print("="*60)
        print("Usando EXACTAMENTE la misma lógica que la GUI")
        print("Presiona Ctrl+C para detener\n")
        
        # 4. Ejecutar el trader (método protegido sin QThread)
        trader.running = True
        trader.paused = False
        
        # Ejecutar el loop principal del trader
        try:
            trader._run_protected()
        except KeyboardInterrupt:
            print("\n\n🛑 Deteniendo bot...")
            trader.running = False
        
        # 5. Resumen final
        print("\n" + "="*60)
        print("RESUMEN FINAL")
        print("="*60)
        balance_final = market_data.get_balance()
        print(f"Balance final: ${balance_final:.2f}")
        print(f"Total operaciones: {risk_manager.total_trades}")
        print(f"Ganadas: {risk_manager.wins}")
        print(f"Perdidas: {risk_manager.total_trades - risk_manager.wins}")
        if risk_manager.total_trades > 0:
            win_rate = (risk_manager.wins / risk_manager.total_trades) * 100
            print(f"Win Rate: {win_rate:.1f}%")
        print("="*60 + "\n")
        
        print("👋 Bot detenido correctamente")
        return 0
    
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
