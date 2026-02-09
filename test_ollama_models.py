#!/usr/bin/env python3
"""
Test de velocidad de diferentes modelos de Ollama
Encuentra el modelo más rápido para trading
"""

import requests
import time
import json
from config import Config

def test_ollama_model(model_name, timeout=15):
    """Prueba un modelo específico de Ollama"""
    
    print(f"\n🧪 Probando modelo: {model_name}")
    
    try:
        payload = {
            'model': model_name,
            'prompt': 'Trading EURUSD: RSI 25. Responde: CALL/PUT/HOLD',
            'stream': False,
            'options': {
                'temperature': 0.1,
                'num_ctx': 256,  # Contexto mínimo para velocidad
                'top_p': 0.9,
                'repeat_penalty': 1.1
            }
        }
        
        start_time = time.time()
        
        response = requests.post(
            Config.OLLAMA_URL, 
            json=payload, 
            timeout=timeout, 
            verify=False
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        if response.status_code == 200:
            result = response.json()
            ollama_response = result.get('response', '')
            
            # Verificar que la respuesta sea útil
            if len(ollama_response.strip()) > 0:
                print(f"   ✅ FUNCIONA - Tiempo: {response_time:.2f}s")
                print(f"   📝 Respuesta: {ollama_response[:100]}...")
                
                # Verificar si contiene decisión de trading
                has_decision = any(word in ollama_response.upper() for word in ['CALL', 'PUT', 'HOLD', 'BUY', 'SELL'])
                
                return {
                    'model': model_name,
                    'status': 'success',
                    'response_time': response_time,
                    'response_length': len(ollama_response),
                    'has_trading_decision': has_decision,
                    'response': ollama_response[:200]
                }
            else:
                print(f"   ❌ Respuesta vacía")
                return {'model': model_name, 'status': 'empty_response'}
        else:
            print(f"   ❌ HTTP {response.status_code}: {response.text[:100]}")
            return {'model': model_name, 'status': f'http_error_{response.status_code}'}
            
    except requests.exceptions.Timeout:
        print(f"   ⏱️ TIMEOUT ({timeout}s)")
        return {'model': model_name, 'status': 'timeout'}
    except requests.exceptions.ConnectionError:
        print(f"   🔌 CONNECTION ERROR")
        return {'model': model_name, 'status': 'connection_error'}
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)[:100]}")
        return {'model': model_name, 'status': f'error: {str(e)[:50]}'}

def main():
    """Función principal"""
    
    print("🚀 TEST DE VELOCIDAD DE MODELOS OLLAMA")
    print("=" * 60)
    print(f"URL Base: {Config.OLLAMA_BASE_URL}")
    print("=" * 60)
    
    # Lista de modelos a probar (del más pequeño al más grande)
    models_to_test = [
        # Modelos ultra-pequeños (más rápidos)
        "phi3:mini",           # Microsoft Phi-3 Mini (3.8B)
        "phi3:3.8b",          # Microsoft Phi-3 (3.8B)
        "qwen2:0.5b",         # Qwen2 0.5B (ultra-pequeño)
        "qwen2:1.5b",         # Qwen2 1.5B
        "gemma2:2b",          # Google Gemma2 2B
        
        # Modelos pequeños
        "llama3.2:1b",        # Actual (Llama 3.2 1B)
        "llama3.2:3b",        # Llama 3.2 3B
        "mistral:7b",         # Mistral 7B
        "codellama:7b",       # Code Llama 7B
        
        # Modelos medianos (más lentos pero mejores)
        "llama3.1:8b",        # Llama 3.1 8B
        "qwen2:7b",           # Qwen2 7B
        "gemma2:9b",          # Google Gemma2 9B
    ]
    
    results = []
    
    for model in models_to_test:
        try:
            result = test_ollama_model(model, timeout=20)
            results.append(result)
            
            # Pausa entre tests para no saturar
            time.sleep(2)
            
        except KeyboardInterrupt:
            print("\n🛑 Test interrumpido por usuario")
            break
    
    # Analizar resultados
    print("\n" + "=" * 60)
    print("📊 RESULTADOS DEL TEST")
    print("=" * 60)
    
    successful_models = [r for r in results if r.get('status') == 'success']
    
    if successful_models:
        # Ordenar por velocidad
        successful_models.sort(key=lambda x: x['response_time'])
        
        print("\n🏆 MODELOS QUE FUNCIONAN (ordenados por velocidad):")
        print("-" * 60)
        
        for i, model in enumerate(successful_models, 1):
            speed_emoji = "⚡" if model['response_time'] < 5 else "🐌" if model['response_time'] > 15 else "🚀"
            decision_emoji = "🎯" if model['has_trading_decision'] else "❓"
            
            print(f"{i}. {speed_emoji} {model['model']}")
            print(f"   ⏱️ Tiempo: {model['response_time']:.2f}s")
            print(f"   📏 Longitud: {model['response_length']} chars")
            print(f"   {decision_emoji} Decisión trading: {'Sí' if model['has_trading_decision'] else 'No'}")
            print(f"   💬 Muestra: {model['response'][:80]}...")
            print()
        
        # Recomendación
        fastest = successful_models[0]
        print("🎯 RECOMENDACIÓN:")
        print(f"   Modelo más rápido: {fastest['model']}")
        print(f"   Tiempo de respuesta: {fastest['response_time']:.2f}s")
        
        if fastest['response_time'] < 10:
            print("   ✅ EXCELENTE para trading en tiempo real")
        elif fastest['response_time'] < 20:
            print("   ⚠️ ACEPTABLE para trading (un poco lento)")
        else:
            print("   ❌ DEMASIADO LENTO para trading")
        
        # Generar configuración
        print(f"\n🔧 CONFIGURACIÓN RECOMENDADA:")
        print(f"   Cambiar en .env:")
        print(f"   VITE_OLLAMA_MODEL={fastest['model']}")
        
    else:
        print("❌ NINGÚN MODELO FUNCIONÓ")
        print("\nPosibles problemas:")
        print("- EasyPanel está apagado")
        print("- URL de Ollama incorrecta")
        print("- Modelos no instalados")
        print("- Servidor sobrecargado")
    
    # Mostrar errores
    failed_models = [r for r in results if r.get('status') != 'success']
    if failed_models:
        print(f"\n❌ MODELOS QUE FALLARON ({len(failed_models)}):")
        print("-" * 40)
        
        error_counts = {}
        for model in failed_models:
            status = model['status']
            if status not in error_counts:
                error_counts[status] = []
            error_counts[status].append(model['model'])
        
        for error, models in error_counts.items():
            print(f"   {error}: {', '.join(models)}")
    
    print("\n" + "=" * 60)
    print("✅ Test completado")
    
    return successful_models

if __name__ == "__main__":
    try:
        results = main()
    except KeyboardInterrupt:
        print("\n🛑 Test interrumpido")
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()