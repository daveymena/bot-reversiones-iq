try:
    from stable_baselines3 import PPO
    from stable_baselines3.common.vec_env import DummyVecEnv
    STABLE_BASELINES_AVAILABLE = True
except ImportError:
    print("⚠️ stable-baselines3 no disponible. RL Agent deshabilitado.")
    PPO = None
    DummyVecEnv = None
    STABLE_BASELINES_AVAILABLE = False
    
import numpy as np
import os

class RLAgent:
    def __init__(self, env=None, model_path="models/rl_agent"):
        self.model_path = model_path
        self.env = env
        self.model = None
        self.enabled = STABLE_BASELINES_AVAILABLE

    def create_model(self):
        """Crea un nuevo modelo PPO."""
        if not self.enabled:
            print("⚠️ RL Agent deshabilitado (stable-baselines3 no disponible)")
            return
            
        if self.env is None:
            raise ValueError("Entorno no definido para crear modelo.")
        
        # Usamos PPO por ser robusto y eficiente
        self.model = PPO("MlpPolicy", self.env, verbose=1)

    def train(self, timesteps=10000):
        """Entrena el modelo."""
        if not self.enabled:
            print("⚠️ RL Agent deshabilitado (stable-baselines3 no disponible)")
            return
            
        if self.model is None:
            self.create_model()
        
        print(f"Iniciando entrenamiento por {timesteps} pasos...")
        self.model.learn(total_timesteps=timesteps)
        print("Entrenamiento completado.")
        self.save()

    def predict(self, observation, df_context=None):
        """
        Predice la acción para una observación dada.
        Si se proporciona df_context, usa StrategyOptimizer para mejorar la asertividad.
        """
        if not self.enabled:
            # Si RL no está disponible, usar solo estrategia de confluencia
            if df_context is not None:
                try:
                    from strategies.optimizer import StrategyOptimizer
                    return StrategyOptimizer.get_confluence_signal(df_context)
                except Exception as e:
                    print(f"⚠️ Error en optimizador: {e}")
            return 0  # HOLD por defecto
            
        if self.model is None:
            self.load()
        
        # 1. Predicción del Modelo RL
        action, _states = self.model.predict(observation)
        
        # 2. Validación con Estrategia de Confluencia (Si hay contexto)
        if df_context is not None:
            try:
                from strategies.optimizer import StrategyOptimizer
                confluence_signal = StrategyOptimizer.get_confluence_signal(df_context)
                
                # Lógica de Fusión:
                # Si el RL dice HOLD (0), pero la Confluencia dice CALL/PUT fuerte, tomamos Confluencia.
                # Si el RL dice CALL/PUT, pero la Confluencia contradice, hacemos HOLD (filtro de seguridad).
                
                rl_action = int(action) if hasattr(action, 'item') else int(action)
                
                if rl_action == 0 and confluence_signal != 0:
                    print(f"   ✨ Señal de Oportunidad detectada por Estrategia: {confluence_signal}")
                    return confluence_signal
                    
                if rl_action != 0 and confluence_signal != 0 and rl_action != confluence_signal:
                    print(f"   ⚠️ Conflicto de señales (RL: {rl_action}, Estrategia: {confluence_signal}) -> HOLD")
                    return 0
                    
            except Exception as e:
                print(f"   ⚠️ Error en optimizador: {e}")
                
        return action

    def save(self):
        """Guarda el modelo en disco."""
        if not self.enabled or not self.model:
            return
            
        self.model.save(self.model_path)
        print(f"Modelo guardado en {self.model_path}")

    def load(self):
        """Carga el modelo desde disco."""
        if not self.enabled:
            return
            
        if os.path.exists(self.model_path + ".zip"):
            self.model = PPO.load(self.model_path)
            print(f"Modelo cargado desde {self.model_path}")
        else:
            print("No se encontró modelo guardado. Se requiere entrenamiento previo.")
