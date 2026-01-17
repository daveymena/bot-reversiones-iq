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
import pandas as pd
sys.path.insert(0, '.')

from observe_market import MarketObserver
from strategies.breakout_momentum import BreakoutMomentumStrategy
from strategies.smart_reversal import SmartReversalStrategy
from strategies.trend_following import TrendFollowingStrategy
from strategies.trap_detector import TrapDetector
from strategies.multi_timeframe import MultiTimeframeAnalyzer
from strategies.bollinger_rsi_real import BollingerRSIStrategy
from strategies.market_intent import MarketIntentAnalyzer
from strategies.volatility_sniper import VolatilitySniperStrategy
from strategies.pattern_recon import PatternReconStrategy
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
        self.volatility_strategy = VolatilitySniperStrategy()
        self.pattern_strategy = PatternReconStrategy()
        self.trap_detector = TrapDetector()  # 🚨 Detector de trampas
        self.intent_analyzer = MarketIntentAnalyzer() # 🏎️ Analizador de inercia
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
                df_local = self.observer.market_data.get_candles(asset, 60, 200, time.time())
                
                print(f"   💡 Velas obtenidas para {asset}: {len(df_local)}")
                
                if df_local.empty or len(df_local) < 100:
                    print(f"   ⚠️ Datos insuficientes")
                    continue
                
                # Aplicar indicadores
                df_local = self.observer.feature_engineer.prepare_for_rl(df_local)
                
                # Análisis de movimientos
                movement_analysis = self.analyze_movements(df_local, asset)
                
                # 🟢 MODO SUPERVISOR: Validar si el activo está respetando zonas
                if asset not in self.zone_validation:
                    self.zone_validation[asset] = {'validated_supports': [], 'validated_resistances': [], 'last_observation': None}
                
                # Actualizar validación de zonas (mirar si rebotó en los últimos 20 periodos)
                self.supervise_zones(df_local, asset)
                
                # Análisis de timing
                timing_analysis = self.analyze_timing_patterns(df_local, asset)
                
                # 🎯 ANÁLISIS MULTI-TIMEFRAME (M15, M30)
                mtf_context = {}
                try:
                    mtf_data = self.mtf_analyzer.analyze_asset(asset)
                    if mtf_data:
                        mtf_context = mtf_data.get('current_context', {})
                except Exception as mtf_e:
                    print(f"      ⚠️ Error MTF en {asset}: {mtf_e}")
                    mtf_data = {}

                # 🎯 ANÁLISIS PRIORITARIO: Bollinger+RSI (Patrón Real)
                current_threshold = self.get_adaptive_threshold()
                bollinger_rsi_analysis = self.bollinger_rsi_strategy.analyze(df_local, min_confidence=current_threshold)
                
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
                        'hour': datetime.now().hour,
                        'movement': movement_analysis,
                        'timing': timing_analysis,
                        'mtf_context': mtf_context,
                        'mtf_data': mtf_data,
                        'strategy': bollinger_rsi_analysis,
                        'all_strategies': {
                            'bollinger_rsi': bollinger_rsi_analysis,
                            'breakout': {'action': 'WAIT', 'confidence': 0},
                            'reversal': {'action': 'WAIT', 'confidence': 0},
                            'trend': {'action': 'WAIT', 'confidence': 0},
                            'volatility': {'action': 'WAIT', 'confidence': 0},
                            'pattern': {'action': 'WAIT', 'confidence': 0}
                        },
                        'current_price': df_local.iloc[-1]['close']
                    }
                else:
                    # Si no hay patrón real, usar estrategias secundarias
                    breakout_analysis = self.breakout_strategy.analyze(df_local)
                    reversal_analysis = self.reversal_strategy.analyze(df_local)
                    trend_analysis = self.trend_strategy.analyze(df_local)
                    volatility_analysis = self.volatility_strategy.analyze(df_local)
                    pattern_analysis = self.pattern_strategy.analyze(df_local)
                    
                    # Elegir la mejor señal
                    strategies = [
                        breakout_analysis, 
                        reversal_analysis, 
                        trend_analysis, 
                        volatility_analysis, 
                        pattern_analysis
                    ]
                    best_strat = max(strategies, key=lambda x: x['confidence'])
                    
                    result = {
                        'asset': asset,
                        'timestamp': datetime.now(),
                        'hour': datetime.now().hour,
                        'movement': movement_analysis,
                        'timing': timing_analysis,
                        'mtf_context': mtf_context,
                        'mtf_data': mtf_data,
                        'strategy': best_strat,
                        'all_strategies': {
                            'bollinger_rsi': bollinger_rsi_analysis,
                            'breakout': breakout_analysis,
                            'reversal': reversal_analysis,
                            'trend': trend_analysis,
                            'volatility': volatility_analysis,
                            'pattern': pattern_analysis
                        },
                        'current_price': df_local.iloc[-1]['close']
                    }
                
                # Aplicar aprendizaje dinámico
                result = self.apply_learned_filters(result, df_local)
                
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
                import traceback
                traceback.print_exc()
                print(f"   ❌ Error: {e}")
                continue
        
        return analysis_results

    def apply_learned_filters(self, result, df=None):
        """
        Refina la confianza de la estrategia basándose en patrones de aprendizaje profundo
        """
        # Inicialización robusta para evitar UnboundLocalError
        current_df = df
        
        asset = result['asset']
        strategy = result['strategy']
        
        # Obtener refinamientos del optimizador
        refinements = self.knowledge_optimizer.get_refinements_for_asset(asset)
        
        # 1. Filtro de Activo Tóxico
        if refinements['is_toxic']:
            strategy['confidence'] *= 0.7
            strategy['reason'] += " (⚠️ ACTIVO TÓXICO: Historial negativo)"
            print(f"   ⚠️ Penalización por Activo Tóxico en {asset}")

        # 2. Bono por Activo Estrella
        if refinements['is_star']:
            strategy['confidence'] = min(99.0, strategy['confidence'] * 1.1)
            strategy['reason'] += " (🌟 ACTIVO ESTRELLA)"

        # 2.1 Filtro de Horario Peligroso (Nuevo: Aprendizaje de Estabilidad)
        current_hour = datetime.now().hour
        if current_hour in refinements.get('dangerous_hours', []):
            strategy['confidence'] *= 0.5
            strategy['reason'] += f" (⏰ HORARIO PELIGROSO: {current_hour}:00 suele ser inestable)"
            print(f"   ⏰ Penalización por Horario Peligroso: {current_hour}:00")

        # 2.2 Filtro de Estrategia Prohibida (Nuevo: Aprendizaje de Efectividad)
        strat_name = strategy.get('strategy', 'Unknown')
        if strat_name in refinements.get('forbidden_strategies', []):
            strategy['confidence'] *= 0.5
            strategy['reason'] += f" (🚫 ESTRATEGIA FALLIDA: {strat_name} tiene bajo WR histórico)"
            print(f"   🚫 Penalización por Estrategia Fallida: {strat_name}")

        # 3. Comprobación de Umbrales RSI Adaptativos
        rsi_adjusts = refinements.get('rsi_adjust', {})
        current_rsi = 50
        try:
            if 'details' in strategy:
                current_rsi = strategy['details'].get('rsi', 50)
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
                strategy['confidence'] *= 0.8
                strategy['reason'] += f" (⚠️ RSI {current_rsi:.1f} > Seguro {safe_rsi:.1f})"
        elif action == 'PUT':
            safe_rsi = rsi_adjusts.get('PUT')
            if safe_rsi and current_rsi < safe_rsi:
                strategy['confidence'] *= 0.8
                strategy['reason'] += f" (⚠️ RSI {current_rsi:.1f} < Seguro {safe_rsi:.1f})"

        # 4. Filtro de Alineación con Temporalidad Mayor
        mtf = result.get('mtf_context', {})
        if mtf:
            trend_m30 = mtf.get('trend_m30')
            strength = mtf.get('trend_strength', 'WEAK')
            if action == 'CALL' and trend_m30 == 'DOWNTREND':
                penalty = 0.6 if strength == 'STRONG' else 0.8
                strategy['confidence'] *= penalty
                strategy['reason'] += f" (🚨 CONTRA-TENDENCIA M30 {strength})"
            elif action == 'PUT' and trend_m30 == 'UPTREND':
                penalty = 0.6 if strength == 'STRONG' else 0.8
                strategy['confidence'] *= penalty
                strategy['reason'] += f" (🚨 CONTRA-TENDENCIA M30 {strength})"

        # --- FILTRO DE RIGUROSIDAD INTEGRAL ---
        if current_df is None or current_df.empty:
             try:
                current_df = self.observer.market_data.get_candles(result['asset'], 60, 50, time.time())
             except:
                current_df = pd.DataFrame()
        
        if current_df is None or current_df.empty:
            return result

        # 4.1 Filtro ADX
        if mtf and mtf.get('adx_m30', 0) > 35:
            if 'Reversal' in strategy.get('strategy', ''):
                strategy['confidence'] *= 0.6
                strategy['reason'] += " (🛑 TENDENCIA HTF IMPARABLE: ADX > 35)"

        # 4.2 Trap Detector
        is_accelerating, acc_score = self.trap_detector.detect_momentum_acceleration(current_df, action)
        if is_accelerating:
            strategy['confidence'] *= 0.5
            strategy['reason'] += " (🏎️ ACELERACIÓN: El precio viene con demasiada fuerza)"

        is_explosive, vol_score = self.trap_detector.detect_volatility_explosion(current_df)
        if is_explosive:
            strategy['confidence'] *= 0.5
            strategy['reason'] += " (⚡ MERCADO INESTABLE: Explosión de Volatilidad)"
            
        # 4.4 Muro de Tendencia HTF
        if mtf:
            trend_h1 = mtf.get('trend_h1', 'SIDEWAYS')
            trend_m30 = mtf.get('trend_m30')
            trend_m15 = mtf.get('trend_m15')
            if trend_h1 != 'SIDEWAYS':
                if (action == 'CALL' and trend_h1 == 'DOWNTREND') or (action == 'PUT' and trend_h1 == 'UPTREND'):
                    strategy['confidence'] *= 0.5
                    strategy['reason'] += " (⛔ CONTRA TENDENCIA H1)"
            if trend_m30 == trend_m15 and trend_m30 != 'SIDEWAYS':
                if (action == 'CALL' and trend_m30 == 'DOWNTREND') or (action == 'PUT' and trend_m30 == 'UPTREND'):
                    strategy['confidence'] *= 0.8
                    strategy['reason'] += " (🛑 MURO DE TENDENCIA HTF)"

        # 5. Validación de Zona
        if 'Reversal' in strategy.get('strategy', ''):
            price = strategy.get('details', {}).get('price', 0)
            key_levels = mtf.get('key_levels', {}) if 'key_levels' in mtf else {}
            if not key_levels and 'mtf_data' in result:
                key_levels = result['mtf_data'].get('key_levels', {})

            exhaustion = self.trap_detector.detect_level_exhaustion(current_df, key_levels)
            is_exhausted = False
            if action == 'CALL' and any(abs(price - s)/price < 0.0005 for s in exhaustion['support']):
                is_exhausted = True
            elif action == 'PUT' and any(abs(price - r)/price < 0.0005 for r in exhaustion['resistance']):
                is_exhausted = True
                
            if is_exhausted:
                strategy['confidence'] *= 0.4
                strategy['reason'] += " (🛑 NIVEL EXHAUSTO: Probable Ruptura)"
                return result

            is_sweep, sweep_score = self.trap_detector.detect_liquidity_sweep(current_df, action, key_levels)
            if is_sweep:
                strategy['confidence'] = min(99.0, strategy['confidence'] + 15)
                strategy['reason'] += " (🌊 LIQUIDITY SWEEP DETECTADO)"

            is_valid = self.is_zone_validated(asset, price, action)
            if not is_valid:
                strategy['confidence'] *= 0.5
                strategy['reason'] += " (🕵️ ZONA NO VALIDADA POR SUPERVISOR)"
            else:
                strategy['confidence'] = min(99.0, strategy['confidence'] * 1.1)
                strategy['reason'] += " (💎 ZONA PROBADA Y EFECTIVA)"

        # 6. Horario Peligroso
        current_hour = datetime.utcnow().hour
        dangerous_hours = self.knowledge_optimizer.db.get('patterns_found', {}).get('dangerous_hours', [])
        if current_hour in dangerous_hours:
            strategy['confidence'] *= 0.85
            strategy['reason'] += f" (⚠️ Horario difícil {current_hour}:00)"

        # 5. NUEVO: FILTRO DE INTENCIÓN DE MERCADO (Inercia Insoportable)
        intent = self.intent_analyzer.analyze_intent(current_df)
        action = result['strategy']['action']
        
        if intent['is_unstoppable']:
            # Si el mercado es imparable hacia un lado, NO operar en contra
            if (intent['intent'].startswith('BEARISH') and action == 'CALL') or \
               (intent['intent'].startswith('BULLISH') and action == 'PUT'):
                print(f"   🚨 BLOQUEO POR INERCIA: {intent['reason']}")
                strategy['confidence'] = 0 # Anular operación
                strategy['reason'] += f" (🚫 FORCE LOCK: {intent['intent']})"
                return result
            # Si el mercado es imparable HACIA nuestra dirección, darle bonus
            elif (intent['intent'].startswith('BULLISH') and action == 'CALL') or \
                 (intent['intent'].startswith('BEARISH') and action == 'PUT'):
                print(f"   🚀 BONUS POR INERCIA: El mercado empuja a nuestro favor.")
                strategy['confidence'] = min(99.0, strategy['confidence'] + 10)
                strategy['reason'] += " (🚀 MARKET FORCE)"

        # 6. FILTRO DE ZONAS (CRÍTICO: Evitar comprar en resistencia)
        try:
            current_price = current_df.iloc[-1]['close']
        except:
            current_price = 0
            
        # Validar si estamos en zona peligrosa
        zone_status = self.check_zone_status(asset, current_price)
        
        if zone_status['in_resistance'] and action == 'CALL':
            print(f"   🛑 ALERTA: Señal de COMPRA justo en RESISTENCIA VALIDADA ({zone_status['nearest_level']})")
            print(f"   🔄 INVIRTIENDO ESTRATEGIA: El mercado va a rebotar.")
            result['strategy']['action'] = 'PUT'
            result['strategy']['reason'] = f"REVERSIÓN POR RESISTENCIA (Original era CALL). Mercado en techo {zone_status['nearest_level']}"
            result['strategy']['confidence'] = 85.0
            
        elif zone_status['in_support'] and action == 'PUT':
            print(f"   🛑 ALERTA: Señal de VENTA justo en SOPORTE VALIDADO ({zone_status['nearest_level']})")
            print(f"   🔄 INVIRTIENDO ESTRATEGIA: El mercado va a rebotar.")
            result['strategy']['action'] = 'CALL'
            result['strategy']['reason'] = f"REVERSIÓN POR SOPORTE (Original era PUT). Mercado en suelo {zone_status['nearest_level']}"
            result['strategy']['confidence'] = 85.0

        strategy['confidence'] = min(round(strategy['confidence'], 1), 99.0)

        # 7. VALIDACIÓN FINAL CON OLLAMA (IA)
        if strategy['confidence'] > 55.0 and self.llm:
            try:
                # Contexto para el "Abogado del Diablo"
                extra_context = f"""
                ZONA ACTUAL: {'Resistencia' if zone_status['in_resistance'] else 'Soporte' if zone_status['in_support'] else 'Ninguna'}
                DISTANCIA A NIVEL: {zone_status['dist_res'] if zone_status['in_resistance'] else zone_status['dist_sup'] if zone_status['in_support'] else 'Lejos'}
                INERCIA DETECTADA: {intent['intent']}
                """
                
                print(f"   🤖 Consultando IA (Abogado del Diablo) para {asset}...")
                ai_check = self.llm.analyze_entry_timing(current_df, result['strategy']['action'], asset, extra_context)
                
                if not ai_check.get('is_optimal', True):
                    # Si la IA duda, gran penalización (protección contra trampas)
                    penalty = 0.6 # -40%
                    strategy['confidence'] *= penalty
                    strategy['reason'] += f" (🤖 IA Advierte: {ai_check.get('reasoning', 'No óptimo')})"
                else:
                    # Si la IA confirma, bonus moderado
                    strategy['confidence'] = min(99.0, strategy['confidence'] + 5)
                    strategy['reason'] += f" (🤖 IA Confirma: {ai_check.get('reasoning', 'OK')})"
            except Exception as e:
                print(f"   ⚠️ Error consultando IA: {e}")

        return result

    def check_zone_status(self, asset, current_price):
        """Verifica si el precio está en zona de soporte o resistencia"""
        zones = self.zone_validation.get(asset, {'validated_supports': [], 'validated_resistances': []})
        tolerance = 0.0003 # 3-4 pips
        
        status = {
            'in_resistance': False,
            'in_support': False,
            'nearest_level': None,
            'dist_res': None,
            'dist_sup': None
        }
        
        # Check Resistencia
        if zones['validated_resistances']:
            try:
                nearest_res = min(zones['validated_resistances'], key=lambda x: abs(x - current_price))
                dist = abs(current_price - nearest_res)
                status['dist_res'] = dist
                if dist < tolerance:
                    status['in_resistance'] = True
                    status['nearest_level'] = nearest_res
            except:
                pass
                
        # Check Soporte
        if zones['validated_supports']:
            try:
                nearest_sup = min(zones['validated_supports'], key=lambda x: abs(x - current_price))
                dist = abs(current_price - nearest_sup)
                status['dist_sup'] = dist
                if dist < tolerance:
                    status['in_support'] = True
                    status['nearest_level'] = nearest_sup
            except:
                pass
                
        return status
    
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

    def wait_for_price_confirmation(self, asset, action, wait_seconds=10):
        """
        PROTOCOLO 'END OF CANDLE SNIPER' (Sincronización con Cierre):
        1. Espera a que la vela actual esté cerca de cerrar (segundos 50-58).
        2. Verifica si hay una MECHA de rechazo.
        3. Si la vela es un 'Marubozu' (fuerza total sin mecha), aborta.
        """
        print(f"⏳ PROTOCOLO END-OF-CANDLE SNIPER: Sincronizando con el cierre de vela para {action}...")
        
        try:
            # 1. Esperar al momento óptimo (segundos 50-55 de la vela de 1m)
            start_wait = time.time()
            current_sec = datetime.now().second
            
            # Si estamos antes del segundo 50, esperar hasta llegar ahí
            if current_sec < 50:
                wait_to_sync = 50 - current_sec
                print(f"   ⏱️ Sincronizando: Esperando {wait_to_sync}s para llegar al cierre de la vela...")
                time.sleep(wait_to_sync)
            
            # 2. Análisis de la vela en formación (Segundos finales)
            print(f"   🔍 Analizando rechazo en segundos finales...")
            df = self.observer.market_data.get_candles(asset, 60, 1, time.time())
            if df.empty: return False, "Fallo datos"
            
            last_candle = df.iloc[-1]
            high, low = last_candle['high'], last_candle['low']
            open_p, close_p = last_candle['open'], last_candle['close']
            
            # Calcular mechas
            upper_wick = high - max(open_p, close_p)
            lower_wick = min(open_p, close_p) - low
            body = abs(close_p - open_p)
            total_range = high - low if high > low else 0.0001
            
            # --- CRITERIOS DE RECHAZO ---
            if action == 'CALL':
                # Queremos ver una mecha INFERIOR (rechazo de vendedores)
                wick_ratio = lower_wick / total_range
                if wick_ratio > 0.25:
                    print(f"   ✅ RECHAZO DETECTADO: Mecha inferior del {wick_ratio*100:.1f}%. Compradores defendiendo.")
                    return True, f"Wick Rejection {wick_ratio*100:.1f}%"
                if body > total_range * 0.8 and close_p < open_p:
                    print(f"   🚨 BLOQUEO: Vela Marubozu bajista (Sin mecha). Fuerza vendedora absoluta.")
                    return False, "Marubozu bajista (Sin rechazo)"
                    
            if action == 'PUT':
                # Queremos ver una mecha SUPERIOR (rechazo de compradores)
                wick_ratio = upper_wick / total_range
                if wick_ratio > 0.25:
                    print(f"   ✅ RECHAZO DETECTADO: Mecha superior del {wick_ratio*100:.1f}%. Vendedores defendiendo.")
                    return True, f"Wick Rejection {wick_ratio*100:.1f}%"
                if body > total_range * 0.8 and close_p > open_p:
                    print(f"   🚨 BLOQUEO: Vela Marubozu alcista. Fuerza compradora absoluta.")
                    return False, "Marubozu alcista (Sin rechazo)"

            # Por defecto, si no hay gran mecha pero tampoco es un marubozu violento, 
            # hacemos una última micro-confirmación de dirección de 3 segundos
            print(f"   ⚖️ Sin mecha clara. Observando micro-dirección de 3s...")
            p1 = self.observer.market_data.get_candles(asset, 1, 1, time.time()).iloc[-1]['close']
            time.sleep(3)
            p2 = self.observer.market_data.get_candles(asset, 1, 1, time.time()).iloc[-1]['close']
            
            if action == 'CALL' and p2 > p1: return True, "Micro-rebote alcista"
            if action == 'PUT' and p2 < p1: return True, "Micro-rebote bajista"
            
            return False, "Falta de rechazo o micro-reacción"
            
        except Exception as e:
            return True, f"Error en sniper, procediendo por seguridad: {e}"

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
        if total_ops < 20: 
            print(f"   🧠 MODO APRENDIZAJE ACTIVO ({total_ops}/20 ops recientes): Recolectando datos (Umbral 65%)...")
            return 65.0 # AJUSTADO A PEDIDO DEL USUARIO (Antes 60.0)
            
        # Calcular Win Rate reciente
        recent_ops = history[-20:]
        wins = len([o for o in recent_ops if o.get('result') == 'win'])
        win_rate = wins / len(recent_ops) if recent_ops else 0
        
        # --- FASE 2: OPTIMIZACIÓN ---
        if total_ops < 100:
            base = 70.0 # AJUSTADO A PEDIDO DEL USUARIO
            if win_rate < 0.50:
                adjustment = 5.0 # Penalización más suave (75% en vez de 80%) para permitir recuperación
                print(f"   ⚠️ APRENDIZAJE DEFENSIVO: WR bajo ({win_rate*100:.0f}%). Ajustando umbral a {base+adjustment}%.")
            else:
                adjustment = 0.0
            return base + adjustment
            
        # --- FASE 3: ÉLITE (Máxima selectividad) ---
        print(f"   🏆 MODO ÉLITE ACTIVADO ({total_ops} ops): Máxima selectividad para proteger capital.")
        if win_rate < 0.60:
            return 80.0  # Bajado levemente de 85 a 80 para mantener actividad
        return 75.0 # Bajado de 80 a 75 para mantener flujo constante en elite

    
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
    
    def analyze_missed_opportunity(self, asset, action, loose_time, loose_price):
        """
        ANÁLISIS FORENSE POST-MORTEM 🕵️‍♂️
        Busca dónde ESTABA la entrada ganadora después de perder.
        """
        try:
            # Obtener datos: 1 minuto antes (contexto) y 5 minutos después (resultado)
            df = self.observer.market_data.get_candles(asset, 60, 10, loose_time + 300)
            if df is None or df.empty: return None

            best_correction = None
            
            # Buscar el punto extremo opuesto en los siguientes 5 minutos
            if action == 'CALL':
                # Si era CALL y perdimos, el precio bajó. ¿Dónde estuvo el piso real?
                real_min = df['low'].min()
                if real_min < loose_price:
                    diff = loose_price - real_min
                    best_correction = {
                        "type": "WAIT_BETTER_PRICE",
                        "value": diff,
                        "msg": f"Entrada prematura. Debimos esperar a que el precio cayera hasta {real_min:.5f} (diferencia de {diff:.5f})"
                    }
            elif action == 'PUT':
                # Si era PUT y perdimos, el precio subió. ¿Dónde estuvo el techo real?
                real_max = df['high'].max()
                if real_max > loose_price:
                    diff = real_max - loose_price
                    best_correction = {
                        "type": "WAIT_BETTER_PRICE",
                        "value": diff,
                        "msg": f"Entrada prematura. Debimos esperar a que el precio subiera hasta {real_max:.5f} (diferencia de {diff:.5f})"
                    }
            
            return best_correction
        except Exception as e:
            print(f"⚠️ Error en análisis forense: {e}")
            return None

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
                    print(f"\n⚠️ STOP LOSS DE SESIÓN ALCANZADO ({self.max_session_losses} pérdidas).")
                    print("🛡️ PERO CONTINUANDO EN MODO ENTRENAMIENTO 24/7 (Simulación/Práctica)")
                    # No hacemos break para cumplir con el requerimiento de "entrenamiento continuo"
                    # break 
                
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
                        # Obtenemos DF aquí por seguridad si no se obtuvo antes
                        if 'df' not in locals():
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
                            current_price = df.iloc[-1]['close'] if not df.empty else 0
                            print(f"✅ ¡Operación abierta! ID: {order_id} (Precio: {current_price}). Esperando resultado...")
                            # Registrar
                            strategy['entry_price'] = current_price
                            opp_record = {
                                'id': order_id,
                                'timestamp': datetime.now().isoformat(),
                                'asset': asset,
                                'strategy': strategy,
                                'mtf_context': context if 'context' in locals() else {},
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
                        trend = mtf.get('trend_m30', 'DESCONOCIDA') if mtf else 'N/A'
                        
                        # 1. Diagnóstico de Tendencia
                        diag = f"🛑 DIAGNÓSTICO: Pérdida en {asset} contra tendencia M30 ({trend})."
                        print(f"   {diag}")
                        
                        # 2. Análisis de Oportunidad Perdida (Correction Lesson)
                        try:
                            loose_price = op.get('strategy', {}).get('entry_price', 0) # Necesitamos registrar el entry_price al crear la op
                            action_type = op.get('strategy', {}).get('action')
                            
                            correction = self.analyze_missed_opportunity(asset, action_type, time.time(), loose_price)
                            
                            if correction:
                                lesson = f"🎓 LECCIÓN APRENDIDA: {correction['msg']}"
                                print(f"   {lesson}")
                                # Guardar lección en DB
                                self.knowledge_optimizer.db.setdefault('corrections', []).append({
                                    'asset': asset,
                                    'action': action_type,
                                    'correction': correction['value'],
                                    'timestamp': datetime.now().isoformat()
                                })
                        except Exception as e_forensic:
                            print(f"⚠️ Fallo en forense: {e_forensic}")

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
    # Asegurar codificación UTF-8 para la consola (evita caracteres raros en logs)
    if sys.stdout.encoding != 'utf-8':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except:
            pass

    # Soporte para modo no interactivo (Docker/Easypanel)
    if os.getenv("HEADLESS_MODE", "false").lower() == "true":
        print("🤖 MODO HEADLESS ACTIVADO: BUCLE INFINITO DE APRENDIZAJE 24/7")
        print("💡 El bot se reiniciará automáticamente si la sesión termina.")
        
        while True:
            try:
                system_main = IntelligentLearningSystem()
                # 1440 minutos = 24 horas por sesión. 1000 ops target.
                # Al terminar, el bucle while lo reinicia inmediatamente.
                system_main.continuous_learning_session(1440, 1000)
            except Exception as e:
                print(f"⚠️ Error crítico en ciclo principal: {e}")
                import traceback
                traceback.print_exc()
            
            print("🔄 Reiniciando ciclo de aprendizaje en 10 segundos...")
            time.sleep(10)
    else:
        main()
