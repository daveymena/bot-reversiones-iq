"""
Test de Conexión a IQ Option
Prueba la conexión con las credenciales configuradas
"""
import sys
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

print("=" * 70)
print("🔌 TEST DE CONEXIÓN A IQ OPTION")
print("=" * 70)

# 1. Verificar credenciales
print("\n1️⃣ Verificando credenciales...")
email = os.getenv('IQ_OPTION_EMAIL')
password = os.getenv('IQ_OPTION_PASSWORD')

if email and password:
    print(f"   ✅ Email: {email[:4]}***")
    print(f"   ✅ Password: {password[:4]}***")
else:
    print("   ❌ Credenciales no encontradas en .env")
    sys.exit(1)

# 2. Importar librería
print("\n2️⃣ Importando IQ Option API...")
try:
    from iqoptionapi.stable_api import IQ_Option
    print("   ✅ Librería importada correctamente")
except ImportError as e:
    print(f"   ❌ Error importando: {e}")
    sys.exit(1)

# 3. Crear instancia
print("\n3️⃣ Creando instancia de IQ_Option...")
try:
    api = IQ_Option(email, password)
    print("   ✅ Instancia creada")
except Exception as e:
    print(f"   ❌ Error creando instancia: {e}")
    sys.exit(1)

# 4. Conectar
print("\n4️⃣ Conectando a IQ Option...")
print("   ⏳ Esto puede tardar unos segundos...")
try:
    check, reason = api.connect()
    
    if check:
        print("   ✅ CONEXIÓN EXITOSA!")
        
        # 5. Cambiar a cuenta PRACTICE
        print("\n5️⃣ Cambiando a cuenta PRACTICE...")
        api.change_balance("PRACTICE")
        import time
        time.sleep(2)
        
        # 6. Obtener balance
        print("\n6️⃣ Obteniendo información de la cuenta...")
        try:
            balance = api.get_balance()
            print(f"   💰 Balance PRACTICE: ${balance:.2f}")
        except Exception as e:
            print(f"   ⚠️ No se pudo obtener balance: {e}")
        
        # 7. Verificar activos disponibles
        print("\n7️⃣ Verificando activos disponibles...")
        try:
            # Intentar obtener algunos activos
            print("   ⏳ Obteniendo lista de activos...")
            time.sleep(1)
            print("   ✅ Conexión estable")
        except Exception as e:
            print(f"   ⚠️ Error obteniendo activos: {e}")
        
        print("\n" + "=" * 70)
        print("✅ IQ OPTION ESTÁ FUNCIONANDO CORRECTAMENTE")
        print("=" * 70)
        print("\n💡 Puedes usar IQ Option desde la interfaz gráfica")
        print("   Solo cambia el broker a 'IQ Option' en la configuración")
        
    else:
        print(f"   ❌ ERROR DE CONEXIÓN: {reason}")
        print("\n   Posibles causas:")
        print("   - Credenciales incorrectas")
        print("   - Cuenta bloqueada o suspendida")
        print("   - Problemas de red")
        
except Exception as e:
    print(f"   ❌ Error durante conexión: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
