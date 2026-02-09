"""
Script para probar el Parsing de Señales
"""
from core.signal_parser import SignalParser

def test_parser():
    print("====================================")
    print("TEST DE PARSER DE SEÑALES TELEGRAM")
    print("====================================")
    
    parser = SignalParser()
    
    # -----------------------------------------------
    # PRUEBAS UNITARIAS
    # -----------------------------------------------
    ejemplos_tipicos = [
        "ATENCION: EURUSD-OTC CALL 5 MIN",
        "VAMOS CON PUT EN GBPJPY 1M YA",
        "AUD/CAD COMPRA M3",
        "USD-JPY VENTA 5",
        "SEÑAL: \nACTIVO: EURUSD\nACCION: CALL\nTIEMPO: 3 min",
        "🟢 EURUSD-OTC ⬆️ 5M",
        "🔴 GBPUSD-OTC ⬇️ 1M"
    ]
    
    print("\n[TEST 1] Formatos Típicos:")
    for msg in ejemplos_tipicos:
        signal = parser.parse(msg)
        if signal:
            print(f"✅ OK: '{msg}' -> {signal['asset']} {signal['direction'].upper()} {signal['expiration']}m")
        else:
            print(f"❌ FALLO: '{msg}' -> No se detectó señal")

    # -----------------------------------------------
    # PRUEBA INTERACTIVA
    # -----------------------------------------------
    print("\n" + "="*40)
    print("PRUEBA INTERACTIVA (Escribe tu mensaje)")
    print("========================================")
    
    while True:
        try:
            user_input = input("\nEscribe un mensaje de prueba (o 'salir'): ")
            if user_input.lower() in ['salir', 'exit', 'q']:
                break
            
            signal = parser.parse(user_input)
            
            if signal:
                print("\n✅ SEÑAL DETECTADA:")
                print(f"   Activo:    {signal['asset']}")
                print(f"   Dirección: {signal['direction'].upper()}")
                print(f"   Expiración: {signal['expiration']} minutos")
            else:
                print("\n❌ NO SE DETECTÓ SEÑAL. Verifica el formato.")
                
        except KeyboardInterrupt:
            break
            
    print("\n👋 Test finalizado.")

if __name__ == "__main__":
    test_parser()
