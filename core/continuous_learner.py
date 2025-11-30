"""
Continuous Learner - Aprende continuamente de operaciones reales
"""
import numpy as np
import pandas as pd

try:
    from stable_baselines3 import PPO
    from stable_baselines3.common.vec_env import DummyVecEnv
    STABLE_BASELINES_AVAILABLE = True
except ImportError:
    print("⚠️ stable-baselines3 no disponible. Aprendizaje continuo deshabilitado.")
    PPO = None
    DummyVecEnv = None
    STABLE_BASELINES_AVAILABLE = False

try:
    from env.trading_env import BinaryOptionsEnv
except ImportError:
    BinaryOptionsEnv = None
    
from core.experience_buffer import ExperienceBuffer

class ContinuousLearner:
    """
    Sistema de aprendizaje continuo que re-entrena el modelo
    con experiencias reales de trading
    """
    def __init__(self, agent, feature_engineer, market_data):
        self.agent = agent
        self.feature_engineer = feature_engineer
        self.market_data = market_data
        self.experience_buffer = ExperienceBuffer()
        
        # Configuración de Re-entrenamiento
        self.min_experiences_to_train = 20  # Mínimo de experiencias (reducido de 50 a 20)
        self.retrain_frequency = 20  # Re-entrenar cada 20 operaciones (reducido de 100 a 20)
        self.retrain_timesteps = 2000  # Pasos de re-entrenamiento
        
        # Configuración de Evaluación Continua
        self.evaluation_frequency = 10  # Evaluar cada 10 operaciones
        self.min_win_rate = 0.40  # Win rate mínimo aceptable (40%)
        self.max_consecutive_losses = 5  # Máximo de pérdidas consecutivas antes de re-entrenar
        
        # Control de re-entrenamientos
        # IMPORTANTE: Inicializar con el número de experiencias cargadas para evitar bucle
        self.last_retrain_count = len(self.experience_buffer.experiences)
        self.retraining_in_progress = False  # Flag para evitar re-entrenamientos simultáneos
        
    def add_real_trade_experience(self, state_before, action, profit, state_after, metadata=None):
        """
        Agrega experiencia de una operación real
        
        Args:
            state_before: DataFrame con indicadores antes de la operación
            action: Acción tomada (0=HOLD, 1=CALL, 2=PUT)
            profit: Resultado en $ (positivo=ganancia, negativo=pérdida)
            state_after: DataFrame con indicadores después
            metadata: Info adicional (activo, timestamp, etc.)
        """
        # Convertir DataFrames a arrays
        if isinstance(state_before, pd.DataFrame):
            state_before = state_before.values.flatten()
        if isinstance(state_after, pd.DataFrame):
            state_after = state_after.values.flatten()
        
        # Normalizar reward (profit)
        # Convertir $ a reward normalizado
        reward = profit  # Mantener el valor real
        
        # Determinar si terminó (siempre False para trading continuo)
        done = False
        
        # Agregar al buffer
        self.experience_buffer.add_experience(
            state=state_before,
            action=action,
            reward=reward,
            next_state=state_after,
            done=done,
            metadata=metadata
        )
        
        print(f"📝 Experiencia agregada: Action={action}, Reward=${profit:.2f}")
        
        # EVALUACIÓN CONTINUA cada N experiencias
        total_exp = len(self.experience_buffer.experiences)
        
        # Evitar re-entrenamientos si ya se hizo uno recientemente
        if self.retraining_in_progress:
            return
        
        # Solo evaluar si hay experiencias NUEVAS desde el último re-entrenamiento
        new_experiences = total_exp - self.last_retrain_count
        
        # Evaluar cada 10 operaciones NUEVAS
        if new_experiences >= self.evaluation_frequency and new_experiences % self.evaluation_frequency == 0:
            print(f"\n📊 EVALUACIÓN CONTINUA (Operación #{total_exp}, {new_experiences} nuevas)")
            evaluation = self.evaluate_performance()
            print(f"   {evaluation['reason']}")
            
            if evaluation['should_retrain']:
                print(f"   🎓 Acción: {evaluation['action']}")
                if evaluation['action'] == 'RETRAIN_URGENT':
                    print(f"   ⚠️ RE-ENTRENAMIENTO URGENTE")
                self.retrain_from_experiences()
        
        # Re-entrenar cada N experiencias NUEVAS (frecuencia normal)
        elif new_experiences >= self.retrain_frequency:
            print(f"\n🎓 Re-entrenamiento programado ({new_experiences} experiencias nuevas)")
            self.retrain_from_experiences()
    
    def retrain_from_experiences(self):
        """
        Re-entrena el modelo usando experiencias reales + datos frescos
        """
        # Evitar re-entrenamientos simultáneos
        if self.retraining_in_progress:
            print("⚠️ Re-entrenamiento ya en progreso, saltando...")
            return False
        
        try:
            self.retraining_in_progress = True
            
            # Obtener experiencias recientes
            experiences = self.experience_buffer.get_recent_experiences(500)
            
            if len(experiences) < self.min_experiences_to_train:
                print(f"⚠️ Pocas experiencias ({len(experiences)}), se necesitan al menos {self.min_experiences_to_train}")
                return False
            
            print(f"📊 Preparando {len(experiences)} experiencias para entrenamiento...")
            
            # Estadísticas ANTES del re-entrenamiento
            stats = self.experience_buffer.get_statistics()
            print(f"\n📊 Estadísticas ANTES del re-entrenamiento:")
            print(f"   Total: {stats['total']}")
            print(f"   Ganadas: {stats['wins']}")
            print(f"   Perdidas: {stats['losses']}")
            print(f"   Win Rate: {stats['win_rate']:.1f}%")
            print(f"   Profit Total: ${stats['total_profit']:.2f}")
            
            # Si el win rate es muy bajo, re-entrenar con datos frescos
            if stats['win_rate'] < self.min_win_rate * 100:
                print(f"\n⚠️ Win rate bajo ({stats['win_rate']:.1f}%), re-entrenando con datos frescos...")
                result = self.retrain_with_fresh_data()
                
                # Actualizar contador de último re-entrenamiento
                self.last_retrain_count = len(self.experience_buffer.experiences)
                return result
            
            # Si el win rate es aceptable, solo mostrar estadísticas
            print(f"\n✅ Win rate aceptable ({stats['win_rate']:.1f}%), continuando...")
            
            # Actualizar contador
            self.last_retrain_count = len(self.experience_buffer.experiences)
            return True
            
        except Exception as e:
            print(f"❌ Error en re-entrenamiento: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            # IMPORTANTE: Siempre resetear el flag, incluso si hay error
            self.retraining_in_progress = False
    
    def retrain_with_fresh_data(self, asset="EURUSD-OTC", num_candles=1000):
        """
        Re-entrena con datos frescos del broker
        Combina datos históricos con experiencias reales
        """
        print(f"\n🔄 Re-entrenando con datos frescos de {asset}...")
        
        try:
            # Obtener datos frescos
            import time
            df = self.market_data.get_candles(asset, 60, num_candles, time.time())
            
            if df.empty:
                print("❌ No se pudieron obtener datos")
                return False
            
            print(f"✅ Obtenidas {len(df)} velas")
            
            # Procesar indicadores
            df_processed = self.feature_engineer.prepare_for_rl(df)
            
            if df_processed.empty:
                print("❌ Error procesando indicadores")
                return False
            
            print(f"✅ Indicadores calculados ({df_processed.shape[1]} features)")
            
            # Crear entorno
            env = DummyVecEnv([lambda: BinaryOptionsEnv(
                df=df_processed,
                window_size=10,
                initial_balance=1000
            )])
            
            # Re-entrenar
            print(f"🎓 Re-entrenando por {self.retrain_timesteps} pasos...")
            
            # Actualizar entorno del agente
            self.agent.env = env
            
            # Si el modelo existe, continuar entrenamiento
            if self.agent.model is not None:
                print("📦 Actualizando modelo existente...")
                self.agent.model.set_env(env)
                self.agent.model.learn(total_timesteps=self.retrain_timesteps)
            else:
                print("📦 Creando nuevo modelo...")
                # Crear nuevo modelo
                self.agent.create_model()
                self.agent.train(timesteps=self.retrain_timesteps)
            
            # Guardar
            print("💾 Guardando modelo...")
            self.agent.save()
            
            print("✅ Re-entrenamiento completado exitosamente")
            
            # Mostrar estadísticas de experiencias
            stats = self.experience_buffer.get_statistics()
            print(f"\n📊 Experiencias acumuladas:")
            print(f"   Total: {stats['total']}")
            print(f"   Win Rate: {stats['win_rate']:.1f}%")
            print(f"   Profit Total: ${stats['total_profit']:.2f}")
            
            # IMPORTANTE: Actualizar contador para evitar bucle
            self.last_retrain_count = len(self.experience_buffer.experiences)
            
            print("🔄 Continuando operaciones normales...\n")
            
            return True
            
        except Exception as e:
            print(f"❌ Error en re-entrenamiento: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_learning_stats(self):
        """Obtiene estadísticas del aprendizaje"""
        return self.experience_buffer.get_statistics()
    
    def evaluate_performance(self):
        """
        Evalúa el rendimiento actual del bot
        
        Returns:
            dict: {
                'should_retrain': bool,
                'reason': str,
                'stats': dict,
                'action': str
            }
        """
        stats = self.experience_buffer.get_statistics()
        
        result = {
            'should_retrain': False,
            'reason': '',
            'stats': stats,
            'action': 'CONTINUE'
        }
        
        # No hay suficientes datos
        if stats['total'] < 10:
            result['reason'] = "Pocas operaciones para evaluar"
            return result
        
        # Obtener últimas 10 experiencias
        recent = self.experience_buffer.get_recent_experiences(10)
        recent_wins = sum(1 for exp in recent if exp['reward'] > 0)
        recent_win_rate = (recent_wins / len(recent)) * 100 if recent else 0
        
        # Calcular pérdidas consecutivas
        consecutive_losses = 0
        for exp in reversed(recent):
            if exp['reward'] < 0:
                consecutive_losses += 1
            else:
                break
        
        # CRITERIO 1: Win rate muy bajo
        if recent_win_rate < self.min_win_rate * 100:
            result['should_retrain'] = True
            result['reason'] = f"Win rate bajo ({recent_win_rate:.0f}% < {self.min_win_rate*100:.0f}%)"
            result['action'] = 'RETRAIN'
            return result
        
        # CRITERIO 2: Muchas pérdidas consecutivas
        if consecutive_losses >= self.max_consecutive_losses:
            result['should_retrain'] = True
            result['reason'] = f"{consecutive_losses} pérdidas consecutivas"
            result['action'] = 'RETRAIN_URGENT'
            return result
        
        # CRITERIO 3: Profit negativo en últimas 10 ops
        recent_profit = sum(exp['reward'] for exp in recent)
        if recent_profit < -50:  # Perdió más de $50
            result['should_retrain'] = True
            result['reason'] = f"Profit negativo (${recent_profit:.2f})"
            result['action'] = 'RETRAIN'
            return result
        
        # Todo bien
        result['reason'] = f"Rendimiento aceptable (Win rate: {recent_win_rate:.0f}%)"
        result['action'] = 'CONTINUE'
        return result
    
    def should_pause_trading(self):
        """
        Determina si el bot debería pausar operaciones
        
        Returns:
            tuple: (should_pause: bool, reason: str)
        """
        stats = self.experience_buffer.get_statistics()
        
        # No hay suficientes datos
        if stats['total'] < 5:
            return False, ""
        
        # Obtener últimas experiencias
        recent = self.experience_buffer.get_recent_experiences(10)
        
        # Calcular pérdidas consecutivas
        consecutive_losses = 0
        for exp in reversed(recent):
            if exp['reward'] < 0:
                consecutive_losses += 1
            else:
                break
        
        # PAUSAR si hay muchas pérdidas consecutivas
        if consecutive_losses >= self.max_consecutive_losses:
            return True, f"🛑 {consecutive_losses} pérdidas consecutivas - PAUSANDO para re-entrenar"
        
        # PAUSAR si el win rate es muy bajo
        if len(recent) >= 10:
            recent_wins = sum(1 for exp in recent if exp['reward'] > 0)
            recent_win_rate = (recent_wins / len(recent)) * 100
            
            if recent_win_rate < 30:  # Menos del 30%
                return True, f"🛑 Win rate crítico ({recent_win_rate:.0f}%) - PAUSANDO para re-entrenar"
        
        return False, ""
