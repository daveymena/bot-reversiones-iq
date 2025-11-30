"""Script de prueba con configuración correcta de Exnova"""
import sys
import time
from config import Config

try:
    from exnovaapi.stable_api import Exnova
    print("✅ exnovaapi importada\n")
except ImportError as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

def test_exnova_correcto():
    print("=" * 60)
    print("PRUEBA EXNOVA - CONFIGURACIÓN CORRECTA")
    print("=" * 60)
    
    print("\n[1/5] INICIALIZANDO...")
    # CORRECCIÓN: Solo email y password, SIN account_type
    api = Exnova(Config.EX_EMAIL, Config.EX_PASSWORD)
    print("✅ API inicializada")
    
    print("\n[2/5] CONECTANDO...")
    try:
        status, message = api.connect()
        
        if not status:
            print(f"❌ Fallo: {message}")
            return False
        
        print(f"✅ Conectado: {message}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n[3/5] VERIFICANDO WEBSOCKET...")
    if not api.check_connect():
        print("❌ WebSocket NO conectado")
        return False
    print("✅ WebSocket OK")
    
    print("\n[4/5] OBTENIENDO INFO...")
    try:
        balance = api.get_balance()
        currency = api.get_currency()
        mode = api.get_balance_mode()
        print(f"💰 Balance: {balance} {currency}")
        print(f"📊 Modo: {mode}")
    except Exception as e:
        print(f"⚠️ Error: {e}")
    
    print("\n[5/5] ACTUALIZANDO ACTIVOS...")
    try:
        api.update_ACTIVES_OPCODE()
        print("✅ Códigos actualizados")
    except Exception as e:
        print(f"⚠️ Error: {e}")
    
    print("\n[6/6] PROBANDO VELAS...")
    try:
        candles = api.get_candles("EURUSD-OTC", 60, 5, int(time.time()))
        if candles and len(candles) > 0:
            print(f"✅ {len(candles)} velas obtenidas")
        else:
            print("⚠️ Sin velas")
    except Exception as e:
        print(f"⚠️ Error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ EXNOVA FUNCIONAL")
    print("=" * 60)
    return True

if __name__ == "__main__":
    try:
        test_exnova_correcto()
    except KeyboardInterrupt:
        print("\nInterrumpido")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
