"""
Script de Entrenamiento del Bot de Trading
Entrena el agente RL con datos históricos
"""
import argparse
import time
from config import Config
from data.market_data import MarketDataHandler
from strategies.technical import FeatureEngineer
from core.agent import RLAgent
from env.trading_env import BinaryOptionsEnv
from stable_baselines3.common.vec_env import DummyVecEnv

def train_bot(asset="EURUSD-OTC", num_candles=2000, timesteps=10000, broker="exnova"):
    """
    Entrena el bot con datos históricos
    
    Args:
        asset: Activo a usar para entrenamiento
        num_candles: Número de velas históricas
        timesteps: Pasos de entrenamiento
        broker: Broker a usar (exnova o iq)
    """
    print("=" * 70)
    print("🤖 ENTRENAMIENTO DEL BOT DE TRADING")
    print("=" * 70)
    
    # 1. Conectar al broker
    print(f"\n[1/6] Conectando a {broker.upper()}...")
    market_data = MarketDataHandler(broker_name=broker, account_type="PRACTICE")
    
    if broker == "exnova":
        email = Config.EX_EMAIL
        password = Config.EX_PASSWORD
    else:
        email = Config.IQ_EMAIL
        password = Config.IQ_PASSWORD
    
    if not market_data.connect(email, password):
        print("❌ Error: No se pudo conectar al broker")
        print("   Verifica tus credenciales en .env")
        return False
    
    print(f"✅ Conectado a {broker.upper()}")
    
    # 2. Obtener datos históricos
    print(f"\n[2/6] Obteniendo {num_candles} velas de {asset}...")
    df = market_data.get_candles(asset, Config.TIMEFRAME, num_candles, time.time())
    
    if df.empty:
        print("❌ Error: No se pudieron obtener datos")
        return False
    
    print(f"✅ Obtenidas {len(df)} velas")
    print(f"   Rango: {df.index[0]} a {df.index[-1]}")
    
    # 3. Procesar indicadores técnicos
    print("\n[3/6] Calculando indicadores técnicos...")
    feature_engineer = FeatureEngineer()
    
    try:
        df_processed = feature_engineer.prepare_for_rl(df)
        
        if df_processed.empty:
            print("❌ Error: DataFrame vacío después de procesar")
            print(f"   Necesitas al menos 50 velas para calcular indicadores")
            return False
        
        print(f"✅ Indicadores calculados")
        print(f"   Velas procesadas: {len(df_processed)}")
        print(f"   Features: {df_processed.shape[1]} columnas")
        print(f"   Columnas: {list(df_processed.columns)}")
        
    except Exception as e:
        print(f"❌ Error procesando indicadores: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 4. Crear entorno de trading
    print("\n[4/6] Creando entorno de simulación...")
    try:
        env = DummyVecEnv([lambda: BinaryOptionsEnv(
            df=df_processed,
            window_size=10,
            initial_balance=1000
        )])
        print("✅ Entorno creado")
        print(f"   Balance inicial: $1000")
        print(f"   Ventana de observación: 10 velas")
        print(f"   Acciones: HOLD, CALL, PUT")
    except Exception as e:
        print(f"❌ Error creando entorno: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 5. Crear/cargar agente
    print("\n[5/6] Configurando agente RL...")
    agent = RLAgent(env=env, model_path=Config.MODEL_PATH)
    
    try:
        agent.load()
        print("✅ Modelo existente cargado")
        print("   Se continuará el entrenamiento")
    except:
        print("⚠️  No hay modelo previo")
        print("   Se creará uno nuevo")
        agent.create_model()
    
    # 6. Entrenar
    print(f"\n[6/6] Entrenando por {timesteps} pasos...")
    print("   Esto puede tomar varios minutos...")
    print("   Presiona Ctrl+C para detener\n")
    
    try:
        start_time = time.time()
        agent.train(timesteps=timesteps)
        elapsed = time.time() - start_time
        
        print(f"\n✅ Entrenamiento completado en {elapsed:.1f} segundos")
        print(f"   Modelo guardado en: {Config.MODEL_PATH}")
        
        # Estadísticas finales
        print("\n" + "=" * 70)
        print("📊 RESUMEN DEL ENTRENAMIENTO")
        print("=" * 70)
        print(f"Activo:           {asset}")
        print(f"Velas usadas:     {len(df_processed)}")
        print(f"Timesteps:        {timesteps}")
        print(f"Tiempo:           {elapsed:.1f}s")
        print(f"Modelo guardado:  {Config.MODEL_PATH}.zip")
        print("=" * 70)
        
        print("\n✅ El bot está listo para operar")
        print("   Ejecuta: python main_modern.py")
        
        return True
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Entrenamiento interrumpido por el usuario")
        print("   Guardando progreso...")
        agent.save()
        print("✅ Progreso guardado")
        return False
    
    except Exception as e:
        print(f"\n❌ Error durante entrenamiento: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    parser = argparse.ArgumentParser(description="Entrenar el bot de trading")
    parser.add_argument("--asset", default="EURUSD-OTC", help="Activo a usar")
    parser.add_argument("--candles", type=int, default=2000, help="Número de velas")
    parser.add_argument("--timesteps", type=int, default=10000, help="Pasos de entrenamiento")
    parser.add_argument("--broker", default="exnova", choices=["exnova", "iq"], help="Broker")
    
    args = parser.parse_args()
    
    success = train_bot(
        asset=args.asset,
        num_candles=args.candles,
        timesteps=args.timesteps,
        broker=args.broker
    )
    
    if success:
        print("\n🎉 ¡Entrenamiento exitoso!")
    else:
        print("\n❌ Entrenamiento fallido")
        exit(1)

if __name__ == "__main__":
    main()
