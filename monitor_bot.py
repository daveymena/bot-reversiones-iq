"""
Monitor en tiempo real del bot de trading
Muestra cuando detecta oportunidades y la lógica aplicada
"""
import time
import json
from pathlib import Path
from datetime import datetime

def monitor_bot():
    db_path = Path("data/learning_database.json")
    last_ops_count = 0
    
    print("🔍 MONITOR DE BOT ACTIVO")
    print("=" * 80)
    print("Esperando operaciones del bot...")
    print("Presiona Ctrl+C para detener")
    print("=" * 80)
    
    try:
        while True:
            if db_path.exists():
                with open(db_path, 'r', encoding='utf-8') as f:
                    db = json.load(f)
                
                ops = db.get('operations', [])
                current_count = len(ops)
                
                # Si hay nuevas operaciones
                if current_count > last_ops_count:
                    new_ops = ops[last_ops_count:]
                    
                    for op in new_ops:
                        print(f"\n{'='*80}")
                        print(f"🆕 NUEVA OPERACIÓN DETECTADA")
                        print(f"{'='*80}")
                        print(f"⏰ Tiempo: {op.get('timestamp', 'N/A')}")
                        print(f"📊 Activo: {op.get('asset', 'N/A')}")
                        
                        strat = op.get('strategy', {})
                        print(f"🎯 Acción: {strat.get('action', 'N/A')}")
                        print(f"📈 Estrategia: {strat.get('strategy', 'N/A')}")
                        print(f"💯 Confianza: {strat.get('confidence', 0):.1f}%")
                        print(f"📝 Razón: {strat.get('reason', 'N/A')}")
                        
                        # Mostrar contexto MTF
                        mtf = op.get('mtf_context', {})
                        if mtf:
                            print(f"\n🌍 CONTEXTO HTF:")
                            print(f"   M30: {mtf.get('trend_m30', 'N/A')}")
                            print(f"   M15: {mtf.get('trend_m15', 'N/A')}")
                        
                        # Mostrar si está ejecutada
                        if op.get('executed'):
                            print(f"\n✅ EJECUTADA: Esperando resultado...")
                        else:
                            print(f"\n⏸️ NO EJECUTADA: Filtros bloquearon la entrada")
                        
                        # Resultado si está disponible
                        result = op.get('result', 'pending')
                        if result != 'pending':
                            emoji = "✅" if result == 'win' else "❌" if result == 'loose' else "⚪"
                            print(f"\n{emoji} RESULTADO: {result.upper()}")
                            profit = op.get('profit', 0)
                            print(f"💰 Profit: ${profit:.2f}")
                    
                    last_ops_count = current_count
            
            time.sleep(5)  # Revisar cada 5 segundos
            
    except KeyboardInterrupt:
        print("\n\n🛑 Monitor detenido por el usuario")

if __name__ == "__main__":
    monitor_bot()
