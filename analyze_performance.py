import json
from pathlib import Path

# Cargar base de datos
db_path = Path("data/learning_database.json")
if not db_path.exists():
    print("❌ No se encontró la base de datos de aprendizaje")
    exit(1)

with open(db_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

ops = data.get('operations', [])
total = len(ops)
wins = len([o for o in ops if o.get('result') == 'win'])
losses = len([o for o in ops if o.get('result') == 'loose'])
pending = len([o for o in ops if o.get('result') == 'pending'])

print("="*60)
print("📊 ANÁLISIS DE RENDIMIENTO DEL BOT")
print("="*60)
print(f"\n📈 ESTADÍSTICAS GENERALES:")
print(f"   Total Operaciones: {total}")
print(f"   ✅ Ganadas: {wins}")
print(f"   ❌ Perdidas: {losses}")
print(f"   ⏳ Pendientes: {pending}")

if total > 0:
    wr = wins / (wins + losses) * 100 if (wins + losses) > 0 else 0
    print(f"   🎯 Win Rate: {wr:.1f}%")
    
print(f"\n📋 ÚLTIMAS 10 OPERACIONES:")
recent = ops[-10:]
for i, o in enumerate(recent, 1):
    asset = o.get('asset', 'N/A')
    action = o.get('strategy', {}).get('action', 'N/A')
    result = o.get('result', 'pending')
    confidence = o.get('strategy', {}).get('confidence', 0)
    
    emoji = "✅" if result == "win" else "❌" if result == "loose" else "⏳"
    print(f"   {emoji} {asset} - {action} ({confidence:.0f}%) - {result}")

# Análisis por activo
print(f"\n💹 RENDIMIENTO POR ACTIVO:")
by_asset = {}
for o in ops:
    asset = o.get('asset', 'N/A')
    result = o.get('result')
    if asset not in by_asset:
        by_asset[asset] = {'wins': 0, 'losses': 0, 'total': 0}
    by_asset[asset]['total'] += 1
    if result == 'win':
        by_asset[asset]['wins'] += 1
    elif result == 'loose':
        by_asset[asset]['losses'] += 1

for asset, stats in sorted(by_asset.items(), key=lambda x: x[1]['total'], reverse=True)[:5]:
    total_asset = stats['total']
    wins_asset = stats['wins']
    losses_asset = stats['losses']
    wr_asset = wins_asset / (wins_asset + losses_asset) * 100 if (wins_asset + losses_asset) > 0 else 0
    print(f"   {asset}: {total_asset} ops ({wins_asset}W-{losses_asset}L) - WR: {wr_asset:.1f}%")

# Análisis de estrategias
print(f"\n🎯 RENDIMIENTO POR ESTRATEGIA:")
by_strategy = {}
for o in ops:
    strat = o.get('strategy', {}).get('strategy', 'N/A')
    result = o.get('result')
    if strat not in by_strategy:
        by_strategy[strat] = {'wins': 0, 'losses': 0, 'total': 0}
    by_strategy[strat]['total'] += 1
    if result == 'win':
        by_strategy[strat]['wins'] += 1
    elif result == 'loose':
        by_strategy[strat]['losses'] += 1

for strat, stats in sorted(by_strategy.items(), key=lambda x: x[1]['total'], reverse=True)[:5]:
    total_strat = stats['total']
    wins_strat = stats['wins']
    losses_strat = stats['losses']
    wr_strat = wins_strat / (wins_strat + losses_strat) * 100 if (wins_strat + losses_strat) > 0 else 0
    print(f"   {strat}: {total_strat} ops ({wins_strat}W-{losses_strat}L) - WR: {wr_strat:.1f}%")

print("\n" + "="*60)
