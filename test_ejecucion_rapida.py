"""
Test RÁPIDO de ejecución - Solo verifica que se pueda ejecutar operación
NO espera resultado, solo confirma que la orden se ejecuta
"""
import time
from config import Config

print("=" * 60)
print("TEST RÁPIDO DE EJECUCIÓN")
print("=" * 60)

# TEST IQ OPTION
print("\n[IQ OPTION - DEMO]")
print("-" * 60)
try:
    from iqoptionapi.stable_api import IQ_Option
    
    api_iq = IQ_Option(Config.IQ_EMAIL, Config.IQ_PASSWORD)
    check, _ = api_iq.connect()
    
    if check:
        api_iq.change_balance("PRACTICE")
        time.sleep(1)
        balance = api_iq.get_balance()
        print(f"✅ Conectado - Balance: ${balance:.2f}")
        
        # Ejecutar operación de $1
        status, order_id = api_iq.buy(1, "EURUSD-OTC", "call", 1)
        
        if status:
            print(f"✅ OPERACIÓN EJECUTADA - ID: {order_id}")
            print("   (No esperamos resultado para ir rápido)")
        else:
            print(f"❌ Fallo: {order_id}")
    else:
        print("❌ No se pudo conectar")
        
except Exception as e:
    print(f"❌ Error: {e}")

# TEST EXNOVA
print("\n[EXNOVA - PRACTICE]")
print("-" * 60)
try:
    from exnovaapi.stable_api import Exnova
    
    api_ex = Exnova(Config.EX_EMAIL, Config.EX_PASSWORD)
    status, _ = api_ex.connect()
    
    if status and api_ex.check_connect():
        api_ex.update_ACTIVES_OPCODE()
        balance = api_ex.get_balance()
        mode = api_ex.get_balance_mode()
        print(f"✅ Conectado - Balance: ${balance:.2f} ({mode})")
        
        # Ejecutar operación de $1
        buy_status, order_id = api_ex.buy(1, "EURUSD-OTC", "call", 1)
        
        if buy_status:
            print(f"✅ OPERACIÓN EJECUTADA - ID: {order_id}")
            print("   (No esperamos resultado para ir rápido)")
        else:
            print(f"❌ Fallo: {order_id}")
    else:
        print("❌ No se pudo conectar")
        
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 60)
print("RESUMEN")
print("=" * 60)
print("✅ Si ambos muestran 'OPERACIÓN EJECUTADA', todo funciona")
print("✅ Ahora puedes usar la interfaz gráfica con confianza")
print("=" * 60)
