import json
from datetime import datetime

with open('bot/brain/trade_history.json') as f:
    data = json.load(f)

trades = data['trades']
wins   = [t for t in trades if t['result'] == 'WIN']
losses = [t for t in trades if t['result'] == 'LOSS']

print("=== ANALISIS DE PERDIDAS ===")
print(f"Total: {len(trades)} | Wins: {len(wins)} | Losses: {len(losses)}")
print(f"PnL Total: {data['total_pnl']:.2f}")
print()

# Por sesion
sessions = {}
for t in trades:
    s = t.get('session', '?')
    if s not in sessions:
        sessions[s] = {'W': 0, 'L': 0}
    if t['result'] == 'WIN':
        sessions[s]['W'] += 1
    else:
        sessions[s]['L'] += 1

print("=== POR SESION ===")
for s, v in sorted(sessions.items()):
    total = v['W'] + v['L']
    wr = v['W'] / total * 100 if total else 0
    flag = " <-- PROBLEMATICA" if wr < 50 else ""
    print(f"  {s}: {v['W']}W/{v['L']}L  WR={wr:.0f}%{flag}")

# Por direccion
print()
dirs = {'CALL': {'W': 0, 'L': 0}, 'PUT': {'W': 0, 'L': 0}}
for t in trades:
    d = t['direction']
    if t['result'] == 'WIN':
        dirs[d]['W'] += 1
    else:
        dirs[d]['L'] += 1

print("=== POR DIRECCION ===")
for d, v in dirs.items():
    total = v['W'] + v['L']
    if total > 0:
        wr = v['W'] / total * 100
        flag = " <-- PROBLEMATICA" if wr < 50 else ""
        print(f"  {d}: {v['W']}W/{v['L']}L  WR={wr:.0f}%{flag}")

# Por patron
print()
patterns = {}
for t in trades:
    p = t.get('pattern', '?')
    if p not in patterns:
        patterns[p] = {'W': 0, 'L': 0}
    if t['result'] == 'WIN':
        patterns[p]['W'] += 1
    else:
        patterns[p]['L'] += 1

print("=== POR PATRON ===")
for p, v in sorted(patterns.items()):
    total = v['W'] + v['L']
    if total > 0:
        wr = v['W'] / total * 100
        flag = " <-- PROBLEMATICA" if wr < 50 else ""
        print(f"  {p}: {v['W']}W/{v['L']}L  WR={wr:.0f}%{flag}")

# Detalle de losses
print()
print("=== DETALLE PERDIDAS ===")
for t in losses:
    ts = datetime.fromtimestamp(t['timestamp']).strftime('%H:%M')
    print(f"  [{ts}] {t['asset']} {t['direction']} | {t['pattern']} | zona={t['zone_strength']:.2f} | sesion={t['session']} | conf={t['confidence']:.0%}")

# Análisis de la causa raiz
print()
print("=== CAUSA RAIZ PROBABLE ===")
pacific_losses = [t for t in losses if t.get('session') == 'PACIFIC']
call_losses    = [t for t in losses if t['direction'] == 'CALL']
low_wr_sessions = [s for s, v in sessions.items() if v['L'] > 0 and v['W'] / (v['W'] + v['L']) < 0.5]

if pacific_losses:
    print(f"  SESION PACIFIC: {len(pacific_losses)} perdidas ({len(pacific_losses)/len(losses)*100:.0f}% del total)")
if call_losses:
    print(f"  CALLS: {len(call_losses)} perdidas de {dirs['CALL']['W']+dirs['CALL']['L']} totales")
if low_wr_sessions:
    print(f"  Sesiones problemáticas: {', '.join(low_wr_sessions)}")
