"""
Test de conexión Exnova usando la lógica EXACTA del bot funcional
"""
import sys
import time
from config import Config

# Importar exactamente como el bot funcional
from exnovaapi.stable_api import Exnova

def test_conexion_exacta():
    print("=" * 60)
    print("TEST CON LÓGICA EXACTA DEL BOT FUNCIONAL")
    print("=" * 60)
    
    # Credenciales (exactamente como el bot funcional)
    email = Config.EX_EMAIL
    password = Config.EX_PASSWORD
    
    print(f"\nEmail: {email}")
    print("Conectando a la API...")
    
    try:
        # 1. Inicializar API (sin account_type, como el bot funcional)
        api = Exnova(email, password)
        print("[OK] API inicializada")
        
        # 2. Conectar (exactamente como línea 147 del bot funcional)
        status, message = api.connect()
        
        if status:
            print(f"[OK] Conexion exitosa: {message}")
            
            # 3. Verificar WebSocket (exactamente como línea 154)
            if api.check_connect():
                print("[OK] Conexion WebSocket verificada!")
                
                # 4. Obtener información de cuenta (líneas 158-160)
                balance = api.get_balance()
                balance_mode = api.get_balance_mode()
                currency = api.get_currency()
                
                print(f"\n💰 Saldo: {balance} {currency}")
                print(f"📊 Tipo de cuenta: {balance_mode}")
                
                # 5. Actualizar códigos de activos (línea 177)
                print("\nActualizando codigos de activos...")
                api.update_ACTIVES_OPCODE()
                print("[OK] Códigos actualizados")
                
                # 6. Probar obtener velas
                print("\nProbando obtención de velas...")
                candles = api.get_candles("EURUSD-OTC", 60, 5, int(time.time()))
                
                if candles and len(candles) > 0:
                    print(f"[OK] {len(candles)} velas obtenidas")
                    print(f"Última vela: Open={candles[-1].get('open')}, Close={candles[-1].get('close')}")
                else:
                    print("[WARN] No se obtuvieron velas")
                
                print("\n" + "=" * 60)
                print("✅ EXNOVA FUNCIONAL - PRUEBA EXITOSA")
                print("=" * 60)
                return True
                
            else:
                print("[ERROR] Conexion WebSocket fallida!")
                return False
        else:
            print(f"[ERROR] Conexion fallida: {message}")
            return False
            
    except Exception as e:
        print(f"\n[ERROR] Error durante la conexion: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_conexion_exacta()
