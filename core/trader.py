import time
import pandas as pd
from PySide6.QtCore import QThread, Signal, QObject
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
    stats_update = Signal(int, int, float) # wins, losses, total_profit

from core.trade_analyzer import TradeAnalyzer
from core.continuous_learner import ContinuousLearner
from core.decision_validator import DecisionValidator
from core.trade_intelligence import TradeIntelligence
from core.observational_learner import ObservationalLearner

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
        
        self.signals = TraderSignals()
        self.running = False
        self.paused = False
        self.active_trades = [] # Lista de dicts: {id, asset, direction, entry_time, entry_price, amount, state_before, df_before}
        
        # Control de tiempo entre operaciones
        self.last_trade_time = 0
        self.min_time_between_trades = 30  # Mínimo 30 segundos entre operaciones
        self.cooldown_after_loss = 60  # 1 minuto de espera después de perder
        self.consecutive_losses = 0
        self.last_trade_result = None

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

        print("[DEBUG] Entrando al bucle principal while...")
        iteration_count = 0
        last_heartbeat = time.time()
        
        while self.running:
            # Heartbeat cada 60 segundos
            if time.time() - last_heartbeat >= 60:
                self.signals.log_message.emit(f"💓 Bot activo - Iteración #{iteration_count}")
                last_heartbeat = time.time()
            iteration_count += 1
            if iteration_count % 10 == 0:  # Log cada 10 iteraciones
                print(f"[DEBUG] Iteración #{iteration_count}, running={self.running}, paused={self.paused}")
            
            if self.paused:
                time.sleep(1)
                continue

            try:
                # --- Monitoreo de Operaciones Activas ---
                self.check_active_trades()

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
                                time.sleep(60)
                                # Resetear para permitir operar nuevamente
                                self.consecutive_losses = 0
                                self.signals.log_message.emit("🔄 Contador de pérdidas reseteado para reintentar")
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
                    if time_since_last_scan >= 30:
                        self.signals.log_message.emit("🔍 Escaneando oportunidades...")
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
                    continue
                
                # REGLA 2: Verificar tiempo mínimo entre operaciones
                time_since_last_trade = time.time() - self.last_trade_time
                
                # Si perdió la última, esperar más tiempo (cooldown)
                if self.last_trade_result == 'loss':
                    required_wait = self.cooldown_after_loss
                    if self.consecutive_losses >= 2:
                        required_wait = self.cooldown_after_loss * 2  # 10 minutos después de 2 pérdidas
                    
                    if time_since_last_trade < required_wait:
                        remaining = int(required_wait - time_since_last_trade)
                        if remaining % 30 == 0:  # Mostrar cada 30 segundos
                            self.signals.log_message.emit(f"⏳ Cooldown después de pérdida: {remaining}s restantes")
                        continue
                else:
                    # Tiempo normal entre operaciones
                    if time_since_last_trade < self.min_time_between_trades:
                        remaining = int(self.min_time_between_trades - time_since_last_trade)
                        if remaining % 30 == 0:  # Mostrar cada 30 segundos
                            self.signals.log_message.emit(f"⏳ Esperando tiempo mínimo: {remaining}s restantes")
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
                            
                            # 3. 🎯 GROQ ANALIZA EL TIMING PERFECTO
                            timing_analysis = None
                            if self.llm_client and Config.USE_LLM:
                                try:
                                    self.signals.log_message.emit("⏱️ Groq analizando timing óptimo...")
                                    timing_analysis = self.llm_client.analyze_entry_timing(
                                        df=df,
                                        proposed_action=best_opportunity['action'],
                                        proposed_asset=self.current_asset
                                    )
                                    
                                    if timing_analysis:
                                        self.signals.log_message.emit(f"   Momento óptimo: {'✅ SÍ' if timing_analysis['is_optimal'] else '⏳ Esperar'}")
                                        self.signals.log_message.emit(f"   Confianza: {timing_analysis['confidence']*100:.0f}%")
                                        self.signals.log_message.emit(f"   Expiración recomendada: {timing_analysis['recommended_expiration']} min")
                                        self.signals.log_message.emit(f"   Razón: {timing_analysis['reasoning']}")
                                        
                                        # Si Groq dice que espere, evaluar confianza
                                        if not timing_analysis['is_optimal'] and timing_analysis['wait_time'] > 0:
                                            # Si la confianza es decente (>=55%), operar de todos modos
                                            if timing_analysis['confidence'] >= 0.55:
                                                self.signals.log_message.emit(f"⚡ Confianza aceptable ({timing_analysis['confidence']*100:.0f}%), operando sin esperar")
                                            else:
                                                # Confianza baja, registrar como observación y esperar
                                                self.signals.log_message.emit(f"👁️ Registrando oportunidad para aprendizaje observacional...")
                                                
                                                # Registrar oportunidad no ejecutada
                                                self.observational_learner.observe_opportunity(
                                                    opportunity_data={
                                                        'asset': self.current_asset,
                                                        'action': best_opportunity['action'],
                                                        'score': best_opportunity['score'],
                                                        'confidence': timing_analysis['confidence'],
                                                        'entry_price': last_candle['close'],
                                                        'state_before': df.iloc[-10:].copy() if len(df) >= 10 else None
                                                    },
                                                    reason_not_executed=f"Groq: {timing_analysis['reasoning']}"
                                                )
                                                
                                                self.signals.log_message.emit(f"⏳ Esperando {timing_analysis['wait_time']}s para entrada óptima...")
                                                time.sleep(min(timing_analysis['wait_time'], 60))  # Máximo 60s
                                                continue
                                except Exception as e:
                                    self.signals.log_message.emit(f"⚠️ Error en análisis de timing: {e}")
                            
                            # 4. VALIDAR DECISIÓN
                            validation = self.decision_validator.validate_decision(
                                df=df,
                                action=action,
                                indicators_analysis=indicators_analysis,
                                rl_prediction=action,
                                llm_advice=best_opportunity['action']
                            )
                            
                            # 5. MOSTRAR ANÁLISIS
                            summary = self.decision_validator.get_summary(validation)
                            for line in summary.split('\n'):
                                self.signals.log_message.emit(line)
                            
                            # 6. EJECUTAR SOLO SI ES VÁLIDO Y TIMING ES BUENO
                            if validation['valid']:
                                # 🧠 NUEVO: ANÁLISIS DE INTELIGENCIA PRE-TRADE (SUPER INTELLIGENCE)
                                self.signals.log_message.emit("\n🧠 Ejecutando Análisis de Super Inteligencia...")
                                pre_trade_analysis = self.trade_intelligence.evaluate_trade_opportunity(
                                    df=df,
                                    asset=self.current_asset,
                                    proposed_action=validation['recommendation']
                                )
                                
                                if not pre_trade_analysis['approved']:
                                    self.signals.log_message.emit(f"⛔ OPERACIÓN BLOQUEADA POR IA: {pre_trade_analysis['reason']}")
                                    
                                    # Mostrar detalles si existen
                                    if pre_trade_analysis.get('knowledge_analysis'):
                                        ka = pre_trade_analysis['knowledge_analysis']
                                        self.signals.log_message.emit(f"   📚 Memoria: {ka['advice']}")
                                    
                                    if pre_trade_analysis.get('consensus_analysis'):
                                        ca = pre_trade_analysis['consensus_analysis']
                                        self.signals.log_message.emit(f"   🤖 Consenso: {ca['consensus']} (Confianza: {ca['confidence']*100:.0f}%)")
                                        self.signals.log_message.emit(f"   🗣️ Razón: {ca['reasoning']}")
                                    
                                    # Registrar observación y continuar
                                    self.observational_learner.observe_opportunity(
                                        opportunity_data={
                                            'asset': self.current_asset,
                                            'action': best_opportunity['action'],
                                            'score': best_opportunity['score'],
                                            'confidence': pre_trade_analysis['confidence'],
                                            'entry_price': last_candle['close'],
                                            'state_before': df.iloc[-10:].copy() if len(df) >= 10 else None
                                        },
                                        reason_not_executed=f"Super IA: {pre_trade_analysis['reason']}"
                                    )
                                    continue
                                
                                # Si pasa la Super Inteligencia, proceder
                                self.signals.log_message.emit(f"✅ APROBADO POR SUPER IA (Confianza: {pre_trade_analysis['confidence']*100:.0f}%)")
                                
                                # Determinar tiempo de expiración según configuración
                                if Config.AUTO_EXPIRATION:
                                    # Modo Automático: IA decide
                                    expiration = timing_analysis['recommended_expiration'] if timing_analysis else Config.MANUAL_EXPIRATION
                                    self.signals.log_message.emit(f"⏱️ Expiración automática: {expiration} min (recomendado por IA)")
                                else:
                                    # Modo Manual: usuario decide
                                    expiration = Config.MANUAL_EXPIRATION
                                    self.signals.log_message.emit(f"⏱️ Expiración manual: {expiration} min (configurado por usuario)")
                                
                                direction = "call" if validation['recommendation'] == 'CALL' else "put"
                                self.signals.trade_signal.emit(validation['recommendation'], self.current_asset)
                                self.execute_trade(self.current_asset, direction, last_candle['close'], df, expiration)
                            else:
                                self.signals.log_message.emit("⏸️ Operación cancelada - Esperando mejor oportunidad")
                        else:
                            # No hay oportunidad clara, continuar monitoreando
                            pass
                
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
        amount = self.risk_manager.get_trade_amount()
        self.signals.log_message.emit(f"🚀 Ejecutando {direction.upper()} en {asset}")
        self.signals.log_message.emit(f"   Monto: ${amount:.2f}")
        self.signals.log_message.emit(f"   Expiración: {expiration_minutes} min")
        
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
            
            # Guardar operación activa
            self.active_trades.append({
                "id": trade_id,
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
        try:
            print(f"\n[DEBUG] Iniciando process_trade_result para trade ID: {trade.get('id')}")
            self.signals.log_message.emit(f"📊 Verificando resultado de operación {trade['id']}...")
            
            profit = 0
            result_status = "unknown"
            
            # Obtener resultado REAL del broker
            if trade.get('real_trade', False):
                # Intentar hasta 3 veces obtener el resultado
                for attempt in range(3):
                    try:
                        print(f"[DEBUG] Intento {attempt+1} de verificar resultado...")
                        result_status, profit = self.market_data.api.check_win_v4(trade['id'])
                        
                        if result_status: # Si retornó algo válido
                            print(f"[DEBUG] Resultado recibido: {result_status}, Profit: {profit}")
                            self.signals.log_message.emit(f"📊 Resultado de Exnova: {result_status}, Profit: ${profit:.2f}")
                            break
                        else:
                            print("[DEBUG] check_win_v4 retornó None/False, reintentando...")
                            time.sleep(2)
                    except Exception as e:
                        print(f"[DEBUG] Error en intento {attempt+1}: {e}")
                        time.sleep(2)
                
                # Si después de 3 intentos no hay resultado, usar fallback
                if not result_status or result_status == "unknown":
                    print("⚠️ No se pudo obtener resultado del broker, usando cálculo local (Fallback)")
                    self.signals.log_message.emit("⚠️ Usando verificación local (API no respondió)")
                    profit = self._calculate_profit_by_price(trade)
                    result_status = "win" if profit > 0 else "loose"
            else:
                # Operación simulada
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
                
                # Mostrar cooldown
                if self.consecutive_losses == 1:
                    self.signals.log_message.emit(f"⏳ Cooldown: 5 minutos antes de la próxima operación")
                elif self.consecutive_losses >= 2:
                    self.signals.log_message.emit(f"⚠️ {self.consecutive_losses} pérdidas consecutivas")
                    self.signals.log_message.emit(f"⏳ Cooldown extendido: 10 minutos antes de la próxima operación")
        
            # Emitir actualización de estadísticas
            wins = self.risk_manager.wins
            total = self.risk_manager.total_trades
            losses = total - wins
            pnl = self.risk_manager.daily_pnl
            self.signals.stats_update.emit(wins, losses, pnl)

        except Exception as e:
            print(f"[DEBUG] ERROR EN PROCESO PRINCIPAL: {e}")
            self.signals.error_message.emit(f"❌ Error procesando resultado: {e}")
            import traceback
            traceback.print_exc()
            return
        
        # 🧠 INTELIGENCIA DE TRADING: Analizar operación
        print("[DEBUG] Iniciando análisis inteligente...")
        try:
            self.signals.log_message.emit("\n🧠 ANÁLISIS INTELIGENTE DE LA OPERACIÓN")
            
            intelligence_analysis = self.trade_intelligence.analyze_trade_result(
                trade_data=trade,
                result={'won': won, 'profit': profit}
            )
            
            # Mostrar razones
            self.signals.log_message.emit("📊 ¿Por qué " + ("ganó" if won else "perdió") + "?")
            for reason in intelligence_analysis['reasons']:
                self.signals.log_message.emit(f"   {reason}")
            
            # Mostrar lecciones
            for lesson in intelligence_analysis['lessons']:
                self.signals.log_message.emit(f"{lesson}")
            
            # 🤖 Mostrar insights de Groq/Ollama si están disponibles
            if 'groq_insights' in intelligence_analysis and intelligence_analysis['groq_insights']:
                groq = intelligence_analysis['groq_insights']
                
                if 'error' not in groq:
                    source = groq.get('source', 'IA')
                    self.signals.log_message.emit(f"\n🤖 ANÁLISIS PROFUNDO ({source}):")
                    
                    if groq.get('analisis_profundo'):
                        self.signals.log_message.emit(f"   💡 {groq['analisis_profundo']}")
                    
                    if groq.get('factor_clave'):
                        self.signals.log_message.emit(f"   🎯 Factor clave: {groq['factor_clave']}")
                    
                    if won and groq.get('acierto_principal'):
                        self.signals.log_message.emit(f"   ✅ Acierto: {groq['acierto_principal']}")
                    elif not won and groq.get('error_principal'):
                        self.signals.log_message.emit(f"   ❌ Error: {groq['error_principal']}")
                    
                    if groq.get('patron_identificado'):
                        self.signals.log_message.emit(f"   📋 Patrón: {groq['patron_identificado']}")
                    
                    if groq.get('recomendacion_especifica'):
                        self.signals.log_message.emit(f"   💡 Recomendación: {groq['recomendacion_especifica']}")
                    
                    # Mostrar ajustes sugeridos
                    if groq.get('ajuste_confianza') != 'mantener':
                        self.signals.log_message.emit(f"   ⚙️ Sugerencia: {groq['ajuste_confianza']} confianza mínima")
                    if groq.get('ajuste_timing') != 'mantener':
                        self.signals.log_message.emit(f"   ⏱️ Sugerencia: {groq['ajuste_timing']} antes de entrar")
            
            # Mostrar recomendaciones cada 10 operaciones
            if len(self.trade_intelligence.trade_history) % 10 == 0:
                self.signals.log_message.emit("\n💡 RECOMENDACIONES DEL SISTEMA:")
                for rec in intelligence_analysis['recommendations']:
                    self.signals.log_message.emit(f"   {rec}")
                
                # Aplicar recomendaciones automáticamente
                summary = self.trade_intelligence.get_intelligence_summary()
                
                # Ajustar confianza mínima del validador
                self.decision_validator.min_confidence = summary['recommended_min_confidence']
                self.signals.log_message.emit(f"\n⚙️ Ajuste automático: Confianza mínima → {summary['recommended_min_confidence']*100:.0f}%")
                
                # Ajustar score mínimo del asset manager
                if hasattr(self.asset_manager, 'min_score'):
                    self.asset_manager.min_score = summary['recommended_score_threshold']
                    self.signals.log_message.emit(f"⚙️ Ajuste automático: Score mínimo → {summary['recommended_score_threshold']}")
                
                # Aplicar recomendaciones de Groq/Ollama
                self.trade_intelligence._apply_groq_recommendations()
        
        except Exception as e:
            print(f"[DEBUG] ERROR EN ANÁLISIS INTELIGENTE: {e}")
            self.signals.log_message.emit(f"⚠️ Error en análisis inteligente: {e}")
            import traceback
            traceback.print_exc()
        
        # APRENDIZAJE CONTINUO: Agregar experiencia real
        try:
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
        except Exception as e:
            print(f"\n[ERROR] Error guardando experiencia: {e}")
            import traceback
            traceback.print_exc()
        
        print("[DEBUG] process_trade_result completado")

    
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
    def _calculate_profit_by_price(self, trade):
        """
        Calcula el resultado de la operación basado en el precio actual (Fallback)
        Se usa cuando la API del broker falla al verificar el resultado.
        """
        try:
            # Obtener precio actual
            df = self.market_data.get_candles(trade['asset'], Config.TIMEFRAME, 1)
            if df.empty:
                return 0.0
            
            exit_price = df.iloc[-1]['close']
            entry_price = trade['entry_price']
            direction = trade['direction']
            amount = trade['amount']
            payout = 0.85  # Estimado conservador
            
            won = False
            if direction == 'call':
                won = exit_price > entry_price
            else:
                won = exit_price < entry_price
                
            if won:
                return amount * payout
            else:
                return -amount
                
        except Exception as e:
            print(f"[ERROR] Error calculando profit por precio: {e}")
            return 0.0
