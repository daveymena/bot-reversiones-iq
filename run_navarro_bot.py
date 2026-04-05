#!/usr/bin/env python3
"""
BOT EXNOVA - S/R FRACTAL NAVARRO + OPERACION REAL
Usa S/R fractales del script Navarro con operacion automatica
"""
import time, sys, os, json
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, os.getcwd())

from config import Config
from data.market_data import MarketDataHandler
from strategies.technical import FeatureEngineer

G = '\033[92m'
R = '\033[91m'
Y = '\033[93m'
C = '\033[96m'
W = '\033[97m'
X = '\033[0m'
BOLD = '\033[1m'

print(C + "="*78)
print("BOT EXNOVA - S/R FRACTAL NAVARRO + OPERACION REAL")
print("="*78)
print(W + f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(Y + "MODO: PRACTICA (DEMO)")
print("="*78 + X)

email = os.getenv('EXNOVA_EMAIL', '')
password = os.getenv('EXNOVA_PASSWORD', '')

market_data = MarketDataHandler(broker_name='exnova', account_type='PRACTICE')

if market_data.connect(email, password):
    print(f'{G}[OK] CONECTADO{X}')
else:
    print(f'{R}[ERROR]{X}')
    sys.exit(1)

try:
    balance = market_data.get_balance()
    print(f'{C}Balance: ${balance}{X}')
except:
    balance = 10000.0

try:
    market_data.api.update_ACTIVES_OPCODE()
except: pass

feature_engineer = FeatureEngineer()
assets = ['EURUSD-OTC', 'GBPUSD-OTC', 'AUDUSD-OTC']

wins = 0
losses = 0
start_time = time.time()
last_trade_time = 0
trade_history = []

def find_fractal_levels(df):
    """Detecta S/R por fractales (5 velas) + HH/LL multiples"""
    if len(df) < 10:
        return [], [], {}
    
    highs = df['high'].values
    lows = df['low'].values
    
    resistances = []
    supports = []
    
    # Fractales (igual que script Lua)
    for i in range(2, len(highs) - 2):
        c = highs[i]
        is_fractal = (highs[i] >= highs[i-2] and highs[i] >= highs[i-1] and 
                      highs[i] >= highs[i+1] and highs[i] >= highs[i+2])
        if is_fractal:
            resistances.append(c)
    
    for i in range(2, len(lows) - 2):
        c = lows[i]
        is_fractal = (lows[i] <= lows[i-2] and lows[i] <= lows[i-1] and 
                      lows[i] <= lows[i+1] and lows[i] <= lows[i+2])
        if is_fractal:
            supports.append(c)
    
    # HH/LL multiples
    hh_ll = {}
    for period in [10, 30, 60, 100, 150, 200]:
        if len(df) >= period:
            hh_ll[f'HH{period}'] = df['high'].tail(period).max()
            hh_ll[f'LL{period}'] = df['low'].tail(period).min()
    
    # Unicos (eliminar duplicados cercanos)
    unique_res = []
    for r in sorted(resistances, reverse=True):
        if not any(abs(r - u) / r < 0.0001 for u in unique_res):
            unique_res.append(r)
    
    unique_supp = []
    for s in sorted(supports):
        if not any(abs(s - u) / s < 0.0001 for u in unique_supp):
            unique_supp.append(s)
    
    return unique_res[:10], unique_supp[:10], hh_ll

def score_opportunity(price, rsi, macd, macd_sig, bb_upper, bb_lower, 
                      nearest_res, nearest_supp, dist_to_res, dist_to_supp):
    """Score de oportunidad con logica corregida"""
    call_score = 0
    put_score = 0
    reasons = []
    
    # === REGLA DE ORO: Comprar en SOPORTE, Vender en RESISTENCIA ===
    
    # CALL: Precio cerca de SOPORTE = oportunidad de compra
    if dist_to_supp < 0.05:
        call_score += 40
        reasons.append(f'CALL: Precio en SOPORTE ({dist_to_supp:.3f}%)')
    elif dist_to_supp < 0.1:
        call_score += 25
        reasons.append(f'CALL: Precio cerca de soporte ({dist_to_supp:.3f}%)')
    elif dist_to_supp < 0.3:
        call_score += 10
        reasons.append(f'CALL: Precio relativamente cerca de soporte ({dist_to_supp:.3f}%)')
    
    # PUT: Precio cerca de RESISTENCIA = oportunidad de venta
    if dist_to_res < 0.05:
        put_score += 40
        reasons.append(f'PUT: Precio en RESISTENCIA ({dist_to_res:.3f}%)')
    elif dist_to_res < 0.1:
        put_score += 25
        reasons.append(f'PUT: Precio cerca de resistencia ({dist_to_res:.3f}%)')
    elif dist_to_res < 0.3:
        put_score += 10
        reasons.append(f'PUT: Precio relativamente cerca de resistencia ({dist_to_res:.3f}%)')
    
    # RSI
    if rsi < 25:
        call_score += 25
        reasons.append(f'RSI sobreventa extrema ({rsi:.1f})')
    elif rsi < 35:
        call_score += 20
        reasons.append(f'RSI sobreventa ({rsi:.1f})')
    elif rsi < 45:
        call_score += 10
        reasons.append(f'RSI bajo ({rsi:.1f})')
    elif rsi > 75:
        put_score += 25
        reasons.append(f'RSI sobrecompra extrema ({rsi:.1f})')
    elif rsi > 65:
        put_score += 20
        reasons.append(f'RSI sobrecompra ({rsi:.1f})')
    elif rsi > 55:
        put_score += 10
        reasons.append(f'RSI alto ({rsi:.1f})')
    
    # MACD
    if macd > macd_sig:
        call_score += 15
        reasons.append('MACD alcista')
    elif macd < macd_sig:
        put_score += 15
        reasons.append('MACD bajista')
    
    # Bollinger
    if price <= bb_lower * 1.002:
        call_score += 15
        reasons.append('Precio en BB inferior')
    elif price >= bb_upper * 0.998:
        put_score += 15
        reasons.append('Precio en BB superior')
    
    # ANTI-TRAMPA: No comprar en resistencia, no vender en soporte
    if dist_to_res < 0.03 and call_score > 0:
        call_score = max(0, call_score - 30)
        reasons.append('ANTI-TRAMPA: No comprar en resistencia!')
    
    if dist_to_supp < 0.03 and put_score > 0:
        put_score = max(0, put_score - 30)
        reasons.append('ANTI-TRAMPA: No vender en soporte!')
    
    return call_score, put_score, reasons

def run_bot():
    global wins, losses, balance, last_trade_time, trade_history
    
    print(f'\n{G}{"="*78}')
    print(f'  EJECUCION INICIADA - S/R FRACTAL NAVARRO')
    print(f'  Presiona Ctrl+C para detener')
    print(f'{"="*78}{X}\n')
    
    import signal
    signal.signal(signal.SIGINT, lambda s, f: (print(f'\n{Y}Deteniendo...{X}'), save_report(), sys.exit(0)))
    
    cycle = 0
    while True:
        cycle += 1
        now = time.time()
        elapsed = now - start_time
        
        for asset in assets:
            try:
                df = market_data.get_candles(asset, timeframe=60, num_candles=250)
                if df is None or len(df) < 50:
                    continue
                
                df = feature_engineer.add_technical_indicators(df)
                
                price = df.iloc[-1]['close']
                rsi = df.iloc[-1].get('rsi', 50)
                macd = df.iloc[-1].get('macd', 0)
                macd_sig = df.iloc[-1].get('macd_signal', 0)
                bb_upper = df.iloc[-1].get('bb_high', price)
                bb_lower = df.iloc[-1].get('bb_low', price)
                
                fractal_res, fractal_supp, hh_ll = find_fractal_levels(df)
                
                if not fractal_res or not fractal_supp:
                    continue
                
                nearest_res = fractal_res[0]
                nearest_supp = fractal_supp[0]
                dist_to_res = abs(nearest_res - price) / price * 100
                dist_to_supp = abs(price - nearest_supp) / price * 100
                
                call_score, put_score, reasons = score_opportunity(
                    price, rsi, macd, macd_sig, bb_upper, bb_lower,
                    nearest_res, nearest_supp, dist_to_res, dist_to_supp
                )
                
                # Mostrar analisis
                if call_score >= 40 or put_score >= 40:
                    signal_name = 'CALL' if call_score > put_score else 'PUT'
                    score = max(call_score, put_score)
                    
                    print(f'\n{C}[{datetime.now().strftime("%H:%M:%S")}] {asset}')
                    print(f'  Precio: {price:.5f} | RSI: {rsi:.1f}')
                    print(f'  S: {nearest_supp:.5f} ({dist_to_supp:.3f}%) | R: {nearest_res:.5f} ({dist_to_res:.3f}%)')
                    print(f'  Score CALL: {call_score} | PUT: {put_score}')
                    for r in reasons:
                        print(f'    - {r}')
                    
                    if score >= 55 and now - last_trade_time >= 120:
                        amount = 1
                        expiration = 3
                        
                        print(f'\n{BOLD}{G if signal_name == "CALL" else R}>>> {signal_name} ${amount} {expiration}min <<<{X}')
                        
                        status, trade_id = market_data.api.buy(amount, asset, signal_name.lower(), expiration)
                        
                        if status:
                            print(f'  {G}[OK] ID: {trade_id} | Esperando...{X}')
                            time.sleep(expiration * 60 + 15)
                            
                            result_status, profit = market_data.api.check_win_v4(trade_id, timeout=90)
                            if result_status is not None:
                                won = result_status == 'win'
                                actual_profit = profit if won else -amount
                                
                                if won:
                                    wins += 1
                                    print(f'  {BOLD}{G}[WIN] +${actual_profit:.2f}{X}')
                                else:
                                    losses += 1
                                    print(f'  {BOLD}{R}[LOSS] ${actual_profit:.2f}{X}')
                                
                                balance += actual_profit
                                last_trade_time = now
                                
                                trade_history.append({
                                    'time': datetime.now().isoformat(),
                                    'asset': asset,
                                    'signal': signal_name,
                                    'amount': amount,
                                    'won': won,
                                    'profit': actual_profit,
                                    'score': score,
                                    'dist_supp': dist_to_supp,
                                    'dist_res': dist_to_res,
                                    'rsi': rsi
                                })
                            else:
                                print(f'  {Y}[TIMEOUT]{X}')
                        else:
                            print(f'  {R}[ERROR] {trade_id}{X}')
                    elif now - last_trade_time < 120:
                        print(f'  {Y}Cooldown activo{X}')
                    else:
                        print(f'  {Y}Score insuficiente ({score} < 55){X}')
                        
            except Exception as e:
                print(f'  {R}Error {asset}: {e}{X}')
                continue
        
        total = wins + losses
        wr = (wins/total*100) if total > 0 else 0
        pnl = balance - 10000.0
        mins = int(elapsed / 60)
        secs = int(elapsed % 60)
        pc = G if pnl >= 0 else R
        print(f'\n{C}Ciclo {cycle} | {mins}m{secs}s | T:{total} | {G}{wins}{X}/{R}{losses}{X} | WR:{wr:.1f}% | {pc}${pnl:+.2f}{X}')
        
        time.sleep(10)

def save_report():
    """Guarda reporte de operaciones"""
    if trade_history:
        with open(f'data/trade_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json', 'w') as f:
            json.dump(trade_history, f, indent=2)
        print(f'{C}Reporte guardado: {len(trade_history)} operaciones{X}')

try:
    run_bot()
except KeyboardInterrupt:
    print(f'\n\n{Y}Detenido{X}')
    save_report()
