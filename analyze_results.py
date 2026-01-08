import json
from datetime import datetime
from collections import Counter

try:
    with open('data/learning_database.json', 'r', encoding='utf-8') as f:
        db = json.load(f)

    ops = db.get('operations', [])
    print(f"Total históricas: {len(ops)}")
    
    # Solo operaciones con resultado real
    results = [o for o in ops if o.get('result') in ['win', 'loose']]
    print(f"Operaciones con resultado: {len(results)}")
    
    if not results:
        print("No hay operaciones con resultados cerrados para analizar.")
        exit()

    recent = results[-20:]
    wins = len([o for o in recent if o.get('result') == 'win'])
    losses = len([o for o in recent if o.get('result') == 'loose'])
    wr = (wins / len(recent)) * 100 if recent else 0
    
    print(f"\n--- ÚLTIMAS {len(recent)} OPERACIONES ---")
    print(f"Win Rate: {wr:.1f}% ({wins}W - {losses}L)")
    
    print("\nANÁLISIS POR ESTRATEGIA:")
    strats = {}
    for o in recent:
        s_data = o.get('strategy', {})
        if not s_data and 'opportunity' in o:
            s_data = o.get('opportunity', {}).get('strategy', {})
        
        name = s_data.get('strategy', 'Unknown')
        res = o.get('result')
        
        if name not in strats:
            strats[name] = {'win': 0, 'loose': 0}
        strats[name][res] += 1

    for name, data in strats.items():
        total = data['win'] + data['loose']
        swr = (data['win'] / total) * 100
        print(f" - {name}: {swr:.1f}% WR ({data['win']}/{total})")

    print("\nDETALLE DE PÉRDIDAS (Últimas 5):")
    losses_only = [o for o in results if o.get('result') == 'loose'][-5:]
    for o in losses_only:
        s_data = o.get('strategy', {})
        if not s_data and 'opportunity' in o:
            s_data = o.get('opportunity', {}).get('strategy', {})
        
        asset = o.get('asset', 'N/A')
        reason = s_data.get('reason', 'N/A')
        print(f" • {asset} | {s_data.get('strategy')} | Razón: {reason}")

except Exception as e:
    print(f"Error: {e}")
