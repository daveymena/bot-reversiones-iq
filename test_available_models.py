#!/usr/bin/env python3
"""
Test de velocidad para los modelos disponibles en Ollama
"""
import requests
import json
import time
from urllib3.exceptions import InsecureRequestWarning
import urllib3

# Desactivar warnings SSL
urllib3.disable_warnings(InsecureRequestWarning)

def test_model_speed(model_name, timeout=5):
    """Prueba la velocidad de un modelo específico"""
    
    base_url = "https://ollama-ollama.ginee6.easypanel.host"
    
    # Prompt simple para trading
    prompt = "EURUSD price 1.0850, RSI 65, MACD positive. Trade recommendation: CALL or PUT?"
    
    data = {
        "model": model_name,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1,
            "top_p": 0.9,
            "num_predict": 50  # Respuesta corta
        }
    }
    
    try:
        print(f"🧪 Probando {model_name} (timeout: {timeout}s)...")
        start_time = time.time()
        
        response = requests.post(
            f"{base_url}/api/generate",
            json=data,
            timeout=timeout,
            verify=False
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        if response.status_code == 200:
            result = response.json()
            answer = result.get('response', '').strip()
            
            print(f"   ✅ ÉXITO - {response_time:.2f}s")
            print(f"   📝 Respuesta: {answer[:100]}...")
            return response_time, True, answer
        else:
            print(f"   ❌ HTTP {response.status_code}: {response.text}")
            return None, False, None
            
    except requests.exceptions.Timeout:
        print(f"   ⏱️ TIMEOUT ({timeout}s)")
        return None, False, None
        
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return None, False, None

def main():
    """Prueba todos los modelos disponibles"""
    
    # Modelos disponibles según el check anterior
    available_models = [
        "llama3.2:1b",      # 1259.9 MB - más pequeño
        "gemma2:2b",        # 1554.0 MB
        "qwen2.5:3b",       # 1840.5 MB  
        "qwen2.5:7b"        # 4466.1 MB - más grande
    ]
    
    print("🚀 TEST DE VELOCIDAD - MODELOS DISPONIBLES")
    print("=" * 50)
    
    results = []
    
    # Probar cada modelo con timeout progresivo
    for model in available_models:
        # Empezar con timeout corto y aumentar si es necesario
        for timeout in [3, 5, 10]:
            response_time, success, answer = test_model_speed(model, timeout)
            
            if success:
                results.append({
                    'model': model,
                    'time': response_time,
                    'answer': answer
                })
                break
            elif timeout == 10:  # Último intento
                print(f"   ❌ {model} falló en todos los timeouts")
        
        print()
    
    # Mostrar resultados
    print("=" * 50)
    print("📊 RESULTADOS FINALES")
    print("=" * 50)
    
    if results:
        # Ordenar por velocidad
        results.sort(key=lambda x: x['time'])
        
        print("🏆 RANKING DE VELOCIDAD:")
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['model']}: {result['time']:.2f}s")
        
        # Recomendar el más rápido
        fastest = results[0]
        print(f"\n✅ MODELO MÁS RÁPIDO: {fastest['model']}")
        print(f"⚡ Tiempo: {fastest['time']:.2f}s")
        print(f"📝 Respuesta de ejemplo: {fastest['answer'][:150]}...")
        
        # Actualizar .env automáticamente
        print(f"\n🔧 ACTUALIZANDO .env con el modelo más rápido...")
        update_env_file(fastest['model'])
        
    else:
        print("❌ NINGÚN MODELO FUNCIONÓ")
        print("💡 Recomendación: Usar solo LocalAI (ultra-rápida)")

def update_env_file(best_model):
    """Actualiza el archivo .env con el mejor modelo"""
    try:
        # Leer .env actual
        with open('.env', 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Actualizar OLLAMA_MODEL
        updated = False
        for i, line in enumerate(lines):
            if line.startswith('OLLAMA_MODEL='):
                lines[i] = f'OLLAMA_MODEL={best_model}\n'
                updated = True
                break
        
        # Si no existe, agregarlo
        if not updated:
            lines.append(f'OLLAMA_MODEL={best_model}\n')
        
        # Escribir .env actualizado
        with open('.env', 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        print(f"✅ .env actualizado: OLLAMA_MODEL={best_model}")
        
    except Exception as e:
        print(f"❌ Error actualizando .env: {e}")

if __name__ == "__main__":
    main()