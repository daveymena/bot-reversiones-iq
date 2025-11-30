"""
Test DIRECTO de operación en OTC - IQ Option
Ejecuta UNA operación real de $1 en EURUSD-OTC
"""
import time
from iqoptionapi.stable_api import IQ_Option

print("=" * 60)
print("TEST DE OPERACIÓN REAL - IQ OPTION OTC")
print("=" * 60)

# Credenciales
email = "deinermena25@gmail.com"
password = "6715320daveymena15.D"

print(f"\n[1] Conectando a IQ Option...")
api = IQ_Option(email, password)
check, msg = api.connect()

if not check:
    print(f"❌ Error de conexión: {msg}")
    exit(1)

print("✅ Conectado")

# Cambiar a PRACTICE
api.change_balance("PRACTICE")
time.sleep(2)

# Info de cuenta
balance_inicial = api.get_balance()
print(f"\n[2] Balance: ${balance_inicial:.2f} (PRACTICE)")

# Configurar operación OTC
activo = "EURUSD-OTC"  # OTC específicamente
monto = 1
direccion = "call"
duracion = 1  # 1 minuto

print(f"\n[3] Ejecutando operación:")
print(f"    Activo: {activo}")
print(f"    Monto: ${monto}")
print(f"    Dirección: {direccion.upper()}")
print(f"    Duración: {duracion} min")

try:
    status, order_id = api.buy(monto, activo, direccion, duracion)
    
    if status:
        print(f"\n✅ ¡OPERACIÓN EJECUTADA!")
        print(f"    Order ID: {order_id}")
        print(f"\n[4] Esperando resultado ({duracion} min + 10 seg)...")
        
        # Esperar
        time.sleep((duracion * 60) + 10)
        
        # Verificar resultado
        print("\n[5] Verificando resultado...")
        profit = api.check_win_v3(order_id)
        
        balance_final = api.get_balance()
        diferencia = balance_final - balance_inicial
        
        print("\n" + "=" * 60)
        print("RESULTADO FINAL")
        print("=" * 60)
        print(f"Profit/Loss: ${profit:.2f}")
        print(f"Balance inicial: ${balance_inicial:.2f}")
        print(f"Balance final: ${balance_final:.2f}")
        print(f"Diferencia real: ${diferencia:.2f}")
        
        if profit > 0:
            print("\n🎉 ¡GANASTE!")
        elif profit < 0:
            print("\n😞 Perdiste")
        else:
            print("\n⏸️ Empate")
        
        print("=" * 60)
        print("✅ IQ OPTION PUEDE EJECUTAR OPERACIONES CORRECTAMENTE")
        print("=" * 60)
    else:
        print(f"\n❌ Fallo al ejecutar: {order_id}")
        
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
