"""
Test para ver qué devuelve check_win_v3
"""
import time
from config import Config
from iqoptionapi.stable_api import IQ_Option

print("Conectando...")
api = IQ_Option(Config.IQ_EMAIL, Config.IQ_PASSWORD)
check, reason = api.connect()

if not check:
    print(f"Error: {reason}")
    exit(1)

print("✅ Conectado")
api.change_balance("PRACTICE")
time.sleep(1)

print("\nEjecutando operación...")
status, order_id = api.buy(1, "EURUSD-OTC", "call", 1)

if not status:
    print(f"Error: {order_id}")
    exit(1)

print(f"✅ Operación ejecutada - ID: {order_id}")
print(f"Tipo de order_id: {type(order_id)}")

print("\nEsperando 70 segundos...")
time.sleep(70)

print("\nProbando check_win_v3...")
try:
    result = api.check_win_v3(order_id)
    print(f"Resultado: {result}")
    print(f"Tipo: {type(result)}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
