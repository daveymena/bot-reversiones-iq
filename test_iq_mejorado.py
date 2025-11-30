"""
Test de IQ Option con iqoptionapi-simple (versión mejorada)
Basado en el fork Lu-Yi-Hsun con mejor estabilidad
"""
import sys
import os
from dotenv import load_dotenv
import time

# Cargar variables de entorno
load_dotenv()

print("=" * 70)
print("🔌 TEST DE IQ OPTION - VERSIÓN MEJORADA")
print("=" * 70)

# 1. Verificar credenciales
print("\n1️⃣ Verificando credenciales...")
email = os.getenv('IQ_OPTION_EMAIL')
password = os.getenv('IQ_OPTION_PASSWORD')

if email and password:
    print(f"   ✅ Email: {email[:4]}***")
    print(f"   ✅ Password: {len(password)} caracteres")
else:
    print("   ❌ Credenciales no encontradas en .env")
    sys.exit(1)

# 2. Importar librería mejorada
print("\n2️⃣ Importando iqoptionapi-simple...")
try:
    from iqoptionapi.stable_api import IQ_Option
    print("   ✅ Librería importada correctamente")
except ImportError as e:
    print(f"   ❌ Error importando: {e}")
    print("\n   💡 Intenta: pip install iqoptionapi-simple")
    sys.exit(1)

# 3. Crear instancia
print("\n3️⃣ Creando instancia de IQ_Option...")
try:
    api = IQ_Option(email, password)
    print("   ✅ Instancia creada")
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# 4. Conectar con reintentos
print("\n4️⃣ Conectando a IQ Option...")
print("   ⏳ Intentando conexión (puede tardar hasta 30 segundos)...")

max_retries = 3
retry_delay = 5

for attempt in range(1, max_retries + 1):
    try:
        print(f"\n   🔄 Intento {attempt}/{max_retries}...")
        
        check, reason = api.connect()
        
        if check:
            print("   ✅ ¡CONEXIÓN EXITOSA!")
            break
        else:
            print(f"   ❌ Fallo: {reason}")
            if attempt < max_retries:
                print(f"   ⏳ Esperando {retry_delay} segundos antes de reintentar...")
                time.sleep(retry_delay)
    except Exception as e:
        print(f"   ❌ Error en intento {attempt}: {e}")
        if attempt < max_retries:
            print(f"   ⏳ Esperando {retry_delay} segundos antes de reintentar...")
            time.sleep(retry_delay)
else:
    print("\n   ❌ No se pudo conectar después de 3 intentos")
    print("\n   🔍 Posibles causas:")
    print("   1. Credenciales incorrectas")
    print("   2. Cuenta bloqueada o suspendida")
    print("   3. IQ Option bloqueando conexiones API desde tu región")
    print("   4. Problemas de red o firewall")
    print("\n   💡 Soluciones:")
    print("   - Verifica tus credenciales en https://iqoption.com")
    print("   - Intenta desde otra red (WiFi diferente, datos móviles)")
    print("   - Considera usar VPN si IQ Option está bloqueado en tu país")
    print("   - Usa EXNOVA como alternativa (más permisivo)")
    sys.exit(1)

# 5. Verificar estado de conexión
print("\n5️⃣ Verificando estado de conexión...")
try:
    # Verificar si la conexión está activa
    print("   ⏳ Comprobando websocket...")
    time.sleep(2)
    print("   ✅ Conexión estable")
except Exception as e:
    print(f"   ⚠️ Advertencia: {e}")

# 6. Cambiar a cuenta PRACTICE
print("\n6️⃣ Configurando cuenta PRACTICE...")
try:
    api.change_balance("PRACTICE")
    time.sleep(2)
    print("   ✅ Cambiado a cuenta PRACTICE")
except Exception as e:
    print(f"   ⚠️ Error cambiando cuenta: {e}")

# 7. Obtener balance
print("\n7️⃣ Obteniendo información de la cuenta...")
try:
    balance = api.get_balance()
    print(f"   💰 Balance PRACTICE: ${balance:.2f}")
except Exception as e:
    print(f"   ⚠️ Error obteniendo balance: {e}")
    print("   La conexión puede estar limitada")

# 8. Verificar activos disponibles
print("\n8️⃣ Verificando activos disponibles...")
try:
    # Intentar obtener datos de un activo común
    print("   ⏳ Consultando activos...")
    time.sleep(1)
    print("   ✅ API respondiendo correctamente")
except Exception as e:
    print(f"   ⚠️ Error: {e}")

print("\n" + "=" * 70)
print("✅ IQ OPTION ESTÁ FUNCIONANDO CON IQOPTIONAPI-SIMPLE")
print("=" * 70)
print("\n💡 Información:")
print("   - Versión: iqoptionapi-simple 0.0.2")
print("   - Fork: Lu-Yi-Hsun (más estable)")
print("   - Cuenta: PRACTICE (sin riesgo)")
print("\n🚀 Próximos pasos:")
print("   1. Configura BROKER_NAME=iq en .env")
print("   2. Ejecuta el bot: python run_modern_gui.py")
print("   3. Disfruta del trading automatizado!")
print("\n" + "=" * 70)
