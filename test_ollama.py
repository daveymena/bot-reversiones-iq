"""
Test de Conexión Ollama
Verifica que se pueda conectar al servidor remoto y usar los modelos configurados.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from ai.llm_client import LLMClient

print("=" * 60)
print("📡 TEST: CONEXIÓN OLLAMA")
print(f"URL: {Config.OLLAMA_URL}")
print(f"Modelo Default: {Config.OLLAMA_MODEL}")
print(f"Modelo Rápido: {getattr(Config, 'OLLAMA_MODEL_FAST', 'N/A')}")
print("=" * 60)

client = LLMClient()
client.use_groq = False # Forzar uso de Ollama para este test

print("\n1️⃣ Probando Modelo Rápido (Market Analysis)...")
try:
    response = client.analyze_market("RSI: 30, Tendencia: Alcista, Precio en soporte")
    print(f"✅ Respuesta recibida ({len(response)} chars):")
    print(f"   {response[:100]}...")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n2️⃣ Probando Modelo Principal (Consenso)...")
try:
    # Simular llamada a consenso (usa modelo default por defecto en _query_ollama si no se especifica fast)
    # Nota: get_consensus_decision llama a _query_ollama sin use_fast_model=True
    response = client.get_consensus_decision("RSI: 70, Tendencia: Bajista", "EURUSD")
    print(f"✅ Respuesta recibida (Consenso): {response['consensus']}")
    print(f"   Confianza: {response['confidence']}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 60)
