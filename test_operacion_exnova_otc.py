"""
Test DIRECTO de operación en OTC - Exnova
Ejecuta UNA operación real de $1 en EURUSD-OTC
"""
import time
from exnovaapi.stable_api import Exnova

print("=" * 60)
print("TEST DE OPERACIÓN REAL - EXNOVA OTC")
print("=" * 60)

# Credenciales
email = "daveymena16@gmail.com"
password = "6715320Dvd."

print(f"\n[1] Conectando a Exnova...")
api = Exnova(email, password)
status, msg = api.connect()

if not status or not api.check_connect():
    print(f"❌ Error de conexión: {msg}")
    exit(1)

print("✅ Conectado")

# Actualizar códigos
api.update_ACTIVES_OPCODE()

# Info de cuenta
balance_inicial = api.get_balance()
mode = api.get_balance_mode()
print(f"\n[2] Balance: ${balance_inicial:.2f} ({mode})")

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
    buy_status, order_id = api.buy(monto, activo, direccion, duracion)
    
    if buy_status:
        print(f"\n✅ ¡OPERACIÓN EJECUTADA!")
        print(f"    Order ID: {order_id}")
        print(f"\n[4] Esperando resultado ({duracion} min + 10 seg)...")
        
        # Esperar
        time.sleep((duracion * 60) + 10)
        
        # Verificar resultado
        print("\n[5] Verificando resultado...")
        result_status, profit = api.check_win_v4(order_id)
        
        balance_final = api.get_balance()
        diferencia = balance_final - balance_inicial
        
        print("\n" + "=" * 60)
        print("RESULTADO FINAL")
        print("=" * 60)
        print(f"Estado: {result_status}")
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
        print("✅ EXNOVA PUEDE EJECUTAR OPERACIONES CORRECTAMENTE")
        print("=" * 60)
    else:
        print(f"\n❌ Fallo al ejecutar: {order_id}")
        
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
