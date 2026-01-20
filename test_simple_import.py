#!/usr/bin/env python3
"""
Test simple de importación
"""

import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("Probando importaciones...")

try:
    print("1. Importando SmartMoneyAnalyzer...")
    from core.smart_money_analyzer import SmartMoneyAnalyzer
    print("   ✅ SmartMoneyAnalyzer importado correctamente")
    
    # Crear instancia
    analyzer = SmartMoneyAnalyzer()
    print("   ✅ Instancia creada correctamente")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

try:
    print("2. Importando ProfessionalLearningSystem...")
    from core.professional_learning_system import ProfessionalLearningSystem
    print("   ✅ ProfessionalLearningSystem importado correctamente")
    
    # Crear instancia
    learning = ProfessionalLearningSystem()
    print("   ✅ Instancia creada correctamente")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

try:
    print("3. Importando LLMClient...")
    from ai.llm_client import LLMClient
    print("   ✅ LLMClient importado correctamente")
    
    # Crear instancia
    llm = LLMClient()
    print("   ✅ Instancia creada correctamente")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\nTest de importaciones completado.")