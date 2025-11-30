import pandas as pd
try:
    from stable_baselines3 import PPO
    from stable_baselines3.common.vec_env import DummyVecEnv
    STABLE_BASELINES_AVAILABLE = True
except ImportError:
    print("⚠️ stable-baselines3 no disponible. AutoTrainer deshabilitado.")
    PPO = None
    DummyVecEnv = None
    STABLE_BASELINES_AVAILABLE = False

try:
    from env.trading_env import BinaryOptionsEnv
except ImportError:
    BinaryOptionsEnv = None
    
from strategies.technical import FeatureEngineer
from config import Config
import os

class AutoTrainer:
    def __init__(self, market_data, feature_engineer):
        self.market_data = market_data
        self.feature_engineer = feature_engineer
        self.model_path = Config.MODEL_PATH

    def train_on_recent_data(self, asset, num_candles=1000):
        """Descarga datos recientes y re-entrena el modelo."""
        print(f"🔄 Iniciando Auto-Entrenamiento para {asset}...")
        
        # 1. Obtener datos recientes
        df = self.market_data.get_candles(asset, Config.TIMEFRAME, num_candles)
        if df.empty:
            print("❌ No se pudieron obtener datos para entrenamiento.")
            return False

        # 2. Procesar
        df = self.feature_engineer.prepare_for_rl(df)
        if len(df) < 100:
            print("❌ Datos insuficientes después del procesamiento.")
            return False

        # 3. Crear entorno temporal
        env = DummyVecEnv([lambda: BinaryOptionsEnv(df)])

        # 4. Cargar o Crear Modelo
        try:
            if os.path.exists(self.model_path + ".zip"):
                model = PPO.load(self.model_path, env=env)
                print("Modelo existente cargado. Refinando...")
            else:
                model = PPO("MlpPolicy", env, verbose=0)
                print("Creando nuevo modelo...")
            
            # 5. Entrenar (pocos pasos para adaptación rápida)
            model.learn(total_timesteps=2000)
            
            # 6. Guardar
            model.save(self.model_path)
            print("✅ Auto-Entrenamiento completado y modelo guardado.")
            return True

        except Exception as e:
            print(f"❌ Error durante el entrenamiento: {e}")
            return False
