#!/usr/bin/env python3
"""
Test del Sistema de IA Orquestador Completo
Prueba todos los componentes del nuevo sistema inteligente
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.smart_money_analyzer import SmartMoneyAnalyzer
from core.professional_learning_system import ProfessionalLearningSystem, TradingConcept, MarketPhase
from core.market_structure_analyzer import MarketStructureAnalyzer
from ai.llm_client import LLMClient
from config import Config

def generar_datos_prueba():
    """Genera datos de prueba realistas"""
    print("📊 Generando datos de prueba...")
    
    # Generar 200 velas de EURUSD
    np.random.seed(42)
    
    dates = pd.date_range(start='2024-01-01', periods=200, freq='1min')
    
    # Precio base
    base_price = 1.0850
    
    # Generar movimiento de precio realista
    returns = np.random.normal(0, 0.0001, 200)
    returns[50:70] = np.random.normal(0.0002, 0.0001, 20)  # Tendencia alcista
    returns[120:140] = np.random.normal(-0.0002, 0.0001, 20)  # Tendencia bajista
    
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

def test_smart_money_analyzer():
    """Prueba el analizador Smart Money"""
    print("\n🧠 PROBANDO SMART MONEY ANALYZER")
    print("=" * 50)
    
    try:
        analyzer = SmartMoneyAnalyzer()
        df = generar_datos_prueba()
        
        print("📊 Analizando estructura Smart Money...")
        analysis = analyzer.analyze_smart_money_structure(df)
        
        print(f"✅ Análisis completado")
        print(f"   Order Blocks detectados: {len(analysis.get('order_blocks', []))}")
        print(f"   Fair Value Gaps: {len(analysis.get('fair_value_gaps', []))}")
        print(f"   Zonas de liquidez: {len(analysis.get('liquidity_zones', []))}")
        
        bias = analysis.get('directional_bias', {})
        print(f"   Bias direccional: {bias.get('bias', 'N/A')} ({bias.get('confidence', 0):.0f}%)")
        
        entry_signal = analysis.get('entry_signal', {})
        if entry_signal.get('should_enter'):
            print(f"   🎯 SEÑAL: {entry_signal.get('direction')} con {entry_signal.get('confidence', 0):.0f}% confianza")
        else:
            print(f"   ⏳ Sin señal de entrada clara")
        
        return analysis
        
    except Exception as e:
        print(f"❌ Error en Smart Money Analyzer: {e}")
        return None

def test_professional_learning():
    """Prueba el sistema de aprendizaje profesional"""
    print("\n🎓 PROBANDO SISTEMA DE APRENDIZAJE PROFESIONAL")
    print("=" * 50)
    
    try:
        learning_system = ProfessionalLearningSystem()
        
        # Simular algunas lecciones
        print("📚 Simulando lecciones de trading...")
        
        # Lección 1: Order Block exitoso
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
        
        # Lección 2: FVG fallido
        trade_data['direction'] = 'put'
        market_analysis['fair_value_gaps'] = [{'type': 'bearish_fvg', 'filled': False}]
        market_analysis['market_phase'] = 'distribution'
        result = {'won': False, 'profit': -10}
        
        lesson2 = learning_system.analyze_trade_for_learning(trade_data, market_analysis, result)
        if lesson2:
            print(f"✅ Lección 2: {lesson2.concept.value} en {lesson2.market_phase.value}")
        
        # Obtener insights
        print("\n📊 Obteniendo insights de aprendizaje...")
        insights = learning_system.get_learning_insights()
        
        if 'error' not in insights:
            print(f"   Total lecciones: {insights.get('total_lessons', 0)}")
            print(f"   Conceptos aprendidos: {insights.get('concepts_learned', 0)}")
            
            best_concepts = insights.get('best_concepts', [])
            if best_concepts:
                print(f"   Mejor concepto: {best_concepts[0]['concept']} ({best_concepts[0]['success_rate']:.1%})")
        
        return learning_system
        
    except Exception as e:
        print(f"❌ Error en Sistema de Aprendizaje: {e}")
        return None

def test_market_structure_analyzer():
    """Prueba el analizador de estructura de mercado"""
    print("\n📊 PROBANDO ANALIZADOR DE ESTRUCTURA DE MERCADO")
    print("=" * 50)
    
    try:
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
            
            reasons = entry_signal.get('reasons', [])
            if reasons:
                print(f"   Razones: {', '.join(reasons[:2])}")
        else:
            print(f"   ⏳ Esperando mejor momento")
            
            warnings = entry_signal.get('warnings', [])
            if warnings:
                print(f"   Advertencias: {', '.join(warnings[:2])}")
        
        return analysis
        
    except Exception as e:
        print(f"❌ Error en Analizador de Estructura: {e}")
        return None

def test_llm_integration():
    """Prueba la integración con Ollama"""
    print("\n🧠 PROBANDO INTEGRACIÓN CON OLLAMA")
    print("=" * 50)
    
    try:
        llm_client = LLMClient()
        
        # Preparar datos de prueba
        market_summary = "EURUSD: 1.0850 | RSI: 28 (Sobreventa) | MACD: Alcista | Fase: Accumulation"
        smart_money_summary = "Order Block fresco detectado | Bias: BULLISH (85%) | BOS alcista confirmado"
        learning_summary = "Performance reciente: 72% | Mejor concepto: ORDER_BLOCK (78%)"
        
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
            
            risks = decision.get('risk_factors', [])
            if risks:
                print(f"   Riesgos identificados: {len(risks)}")
        
        return decision
        
    except Exception as e:
        print(f"❌ Error en integración Ollama: {e}")
        print("   Nota: Asegúrate de que Ollama esté ejecutándose en EasyPanel")
        return None

def test_integration_complete():
    """Prueba la integración completa del sistema"""
    print("\n🚀 PROBANDO INTEGRACIÓN COMPLETA")
    print("=" * 60)
    
    try:
        # Generar datos
        df = generar_datos_prueba()
        
        # Inicializar componentes
        smart_money = SmartMoneyAnalyzer()
        learning_system = ProfessionalLearningSystem()
        structure_analyzer = MarketStructureAnalyzer()
        llm_client = LLMClient()
        
        print("🔄 Ejecutando flujo completo de análisis...")
        
        # 1. Análisis Smart Money
        print("   1/4 Analizando Smart Money...")
        smart_analysis = smart_money.analyze_smart_money_structure(df)
        
        # 2. Análisis de estructura
        print("   2/4 Analizando estructura de mercado...")
        structure_analysis = structure_analyzer.analyze_full_context(df)
        
        # 3. Insights de aprendizaje
        print("   3/4 Obteniendo insights de aprendizaje...")
        learning_insights = learning_system.get_learning_insights()
        
        # 4. Preparar resúmenes para Ollama
        print("   4/4 Consultando Ollama...")
        
        # Simular preparación de resúmenes (normalmente se haría en trader.py)
        market_summary = f"EURUSD: {df.iloc[-1]['close']:.5f} | RSI: {df.iloc[-1]['rsi']:.1f} | Fase: {structure_analysis.get('market_phase', 'N/A')}"
        
        bias = smart_analysis.get('directional_bias', {})
        smart_summary = f"Bias: {bias.get('bias', 'neutral').upper()} ({bias.get('confidence', 0):.0f}%) | Order Blocks: {len(smart_analysis.get('order_blocks', []))}"
        
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
        print("🎯 DECISIÓN FINAL DEL SISTEMA COMPLETO")
        print("=" * 60)
        
        if final_decision.get('should_trade'):
            print(f"✅ EJECUTAR OPERACIÓN:")
            print(f"   Activo: EURUSD")
            print(f"   Dirección: {final_decision.get('direction')}")
            print(f"   Confianza: {final_decision.get('confidence', 0):.0f}%")
            print(f"   Tamaño posición: ${final_decision.get('position_size', 0):.2f}")
            print(f"   Razón principal: {final_decision.get('primary_reason', 'N/A')}")
            
            confluences = final_decision.get('confluences', [])
            if confluences:
                print(f"\n   Confluencias detectadas ({len(confluences)}):")
                for i, conf in enumerate(confluences, 1):
                    print(f"     {i}. {conf}")
            
            print(f"\n   Calidad del timing: {final_decision.get('timing_quality', 'N/A')}")
            print(f"   Resultado esperado: {final_decision.get('expected_outcome', 'N/A')}")
            
        else:
            print(f"⏸️ NO OPERAR:")
            print(f"   Razón: {final_decision.get('primary_reason', 'N/A')}")
            
            risks = final_decision.get('risk_factors', [])
            if risks:
                print(f"\n   Factores de riesgo identificados:")
                for i, risk in enumerate(risks, 1):
                    print(f"     {i}. {risk}")
        
        print("\n✅ Prueba de integración completa exitosa!")
        return True
        
    except Exception as e:
        print(f"❌ Error en integración completa: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Función principal de pruebas"""
    print("🧪 INICIANDO PRUEBAS DEL SISTEMA IA ORQUESTADOR")
    print("=" * 60)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Configuración Ollama: {Config.OLLAMA_MODEL} @ {Config.OLLAMA_BASE_URL}")
    print("=" * 60)
    
    # Ejecutar pruebas individuales
    results = {}
    
    results['smart_money'] = test_smart_money_analyzer() is not None
    results['learning'] = test_professional_learning() is not None
    results['structure'] = test_market_structure_analyzer() is not None
    results['llm'] = test_llm_integration() is not None
    results['integration'] = test_integration_complete()
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ PASÓ" if passed else "❌ FALLÓ"
        print(f"{test_name.upper().replace('_', ' ')}: {status}")
    
    total_passed = sum(results.values())
    total_tests = len(results)
    
    print(f"\nResultado: {total_passed}/{total_tests} pruebas exitosas")
    
    if total_passed == total_tests:
        print("🎉 ¡TODAS LAS PRUEBAS PASARON! El sistema está listo.")
    else:
        print("⚠️ Algunas pruebas fallaron. Revisar configuración.")
    
    print("\n💡 Próximos pasos:")
    print("   1. Asegurar que Ollama esté ejecutándose en EasyPanel")
    print("   2. Verificar configuración en .env")
    print("   3. Ejecutar el bot con: python main_modern.py")

if __name__ == "__main__":
    main()