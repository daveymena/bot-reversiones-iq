"""
🧠 SISTEMA DE APRENDIZAJE CONTINUO - TRADING INTELIGENTE
Opera en cuenta DEMO, analiza resultados, y aprende patrones reales del mercado
"""
import time
import json
from datetime import datetime
from pathlib import Path
import os
import sys
sys.path.insert(0, '.')

from observe_market import MarketObserver
from strategies.breakout_momentum import BreakoutMomentumStrategy
from strategies.smart_reversal import SmartReversalStrategy
from strategies.trend_following import TrendFollowingStrategy
from optimize_knowledge import KnowledgeOptimizer
from ai.llm_client import LLMClient
import config

class IntelligentLearningSystem:
    """
    Sistema que opera en DEMO y aprende de cada operación
    """
    
    def __init__(self):
        self.observer = MarketObserver()
        self.breakout_strategy = BreakoutMomentumStrategy()
        self.reversal_strategy = SmartReversalStrategy()
        self.trend_strategy = TrendFollowingStrategy()
        
        # Priorizar EUR/USD (más líquido y predecible)
        self.priority_assets = [
            "EURUSD-OTC",    # Prioridad 1 - Más líquido
            "GBPUSD-OTC",    # Prioridad 2
            "USDJPY-OTC",    # Prioridad 3
            "USDCAD-OTC",    # Prioridad 4
            "AUDUSD-OTC",    # Prioridad 5
            "EURJPY-OTC",    # Prioridad 6
        ]
        
        # Base de conocimiento
        self.learning_database = {
            'operations': [],
            'patterns_found': {},
            'asset_statistics': {},
            'timing_analysis': {},
            'success_factors': [],
            'config': {
                'base_threshold': 75.0,
                'min_win_rate_target': 0.65
            }
        }
        
        # Archivo de aprendizaje
        self.learning_file = Path("data/learning_database.json")
        self.active_trades = {}
        self.llm = LLMClient() if config.Config.USE_LLM else None
        self.load_learning_database()
    
    def load_learning_database(self):
        """Carga la base de conocimiento existente"""
        if self.learning_file.exists():
            try:
                with open(self.learning_file, 'r', encoding='utf-8') as f:
                    self.learning_database = json.load(f)
                print(f"✅ Base de conocimiento cargada: {len(self.learning_database.get('operations', []))} operaciones")
            except Exception as e:
                print(f"⚠️ Error cargando base de conocimiento: {e}")
    
    def save_learning_database(self):
        """Guarda la base de conocimiento"""
        try:
            self.learning_file.parent.mkdir(exist_ok=True)
            with open(self.learning_file, 'w', encoding='utf-8') as f:
                json.dump(self.learning_database, f, indent=2, default=str)
            print(f"💾 Base de conocimiento guardada")
        except Exception as e:
            print(f"⚠️ Error guardando: {e}")
    
    def analyze_all_assets_deep(self):
        """
        Análisis profundo de todos los activos
        Identifica:
        - Subidas y bajadas recientes
        - Timing de reversiones
        - Patrones de comportamiento
        """
        print("\n" + "="*80)
        print("🔍 ANÁLISIS PROFUNDO DE MÚLTIPLES DIVISAS")
        print("="*80)
        
        analysis_results = []
        
        for asset in self.priority_assets:
            print(f"\n📊 Analizando {asset}...")
            
            try:
                # Obtener datos históricos (últimas 200 velas)
                df = self.observer.market_data.get_candles(asset, 60, 200, time.time())
                
                print(f"   💡 Velas obtenidas para {asset}: {len(df)}")
                
                if df.empty or len(df) < 100:
                    print(f"   ⚠️ Datos insuficientes")
                    continue
                
                # Aplicar indicadores
                df = self.observer.feature_engineer.prepare_for_rl(df)
                
                # Análisis de movimientos
                movement_analysis = self.analyze_movements(df, asset)
                
                # Análisis de timing
                timing_analysis = self.analyze_timing_patterns(df, asset)
                
                # Análisis de múltiples estrategias
                breakout_analysis = self.breakout_strategy.analyze(df)
                reversal_analysis = self.reversal_strategy.analyze(df)
                trend_analysis = self.trend_strategy.analyze(df)
                
                # Elegir la mejor señal
                strategies = [breakout_analysis, reversal_analysis, trend_analysis]
                best_strat = max(strategies, key=lambda x: x['confidence'])
                
                result = {
                    'asset': asset,
                    'timestamp': datetime.now(),
                    'movement': movement_analysis,
                    'timing': timing_analysis,
                    'strategy': best_strat,
                    'all_strategies': {
                        'breakout': breakout_analysis,
                        'reversal': reversal_analysis,
                        'trend': trend_analysis
                    },
                    'current_price': df.iloc[-1]['close']
                }
                
                # Aplicar aprendizaje dinámico
                result = self.apply_learned_filters(result)
                
                analysis_results.append(result)
                
                # Mostrar resumen
                self.print_asset_summary(result)
                
                time.sleep(1)  # Pausa entre activos
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                continue
        
        return analysis_results

    def apply_learned_filters(self, result):
        """
        Refina la confianza de la estrategia basándose en los patrones aprendidos
        """
        patterns = self.learning_database.get('patterns_found', {})
        if not patterns:
            return result

        asset = result['asset']
        strategy = result['strategy']
        volatility = result['movement'].get('volatility_pct', 0)
        
        # 1. Filtro de Volatilidad Mínima Ganadora
        # OTC suele tener baja volatilidad, bajamos el muro de 0.075 a 0.03
        min_vol = patterns.get('volatility_correlation', {}).get('min_win_volatility', 0.03)
        if volatility < min_vol:
            # Si no hay suficiente "fuerza", bajamos la confianza drásticamente
            strategy['confidence'] *= 0.5
            strategy['reason'] += f" (Baja Volatilidad: {volatility:.3f}% < {min_vol:.3f}%)"

        # 2. Bono por Activo Estrella
        best_assets = patterns.get('best_assets', {})
        if asset in best_assets and best_assets[asset] > 0:
            # Si el activo ha sido rentable, subimos la confianza
            strategy['confidence'] *= 1.1
            strategy['reason'] += " (Activo Rentable)"

        # 3. Penalización por Estrategia Débil
        strat_perf = patterns.get('strategy_performance', {})
        strat_name = strategy.get('strategy')
        if strat_name in strat_perf and strat_perf[strat_name] < 0.3:
            # Si la estrategia gana menos del 30%, bajamos confianza
            strategy['confidence'] *= 0.8
            strategy['reason'] += f" (Bajo rendimiento: {strat_perf[strat_name]*100:.0f}%)"

        # Asegurar límites
        strategy['confidence'] = min(round(strategy['confidence'], 1), 99.0)
        
        return result
    
    def get_adaptive_threshold(self):
        """
        Calcula un umbral de confianza adaptativo basado en el rendimiento reciente
        """
        ops = self.learning_database.get('operations', [])
        if len(ops) < 10:
            return 75.0  # Umbral base inicial
        
        # Analizar últimas 20 operaciones con resultado
        history = [o for o in ops if o.get('result') in ['win', 'loose']]
        recent_ops = history[-20:]
        
        if len(recent_ops) < 5:
            return 70.0  # Umbral base más bajo para empezar
            
        wins = len([o for o in recent_ops if o.get('result') == 'win'])
        total = len(recent_ops)
        win_rate = wins / total
        
        base = 70.0 # Bajamos la base de 75 a 70
        
        if win_rate < 0.40:
            # Rendimiento muy pobre, subir exigencia pero no tanto
            adjustment = 10.0
            print(f"⚠️ RENDIMIENTO BAJO ({win_rate*100:.0f}% WR). Ajustando filtros de seguridad.")
        elif win_rate < 0.60:
            # Rendimiento regular, equilibrio entre aprendizaje y seguridad
            adjustment = 5.0
            print(f"📉 FASE DE APRENDIZAJE ({win_rate*100:.0f}% WR). Manteniendo cautela.")
        elif win_rate > 0.85:
            # Rendimiento excelente, ser más flexible
            adjustment = -5.0
            print(f"🔥 RENDIMIENTO EXCELENTE ({win_rate*100:.0f}% WR). Maximizando oportunidades.")
        else:
            adjustment = 0
            
        final_threshold = max(65.0, min(80.0, base + adjustment))
        print(f"🧠 AJUSTE INTELIGENTE: Umbral adaptativo optimizado en {final_threshold}%")
        return final_threshold
    
    def analyze_movements(self, df, asset):
        """
        Analiza movimientos de subida y bajada
        """
        if len(df) < 50:
            return {}
        
        # Últimas 50 velas
        recent = df.tail(50)
        
        # Contar velas alcistas y bajistas
        bullish_candles = len(recent[recent['close'] > recent['open']])
        bearish_candles = len(recent[recent['close'] < recent['open']])
        
        # Calcular movimiento total
        price_start = recent.iloc[0]['close']
        price_end = recent.iloc[-1]['close']
        total_movement = ((price_end - price_start) / price_start) * 100
        
        # Identificar reversiones
        reversals = 0
        for i in range(1, len(recent)):
            prev_trend = "up" if recent.iloc[i-1]['close'] > recent.iloc[i-1]['open'] else "down"
            curr_trend = "up" if recent.iloc[i]['close'] > recent.iloc[i]['open'] else "down"
            if prev_trend != curr_trend:
                reversals += 1
        
        # Volatilidad
        volatility = recent['close'].std() / recent['close'].mean() * 100
        
        return {
            'bullish_candles': bullish_candles,
            'bearish_candles': bearish_candles,
            'total_movement_pct': total_movement,
            'reversals': reversals,
            'volatility_pct': volatility,
            'trend': 'ALCISTA' if total_movement > 0.1 else 'BAJISTA' if total_movement < -0.1 else 'LATERAL'
        }
    
    def analyze_timing_patterns(self, df, asset):
        """
        Analiza patrones de timing:
        - ¿Cuánto tiempo dura una subida?
        - ¿Cuánto tiempo dura una bajada?
        - ¿Cuándo ocurren las reversiones?
        """
        if len(df) < 20:
            return {}
        
        # Identificar rachas alcistas y bajistas
        streaks = []
        current_streak = {'type': None, 'length': 0, 'start_price': None, 'end_price': None}
        
        for i, row in df.tail(50).iterrows():
            candle_type = 'bullish' if row['close'] > row['open'] else 'bearish'
            
            if current_streak['type'] == candle_type:
                current_streak['length'] += 1
                current_streak['end_price'] = row['close']
            else:
                if current_streak['type'] is not None:
                    streaks.append(current_streak.copy())
                current_streak = {
                    'type': candle_type,
                    'length': 1,
                    'start_price': row['open'],
                    'end_price': row['close']
                }
        
        # Agregar última racha
        if current_streak['type'] is not None:
            streaks.append(current_streak)
        
        # Calcular promedios
        if streaks:
            bullish_streaks = [s for s in streaks if s['type'] == 'bullish']
            bearish_streaks = [s for s in streaks if s['type'] == 'bearish']
            
            avg_bullish_duration = sum(s['length'] for s in bullish_streaks) / len(bullish_streaks) if bullish_streaks else 0
            avg_bearish_duration = sum(s['length'] for s in bearish_streaks) / len(bearish_streaks) if bearish_streaks else 0
            
            return {
                'avg_bullish_duration_candles': avg_bullish_duration,
                'avg_bearish_duration_candles': avg_bearish_duration,
                'total_streaks': len(streaks),
                'longest_bullish': max([s['length'] for s in bullish_streaks]) if bullish_streaks else 0,
                'longest_bearish': max([s['length'] for s in bearish_streaks]) if bearish_streaks else 0,
                'current_streak': current_streak
            }
        
        return {}
    
    def print_asset_summary(self, result):
        """Imprime resumen del análisis de un activo"""
        asset = result['asset']
        movement = result['movement']
        timing = result['timing']
        strategy = result['strategy']
        
        print(f"\n   📈 MOVIMIENTO:")
        print(f"      Tendencia: {movement.get('trend', 'N/A')}")
        print(f"      Velas alcistas: {movement.get('bullish_candles', 0)}")
        print(f"      Velas bajistas: {movement.get('bearish_candles', 0)}")
        print(f"      Movimiento total: {movement.get('total_movement_pct', 0):.3f}%")
        print(f"      Reversiones: {movement.get('reversals', 0)}")
        print(f"      Volatilidad: {movement.get('volatility_pct', 0):.3f}%")
        
        print(f"\n   ⏱️ TIMING:")
        print(f"      Duración promedio subida: {timing.get('avg_bullish_duration_candles', 0):.1f} velas")
        print(f"      Duración promedio bajada: {timing.get('avg_bearish_duration_candles', 0):.1f} velas")
        print(f"      Racha actual: {timing.get('current_streak', {}).get('type', 'N/A')} ({timing.get('current_streak', {}).get('length', 0)} velas)")
        
        print(f"\n   🎯 ESTRATEGIA:")
        print(f"      Acción: {strategy.get('action', 'WAIT')}")
        if strategy.get('action') != 'WAIT':
            print(f"      Tipo: {strategy.get('strategy', 'N/A')}")
            print(f"      Confianza: {strategy.get('confidence', 0)}%")
            print(f"      Razón: {strategy.get('reason', 'N/A')}")
    
    def continuous_learning_session(self, duration_minutes=60, operations_target=20):
        """
        Sesión de aprendizaje continuo
        Opera múltiples veces y aprende de cada resultado
        """
        print("\n" + "="*80)
        print(f"🧠 SESIÓN DE APRENDIZAJE CONTINUO")
        print(f"   Duración: {duration_minutes} minutos")
        print(f"   Objetivo: {operations_target} operaciones")
        print("="*80)
        
        # Conectar
        if not self.observer.connect():
            print("❌ No se pudo conectar")
            return
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        operations_completed = 0
        
        while time.time() < end_time and operations_completed < operations_target:
            iteration = operations_completed + 1
            
            print(f"\n{'='*80}")
            print(f"🔄 ITERACIÓN #{iteration}")
            print(f"   Tiempo transcurrido: {(time.time() - start_time) / 60:.1f} minutos")
            print(f"   Operaciones completadas: {operations_completed}/{operations_target}")
            print(f"{'='*80}")
            
            # 1. Verificar resultados de operaciones activas
            self.check_active_trades_results()

            # 2. Análisis profundo
            analysis_results = self.analyze_all_assets_deep()
            
            # 3. Encontrar mejor oportunidad
            best_opportunity = self.find_best_opportunity_from_analysis(analysis_results)
            
            if best_opportunity:
                # Registrar todas las oportunidades encontradas para análisis
                opportunity_record = {
                    'timestamp': datetime.now().isoformat(),
                    'asset': best_opportunity['asset'],
                    'strategy': best_opportunity['strategy'],
                    'movement': best_opportunity['movement'],
                    'timing': best_opportunity['timing'],
                    'current_price': best_opportunity['current_price'],
                    'executed': False,
                    'result': 'pending'
                }

                # --- REGLA: UNA OPERACIÓN POR ACTIVO ---
                active_assets = [t['asset'] for t in self.active_trades.values()]
                
                # Umbral Adaptativo: Se vuelve más estricto si perdemos
                current_threshold = self.get_adaptive_threshold()
                
                if best_opportunity['asset'] in active_assets:
                    print(f"\n⏸️ Omitiendo {best_opportunity['asset']}: Ya hay una operación activa. Esperando resultado para aprender.")
                    opportunity_record['reason_not_executed'] = "Operación activa en curso"
                elif best_opportunity['strategy']['confidence'] >= current_threshold:
                    
                    # --- VALIDACIÓN IA (LLM / GROQ / OLLAMA) ---
                    if self.llm:
                        print(f"🧠 Consultando IA para validación de timing...")
                        ai_analysis = self.llm.analyze_entry_timing(
                            df, 
                            best_opportunity['strategy']['action'],
                            best_opportunity['asset']
                        )
                        
                        if ai_analysis.get('is_optimal'):
                            print(f"✅ IA CONFIRMA ENTRADA: {ai_analysis.get('reasoning')}")
                            best_opportunity['strategy']['confidence'] *= (0.5 + ai_analysis.get('confidence', 0.5))
                            best_opportunity['strategy']['reason'] += f" | IA: {ai_analysis.get('reasoning')}"
                        else:
                            print(f"⚠️ IA RECOMIENDA ESPERAR: {ai_analysis.get('reasoning')}")
                            opportunity_record['reason_not_executed'] = f"IA: {ai_analysis.get('reasoning')}"
                            # No ejecutamos
                            self.learning_database['operations'].append(opportunity_record)
                            time.sleep(1)
                            continue

                    print(f"\n🚀 EJECUTANDO OPERACIÓN REAL (DEMO):")
                    print(f"   Activo: {best_opportunity['asset']}")
                    print(f"   Acción: {best_opportunity['strategy']['action']}")
                    print(f"   Confianza: {best_opportunity['strategy']['confidence']}%")
                    
                    # Ejecutar en el broker
                    asset = best_opportunity['asset']
                    action = best_opportunity['strategy']['action'].lower()
                    amount = config.Config.CAPITAL_PER_TRADE
                    expiration = best_opportunity['strategy'].get('expiration', 60) # segundos
                    
                    # Exnovaapi espera minutos
                    expiration_minutes = max(1, round(expiration / 60))
                    
                    success, order_id = self.observer.market_data.api.buy(
                        amount, asset, action, expiration_minutes
                    )
                    
                    if success:
                        print(f"✅ Operación enviada exitosamente! ID: {order_id}")
                        opportunity_record['id'] = order_id
                        opportunity_record['executed'] = True
                        opportunity_record['expiration_time'] = time.time() + (expiration_minutes * 60) + 10
                        
                        self.active_trades[order_id] = opportunity_record
                        operations_completed += 1
                    else:
                        print(f"❌ Error al ejecutar: {order_id}")
                else:
                    print(f"\n⏸️ Oportunidad en {best_opportunity['asset']} con confianza {best_opportunity['strategy']['confidence']}% - Demasiado baja (requiere {current_threshold}%)")
                
                self.learning_database['operations'].append(opportunity_record)
            else:
                print(f"\n⏸️ No hay oportunidades claras en este momento")
            
            self.save_learning_database()
            
            # --- AUTO-OPTIMIZACIÓN ---
            # Cada 5 operaciones, re-analizar patrones para mejorar
            if operations_completed > 0 and operations_completed % 5 == 0:
                print("\n🧠 Optimizando conocimiento con datos recientes...")
                optimizer = KnowledgeOptimizer()
                optimizer.analyze_patterns()
                # Recargar la base de datos interna para aplicar los nuevos filtros
                with open(self.learning_file, 'r', encoding='utf-8') as f:
                    self.learning_database = json.load(f)
                print("✅ Filtros de inteligencia actualizados automáticamente.")

            # Esperar antes de la siguiente iteración
            wait_time = 20  # 20 segundos
            print(f"\n⏳ Esperando {wait_time} segundos antes de la siguiente iteración...")
            time.sleep(wait_time)
        
        # Mostrar resumen final
        self.show_learning_summary()

    def check_active_trades_results(self):
        """Verifica los resultados de las operaciones que ya expiraron"""
        if not self.active_trades:
            return

        current_time = time.time()
        completed = []

        for trade_id, trade in self.active_trades.items():
            if current_time >= trade['expiration_time']:
                print(f"\n📊 Verificando resultado de ID: {trade_id} ({trade['asset']})")
                
                try:
                    # check_win_v4 retorna (status, profit)
                    # status puede ser "win", "loose", "equal", None si no terminó
                    status, profit = self.observer.market_data.api.check_win_v4(trade_id, timeout=10)
                    
                    if status is not None:
                        result_text = "GANADA ✅" if status == "win" else "PERDIDA ❌" if status == "loose" else "EMPATE ⚪"
                        print(f"   Resultado: {result_text} (Profit: ${profit:.2f})")
                        
                        # Actualizar en la base de datos de aprendizaje
                        for op in self.learning_database['operations']:
                            if op.get('id') == trade_id:
                                op['result'] = status
                                op['profit'] = profit
                                break
                        
                        completed.append(trade_id)
                    else:
                        print(f"   Aún esperando resultado...")
                except Exception as e:
                    print(f"   ⚠️ Error verificando resultado: {e}")

        # Limpiar activas
        for tid in completed:
            del self.active_trades[tid]
    
    def find_best_opportunity_from_analysis(self, analysis_results):
        """
        Encuentra la mejor oportunidad de todas las analizadas
        """
        opportunities = []
        
        for result in analysis_results:
            if result['strategy']['action'] != 'WAIT':
                opportunities.append(result)
        
        if not opportunities:
            return None
        
        # Ordenar por confianza
        best = max(opportunities, key=lambda x: x['strategy']['confidence'])
        return best
    
    def show_learning_summary(self):
        """Muestra resumen de todo lo aprendido"""
        print(f"\n{'='*80}")
        print(f"📊 RESUMEN DE APRENDIZAJE")
        print(f"{'='*80}")
        
        total_ops = len(self.learning_database['operations'])
        print(f"\nTotal de oportunidades identificadas: {total_ops}")
        
        if total_ops > 0:
            # Agrupar por activo
            by_asset = {}
            for op in self.learning_database['operations']:
                asset = op.get('asset') or op.get('opportunity', {}).get('asset', 'Unknown')
                if asset not in by_asset:
                    by_asset[asset] = []
                by_asset[asset].append(op)
            
            print(f"\n📈 Por activo:")
            for asset, ops in sorted(by_asset.items(), key=lambda x: len(x[1]), reverse=True):
                wins = len([o for o in ops if o.get('result') == 'win'])
                losses = len([o for o in ops if o.get('result') == 'loose'])
                print(f"   {asset}: {len(ops)} ops ({wins}W-{losses}L)")
            
            # Agrupar por acción
            by_action = {}
            for op in self.learning_database['operations']:
                action = op.get('action') or op.get('opportunity', {}).get('strategy', {}).get('action') or 'WAIT'
                if action not in by_action:
                    by_action[action] = []
                by_action[action].append(op)
            
            print(f"\n🎯 Por tipo de operación:")
            for action, ops in by_action.items():
                print(f"   {action}: {len(ops)} ops")
        
        print(f"\n💾 Base de conocimiento guardada en: {self.learning_file}")


def main():
    """Función principal"""
    system = IntelligentLearningSystem()
    
    print("\n" + "="*80)
    print("🧠 SISTEMA DE APRENDIZAJE INTELIGENTE")
    print("="*80)
    print("\nOpciones:")
    print("1. Análisis profundo de todas las divisas (una vez)")
    print("2. Sesión de aprendizaje continuo (múltiples análisis)")
    print("3. Ver resumen de aprendizaje actual")
    
    try:
        choice = input("\nElige una opción (1-3): ").strip()
        
        if choice == "1":
            # Conectar
            if not system.observer.connect():
                print("❌ No se pudo conectar")
                return
            
            # Análisis profundo
            results = system.analyze_all_assets_deep()
            
            # Guardar resultados
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = Path(f"data/deep_analysis_{timestamp}.json")
            report_file.parent.mkdir(exist_ok=True)
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, default=str)
            
            print(f"\n💾 Análisis guardado en: {report_file}")
        
        elif choice == "2":
            duration = input("¿Cuántos minutos? (default: 60): ").strip()
            duration = int(duration) if duration else 60
            
            operations = input("¿Cuántas operaciones objetivo? (default: 20): ").strip()
            operations = int(operations) if operations else 20
            
            system.continuous_learning_session(duration, operations)
        
        elif choice == "3":
            system.show_learning_summary()
        
        elif choice == "4":
            print("\n🚀 Iniciando Sesión Headless (24/7)...")
            system.continuous_learning_session(1440, 100) # 24 horas, 100 ops
        
        else:
            print("❌ Opción inválida")
    
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrumpido por el usuario")
        system.show_learning_summary()
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Soporte para modo no interactivo (Docker/Easypanel)
    if os.getenv("HEADLESS_MODE", "false").lower() == "true":
        print("🤖 MODO HEADLESS ACTIVADO")
        system_main = IntelligentLearningSystem()
        # Automatizar inicio de sesión de aprendizaje
        # 1440 minutos = 24 horas
        system_main.continuous_learning_session(1440, 200)
    else:
        main()
