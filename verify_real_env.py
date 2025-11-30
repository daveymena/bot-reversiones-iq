"""
Verificación de Configuración para Cuenta REAL
Verifica que el archivo .env tenga las credenciales necesarias sin exponerlas.
"""
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

print("=" * 70)
print("🔐 VERIFICACIÓN DE CONFIGURACIÓN (.env)")
print("=" * 70)

# 1. Verificar Broker
broker = os.getenv("BROKER_NAME")
print(f"\n1️⃣ Broker Configurado: {broker}")
if broker != "iq":
    print("   ⚠️ ADVERTENCIA: BROKER_NAME no es 'iq'. El bot usará Exnova.")
    print("   Para probar IQ Option, cambia BROKER_NAME=iq en .env")

# 2. Verificar Tipo de Cuenta
account_type = os.getenv("ACCOUNT_TYPE")
print(f"\n2️⃣ Tipo de Cuenta: {account_type}")
if account_type != "REAL":
    print("   ⚠️ ADVERTENCIA: ACCOUNT_TYPE no es 'REAL'.")
    print("   Para pruebas reales, cambia ACCOUNT_TYPE=REAL en .env")

# 3. Verificar Credenciales IQ Option
print("\n3️⃣ Credenciales IQ Option:")
email = os.getenv("IQ_OPTION_EMAIL")
password = os.getenv("IQ_OPTION_PASSWORD")

if email:
    print(f"   ✅ Email encontrado: {email[:3]}***{email.split('@')[1] if '@' in email else ''}")
else:
    print("   ❌ ERROR: IQ_OPTION_EMAIL no encontrado en .env")

if password:
    print(f"   ✅ Password encontrado: {'*' * len(password)} ({len(password)} caracteres)")
else:
    print("   ❌ ERROR: IQ_OPTION_PASSWORD no encontrado en .env")

# 4. Verificar Credenciales Exnova (como backup)
print("\n4️⃣ Credenciales Exnova:")
ex_email = os.getenv("EXNOVA_EMAIL")
ex_password = os.getenv("EXNOVA_PASSWORD")

if ex_email:
    print(f"   ✅ Email encontrado: {ex_email[:3]}***")
else:
    print("   ⚠️ Exnova Email no encontrado")

if ex_password:
    print(f"   ✅ Password encontrado: {len(ex_password)} caracteres")
else:
    print("   ⚠️ Exnova Password no encontrado")

print("\n" + "=" * 70)
