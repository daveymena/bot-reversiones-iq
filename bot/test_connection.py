#!/usr/bin/env python3
"""
Script de diagnóstico para probar la conexión a Exnova
"""
import sys
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Importar la API
from exnovaapi.stable_api import Exnova

def test_connection():
    email = os.getenv("EXNOVA_EMAIL", "")
    password = os.getenv("EXNOVA_PASSWORD", "")
    
    print(f"═══════════════════════════════════════════════════")
    print(f"  TEST DE CONEXIÓN A EXNOVA")
    print(f"═══════════════════════════════════════════════════")
    print(f"Email: {email}")
    print(f"Password: {'*' * len(password)}")
    print(f"Tipo de cuenta: PRACTICE")
    print(f"═══════════════════════════════════════════════════\n")
    
    try:
        print("1. Creando instancia de Exnova API...")
        api = Exnova(email, password, active_account_type="PRACTICE")
        print("   ✓ Instancia creada\n")
        
        print("2. Intentando conectar...")
        check, reason = api.connect()
        
        if check:
            print("   ✓ CONEXIÓN EXITOSA!\n")
            
            print("3. Verificando conexión...")
            if api.check_connect():
                print("   ✓ Conexión verificada\n")
                
                print("4. Obteniendo balance...")
                balance = api.get_balance()
                print(f"   ✓ Balance: ${balance:,.2f}\n")
                
                print("5. Obteniendo activos disponibles...")
                try:
                    api.update_ACTIVES_OPCODE()
                    print("   ✓ Activos actualizados\n")
                except Exception as e:
                    print(f"   ⚠ Error actualizando activos: {e}\n")
                
                print("═══════════════════════════════════════════════════")
                print("  ✓ TODAS LAS PRUEBAS PASARON")
                print("═══════════════════════════════════════════════════")
                return True
            else:
                print("   ✗ Conexión no verificada\n")
                return False
        else:
            print(f"   ✗ CONEXIÓN FALLIDA\n")
            print(f"Razón: {reason}\n")
            print("═══════════════════════════════════════════════════")
            print("  ✗ PRUEBA FALLIDA")
            print("═══════════════════════════════════════════════════")
            return False
            
    except Exception as e:
        print(f"\n✗ ERROR CRÍTICO: {e}\n")
        import traceback
        traceback.print_exc()
        print("\n═══════════════════════════════════════════════════")
        print("  ✗ PRUEBA FALLIDA CON EXCEPCIÓN")
        print("═══════════════════════════════════════════════════")
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
