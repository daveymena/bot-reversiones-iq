#!/usr/bin/env python3
"""
Test de Conexión Básica a Exnova
Prueba directa sin capas adicionales
"""
import sys
import time
from config import Config

print("="*60)
print("TEST DE CONEXIÓN BÁSICA A EXNOVA")
print("="*60)
print(f"Email: {Config.EXNOVA_EMAIL}")
print(f"Modo: {Config.ACCOUNT_TYPE}")
print("="*60 + "\n")

try:
    # Importar API directamente
    print("1. Importando API de Exnova...")
    from exnovaapi.stable_api import ExnovaAPI
    print("   ✅ API importada\n")
    
    # Crear instancia
    print("2. Creando instancia de API...")
    api = ExnovaAPI(
        host="ws.trade.exnova.com",
        username=Config.EXNOVA_EMAIL,
        password=Config.EXNOVA_PASSWORD
    )
    print("   ✅ Instancia creada\n")
    
    # Conectar
    print("3. Conectando a Exnova...")
    print("   (Esto puede tardar 10-15 segundos)")
    
    check, reason = api.connect()
    
    if check:
        print("   ✅ CONECTADO EXITOSAMENTE!\n")
        
        # Obtener balance
        print("4. Obteniendo información de cuenta...")
        time.sleep(2)  # Esperar a que se sincronice
        
        # Cambiar a cuenta PRACTICE si es necesario
        if Config.ACCOUNT_TYPE == "PRACTICE":
            print("   Cambiando a cuenta PRACTICE...")
            api.change_balance("PRACTICE")
            time.sleep(1)
        
        # Obtener balance
        balance = api.get_balance()
        print(f"   💰 Balance: ${balance:.2f}\n")
        
        # Obtener activos disponibles
        print("5. Obteniendo activos disponibles...")
        actives = api.get_all_open_time()
        
        if actives:
            print(f"   ✅ {len(actives)} activos disponibles")
            
            # Mostrar algunos activos OTC
            otc_actives = [a for a in actives.keys() if 'OTC' in a]
            print(f"   📊 Activos OTC disponibles: {len(otc_actives)}")
            if otc_actives:
                print(f"   Ejemplos: {', '.join(list(otc_actives)[:5])}")
        
        print("\n" + "="*60)
        print("✅ PRUEBA DE CONEXIÓN EXITOSA")
        print("="*60)
        print("\nLa conexión funciona correctamente.")
        print("El problema NO es del código, fue temporal.\n")
        
        # Cerrar conexión
        api.close()
        
    else:
        print(f"   ❌ ERROR DE CONEXIÓN: {reason}\n")
        print("="*60)
        print("❌ PRUEBA DE CONEXIÓN FALLIDA")
        print("="*60)
        print(f"\nRazón: {reason}")
        print("\nPosibles causas:")
        print("1. Problema de internet/red")
        print("2. Servidor de Exnova caído")
        print("3. Credenciales incorrectas")
        print("4. Firewall bloqueando conexión\n")
        
except Exception as e:
    print(f"\n❌ ERROR FATAL: {e}")
    import traceback
    traceback.print_exc()
    print("\n" + "="*60)
    print("❌ PRUEBA DE CONEXIÓN FALLIDA")
    print("="*60)
