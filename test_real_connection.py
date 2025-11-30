"""
Test de Conexión a Cuenta REAL de IQ Option
⚠️ ADVERTENCIA: ESTO CONECTARÁ A TU CUENTA REAL
"""
import sys
import os
from dotenv import load_dotenv
import time

# Cargar variables de entorno
load_dotenv()

print("=" * 70)
print("💰 TEST DE CONEXIÓN A CUENTA REAL - IQ OPTION")
print("=" * 70)
print("⚠️  ADVERTENCIA DE SEGURIDAD")
print("   Estás a punto de conectar a tu cuenta REAL.")
print("   Asegúrate de que esto es lo que deseas.")
print("=" * 70)

# 1. Verificar credenciales
email = os.getenv('IQ_OPTION_EMAIL')
password = os.getenv('IQ_OPTION_PASSWORD')

if not email or not password:
    print("❌ Credenciales no encontradas en .env")
    sys.exit(1)

# 2. Importar librería
print("\n1️⃣ Importando librería...")
try:
    from iqoptionapi.stable_api import IQ_Option
    print("   ✅ Librería importada")
except ImportError:
    print("   ❌ Error importando iqoptionapi")
    sys.exit(1)

# 3. Conectar
print("\n2️⃣ Conectando a IQ Option (REAL)...")
api = IQ_Option(email, password)

try:
    # Intentar conectar con timeout
    check, reason = api.connect()
    
    if check:
        print("   ✅ CONEXIÓN EXITOSA")
        
        # 4. Cambiar a REAL
        print("\n3️⃣ Cambiando a balance REAL...")
        api.change_balance("REAL")
        time.sleep(2)
        
        # 5. Obtener balance
        balance = api.get_balance()
        print(f"   💰 BALANCE REAL: ${balance:.2f}")
        
        print("\n✅ PRUEBA COMPLETADA EXITOSAMENTE")
        
    else:
        print(f"   ❌ ERROR DE CONEXIÓN: {reason}")
        if reason == "2FA":
            print("   ⚠️ La cuenta tiene autenticación de dos factores (2FA).")
            print("   Esta librería no soporta 2FA automáticamente.")
            
except Exception as e:
    print(f"   ❌ Error durante la conexión: {e}")

print("\n" + "=" * 70)
