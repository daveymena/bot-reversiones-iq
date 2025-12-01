import requests
import json

OLLAMA_URL = "https://davey-ollama2.mapf5v.easypanel.host/api/tags"

print(f"🔍 Consultando modelos en: {OLLAMA_URL}")

try:
    response = requests.get(OLLAMA_URL, timeout=10)
    if response.status_code == 200:
        models = response.json().get('models', [])
        print("\n✅ Modelos disponibles:")
        for model in models:
            print(f"   • {model['name']} ({model.get('size', 0) / 1024 / 1024 / 1024:.2f} GB)")
            
        # Buscar gemma o similar
        gemma_models = [m['name'] for m in models if 'gemma' in m['name'].lower() or 'gamin' in m['name'].lower()]
        if gemma_models:
            print(f"\n🎯 Posibles coincidencias para 'gamin': {gemma_models}")
    else:
        print(f"❌ Error {response.status_code}: {response.text}")
except Exception as e:
    print(f"❌ Error de conexión: {e}")
