"""
🎯 ANÁLISIS INTELIGENTE DE MERCADO EXNOVA
Genera reporte detallado de oportunidades de trading
"""
import sys
import json
from datetime import datetime
sys.path.insert(0, '.')

from observe_market import MarketObserver

def main():
    # Crear observador
    observer = MarketObserver()
    
    # Conectar
    print("\n" + "="*80)
    print("🔌 CONECTANDO A EXNOVA")
    print("="*80)
    
    if not observer.connect():
        print("❌ No se pudo conectar. Verifica tus credenciales en .env")
        return
    
    # Buscar mejor oportunidad
    print("\n" + "="*80)
    print("🔍 ESCANEANDO MERCADO EN BUSCA DE OPORTUNIDADES...")
    print("="*80)
    print("Esto tomará aproximadamente 1-2 minutos...")
    print()
    
    best = observer.find_best_opportunity()
    
    # Mostrar resumen
    print("\n" + "="*80)
    print("📊 RESUMEN DEL ANÁLISIS")
    print("="*80)
    observer.show_summary()
    
    # Guardar reporte
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"data/market_report_{timestamp}.json"
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'total_observations': len(observer.observations),
        'total_opportunities': len(observer.opportunities_found),
        'best_opportunity': best,
        'all_observations': observer.observations,
        'all_opportunities': observer.opportunities_found
    }
    
    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, default=str)
        print(f"\n💾 Reporte guardado en: {report_file}")
    except Exception as e:
        print(f"\n⚠️ No se pudo guardar el reporte: {e}")
    
    # Recomendaciones finales
    print("\n" + "="*80)
    print("💡 RECOMENDACIONES PARA EL BOT")
    print("="*80)
    
    if observer.opportunities_found:
        print(f"\n✅ Se encontraron {len(observer.opportunities_found)} oportunidades")
        print("\n📋 Activos más prometedores:")
        
        # Agrupar por activo
        by_asset = {}
        for opp in observer.opportunities_found:
            asset = opp['asset']
            if asset not in by_asset:
                by_asset[asset] = []
            by_asset[asset].append(opp)
        
        # Ordenar por cantidad de oportunidades
        sorted_assets = sorted(by_asset.items(), key=lambda x: len(x[1]), reverse=True)
        
        for asset, opps in sorted_assets[:3]:  # Top 3
            avg_strength = sum(o['signal_strength'] for o in opps) / len(opps)
            actions = [o['action'] for o in opps]
            most_common_action = max(set(actions), key=actions.count)
            
            print(f"\n   {asset}:")
            print(f"      Oportunidades: {len(opps)}")
            print(f"      Fuerza promedio: {avg_strength:.0f}/100")
            print(f"      Acción recomendada: {most_common_action}")
        
        print("\n💡 Configuración recomendada para el bot:")
        print(f"   - Activos prioritarios: {', '.join([a for a, _ in sorted_assets[:3]])}")
        print(f"   - Timeframe: 1 minuto (60 segundos)")
        print(f"   - Expiración: 1-2 minutos")
        print(f"   - Filtro de señal mínima: 40/100")
        
    else:
        print("\n⚠️ No se encontraron oportunidades fuertes en este momento")
        print("\n💡 Esto puede significar:")
        print("   - El mercado está en consolidación (lateral)")
        print("   - Baja volatilidad actual")
        print("   - Esperar a sesiones de mayor liquidez")
        print("\n📅 Mejores horarios para operar (UTC):")
        print("   - 07:00-12:00 (Sesión Londres)")
        print("   - 12:00-18:00 (Overlap Londres-NY)")
        print("   - 19:00-23:00 (Sesión Asia)")
    
    print("\n" + "="*80)
    print("✅ ANÁLISIS COMPLETADO")
    print("="*80)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Análisis interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
