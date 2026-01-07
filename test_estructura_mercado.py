"""
Test del Sistema de Análisis de Estructura de Mercado
"""
import pandas as pd
import numpy as np
from core.market_structure_analyzer import MarketStructureAnalyzer
from datetime import datetime, timedelta

def generate_test_candles(scenario='accumulation'):
    """Genera velas de prueba según el escenario"""
    
    base_price = 100.0
    num_candles = 100
    
    dates = [datetime.now() - timedelta(minutes=i) for i in range(num_candles, 0, -1)]
    
    if scenario == 'accumulation':
        # Caída seguida de rango lateral (acumulación)
        prices = []
        for i in range(num_candles):
            if i < 40:
                # Caída
                prices.append(base_price - (i * 0.2))
            else:
                # Rango lateral (acumulación)
                prices.append(92 + np.random.uniform(-0.3, 0.3))
        
    elif scenario == 'markup':
        # Salida de acumulación (despegue alcista)
        prices = []
        for i in range(num_candles):
            if i < 40:
                # Caída
                prices.append(base_price - (i * 0.2))
            elif i < 70:
                # Acumulación
                prices.append(92 + np.random.uniform(-0.3, 0.3))
            else:
                # Despegue (markup)
                prices.append(92 + ((i - 70) * 0.3))
    
    elif scenario == 'distribution':
        # Subida seguida de rango lateral (distribución)
        prices = []
        for i in range(num_candles):
            if i < 40:
                # Subida
                prices.append(base_price + (i * 0.2))
            else:
                # Rango lateral (distribución)
                prices.append(108 + np.random.uniform(-0.3, 0.3))
    
    elif scenario == 'markdown':
        # Salida de distribución (despegue bajista)
        prices = []
        for i in range(num_candles):
            if i < 40:
                # Subida
                prices.append(base_price + (i * 0.2))
            elif i < 70:
                # Distribución
                prices.append(108 + np.random.uniform(-0.3, 0.3))
            else:
                # Despegue (markdown)
                prices.append(108 - ((i - 70) * 0.3))
    
    elif scenario == 'bullish_bos':
        # Tendencia alcista con BOS
        prices = []
        last_high = base_price
        for i in range(num_candles):
            if i % 20 == 0 and i > 0:
                last_high += 2
            prices.append(last_high + np.random.uniform(-0.5, 0.5))
            if i == num_candles - 5:
                # BOS: romper el último high
                prices[-1] = last_high + 1.5
    
    elif scenario == 'choch':
        # Cambio de carácter (reversión)
        prices = []
        for i in range(num_candles):
            if i < 60:
                # Tendencia bajista
                prices.append(base_price - (i * 0.15))
            else:
                # Reversión alcista (CHoCH)
                prices.append(91 + ((i - 60) * 0.2))
    
    else:
        # Neutral
        prices = [base_price + np.random.uniform(-1, 1) for _ in range(num_candles)]
    
    # Crear DataFrame
    data = []
    for i, (date, close) in enumerate(zip(dates, prices)):
        high = close + np.random.uniform(0, 0.2)
        low = close - np.random.uniform(0, 0.2)
        open_price = close + np.random.uniform(-0.1, 0.1)
        
        data.append({
            'timestamp': date,
            'open': open_price,
            'high': high,
            'low': low,
            'close': close,
            'volume': np.random.uniform(1000, 5000)
        })
    
    return pd.DataFrame(data)


def test_scenario(analyzer, scenario_name, candles):
    """Prueba un escenario específico"""
    print("\n" + "="*80)
    print(f"🧪 PROBANDO ESCENARIO: {scenario_name.upper()}")
    print("="*80)
    
    # Analizar
    analysis = analyzer.analyze_full_context(candles)
    
    # Mostrar resultado
    readable = analyzer.get_human_readable_analysis(analysis)
    print(readable)
    
    # Verificar resultado esperado
    entry_signal = analysis['entry_signal']
    print("\n📋 RESUMEN:")
    print(f"   Fase detectada: {analysis['market_phase']}")
    print(f"   Tendencia: {analysis['structure']['trend']}")
    print(f"   Momentum: {analysis['momentum']['state']}")
    print(f"   Debe entrar: {'✅ SÍ' if entry_signal['should_enter'] else '❌ NO'}")
    if entry_signal['should_enter']:
        print(f"   Dirección: {entry_signal['direction']}")
        print(f"   Confianza: {entry_signal['confidence']}%")


def main():
    print("="*80)
    print("🧪 TEST DEL SISTEMA DE ANÁLISIS DE ESTRUCTURA DE MERCADO")
    print("="*80)
    
    analyzer = MarketStructureAnalyzer()
    
    # Escenarios a probar
    scenarios = [
        ('accumulation', 'Acumulación (rango lateral después de caída)'),
        ('markup', 'Markup (despegue alcista desde acumulación)'),
        ('distribution', 'Distribución (rango lateral después de subida)'),
        ('markdown', 'Markdown (despegue bajista desde distribución)'),
        ('bullish_bos', 'BOS Alcista (quiebre de estructura)'),
        ('choch', 'CHoCH (cambio de carácter - reversión)')
    ]
    
    for scenario_key, scenario_desc in scenarios:
        candles = generate_test_candles(scenario_key)
        test_scenario(analyzer, scenario_desc, candles)
        input("\n⏸️ Presiona ENTER para continuar al siguiente escenario...")
    
    print("\n" + "="*80)
    print("✅ PRUEBAS COMPLETADAS")
    print("="*80)
    print("\n💡 El sistema está listo para usar en el bot")
    print("   Ejecuta: python main_modern.py")


if __name__ == "__main__":
    main()
