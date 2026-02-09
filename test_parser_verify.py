from core.signal_parser import SignalParser

def verify_parser():
    print("====================================")
    print(" VERIFICANDO PARSER DE SEÑALES (AUTO)")
    print("====================================")
    
    parser = SignalParser()
    
    # Lista de pruebas que DEBEN pasar
    test_cases = [
        ("EURUSD-OTC CALL 5 MIN", {"asset": "EURUSD-OTC", "direction": "call", "expiration": 5}),
        ("GBPUSD PUT M3", {"asset": "GBPUSD-OTC", "direction": "put", "expiration": 3}),  # Asume OTC si falta
        ("AUD/CAD COMPRA 1", {"asset": "AUDCAD-OTC", "direction": "call", "expiration": 1}),
        ("USDJPY VENTA 5M", {"asset": "USDJPY-OTC", "direction": "put", "expiration": 5}),
        ("🟢 EURUSD ⬆️ 3M", {"asset": "EURUSD-OTC", "direction": "call", "expiration": 3}),  # Emojis
        ("Hola gente, cómo están?", None),  # NO es señal
    ]
    
    passed = 0
    failed = 0
    
    for message, expected in test_cases:
        result = parser.parse(message)
        
        status = "✅ PASS"
        if expected is None:
            if result is None:
                pass  # Correcto
            else:
                status = "❌ FAIL (Detectó señal falsa)"
                failed += 1
        else:
            if result and \
               result['asset'] == expected['asset'] and \
               result['direction'] == expected['direction'] and \
               result['expiration'] == expected['expiration']:
                pass  # Correcto
            else:
                status = f"❌ FAIL (Esperado: {expected}, Obtenido: {result})"
                failed += 1
        
        if status == "✅ PASS":
            passed += 1
            
        print(f"[{status}] '{message}' -> {result}")

    print("\n====================================")
    print(f"RESULTADO: {passed}/{len(test_cases)} PASARON")
    print("====================================")

if __name__ == "__main__":
    verify_parser()
