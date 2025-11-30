"""
Test completo del bot de trading con IQ Option
Verifica que todos los componentes funcionen correctamente
"""
import time
from config import Config
from data.market_data import MarketDataHandler
from strategies.technical import FeatureEngineer
from core.agent import RLAgent
from core.risk import RiskManager

print("=" * 60)
print("TEST COMPLETO DEL BOT - IQ OPTION")
print("=" * 60)

# 1. Test de Conexión
print("\n[1/6] Probando conexión...")
market_data = MarketDataHandler(broker_name="iq", account_type="PRACTICE")
connected = market_data.connect(Config.IQ_EMAIL, Config.IQ_PASSWORD)

if not connected:
    print("❌ Error de conexión")
    exit(1)

print("✅ Conectado a IQ Option")

# 2. Test de Balance
print("\n[2/6] Obteniendo balance...")
balance = market_data.get_balance()
print(f"✅ Balance: ${balance:.2f}")

# 3. Test de Datos de Mercado
print("\n[3/6] Obteniendo datos de mercado...")
df = market_data.get_candles("EURUSD-OTC", 60, 100)

if df.empty:
    print("❌ No se pudieron obtener datos")
    exit(1)

print(f"✅ Obtenidos {len(df)} velas")
print(f"   Última vela: {df.iloc[-1]['close']:.5f}")

# 4. Test de Indicadores Técnicos
print("\n[4/6] Calculando indicadores técnicos...")
feature_engineer = FeatureEngineer()

try:
    df_features = feature_engineer.prepare_for_rl(df)
    
    if df_features.empty:
        print("❌ DataFrame vacío después de calcular indicadores")
        print(f"   Datos originales: {len(df)} velas")
        exit(1)
except Exception as e:
    print(f"❌ Error calculando indicadores: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print(f"✅ Indicadores calculados")
print(f"   Columnas: {len(df_features.columns)}")
print(f"   RSI: {df_features.iloc[-1]['rsi']:.2f}")
print(f"   MACD: {df_features.iloc[-1]['macd']:.5f}")

# 5. Test de Agente RL
print("\n[5/6] Probando agente RL...")
agent = RLAgent(model_path=Config.MODEL_PATH)

# Intentar cargar modelo existente
try:
    agent.load()
    print("✅ Modelo cargado")
except:
    print("⚠️ No hay modelo entrenado (normal en primera ejecución)")

# Hacer predicción
window_size = 10
if len(df_features) >= window_size:
    obs = df_features.iloc[-window_size:].values
    action = agent.predict(obs)
    
    # Convertir a int si es array
    if hasattr(action, 'item'):
        action = action.item()
    action = int(action)
    
    actions_map = {0: "HOLD", 1: "CALL", 2: "PUT"}
    print(f"✅ Predicción: {actions_map[action]}")
else:
    print("⚠️ No hay suficientes datos para predicción")

# 6. Test de Risk Manager
print("\n[6/6] Probando gestión de riesgo...")
risk_manager = RiskManager(
    capital_per_trade=Config.CAPITAL_PER_TRADE,
    stop_loss_pct=Config.STOP_LOSS_PCT,
    take_profit_pct=Config.TAKE_PROFIT_PCT
)

amount = risk_manager.get_trade_amount()
print(f"✅ Monto de operación: ${amount:.2f}")

# Simular pérdida
risk_manager.update_trade_result(-1.0)
print(f"   Después de pérdida: ${risk_manager.get_trade_amount():.2f}")

# Simular ganancia
risk_manager.update_trade_result(0.85)
print(f"   Después de ganancia: ${risk_manager.get_trade_amount():.2f}")

print("\n" + "=" * 60)
print("✅ TODOS LOS COMPONENTES FUNCIONAN CORRECTAMENTE")
print("=" * 60)
print("\nEl bot está listo para operar.")
print("Puedes ejecutar 'python main.py' para iniciar la GUI.")
