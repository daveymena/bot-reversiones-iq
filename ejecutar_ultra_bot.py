#!/usr/bin/env python3
"""
Script simplificado para ejecutar el Ultra-Smart Bot
"""
import os
import sys

print("=" * 70)
print("ULTRA-SMART TRADING BOT v2.0")
print("=" * 70)

# Verificar Python 3.8+
if sys.version_info < (3, 8):
    print("ERROR: Se requiere Python 3.8 o superior")
    sys.exit(1)

# Instalar dependencias si faltan
try:
    import pandas
    import numpy
    import sklearn
except ImportError as e:
    print(f"Instalando dependencias: {e}")
    os.system("pip install pandas numpy scikit-learn joblib")

try:
    import websockets
except ImportError:
    print("Instalando websockets...")
    os.system("pip install websockets")

print("\nIniciando Ultra-Smart Bot...")
print("-" * 70)

from ultra_smart_bot import main

if __name__ == "__main__":
    main()
