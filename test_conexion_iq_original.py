"""
Test de conexión a IQ Option
Verifica las credenciales y la conexión
"""
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv("bot_reversiones_pro/config/.env")

email = os.getenv("IQ_EMAIL")
password = os.getenv("IQ_PASSWORD")

print("="*60)
print("TEST DE CONEXIÓN A IQ OPTION")
print("="*60)
print(f"\nEmail: {email}")
print(f"Password length: {len(password)} caracteres")
print(f"Password (oculta): {'*' * len(password)}")
print(f"Primer carácter: {password[0] if password else 'N/A'}")
print(f"Último carácter: {password[-1] if password else 'N/A'}")

print("\n" + "="*60)
print("INTENTANDO CONEXIÓN...")
print("="*60)

try:
    from iqoptionapi.stable_api import IQ_Option
    import time
    
    print("\n[1/4] Creando instancia de IQ_Option...")
    api = IQ_Option(email, password)
    
    print("[2/4] Conectando...")
    check, reason = api.connect()
    
    if check:
        print("[3/4] ✓ Conexión exitosa!")
        
        print("[4/4] Configurando modo DEMO...")
        api.change_balance("PRACTICE")
        
        balance = api.get_balance()
        print(f"\n✓ CONEXIÓN EXITOSA")
        print(f"Balance DEMO: ${balance:.2f}")
        
        # Obtener información de la cuenta
        print("\nInformación de la cuenta:")
        profile = api.get_profile()
        if profile:
            print(f"  - ID: {profile.get('user_id', 'N/A')}")
            print(f"  - Nombre: {profile.get('name', 'N/A')}")
            print(f"  - Email: {profile.get('email', 'N/A')}")
        
    else:
        print(f"\n✗ ERROR DE CONEXIÓN")
        print(f"Razón: {reason}")
        
        if "invalid_credentials" in str(reason).lower():
            print("\n⚠️ CREDENCIALES INVÁLIDAS")
            print("\nPosibles causas:")
            print("1. Email o contraseña incorrectos")
            print("2. La cuenta necesita verificación")
            print("3. La cuenta está bloqueada")
            print("4. Necesitas iniciar sesión en el sitio web primero")
            print("\nSoluciones:")
            print("1. Verifica tu email y contraseña en https://iqoption.com")
            print("2. Intenta iniciar sesión en el navegador primero")
            print("3. Verifica que no tengas 2FA activado")
            print("4. Asegúrate de que la cuenta esté activa")
        
except Exception as e:
    print(f"\n✗ ERROR CRÍTICO: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
