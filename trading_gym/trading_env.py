"""
Trading Environment para Reinforcement Learning
Entorno de Gymnasium para entrenar el agente PPO
"""
import gymnasium as gym
from gymnasium import spaces
import numpy as np

class BinaryOptionsEnv(gym.Env):
    """
    Entorno de trading para opciones binarias
    Compatible con Gymnasium y Stable-Baselines3
    """
    
    def __init__(self, data, feature_engineer):
        super(BinaryOptionsEnv, self).__init__()
        
        self.data = data
        self.feature_engineer = feature_engineer
        self.current_step = 0
        self.max_steps = len(data) - 1
        
        # Espacio de acciones: 0=No operar, 1=CALL, 2=PUT
        self.action_space = spaces.Discrete(3)
        
        # Espacio de observaciones: features técnicos
        # Ajustar según el número de features que genere feature_engineer
        self.observation_space = spaces.Box(
            low=-np.inf, 
            high=np.inf, 
            shape=(20,),  # Ajustar según features
            dtype=np.float32
        )
        
        # Estado del trading
        self.balance = 1000.0
        self.initial_balance = 1000.0
        self.trades = []
        
    def reset(self, seed=None, options=None):
        """Reiniciar el entorno"""
        super().reset(seed=seed)
        
        self.current_step = 0
        self.balance = self.initial_balance
        self.trades = []
        
        obs = self._get_observation()
        info = {}
        
        return obs, info
    
    def step(self, action):
        """Ejecutar una acción"""
        # Obtener observación actual
        obs = self._get_observation()
        
        # Calcular reward
        reward = 0.0
        done = False
        truncated = False
        
        # Ejecutar acción
        if action == 1:  # CALL
            # Simular resultado de operación CALL
            result = self._simulate_trade('call')
            reward = result
            self.balance += result
            
        elif action == 2:  # PUT
            # Simular resultado de operación PUT
            result = self._simulate_trade('put')
            reward = result
            self.balance += result
        
        # Avanzar paso
        self.current_step += 1
        
        # Verificar si terminó el episodio
        if self.current_step >= self.max_steps:
            done = True
        
        # Verificar si se quedó sin balance
        if self.balance <= 0:
            done = True
            reward = -100  # Penalización por perder todo
        
        info = {
            'balance': self.balance,
            'trades': len(self.trades)
        }
        
        return obs, reward, done, truncated, info
    
    def _get_observation(self):
        """Obtener observación del estado actual"""
        if self.current_step >= len(self.data):
            # Retornar observación vacía si no hay más datos
            return np.zeros(self.observation_space.shape, dtype=np.float32)
        
        # Obtener datos actuales
        current_data = self.data.iloc[max(0, self.current_step-100):self.current_step+1]
        
        # Generar features
        try:
            features = self.feature_engineer.engineer_features(current_data)
            
            # Convertir a array numpy
            if isinstance(features, dict):
                # Tomar los últimos valores de cada feature
                feature_values = []
                for key in sorted(features.keys()):
                    if isinstance(features[key], (list, np.ndarray)):
                        feature_values.append(features[key][-1] if len(features[key]) > 0 else 0.0)
                    else:
                        feature_values.append(float(features[key]))
                
                obs = np.array(feature_values, dtype=np.float32)
            else:
                obs = np.array(features, dtype=np.float32)
            
            # Asegurar que tenga el tamaño correcto
            if len(obs) < self.observation_space.shape[0]:
                obs = np.pad(obs, (0, self.observation_space.shape[0] - len(obs)))
            elif len(obs) > self.observation_space.shape[0]:
                obs = obs[:self.observation_space.shape[0]]
            
            return obs
            
        except Exception as e:
            print(f"Error generando features: {e}")
            return np.zeros(self.observation_space.shape, dtype=np.float32)
    
    def _simulate_trade(self, direction):
        """Simular resultado de una operación"""
        # Obtener precio actual y siguiente
        if self.current_step + 1 >= len(self.data):
            return 0.0
        
        current_price = self.data.iloc[self.current_step]['close']
        next_price = self.data.iloc[self.current_step + 1]['close']
        
        # Determinar si ganó o perdió
        if direction == 'call':
            won = next_price > current_price
        else:  # put
            won = next_price < current_price
        
        # Calcular reward
        trade_amount = 10.0  # Monto fijo por operación
        
        if won:
            profit = trade_amount * 0.85  # 85% de ganancia
            self.trades.append({'result': 'win', 'profit': profit})
            return profit
        else:
            loss = -trade_amount
            self.trades.append({'result': 'loss', 'profit': loss})
            return loss
    
    def render(self, mode='human'):
        """Renderizar el entorno (opcional)"""
        pass
    
    def close(self):
        """Cerrar el entorno"""
        pass
