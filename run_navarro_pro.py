#!/usr/bin/env python3
"""
BOT EXNOVA - ESTRATEGIA NAVARRO + LIQUIDEZ
Usa la logica exacta del script Lua del usuario:
- S/R por FRACTALES (2 velas a cada lado)
- Niveles HH/LL de 10, 30, 60, 100, 150, 200
- Punto BALANCEADO (entrar en zona de mecha/wick)
- Liquidez (sweeps)
"""
import time, random, sys, os, json
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, os.getcwd())

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
print("BOT EXNOVA - NAVARRO S/R + LIQUIDEZ")
print("="*78)
print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("Estrategia: Fractales + HH/LL + Balanceado + Liquidez")
print("="*78 + X)

email = os.getenv('EXNOVA_EMAIL', '')
password = os.getenv('EXNOVA_PASSWORD', '')

print("Conectando...")
market_data = MarketDataHandler(broker_name='exnova', account_type='PRACTICE')

if market_data.connect(email, password):
    print(f"{G}[OK] CONECTADO{X}")
else:
    print(f"{R}[ERROR]{X}")
    sys.exit(1)

try:
    balance = market_data.get_balance()
    print(f"{C}Balance: ${balance}{X}")
except:
    balance = 10000.0

feature_engineer = FeatureEngineer()

# Configuracion
MAX_TRADES_PER_HOUR = 10
MIN_COOLDOWN_SECONDS = 300  # 5 minutos
MIN_SCORE_TO_TRADE = 50

assets = [
    'EURUSD-OTC', 'GBPUSD-OTC', 'AUDUSD-OTC', 'USDJPY-OTC',
    'EURJPY-OTC', 'EURGBP-OTC', 'GBPJPY-OTC', 'AUDJPY-OTC',
    'USDCAD-OTC', 'USDCHF-OTC', 'NZDUSD-OTC', 'EURAUD-OTC'
]

wins = 0
losses = 0
start_time = time.time()
last_trade_time = 0
trade_history = []
trades_this_hour = []
hour_start = time.time()

def find_fractal_resistance(df, lookback=200):
    """
    Detecta resistencias por fractales (IGUAL que script Lua):
    - Busca high[i] que sea mayor que los 2 anteriores y 2 posteriores
    - Filtra si el precio no ha caido mas del 2% desde ese nivel
    """
    if len(df) < 5:
        return []
    
    highs = df['high'].values
    resistencias = []
    
    for i in range(2, len(highs) - 2):
        c = highs[i]
        
        # Fractal: high[i] > high[i-2], high[i-1], high[i+1], high[i+2]
        is_fractal = (highs[i] >= highs[i-2] and 
                      highs[i] >= highs[i-1] and 
                      highs[i] >= highs[i+1] and 
                      highs[i] >= highs[i+2])
        
        # Filtro: precio actual no ha caido mas del 2% desde la resistencia
        current_high = df['high'].iloc[-1]
        within_range = current_high > c * 0.98
        
        if is_fractal and within_range:
            resistencias.append(c)
    
    # Unicos
    unique = []
    for r in sorted(resistencias, reverse=True):
        if not any(abs(r - u) / r < 0.0001 for u in unique):
            unique.append(r)
    
    return unique[:10]

def find_fractal_support(df, lookback=200):
    """
    Detecta soportes por fractales (IGUAL que script Lua):
    - Busca low[i] que sea menor que los 2 anteriores y 2 posteriores
    - Filtro: precio actual no ha subido mas del 2% desde ese nivel
    """
    if len(df) < 5:
        return []
    
    lows = df['low'].values
    soportes = []
    
    for i in range(2, len(lows) - 2):
        c = lows[i]
        
        # Fractal: low[i] < low[i-2], low[i-1], low[i+1], low[i+2]
        is_fractal = (lows[i] <= lows[i-2] and 
                      lows[i] <= lows[i-1] and 
                      lows[i] <= lows[i+1] and 
                      lows[i] <= lows[i+2])
        
        # Filtro: precio actual no ha subido mas del 2%
        current_low = df['low'].iloc[-1]
        within_range = current_low < c * 1.02
        
        if is_fractal and within_range:
            soportes.append(c)
    
    unique = []
    for s in sorted(soportes):
        if not any(abs(s - u) / s < 0.0001 for u in unique):
            unique.append(s)
    
    return unique[:10]

def get_hh_ll_levels(df):
    """
    Obtiene niveles HH/LL de multiples periodos (IGUAL que script Lua):
    HH10/LL10, HH30/LL30, HH60/LL60, HH100/LL100, HH150/LL150, HH200/LL200
    """
    levels = {}
    
    for period in [10, 30, 60, 100, 150, 200]:
        if len(df) >= period:
            levels[f'HH{period}'] = df['high'].tail(period).max()
            levels[f'LL{period}'] = df['low'].tail(period).min()
    
    return levels

def detect_liquidity_sweep(df, near_level):
    """
    Detecta liquidity sweep - precio toca nivel pero hace mecha de rechazo
    """
    if len(df) < 3:
        return None
    
    current = df.iloc[-1]
    price = current['close']
    high = current['high']
    low = current['low']
    
    body = abs(current['close'] - current['open'])
    upper_wick = current['high'] - max(current['open'], current['close'])
    lower_wick = min(current['open'], current['close']) - current['low']
    
    # Si precio esta cerca de una resistencia y hace mecha grande arriba = PUT
    if near_level['type'] == 'resistance':
        if upper_wick > body * 1.2:  # Mecha significativa
            return {
                'type': 'LIQUIDITY_SWEEP_UP',
                'direction': 'PUT',
                'confidence': min(85, 60 + int(upper_wick / body * 10))
            }
    
    # Si precio esta cerca de un soporte y hace mecha grande abajo = CALL
    elif near_level['type'] == 'support':
        if lower_wick > body * 1.2:
            return {
                'type': 'LIQUIDITY_SWEEP_DOWN',
                'direction': 'CALL',
                'confidence': min(85, 60 + int(lower_wick / body * 10))
            }
    
    return None

def analyze_asset_navarro(asset):
    """Analisis con estrategia Navarro completa"""
    try:
        df = market_data.get_candles(asset, timeframe=60, num_candles=250)
        if df is None or len(df) < 50:
            return None
        
        df = feature_engineer.add_technical_indicators(df)
        
        price = df.iloc[-1]['close']
        rsi = df.iloc[-1].get('rsi', 50)
        macd = df.iloc[-1].get('macd', 0)
        macd_sig = df.iloc[-1].get('macd_signal', 0)
        
        current = df.iloc[-1]
        body = abs(current['close'] - current['open'])
        if body == 0:
            body = 0.00001  # Evitar division por cero
        upper_wick = current['high'] - max(current['open'], current['close'])
        lower_wick = min(current['open'], current['close']) - current['low']
        
        # 1. S/R FRACTALES (como script Lua)
        resistencias = find_fractal_resistance(df)
        soportes = find_fractal_support(df)
        
        # 2. HH/LL MULTIPLES
        hh_ll = get_hh_ll_levels(df)
        
        # Encontrar nivel mas cercano
        nearest_r = min(resistencias, key=lambda x: abs(x - price)) if resistencias else None
        nearest_s = min(soportes, key=lambda x: abs(x - price)) if soportes else None
        
        # Verificar si hay HH/LL mas cercanos
        for period in [10, 30, 60]:
            hh_key = f'HH{period}'
            ll_key = f'LL{period}'
            if hh_key in hh_ll:
                dist_hh = abs(hh_ll[hh_key] - price) / price * 100
                if nearest_r:
                    dist_existing = abs(nearest_r - price) / price * 100
                    if dist_hh < dist_existing:
                        nearest_r = hh_ll[hh_key]
            if ll_key in hh_ll:
                dist_ll = abs(price - hh_ll[ll_key]) / price * 100
                if nearest_s:
                    dist_existing = abs(price - nearest_s) / price * 100
                    if dist_ll < dist_existing:
                        nearest_s = hh_ll[ll_key]
        
        # Distancias
        if nearest_r is None or price is None or price == 0:
            dist_r = 999
        else:
            dist_r = abs(price - nearest_r) / price * 100
        
        if nearest_s is None or price is None or price == 0:
            dist_s = 999
        else:
            dist_s = abs(price - nearest_s) / price * 100
        
        # SCORE
        call_score = 0
        put_score = 0
        reasons = []
        
        # === PUNTO BALANCEADO (Zona de mecha) ===
        # CALL: Precio cerca de soporte Y en zona de mecha inferior
        if nearest_s:
            # Esta cerca del soporte?
            if dist_s < 0.03:
                # Esta en zona de mecha/wick?
                is_lower_wick = lower_wick > body * 0.5
                is_price_near_low = price <= (current['open'] + current['close']) / 2
                
                if is_lower_wick or is_price_near_low:
                    call_score += 35
                    reasons.append(f"PUNTO BALANCEADO CALL: precio en mecha cerca SOPORTE ({dist_s:.3f}%)")
                else:
                    call_score += 20
                    reasons.append(f"cerca de SOPORTE ({dist_s:.3f}%)")
        
        # PUT: Precio cerca de resistencia Y en zona de mecha superior
        if nearest_r:
            if dist_r < 0.03:
                is_upper_wick = upper_wick > body * 0.5
                is_price_near_high = price >= (current['open'] + current['close']) / 2
                
                if is_upper_wick or is_price_near_high:
                    put_score += 35
                    reasons.append(f"PUNTO BALANCEADO PUT: precio en mecha cerca RESISTENCIA ({dist_r:.3f}%)")
                else:
                    put_score += 20
                    reasons.append(f"cerca de RESISTENCIA ({dist_r:.3f}%)")
        
        # === RSI ===
        if rsi < 30:
            call_score += 25
            reasons.append(f"RSI sobreventa extrema ({rsi:.1f})")
        elif rsi < 40:
            call_score += 15
            reasons.append(f"RSI bajo ({rsi:.1f})")
        elif rsi > 70:
            put_score += 25
            reasons.append(f"RSI sobrecompra extrema ({rsi:.1f})")
        elif rsi > 60:
            put_score += 15
            reasons.append(f"RSI alto ({rsi:.1f})")
        
        # === MACD ===
        if macd > macd_sig and macd > 0:
            call_score += 15
            reasons.append("MACD alcista")
        elif macd < macd_sig and macd < 0:
            put_score += 15
            reasons.append("MACD bajista")
        
        # === LIQUIDEZ (Sweep) ===
        # CALL: Soporte con mecha de rechazo
        if nearest_s and dist_s < 0.02 and body > 0 and lower_wick > body * 1.0:
            call_score += 20
            reasons.append(f"LIQUIDEZ: rechazo en SOPORTE")
        
        # PUT: Resistencia con mecha de rechazo  
        if nearest_r and dist_r < 0.02 and body > 0 and upper_wick > body * 1.0:
            put_score += 20
            reasons.append(f"LIQUIDEZ: rechazo en RESISTENCIA")
        
        # Decision
        if call_score >= MIN_SCORE_TO_TRADE and call_score > put_score:
            return {
                "asset": asset, "signal": "CALL", "score": call_score,
                "reasons": reasons, "rsi": rsi, "price": price,
                "dist_s": dist_s, "dist_r": dist_r,
                "has_sweep": lower_wick > body
            }
        elif put_score >= MIN_SCORE_TO_TRADE and put_score > call_score:
            return {
                "asset": asset, "signal": "PUT", "score": put_score,
                "reasons": reasons, "rsi": rsi, "price": price,
                "dist_s": dist_s, "dist_r": dist_r,
                "has_sweep": upper_wick > body
            }
        
        return None
        
    except Exception as e:
        return None

def can_trade():
    global trades_this_hour, hour_start
    now = time.time()
    if now - hour_start > 3600:
        trades_this_hour = []
        hour_start = now
    if len(trades_this_hour) >= MAX_TRADES_PER_HOUR:
        return False, "limite"
    if now - last_trade_time < MIN_COOLDOWN_SECONDS:
        return False, "cooldown"
    return True, "ok"

print(f"\n{G}NAVARRO S/R + LIQUIDEZ{X}")
print(f"10 ops/hr | Score>={MIN_SCORE_TO_TRADE} | Cooldown {MIN_COOLDOWN_SECONDS//60}min")
print(f"12 activos{X}\n")

cycle = 0
try:
    while True:
        cycle += 1
        now = time.time()
        
        print(f"\n{'='*60}")
        print(f"CICLO {cycle} | {datetime.now().strftime('%H:%M:%S')} | {len(trades_this_hour)}/{MAX_TRADES_PER_HOUR} ops/hr")
        print(f"{'='*60}")
        
        puede, reason = can_trade()
        if not puede:
            if reason == "limite":
                print(f"{Y}>>> LIMITE {MAX_TRADES_PER_HOUR}/hr alcanzado{X}")
            else:
                remaining = MIN_COOLDOWN_SECONDS - (now - last_trade_time)
                print(f"{Y}>>> Cooldown: {remaining//60}m{X}")
            time.sleep(60)
            continue
        
        # Analizar todos los activos
        print(f"\n{C}--- Escaneando {len(assets)} activos ---{X}")
        
        opportunities = []
        for asset in assets:
            opp = analyze_asset_navarro(asset)
            if opp:
                opportunities.append(opp)
                color = G if opp['signal'] == 'CALL' else R
                print(f"  {color}{asset}: {opp['signal']} | Score:{opp['score']} | RSI:{opp['rsi']:.0f} | S:{opp['dist_s']:.2f}% R:{opp['dist_r']:.2f}%{X}")
        
        if not opportunities:
            print(f"{Y}Sin senales claras{X}")
            time.sleep(90)
            continue
        
        # Mejor oportunidad
        opportunities.sort(key=lambda x: x['score'], reverse=True)
        best = opportunities[0]
        
        print(f"\n{G}>>> MEJOR: {best['asset']} {best['signal']} | Score:{best['score']}{X}")
        for r in best['reasons']:
            print(f"  - {r}")
        
        # Ejecutar
        delay = random.randint(3, 8)
        print(f"\nEjecutando en {delay}s...")
        time.sleep(delay)
        
        try:
            print(f"\n{BOLD}{G if best['signal']=='CALL' else R}>>> {best['signal']} {best['asset']} $1 3min{X}")
            
            status, trade_id = market_data.api.buy(1, best['asset'], best['signal'].lower(), 3)
            
            if status:
                print(f"ID: {trade_id} | Esperando 3 min...")
                time.sleep(3*60 + 20)
                
                result = None
                for _ in range(4):
                    try:
                        result_status, profit = market_data.api.check_win_v4(trade_id, timeout=90)
                        if result_status:
                            result = (result_status, profit)
                            break
                    except:
                        time.sleep(5)
                
                if result:
                    won = result[0] == "win"
                    profit = result[1] if won else -1
                    
                    if won:
                        wins += 1
                        print(f"\n{G}*** WIN +${profit:.2f} ***{X}")
                    else:
                        losses += 1
                        print(f"\n{R}*** LOSS -$1 ***{X}")
                    
                    balance += profit
                    last_trade_time = time.time()
                    trades_this_hour.append(last_trade_time)
                    
                    trade_history.append({
                        "time": datetime.now().isoformat(),
                        "asset": best['asset'],
                        "signal": best['signal'],
                        "score": best['score'],
                        "won": won,
                        "profit": profit
                    })
                else:
                    print(f"{Y}[TIMEOUT]{X}")
        except Exception as e:
            print(f"Error: {e}")
        
        # Resumen
        total = wins + losses
        wr = (wins/total*100) if total > 0 else 0
        mins = int((time.time() - start_time) / 60)
        pnl = balance - 10000.0
        pc = G if pnl >= 0 else R
        
        print(f"\n{C}RESUMEN: {mins}min | W:{wins} L:{losses} | WR:{wr:.0f}% | ${pnl:+.2f}{X}")
        
        time.sleep(random.randint(240, 360))

except KeyboardInterrupt:
    print(f"\n{Y}Detenido{X}")
    if trade_history:
        with open(f"data/navarro_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "w") as f:
            json.dump(trade_history, f, indent=2)