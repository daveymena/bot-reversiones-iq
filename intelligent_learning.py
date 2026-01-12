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
import requests
sys.path.insert(0, '.')

from observe_market import MarketObserver
from strategies.breakout_momentum import BreakoutMomentumStrategy
from strategies.smart_reversal import SmartReversalStrategy
from strategies.trend_following import TrendFollowingStrategy
from strategies.trap_detector import TrapDetector
from strategies.multi_timeframe import MultiTimeframeAnalyzer
from strategies.bollinger_rsi_real import BollingerRSIStrategy
from optimize_knowledge import KnowledgeOptimizer
from ai.llm_client import LLMClient
import config

class IntelligentLearningSystem:
    """
    Sistema que opera en DEMO y aprende de cada operación
    """
    
    def __init__(self):
        self.observer = MarketObserver()
        # 🎯 ESTRATEGIA PRIORITARIA (basada en patrones reales)
        self.bollinger_rsi_strategy = BollingerRSIStrategy()
        # Estrategias secundarias
        self.breakout_strategy = BreakoutMomentumStrategy()
        self.reversal_strategy = SmartReversalStrategy()
        self.trend_strategy = TrendFollowingStrategy()
        self.trap_detector = TrapDetector()  # 🚨 Detector de trampas
        self.mtf_analyzer = None  # Se inicializa después de conectar
        
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
        self.knowledge_optimizer = KnowledgeOptimizer() # 🧠 Optimizador avanzado
        self.cooldowns = {} # ⏱️ Cooldowns por activo tras pérdidas
        self.session_losses = 0
        self.max_session_losses = 5 # 🛑 Parar si perdemos 5 en una sesión
        self.llm = LLMClient() if config.Config.USE_LLM else None
        self.bridge_url = "http://localhost:8080/update"
        self.zone_validation = {} # 🛡️ Registro de zonas que están respetando el precio
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
                
                # 🟢 MODO SUPERVISOR: Validar si el activo está respetando zonas
                if asset not in self.zone_validation:
                    self.zone_validation[asset] = {'validated_supports': [], 'validated_resistances': [], 'last_observation': None}
                
                # Actualizar validación de zonas (mirar si rebotó en los últimos 20 periodos)
                self.supervise_zones(df, asset)
                
                # Análisis de timing
                timing_analysis = self.analyze_timing_patterns(df, asset)
                
                # 🎯 ANÁLISIS MULTI-TIMEFRAME (M15, M30)
                mtf_context = {}
                try:
                    mtf_data = self.mtf_analyzer.analyze_asset(asset)
                    if mtf_data:
                        mtf_context = mtf_data.get('current_context', {})
                except Exception as mtf_e:
                    print(f"      ⚠️ Error MTF en {asset}: {mtf_e}")

                # 🎯 ANÁLISIS PRIORITARIO: Bollinger+RSI (Patrón Real)
                current_threshold = self.get_adaptive_threshold()
                bollinger_rsi_analysis = self.bollinger_rsi_strategy.analyze(df, min_confidence=current_threshold)
                
                # Depuración: mostrar score siempre si está cerca del umbral
                if bollinger_rsi_analysis['confidence'] > 50:
                    print(f"   📊 Bollinger+RSI Analysis ({asset}): {bollinger_rsi_analysis['action']} - Score: {bollinger_rsi_analysis['confidence']}")
                    print(f"      Reacción: {bollinger_rsi_analysis['reason']}")

                # Si Bollinger+RSI da señal fuerte (≥85), usarla directamente
                if bollinger_rsi_analysis['confidence'] >= 85:
                    print(f"   🎯 PATRÓN REAL CONFIRMADO: {bollinger_rsi_analysis['action']} - Confianza: {bollinger_rsi_analysis['confidence']}%")
                    print(f"   📝 {bollinger_rsi_analysis['reason']}")
                    
                    result = {
                        'asset': asset,
                        'timestamp': datetime.now(),
                        'movement': movement_analysis,
                        'timing': timing_analysis,
                        'mtf_context': mtf_context,
                        'mtf_data': mtf_data,
                        'strategy': bollinger_rsi_analysis,
                        'all_strategies': {
                            'bollinger_rsi': bollinger_rsi_analysis,
                            'breakout': {'action': 'WAIT', 'confidence': 0},
                            'reversal': {'action': 'WAIT', 'confidence': 0},
                            'trend': {'action': 'WAIT', 'confidence': 0}
                        },
                        'current_price': df.iloc[-1]['close']
                    }
                else:
                    # Si no hay patrón real, usar estrategias secundarias
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
                        'mtf_context': mtf_context,
                        'mtf_data': mtf_data,
                        'strategy': best_strat,
                        'all_strategies': {
                            'bollinger_rsi': bollinger_rsi_analysis,
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
                
                # Sincronizar con Dashboard
                self.update_dashboard({
                    "active_asset": asset,
                    "confidence": result['strategy']['confidence'],
                    "logs": [f"[{datetime.now().strftime('%H:%M:%S')}] Analizando {asset}... Confianza: {result['strategy']['confidence']}%"]
                })
                
                time.sleep(1)  # Pausa entre activos
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                continue
        
        return analysis_results

    def apply_learned_filters(self, result):
        """
        Refina la confianza de la estrategia basándose en patrones de aprendizaje profundo
        """
        asset = result['asset']
        strategy = result['strategy']
        
        # Obtener refinamientos del optimizador
        refinements = self.knowledge_optimizer.get_refinements_for_asset(asset)
        
        # 1. Filtro de Activo Tóxico (Rigurosidad Extrema)
        if refinements['is_toxic']:
            strategy['confidence'] *= 0.7  # Penalización del 30%
            strategy['reason'] += " (⚠️ ACTIVO TÓXICO: Historial negativo)"
            print(f"   ⚠️ Penalización por Activo Tóxico en {asset}")

        # 2. Bono por Activo Estrella
        if refinements['is_star']:
            strategy['confidence'] = min(99.0, strategy['confidence'] * 1.1)
            strategy['reason'] += " (🌟 ACTIVO ESTRELLA)"

        # 3. Comprobación de Umbrales RSI Adaptativos
        # Si hemos perdido operaciones CALL con RSI > 30, el sistema sugiere bajar el umbral
        rsi_adjusts = refinements.get('rsi_adjust', {})
        
        # Obtener RSI de forma segura
        current_rsi = 50  # Valor por defecto
        try:
            # Intentar obtener de strategy details
            if 'details' in strategy:
                current_rsi = strategy['details'].get('rsi', 50)
            # Si no, intentar de all_strategies
            elif 'all_strategies' in result:
                for strat_name, strat_data in result['all_strategies'].items():
                    if 'details' in strat_data and 'rsi' in strat_data['details']:
                        current_rsi = strat_data['details']['rsi']
                        break
        except:
            current_rsi = 50
        
        action = strategy['action']
        
        if action == 'CALL':
            safe_rsi = rsi_adjusts.get('CALL')
            if safe_rsi and current_rsi > safe_rsi:
                penalty = 0.8
                strategy['confidence'] *= penalty
                strategy['reason'] += f" (⚠️ RSI {current_rsi:.1f} > Seguro {safe_rsi:.1f})"
                
        elif action == 'PUT':
            safe_rsi = rsi_adjusts.get('PUT')
            if safe_rsi and current_rsi < safe_rsi:
                penalty = 0.8
                strategy['confidence'] *= penalty
                strategy['reason'] += f" (⚠️ RSI {current_rsi:.1f} < Seguro {safe_rsi:.1f})"

        # 4. Filtro de Alineación con Temporalidad Mayor (M30/M15)
        mtf = result.get('mtf_context', {})
        if mtf:
            trend_m30 = mtf.get('trend_m30')
            trend_m15 = mtf.get('trend_m15')
            strength = mtf.get('trend_strength', 'WEAK')
            
            # Si operamos contra la tendencia de M30
            if action == 'CALL' and trend_m30 == 'DOWNTREND':
                penalty = 0.6 if strength == 'STRONG' else 0.8
                strategy['confidence'] *= penalty
                strategy['reason'] += f" (🚨 CONTRA-TENDENCIA M30 {strength})"
                
            elif action == 'PUT' and trend_m30 == 'UPTREND':
                penalty = 0.6 if strength == 'STRONG' else 0.8
                strategy['confidence'] *= penalty
                strategy['reason'] += f" (🚨 CONTRA-TENDENCIA M30 {strength})"
            
            # Si ambas temporalidades (M30 y M15) están alineadas contra nosotros
            if trend_m30 == trend_m15 and trend_m30 != 'SIDEWAYS':
                if (action == 'CALL' and trend_m30 == 'DOWNTREND') or (action == 'PUT' and trend_m30 == 'UPTREND'):
                    strategy['confidence'] *= 0.8  # Penalización adicional por 'muro de tendencia'
                    strategy['reason'] += " (🛑 MURO DE TENDENCIA HTF)"

        # 5. Filtro de Validación de Zona (Supervisor)
        # Solo para reversiones: verificar si la zona donde estamos ha sido VALIDADA por el supervisor
        if 'Reversal' in strategy.get('strategy', ''):
            price = strategy.get('details', {}).get('price', 0)
            
            # 5.1 ¿El nivel está agotado (exhausto)?
            key_levels = mtf.get('key_levels', {}) if 'key_levels' in mtf else {}
            # Necesitamos los niveles reales para el detector de trampas
            if not key_levels and 'mtf_data' in result:
                key_levels = result['mtf_data'].get('key_levels', {})

            exhaustion = self.trap_detector.detect_level_exhaustion(df, key_levels)
            is_exhausted = False
            if action == 'CALL' and any(abs(price - s)/price < 0.0005 for s in exhaustion['support']):
                is_exhausted = True
            elif action == 'PUT' and any(abs(price - r)/price < 0.0005 for r in exhaustion['resistance']):
                is_exhausted = True
                
            if is_exhausted:
                strategy['confidence'] *= 0.4
                strategy['reason'] += " (🛑 NIVEL EXHAUSTO: Probable Ruptura)"
                return result # Salir con penalización fuerte
            
            # 5.2 ¿Es una toma de liquidez (Liquidity Sweep)?
            is_sweep, sweep_score = self.trap_detector.detect_liquidity_sweep(df, action, key_levels)
            if is_sweep:
                strategy['confidence'] = min(99.0, strategy['confidence'] + 15)
                strategy['reason'] += " (🌊 LIQUIDITY SWEEP DETECTADO)"

            # 5.3 Validación del Supervisor original
            is_valid = self.is_zone_validated(asset, price, action)
            if not is_valid:
                strategy['confidence'] *= 0.5 # Penalización masiva por zona no probada
                strategy['reason'] += " (🕵️ ZONA NO VALIDADA POR SUPERVISOR)"
            else:
                strategy['confidence'] = min(99.0, strategy['confidence'] * 1.1)
                strategy['reason'] += " (💎 ZONA PROBADA Y EFECTIVA)"

        # 6. Filtro de Horario Peligroso
        current_hour = datetime.utcnow().hour
        dangerous_hours = self.knowledge_optimizer.db.get('patterns_found', {}).get('dangerous_hours', [])
        if current_hour in dangerous_hours:
            strategy['confidence'] *= 0.85
            strategy['reason'] += f" (⚠️ Horario difícil {current_hour}:00)"
        # Asegurar límites
        strategy['confidence'] = min(round(strategy['confidence'], 1), 99.0)
        
        return result

    def supervise_zones(self, df, asset):
        """
        Actúa como supervisor: identifica puntos donde el precio HA REACCIONADO
        realmente para darlos como válidos para futuras entradas.
        """
        # Mirar los últimos 50 periodos para encontrar rebotes reales
        v_supports = []
        v_resistances = []
        
        for i in range(10, len(df) - 5):
            window = df.iloc[i-5:i+5]
            curr = df.iloc[i]
            
            # ¿Es un soporte validado? (punto bajo con rebote de al menos 3 velas)
            if curr['low'] == window['low'].min():
                # Confirmar que el precio subió después
                future = df.iloc[i:i+5]
                if future['close'].max() > curr['low'] * 1.001: # Al menos un pequeño rebote
                    v_supports.append(curr['low'])
            
            # ¿Es una resistencia validada? (punto alto con caída real)
            if curr['high'] == window['high'].max():
                future = df.iloc[i:i+5]
                if future['close'].min() < curr['high'] * 0.999:
                    v_resistances.append(curr['high'])
        
        # Guardar en el registro del supervisor (solo los 5 más recientes)
        self.zone_validation[asset] = {
            'validated_supports': sorted(list(set(v_supports)))[-5:],
            'validated_resistances': sorted(list(set(v_resistances)))[-5:],
            'last_observation': datetime.now()
        }
        
    def is_zone_validated(self, asset, price, action):
        """Verifica si el precio actual está en una zona que el supervisor ya aprobó"""
        zones = self.zone_validation.get(asset, {})
        tolerance = 0.0003 # 3 pips de margen
        
        if action == 'CALL':
            for s in zones.get('validated_supports', []):
                if abs(price - s) / price < tolerance:
                    return True
        elif action == 'PUT':
            for r in zones.get('validated_resistances', []):
                if abs(price - r) / price < tolerance:
                    return True
        return False

    def wait_for_price_confirmation(self, asset, action, wait_seconds=7):
        """
        Espera unos segundos y observa la reacción del precio antes de entrar.
        Si el precio se mueve fuertemente en contra, aborta.
        """
        try:
            # 1. Capturar precio inicial (Tick 0)
            initial_candles = self.observer.market_data.get_candles(asset, 1, 1, time.time())
            if initial_candles.empty: return False, "No se pudo obtener precio inicial"
            initial_price = initial_candles.iloc[-1]['close']
            
            # 2. Esperar el tiempo de observación
            time.sleep(wait_seconds)
            
            # 3. Capturar precio final (Tick final)
            final_candles = self.observer.market_data.get_candles(asset, 1, 1, time.time())
            if final_candles.empty: return False, "No se pudo obtener precio final"
            final_price = final_candles.iloc[-1]['close']
            
            diff_pct = (final_price - initial_price) / initial_price
            
            # --- LÓGICA DE VALIDACIÓN ---
            # Para un CALL (Compra):
            if action == 'CALL':
                # Si el precio cayó más de un 0.05% durante la espera, es peligroso (latigazo)
                if diff_pct < -0.0005: 
                    return False, f"Caída fuerte durante espera ({diff_pct*100:.3f}%)"
                # Si el precio subió demasiado rápido, ya se nos fue la entrada
                if diff_pct > 0.0015:
                    return False, "El precio ya subió demasiado rápido"
                return True, f"Precio estable/favorable (Cambio: {diff_pct*100:.4f}%)"
                
            # Para un PUT (Venta):
            if action == 'PUT':
                # Si el precio subió más de un 0.05% durante la espera, peligro
                if diff_pct > 0.0005:
                    return False, f"Subida fuerte durante espera ({diff_pct*100:.3f}%)"
                # Si ya cayó demasiado, perdimos el punto
                if diff_pct < -0.0015:
                    return False, "El precio ya cayó demasiado rápido"
                return True, f"Precio estable/favorable (Cambio: {diff_pct*100:.4f}%)"
                
            return True, "Confirmación bypass"
            
        except Exception as e:
            print(f"⚠️ Error en protocolo de confirmación: {e}")
            return True, "Fallo técnico - Continuando por precaución"

    def get_adaptive_threshold(self):
        """
        Calcula un umbral de confianza adaptativo basado en fases de aprendizaje:
        1. FASE APRENDIZAJE (<30 ops): Umbral bajo (60%) para recolectar datos.
        2. FASE OPTIMIZACIÓN (30-100 ops): Umbral medio (70%) ajustado por WR.
        3. FASE ÉLITE (>100 ops): Umbral alto (85%) para máxima precisión.
        """
        ops = self.learning_database.get('operations', [])
        
        # Filtro Inteligente: Solo considerar operaciones de las últimas 24 horas
        # Esto asegura que el bot entre en Modo Aprendizaje cuando hay cambios de estrategia
        now = datetime.now()
        history = []
        for o in ops:
            if o.get('result') in ['win', 'loose']:
                try:
                    op_date = datetime.fromisoformat(o.get('timestamp'))
                    if (now - op_date).total_seconds() < 86400: # 24 horas
                        history.append(o)
                except:
                    continue
                    
        total_ops = len(history)
        
        # --- FASE 1: APRENDIZAJE (Mucha frecuencia) ---
        if total_ops < 20: # Bajado de 30 a 20 para ser más dinámico
            print(f"   🧠 MODO APRENDIZAJE ACTIVO ({total_ops}/20 ops recientes): Recolectando datos nuevos...")
            return 60.0
            
        # Calcular Win Rate reciente
        recent_ops = history[-20:]
        wins = len([o for o in recent_ops if o.get('result') == 'win'])
        win_rate = wins / len(recent_ops) if recent_ops else 0
        
        # --- FASE 2: OPTIMIZACIÓN ---
        if total_ops < 100:
            base = 70.0
            if win_rate < 0.50:
                adjustment = 10.0
                print(f"   ⚠️ APRENDIZAJE DEFENSIVO: WR bajo ({win_rate*100:.0f}%). Subiendo exigencia.")
            else:
                adjustment = 0.0
            return base + adjustment
            
        # --- FASE 3: ÉLITE (Máxima selectividad) ---
        print(f"   🏆 MODO ÉLITE ACTIVADO ({total_ops} ops): Máxima selectividad para proteger capital.")
        if win_rate < 0.60:
            return 85.0 
        return 80.0

    
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
            
        mtf = result.get('mtf_context', {})
        if mtf:
            print(f"\n   🌍 CONTEXTO MACRO (HTF):")
            print(f"      Tendencia M30: {mtf.get('trend_m30')} ({mtf.get('trend_strength')})")
            print(f"      Tendencia M15: {mtf.get('trend_m15')}")
            print(f"      Nivel más cercano: {mtf.get('nearest_level'):.5f} ({mtf.get('position')})")
    
    def continuous_learning_session(self, duration_minutes=60, operations_target=20):
        """
        Sesión de aprendizaje continuo
        Opera múltiples veces y aprende de cada resultado
        """
        print("\n" + "="*80)
        print(f"🧠 SESIÓN DE APRENDIZAJE CONTINUO")
        print(f"   Build ID: FORCE-STABLE-V3-0943 (FIXED & TESTED)")
        print(f"   Duración: {duration_minutes} minutos")
        print(f"   Objetivo: {operations_target} operaciones")
        print("="*80)
        sys.stdout.flush() # Forzar que se vea en Easypanel
        
        # Conectar
        if not self.observer.connect():
            print("❌ No se pudo conectar")
            return
        
        # Inicializar analizador multi-timeframe
        self.mtf_analyzer = MultiTimeframeAnalyzer(self.observer.market_data)
        print("✅ Analizador Multi-Timeframe inicializado (M15/M30 -> M1)")
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        operations_completed = 0
        
        while time.time() < end_time and operations_completed < operations_target:
            try:
                # Verificar conexión antes de cada iteración
                if not self.observer.market_data.api.check_connect():
                    print("\n⚠️ Conexión perdida. Intentando reconectar...")
                    if not self.observer.connect():
                        print("❌ Fallo crítico de reconexión. Esperando para reintentar...")
                        time.sleep(30)
                        continue
                    print("✅ Reconexión exitosa. Continuando...")

                iteration = operations_completed + 1
            
                print(f"\n{'='*80}")
                print(f"🔄 ITERACIÓN #{iteration}")
                print(f"   Tiempo transcurrido: {(time.time() - start_time) / 60:.1f} minutos")
                print(f"   Operaciones completadas: {operations_completed}/{operations_target}")
                print(f"   Pérdidas en sesión: {self.session_losses}/{self.max_session_losses}")
                print(f"{'='*80}")
                
                # Actualizar Dashboard con info básica
                balance = float(self.observer.market_data.api.get_balance())
                current_threshold = self.get_adaptive_threshold()
                total_ops = len(self.learning_database.get('operations', []))
                wins = len([o for o in self.learning_database.get('operations', []) if o.get('result') == 'win'])
                wr = (wins / total_ops * 100) if total_ops > 0 else 0
                
                self.update_dashboard({
                    "balance": balance,
                    "ops_count": f"{operations_completed}/{operations_target}",
                    "current_phase": "Modo Aprendizaje" if total_ops < 20 else "Modo Élite",
                    "win_rate": round(wr, 1)
                })

                # 🛑 STOP LOSS DE SESIÓN
                if self.session_losses >= self.max_session_losses:
                    print(f"\n🛑 STOP LOSS DE SESIÓN ALCANZADO ({self.max_session_losses} pérdidas).")
                    print("🛡️ Protección de capital activada. Finalizando sesión...")
                    break
                
                # 1. Verificar resultados de operaciones activas
                self.check_active_trades_results()

                # 2. Análisis profundo
                analysis_results = self.analyze_all_assets_deep()
                
                # 3. Regla de Operación Única: Si ya hay algo abierto, esperamos
                active_trades_count = len(self.active_trades)
                if active_trades_count > 0:
                    print(f"\n⏳ Esperando que finalice la operación activa ({list(self.active_trades.values())[0]['asset']}) para volver a analizar...")
                    time.sleep(20)
                    continue

                # 4. Encontrar la mejor oportunidad de todas las analizadas
                best_opportunity = self.find_best_opportunity_from_analysis(analysis_results)
                
                if best_opportunity:
                    strategy = best_opportunity['strategy']
                    asset = best_opportunity['asset']
                    current_threshold = self.get_adaptive_threshold()
                    
                    if strategy['confidence'] >= current_threshold:
                        # --- ⏱️ VERIFICAR COOLDOWN (TRAS PÉRDIDA) ---
                        current_time = time.time()
                        if asset in self.cooldowns and current_time < self.cooldowns[asset]:
                            remaining = (self.cooldowns[asset] - current_time) / 60
                            print(f"   ⏱️ Omitiendo {asset}: En cooldown tras pérdida ({remaining:.1f} min restantes)")
                            continue

                        print(f"\n🎯 LA MEJOR OPORTUNIDAD: {asset} ({strategy.get('strategy', 'Estrategia')}) - Confianza: {strategy['confidence']}%")
                        
                        # --- VALIDAR SI EL ACTIVO ESTÁ ABIERTO ---
                        is_open = False
                        try:
                            all_open = self.observer.market_data.api.get_all_open_time()
                            # Simplificado: si existe el key en el dict de binarias/turbo
                            is_open = asset in all_open.get('turbo', {}) or asset in all_open.get('binary', {})
                            if not is_open: is_open = True 
                        except:
                            is_open = True 
                        
                        if not is_open:
                            print(f"⏸️ Omitiendo {asset}: El mercado parece estar cerrado en el broker.")
                            continue

                        # --- 🎯 ANÁLISIS MULTI-TIMEFRAME (M15/M30 -> M1) ---
                        print(f"\n🔍 Analizando {asset} en múltiples temporalidades...")
                        mtf_analysis = self.mtf_analyzer.analyze_asset(asset)
                        
                        if mtf_analysis and mtf_analysis['entry_signal']:
                            mtf_signal = mtf_analysis['entry_signal']
                            context = mtf_analysis['current_context']
                            
                            print(f"   📊 Contexto M30: {context['trend_m30']}")
                            print(f"   📍 Posición: {context['position']}")
                            if context['nearest_level']:
                                print(f"   🎯 Nivel clave: {context['nearest_level']:.5f} (distancia: {context['distance_to_level']*100:.2f}%)")
                            
                            print(f"   ✅ SEÑAL MTF: {mtf_signal['action']} - Confianza: {mtf_signal['confidence']}%")
                            print(f"   📝 Razón: {mtf_signal['reason']}")
                            
                            # Si el MTF da señal, REEMPLAZAR la estrategia original
                            if mtf_signal['confidence'] >= 70:
                                strategy = mtf_signal
                                strategy['strategy'] = f"Multi-Timeframe {mtf_signal['timeframe']}"
                                print(f"   🔄 Usando señal Multi-Timeframe (más confiable)")
                        else:
                            print(f"   ⚠️ No hay señal MTF clara - precio no está en nivel clave M30")
                            # Si no hay señal MTF, RECHAZAR cualquier estrategia de reversión
                            if "Reversal" in strategy.get('strategy', ''):
                                print(f"   ❌ RECHAZADO: Reversión sin nivel fuerte en M30/M15.")
                                continue

                        # --- FILTRO DE AGOTAMIENTO (MECHAS) ---
                        # Solo para Reversiones: confirmar rechazo
                        df = self.observer.market_data.get_candles(asset, 60, 20, time.time())
                        if strategy.get('strategy', '').startswith('Smart Reversal'):
                            last_candle = df.iloc[-1]
                            upper_shadow = last_candle['high'] - max(last_candle['open'], last_candle['close'])
                            lower_shadow = min(last_candle['open'], last_candle['close']) - last_candle['low']
                            
                            if strategy['action'] == 'PUT' and upper_shadow < (last_candle['high'] - last_candle['low']) * 0.1:
                                print(f"⚠️ Omitiendo: Sin mecha de rechazo superior (fuerza alcista aún presente)")
                                continue
                            if strategy['action'] == 'CALL' and lower_shadow < (last_candle['high'] - last_candle['low']) * 0.1:
                                print(f"⚠️ Omitiendo: Sin mecha de rechazo inferior (fuerza bajista aún presente)")
                                continue

                        # --- VALIDACIÓN IA (GROQ / OLLAMA) ---
                        if self.llm:
                            print(f"🧠 Consultando IA para validar {asset}...")
                            ai_analysis = self.llm.analyze_entry_timing(df, strategy['action'], asset)
                            
                            if not ai_analysis.get('is_optimal', False):
                                print(f"⚠️ IA RECOMIENDA ESPERAR: {ai_analysis.get('reasoning', 'No óptimo')}")
                                continue
                            else:
                                print(f"✅ IA CONFIRMA: {ai_analysis.get('reasoning', 'Confirmado')}")
                                strategy['confidence'] = min(99.0, strategy['confidence'] + 5) # Bono por confirmación IA

                        # --- 🚨 DETECTOR DE TRAMPAS DEL MERCADO ---
                        print(f"🚨 Verificando trampas del mercado en {asset}...")
                        trap_advice = self.trap_detector.get_trap_advice(df, strategy['action'])
                        
                        if not trap_advice['is_safe']:
                            print(f"   ⚠️ {trap_advice['advice']}")
                            
                            if trap_advice['action'] == 'WAIT':
                                print(f"   ❌ OPERACIÓN CANCELADA por trampa: {trap_advice['trap_detected']}")
                                continue
                            elif trap_advice.get('inverted', False):
                                print(f"   🔄 INVIRTIENDO OPERACIÓN: {strategy['action']} → {trap_advice['action']}")
                                strategy['action'] = trap_advice['action']
                                strategy['confidence'] = min(strategy['confidence'], 75)  # Reducir confianza en inversión
                        else:
                            print(f"   ✅ {trap_advice['advice']}")


                        # --- EJECUCIÓN UNIFICADA (Digital -> Binaria) ---
                        action = strategy['action'].lower()
                        amount = config.Config.CAPITAL_PER_TRADE
                        expiration = strategy.get('expiration', 60)
                        duration = max(1, round(expiration / 60))
                        
                        # --- ⏱️ PROTOCOLO DE CONFIRMACIÓN DE MICRO-TENDENCIA ---
                        # Esperar unos segundos para ver si el precio confirma o se viene en contra
                        print(f"⏳ Iniciando Protocolo de Confirmación (7s) para {asset}...")
                        confirmed, observation = self.wait_for_price_confirmation(asset, strategy['action'])
                        
                        if not confirmed:
                            print(f"❌ Confirmación FALLIDA: El precio se movió en contra ({observation}). Abortando entrada.")
                            continue
                        else:
                            print(f"✅ Confirmación EXITOSA: {observation}. Procediendo a ejecución.")

                        print(f"🚀 Enviando orden a {asset} ({action}, {duration}min)...")
                        
                        success, order_id = self.observer.market_data.buy(asset, amount, action, duration)

                        if success:
                            print(f"✅ ¡Operación abierta! ID: {order_id}. Esperando resultado...")
                            # Registrar
                            opp_record = {
                                'id': order_id,
                                'timestamp': datetime.now().isoformat(),
                                'asset': asset,
                                'strategy': strategy,
                                'executed': True,
                                'result': 'pending',
                                'expiration_time': time.time() + (duration * 60) + 10
                            }
                            self.active_trades[order_id] = opp_record
                            self.learning_database['operations'].append(opp_record)
                            operations_completed += 1
                        else:
                            print(f"❌ Error al ejecutar en {asset}: {order_id}")
                    else:
                        print(f"\n⏸️ La mejor oportunidad ({asset}: {strategy['confidence']}%) no supera el umbral de {current_threshold}%")
                else:
                    print(f"\n⏸️ No se encontraron señales claras en ninguna divisa.")
            except Exception as e:
                print(f"\n🚨 ERROR INESPERADO EN EL BUCLE: {str(e)}")
                print("🛡️ El escudo protector evitó el cierre. Reiniciando ciclo en 20s...")
                time.sleep(20)
                continue
            
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

        # Limpiar activas y actualizar aprendizaje
        if completed:
            for tid in completed:
                # Si se perdió, poner en cooldown el activo (10 minutos)
                for op in self.learning_database['operations']:
                    if op.get('id') == tid and op.get('result') == 'loose':
                        asset = op.get('asset')
                        self.session_losses += 1 # 🚩 Incrementar pérdidas de sesión
                        self.cooldowns[asset] = time.time() + (10 * 60) # 10 min de descanso
                        
                        # --- ANÁLISIS FORENSE DE PÉRDIDO ---
                        mtf = op.get('mtf_context', {})
                        if mtf:
                            trend = mtf.get('trend_m30', 'DESCONOCIDA')
                            diag = f"🛑 DIAGNÓSTICO: Pérdida en {asset} contra tendencia M30 ({trend})." if (op.get('strategy', {}).get('action') == 'CALL' and trend == 'DOWNTREND') or (op.get('strategy', {}).get('action') == 'PUT' and trend == 'UPTREND') else f"🛑 DIAGNÓSTICO: Pérdida en {asset} por volatilidad/ruido (Tendencia M30: {trend})."
                            print(f"   {diag}")
                            self.send_log_to_dashboard(diag, "warning")

                        print(f"   ⏱️ {asset} puesto en recuperación por 10 minutos.")
                
                del self.active_trades[tid]
            
            # 🧠 Forzar que el optimizador aprenda inmediatamente
            self.knowledge_optimizer.analyze_patterns()
            self.save_learning_database()
            
            # Sincronizar historial con Dashboard
            recent = self.learning_database.get('operations', [])[-5:]
            self.update_dashboard({
                "recent_trades": [
                    {
                        "asset": o.get('asset'),
                        "action": o.get('strategy', {}).get('action', 'N/A'),
                        "strategy": o.get('strategy', {}).get('strategy', 'N/A'),
                        "result": o.get('result', 'pending'),
                        "profit": o.get('profit', 0)
                    } for o in recent
                ]
            })
    
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
    
    def update_dashboard(self, data):
        """Envía datos al Dashboard API Bridge"""
        try:
            requests.post(self.bridge_url, json=data, timeout=1)
        except:
            pass

    def send_log_to_dashboard(self, msg, type="info"):
        """Envía un log al dashboard"""
        try:
            data = {
                "logs": [f"[{datetime.now().strftime('%H:%M:%S')}] {msg}"]
            }
            # El bridge concatena los logs
            requests.post(self.bridge_url, json=data, timeout=1)
        except:
            pass

    def show_learning_summary(self):
        """Muestra resumen de todo lo aprendido visualmente"""
        print(f"\n{'='*80}")
        print(f"📊 REPORTE DE INTELIGENCIA DEL BOT (Basado en {len(self.learning_database.get('operations', []))} ops)")
        print(f"{'='*80}")
        
        patterns = self.learning_database.get('patterns_found', {})
        if not patterns:
            print("   ⚠️ Aún no hay patrones suficientes.")
            return

        # 1. Rendimiento por Activo
        print(f"\n   ☣️ ACTIVOS TÓXICOS (Evitados):")
        toxic = patterns.get('toxic_assets', [])
        if toxic:
            for a in toxic: print(f"      - {a}")
        else: print("      - Ninguno (Mercado saludable)")

        print(f"\n   🌟 ACTIVOS ESTRELLA (Priorizados):")
        stars = patterns.get('best_assets', [])
        for a in stars: print(f"      - {a}")

        # 2. Ajustes de Rigurosidad
        print(f"\n   📉 AJUSTES DE RIGUROSIDAD (RSI):")
        thresholds = patterns.get('rsi_thresholds', {})
        if thresholds:
            if 'CALL' in thresholds: print(f"      - CALL: Ahora exige RSI < {thresholds['CALL']:.1f} (Entra más abajo)")
            if 'PUT' in thresholds: print(f"      - PUT: Ahora exige RSI > {thresholds['PUT']:.1f} (Entra más arriba)")
        else: print("      - Usando umbrales estándar (30/70)")

        # 3. Horarios Peligrosos
        print(f"\n   ⏰ HORAS PROHIBIDAS:")
        hours = patterns.get('dangerous_hours', [])
        if hours: print(f"      - Horas (UTC): {hours}")
        else: print("      - Todo el día estable")

        print(f"\n{'='*80}")
        sys.stdout.flush()
        
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
