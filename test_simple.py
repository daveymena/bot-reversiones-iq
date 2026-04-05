#!/usr/bin/env python3
import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from config import Config
from exnovaapi.stable_api import ExnovaAPI
import time

print("="*60)
print("TEST CONEXION EXNOVA")
print("="*60)
print(f"Email: {Config.EXNOVA_EMAIL}")
print("="*60)

try:
    print("\n1. Creando API...")
    api = ExnovaAPI(
        host="ws.trade.exnova.com",
        username=Config.EXNOVA_EMAIL,
        password=Config.EXNOVA_PASSWORD
    )
    print("OK - API creada")
    
    print("\n2. Conectando...")
    check, reason = api.connect()
    
    if check:
        print("OK - CONECTADO!")
        
        time.sleep(2)
        
        if Config.ACCOUNT_TYPE == "PRACTICE":
            print("\n3. Cambiando a PRACTICE...")
            api.change_balance("PRACTICE")
            time.sleep(1)
        
        balance = api.get_balance()
        print(f"\n4. Balance: ${balance:.2f}")
        
        print("\n" + "="*60)
        print("EXITO - Conexion funciona correctamente")
        print("="*60)
        
        api.close()
        
    else:
        print(f"ERROR - No conecta: {reason}")
        
except Exception as e:
    print(f"\nERROR FATAL: {e}")
    import traceback
    traceback.print_exc()
