"""
Bot de Trading con Aprendizaje Continuo
Registra cada operación con todos los detalles para mejorar automáticamente
"""
import time
import json
import pandas as pd
from datetime import datetime
from config import Config
from data.market_data import MarketDataHandler
from strategies.technical import FeatureEngineer
from core.agent import RLAgent
from core.risk import RiskManager

class TradingLogger:
    """Registra cada operación con todos los detalles para aprendizaje"""
    
    def __init__(self, log_file="data/operaciones_log.json"):
        self.log_file = log_file
        self.operations = []
        
    def log_operation(self, operation_data):
        """Registra una operación completa"""
        operation_data['timestamp'] = datetime.now().isoformat()
        self.operations.append(operation_data)
        
        # Guardar inmediatamente
        self.save()
        
    def save(self):
        """Guarda el log en archivo JSON"""
        try:
            with open(self.log_file, 'w') as f:
                json.dump(self.operations, f, indent=2)
        except Exception as e:
            print(f"⚠️ Error guardando log: {e}")
            
    def get_statistics(self):
        """Calcula estadísticas de aprendizaje"""
        if not self.operations:
            return None
            
        wins = sum(1 for op in self.operations if op.get('result') == 'WIN')
        losses = sum(1 for op in self.operations if op.get('result') == 'LOSS')
        total = len(self.operations)
        
        return {
            'total_operations': total,
            'wins': wins,
            'losses': losses,
            'win_rate': (wins / total * 100) if total > 0 else 0,
            'avg_rsi_wins': self._avg_indicator('rsi', 'WIN'),
            'avg_rsi_losses': self._avg_indicator('rsi', 'LOSS'),
        }
        
    def _avg_indicator(self, indicator, result_type):
        """Calcula promedio de un indicador para un tipo de resultado"""
        values = [op['indicators'][indicator] for op in self.operations 
                  if op.get('result') == result_type and indicator in op.get('indicators', {})]
        return sum(values) / len(values) if values else 0

def run_bot_with_learning(max_operations=50):
    """
    Ejecuta el bot con aprendizaje continuo
    Registra cada operación con todos los detalles
    """
    print("\n" + "=" * 70)
    print(" 🤖 BOT DE TRADING CON APRENDIZAJE CONTINUO")
    print("=" * 70)
    
    # Inicializar componentes
    broker = Config.BROKER_NAME or "exnova"
    print(f"\n[1] Inicializando componentes...")
    print(f"   Broker: {broker.upper()}")
    print(f"   Operaciones máximas: {max_operations}")
    
    market_data = MarketDataHandler(broker_name=broker, account_type=Config.ACCOUNT_TYPE)
    feature_engineer = FeatureEngineer()
    # agent = RLAgent(model_path=Config.MODEL_PATH)  # No necesario - usamos solo optimizador
    risk_manager = RiskManager(Config.CAPITAL_PER_TRADE, Config.STOP_LOSS_PCT, Config.TAKE_PROFIT_PCT)
    logger = TradingLogger()
    
    # Conectar
    print("\n[2] Conectando...")
    if broker == "iq":
        connected = market_data.connect(Config.IQ_EMAIL, Config.IQ_PASSWORD)
    else:
        connected = market_data.connect(Config.EX_EMAIL, Config.EX_PASSWORD)
        
    if not connected:
        print("❌ No se pudo conectar")
        return
        
    print("✅ Conectado")
    
    # Cargar modelo
    print("\n[3] Sistema de estrategia basado en confluencia de indicadores")
    print("   ✅ No requiere modelo RL - Opera con análisis técnico puro")
        
    # Variables de control
    asset = "EURUSD-OTC"
    operations_count = 0
    
    print(f"\n[4] Iniciando trading en {asset}...")
    print("   Presiona Ctrl+C para detener\n")
    
    try:
        while operations_count < max_operations:
            print(f"\n{'='*70}")
            print(f"OPERACIÓN #{operations_count + 1}/{max_operations}")
            print(f"{'='*70}")
            
            # A. Obtener datos
            print("\n📥 Obteniendo datos de mercado...")
            df = market_data.get_candles(asset, 60, 100)
            
            if df.empty:
                print("❌ Error obteniendo datos. Reintentando en 5s...")
                time.sleep(5)
                continue
                
            current_price = df.iloc[-1]['close']
            print(f"   Precio actual: {current_price:.5f}")
            
            # B. Calcular indicadores
            print("🧮 Calculando indicadores...")
            try:
                df_features = feature_engineer.prepare_for_rl(df)
                
                # Extraer indicadores actuales
                indicators = {
                    'rsi': float(df_features.iloc[-1]['rsi']),
                    'macd': float(df_features.iloc[-1]['macd']),
                    'bb_width': float(df_features.iloc[-1]['bb_width']),
                    'price': float(current_price),
                    'sma_20': float(df_features.iloc[-1]['sma_20']),
                    'sma_50': float(df_features.iloc[-1]['sma_50']),
                }
                
                print(f"   RSI: {indicators['rsi']:.2f}")
                print(f"   MACD: {indicators['macd']:.5f}")
                print(f"   BB Width: {indicators['bb_width']:.5f}")
                
            except Exception as e:
                print(f"❌ Error en indicadores: {e}")
                continue
                
            # C. Decisión de Trading (Solo Optimizador - No requiere modelo RL)
            print("🎯 Analizando estrategia de confluencia...")
            action = 0
            try:
                from strategies.optimizer import StrategyOptimizer
                
                # Usar SOLO el optimizador (no necesita modelo RL)
                action = StrategyOptimizer.get_confluence_signal(df_features)
                
                # Mostrar análisis detallado
                last = df_features.iloc[-1]
                print(f"   📊 Análisis de Confluencia:")
                
                # RSI
                if last['rsi'] < 30:
                    print(f"      ✅ RSI Sobrevendido: {last['rsi']:.2f} → Señal CALL")
                elif last['rsi'] > 70:
                    print(f"      ✅ RSI Sobrecomprado: {last['rsi']:.2f} → Señal PUT")
                else:
                    print(f"      ⚪ RSI Neutral: {last['rsi']:.2f}")
                    
                # Bandas Bollinger
                if last['close'] < last['bb_low']:
                    print(f"      ✅ Precio bajo BB inferior → Señal CALL")
                elif last['close'] > last['bb_high']:
                    print(f"      ✅ Precio sobre BB superior → Señal PUT")
                else:
                    print(f"      ⚪ Precio dentro de bandas")
                    
                # Tendencia
                if last['close'] > last['sma_50']:
                    print(f"      📈 Tendencia alcista (precio > SMA50)")
                else:
                    print(f"      📉 Tendencia bajista (precio < SMA50)")
                    
            except Exception as e:
                print(f"⚠️ Error en análisis: {e}")
                import traceback
                traceback.print_exc()
                
            actions_map = {0: "HOLD", 1: "CALL", 2: "PUT"}
            decision = actions_map.get(action, "HOLD")
            print(f"   DECISIÓN: {decision}")
            
            # D. Ejecutar operación
            if action in [1, 2]:
                direction = "call" if action == 1 else "put"
                amount = risk_manager.get_trade_amount()
                
                print(f"\n🚀 Ejecutando {direction.upper()} de ${amount:.2f}...")
                
                # Registrar datos PRE-operación
                operation_data = {
                    'operation_number': operations_count + 1,
                    'asset': asset,
                    'direction': direction,
                    'amount': amount,
                    'indicators': indicators,
                    'decision_source': 'RL+Optimizer',
                    'entry_price': current_price,
                }
                
                # Ejecutar
                try:
                    print(f"   📡 Enviando orden al broker {broker.upper()}...")
                    print(f"   Parámetros: Asset={asset}, Amount=${amount}, Direction={direction}, Duration=1min")
                    
                    if broker == "iq":
                        status, order_id = market_data.api.buy(amount, asset, direction, 1)
                    else:
                        # Exnova usa buy_digital_spot
                        status, order_id = market_data.api.buy_digital_spot(asset, amount, direction, 1)
                    
                    print(f"   📋 Respuesta del broker: Status={status}, OrderID={order_id}")
                        
                except Exception as e:
                    print(f"   ❌ EXCEPCIÓN al ejecutar: {e}")
                    import traceback
                    traceback.print_exc()
                    status = False
                    order_id = f"ERROR: {e}"
                    
                if status:
                    print(f"✅ Operación enviada exitosamente")
                    print(f"   🆔 Order ID: {order_id}")
                    print(f"   💰 Monto: ${amount}")
                    print(f"   📊 Dirección: {direction.upper()}")
                    print(f"   ⏰ Duración: 1 minuto")
                    operation_data['order_id'] = str(order_id)
                    
                    print("\n⏳ Esperando resultado (65s)...")
                    time.sleep(65)
                    
                    # Verificar resultado
                    profit = 0
                    if broker == "iq":
                        profit = market_data.api.check_win_v3(order_id)
                    else:
                        try:
                            profit = market_data.api.check_win_v3(order_id)
                        except:
                            try:
                                status_win, profit_val = market_data.api.check_win_v4(order_id)
                                profit = profit_val
                            except:
                                profit = 0
                                
                    # Obtener precio de salida
                    df_exit = market_data.get_candles(asset, 60, 10)
                    exit_price = df_exit.iloc[-1]['close'] if not df_exit.empty else current_price
                    
                    # Registrar resultado
                    operation_data['exit_price'] = float(exit_price)
                    operation_data['profit'] = float(profit)
                    
                    if profit > 0:
                        print(f"\n🎉 GANADA - Profit: ${profit:.2f}")
                        operation_data['result'] = 'WIN'
                        risk_manager.update_trade_result(profit)
                    elif profit < 0:
                        print(f"\n😞 PERDIDA - Loss: ${abs(profit):.2f}")
                        operation_data['result'] = 'LOSS'
                        risk_manager.update_trade_result(profit)
                    else:
                        print(f"\n😐 EMPATE")
                        operation_data['result'] = 'TIE'
                        
                    # Análisis post-operación
                    price_movement = exit_price - current_price
                    operation_data['price_movement'] = float(price_movement)
                    operation_data['predicted_correctly'] = (
                        (direction == 'call' and price_movement > 0) or
                        (direction == 'put' and price_movement < 0)
                    )
                    
                    # Guardar en log
                    logger.log_operation(operation_data)
                    
                    # Mostrar aprendizaje
                    print("\n📊 ANÁLISIS DE LA OPERACIÓN:")
                    print(f"   Movimiento del precio: {price_movement:+.5f}")
                    print(f"   Predicción correcta: {'✅ SÍ' if operation_data['predicted_correctly'] else '❌ NO'}")
                    
                    operations_count += 1
                    
                else:
                    print(f"❌ Error ejecutando operación")
                    print(f"   Detalles: {order_id}")
                    
            else:
                print("⏸️ Sin señal clara. Esperando 10s...")
                time.sleep(10)
                
            # Mostrar estadísticas cada 5 operaciones
            if operations_count > 0 and operations_count % 5 == 0:
                stats = logger.get_statistics()
                print(f"\n{'='*70}")
                print("📈 ESTADÍSTICAS DE APRENDIZAJE")
                print(f"{'='*70}")
                print(f"Operaciones: {stats['total_operations']}")
                print(f"Ganadas: {stats['wins']}")
                print(f"Perdidas: {stats['losses']}")
                print(f"Win Rate: {stats['win_rate']:.2f}%")
                print(f"RSI promedio (ganadas): {stats['avg_rsi_wins']:.2f}")
                print(f"RSI promedio (perdidas): {stats['avg_rsi_losses']:.2f}")
                print(f"{'='*70}\n")
                
    except KeyboardInterrupt:
        print("\n\n⚠️ Detenido por el usuario")
        
    # Resumen final
    print("\n" + "=" * 70)
    print("📊 RESUMEN FINAL")
    print("=" * 70)
    
    stats = logger.get_statistics()
    if stats:
        print(f"Total de operaciones: {stats['total_operations']}")
        print(f"Ganadas: {stats['wins']}")
        print(f"Perdidas: {stats['losses']}")
        print(f"Win Rate: {stats['win_rate']:.2f}%")
        print(f"\n✅ Log guardado en: {logger.log_file}")
        print("   Analiza el archivo JSON para ver todos los detalles")
    else:
        print("No se ejecutaron operaciones")
        
    print("\n💡 PRÓXIMOS PASOS:")
    print("   1. Analiza 'data/operaciones_log.json' para ver patrones")
    print("   2. Identifica qué indicadores funcionan mejor")
    print("   3. Ajusta el umbral del optimizador según resultados")
    print("   4. Re-entrena el modelo con: python train_bot.py")

if __name__ == "__main__":
    run_bot_with_learning(max_operations=50)
