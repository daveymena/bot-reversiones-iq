#!/usr/bin/env python3
"""
Bot de Trading Headless - Versión corregida y optimizada
"""

import sys
import os
import time
import signal
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar componentes
from data.market_data import MarketDataHandler
from strategies.technical import FeatureEngineer
from core.agent import RLAgent
from core.risk import RiskManager
from core.asset_manager import AssetManager
from core.trader import LiveTrader
from ai.llm_client import LLMClient
from config import Config

def signal_handler(sig, frame):
    """Maneja la señal de interrupción"""
    print("\n🛑 Deteniendo bot...")
    sys.exit(0)

def main():
    """Función principal"""
    # Configurar manejo de señales
    signal.signal(signal.SIGINT, signal_handler)
    
    print("[!] Base de datos DESHABILITADA (para evitar congelamientos)")
    print("   El bot funcionará sin guardar en BD")
    
    print("=" * 60)
    print("🤖 BOT DE TRADING EXNOVA - MODO CONSOLA OPTIMIZADO")
    print("=" * 60)
    print(f"📅 Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🏦 Broker: {Config.BROKER_NAME}")
    print(f"💰 Capital: ${Config.CAPITAL_PER_TRADE}")
    print("🎯 Estrategias: Smart Money + IA Agresiva + Ollama Orquestador")
    print("=" * 60)
    
    try:
        # Inicializar componentes
        print("🧠 Cargando módulos de IA...")
        llm_client = LLMClient()
        
        print("📊 Cargando gestores de datos...")
        market_data = MarketDataHandler(
            broker_name=Config.BROKER_NAME,
            account_type=Config.ACCOUNT_TYPE
        )
        feature_engineer = FeatureEngineer()
        
        print("🛡️ Inicializando gestores de riesgo...")
        risk_manager = RiskManager(
            capital_per_trade=Config.CAPITAL_PER_TRADE,
            stop_loss_pct=Config.STOP_LOSS_PERCENT,
            take_profit_pct=Config.TAKE_PROFIT_PERCENT
        )
        print(f"   - Capital Base: ${Config.CAPITAL_PER_TRADE}")
        print(f"   - Martingala Max Pasos: {Config.MAX_MARTINGALE} ({'Desactivado' if Config.MAX_MARTINGALE == 0 else 'Activado'})")
        
        # Conectar al broker
        print(f"🔌 Conectando a {Config.BROKER_NAME.title()} como {Config.EXNOVA_EMAIL}...")
        success = market_data.connect(Config.EXNOVA_EMAIL, Config.EXNOVA_PASSWORD)
        
        if not success:
            print("❌ Error conectando al broker")
            return False
        
        print(f"✅ Conectado exitosamente - MODO {Config.ACCOUNT_TYPE}")
        
        # Inicializar agente RL
        agent = RLAgent()
        
        # Inicializar asset manager con configuración agresiva
        asset_manager = AssetManager(market_data)
        asset_manager.min_profit = 60  # Más agresivo (reducido de 70)
        
        print("🚀 Iniciando motor de trading...")
        
        # Crear trader con configuración optimizada
        trader = LiveTrader(
            market_data=market_data,
            feature_engineer=feature_engineer,
            agent=agent,
            risk_manager=risk_manager,
            asset_manager=asset_manager,
            llm_client=llm_client
        )
        
        # Configuración agresiva
        trader.scan_interval = 15  # Escanear cada 15 segundos (más agresivo)
        trader.min_time_between_trades = 30  # Reducir tiempo entre trades
        
        # Iniciar el trader
        trader.start()
        
        # Mantener el programa corriendo
        try:
            while trader.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Deteniendo bot por solicitud del usuario...")
            trader.stop()
            trader.wait()
        
        print("✅ Bot detenido correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)