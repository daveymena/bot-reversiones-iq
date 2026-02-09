#!/usr/bin/env python3
"""
Script para verificar qué modelos están disponibles en Ollama
"""
import requests
import json
from urllib3.exceptions import InsecureRequestWarning
import urllib3

# Desactivar warnings SSL
urllib3.disable_warnings(InsecureRequestWarning)

def check_available_models():
    """Verifica qué modelos están disponibles en Ollama"""
    
    base_url = "https://ollama-ollama.ginee6.easypanel.host"
    
    print("🔍 VERIFICANDO MODELOS DISPONIBLES EN OLLAMA")
    print("=" * 60)
    print(f"URL: {base_url}")
    print("=" * 60)
    
    try:
        # Verificar conexión básica
        print("🔗 Verificando conexión...")
        response = requests.get(f"{base_url}/api/tags", 
                              timeout=10, 
                              verify=False)
        
        if response.status_code == 200:
            data = response.json()
            models = data.get('models', [])
            
            print(f"✅ Conexión exitosa!")
            print(f"📊 Modelos encontrados: {len(models)}")
            print("-" * 40)
            
            if models:
                for i, model in enumerate(models, 1):
                    name = model.get('name', 'Sin nombre')
                    size = model.get('size', 0)
                    size_mb = size / (1024 * 1024) if size > 0 else 0
                    modified = model.get('modified_at', 'Desconocido')
                    
                    print(f"{i}. {name}")
                    print(f"   Tamaño: {size_mb:.1f} MB")
                    print(f"   Modificado: {modified}")
                    print()
                
                # Encontrar el modelo más pequeño
                smallest = min(models, key=lambda x: x.get('size', float('inf')))
                print("🏆 MODELO MÁS PEQUEÑO (RECOMENDADO):")
                print(f"   Nombre: {smallest.get('name')}")
                print(f"   Tamaño: {smallest.get('size', 0) / (1024 * 1024):.1f} MB")
                
            else:
                print("❌ No se encontraron modelos instalados")
                print("\n💡 SOLUCIONES:")
                print("1. Instalar un modelo pequeño en EasyPanel:")
                print("   docker exec ollama ollama pull phi3:mini")
                print("   docker exec ollama ollama pull qwen2:0.5b")
                print("2. O usar solo la IA local (LocalAI)")
                
        else:
            print(f"❌ Error HTTP {response.status_code}: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏱️ TIMEOUT - El servidor no responde")
        print("💡 Posible solución: Usar solo LocalAI (ultra-rápida)")
        
    except requests.exceptions.ConnectionError:
        print("❌ ERROR DE CONEXIÓN")
        print("💡 Verificar que EasyPanel esté funcionando")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    check_available_models()