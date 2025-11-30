"""
Test de Super Inteligencia
Verifica KnowledgeBase, Consenso Multi-Agente y Pre-Trade Analysis
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from core.knowledge_base import KnowledgeBase
from core.trade_intelligence import TradeIntelligence
from ai.llm_client import LLMClient

print("=" * 60)
print("🧪 TEST: SUPER INTELIGENCIA")
print("=" * 60)

# 1. Test KnowledgeBase
print("\n1️⃣ Test KnowledgeBase...")
try:
    kb = KnowledgeBase("tests/test_kb.json")
    
    # Crear contexto simulado
    context = {
        'rsi': 25,
        'macd': -0.005,
        'bb_position': 'LOWER',
        'trend': 'UPTREND',
        'momentum': 'BULLISH',
        'volatility': 'NORMAL'
    }
    
    # Guardar experiencia ganadora
    print("   Guardando experiencia ganadora...")
    kb.add_experience(context, {'won': True, 'profit': 8.5}, {'reason': 'Test'})
    
    # Guardar experiencia perdedora (contexto diferente)
    context_loss = context.copy()
    context_loss['rsi'] = 50
    print("   Guardando experiencia perdedora...")
    kb.add_experience(context_loss, {'won': False, 'profit': -10}, {'reason': 'Test'})
    
    # Buscar similares
    print("   Buscando similares...")
    analysis = kb.get_win_probability(context)
    print(f"   Probabilidad: {analysis['probability']:.2f}")
    print(f"   Consejo: {analysis['advice']}")
    
    assert analysis['probability'] == 1.0, "Debería ser 100% win rate para este contexto exacto"
    print("✅ KnowledgeBase funciona correctamente")
    
except Exception as e:
    print(f"❌ Error en KnowledgeBase: {e}")
    import traceback
    traceback.print_exc()

# 2. Test Pre-Trade Analysis (Mocked LLM)
print("\n2️⃣ Test Pre-Trade Analysis...")
try:
    # Mock LLM Client
    class MockLLMClient:
        def get_consensus_decision(self, market_summary, asset):
            return {
                'consensus': 'CALL',
                'confidence': 0.9,
                'votes': {'strategist': 'CALL', 'sniper': 'CALL', 'risk_manager': 'CALL'},
                'reasoning': 'Consenso simulado perfecto'
            }
            
    ti = TradeIntelligence(llm_client=MockLLMClient())
    ti.knowledge_base = kb # Usar la KB de prueba
    
    # DataFrame simulado
    df = pd.DataFrame({
        'close': [1.0, 1.1, 1.2],
        'rsi': [25, 25, 25],
        'macd': [-0.005, -0.005, -0.005],
        'atr': [0.001, 0.001, 0.001],
        'sma_20': [1.0, 1.0, 1.0],
        'sma_50': [0.9, 0.9, 0.9],
        'bb_low': [1.2, 1.2, 1.2],
        'bb_high': [1.3, 1.3, 1.3]
    })
    
    print("   Evaluando oportunidad...")
    analysis = ti.evaluate_trade_opportunity(df, "EURUSD", "CALL")
    
    print(f"   Aprobado: {analysis['approved']}")
    print(f"   Razón: {analysis['reason']}")
    
    assert analysis['approved'] == True, "Debería aprobar con consenso positivo y memoria positiva"
    print("✅ Pre-Trade Analysis funciona correctamente")

except Exception as e:
    print(f"❌ Error en Pre-Trade Analysis: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("✅ TESTS COMPLETADOS")
print("=" * 60)
