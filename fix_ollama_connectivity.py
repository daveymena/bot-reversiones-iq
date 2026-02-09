#!/usr/bin/env python3
"""
Solución definitiva para problemas de conectividad de Ollama
"""

import sys
import os
import json
import time
import requests
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_ollama_connectivity():
    """Prueba la conectividad con Ollama y diagnostica problemas"""
    print("🔍 DIAGNÓSTICO DE CONECTIVIDAD OLLAMA")
    print("=" * 60)
    
    from config import Config
    
    print(f"📡 URL: {Config.OLLAMA_BASE_URL}")
    print(f"🤖 Modelo: {Config.OLLAMA_MODEL}")
    
    # 1. Probar conectividad básica
    print("\