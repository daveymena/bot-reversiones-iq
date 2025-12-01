"""
Script para generar el ejecutable del cliente de escritorio
Ejecutar: python build_exe.py
"""
import subprocess
import sys

print("=" * 60)
print("GENERANDO EJECUTABLE DEL CLIENTE")
print("=" * 60)

# Comando PyInstaller
command = [
    'pyinstaller',
    '--onefile',
    '--windowed',  # Sin consola
    '--name=TradingBotClient',
    '--add-data=gui;gui',
    '--add-data=backend/api;backend/api',
    '--hidden-import=PySide6',
    '--hidden-import=requests',
    '--hidden-import=websockets',
    '--hidden-import=pyqtgraph',
    '--exclude-module=torch',
    '--exclude-module=tensorflow',
    '--exclude-module=stable_baselines3',
    'run_client.py'
]

print(f"\nEjecutando: {' '.join(command)}\n")

try:
    result = subprocess.run(command, check=True)
    print("\n" + "=" * 60)
    print("✅ EJECUTABLE GENERADO EXITOSAMENTE")
    print("=" * 60)
    print("Ubicación: dist/TradingBotClient.exe")
    print("\nPuedes distribuir este archivo de forma independiente.")
except subprocess.CalledProcessError as e:
    print(f"\n❌ Error: {e}")
    sys.exit(1)
