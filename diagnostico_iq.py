"""
Diagnóstico IQ Option - Identificar dónde se bloquea
"""
import time
import sys

print("=" * 60)
print("DIAGNÓSTICO IQ OPTION")
print("=" * 60)

# Credenciales
email = "deinermena25@gmail.com"
password = "6715320daveymena15.D"

print(f"\nEmail: {email}")

# Test 1: Importar librería
print("\n[1/5] Importando librería...")
try:
    from iqoptionapi.stable_api import IQ_Option
    print("✅ Librería importada")
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

# Test 2: Crear instancia
print("\n[2/5] Creando instancia...")
try:
    api = IQ_Option(email, password)
    print("✅ Instancia creada")
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

# Test 3: Conectar (con timeout manual)
print("\n[3/5] Conectando (máximo 30 segundos)...")
import threading

resultado = {'check': None, 'reason': None, 'error': None}

def conectar():
    try:
        check, reason = api.connect()
        resultado['check'] = check
        resultado['reason'] = reason
    except Exception as e:
        resultado['error'] = str(e)

thread = threading.Thread(target=conectar)
thread.daemon = True
thread.start()
thread.join(timeout=30)

if thread.is_alive():
    print("❌ TIMEOUT: La conexión se bloqueó")
    print("\nPROBLEMA IDENTIFICADO:")
    print("  - api.connect() se bloquea indefinidamente")
    print("  - Esto puede ser:")
    print("    1. Problema de red/firewall")
    print("    2. API de IQ Option caída")
    print("    3. Cuenta bloqueada")
    sys.exit(1)

if resultado['error']:
    print(f"❌ Error: {resultado['error']}")
    sys.exit(1)

if not resultado['check']:
    print(f"❌ Conexión fallida: {resultado['reason']}")
    sys.exit(1)

print(f"✅ Conectado: {resultado['reason']}")

# Test 4: Cambiar balance
print("\n[4/5] Cambiando a PRACTICE...")
try:
    api.change_balance("PRACTICE")
    time.sleep(2)
    balance = api.get_balance()
    print(f"✅ Balance: ${balance:.2f}")
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

# Test 5: Ejecutar operación
print("\n[5/5] Ejecutando operación de prueba...")
try:
    status, order_id = api.buy(1, "EURUSD-OTC", "call", 1)
    
    if status:
        print(f"✅ OPERACIÓN EJECUTADA - ID: {order_id}")
        print("\n" + "=" * 60)
        print("✅ IQ OPTION FUNCIONA CORRECTAMENTE")
        print("=" * 60)
    else:
        print(f"❌ Fallo: {order_id}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
