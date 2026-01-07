"""
Test de Timing Óptimo de Entrada
Verifica que el bot espere el momento correcto para entrar
"""
import pandas as pd
import numpy as np
from core.decision_validator import DecisionValidator

def create_premature_entry_scenario():
    """
    Crea escenario donde el precio sube pero sin pullback
    (entrada prematura - debería rechazar)
    """
    n = 100
    data = {
        'open': [],
        'high': [],
        'low': [],
        'close': [],
    }
    
    base_price = 1.40800
    
    # Primeras 95 velas: tendencia alcista
    for i in range(95):
        open_price = base_price + i * 0.00005
        close_price = open_price + 0.00003  # Velas verdes
        high_price = close_price + 0.00002
        low_price = open_price - 0.00001
        
        data['open'].append(open_price)
        data['high'].append(high_price)
        data['low'].append(low_price)
        data['close'].append(close_price)
    
    # Últimas 5 velas: continúa subiendo (sin pullback)
    for i in range(5):
        open_price = data['close'][-1]
        close_price = open_price + 0.00004  # Sigue subiendo
        high_price = close_price + 0.00002
        low_price = open_price - 0.00001
        
        data['open'].append(open_price)
        data['high'].append(high_price)
        data['low'].append(low_price)
        data['close'].append(close_price)
    
    return pd.DataFrame(data)

def create_optimal_entry_scenario():
    """
    Crea escenario con pullback + impulso
    (entrada óptima - debería aprobar)
    """
    n = 100
    data = {
        'open': [],
        'high': [],
        'low': [],
        'close': [],
    }
    
    base_price = 1.40800
    
    # Primeras 92 velas: tendencia alcista
    for i in range(92):
        open_price = base_price + i * 0.00005
        close_price = open_price + 0.00003  # Velas verdes
        high_price = close_price + 0.00002
        low_price = open_price - 0.00001
        
        data['open'].append(open_price)
        data['high'].append(high_price)
        data['low'].append(low_price)
        data['close'].append(close_price)
    
    # Velas 93-97: pullback (consolidación bajista)
    for i in range(5):
        open_price = data['close'][-1]
        close_price = open_price - 0.00002  # Velas rojas (pullback)
        high_price = open_price + 0.00001
        low_price = close_price - 0.00001
        
        data['open'].append(open_price)
        data['high'].append(high_price)
        data['low'].append(low_price)
        data['close'].append(close_price)
    
    # Velas 98-100: impulso alcista fuerte
    for i in range(3):
        open_price = data['close'][-1]
        close_price = open_price + 0.00008  # Vela verde FUERTE (impulso)
        high_price = close_price + 0.00003
        low_price = open_price - 0.00001
        
        data['open'].append(open_price)
        data['high'].append(high_price)
        data['low'].append(low_price)
        data['close'].append(close_price)
    
    return pd.DataFrame(data)

def test_timing_detection():
    """Prueba la detección de timing óptimo"""
    print("=" * 70)
    print("🧪 TEST DE TIMING ÓPTIMO DE ENTRADA")
    print("=" * 70)
    
    validator = DecisionValidator()
    
    # Test 1: Entrada Prematura (sin pullback)
    print("\n📊 Test 1: Entrada Prematura (Sin Pullback)")
    print("-" * 70)
    premature_df = create_premature_entry_scenario()
    
    can_enter, message = validator.wait_for_optimal_entry(premature_df, 'CALL')
    
    print(f"Resultado: {'✅ APROBADO' if can_enter else '❌ RECHAZADO'}")
    if message:
        print(f"Mensaje: {message}")
    
    if not can_enter:
        print("✅ CORRECTO: Bot rechazó entrada prematura")
    else:
        print("❌ ERROR: Bot debería rechazar entrada sin pullback")
    
    # Test 2: Entrada Óptima (con pullback + impulso)
    print("\n📊 Test 2: Entrada Óptima (Pullback + Impulso)")
    print("-" * 70)
    optimal_df = create_optimal_entry_scenario()
    
    can_enter, message = validator.wait_for_optimal_entry(optimal_df, 'CALL')
    
    print(f"Resultado: {'✅ APROBADO' if can_enter else '❌ RECHAZADO'}")
    if message:
        print(f"Mensaje: {message}")
    
    if can_enter:
        print("✅ CORRECTO: Bot aprobó entrada óptima")
    else:
        print("❌ ERROR: Bot debería aprobar entrada con pullback + impulso")
    
    # Test 3: Verificar Pullback
    print("\n📊 Test 3: Detección de Pullback")
    print("-" * 70)
    
    has_pullback_premature, msg1 = validator.detect_pullback(premature_df, 'CALL')
    has_pullback_optimal, msg2 = validator.detect_pullback(optimal_df, 'CALL')
    
    print(f"Escenario Prematuro: {'✅ Pullback' if has_pullback_premature else '❌ Sin Pullback'}")
    print(f"  {msg1}")
    print(f"Escenario Óptimo: {'✅ Pullback' if has_pullback_optimal else '❌ Sin Pullback'}")
    print(f"  {msg2}")
    
    # Test 4: Verificar Impulso
    print("\n📊 Test 4: Confirmación de Impulso")
    print("-" * 70)
    
    has_impulse_premature, msg1, strength1 = validator.confirm_momentum_impulse(premature_df, 'CALL')
    has_impulse_optimal, msg2, strength2 = validator.confirm_momentum_impulse(optimal_df, 'CALL')
    
    print(f"Escenario Prematuro:")
    print(f"  Impulso: {'✅ Sí' if has_impulse_premature else '❌ No'}")
    print(f"  Fuerza: {strength1:.2f}x")
    print(f"  {msg1}")
    
    print(f"\nEscenario Óptimo:")
    print(f"  Impulso: {'✅ Sí' if has_impulse_optimal else '❌ No'}")
    print(f"  Fuerza: {strength2:.2f}x")
    print(f"  {msg2}")
    
    # Resumen Final
    print("\n" + "=" * 70)
    print("📋 RESUMEN DE PRUEBAS")
    print("=" * 70)
    
    tests_passed = 0
    tests_total = 4
    
    # Test 1: Rechazar entrada prematura
    if not can_enter:  # Usar resultado del test 1
        tests_passed += 1
        print("✅ Test 1: Rechazo de entrada prematura - PASADO")
    else:
        print("❌ Test 1: Rechazo de entrada prematura - FALLADO")
    
    # Test 2: Aprobar entrada óptima
    can_enter_optimal, _ = validator.wait_for_optimal_entry(optimal_df, 'CALL')
    if can_enter_optimal:
        tests_passed += 1
        print("✅ Test 2: Aprobación de entrada óptima - PASADO")
    else:
        print("❌ Test 2: Aprobación de entrada óptima - FALLADO")
    
    # Test 3: Detección de pullback
    if not has_pullback_premature and has_pullback_optimal:
        tests_passed += 1
        print("✅ Test 3: Detección de pullback - PASADO")
    else:
        print("❌ Test 3: Detección de pullback - FALLADO")
    
    # Test 4: Confirmación de impulso
    if strength2 > strength1 and has_impulse_optimal:
        tests_passed += 1
        print("✅ Test 4: Confirmación de impulso - PASADO")
    else:
        print("❌ Test 4: Confirmación de impulso - FALLADO")
    
    print("\n" + "=" * 70)
    print(f"🎯 RESULTADO FINAL: {tests_passed}/{tests_total} tests pasados")
    
    if tests_passed == tests_total:
        print("✅ TODOS LOS TESTS PASARON - Timing óptimo funcionando correctamente")
    else:
        print(f"⚠️ {tests_total - tests_passed} tests fallaron - Revisar implementación")
    
    print("=" * 70)
    
    # Ejemplo de uso en producción
    print("\n📝 EJEMPLO DE USO EN PRODUCCIÓN:")
    print("-" * 70)
    print("""
    # El bot detecta señal CALL
    signal = 'CALL'
    
    # Verifica timing óptimo
    can_enter, message = validator.wait_for_optimal_entry(df, signal)
    
    if can_enter:
        print(f"🎯 {message}")
        print("🚀 Ejecutando operación...")
        # execute_trade(signal)
    else:
        print(f"⏳ {message}")
        print("⏸️ Esperando mejor momento...")
        # wait_and_retry()
    """)

if __name__ == "__main__":
    test_timing_detection()
