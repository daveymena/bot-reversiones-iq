"""
Diagnóstico Avanzado de IQ Option
Identifica problemas específicos de conexión con timeout y manejo de errores
"""
import sys
import os
from dotenv import load_dotenv
import signal
from threading import Thread
import time

# Cargar variables de entorno
load_dotenv()

print("=" * 70)
print("🔍 DIAGNÓSTICO AVANZADO DE IQ OPTION")
print("=" * 70)

# 1. Verificar credenciales
print("\n1️⃣ Verificando credenciales...")
email = os.getenv('IQ_OPTION_EMAIL')
password = os.getenv('IQ_OPTION_PASSWORD')

if email and password:
    print(f"   ✅ Email: {email[:4]}***")
    print(f"   ✅ Password configurado: {len(password)} caracteres")
else:
    print("   ❌ Credenciales no encontradas en .env")
    print("\n   💡 Solución:")
    print("   1. Copia .env.example a .env")
    print("   2. Edita .env con tus credenciales reales de IQ Option")
    sys.exit(1)

# 2. Verificar instalación de la librería
print("\n2️⃣ Verificando instalación de iqoptionapi...")
try:
    import iqoptionapi
    print(f"   ✅ iqoptionapi instalado")
    try:
        version = iqoptionapi.__version__
        print(f"   📦 Versión: {version}")
    except:
        print("   ⚠️ No se pudo determinar la versión")
except ImportError as e:
    print(f"   ❌ Error: {e}")
    print("\n   💡 Solución:")
    print("   pip install iqoptionapi")
    sys.exit(1)

# 3. Importar API
print("\n3️⃣ Importando IQ_Option API...")
try:
    from iqoptionapi.stable_api import IQ_Option
    print("   ✅ Importación exitosa")
except ImportError as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# 4. Crear instancia
print("\n4️⃣ Creando instancia de IQ_Option...")
try:
    api = IQ_Option(email, password)
    print("   ✅ Instancia creada")
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# 5. Intentar conexión con timeout
print("\n5️⃣ Intentando conexión con timeout de 30 segundos...")
print("   ⏳ Conectando...")

connection_result = {"success": False, "reason": None, "error": None}

def try_connect():
    try:
        check, reason = api.connect()
        connection_result["success"] = check
        connection_result["reason"] = reason
    except Exception as e:
        connection_result["error"] = str(e)

# Ejecutar conexión en thread separado
connect_thread = Thread(target=try_connect)
connect_thread.daemon = True
connect_thread.start()

# Esperar con timeout
connect_thread.join(timeout=30)

if connect_thread.is_alive():
    print("   ❌ TIMEOUT: La conexión tardó más de 30 segundos")
    print("\n   🔍 DIAGNÓSTICO:")
    print("   - IQ Option puede estar bloqueando la conexión")
    print("   - Posibles causas:")
    print("     1. Credenciales incorrectas")
    print("     2. Cuenta suspendida o bloqueada")
    print("     3. IQ Option detectó uso de API (no permitido en algunos países)")
    print("     4. Problemas de red o firewall")
    print("     5. Servidor de IQ Option caído")
    print("\n   💡 SOLUCIONES:")
    print("   1. Verifica tus credenciales en https://iqoption.com")
    print("   2. Intenta iniciar sesión manualmente en el navegador")
    print("   3. Verifica que tu cuenta no esté bloqueada")
    print("   4. Considera usar EXNOVA en su lugar (más estable)")
    print("\n   ⚙️ Para cambiar a EXNOVA:")
    print("   - Edita .env y cambia: BROKER_NAME=exnova")
    print("   - Configura EXNOVA_EMAIL y EXNOVA_PASSWORD")
    sys.exit(1)

# Verificar resultado
if connection_result["error"]:
    print(f"   ❌ Error durante conexión: {connection_result['error']}")
    sys.exit(1)

if connection_result["success"]:
    print("   ✅ ¡CONEXIÓN EXITOSA!")
    
    # 6. Probar funcionalidades básicas
    print("\n6️⃣ Probando funcionalidades básicas...")
    
    try:
        print("   📊 Cambiando a cuenta PRACTICE...")
        api.change_balance("PRACTICE")
        time.sleep(2)
        
        balance = api.get_balance()
        print(f"   💰 Balance PRACTICE: ${balance:.2f}")
        
        print("\n" + "=" * 70)
        print("✅ IQ OPTION FUNCIONA CORRECTAMENTE")
        print("=" * 70)
        print("\n💡 Puedes usar IQ Option en el bot")
        print("   Configura en .env: BROKER_NAME=iq")
        
    except Exception as e:
        print(f"   ⚠️ Conexión exitosa pero error obteniendo datos: {e}")
        print("   La API puede estar limitada o la cuenta tener restricciones")
        
else:
    print(f"   ❌ Conexión fallida: {connection_result['reason']}")
    print("\n   🔍 DIAGNÓSTICO:")
    print("   Razones comunes:")
    print("   - 'Invalid credentials': Email o password incorrectos")
    print("   - 'Account blocked': Cuenta suspendida")
    print("   - 'Too many attempts': Demasiados intentos de login")
    print("\n   💡 SOLUCIÓN:")
    print("   1. Verifica tus credenciales")
    print("   2. Intenta resetear tu password en IQ Option")
    print("   3. Contacta soporte de IQ Option")
    print("   4. Usa EXNOVA como alternativa (más confiable)")

print("\n" + "=" * 70)
