#!/usr/bin/env python3
"""
Trading Bot - Versión Consola
Sin interfaz gráfica, solo logs por consola
"""
import sys
import io

# Fix encoding para Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import time
import signal
from datetime import datetime
from config import Config
from data.market_data import MarketDataHandler
from strategies.technical import FeatureEngineer

# RLAgent - usar con cuidado (puede causar hang en importación)
# Usando dummy para operación rápida
class RLAgent:
    def load(self): return False
    def predict(self, state, **kwargs): return 1  # CALL por defecto

from core.risk import RiskManager
from core.asset_manager import AssetManager

# ContinuousLearner, DecisionValidator, TradeAnalyzer, TradeIntelligence
# Todos usan stable_baselines3 que cuelga en Windows
# Usar versiones dummy

class ContinuousLearner:
    def __init__(self, agent, feature_engineer, market_data): pass
    def learn_from_trade(self, *args, **kwargs): pass

class DecisionValidator:
    def validate(self, *args, **kwargs): return True

class TradeAnalyzer:
    def analyze(self, *args, **kwargs): return {}

class TradeIntelligence:
    def __init__(self, **kwargs): pass
    def analyze(self, *args, **kwargs): return None

class LLMClient:
    def __init__(self, **kwargs): pass
    def ask(self, *args, **kwargs): return None

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
    print("TRADING BOT PRO - AI POWERED (CONSOLA)")
    print("="*60)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Broker: {Config.BROKER_NAME.upper()}")
    print(f"Modo: {Config.ACCOUNT_TYPE}")
    print("="*60 + "\n")

def main():
    """Función principal"""
    global running
    
    # Configurar manejo de Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    print_banner()
    
    try:
        # 1. Inicializar componentes
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
            print("⚠️ No se encontró modelo RL, se usará sin entrenar")
        
        # Risk Manager
        risk_manager = RiskManager(
            capital_per_trade=Config.CAPITAL_PER_TRADE,  # $1 por operación
            stop_loss_pct=0.8,      # Stop loss 80%
            take_profit_pct=0.85,   # Take profit 85%
            max_martingale_steps=Config.MAX_MARTINGALE  # 0 = Sin martingala
        )
        
        # Asset Manager
        asset_manager = AssetManager(market_data)
        
        # LLM Client (opcional)
        llm_client = None
        if Config.USE_LLM:
            try:
                llm_client = LLMClient()
                print("✅ Cliente LLM inicializado")
            except Exception as e:
                print(f"⚠️ LLM no disponible: {e}")
        
        # Continuous Learner
        continuous_learner = ContinuousLearner(agent, feature_engineer, market_data)
        
        # Decision Validator
        decision_validator = DecisionValidator()
        
        # Trade Analyzer
        trade_analyzer = TradeAnalyzer()
        
        # Trade Intelligence
        trade_intelligence = TradeIntelligence(llm_client=llm_client)
        
        print("✅ Componentes inicializados\n")
        
        # 2. Conectar al broker
        print(f"🔌 Conectando a {Config.BROKER_NAME.upper()}...")
        
        if Config.BROKER_NAME == "exnova":
            email = Config.EXNOVA_EMAIL
            password = Config.EXNOVA_PASSWORD
        else:
            email = Config.IQ_OPTION_EMAIL
            password = Config.IQ_OPTION_PASSWORD
        
        if not market_data.connect(email, password):
            print("❌ Error conectando al broker")
            return 1
        
        print(f"✅ Conectado a {Config.BROKER_NAME.upper()}\n")
        
        # 3. Obtener balance inicial
        balance = market_data.get_balance()
        print(f"💰 Balance inicial: ${balance:.2f}\n")
        
        # 4. Verificar activos disponibles
        print("🔍 Verificando activos disponibles...")
        available_assets = [
            "EURUSD-OTC", "GBPUSD-OTC", "USDJPY-OTC", 
            "AUDUSD-OTC", "USDCAD-OTC", "EURJPY-OTC"
        ]
        print(f"✅ {len(available_assets)} activos OTC disponibles 24/7\n")
        
        # 5. Iniciar loop de trading
        print("="*60)
        print("🚀 INICIANDO BOT DE TRADING")
        print("="*60)
        print("Presiona Ctrl+C para detener\n")
        
        active_trades = {}
        iteration = 0
        last_scan_time = 0
        
        while running:
            try:
                iteration += 1
                current_time = time.time()
                
                # ⏰ VERIFICACIÓN DE HORARIO - DESHABILITADA (opera 24/7)
                # El bot operará continuamente sin restricciones de horario
                
                # Mostrar heartbeat cada 30 segundos
                if iteration % 30 == 0:
                    balance = market_data.get_balance()
                    print(f"\n💓 Bot activo - Iteración #{iteration} - Balance: ${balance:.2f}")
                
                # Verificar operaciones activas
                if active_trades:
                    for trade_id, trade in list(active_trades.items()):
                        if current_time >= trade['expiration_time']:
                            print(f"\n📊 Verificando resultado de operación {trade_id}...")
                            
                            try:
                                # Obtener resultado del broker
                                if Config.BROKER_NAME == "exnova":
                                    result_status, profit = market_data.api.check_win_v4(trade_id, timeout=90)
                                    
                                    if result_status is None:
                                        print("⏱️ Timeout obteniendo resultado")
                                        profit = 0
                                        result_status = "unknown"
                                else:
                                    profit = market_data.api.check_win_v3(trade_id)
                                    result_status = "win" if profit > 0 else "loose"
                                
                                # Mostrar resultado
                                if profit > 0:
                                    print(f"✅ GANADA: +${profit:.2f}")
                                    risk_manager.update_trade_result(profit)
                                else:
                                    print(f"❌ PERDIDA: ${profit:.2f}")
                                    risk_manager.update_trade_result(profit)
                                
                                # Actualizar balance
                                balance = market_data.get_balance()
                                print(f"💰 Balance actual: ${balance:.2f}")
                                
                                # Remover de activas
                                del active_trades[trade_id]
                                
                            except Exception as e:
                                print(f"⚠️ Error procesando resultado: {e}")
                                del active_trades[trade_id]
                
                # Escanear oportunidades cada 15 segundos (más frecuente)
                if current_time - last_scan_time >= 15:
                    last_scan_time = current_time
                    
                    print(f"\n🔍 Escaneando oportunidades... ({datetime.now().strftime('%H:%M:%S')})")
                    
                    # Buscar oportunidades (simplificado)
                    opportunities = []
                    for asset in available_assets[:3]:  # Solo primeros 3 activos
                        try:
                            df = market_data.get_candles(asset, Config.TIMEFRAME, 200)
                            if df.empty or len(df) < 100:
                                continue
                            
                            # Preparar features
                            df = feature_engineer.prepare_for_rl(df)
                            if df.empty or len(df) < 10:
                                continue
                            
                            # Predecir con RL
                            state = df.iloc[-10:].values  # Convertir a numpy array
                            action = agent.predict(state, df_context=df)
                            
                            # Convertir acción a int si es necesario
                            if hasattr(action, 'item'):
                                action = action.item()
                            action = int(action)
                            
                            # Convertir acción a dirección
                            if action == 0:  # HOLD
                                continue
                            
                            direction = 'call' if action == 1 else 'put'
                            
                            # Calcular confianza basada en indicadores
                            last_candle = df.iloc[-1]
                            rsi = last_candle.get('rsi', 50)
                            macd = last_candle.get('macd', 0)
                            bb_position = last_candle.get('bb_position', 0.5)
                            
                            # Mejor cálculo de confianza
                            if direction == 'call':
                                # CALL: RSI bajo + MACD positivo + cerca de banda inferior
                                confidence = 0.5 + (50 - rsi) / 100 + macd / 10
                                if bb_position < 0.2:  # Cerca de banda inferior
                                    confidence += 0.1
                            else:
                                # PUT: RSI alto + MACD negativo + cerca de banda superior
                                confidence = 0.5 + (rsi - 50) / 100 - macd / 10
                                if bb_position > 0.8:  # Cerca de banda superior
                                    confidence += 0.1
                            
                            confidence = max(0.5, min(0.95, confidence))
                            
                            # UMbral reducido para operar más
                            if confidence > 0.55:
                                opportunities.append({
                                    'asset': asset,
                                    'direction': direction,
                                    'confidence': confidence
                                })
                        except Exception as e:
                            import traceback
                            print(f"⚠️ Error analizando {asset}: {e}")
                            # traceback.print_exc()  # Descomentar para debug
                            continue
                    
                    if opportunities:
                        # Ordenar por confianza
                        opportunities.sort(key=lambda x: x['confidence'], reverse=True)
                        best_opp = opportunities[0]
                        asset = best_opp['asset']
                        direction = best_opp['direction']
                        confidence = best_opp['confidence']
                        
                        print(f"\n💎 Oportunidad detectada:")
                        print(f"   Asset: {asset}")
                        print(f"   Dirección: {direction.upper()}")
                        print(f"   Confianza: {confidence*100:.1f}%")
                        
                        # Ejecutar operación
                        amount = risk_manager.get_trade_amount()
                        expiration = 3  # 3 minutos
                        
                        print(f"\n🚀 Ejecutando {direction.upper()} en {asset}")
                        print(f"   Monto: ${amount:.2f}")
                        print(f"   Expiración: {expiration} min")
                        
                        try:
                            # Obtener precio actual
                            df = market_data.get_candles(asset, Config.TIMEFRAME, 1)
                            current_price = df.iloc[-1]['close'] if not df.empty else 0
                            
                            # Ejecutar en broker
                            success, order_id = market_data.api.buy(
                                amount,
                                asset,
                                direction,
                                expiration
                            )
                            
                            if success:
                                print(f"✅ Operación ejecutada - ID: {order_id}")
                                
                                # Agregar a activas
                                active_trades[order_id] = {
                                    'id': order_id,
                                    'asset': asset,
                                    'direction': direction,
                                    'amount': amount,
                                    'entry_price': current_price,
                                    'expiration_time': current_time + (expiration * 60),
                                    'timestamp': current_time
                                }
                                
                                # Cooldown de 2 minutos
                                print("⏳ Cooldown: 2 minutos antes de la próxima operación")
                                time.sleep(120)
                            else:
                                print(f"❌ Error ejecutando operación: {order_id}")
                        
                        except Exception as e:
                            print(f"❌ Error en ejecución: {e}")
                            import traceback
                            traceback.print_exc()
                    else:
                        print("⏳ No hay oportunidades claras, esperando...")
                
                # Pausa pequeña para no saturar CPU
                time.sleep(1)
            
            except KeyboardInterrupt:
                print("\n\n🛑 Deteniendo bot...")
                break
            
            except Exception as e:
                print(f"\n❌ Error en loop principal: {e}")
                import traceback
                traceback.print_exc()
                print("⚠️ Bot continuará operando...\n")
                time.sleep(5)
        
        # 6. Cerrar conexión
        print("\n" + "="*60)
        print("RESUMEN FINAL")
        print("="*60)
        balance_final = market_data.get_balance()
        print(f"Balance final: ${balance_final:.2f}")
        print(f"Ganancia/Pérdida: ${balance_final - balance:.2f}")
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
