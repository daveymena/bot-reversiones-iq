"""
Script rápido para ejecutar el observador automáticamente
"""
import sys
sys.path.insert(0, '.')

from observe_market import MarketObserver

# Crear observador
observer = MarketObserver()

# Conectar
print("\n🔌 Conectando a Exnova...")
if not observer.connect():
    print("❌ No se pudo conectar")
    sys.exit(1)

# Buscar mejor oportunidad
print("\n🎯 Buscando mejor oportunidad en el mercado...")
best = observer.find_best_opportunity()

if best:
    print("\n" + "="*80)
    print("✅ ANÁLISIS COMPLETADO")
    print("="*80)
else:
    print("\n⚠️ No se encontraron oportunidades fuertes en este momento")
    print("💡 Esto es normal - el mercado no siempre tiene señales claras")

print("\n📊 Mostrando resumen de observaciones...")
observer.show_summary()
