#!/usr/bin/env python3
"""
Test simplificado del Sistema de IA Orquestador
Prueba los componentes principales sin SmartMoneyAnalyzer
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def generar_datos_prueba():
    """Genera datos de prueba realistas"""
    print("📊 Generando datos de prueba...")
    
    # Generar 100 velas de EURUSD
    np.random.seed(42)
    
    dates = pd.date_range(start='2024-01-01', periods=100, freq='1min')
    
    # Precio base
    base_price = 1.0850
    
    # Generar movimiento de precio realista
    returns = np.random.normal(0, 0.0001, 100)
    returns[30:50] = np.random.normal(0.0002, 0.0001, 20)  # Tendencia alcista
    
    prices = [base_price]
    for ret in returns:
        prices.append(prices[-1] * (1 + ret))
    
    prices = prices[1:]  # Remover el precio base
    
    # Crear OHLC realista
    data = []
    for i, price in enumerate(prices):
        volatility = np.random.uniform(0.00005, 0.0002)
        
        open_price = price
        high_price = price + np.random.uniform(0, volatility)
        low_price = price - np.random.uniform(0, volatility)
        close_price = price + np.random.uniform(-volatility/2, volatility/2)
        
        # Asegurar OHLC válido
        high_price = max(high_price, open_price, close_price)
        low_price = min(low_price, open_price, close_price)
        
        data.append({
            'timestamp': dates[i],
            'open': open_price,
            'high': high_price,
            'low': low_price,
            'close': close_price,
            'volume': np.random.randint(100, 1000)
        })
    
    df = pd.DataFrame(data)
    df.set_index('timestamp', inplace=True)
    
    # Agregar indicadores técnicos básicos
    df['rsi'] = 50 + np.random.normal(0, 15, len(df))  # RSI simulado
    df['rsi'] = df['rsi'].clip(0, 100)
    
    df['macd'] = np.random.normal(0, 0.00001, len(df))  # MACD simulado
    
    # Bollinger Bands simuladas
    df['bb_high'] = df['close'] * 1.001
    df['bb_low'] = df['close'] * 0.999
    
    print(f"✅ Generados {len(df)} velas de prueba")
    return df

def test_professional_learning():
    """Prueba el sistema de aprendizaje profesional"""
    print("\n🎓 PROBANDO SISTEMA DE APRENDIZAJE PROFESIONAL")
    print("=" * 50)
    
    try:
        from core.professional_learning_system import ProfessionalLearningSystem
        
        learning_system = ProfessionalLearningSystem()
        
        # Simular algunas lecciones
        print("📚 Simulando lecciones de trading...")
        
        # Lección 1: Operación exitosa
        trade_data = {
            'asset': 'EURUSD',
            'direction': 'call',
            'entry_price': 1.0850,
            'amount': 10
        }
        
        market_analysis = {
            'order_blocks': [{'type': 'bullish_ob', 'mitigated': False}],
            'market_phase': 'accumulation',
            'confidence': 75
        }
        
        result = {'won': True, 'profit': 8.5}
        
        lesson1 = learning_system.analyze_trade_for_learning(trade_data, market_analysis, result)
        if lesson1:
            print(f"✅ Lección 1: {lesson1.concept.value} en {lesson1.market_phase.value}")
        
        # Obtener insights
        print("\n📊 Obteniendo insights de aprendizaje...")
        insights = learning_system.get_learning_insights()
        
        if 'error' not in insights:
            print(f"   Total lecciones: {insights.get('total_lessons', 0)}")
            print(f"   Conceptos aprendidos: {insights.get('concepts_learned', 0)}")
        
        return learning_system
        
    except Exception as e:
        print(f"❌ Error en Sistema de Aprendizaje: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_market_structure_analyzer():
    """Prueba el analizador de estructura de mercado"""
    print("\n📊 PROBANDO ANALIZADOR DE ESTRUCTURA DE MERCADO")
    print("=" * 50)
    
    try:
        from core.market_structure_analyzer import MarketStructureAnalyzer
        
        analyzer = MarketStructureAnalyzer()
        df = generar_datos_prueba()
        
        print("📈 Analizando estructura completa...")
        analysis = analyzer.analyze_full_context(df)
        
        print(f"✅ Análisis completado")
        print(f"   Fase de mercado: {analysis.get('market_phase', 'N/A')}")
        
        structure = analysis.get('structure', {})
        print(f"   Tendencia: {structure.get('trend', 'N/A')} (Fuerza: {structure.get('strength', 0)}%)")
        
        entry_signal = analysis.get('entry_signal', {})
        if entry_signal.get('should_enter'):
            print(f"   🎯 ENTRADA: {entry_signal.get('direction')} con {entry_signal.get('confidence', 0):.0f}% confianza")
        else:
            print(f"   ⏳ Esperando mejor momento")
        
        return analysis
        
    except Exception as e:
        print(f"❌ Error en Analizador de Estructura: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_llm_integration():
    """Prueba la integración con Ollama"""
    print("\n🧠 PROBANDO INTEGRACIÓN CON OLLAMA")
    print("=" * 50)
    
    try:
        from ai.llm_client import LLMClient
        
        llm_client = LLMClient()
        
        # Preparar datos de prueba
        market_summary = "EURUSD: 1.0850 | RSI: 28 (Sobreventa) | MACD: Alcista | Fase: Accumulation"
        smart_money_summary = "Análisis Smart Money básico | Tendencia: Alcista | Confianza: 65%"
        learning_summary = "Performance reciente: 72% | Sistema inicializándose"
        
        print("🤖 Consultando a Ollama como trader profesional...")
        
        decision = llm_client.analyze_complete_trading_opportunity(
            market_data_summary=market_summary,
            smart_money_analysis=smart_money_summary,
            learning_insights=learning_summary,
            asset="EURUSD",
            current_balance=1000.0
        )
        
        print(f"✅ Decisión recibida de Ollama:")
        print(f"   Operar: {'SÍ' if decision.get('should_trade') else 'NO'}")
        
        if decision.get('should_trade'):
            print(f"   Dirección: {decision.get('direction')}")
            print(f"   Confianza: {decision.get('confidence', 0):.0f}%")
            print(f"   Razón: {decision.get('primary_reason', 'N/A')}")
            
            confluences = decision.get('confluences', [])
            if confluences:
                print(f"   Confluencias: {len(confluences)}")
                for i, conf in enumerate(confluences[:2], 1):
                    print(f"     {i}. {conf}")
        else:
            print(f"   Razón rechazo: {decision.get('primary_reason', 'N/A')}")
        
        return decision
        
    except Exception as e:
        print(f"❌ Error en integración Ollama: {e}")
        print("   Nota: Asegúrate de que Ollama esté ejecutándose en EasyPanel")
        import traceback
        traceback.print_exc()
        return None

def test_integration_simplified():
    """Prueba la integración simplificada del sistema"""
    print("\n🚀 PROBANDO INTEGRACIÓN SIMPLIFICADA")
    print("=" * 60)
    
    try:
        # Generar datos
        df = generar_datos_prueba()
        
        # Inicializar componentes disponibles
        from core.professional_learning_system import ProfessionalLearningSystem
        from core.market_structure_analyzer import MarketStructureAnalyzer
        from ai.llm_client import LLMClient
        
        learning_system = ProfessionalLearningSystem()
        structure_analyzer = MarketStructureAnalyzer()
        llm_client = LLMClient()
        
        print("🔄 Ejecutando flujo simplificado de análisis...")
        
        # 1. Análisis de estructura
        print("   1/3 Analizando estructura de mercado...")
        structure_analysis = structure_analyzer.analyze_full_context(df)
        
        # 2. Insights de aprendizaje
        print("   2/3 Obteniendo insights de aprendizaje...")
        learning_insights = learning_system.get_learning_insights()
        
        # 3. Preparar resúmenes para Ollama
        print("   3/3 Consultando Ollama...")
        
        # Preparar resúmenes
        market_summary = f"EURUSD: {df.iloc[-1]['close']:.5f} | RSI: {df.iloc[-1]['rsi']:.1f} | Fase: {structure_analysis.get('market_phase', 'N/A')}"
        
        smart_summary = "Smart Money: Análisis básico | Tendencia detectada | Confianza: 65%"
        
        learning_summary = "Sistema inicializándose" if 'error' in learning_insights else f"Lecciones: {learning_insights.get('total_lessons', 0)}"
        
        # Decisión final de Ollama
        final_decision = llm_client.analyze_complete_trading_opportunity(
            market_data_summary=market_summary,
            smart_money_analysis=smart_summary,
            learning_insights=learning_summary,
            asset="EURUSD",
            current_balance=1000.0
        )
        
        print("\n" + "=" * 60)
        print("🎯 DECISIÓN FINAL DEL SISTEMA SIMPLIFICADO")
        print("=" * 60)
        
        if final_decision.get('should_trade'):
            print(f"✅ EJECUTAR OPERACIÓN:")
            print(f"   Activo: EURUSD")
            print(f"   Dirección: {final_decision.get('direction')}")
            print(f"   Confianza: {final_decision.get('confidence', 0):.0f}%")
            print(f"   Razón principal: {final_decision.get('primary_reason', 'N/A')}")
            
            confluences = final_decision.get('confluences', [])
            if confluences:
                print(f"\n   Confluencias detectadas ({len(confluences)}):")
                for i, conf in enumerate(confluences[:3], 1):
                    print(f"     {i}. {conf}")
            
        else:
            print(f"⏸️ NO OPERAR:")
            print(f"   Razón: {final_decision.get('primary_reason', 'N/A')}")
            
            risks = final_decision.get('risk_factors', [])
            if risks:
                print(f"\n   Factores de riesgo identificados:")
                for i, risk in enumerate(risks[:3], 1):
                    print(f"     {i}. {risk}")
        
        print("\n✅ Prueba de integración simplificada exitosa!")
        return True
        
    except Exception as e:
        print(f"❌ Error en integración simplificada: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Función principal de pruebas"""
    print("🧪 INICIANDO PRUEBAS DEL SISTEMA IA ORQUESTADOR (SIMPLIFICADO)")
    print("=" * 70)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Ejecutar pruebas individuales
    results = {}
    
    results['learning'] = test_professional_learning() is not None
    results['structure'] = test_market_structure_analyzer() is not None
    results['llm'] = test_llm_integration() is not None
    results['integration'] = test_integration_simplified()
    
    # Resumen final
    print("\n" + "=" * 70)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 70)
    
    for test_name, passed in results.items():
        status = "✅ PASÓ" if passed else "❌ FALLÓ"
        print(f"{test_name.upper().replace('_', ' ')}: {status}")
    
    total_passed = sum(results.values())
    total_tests = len(results)
    
    print(f"\nResultado: {total_passed}/{total_tests} pruebas exitosas")
    
    if total_passed == total_tests:
        print("🎉 ¡TODAS LAS PRUEBAS PASARON! El sistema básico está listo.")
    else:
        print("⚠️ Algunas pruebas fallaron. Revisar configuración.")
    
    print("\n💡 Próximos pasos:")
    print("   1. Asegurar que Ollama esté ejecutándose en EasyPanel")
    print("   2. Verificar configuración en .env")
    print("   3. El sistema funcionará con análisis básico Smart Money")
    print("   4. Ejecutar el bot con: python main_modern.py")

if __name__ == "__main__":
    main()