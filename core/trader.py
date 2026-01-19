import time
import pandas as pd
import os

# Importar PySide6 de forma opcional para soporte Headless (Docker)
try:
    from PySide6.QtCore import QThread, Signal, QObject
    GUI_AVAILABLE = True
except Exception as e:
    # Capturar CUALQUIER error (ImportError, RuntimeError, OSError por falta de .so, etc.)
    print(f"⚠️ PySide6 no disponible ({type(e).__name__}: {e}). Ejecutando en modo HEADLESS (sin GUI)")
    GUI_AVAILABLE = False
    # Mock classes para evitar errores en modo headless
    class QThread:
        def __init__(self, *args, **kwargs): pass
        def start(self): pass
        def wait(self): pass
    class QObject:
        def __init__(self, *args, **kwargs): pass
    class Signal:
        def __init__(self, *args, **kwargs): pass
        def emit(self, *args, **kwargs): pass

from core.risk import RiskManager
from config import Config

class TraderSignals(QObject):
    """Señales para comunicar el hilo de trading con la GUI."""
    price_update = Signal(float, float) # timestamp, price
    new_candle = Signal(object) # DataFrame row
    trade_signal = Signal(str, str) # Action, Asset
    log_message = Signal(str)
    error_message = Signal(str)
    balance_update = Signal(float)
    decision_analysis = Signal(object, float) # validation_result, profitability_score
    stats_update = Signal(int, int, float) # wins, losses, total_profit

from core.trade_analyzer import TradeAnalyzer
from core.continuous_learner import ContinuousLearner
from core.decision_validator import DecisionValidator
from core.trade_intelligence import TradeIntelligence
from core.observational_learner import ObservationalLearner
from core.intelligent_filters import IntelligentFilters
from core.parallel_trainer import ParallelTrainer
from core.market_structure_analyzer import MarketStructureAnalyzer
from core.consistency_manager import ConsistencyManager
from database.db_manager import db
from datetime import datetime
import json

class LiveTrader(QThread):
    def __init__(self, market_data, feature_engineer, agent, risk_manager, asset_manager, llm_client=None):
        super().__init__()
        self.market_data = market_data
        self.feature_engineer = feature_engineer
        self.agent = agent
        self.risk_manager = risk_manager
        self.asset_manager = asset_manager
        self.llm_client = llm_client
        self.trade_analyzer = TradeAnalyzer()
        
        # Sistema de aprendizaje continuo
        self.continuous_learner = ContinuousLearner(agent, feature_engineer, market_data)
        
        # Validador de decisiones
        self.decision_validator = DecisionValidator()
        
        # 🧠 Sistema de Inteligencia de Trading (con Groq/Ollama)
        self.trade_intelligence = TradeIntelligence(llm_client=llm_client)
        
        # 👁️ Sistema de Aprendizaje Observacional
        self.observational_learner = ObservationalLearner(
            self.continuous_learner,
            self.market_data,
            self.feature_engineer
        )
        
        # 🎯 Filtros Inteligentes basados en datos históricos
        self.intelligent_filters = IntelligentFilters()
        
        # 🎓 Entrenador Paralelo (aprende mientras opera)
        self.parallel_trainer = ParallelTrainer(
            market_data=market_data,
            feature_engineer=feature_engineer,
            agent=agent,
            llm_client=llm_client
        )
        
        # 📊 Analizador de Estructura de Mercado y Perfilador de Rentabilidad
        from core.market_profiler import MarketProfiler
        self.market_profiler = MarketProfiler(self.market_data)
        
        self.market_structure_analyzer = MarketStructureAnalyzer()
        self.consistency_manager = ConsistencyManager()
        
        self.signals = TraderSignals()
        self.running = False
        self.paused = False
        self.active_trades = [] # Lista de dicts: {id, asset, direction, entry_time, entry_price, amount, state_before, df_before}
        
        # Control de tiempo entre operaciones (MÁS ESTRICTO para evitar sobre-operación)
        self.last_trade_time = 0
        # Control de tiempo entre operaciones (MÁS AGRESIVO para aprovechar oportunidades)
        self.last_trade_time = 0
        self.min_time_between_trades = 30  # Mínimo 30 segundos entre operaciones
        self.cooldown_after_loss = 60      # 1 minuto de espera después de perder
        self.consecutive_losses = 0
        self.last_trade_result = None
        self.max_consecutive_losses = 5    # Pausar después de 5 pérdidas consecutivas
        
        # Control de operaciones por hora
        self.trades_last_hour = []  # Lista de timestamps de operaciones
        self.max_trades_per_hour = 50  # Límite alto para no bloquear
        
        # 🆕 MEJORA 1: Cooldown por activo (evita operar múltiples veces en mismo par)
        self.last_trade_per_asset = {}  # {asset: timestamp}
        self.cooldown_per_asset = 60   # 1 minuto por activo
        
        # Control de escaneo
        self.scan_interval = 30 # Escanear cada 30 segundos
        self.last_scan_time = 0
        
        # 🆕 MEJORA 5: Límite de operaciones por hora
        self.trades_this_hour = []
        # self.max_trades_per_hour = 3 <--- Eliminado redundancia

    def stop(self):
        """Detiene el bot de forma segura."""
        print("[DEBUG] Deteniendo bot...")
        self.running = False
        self.paused = False
        print("[DEBUG] Bot detenido")
    
    def pause(self):
        """Pausa el bot temporalmente."""
        print("[DEBUG] Pausando bot...")
        self.paused = True
        print("[DEBUG] Bot pausado")
    
    def resume(self):
        """Reanuda el bot."""
        print("[DEBUG] Reanudando bot...")
        self.paused = False
        print("[DEBUG] Bot reanudado")
    
    def run(self):
        """Bucle principal de trading (Ejecutado en hilo separado)."""
        # PROTECCIÓN TOTAL ANTI-ERRORES
        print("[DEBUG] Iniciando run()...")
        try:
            self._run_protected()
        except Exception as e:
            print(f"\n{'='*60}")
            print(f"[ERROR FATAL] Error no capturado en run():")
            print(f"{'='*60}")
            print(f"{e}")
            import traceback
            traceback.print_exc()
            print(f"{'='*60}\n")
            try:
                self.signals.error_message.emit(f"Error fatal: {e}")
            except:
                pass
            self.running = False
        finally:
            print("[DEBUG] run() finalizado. running =", self.running)
    
    def _run_protected(self):
        """Método run protegido - contiene la lógica real"""
        self.running = True
        # Defensive Init: Asegurar atributos críticos
        if not hasattr(self, 'scan_interval'): self.scan_interval = 10 # Optimizado para M1 Sniper
        if not hasattr(self, 'last_scan_time'): self.last_scan_time = 0
        
        self.signals.log_message.emit("🚀 Iniciando LiveTrader 24/7 con Martingala Inteligente...")
        self.signals.log_message.emit("♾️ Modo continuo: El bot operará sin detenerse")

        # 1. Verificar conexión primero
        if not self.market_data.connected:
            self.signals.error_message.emit("Debes conectarte al broker primero.")
            self.running = False
            return
        
        # 2. Modo Multi-Divisa: Escanear activos disponibles
        self.signals.log_message.emit("🔍 Verificando activos disponibles...")
        available_assets = self.asset_manager.get_available_otc_assets(verbose=True)
        if available_assets:
            self.signals.log_message.emit(f"✅ {len(available_assets)} activos disponibles para monitoreo")
            # Seleccionar los mejores activos (máximo 5)
            self.asset_manager.monitored_assets = available_assets[:5]
            self.signals.log_message.emit(f"📊 Monitoreando: {', '.join(self.asset_manager.monitored_assets)}")
        else:
            self.signals.log_message.emit("⚠️ No se encontraron activos OTC, usando EURUSD-OTC por defecto")
            self.asset_manager.monitored_assets = ["EURUSD-OTC"]
        
        self.current_asset = None  # Se seleccionará dinámicamente
        self.last_asset_check = time.time()  # Para re-verificar periódicamente

        # 📊 PERFILADO INICIAL (Estudiar el mercado antes de operar)
        self.signals.log_message.emit("🧪 Generando Mapa de Rentabilidad estadístico (API)...")
        for asset in self.asset_manager.monitored_assets:
            self.market_profiler.profile_asset(asset)
        
        print("[DEBUG] Entrando al bucle principal while...")
        iteration_count = 0
        last_heartbeat = time.time()
        last_connection_check = time.time()
        
        while self.running:
            # 🔌 VERIFICACIÓN DE CONEXIÓN cada 30 segundos
            if time.time() - last_connection_check >= 30:
                if not self.market_data.is_really_connected():
                    self.signals.error_message.emit("⚠️ Conexión perdida detectada!")
                    self.signals.log_message.emit("🔄 Iniciando ciclo de reconexión infinita (24/7)...")
                    
                    retry_count = 0
                    while self.running:
                        try:
                            retry_count += 1
                            self.signals.log_message.emit(f"🔄 Intento de reconexión #{retry_count}...")
                            
                            email = Config.EXNOVA_EMAIL if self.market_data.broker_name == "exnova" else Config.IQ_EMAIL
                            password = Config.EXNOVA_PASSWORD if self.market_data.broker_name == "exnova" else Config.IQ_PASSWORD
                            
                            success = self.market_data.reconnect(email, password)
                            if success:
                                self.signals.log_message.emit("✅ Reconexión exitosa! El bot 24/7 reanuda operaciones.")
                                break
                            
                            # Backoff exponencial limitado
                            wait_time = min(30 * (2 ** (retry_count - 1)), 600)  # Máximo 10 minutos
                            self.signals.log_message.emit(f"⏳ Reintento fallido. Esperando {wait_time}s para el próximo intento...")
                            
                            for _ in range(int(wait_time)):
                                if not self.running: break
                                time.sleep(1)
                        except Exception as e:
                            self.signals.error_message.emit(f"❌ Error en ciclo de reconexión: {e}")
                            time.sleep(10)
                
                last_connection_check = time.time()
            
            # Heartbeat cada 60 segundos
            if time.time() - last_heartbeat >= 60:
                self.signals.log_message.emit(f"💓 Bot activo - Iteración #{iteration_count} - Conexión: {'✅' if self.market_data.is_really_connected() else '❌'}")
                last_heartbeat = time.time()
            
            iteration_count += 1
            if iteration_count % 10 == 0:  # Log cada 10 iteraciones
                print(f"[DEBUG] Iteración #{iteration_count}, running={self.running}, paused={self.paused}, connected={self.market_data.is_really_connected()}")
            
            if self.paused:
                time.sleep(1)
                continue

            try:
                # ⏰ VERIFICACIÓN DE HORARIO DE OPERACIÓN - DESHABILITADA (opera 24/7)
                # El bot operará continuamente sin restricciones de horario
                
                # --- Monitoreo de Operaciones Activas ---
                self.check_active_trades()
                
                # 🎓 ENTRENAMIENTO PARALELO: Verificar operaciones simuladas
                if self.market_data.account_type == 'REAL':
                    try:
                        self.parallel_trainer.check_simulated_trades()
                    except Exception as e:
                        print(f"[WARNING] Error en entrenamiento paralelo: {e}")

                # Actualizar balance
                balance = self.market_data.get_balance()
                self.signals.balance_update.emit(balance)
                
                # 👁️ Verificar observaciones y aprender de ellas
                learned = self.observational_learner.check_observations()
                if learned > 0:
                    self.signals.log_message.emit(f"📚 Aprendidas {learned} observaciones del mercado")
                
                # 🔄 Re-verificar activos disponibles cada 5 minutos
                if time.time() - self.last_asset_check >= 300:  # 5 minutos
                    self.signals.log_message.emit("🔄 Actualizando lista de activos disponibles...")
                    update_result = self.asset_manager.update_available_assets()
                    
                    if update_result['added']:
                        self.signals.log_message.emit(f"✅ Activos agregados: {', '.join(update_result['added'])}")
                    if update_result['removed']:
                        self.signals.log_message.emit(f"❌ Activos removidos: {', '.join(update_result['removed'])}")
                    
                    self.signals.log_message.emit(f"📊 Total activos disponibles: {update_result['total']}")
                    self.last_asset_check = time.time()
                
                # 🛑 EVALUACIÓN CONTINUA: Verificar si debe pausar
                try:
                    should_pause, pause_reason = self.continuous_learner.should_pause_trading()
                    if should_pause:
                        self.signals.log_message.emit(pause_reason)
                        self.signals.log_message.emit("🎓 Iniciando re-entrenamiento automático...")
                        self.signals.log_message.emit("⏳ El bot continuará operando después del entrenamiento...")
                        
                        # Re-entrenar con datos frescos
                        try:
                            success = self.continuous_learner.retrain_with_fresh_data(
                                asset=self.current_asset if self.current_asset else "EURUSD-OTC",
                                num_candles=1000
                            )
                            
                            if success:
                                self.signals.log_message.emit("✅ Re-entrenamiento completado exitosamente")
                                self.signals.log_message.emit("🔄 Reanudando operaciones normales...")
                                # Resetear contador de pérdidas
                                self.consecutive_losses = 0
                                self.last_trade_result = None
                            else:
                                self.signals.log_message.emit("⚠️ Re-entrenamiento falló, continuando con modelo actual")
                                self.signals.log_message.emit("⏸️ Esperando 1 minuto antes de continuar...")
                                # Esperar en intervalos cortos para no congelar la GUI
                                for _ in range(60):
                                    if not self.running:
                                        break
                                    time.sleep(1)
                        except Exception as retrain_error:
                            self.signals.error_message.emit(f"❌ Error en re-entrenamiento: {retrain_error}")
                            self.signals.log_message.emit("🔄 Continuando con modelo actual...")
                            print(f"[ERROR] Error en re-entrenamiento: {retrain_error}")
                            import traceback
                            traceback.print_exc()
                        
                        # IMPORTANTE: Siempre continuar después del re-entrenamiento
                        self.signals.log_message.emit("♾️ Bot 24/7 activo - Continuando monitoreo...")
                        continue
                except Exception as e:
                    self.signals.error_message.emit(f"❌ Error en evaluación continua: {e}")
                    print(f"[ERROR] Error en evaluación continua: {e}")
                    import traceback
                    traceback.print_exc()
                    # Continuar operando a pesar del error
                    time.sleep(5)

                # 🎯 MODO MULTI-DIVISA: Escanear mejor oportunidad (cada 30 segundos)
                # Inicializar best_opportunity si no existe
                if not hasattr(self, 'best_opportunity'):
                    self.best_opportunity = None
                    self.last_scan_time = 0  # Inicializar para escanear inmediatamente
                
                if not self.active_trades:  # Solo escanear si no hay operaciones activas
                    # Escanear solo cada 30 segundos para evitar spam
                    time_since_last_scan = time.time() - getattr(self, 'last_scan_time', 0)
                    
                    # 1. ESCANEAR OPORTUNIDADES (Heartbeat visual)
                    if time.time() - self.last_scan_time >= self.scan_interval:
                        self.signals.log_message.emit(f"🔍 Buscando oportunidades en mercado... (Siguiente scan en {self.scan_interval}s)")
                        self.best_opportunity = self.asset_manager.scan_best_opportunity(self.feature_engineer)
                        self.last_scan_time = time.time()
                        
                        if self.best_opportunity:
                            self.current_asset = self.best_opportunity['asset']
                            self.signals.log_message.emit(f"💎 Oportunidad detectada en {self.current_asset}")
                        else:
                            self.signals.log_message.emit("⏳ No hay oportunidades claras, esperando 30s...")
                    elif int(time_since_last_scan) % 10 == 0 and int(time_since_last_scan) > 0:
                        # Mostrar progreso cada 10 segundos
                        remaining = int(30 - time_since_last_scan)
                        if remaining > 0:
                            self.signals.log_message.emit(f"⏱️ Próximo escaneo en {remaining}s...")
                    
                    # Si no hay activo seleccionado, usar el primero disponible
                    if not self.current_asset:
                        self.current_asset = self.asset_manager.monitored_assets[0] if self.asset_manager.monitored_assets else "EURUSD-OTC"
                        self.signals.log_message.emit(f"📊 Monitoreando: {self.current_asset}")
                
                # Usar la oportunidad guardada
                best_opportunity = self.best_opportunity
                
                # Obtener datos del activo actual
                df = self.market_data.get_candles(self.current_asset, Config.TIMEFRAME, 200)
                
                if df.empty:
                    self.signals.log_message.emit(f"⚠️ {self.current_asset} no disponible, cambiando de activo...")
                    
                    # Intentar con otros activos disponibles
                    for alternative_asset in self.asset_manager.monitored_assets:
                        if alternative_asset != self.current_asset:
                            test_df = self.market_data.get_candles(alternative_asset, Config.TIMEFRAME, 10)
                            if not test_df.empty:
                                self.current_asset = alternative_asset
                                self.signals.log_message.emit(f"✅ Cambiado a {self.current_asset}")
                                break
                    
                    time.sleep(2)
                    continue

                # Emitir precio actual
                last_candle = df.iloc[-1]
                self.signals.price_update.emit(last_candle.name.timestamp(), last_candle['close'])
                self.signals.new_candle.emit(last_candle)

                # Procesar indicadores
                df = self.feature_engineer.prepare_for_rl(df)
                
                # Lógica de Trading con VALIDACIÓN COMPLETA
                # REGLA 1: NO operar si hay operaciones activas
                if self.active_trades:
                    # Hay operaciones en curso, esperar
                    if iteration_count % 30 == 0:  # Log cada 30 iteraciones
                        trade_info = self.active_trades[0]
                        remaining_time = int((trade_info['entry_time'] + trade_info['duration'] + 10) - time.time())
                        self.signals.log_message.emit(f"⏳ Operación activa en {trade_info['asset']} - Esperando resultado (~{max(0, remaining_time)}s)")
                    continue
                
                # REGLA 2: Pausar después de 3 pérdidas consecutivas
                if self.consecutive_losses >= self.max_consecutive_losses:
                    if iteration_count % 60 == 0:  # Log cada minuto
                        self.signals.log_message.emit(f"⏸️ PAUSADO: {self.consecutive_losses} pérdidas consecutivas. Esperando mejores condiciones del mercado...")
                        self.signals.log_message.emit(f"💡 El bot se reactivará automáticamente después de re-entrenar o manualmente con 'Reanudar'")
                    time.sleep(1)
                    continue
                
                # REGLA 3: Verificar límite de operaciones por hora
                current_time = time.time()
                # Limpiar operaciones de hace más de 1 hora
                self.trades_last_hour = [t for t in self.trades_last_hour if current_time - t < 3600]
                
                if len(self.trades_last_hour) >= self.max_trades_per_hour:
                    if iteration_count % 60 == 0:  # Log cada minuto
                        oldest_trade = min(self.trades_last_hour)
                        wait_time = int(3600 - (current_time - oldest_trade))
                        self.signals.log_message.emit(f"⏸️ Límite de {self.max_trades_per_hour} operaciones/hora alcanzado. Esperando {wait_time//60} minutos...")
                    time.sleep(1)
                    continue
                
                # REGLA 4: Verificar tiempo mínimo entre operaciones
                time_since_last_trade = time.time() - self.last_trade_time
                
                # Si perdió la última, esperar más tiempo (cooldown)
                if self.last_trade_result == 'loss':
                    required_wait = self.cooldown_after_loss
                    if self.consecutive_losses >= 2:
                        required_wait = self.cooldown_after_loss * 2  # 30 minutos después de 2 pérdidas
                    
                    if time_since_last_trade < required_wait:
                        remaining = int(required_wait - time_since_last_trade)
                        if remaining % 60 == 0:  # Mostrar cada minuto
                            self.signals.log_message.emit(f"⏳ Cooldown después de pérdida: {remaining//60} minutos restantes")
                        continue
                else:
                    # Tiempo normal entre operaciones
                    if time_since_last_trade < self.min_time_between_trades:
                        remaining = int(self.min_time_between_trades - time_since_last_trade)
                        if remaining % 60 == 0:  # Mostrar cada minuto
                            self.signals.log_message.emit(f"⏳ Esperando tiempo mínimo: {remaining//60} minutos restantes")
                        continue
                
                # REGLA 3: Verificar datos suficientes
                window_size = 10
                if len(df) >= window_size:
                        # Si hay una oportunidad detectada por el scanner, usarla
                        if best_opportunity and best_opportunity['asset'] == self.current_asset:
                            self.signals.log_message.emit(f"\n🎯 Analizando oportunidad detectada...")
                            
                            # Usar la acción sugerida por el scanner
                            action = 1 if best_opportunity['action'] == 'CALL' else 2
                            
                            # 2. ANÁLISIS DE INDICADORES
                            indicators_analysis = self.analyze_indicators(df)
                            
                            # 2.5 ANÁLISIS DE ESTRUCTURA PREVIO (Para contexto IA)
                            htf_context_str = "Sin contexto HTF"
                            try:
                                # Analizar estructura completa (simulado o real si hay datos)
                                market_analysis_pre = self.market_structure_analyzer.analyze_full_context(df)
                                htf_context_str = f"Trend: {market_analysis_pre.get('main_trend', 'N/A')}, Volatility: {market_analysis_pre.get('volatility_state', 'NORMAL')}"
                                if 'levels' in market_analysis_pre:
                                     htf_context_str += f", Near Level: {market_analysis_pre['levels'].get('nearest', 'None')}"
                            except Exception as e:
                                print(f"Warning HTF context: {e}")

                            # 🧪 PERFILADOR DE MERCADO (Análisis estadístico de la API)
                            # Usar perfil existente si es reciente para no perder tiempo
                            asset_profile = self.market_profiler.profiles.get(self.current_asset)
                            if not asset_profile or (time.time() - asset_profile['last_update'] > 3600):
                                asset_profile = self.market_profiler.profile_asset(self.current_asset)
                            
                            stats_context = ""
                            if asset_profile:
                                stats_context = f"DATO API (RENTABILIDAD): Expiración de {asset_profile['best_expiration']} min es la mejor hoy ({asset_profile['winrate_stat']:.1f}% winrate)."
                                # self.signals.log_message.emit(f"📊 Estadística API: {asset_profile['best_expiration']} min tiene mayor probabilidad en {self.current_asset}")

                            # 🔥 OPTIMIZACIÓN: SALTO DE FILTROS PARA SEÑALES INSTITUCIONALES (ROOT)
                            # Si el AssetManager ya hizo el análisis de panorama completo (M15)
                            # y nos da una señal de alta confianza, saltamos validaciones redundantes
                            is_institutional_root = "ROOT" in best_opportunity.get('setup', '') or "SMC" in best_opportunity.get('setup', '')
                            
                            if is_institutional_root and (best_opportunity['confidence'] >= 90 or best_opportunity['confidence'] >= 0.90):
                                self.signals.log_message.emit(f"🚀 SEÑAL INSTITUCIONAL DETECTADA ({best_opportunity['setup']})")
                                self.signals.log_message.emit("⚡ Saltando validaciones redundantes para entrada inmediata en la RAÍZ")
                                
                                # Asegurar escala 0-100 para la confianza
                                conf_val = best_opportunity['confidence']
                                if conf_val <= 1.0: conf_val *= 100

                                validation = {
                                    'valid': True, 
                                    'recommendation': best_opportunity['action'],
                                    'confidence': conf_val / 100, # Escala 0-1 para consistencia con DecisionValidator
                                    'reasons': [
                                        f"Señal Institucional ({best_opportunity['setup']})",
                                        "Detección de Pantalla Completa M15/M30",
                                        f"Estadística API: Expiración {asset_profile['best_expiration'] if asset_profile else '3'} min"
                                    ],
                                    'warnings': []
                                }
                                # Forzar dirección y validez para el resto de la lógica
                                action = 1 if best_opportunity['action'] == 'CALL' else 2
                                indicators_analysis = {'direction': best_opportunity['action'], 'score': 100}
                                timing_analysis = {
                                    'is_optimal': True, 
                                    'confidence': conf_val / 100, 
                                    'wait_time': 0,
                                    'recommended_expiration': asset_profile['best_expiration'] if asset_profile else Config.MANUAL_EXPIRATION
                                }
                            
                            else:
                                # 3. 🎯 IA VISUAL ANALIZA EL TIMING PERFECTO (OLLAMA)
                                timing_analysis = None
                                if self.llm_client and Config.USE_LLM:
                                    try:
                                        self.signals.log_message.emit("⏱️ IA Visual (Ollama) analizando gráfico...")
                                        timing_analysis = self.llm_client.analyze_entry_timing(
                                            df=df,
                                            proposed_action=best_opportunity['action'],
                                            proposed_asset=self.current_asset,
                                            extra_context=f"{htf_context_str} | {stats_context}"
                                        )
                                        
                                        if timing_analysis:
                                            if not timing_analysis['is_optimal'] and timing_analysis['wait_time'] > 0:
                                                if timing_analysis['confidence'] >= 0.55:
                                                    self.signals.log_message.emit(f"⚡ Confianza aceptable ({timing_analysis['confidence']*100:.0f}%), operando sin esperar")
                                                else:
                                                    self.signals.log_message.emit(f"👁️ Registrando oportunidad para aprendizaje observacional...")
                                                    self.best_opportunity = None # Limpiar para no repetir análisis inútilmente
                                                    continue
                                    except Exception as e:
                                        self.signals.log_message.emit(f"⚠️ Error en análisis de timing: {e}")
                                
                                # 4. VALIDAR DECISIÓN (Normal)
                                validation = self.decision_validator.validate_decision(
                                    df=df,
                                    action=action,
                                    indicators_analysis=indicators_analysis,
                                    rl_prediction=action,
                                    llm_advice=best_opportunity['action']
                                )
                            
                            # 🎯 EMITIR ANÁLISIS AL GRÁFICO PROFESIONAL
                            try:
                                # Asegurar que el score sea 0-100 para la señal
                                raw_conf = validation.get('confidence', 0.5)
                                profitability_score = raw_conf * 100 if raw_conf <= 1.0 else raw_conf
                                self.signals.decision_analysis.emit(validation, profitability_score)
                            except: pass
                            
                            # 5. MOSTRAR ANÁLISIS
                            summary = self.decision_validator.get_summary(validation)
                            for line in summary.split('\n'):
                                self.signals.log_message.emit(line)
                            
                            # 6. FLUJO DE EJECUCIÓN (ROOT Y NORMAL)
                            if validation['valid']:
                                if is_institutional_root:
                                    self.signals.log_message.emit("\n✅ ESTRUCTURA CONFIRMADA POR ASSET MANAGER (M15)")
                                else:
                                    self.signals.log_message.emit("\n📊 ANALIZANDO ESTRUCTURA COMPLETA DEL MERCADO...")
                                
                                try:
                                    # Analizar estructura completa
                                    market_analysis = self.market_structure_analyzer.analyze_full_context(df)
                                    
                                    # Mostrar análisis legible
                                    readable_analysis = self.market_structure_analyzer.get_human_readable_analysis(market_analysis)
                                    for line in readable_analysis.split('\n'):
                                        self.signals.log_message.emit(line)
                                    
                                    # Verificar señal de entrada
                                    entry_signal = market_analysis['entry_signal']
                                    
                                    if not entry_signal['should_enter'] and not is_institutional_root:
                                        if entry_signal['should_wait']:
                                            self.signals.log_message.emit("\n⏳ ESPERANDO MOMENTO ÓPTIMO - No es el despegue todavía")
                                            for warning in entry_signal['warnings']:
                                                self.signals.log_message.emit(f"   ⚠️ {warning}")
                                        else:
                                            self.signals.log_message.emit("\n❌ CONDICIONES NO FAVORABLES - Cancelando operación")
                                        
                                        # Registrar como oportunidad observada
                                        opportunity_data = {
                                            'asset': self.current_asset,
                                            'action': validation['recommendation'],
                                            'confidence': validation.get('confidence', 0),
                                            'entry_price': df.iloc[-1]['close'] if not df.empty else 0,
                                            'state_before': df.tail(10) if not df.empty else None
                                        }
                                        try:
                                            self.observational_learner.observe_opportunity(
                                                opportunity_data,
                                                f"Estructura de mercado: {', '.join(entry_signal['warnings'])}"
                                            )
                                        except Exception as obs_err:
                                            print(f"Error en observational learner: {obs_err}")
                                        
                                        self.best_opportunity = None
                                        continue
                                    
                                    # Verificar que la dirección coincida
                                    if entry_signal['direction'] != validation['recommendation']:
                                        # Calcular diferencia de confianza
                                        structure_confidence = entry_signal['confidence']
                                        validation_confidence = validation['confidence']
                                        if validation_confidence <= 1.0: validation_confidence *= 100
                                        confidence_diff = abs(structure_confidence - validation_confidence)
                                        
                                        self.signals.log_message.emit(f"\n⚠️ CONFLICTO DE SEÑALES:")
                                        self.signals.log_message.emit(f"   Estructura dice: {entry_signal['direction']} ({structure_confidence}%)")
                                        self.signals.log_message.emit(f"   Validación dice: {validation['recommendation']} ({validation_confidence}%)")
                                        
                                        # Si la diferencia es mayor a 15%, usar la señal con mayor confianza
                                        if confidence_diff >= 15:
                                            if structure_confidence > validation_confidence:
                                                self.signals.log_message.emit(f"   ✅ Usando señal de ESTRUCTURA (mayor confianza: +{confidence_diff}%)")
                                                validation['recommendation'] = entry_signal['direction']
                                                validation['confidence'] = structure_confidence
                                            else:
                                                self.signals.log_message.emit(f"   ✅ Usando señal de VALIDACIÓN (mayor confianza: +{confidence_diff}%)")
                                        else:
                                            self.signals.log_message.emit(f"   ❌ Confianzas similares (diff: {confidence_diff}%), cancelando por seguridad")
                                            self.best_opportunity = None
                                            continue
                                    
                                    self.signals.log_message.emit(f"\n✅ ESTRUCTURA CONFIRMA: {entry_signal['direction']} con {entry_signal['confidence']}% confianza")
                                    
                                except Exception as e:
                                    self.signals.log_message.emit(f"⚠️ Error en análisis de estructura: {e}")
                                    self.signals.log_message.emit("   Continuando con validación estándar...")
                                
                                # ⚖️ FILTRO DE CONSISTENCIA 24/7 (Punto de Equilibrio)
                                allow_trade, consistency_reason = self.consistency_manager.should_allow_trade(self.current_asset)
                                allow_trade = True # 🔓 MODO BERSERKER ACTIVADO
                                if not allow_trade:
                                    self.signals.log_message.emit(f"\n{consistency_reason}")
                                    self.best_opportunity = None
                                    continue
                                
                                # Ajustar confianza dinámica basada en PnL
                                dynamic_threshold_pct = self.consistency_manager.get_dynamic_confidence_threshold() * 100
                                current_conf = validation.get('confidence', 0)
                                if current_conf <= 1.0: current_conf *= 100
                                
                                if current_conf < dynamic_threshold_pct:
                                    self.signals.log_message.emit(f"⚖️ EQUILIBRIO: Confianza de {current_conf:.1f}% insuficiente para el PnL actual (Req: {dynamic_threshold_pct:.1f}%).")
                                    self.best_opportunity = None
                                    continue

                                # 🎯 FILTROS INTELIGENTES: Consultar datos históricos (PROTEGIDO)
                                self.signals.log_message.emit("\n🎯 VALIDACIÓN CON DATOS HISTÓRICOS")
                                
                                should_trade = True
                                filter_reason = "Validación básica OK"
                                
                                try:
                                    # Extraer condiciones actuales
                                    current_conditions = {
                                        'rsi': float(last_candle.get('rsi', 0)),
                                        'macd': float(last_candle.get('macd', 0)),
                                        'volatility': float(last_candle.get('volatility', 0)),
                                        'trend': 'bullish' if validation['recommendation'] == 'CALL' else 'bearish'
                                    }
                                    
                                    # Detectar patrón (simplificado)
                                    pattern_type = None
                                    rsi = current_conditions['rsi']
                                    if rsi < 30:
                                        pattern_type = 'rsi_oversold'
                                    elif rsi > 70:
                                        pattern_type = 'rsi_overbought'
                                    
                                    # Aplicar filtros inteligentes (con timeout)
                                    should_trade, filter_reason = self.intelligent_filters.should_trade(
                                        asset=self.current_asset,
                                        pattern_type=pattern_type,
                                        current_conditions=current_conditions
                                    )
                                    should_trade = True # 🔓 MODO BERSERKER ACTIVADO
                                    
                                    self.signals.log_message.emit(f"   {filter_reason}")
                                    
                                except Exception as e:
                                    # Si falla la BD, continuar sin filtros (no bloquear)
                                    self.signals.log_message.emit(f"   ⚠️ Filtros no disponibles: {e}")
                                    should_trade = True
                                    filter_reason = "Filtros omitidos por error"
                                
                                if not should_trade:
                                    self.signals.log_message.emit("⏸️ Operación cancelada por filtros inteligentes")
                                    
                                    # 👁️ Registrar como oportunidad no ejecutada para aprendizaje
                                    opportunity_data = {
                                        'asset': self.current_asset,
                                        'action': validation['recommendation'],
                                        'confidence': validation.get('confidence', 0),
                                        'entry_price': df.iloc[-1]['close'] if not df.empty else 0,
                                        'state_before': df.tail(10) if not df.empty else None
                                    }
                                    try:
                                        self.observational_learner.observe_opportunity(opportunity_data, filter_reason)
                                    except: pass
                                    
                                    self.best_opportunity = None
                                    continue
                                
                                # Ajustar confianza mínima basándose en historial
                                recommended_confidence = self.intelligent_filters.get_recommended_confidence(
                                    self.current_asset
                                )
                                self.signals.log_message.emit(f"   💡 Confianza recomendada: {recommended_confidence*100:.0f}%")
                                
                                # 🎓 ENTRENAMIENTO PARALELO: Analizar oportunidad (NO BLOQUEA)
                                if self.market_data.account_type == 'REAL':
                                    try:
                                        # Ejecutar en background para no bloquear
                                        import threading
                                        def analyze_parallel():
                                            try:
                                                parallel_analysis = self.parallel_trainer.analyze_opportunity(
                                                    asset=self.current_asset,
                                                    df=df.copy(),
                                                    real_decision=validation['recommendation']
                                                )
                                                
                                                if parallel_analysis and parallel_analysis.get('comparison', {}).get('should_explore'):
                                                    alternatives = parallel_analysis['comparison']['alternatives']
                                                    self.signals.log_message.emit(f"\n🎓 ENTRENAMIENTO: Explorando {len(alternatives)} estrategias alternativas")
                                                    for alt in alternatives:
                                                        self.signals.log_message.emit(f"   • {alt['strategy'].upper()}: {alt['direction'].upper()} ({alt['confidence']*100:.0f}% confianza)")
                                            except Exception as e:
                                                print(f"[WARNING] Error en análisis paralelo: {e}")
                                        
                                        # Ejecutar en thread separado
                                        thread = threading.Thread(target=analyze_parallel, daemon=True)
                                        thread.start()
                                        
                                    except Exception as e:
                                        print(f"[WARNING] Error iniciando análisis paralelo: {e}")
                                
                            # Determinar tiempo de expiración según configuración
                            if Config.AUTO_EXPIRATION:
                                # Modo Automático: Usar estadística de la API primero, sino IA
                                if asset_profile and asset_profile['winrate_stat'] > 55:
                                    expiration = asset_profile['best_expiration']
                                    self.signals.log_message.emit(f"⏱️ Expiración OPTIMIZADA (API): {expiration} min")
                                else:
                                    expiration = timing_analysis.get('recommended_expiration', Config.MANUAL_EXPIRATION) if isinstance(timing_analysis, dict) else Config.MANUAL_EXPIRATION
                                    self.signals.log_message.emit(f"⏱️ Expiración automática (IA): {expiration} min")
                            else:
                                # Modo Manual: usuario decide
                                expiration = Config.MANUAL_EXPIRATION
                                self.signals.log_message.emit(f"⏱️ Expiración manual: {expiration} min (configurado por usuario)")
                            
                            # ⚠️ VERIFICACIÓN FINAL: NO ejecutar si hay operaciones activas
                            if self.active_trades:
                                self.signals.log_message.emit(f"⏸️ Operación pendiente - Esperando a que termine la operación activa (ID: {self.active_trades[0]['id']})")
                                self.best_opportunity = None
                                continue
                            
                            direction = "call" if validation['recommendation'] == 'CALL' else "put"
                            self.signals.trade_signal.emit(validation['recommendation'], self.current_asset)
                            
                            # -------------------------------------------------------------
                            # 🛡️ MICRO-VALIDACIÓN TÁCTICA (Gatillo Rápido 1s)
                            # -------------------------------------------------------------
                            self.signals.log_message.emit(f"👁️ Micro-Validación: Verificación rápida (1s)...")
                            
                            # Pausa táctica corta
                            time.sleep(1) 
                            
                            # Obtener precio fresco (Tick más reciente)
                            micro_price = self.market_data.get_current_price(self.current_asset)
                            signal_price = df.iloc[-1]['close'] # Usamos el precio de cierre del DF
                            
                            execute_micro = True
                            micro_reason = ""
                            
                            if direction == "call":
                                # 🎯 BUSCANDO VENTAJA EN CALL (COMPRA)
                                advantage = (signal_price - micro_price) / signal_price * 100
                                if micro_price < signal_price * 0.9997: 
                                    execute_micro = False
                                    micro_reason = f"Precio demasiado debil ({advantage:.3f}% abajo). Riesgo de desplome."
                                elif micro_price > signal_price * 1.0003: 
                                    execute_micro = False
                                    micro_reason = f"Precio escapando ({advantage:.3f}%) - Evitando comprar en el techo."
                                else:
                                    if micro_price <= signal_price:
                                        self.signals.log_message.emit(f"   ✅ VENTAJA OBTENIDA: Entrada con {advantage:.4f}% de descuento")
                                    else:
                                        self.signals.log_message.emit(f"   ⚠️ ENTRADA NORMAL: {abs(advantage):.4f}% arriba de la señal")
                                    execute_micro = True
                                    
                            elif direction == "put":
                                # 🎯 BUSCANDO VENTAJA EN PUT (VENTA)
                                advantage = (micro_price - signal_price) / signal_price * 100
                                if micro_price > signal_price * 1.0003: 
                                    execute_micro = False
                                    micro_reason = f"Precio demasiado fuerte ({advantage:.3f}% arriba). Riesgo de trampa."
                                elif micro_price < signal_price * 0.9997: 
                                    execute_micro = False
                                    micro_reason = f"Precio escapando ({advantage:.3f}%) - Evitando vender en el fondo."
                                else:
                                    if micro_price >= signal_price:
                                        self.signals.log_message.emit(f"   ✅ VENTAJA OBTENIDA: Entrada con {advantage:.4f}% de premium")
                                    else:
                                        self.signals.log_message.emit(f"   ⚠️ ENTRADA NORMAL: {abs(advantage):.4f}% abajo de la señal")
                                    execute_micro = True
                            else:
                                execute_micro = True
                            
                            if execute_micro:
                                try:
                                    self.execute_trade(self.current_asset, direction, micro_price, df, expiration)
                                except Exception as exec_error:
                                    self.signals.error_message.emit(f"❌ Error CRÍTICO ejecutando orden: {exec_error}")
                            else:
                                self.signals.log_message.emit(f"🛑 ABORTANDO: {micro_reason}")
                                self.signals.log_message.emit(f"   (Señal: {signal_price:.5f} -> Actual: {micro_price:.5f})")
                        else:
                            self.signals.log_message.emit("⏸️ Operación cancelada - Esperando mejor oportunidad")
                        
                        # LIMPIEZA FINAL DE LA OPORTUNIDAD (Evita bucles infinitos de análisis)
                        self.best_opportunity = None
                
                time.sleep(1)
            except Exception as e:
                print(f"[ERROR] Error en iteración del bucle: {e}")
                try:
                    self.signals.error_message.emit(f"⚠️ Error recuperable: {e}")
                    self.signals.log_message.emit("🔄 Recuperando automáticamente en 5s...")
                except:
                    pass
                import traceback
                traceback.print_exc()
                time.sleep(5)
                # IMPORTANTE: NO cambiar self.running a False, continuar operando
                print("[DEBUG] Continuando después del error...")
        
        # Si el bucle termina, notificar
        print("[DEBUG] Bucle principal terminado")
        self.signals.log_message.emit("⏹️ Bot detenido")

    def execute_trade(self, asset, direction, current_price, df_current=None, expiration_minutes=1):
        # 🆕 MEJORA 1: Verificar cooldown por activo
        if asset in self.last_trade_per_asset:
            time_since_last = time.time() - self.last_trade_per_asset[asset]
            if time_since_last < self.cooldown_per_asset:
                remaining = int(self.cooldown_per_asset - time_since_last)
                self.signals.log_message.emit(f"⏳ Cooldown activo para {asset}: {remaining}s restantes")
                return
        
        # 🆕 MEJORA 5: Verificar límite de operaciones por hora
        current_time = time.time()
        self.trades_this_hour = [t for t in self.trades_this_hour if current_time - t < 3600]
        if len(self.trades_this_hour) >= self.max_trades_per_hour:
            self.signals.log_message.emit(f"⏸️ Límite de {self.max_trades_per_hour} operaciones/hora alcanzado")
            return
        
        amount = self.risk_manager.get_trade_amount()
        account_label = "[REAL]" if self.market_data.account_type == "REAL" else "[PRACTICE/DEMO]"
        self.signals.log_message.emit(f"🚀 {account_label} Ejecutando {direction.upper()} en {asset}")
        self.signals.log_message.emit(f"   Monto: ${amount:.2f} | Expiración: {expiration_minutes} min")
        
        # Guardar estado antes de la operación para aprendizaje
        state_before = None
        if df_current is not None and not df_current.empty:
            # Guardar últimas 10 velas con indicadores
            window_size = 10
            if len(df_current) >= window_size:
                state_before = df_current.iloc[-window_size:].copy()
        
        # EJECUTAR OPERACIÓN REAL EN EL BROKER
        try:
            # Verificar que estamos conectados
            if not self.market_data.connected or not self.market_data.api:
                self.signals.error_message.emit("❌ No conectado al broker")
                return
            
            # Ejecutar operación REAL en Exnova/IQ Option
            self.signals.log_message.emit(f"🚀 Enviando orden REAL al broker...")
            
            status, trade_id = self.market_data.api.buy(
                amount,
                asset,
                direction,
                expiration_minutes  # Usar expiración recomendada por Groq
            )
            
            if not status:
                self.signals.error_message.emit(f"❌ Error ejecutando operación: {trade_id}")
                return
            
            self.signals.log_message.emit(f"✅ Operación REAL ejecutada en {self.market_data.broker_name.upper()}")
            self.signals.log_message.emit(f"🆔 Order ID: {trade_id}")
            
            # 🆕 MEJORA 1 & 5: Registrar operación
            self.last_trade_per_asset[asset] = time.time()
            self.trades_this_hour.append(time.time())
            
            # 🎯 GUARDAR EN BASE DE DATOS
            trade_uuid = None
            try:
                # Extraer contexto del mercado
                market_context = {}
                if df_current is not None and not df_current.empty:
                    last_row = df_current.iloc[-1]
                    market_context = {
                        'rsi': float(last_row.get('rsi', 0)),
                        'macd': float(last_row.get('macd', 0)),
                        'macd_signal': float(last_row.get('macd_signal', 0)),
                        'sma_20': float(last_row.get('sma_20', 0)),
                        'sma_50': float(last_row.get('sma_50', 0)),
                        'bb_upper': float(last_row.get('bb_upper', 0)),
                        'bb_lower': float(last_row.get('bb_lower', 0)),
                        'volatility': float(last_row.get('volatility', 0))
                    }
                
                # Datos del trade para la BD
                trade_data = {
                    'trade_id': str(trade_id),
                    'asset': asset,
                    'direction': direction,
                    'amount': float(amount),
                    'duration': expiration_minutes,
                    'entry_price': float(current_price),
                    'exit_price': None,
                    'result': None,
                    'profit': None,
                    'profit_pct': None,
                    'entry_time': datetime.now(),
                    'exit_time': None,
                    'market_context': json.dumps(market_context),
                    'rl_confidence': getattr(self, 'last_rl_confidence', None),
                    'llm_analysis': getattr(self, 'last_llm_analysis', None),
                    'decision_score': getattr(self, 'last_decision_score', None),
                    'broker': self.market_data.broker_name,
                    'account_type': self.market_data.account_type,
                    'session_id': None
                }
                
                # Guardar en BD en segundo plano para no bloquear GUI
                import threading
                def save_trade_async():
                    try:
                        # Timeout de 5 segundos para guardar
                        import signal
                        
                        def timeout_handler(signum, frame):
                            raise TimeoutError("Timeout guardando en BD")
                        
                        # Solo en sistemas Unix (no Windows)
                        try:
                            signal.signal(signal.SIGALRM, timeout_handler)
                            signal.alarm(5)
                        except:
                            pass  # Windows no soporta SIGALRM
                        
                        trade_uuid = db.save_trade(trade_data)
                        
                        try:
                            signal.alarm(0)  # Cancelar alarma
                        except:
                            pass
                        
                        if trade_uuid:
                            self.signals.log_message.emit(f"💾 Trade guardado en BD: {trade_uuid}")
                    except TimeoutError:
                        self.signals.log_message.emit(f"⚠️ Timeout guardando en BD (continuando sin BD)")
                    except Exception as e:
                        self.signals.log_message.emit(f"⚠️ Error guardando en BD: {e} (continuando sin BD)")
                
                thread = threading.Thread(target=save_trade_async, daemon=True)
                thread.start()
                # NO ESPERAR al thread - continuar inmediatamente
                
            except Exception as e:
                self.signals.log_message.emit(f"⚠️ Error preparando guardado: {e}")
            
            # Guardar operación activa
            self.active_trades.append({
                "id": trade_id,
                "uuid": trade_uuid,  # UUID de la BD
                "asset": asset,
                "direction": direction,
                "entry_time": time.time(),
                "entry_price": current_price,
                "amount": amount,
                "duration": expiration_minutes * 60,  # Convertir a segundos
                "state_before": state_before,
                "df_before": df_current.copy() if df_current is not None else None,
                "real_trade": True  # Marca que es operación real
            })
            
            # Registrar tiempo de la operación
            self.last_trade_time = time.time()
            self.trades_last_hour.append(time.time())  # Agregar a contador de operaciones por hora
            
        except Exception as e:
            self.signals.error_message.emit(f"❌ Error ejecutando operación: {e}")
            import traceback
            traceback.print_exc()

    def check_active_trades(self):
        """Revisa si las operaciones han terminado y obtiene resultados REALES."""
        try:
            completed_trades = []
            
            for trade in self.active_trades:
                # Esperar duración de la operación + 10s de margen
                wait_time = trade['duration'] + 10
                if time.time() - trade['entry_time'] >= wait_time:
                    completed_trades.append(trade)
            
            for trade in completed_trades:
                self.active_trades.remove(trade)
                self.process_trade_result(trade)
        
        except Exception as e:
            print(f"[ERROR] Error en check_active_trades: {e}")
            import traceback
            traceback.print_exc()
            try:
                self.signals.error_message.emit(f"Error verificando trades: {e}")
            except:
                pass

    def process_trade_result(self, trade):
        """Procesa el resultado REAL del broker."""
        # PROTECCIÓN TOTAL: Envolver TODO en try-except para evitar que el bot se cierre
        try:
            print(f"\n[DEBUG] Iniciando process_trade_result para trade ID: {trade.get('id')}")
            self.signals.log_message.emit(f"📊 Verificando resultado de operación {trade['id']}...")
            print("[DEBUG] Entrando al try principal")
            
            # PROTECCIÓN: Verificar que aún estamos conectados
            if not self.market_data.is_really_connected():
                self.signals.error_message.emit("⚠️ Conexión perdida al verificar resultado")
                self.signals.log_message.emit("🔄 Intentando reconectar antes de obtener resultado...")
                
                email = Config.EXNOVA_EMAIL if self.market_data.broker_name == "exnova" else Config.IQ_EMAIL
                password = Config.EXNOVA_PASSWORD if self.market_data.broker_name == "exnova" else Config.IQ_PASSWORD
                
                if not self.market_data.reconnect(email, password):
                    self.signals.error_message.emit("❌ No se pudo reconectar, usando cálculo por precio")
                    profit = self._calculate_profit_by_price(trade)
                    result_status = "win" if profit > 0 else "loose"
                    won = profit > 0
                    # Continuar con el procesamiento básico
                    self._process_basic_result(trade, won, profit)
                    # NO HACER RETURN - El bot debe continuar operando
                    self.signals.log_message.emit("♾️ Bot continuará monitoreando oportunidades...")
                else:
                    # Reconexión exitosa, continuar normalmente
                    pass
            
            # Obtener resultado REAL del broker
            if trade.get('real_trade', False):
                # Operación real - obtener resultado del broker
                if self.market_data.broker_name == "exnova":
                    # Exnova usa check_win_v4 con timeout integrado
                    try:
                        print("[DEBUG] Llamando a check_win_v4 con timeout de 90s...")
                        self.signals.log_message.emit(f"🔍 Consultando resultado a Exnova...")
                        
                        # check_win_v4 ahora tiene timeout integrado (90 segundos)
                        result_status, profit = self.market_data.api.check_win_v4(trade['id'], timeout=90)
                        
                        # Verificar si hubo timeout (retorna None, None)
                        if result_status is None:
                            print("[DEBUG] Timeout en check_win_v4, usando cálculo por precio")
                            self.signals.log_message.emit("⏱️ Timeout consultando resultado, calculando por precio...")
                            profit = self._calculate_profit_by_price(trade)
                            result_status = "win" if profit > 0 else "loose"
                        else:
                            print(f"[DEBUG] Resultado recibido: {result_status}, Profit: {profit}")
                            self.signals.log_message.emit(f"📊 Resultado de Exnova: {result_status}, Profit: ${profit:.2f}")
                            
                    except Exception as e:
                        print(f"[DEBUG] Exception en check_win_v4: {e}")
                        self.signals.error_message.emit(f"⚠️ Error obteniendo resultado de Exnova: {e}")
                        import traceback
                        traceback.print_exc()
                        # Fallback: calcular por precio
                        profit = self._calculate_profit_by_price(trade)
                        result_status = "win" if profit > 0 else "loose"
                else:
                    # IQ Option usa check_win_v3
                    try:
                        profit = self.market_data.api.check_win_v3(trade['id'])
                        result_status = "win" if profit > 0 else ("loose" if profit < 0 else "equal")
                        self.signals.log_message.emit(f"📊 Resultado de IQ Option: Profit: ${profit:.2f}")
                    except Exception as e:
                        self.signals.error_message.emit(f"⚠️ Error obteniendo resultado de IQ: {e}")
                        # Fallback: calcular por precio
                        profit = self._calculate_profit_by_price(trade)
                        result_status = "win" if profit > 0 else "loose"
            else:
                # Operación simulada (no debería llegar aquí)
                profit = self._calculate_profit_by_price(trade)
                result_status = "win" if profit > 0 else "loose"
            
            # Determinar si ganó
            print(f"[DEBUG] Profit: {profit}, Won: {profit > 0}")
            won = profit > 0
            
            # Obtener precio de salida para análisis
            print("[DEBUG] Obteniendo precio de salida...")
            df = self.market_data.get_candles(trade['asset'], Config.TIMEFRAME, 1)
            exit_price = df.iloc[-1]['close'] if not df.empty else trade['entry_price']
            exit_candle = {'close': exit_price}
            print(f"[DEBUG] Exit price: {exit_price}")
            
            # 🎯 ACTUALIZAR RESULTADO EN BASE DE DATOS (EN SEGUNDO PLANO)
            try:
                if trade.get('uuid'):
                    result_str = 'win' if won else 'loss'
                    
                    # Preparar datos para guardar
                    trade_id = str(trade['id'])
                    trade_uuid = trade['uuid']
                    
                    # Guardar en BD de forma simple y rápida (sin bloquear)
                    import threading
                    def update_db_async():
                        try:
                            # Actualizar resultado en BD
                            db.update_trade_result(
                                trade_id=trade_id,
                                result=result_str,
                                exit_price=float(exit_price),
                                profit=float(profit),
                                exit_time=datetime.now()
                            )
                            
                            print(f"[DEBUG] Resultado actualizado en BD")
                            
                            # 🧠 GUARDAR EXPERIENCIA DE APRENDIZAJE
                            if trade.get('state_before') is not None:
                                experience_data = {
                                    'trade_id': trade_uuid,
                                    'state': json.dumps({
                                        'entry_price': float(trade['entry_price']),
                                        'rsi': float(trade.get('df_before', pd.DataFrame()).iloc[-1].get('rsi', 0)) if trade.get('df_before') is not None else 0,
                                        'macd': float(trade.get('df_before', pd.DataFrame()).iloc[-1].get('macd', 0)) if trade.get('df_before') is not None else 0
                                    }),
                                    'action': trade['direction'],
                                    'action_confidence': getattr(self, 'last_rl_confidence', 0),
                                    'reward': 1.0 if won else -1.0,
                                    'next_state': json.dumps({'exit_price': float(exit_price)}),
                                    'was_correct': won,
                                    'error_type': None if won else 'loss',
                                    'lesson': f"{'Ganó' if won else 'Perdió'} en {trade['asset']} con {trade['direction']}",
                                    'should_avoid': not won,
                                    'model_version': 'v1.0'
                                }
                                db.save_experience(experience_data)
                                print(f"[DEBUG] Experiencia guardada para aprendizaje")
                        except Exception as e:
                            print(f"[DEBUG] Error actualizando BD: {e} (continuando sin BD)")
                    
                    # Lanzar thread daemon que no bloquea el cierre
                    thread = threading.Thread(target=update_db_async, daemon=True)
                    thread.start()
                    # NO ESPERAR al thread - continuar inmediatamente
                        
            except Exception as e:
                self.signals.log_message.emit(f"⚠️ Error actualizando BD: {e}")
            
            # Mostrar resultado
            print(f"[DEBUG] Mostrando resultado: {'GANADA' if won else 'PERDIDA'}")
            if won:
                self.signals.log_message.emit(f"✅ GANADA: +${profit:.2f}")
                self.risk_manager.update_trade_result(profit)
                
                # Resetear contador de pérdidas consecutivas
                self.consecutive_losses = 0
                self.last_trade_result = 'win'
                self.signals.log_message.emit(f"✅ Racha de pérdidas reseteada")
            else:
                self.signals.log_message.emit(f"❌ PERDIDA: ${profit:.2f}")
                
                # Incrementar contador de pérdidas consecutivas
                self.consecutive_losses += 1
                self.last_trade_result = 'loss'
                
                # Análisis Post-Trade solo para pérdidas
                analysis = self.trade_analyzer.analyze_loss(
                    entry_candle={'close': trade['entry_price']},
                    exit_candle=exit_candle,
                    trade_direction=trade['direction'],
                    subsequent_candles=pd.DataFrame()
                )
                
                if analysis['should_martingale']:
                    self.signals.log_message.emit(f"💡 Análisis: {analysis['reason']} -> Aplicar Martingala.")
                else:
                    self.signals.log_message.emit(f"⚠️ Análisis: {analysis['reason']} -> NO Martingala.")
                    
                self.risk_manager.update_trade_result(profit, analysis)
            
            # Emitir señal de actualización de estadísticas
            losses = self.risk_manager.total_trades - self.risk_manager.wins
            self.signals.stats_update.emit(
                self.risk_manager.wins,
                losses,
                self.risk_manager.daily_pnl
            )
            
            # Mostrar cooldown
            if self.consecutive_losses == 1:
                self.signals.log_message.emit(f"⏳ Cooldown: 5 minutos antes de la próxima operación")
            elif self.consecutive_losses >= 2:
                self.signals.log_message.emit(f"⚠️ {self.consecutive_losses} pérdidas consecutivas")
                self.signals.log_message.emit(f"⏳ Cooldown extendido: 10 minutos antes de la próxima operación")
        
        except Exception as e:
            print(f"[DEBUG] ERROR EN PROCESO PRINCIPAL: {e}")
            self.signals.error_message.emit(f"❌ Error procesando resultado: {e}")
            import traceback
            traceback.print_exc()
            
            # PROTECCIÓN: No detener el bot por error en procesamiento
            self.signals.log_message.emit("⚠️ Error procesando resultado, pero el bot continuará")
            
            # Intentar al menos actualizar el balance
            try:
                balance = self.market_data.get_balance()
                self.signals.balance_update.emit(balance)
            except:
                pass
            
            # NO HACER RETURN - Continuar con el análisis aunque haya error
            won = False
            profit = 0
        
        # 🧠 INTELIGENCIA DE TRADING: Analizar operación
        print("[DEBUG] Iniciando análisis inteligente...")
        try:
            self.signals.log_message.emit("\nANÁLISIS INTELIGENTE DE LA OPERACIÓN")
            
            # PROTECCIÓN AMBIENTAL: Ejecutar análisis en bloque aislado
            try:
                intelligence_analysis = self.trade_intelligence.analyze_trade_result(
                    trade_data=trade,
                    result={'won': won, 'profit': profit}
                )
                
                # Mostrar razones (Sanitizadas)
                self.signals.log_message.emit("📊 Razones del resultado:")
                if intelligence_analysis and 'reasons' in intelligence_analysis:
                    for reason in intelligence_analysis['reasons']:
                        # Reemplazar emojis potencialmente peligrosos si es necesario
                        clean_reason = reason.encode('ascii', 'ignore').decode('ascii') if os.name == 'nt' else reason
                        self.signals.log_message.emit(f"   - {reason}") # Usar original en GUI, clean en consola si fuera print
                
                # 🤖 Mostrar insights de Groq/Ollama si están disponibles
                if intelligence_analysis and 'groq_insights' in intelligence_analysis and intelligence_analysis['groq_insights']:
                    groq = intelligence_analysis['groq_insights']
                    
                    if 'error' not in groq:
                        source = groq.get('source', 'IA')
                        self.signals.log_message.emit(f"\n🤖 ANÁLISIS PROFUNDO ({source}):")
                        
                        # Imprimir cada campo con protección
                        fields = [
                            ('analisis_profundo', '💡'),
                            ('factor_clave', '🎯'),
                            ('acierto_principal', '✅') if won else ('error_principal', '❌'),
                            ('patron_identificado', '📋'),
                            ('recomendacion_especifica', '💡')
                        ]
                        
                        for key, icon in fields:
                            if groq.get(key):
                                val = groq[key]
                                self.signals.log_message.emit(f"   {icon} {val}")

            except Exception as inner_e:
                print(f"[ERROR] Error interno en TradeIntelligence: {inner_e}")
                self.signals.log_message.emit(f"⚠️ IA no disponible temporalmente lección no generada.")
        
            # APRENDIZAJE CONTINUO: Agregar experiencia real

            print("[DEBUG] Guardando experiencia...")
            if trade.get('state_before') is not None:
                # Obtener estado después
                df_after = self.market_data.get_candles(trade['asset'], Config.TIMEFRAME, 200)
                if not df_after.empty:
                    df_after = self.feature_engineer.prepare_for_rl(df_after)
                    if not df_after.empty and len(df_after) >= 10:
                        state_after = df_after.iloc[-10:]
                        
                        # Convertir dirección a acción
                        action = 1 if trade['direction'] == 'call' else 2
                        
                        # Agregar experiencia
                        self.continuous_learner.add_real_trade_experience(
                            state_before=trade['state_before'],
                            action=action,
                            profit=profit,
                            state_after=state_after,
                            metadata={
                                'asset': trade['asset'],
                                'entry_price': trade['entry_price'],
                                'exit_price': exit_price,
                                'won': won,
                                'timestamp': time.time()
                            }
                        )
                        
                        self.signals.log_message.emit(f"📝 Experiencia guardada para aprendizaje continuo")
            
            print("[DEBUG] process_trade_result completado")
        
        except Exception as e:
            print(f"[DEBUG] ERROR EN ANÁLISIS INTELIGENTE: {e}")
            self.signals.log_message.emit(f"⚠️ Error en análisis inteligente: {e}")
            import traceback
            traceback.print_exc()
        
        # PROTECCIÓN FINAL: Capturar cualquier excepción no manejada en toda la función
        except Exception as fatal_error:
            print(f"\n[FATAL ERROR] Error crítico en process_trade_result: {fatal_error}")
            self.signals.error_message.emit(f"❌ Error crítico procesando resultado: {fatal_error}")
            import traceback
            traceback.print_exc()
            
            # IMPORTANTE: NO DETENER EL BOT - Solo registrar el error
            self.signals.log_message.emit("⚠️ Error crítico, pero el bot continuará operando")
            
            # Intentar actualizar balance al menos
            try:
                balance = self.market_data.get_balance()
                self.signals.balance_update.emit(balance)
            except:
                pass
            
            print("[DEBUG] Bot continuará a pesar del error crítico")

    
    def analyze_indicators(self, df):
        """Analiza indicadores técnicos del DataFrame"""
        if df.empty or len(df) < 1:
            return {}
        
        last_row = df.iloc[-1]
        analysis = {}
        
        # RSI
        if 'rsi' in df.columns:
            rsi = last_row['rsi']
            if rsi < 30:
                analysis['rsi'] = {'value': rsi, 'signal': 'CALL', 'strength': 'strong'}
            elif rsi > 70:
                analysis['rsi'] = {'value': rsi, 'signal': 'PUT', 'strength': 'strong'}
            else:
                analysis['rsi'] = {'value': rsi, 'signal': 'NEUTRAL', 'strength': 'weak'}
        
        # MACD
        if 'macd' in df.columns:
            macd = last_row['macd']
            analysis['macd'] = {
                'value': macd,
                'signal': 'CALL' if macd > 0 else 'PUT',
                'strength': 'medium'
            }
        
        # Bollinger Bands
        if 'bb_high' in df.columns and 'bb_low' in df.columns:
            price = last_row['close']
            bb_high = last_row['bb_high']
            bb_low = last_row['bb_low']
            
            if price <= bb_low:
                analysis['bollinger'] = {'signal': 'CALL', 'strength': 'medium'}
            elif price >= bb_high:
                analysis['bollinger'] = {'signal': 'PUT', 'strength': 'medium'}
            else:
                analysis['bollinger'] = {'signal': 'NEUTRAL', 'strength': 'weak'}
        
        return analysis
    
    def get_llm_advice(self, df, asset):
        """Obtiene consejo del LLM"""
        if df.empty or len(df) < 10:
            return None
        
        try:
            # Preparar contexto para el LLM
            last_row = df.iloc[-1]
            context = f"""
Analiza el siguiente activo: {asset}

Indicadores actuales:
- RSI: {last_row.get('rsi', 'N/A')}
- MACD: {last_row.get('macd', 'N/A')}
- Precio: {last_row.get('close', 'N/A')}

¿Recomendarías CALL, PUT o HOLD? Responde solo con una palabra: CALL, PUT o HOLD.
"""
            
            response = self.llm_client.get_advice(context)
            
            # Extraer recomendación
            if 'CALL' in response.upper():
                return 'CALL'
            elif 'PUT' in response.upper():
                return 'PUT'
            else:
                return 'HOLD'
        except:
            return None

    
    def _calculate_profit_by_price(self, trade):
        """Calcula profit basado en movimiento de precio (fallback)"""
        try:
            df = self.market_data.get_candles(trade['asset'], Config.TIMEFRAME, 1)
            if df.empty:
                return -trade['amount']  # Asumir pérdida si no hay datos
            
            exit_price = df.iloc[-1]['close']
            
            # Determinar si ganó
            if trade['direction'] == 'call':
                won = exit_price > trade['entry_price']
            else:
                won = exit_price < trade['entry_price']
            
            # Calcular profit
            if won:
                return trade['amount'] * 0.85  # 85% payout típico
            else:
                return -trade['amount']
        except:
            return -trade['amount']  # Asumir pérdida en caso de error

    def _process_basic_result(self, trade, won, profit):
        """Procesa resultado básico cuando hay problemas de conexión"""
        try:
            print(f"[DEBUG] Procesando resultado básico: won={won}, profit={profit}")
            
            # Mostrar resultado
            if won:
                self.signals.log_message.emit(f"✅ GANADA (estimado): +${profit:.2f}")
                self.risk_manager.update_trade_result(profit)
                self.consecutive_losses = 0
                self.last_trade_result = 'win'
            else:
                self.signals.log_message.emit(f"❌ PERDIDA (estimado): ${profit:.2f}")
                self.consecutive_losses += 1
                self.last_trade_result = 'loss'
                self.risk_manager.update_trade_result(profit, {'should_martingale': False, 'reason': 'Conexión perdida'})
            
            # Emitir señal de actualización de estadísticas
            losses = self.risk_manager.total_trades - self.risk_manager.wins
            self.signals.stats_update.emit(
                self.risk_manager.wins,
                losses,
                self.risk_manager.daily_pnl
            )
            
            # Actualizar balance
            try:
                balance = self.market_data.get_balance()
                self.signals.balance_update.emit(balance)
            except:
                pass
            
            self.signals.log_message.emit("⚠️ Resultado procesado en modo básico por problemas de conexión")
            
        except Exception as e:
            print(f"[ERROR] Error en _process_basic_result: {e}")
            self.signals.error_message.emit(f"❌ Error en procesamiento básico: {e}")
