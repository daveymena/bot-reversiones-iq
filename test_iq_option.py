"""Script de prueba simplificado para IQ Option"""
import sys
import time
from config import Config

try:
    from iqoptionapi.stable_api import IQ_Option
    print("✅ iqoptionapi importada correctamente\n")
except ImportError as e:
    print(f"❌ Error importando iqoptionapi: {e}")
    sys.exit(1)

def test_iq_option():
    print("=" * 60)
    print("PRUEBA DE IQ OPTION")
    print("=" * 60)
    
    # CONEXIÓN
    print("\n[1/4] CONECTANDO...")
    # Mostrar IP pública para diagnóstico
    try:
        import urllib.request
        external_ip = urllib.request.urlopen('https://api.ipify.org').read().decode('utf8')
        print(f"[DEBUG] IP pública: {external_ip}")
    except Exception as e:
        print(f"[DEBUG] No se pudo obtener IP pública: {e}")
    # Intentar conectar con reintentos
    max_retries = 5
    for attempt in range(1, max_retries + 1):
        print(f"[DEBUG] Intento de conexión {attempt}/{max_retries}")
        api = IQ_Option(Config.IQ_EMAIL, Config.IQ_PASSWORD)
        check, reason = api.connect()
        if check:
            print("✅ Conectado en intento", attempt)
            break
        else:
            print(f"❌ Fallo intento {attempt}: {reason}")
            if attempt < max_retries:
                import time
                time.sleep(5)
    else:
        print("❌ No se pudo conectar después de varios intentos")
        return False

    
    if not check:
        print(f"❌ FALLO: {reason}")
        return False
    
    print("✅ Conectado")
    
    # BALANCE
    print("\n[2/4] BALANCE...")
    api.change_balance("PRACTICE")
    time.sleep(1)
    balance = api.get_balance()
    print(f"💰 ${balance:.2f} (PRACTICE)")
    
    # VELAS
    print("\n[3/4] DATOS DE MERCADO...")
    try:
        candles = api.get_candles("EURUSD", 60, 5, time.time())
        if candles and len(candles) > 0:
            print(f"✅ {len(candles)} velas obtenidas")
            last = candles[-1]
            print(f"   Última: O={last['open']:.5f} C={last['close']:.5f}")
        else:
            print("⚠️ Sin velas")
    except Exception as e:
        print(f"⚠️ Error: {e}")
    
    # ACTIVOS OTC
    print("\n[4/4] ACTIVOS OTC...")
    try:
        # Probar velas OTC
        candles_otc = api.get_candles("EURUSD-OTC", 60, 5, time.time())
        if candles_otc and len(candles_otc) > 0:
            print(f"✅ OTC disponible ({len(candles_otc)} velas)")
        else:
            print("⚠️ OTC sin datos (puede estar cerrado)")
    except Exception as e:
        print(f"⚠️ OTC error: {str(e)[:50]}")
    
    print("\n" + "=" * 60)
    print("✅ IQ OPTION OPERATIVO")
    print("=" * 60)
    return True

if __name__ == "__main__":
    try:
        success = test_iq_option()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
