"""
Bot de Trading Estable - Solo Consola
Sin GUI, sin crashes, con logging completo
"""
import time
import sys
from datetime import datetime
from config import Config
from data.market_data import MarketDataHandler
from strategies.technical import FeatureEngineer
from core.agent import RLAgent
from core.risk import RiskManager
from core.asset_manager import AssetManager
from core.trade_intelligence import TradeIntelligence
from core.continuous_learner import ContinuousLearner
from core.observational_learner import ObservationalLearner
from core.decision_validator import DecisionValidator
from ai.llm_client import LLMClient

def log(msg):
    """Log con timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {msg}")

def main():
    print("\n" + "="*70)
    print(" BOT DE TRADING - MODO CONSOLA ESTABLE")
    print("="*70)
    print(f" Broker: {Config.BROKER_NAME.upper()}")
    print(f" Cuenta: {Config.ACCOUNT_TYPE}")
    print(f" Capital por operacion: ${Config.CAPITAL_PER_TRADE}")
    print("="*70 + "\n")
    
    # Inicializar componentes
    log("Inicializando componentes...")
    
    market_data = MarketDataHandler(
        broker_name=Config.BROKER_NAME,
        account_type=Config.ACCOUNT_TYPE
    )
    
    feature_engineer = FeatureEngineer()
    agent = RLAgent(model_path=Config.MODEL_PATH)
    risk_manager = RiskManager(
        Config.CAPITAL_PER_TRADE,
        Config.STOP_LOSS_PCT,
        Config.TAKE_PROFIT_PCT
    )
    asset_manager = AssetManager(market_data)
    llm_client = LLMClient()
    
    # Sistemas de inteligencia
    trade_intelligence = TradeIntelligence(llm_client=llm_client)
    continuous_learner = ContinuousLearner(agent, feature_engineer, market_data)
    decision_validator = DecisionValidator()
    observational_learner = ObservationalLearner(
        continuous_learner,
        market_data,
        feature_engineer
    )
    
    # Cargar modelo
    try:
        agent.load()
        log("Modelo RL cargado")
    except:
        log("Modelo RL no encontrado")
    
    # Conectar al broker
    log("Conectando al broker...")
    if Config.BROKER_NAME == "exnova":
        connected = market_data.connect(Config.EX_EMAIL, Config.EX_PASSWORD)
    else:
        connected = market_data.connect(Config.IQ_EMAIL, Config.IQ_PASSWORD)
    
    if not connected:
        log("ERROR: No se pudo conectar al broker")
        return
    
    log(f"Conectado exitosamente en modo {Config.ACCOUNT_TYPE}")
    
    # Obtener balance
    try:
        balance = market_data.get_balance()
        log(f"Balance actual: ${balance:.2f}")
    except:
        log("No se pudo obtener el balance")
    
    # Variables de control
    active_trades = []
    consecutive_losses = 0
    last_trade_time = 0
    cooldown_time = 0
    
    log("\nIniciando operaciones...")
    log("Presiona Ctrl+C para detener\n")
    
    try:
        while True:
            try:
                # Verificar cooldown
                if cooldown_time > 0:
                    remaining = cooldown_time - time.time()
                    if remaining > 0:
                        time.sleep(5)
                        continue
                    else:
                        cooldown_time = 0
                
                # Verificar operaciones activas
                if active_trades:
                    for trade in active_trades[:]:
                        wait_time = trade['duration'] + 10
                        if time.time() - trade['entry_time'] >= wait_time:
                            log(f"\nVerificando resultado de operacion {trade['id']}...")
                            
                            try:
                                # Obtener resultado
                                if Config.BROKER_NAME == "exnova":
                                    result_status, profit = market_data.api.check_win_v4(trade['id'])
                                    log(f"Resultado: {result_status}, Profit: ${profit:.2f}")
                                else:
                                    profit = market_data.api.check_win_v3(trade['id'])
                                    result_status = "win" if profit > 0 else "loose"
                                    log(f"Resultado: Profit: ${profit:.2f}")
                                
                                won = profit > 0
                                
                                if won:
                                    log(f"GANADA: +${profit:.2f}")
                                    consecutive_losses = 0
                                else:
                                    log(f"PERDIDA: ${profit:.2f}")
                                    consecutive_losses += 1
                                    cooldown_time = time.time() + 300  # 5 minutos
                                    log(f"Cooldown: 5 minutos")
                                
                                # Actualizar balance
                                try:
                                    balance = market_data.get_balance()
                                    log(f"Balance actualizado: ${balance:.2f}")
                                except:
                                    pass
                                
                                # Remover de activas
                                active_trades.remove(trade)
                                
                            except Exception as e:
                                log(f"ERROR verificando resultado: {e}")
                                active_trades.remove(trade)
                    
                    time.sleep(2)
                    continue
                
                # Buscar oportunidad
                if time.time() - last_trade_time < 30:
                    time.sleep(5)
                    continue
                
                log("Escaneando oportunidades...")
                opportunity = asset_manager.scan_best_opportunity(feature_engineer)
                
                if not opportunity:
                    log("Sin oportunidades claras, esperando...")
                    time.sleep(10)
                    continue
                
                asset = opportunity.get('asset')
                direction = opportunity.get('action', 'call')  # 'action' en lugar de 'direction'
                score = opportunity.get('score', 0)
                
                if not asset or not direction:
                    log("Oportunidad invalida, esperando...")
                    time.sleep(10)
                    continue
                
                log(f"Oportunidad detectada: {direction.upper()} en {asset} (Score: {score})")
                
                # Validar decision
                df = market_data.get_candles(asset, Config.TIMEFRAME, 200)
                if df.empty:
                    log("No se pudieron obtener datos")
                    time.sleep(10)
                    continue
                
                df = feature_engineer.prepare_for_rl(df)
                if df.empty:
                    log("Error preparando datos")
                    time.sleep(10)
                    continue
                
                # Ejecutar operacion
                log(f"Ejecutando {direction.upper()} en {asset}...")
                log(f"Monto: ${Config.CAPITAL_PER_TRADE}")
                
                try:
                    current_price = df.iloc[-1]['close']
                    expiration = 3  # 3 minutos
                    
                    if Config.BROKER_NAME == "exnova":
                        success, order_id = market_data.api.buy(
                            Config.CAPITAL_PER_TRADE,
                            asset,
                            direction,
                            expiration
                        )
                    else:
                        success, order_id = market_data.api.buy(
                            Config.CAPITAL_PER_TRADE,
                            asset,
                            direction,
                            expiration
                        )
                    
                    if success:
                        log(f"Operacion ejecutada exitosamente")
                        log(f"Order ID: {order_id}")
                        
                        active_trades.append({
                            'id': order_id,
                            'asset': asset,
                            'direction': direction,
                            'entry_price': current_price,
                            'entry_time': time.time(),
                            'duration': expiration * 60,
                            'amount': Config.CAPITAL_PER_TRADE
                        })
                        
                        last_trade_time = time.time()
                    else:
                        log(f"ERROR: No se pudo ejecutar la operacion")
                        time.sleep(30)
                
                except Exception as e:
                    log(f"ERROR ejecutando operacion: {e}")
                    import traceback
                    traceback.print_exc()
                    time.sleep(30)
            
            except KeyboardInterrupt:
                raise
            except Exception as e:
                log(f"ERROR en bucle principal: {e}")
                import traceback
                traceback.print_exc()
                time.sleep(10)
    
    except KeyboardInterrupt:
        log("\n\nDeteniendo bot...")
        log("Bot detenido por el usuario")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nERROR FATAL: {e}")
        import traceback
        traceback.print_exc()
        input("\nPresiona Enter para salir...")
