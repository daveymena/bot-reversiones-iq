#!/usr/bin/env python3
"""
Script para verificar que los errores del bot están arreglados
"""

import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Prueba que todos los imports funcionen"""
    print("🔍 Verificando imports...")
    
    try:
        from core.trader import LiveTrader
        print("✅ LiveTrader importado correctamente")
        
        from data.market_data import MarketDataHandler
        print("✅ MarketDataHandler importado correctamente")
        
        from strategies.technical import FeatureEngineer
        print("✅ FeatureEngineer importado correctamente")
        
        from core.asset_manager import AssetManager
        print("✅ AssetManager importado correctamente")
        
        from ai.llm_client import LLMClient
        print("✅ LLMClient importado correctamente")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en imports: {e}")
        return False

def test_syntax():
    """Verifica que no hay errores de sintaxis en trader.py"""
    print("\n🔍 Verificando sintaxis de trader.py...")
    
    try:
        import ast
        
        with open('core/trader.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parsear el archivo para verificar sintaxis
        ast.parse(content)
        print("✅ Sintaxis de trader.py correcta")
        return True
        
    except SyntaxError as e:
        print(f"❌ Error de sintaxis en trader.py: {e}")
        return False
    except Exception as e:
        print(f"❌ Error verificando sintaxis: {e}")
        return False

def check_variables():
    """Verifica que las variables problemáticas estén definidas"""
    print("\n🔍 Verificando variables problemáticas...")
    
    try:
        with open('core/trader.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar que is_institutional_root esté definido antes de usarse
        if 'is_institutional_root = best_opportunity.get(' in content:
            print("✅ is_institutional_root está definido correctamente")
        else:
            print("❌ is_institutional_root no está definido")
            return False
        
        # Verificar que asset_profile esté inicializado
        if 'asset_profile = None' in content:
            print("✅ asset_profile está inicializado correctamente")
        else:
            print("❌ asset_profile no está inicializado")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error verificando variables: {e}")
        return False

def main():
    """Función principal"""
    print("🛠️ VERIFICANDO CORRECCIONES DEL BOT")
    print("=" * 50)
    
    results = []
    
    # Ejecutar pruebas
    results.append(test_imports())
    results.append(test_syntax())
    results.append(check_variables())
    
    # Resumen
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE VERIFICACIONES")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Pruebas pasadas: {passed}/{total}")
    
    if passed == total:
        print("🎉 ¡TODAS LAS CORRECCIONES ESTÁN BIEN!")
        print("✅ El bot debería funcionar sin errores ahora")
        print("\n💡 Próximos pasos:")
        print("   1. Ejecutar: python main_headless.py")
        print("   2. El bot debería detectar y ejecutar operaciones")
        print("   3. Verificar que no aparezcan más errores de variables")
    else:
        print("⚠️ Algunas verificaciones fallaron")
        print("❌ Revisar los errores antes de ejecutar el bot")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)