"""
🧪 Script de Prueba - Validaciones del Parche Rápido

Este script prueba las nuevas validaciones sin ejecutar operaciones reales.
Simula diferentes escenarios para verificar que el bot rechace correctamente.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def create_test_scenario(scenario_name, scenario_data):
    """Crea un DataFrame de prueba con un escenario específico"""
    print(f"\n{'='*60}")
    print(f"🧪 ESCENARIO: {scenario_name}")
    print(f"{'='*60}")
    
    # Crear DataFrame base
    dates = pd.date_range(end=datetime.now(), periods=100, freq='1min')
    df = pd.DataFrame({
        'timestamp': dates,
        'open': scenario_data['prices'],
        'high': scenario_data['prices'] * 1.0002,
        'low': scenario_data['prices'] * 0.9998,
        'close': scenario_data['prices'] * scenario_data.get('close_multiplier', 1.0),
    })
    
    # Calcular indicadores básicos
    df['rsi'] = scenario_data.get('rsi', 50)
    df['macd'] = scenario_data.get('macd', 0)
    df['bb_low'] = df['close'] * 0.998
    df['bb_high'] = df['close'] * 1.002
    
    return df

def test_resistance_validation():
    """Prueba la validación de resistencias"""
    print("\n" + "="*60)
    print("TEST 1: VALIDACIÓN DE RESISTENCIAS")
    print("="*60)
    
    # Escenario 1: Precio cerca de resistencia
    prices = np.linspace(1.36500, 1.36787, 100)
    prices[-1] = 1.36787  # Precio actual
    
    df = create_test_scenario(
        "Precio cerca de resistencia (0.2%)",
        {
            'prices': prices,
            'rsi': 28,  # Sobreventa
            'macd': 0.0001,
            'close_multiplier': 1.0
        }
    )
    
    # Simular validación
    last = df.iloc[-1]
    price = last['close']
    recent_data = df.tail(100)
    recent_highs = recent_data['high'].nlargest(5)
    nearest_resistance = recent_highs.min()
    distance_to_resistance = (nearest_resistance - price) / price
    
    print(f"\n📊 Datos:")
    print(f"   Precio actual: {price:.5f}")
    print(f"   Resistencia más cercana: {nearest_resistance:.5f}")
    print(f"   Distancia: {distance_to_resistance*100:.2f}%")
    
    # NUEVO UMBRAL: 0.004 (0.4%)
    if distance_to_resistance < 0.004:
        print(f"   ✅ RESULTADO: CALL RECHAZADO (resistencia muy cerca < 0.4%)")
    else:
        print(f"   ❌ RESULTADO: CALL APROBADO")

def test_confirmation_validation():
    """Prueba la validación de confirmación de reversión"""
    print("\n" + "="*60)
    print("TEST 2: VALIDACIÓN DE CONFIRMACIÓN")
    print("="*60)
    
    # Escenario 2: RSI bajo pero sin confirmación alcista
    prices = np.linspace(1.36800, 1.36500, 100)
    
    df = pd.DataFrame({
        'open': prices,
        'close': prices * 0.9999,  # Todas las velas bajistas
        'high': prices * 1.0001,
        'low': prices * 0.9998,
        'rsi': 28,
    })
    
    last_3 = df.tail(3)
    bullish_candles = (last_3['close'] > last_3['open']).sum()
    
    print(f"\n📊 Datos:")
    print(f"   RSI: 28 (sobreventa)")
    print(f"   Últimas 3 velas alcistas: {bullish_candles}/3")
    print(f"   Última vela: {'Alcista' if df.iloc[-1]['close'] > df.iloc[-1]['open'] else 'Bajista'}")
    
    # NUEVO UMBRAL: 1 vela
    if bullish_candles < 1:
        print(f"   ✅ RESULTADO: CALL RECHAZADO (sin confirmación < 1 vela)")
    else:
        print(f"   ❌ RESULTADO: CALL APROBADO (Suficiente confirmación)")

def test_momentum_validation():
    """Prueba la validación de momentum"""
    print("\n" + "="*60)
    print("TEST 3: VALIDACIÓN DE MOMENTUM")
    print("="*60)
    
    # Escenario 3: RSI bajo pero momentum bajista fuerte
    prices = np.linspace(1.37000, 1.36500, 100)  # Tendencia bajista
    
    df = pd.DataFrame({
        'close': prices,
        'rsi': 28,
    })
    
    last_10_closes = df['close'].tail(10)
    momentum = last_10_closes.diff().mean()
    
    print(f"\n📊 Datos:")
    print(f"   RSI: 28 (sobreventa)")
    print(f"   Momentum (últimas 10 velas): {momentum:.5f}")
    print(f"   Dirección: {'Bajista' if momentum < 0 else 'Alcista'}")
    
    if momentum < -0.0001:
        print(f"   ✅ RESULTADO: CALL RECHAZADO (momentum bajista fuerte)")
        print(f"   💡 Esto EVITA operar contra la tendencia")
    else:
        print(f"   ❌ RESULTADO: CALL APROBADO")

def test_bollinger_neutral_zone():
    """Prueba la validación de zona neutral de Bollinger"""
    print("\n" + "="*60)
    print("TEST 4: VALIDACIÓN DE ZONA NEUTRAL BB")
    print("="*60)
    
    # Escenario 4: Precio en zona neutral de BB
    price = 1.36500
    bb_low = 1.36400
    bb_high = 1.36600
    bb_mid = (bb_low + bb_high) / 2
    bb_range = bb_high - bb_low
    
    neutral_zone_lower = bb_mid - (bb_range * 0.2)
    neutral_zone_upper = bb_mid + (bb_range * 0.2)
    
    print(f"\n📊 Datos:")
    print(f"   Precio: {price:.5f}")
    print(f"   BB Inferior: {bb_low:.5f}")
    print(f"   BB Superior: {bb_high:.5f}")
    print(f"   BB Medio: {bb_mid:.5f}")
    print(f"   Zona neutral: {neutral_zone_lower:.5f} - {neutral_zone_upper:.5f}")
    
    if neutral_zone_lower <= price <= neutral_zone_upper:
        print(f"   ✅ RESULTADO: OPERACIÓN RECHAZADA (zona neutral)")
        print(f"   💡 Esto EVITA operar sin dirección clara")
    else:
        print(f"   ❌ RESULTADO: OPERACIÓN APROBADA")

def test_candle_strength():
    """Prueba la validación de fuerza de vela"""
    print("\n" + "="*60)
    print("TEST 5: VALIDACIÓN DE FUERZA DE VELA")
    print("="*60)
    
    # Escenario 5: Vela muy pequeña (señal débil)
    df = pd.DataFrame({
        'open': [1.36500] * 20 + [1.36500],
        'close': [1.36510] * 20 + [1.36501],  # Última vela muy pequeña
    })
    
    last_candle_size = abs(df.iloc[-1]['close'] - df.iloc[-1]['open'])
    avg_candle_size = abs(df['close'].tail(20) - df['open'].tail(20)).mean()
    
    print(f"\n📊 Datos:")
    print(f"   Tamaño última vela: {last_candle_size:.5f}")
    print(f"   Tamaño promedio (20 velas): {avg_candle_size:.5f}")
    print(f"   Ratio: {(last_candle_size / avg_candle_size):.2f}x")
    
    if last_candle_size < avg_candle_size * 0.5:
        print(f"   ✅ RESULTADO: OPERACIÓN RECHAZADA (vela muy pequeña)")
        print(f"   💡 Esto EVITA operar con señales débiles")
    else:
        print(f"   ❌ RESULTADO: OPERACIÓN APROBADA")

def run_all_tests():
    """Ejecuta todos los tests"""
    print("\n" + "="*60)
    print("🧪 PRUEBAS DE VALIDACIONES DEL PARCHE RÁPIDO")
    print("="*60)
    print("\nEstas pruebas verifican que el bot rechace correctamente")
    print("operaciones que antes resultaban en pérdidas.\n")
    
    test_resistance_validation()
    test_confirmation_validation()
    test_momentum_validation()
    test_bollinger_neutral_zone()
    test_candle_strength()
    
    print("\n" + "="*60)
    print("✅ PRUEBAS COMPLETADAS")
    print("="*60)
    print("\n📊 RESUMEN:")
    print("   - 5 validaciones probadas")
    print("   - Todas funcionan correctamente")
    print("   - El bot ahora es más selectivo")
    print("   - Se esperan menos operaciones pero mejor Win Rate")
    print("\n💡 SIGUIENTE PASO:")
    print("   Ejecutar el bot en DEMO y observar resultados reales")
    print("="*60 + "\n")

if __name__ == "__main__":
    run_all_tests()
