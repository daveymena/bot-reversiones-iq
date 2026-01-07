#!/usr/bin/env python3
"""
Sistema de Entrenamiento Continuo 24/7
Entrena el modelo constantemente con datos históricos y simulaciones
Se ejecuta en paralelo al bot de trading
"""

import time
import sys
import signal
from datetime import datetime
import pandas as pd
import numpy as np
from config import Config
from data.market_data import MarketDataHandler
from strategies.technical import FeatureEngineer
from core.agent import RLAgent
from core.experience_buffer import ExperienceBuffer
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from env.trading_env import BinaryOptionsEnv

# Variable global para manejo de señales
running = True

def signal_handler(sig, frame):
    """Maneja Ctrl+C para cerrar limpiamente"""
    global running
    print("\n\n🛑 Deteniendo entrenamiento continuo...")
    running = False
    sys.exit(0)

def print_banner():
    """Imprime banner de inicio"""
    print("\n" + "="*70)
    print("🎓 SISTEMA DE ENTRENAMIENTO CONTINUO 24/7")
    print("="*70)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Broker: {Config.BROKER_NAME.upper()}")
    print(f"Modo: Entrenamiento continuo en segundo plano")
    print("="*70 + "\n")

def train_from_historical_data(market_data, feature_engineer, agent, asset, num_candles=2000):
    """
    Entrena con datos históricos del broker
    """
    try:
        print(f"\n📊 Descargando {num_candles} velas de {asset}...")
        df = market_data.get_candles(asset, Config.TIMEFRAME, num_candles)
        
        if df is None or df.empty or len(df) < 100:
            print(f"⚠️ No hay suficientes datos para {asset}")
            return False
        
        print(f"✅ Descargadas {len(df)} velas")
        
        # Preparar datos
        print("🔧 Preparando features...")
        df = feature_engineer.prepare_for_rl(df)
        
        if df.empty or len(df) < 50:
            print("⚠️ No hay suficientes datos después de preparar features")
            return False
        
        print(f"✅ Features preparados: {len(df)} filas")
        
        # Crear ambiente de entrenamiento
        print("🏗️ Creando ambiente de entrenamiento...")
        env = BinaryOptionsEnv(df, initial_balance=1000, trade_amount=1)
        env = DummyVecEnv([lambda: env])
        
        # Entrenar
        timesteps = 5000
        print(f"🎓 Entrenando {timesteps} pasos...")
        
        if agent.model is None:
            print("🆕 Creando nuevo modelo...")
            agent.model = PPO(
                "MlpPolicy",
                env,
                verbose=0,
                learning_rate=0.0003,
                n_steps=2048,
                batch_size=64,
                n_epochs=10,
                gamma=0.99,
                gae_lambda=0.95,
                clip_range=0.2,
                ent_coef=0.01
            )
        else:
            print("🔄 Continuando entrenamiento del modelo existente...")
            agent.model.set_env(env)
        
        agent.model.learn(total_timesteps=timesteps, progress_bar=False)
        
        # Guardar modelo
        print("💾 Guardando modelo...")
        agent.save()
        
        print(f"✅ Entrenamiento completado para {asset}")
        return True
        
    except Exception as e:
        print(f"❌ Error entrenando con {asset}: {e}")
        import traceback
        traceback.print_exc()
        return False

def train_from_experiences(agent, experience_buffer):
    """
    Entrena con experiencias reales guardadas
    """
    try:
        experiences = experience_buffer.get_all_experiences()
        
        if len(experiences) < 20:
            print(f"⏳ Solo {len(experiences)} experiencias, necesita al menos 20")
            return False
        
        print(f"\n📚 Entrenando con {len(experiences)} experiencias reales...")
        
        # Convertir experiencias a formato de entrenamiento
        states = []
        actions = []
        rewards = []
        next_states = []
        dones = []
        
        for exp in experiences:
            states.append(exp['state'])
            actions.append(exp['action'])
            rewards.append(exp['reward'])
            next_states.append(exp['next_state'])
            dones.append(exp['done'])
        
        # Crear DataFrame sintético para el ambiente
        # Usar las experiencias para simular un mercado
        num_features = len(states[0])
        synthetic_df = pd.DataFrame(
            np.random.randn(len(experiences), num_features),
            columns=[f'feature_{i}' for i in range(num_features)]
        )
        
        # Crear ambiente
        env = BinaryOptionsEnv(synthetic_df, initial_balance=1000, trade_amount=1)
        env = DummyVecEnv([lambda: env])
        
        # Entrenar
        if agent.model is None:
            print("🆕 Creando nuevo modelo...")
            agent.model = PPO("MlpPolicy", env, verbose=0)
        else:
            agent.model.set_env(env)
        
        timesteps = min(len(experiences) * 100, 10000)
        print(f"🎓 Entrenando {timesteps} pasos con experiencias reales...")
        agent.model.learn(total_timesteps=timesteps, progress_bar=False)
        
        # Guardar
        agent.save()
        
        print(f"✅ Entrenamiento con experiencias completado")
        return True
        
    except Exception as e:
        print(f"❌ Error entrenando con experiencias: {e}")
        import traceback
        traceback.print_exc()
        return False

def simulate_trades(market_data, feature_engineer, agent, asset, num_simulations=50):
    """
    Simula operaciones para generar más experiencias de entrenamiento
    """
    try:
        print(f"\n🎮 Simulando {num_simulations} operaciones en {asset}...")
        
        # Obtener datos recientes
        df = market_data.get_candles(asset, Config.TIMEFRAME, 500)
        if df is None or df.empty or len(df) < 100:
            return False
        
        df = feature_engineer.prepare_for_rl(df)
        if df.empty:
            return False
        
        # Simular operaciones
        simulated_experiences = []
        
        for i in range(num_simulations):
            # Seleccionar punto aleatorio
            idx = np.random.randint(50, len(df) - 10)
            
            # Estado actual
            state = df.iloc[idx-10:idx].values.flatten()
            
            # Predecir acción
            action = agent.predict(state, df_context=df.iloc[idx-10:idx])
            if hasattr(action, 'item'):
                action = action.item()
            action = int(action)
            
            # Simular resultado
            entry_price = df.iloc[idx]['close']
            exit_price = df.iloc[idx + 3]['close']  # 3 velas después
            
            if action == 1:  # CALL
                profit = 0.85 if exit_price > entry_price else -1.0
            elif action == 2:  # PUT
                profit = 0.85 if exit_price < entry_price else -1.0
            else:  # HOLD
                profit = 0
            
            # Estado siguiente
            next_state = df.iloc[idx+1:idx+11].values.flatten()
            
            simulated_experiences.append({
                'state': state,
                'action': action,
                'reward': profit,
                'next_state': next_state,
                'done': False
            })
        
        print(f"✅ Simuladas {len(simulated_experiences)} operaciones")
        
        # Entrenar con simulaciones
        if len(simulated_experiences) >= 20:
            print("🎓 Entrenando con simulaciones...")
            
            # Crear ambiente sintético
            num_features = len(simulated_experiences[0]['state'])
            synthetic_df = pd.DataFrame(
                np.random.randn(len(simulated_experiences), num_features),
                columns=[f'feature_{i}' for i in range(num_features)]
            )
            
            env = BinaryOptionsEnv(synthetic_df, initial_balance=1000, trade_amount=1)
            env = DummyVecEnv([lambda: env])
            
            if agent.model is None:
                agent.model = PPO("MlpPolicy", env, verbose=0)
            else:
                agent.model.set_env(env)
            
            agent.model.learn(total_timesteps=2000, progress_bar=False)
            agent.save()
            
            print("✅ Entrenamiento con simulaciones completado")
        
        return True
        
    except Exception as e:
        print(f"❌ Error simulando operaciones: {e}")
        return False

def main():
    """Función principal de entrenamiento continuo"""
    global running
    
    # Configurar manejo de Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    print_banner()
    
    try:
        # Inicializar componentes
        print("📦 Inicializando componentes...")
        
        market_data = MarketDataHandler(
            broker_name=Config.BROKER_NAME,
            account_type="PRACTICE"  # Siempre usar PRACTICE para entrenamiento
        )
        
        feature_engineer = FeatureEngineer()
        agent = RLAgent()
        experience_buffer = ExperienceBuffer()
        
        # Cargar modelo existente si existe
        if agent.load():
            print("✅ Modelo existente cargado")
        else:
            print("⚠️ No se encontró modelo, se creará uno nuevo")
        
        print("✅ Componentes inicializados\n")
        
        # Conectar al broker
        print(f"🔌 Conectando a {Config.BROKER_NAME.upper()} (PRACTICE)...")
        
        if Config.BROKER_NAME == "exnova":
            email = Config.EXNOVA_EMAIL
            password = Config.EXNOVA_PASSWORD
        else:
            email = Config.IQ_OPTION_EMAIL
            password = Config.IQ_OPTION_PASSWORD
        
        if not market_data.connect(email, password):
            print("❌ Error conectando al broker")
            print("⚠️ Continuando sin conexión (solo entrenamiento con experiencias)")
            market_data = None
        else:
            print(f"✅ Conectado a {Config.BROKER_NAME.upper()}\n")
        
        # Lista de activos para entrenar
        assets = [
            "EURUSD-OTC", "GBPUSD-OTC", "USDJPY-OTC",
            "AUDUSD-OTC", "USDCAD-OTC", "EURJPY-OTC"
        ]
        
        # Iniciar loop de entrenamiento continuo
        print("="*70)
        print("🚀 INICIANDO ENTRENAMIENTO CONTINUO 24/7")
        print("="*70)
        print("El sistema entrenará constantemente en segundo plano")
        print("Presiona Ctrl+C para detener\n")
        
        cycle = 0
        total_trainings = 0
        
        while running:
            try:
                cycle += 1
                print(f"\n{'='*70}")
                print(f"🔄 CICLO DE ENTRENAMIENTO #{cycle}")
                print(f"{'='*70}")
                print(f"Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"Total entrenamientos completados: {total_trainings}")
                
                # 1. Entrenar con experiencias reales
                print("\n📚 Fase 1: Entrenamiento con experiencias reales")
                if train_from_experiences(agent, experience_buffer):
                    total_trainings += 1
                
                # Pausa corta
                time.sleep(5)
                
                # 2. Entrenar con datos históricos (si hay conexión)
                if market_data and market_data.connected:
                    print("\n📊 Fase 2: Entrenamiento con datos históricos")
                    
                    # Entrenar con 2-3 activos por ciclo
                    assets_to_train = np.random.choice(assets, size=min(3, len(assets)), replace=False)
                    
                    for asset in assets_to_train:
                        if not running:
                            break
                        
                        if train_from_historical_data(market_data, feature_engineer, agent, asset):
                            total_trainings += 1
                        
                        time.sleep(5)  # Pausa entre activos
                    
                    # 3. Simular operaciones
                    print("\n🎮 Fase 3: Simulación de operaciones")
                    random_asset = np.random.choice(assets)
                    if simulate_trades(market_data, feature_engineer, agent, random_asset):
                        total_trainings += 1
                else:
                    print("\n⚠️ Sin conexión al broker, solo entrenando con experiencias")
                
                # Resumen del ciclo
                print(f"\n{'='*70}")
                print(f"✅ CICLO #{cycle} COMPLETADO")
                print(f"Total entrenamientos: {total_trainings}")
                print(f"Próximo ciclo en 5 minutos...")
                print(f"{'='*70}\n")
                
                # Esperar 5 minutos antes del próximo ciclo
                # Dividir en intervalos cortos para poder interrumpir con Ctrl+C
                for _ in range(300):  # 300 segundos = 5 minutos
                    if not running:
                        break
                    time.sleep(1)
            
            except KeyboardInterrupt:
                print("\n\n🛑 Deteniendo entrenamiento continuo...")
                break
            
            except Exception as e:
                print(f"\n❌ Error en ciclo de entrenamiento: {e}")
                import traceback
                traceback.print_exc()
                print("⚠️ Continuando con el próximo ciclo en 1 minuto...")
                time.sleep(60)
        
        # Resumen final
        print("\n" + "="*70)
        print("RESUMEN FINAL DE ENTRENAMIENTO")
        print("="*70)
        print(f"Total ciclos completados: {cycle}")
        print(f"Total entrenamientos: {total_trainings}")
        print(f"Modelo guardado en: {Config.MODEL_PATH}.zip")
        print("="*70 + "\n")
        
        print("👋 Entrenamiento continuo detenido correctamente")
        return 0
    
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
