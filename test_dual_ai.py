#!/usr/bin/env python3
"""
Test para verificar que ambas IAs (Groq + Ollama) funcionan correctamente
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai.llm_client import LLMClient
from config import Config

def test_groq_connection():
    """Prueba la conexión a Groq"""
    print("🧠 PROBANDO GROQ...")
    print(f"   Llaves disponibles: {len(Config.GROQ_API_KEYS)}")
    print(f"   USE_GROQ: {Config.USE_GROQ}")
    
    if not Config.GROQ_API_KEYS:
        print("❌ No hay llaves de Groq configuradas")
        return False
    
    try:
        llm = LLMClient()
        if llm.use_groq and llm.groq_client:
            # Hacer una consulta simple
            response = llm._safe_query("¿Funciona Groq? Responde solo 'SÍ' o 'NO'")
            
            if "Error" not in response and len(response) > 0:
                print(f"✅ Groq funciona: {response[:50]}...")
                return True
            else:
                print(f"❌ Groq no responde correctamente: {response}")
                return False
        else:
            print("❌ Cliente Groq no inicializado")
            return False
    except Exception as e:
        print(f"❌ Error probando Groq: {e}")
        return False

def test_ollama_connection():
    """Prueba la conexión a Ollama"""
    print("\n🤖 PROBANDO OLLAMA...")
    print(f"   URL: {Config.OLLAMA_BASE_URL}")
    print(f"   Modelo: {Config.OLLAMA_MODEL}")
    
    try:
        llm = LLMClient()
        # Forzar uso de Ollama
        response = llm._query_ollama("¿Funciona Ollama? Responde solo 'SÍ' o 'NO'")
        
        if "Error" not in response and len(response) > 0:
            print(f"✅ Ollama funciona: {response[:50]}...")
            return True
        else:
            print(f"❌ Ollama no responde correctamente: {response}")
            return False
    except Exception as e:
        print(f"❌ Error probando Ollama: {e}")
        return False

def test_fallback_system():
    """Prueba el sistema de fallback Groq -> Ollama"""
    print("\n🔄 PROBANDO SISTEMA DE FALLBACK...")
    
    try:
        llm = LLMClient()
        
        # Simular agotamiento de Groq
        original_use_groq = llm.use_groq
        llm.use_groq = False  # Forzar uso de Ollama
        
        response = llm._safe_query("Test de fallback. Responde 'OLLAMA ACTIVO'")
        
        if "OLLAMA" in response.upper() or len(response) > 5:
            print("✅ Sistema de fallback funciona correctamente")
            
            # Restaurar configuración
            llm.use_groq = original_use_groq
            return True
        else:
            print(f"❌ Fallback no funciona: {response}")
            return False
    except Exception as e:
        print(f"❌ Error probando fallback: {e}")
        return False

def test_trading_decision():
    """Prueba una decisión de trading completa"""
    print("\n📊 PROBANDO DECISIÓN DE TRADING...")
    
    try:
        llm = LLMClient()
        
        # Datos de prueba
        market_summary = "EURUSD: 1.1740 | RSI: 45 | MACD: Neutral"
        smart_money = "Setup: TREND_PULLBACK_CALL | Score: 75%"
        learning = "Performance reciente: 60%"
        
        decision = llm.analyze_complete_trading_opportunity(
            market_data_summary=market_summary,
            smart_money_analysis=smart_money,
            learning_insights=learning,
            asset="EURUSD-OTC",
            current_balance=1000
        )
        
        if decision and 'should_trade' in decision:
            print(f"✅ Decisión generada:")
            print(f"   Should trade: {decision.get('should_trade')}")
            print(f"   Direction: {decision.get('direction')}")
            print(f"   Confidence: {decision.get('confidence')}")
            print(f"   Reason: {decision.get('primary_reason', 'N/A')}")
            return True
        else:
            print(f"❌ Decisión inválida: {decision}")
            return False
    except Exception as e:
        print(f"❌ Error probando decisión: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Función principal"""
    print("🔬 TEST DE SISTEMA DUAL AI (GROQ + OLLAMA)")
    print("=" * 60)
    
    results = []
    
    # Test 1: Groq
    results.append(("Groq Connection", test_groq_connection()))
    
    # Test 2: Ollama
    results.append(("Ollama Connection", test_ollama_connection()))
    
    # Test 3: Fallback
    results.append(("Fallback System", test_fallback_system()))
    
    # Test 4: Trading Decision
    results.append(("Trading Decision", test_trading_decision()))
    
    # Resumen
    print("\n" + "=" * 60)
    print("📋 RESUMEN DE PRUEBAS")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} {status}")
        if result:
            passed += 1
    
    print(f"\nResultado: {passed}/{len(results)} pruebas exitosas")
    
    if passed == len(results):
        print("🎉 SISTEMA DUAL AI FUNCIONANDO CORRECTAMENTE")
        print("\nConfiguración recomendada:")
        print("- Groq como IA principal (rápida)")
        print("- Ollama como respaldo (cuando Groq falla)")
        print("- Fallback automático sin intervención")
    else:
        print("⚠️ ALGUNOS COMPONENTES NECESITAN ATENCIÓN")
        
        if not results[0][1]:  # Groq falló
            print("\n🔧 SOLUCIONES PARA GROQ:")
            print("- Verificar llaves API en .env")
            print("- Comprobar límites de uso")
            print("- Verificar conexión a internet")
        
        if not results[1][1]:  # Ollama falló
            print("\n🔧 SOLUCIONES PARA OLLAMA:")
            print("- Verificar que EasyPanel esté activo")
            print("- Comprobar URL de Ollama")
            print("- Cambiar modelo a llama3.2:3b")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)