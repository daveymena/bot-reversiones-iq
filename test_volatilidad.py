"""
Test de Verificación de Volatilidad Mínima
Prueba que el bot detecte correctamente mercados planos vs activos
"""
import pandas as pd
import numpy as np
from core.decision_validator import DecisionValidator

def create_flat_market_data(n_candles=100):
    """Crea datos de mercado plano (sin volatilidad)"""
    base_price = 1.1000
    noise = 0.00005  # Ruido mínimo
    
    data = {
        'open': [base_price + np.random.uniform(-noise, noise) for _ in range(n_candles)],
        'high': [base_price + np.random.uniform(0, noise) for _ in range(n_candles)],
        'low': [base_price - np.random.uniform(0, noise) for _ in range(n_candles)],
        'close': [base_price + np.random.uniform(-noise, noise) for _ in range(n_candles)],
    }
    
    df = pd.DataFrame(data)
    return df

def create_volatile_market_data(n_candles=100):
    """Crea datos de mercado volátil (con movimiento)"""
    base_price = 1.1000
    volatility = 0.001  # 0.1% de volatilidad
    
    data = {
        'open': [],
        'high': [],
        'low': [],
        'close': []
    }
    
    current_price = base_price
    for _ in range(n_candles):
        change = np.random.uniform(-volatility, volatility)
        current_price += change
        
        open_price = current_price
        close_price = current_price + np.random.uniform(-volatility/2, volatility/2)
        high_price = max(open_price, close_price) + np.random.uniform(0, volatility/2)
        low_price = min(open_price, close_price) - np.random.uniform(0, volatility/2)
        
        data['open'].append(open_price)
        data['high'].append(high_price)
        data['low'].append(low_price)
        data['close'].append(close_price)
    
    df = pd.DataFrame(data)
    return df

def test_volatility_detection():
    """Prueba la detección de volatilidad"""
    print("=" * 70)
    print("🧪 TEST DE DETECCIÓN DE VOLATILIDAD")
    print("=" * 70)
    
    validator = DecisionValidator()
    
    # Test 1: Mercado Plano
    print("\n📊 Test 1: Mercado Plano (Sin Volatilidad)")
    print("-" * 70)
    flat_df = create_flat_market_data(100)
    
    is_valid, message, atr_value = validator.check_minimum_volatility(flat_df)
    
    print(f"Resultado: {'✅ VÁLIDO' if is_valid else '❌ RECHAZADO'}")
    if message:
        print(f"Mensaje: {message}")
    print(f"ATR: {atr_value*100:.4f}%")
    print(f"Umbral mínimo: {validator.min_volatility_atr*100:.4f}%")
    
    if not is_valid:
        print("✅ CORRECTO: Bot rechazó mercado plano")
    else:
        print("❌ ERROR: Bot debería rechazar mercado plano")
    
    # Test 2: Mercado Volátil
    print("\n📊 Test 2: Mercado Volátil (Con Movimiento)")
    print("-" * 70)
    volatile_df = create_volatile_market_data(100)
    
    is_valid, message, atr_value = validator.check_minimum_volatility(volatile_df)
    
    print(f"Resultado: {'✅ VÁLIDO' if is_valid else '❌ RECHAZADO'}")
    if message:
        print(f"Mensaje: {message}")
    print(f"ATR: {atr_value*100:.4f}%")
    print(f"Umbral mínimo: {validator.min_volatility_atr*100:.4f}%")
    
    if is_valid:
        print("✅ CORRECTO: Bot aceptó mercado volátil")
    else:
        print("❌ ERROR: Bot debería aceptar mercado volátil")
    
    # Test 3: Movimiento de Precio
    print("\n📊 Test 3: Verificación de Movimiento de Precio")
    print("-" * 70)
    
    # Mercado plano
    is_valid_flat, message_flat = validator.check_price_movement(flat_df)
    print(f"Mercado Plano: {'✅ VÁLIDO' if is_valid_flat else '❌ RECHAZADO'}")
    if message_flat:
        print(f"  {message_flat}")
    
    # Mercado volátil
    is_valid_volatile, message_volatile = validator.check_price_movement(volatile_df)
    print(f"Mercado Volátil: {'✅ VÁLIDO' if is_valid_volatile else '❌ RECHAZADO'}")
    if message_volatile:
        print(f"  {message_volatile}")
    
    # Test 4: Estadísticas Comparativas
    print("\n📊 Test 4: Estadísticas Comparativas")
    print("-" * 70)
    
    # Calcular rangos promedio
    flat_range = (flat_df['high'] - flat_df['low']).mean()
    volatile_range = (volatile_df['high'] - volatile_df['low']).mean()
    
    print(f"Rango promedio (Mercado Plano): {flat_range:.6f}")
    print(f"Rango promedio (Mercado Volátil): {volatile_range:.6f}")
    print(f"Diferencia: {(volatile_range/flat_range):.1f}x más volátil")
    
    # Calcular desviación estándar
    flat_std = flat_df['close'].std()
    volatile_std = volatile_df['close'].std()
    
    print(f"\nDesviación estándar (Mercado Plano): {flat_std:.6f}")
    print(f"Desviación estándar (Mercado Volátil): {volatile_std:.6f}")
    print(f"Diferencia: {(volatile_std/flat_std):.1f}x más volátil")
    
    # Resumen Final
    print("\n" + "=" * 70)
    print("📋 RESUMEN DE PRUEBAS")
    print("=" * 70)
    
    tests_passed = 0
    tests_total = 4
    
    # Usar las variables correctas de cada test
    flat_is_valid, _, _ = validator.check_minimum_volatility(flat_df)
    volatile_is_valid, _, _ = validator.check_minimum_volatility(volatile_df)
    
    if not flat_is_valid:  # Test 1: Rechazar mercado plano
        tests_passed += 1
        print("✅ Test 1: Detección de mercado plano - PASADO")
    else:
        print("❌ Test 1: Detección de mercado plano - FALLADO")
    
    if volatile_is_valid:  # Test 2: Aceptar mercado volátil
        tests_passed += 1
        print("✅ Test 2: Detección de mercado volátil - PASADO")
    else:
        print("❌ Test 2: Detección de mercado volátil - FALLADO")
    
    if not is_valid_flat:  # Test 3a: Rechazar movimiento plano
        tests_passed += 1
        print("✅ Test 3a: Verificación de movimiento plano - PASADO")
    else:
        print("❌ Test 3a: Verificación de movimiento plano - FALLADO")
    
    if is_valid_volatile:  # Test 3b: Aceptar movimiento volátil
        tests_passed += 1
        print("✅ Test 3b: Verificación de movimiento volátil - PASADO")
    else:
        print("❌ Test 3b: Verificación de movimiento volátil - FALLADO")
    
    print("\n" + "=" * 70)
    print(f"🎯 RESULTADO FINAL: {tests_passed}/{tests_total} tests pasados")
    
    if tests_passed == tests_total:
        print("✅ TODOS LOS TESTS PASARON - Sistema funcionando correctamente")
    else:
        print(f"⚠️ {tests_total - tests_passed} tests fallaron - Revisar implementación")
    
    print("=" * 70)

if __name__ == "__main__":
    test_volatility_detection()
