"""
Script de prueba para verificar que el bot no se cierra después del re-entrenamiento
"""
import time
from core.continuous_learner import ContinuousLearner
from core.agent import RLAgent
from strategies.technical import FeatureEngineer
from data.market_data import MarketDataHandler
from config import Config

def test_reentrenamiento():
    print("="*60)
    print("TEST: Re-entrenamiento sin cierre del bot")
    print("="*60)
    
    # Inicializar componentes
    print("\n1. Inicializando componentes...")
    market_data = MarketDataHandler(
        broker_name=Config.BROKER_NAME,
        account_type="PRACTICE"  # Usar práctica para pruebas
    )
    feature_engineer = FeatureEngineer()
    agent = RLAgent(model_path=Config.MODEL_PATH)
    
    # Cargar modelo si existe
    try:
        agent.load()
        print("   ✅ Modelo cargado")
    except:
        print("   ⚠️ Modelo no encontrado (se creará)")
    
    # Crear learner
    learner = ContinuousLearner(agent, feature_engineer, market_data)
    print("   ✅ Learner creado")
    
    # Conectar al broker
    print("\n2. Conectando al broker...")
    if Config.BROKER_NAME == "exnova":
        success = market_data.connect(Config.EX_EMAIL, Config.EX_PASSWORD)
    else:
        success = market_data.connect(Config.IQ_EMAIL, Config.IQ_PASSWORD)
    
    if not success:
        print("   ❌ Error conectando al broker")
        return False
    
    print("   ✅ Conectado al broker")
    
    # Simular re-entrenamiento
    print("\n3. Simulando re-entrenamiento...")
    print("   (Esto debería completarse sin cerrar el script)")
    
    success = learner.retrain_with_fresh_data(
        asset="EURUSD-OTC",
        num_candles=500  # Menos velas para prueba rápida
    )
    
    if success:
        print("\n   ✅ Re-entrenamiento completado exitosamente")
    else:
        print("\n   ❌ Error en re-entrenamiento")
        return False
    
    # Verificar que el script sigue ejecutándose
    print("\n4. Verificando que el script sigue activo...")
    for i in range(5):
        print(f"   Tick {i+1}/5 - Script activo ✓")
        time.sleep(1)
    
    print("\n" + "="*60)
    print("✅ TEST EXITOSO: El bot continúa después del re-entrenamiento")
    print("="*60)
    
    return True

if __name__ == "__main__":
    try:
        result = test_reentrenamiento()
        if result:
            print("\n✅ Prueba completada exitosamente")
        else:
            print("\n❌ Prueba fallida")
    except Exception as e:
        print(f"\n❌ Error en prueba: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\nPresiona Enter para salir...")
        input()
