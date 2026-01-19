from data.market_data import MarketDataHandler
from config import Config
import time
import os

print("\n🔍 DIAGNÓSTICO DE CONEXIÓN")
print("========================")

print("1. Verificando credenciales...")
email = Config.EXNOVA_EMAIL
# Ocultar password parcialmente
pwd_mask = "*" * len(Config.EXNOVA_PASSWORD) if Config.EXNOVA_PASSWORD else "VACIO"
print(f"   Email: {email}")
print(f"   Pass: {pwd_mask}")

if not email or not Config.EXNOVA_PASSWORD:
    print("❌ CREDENCIALES FALTANTES. Revisa tu archivo .env o config.py")
    exit(1)

print("\n2. Inicializando Handler...")
try:
    md = MarketDataHandler()
    print("   Handler OK")
except Exception as e:
    print(f"❌ Error handler: {e}")
    exit(1)

print("\n3. Conectando al Broker (Exnova)...")
try:
    ok = md.connect(email, Config.EXNOVA_PASSWORD)
    if ok:
        print("✅ CONEXIÓN EXITOSA")
    else:
        print("❌ FALLÓ LA CONEXIÓN (CheckUser/Pass o 2FA o IP bloqueada)")
        exit(1)
except Exception as e:
    print(f"❌ Excepción al conectar: {e}")
    exit(1)

print("\n4. Probando descarga de datos (EURUSD-OTC)...")
try:
    df = md.get_candles("EURUSD-OTC", 60, 10, time.time())
    if df is not None and not df.empty:
        print(f"✅ DATOS RECIBIDOS: {len(df)} velas")
        print(f"   Precio actual: {df.iloc[-1]['close']}")
    else:
        print("⚠️ CONECTADO PERO SIN DATOS (DataFrame vacío)")
except Exception as e:
    print(f"❌ Error bajando velas: {e}")

print("\n========================")
print("DIAGNÓSTICO COMPLETADO")
input("Presiona ENTER para cerrar...")
