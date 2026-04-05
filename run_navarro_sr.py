#!/usr/bin/env python3
"""
BOT EXNOVA - S/R FRACTAL NAVARRO (Lua -> Python)
Implementa el detector de soportes/resistencias del script Lua
"""
import time, sys, os
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
print("BOT EXNOVA - S/R FRACTAL NAVARRO (10/30/60/100/150/200)")
print("="*78)
print(W + f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*78 + X)

email = os.getenv('EXNOVA_EMAIL', '')
password = os.getenv('EXNOVA_PASSWORD', '')

market_data = MarketDataHandler(broker_name='exnova', account_type='PRACTICE')

if market_data.connect(email, password):
    print(f'{G}[OK] CONECTADO A EXNOVA{X}')
else:
    print(f'{R}[ERROR] No se pudo conectar{X}')
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

def find_fractal_resistance(df, lookback=200):
    """
    Detecta resistencias por fractales (igual que el script Lua):
    - Busca high[i] que sea mayor que los 2 anteriores y 2 posteriores
    - Filtra si el precio no ha caido mas del 2% desde ese nivel
    """
    if len(df) < 5:
        return []
    
    highs = df['high'].values
    resistances = []
    
    for i in range(2, len(highs) - 2):
        c = highs[i]
        if not c:
            continue
        
        # Fractal: high[i] > high[i-2], high[i-1], high[i+1], high[i+2]
        is_fractal = (highs[i] >= highs[i-2] and 
                      highs[i] >= highs[i-1] and 
                      highs[i] >= highs[i+1] and 
                      highs[i] >= highs[i+2])
        
        # Filtro: precio actual no ha caido mas del 2% desde la resistencia
        current_high = df['high'].iloc[-1]
        within_range = current_high > c * 0.98
        
        if is_fractal and within_range:
            resistances.append(c)
    
    # Eliminar duplicados cercanos (dentro de 0.01%)
    unique = []
    for r in sorted(resistances, reverse=True):
        if not any(abs(r - u) / r < 0.0001 for u in unique):
            unique.append(r)
    
    return unique[:10]

def find_fractal_support(df, lookback=200):
    """
    Detecta soportes por fractales (igual que el script Lua):
    - Busca low[i] que sea menor que los 2 anteriores y 2 posteriores
    - Filtra si el precio no ha subido mas del 2% desde ese nivel
    """
    if len(df) < 5:
        return []
    
    lows = df['low'].values
    supports = []
    
    for i in range(2, len(lows) - 2):
        c = lows[i]
        if not c:
            continue
        
        # Fractal: low[i] < low[i-2], low[i-1], low[i+1], low[i+2]
        is_fractal = (lows[i] <= lows[i-2] and 
                      lows[i] <= lows[i-1] and 
                      lows[i] <= lows[i+1] and 
                      lows[i] <= lows[i+2])
        
        # Filtro: precio actual no ha subido mas del 2% desde el soporte
        current_low = df['low'].iloc[-1]
        within_range = current_low < c * 1.02
        
        if is_fractal and within_range:
            supports.append(c)
    
    # Eliminar duplicados cercanos
    unique = []
    for s in sorted(supports):
        if not any(abs(s - u) / s < 0.0001 for u in unique):
            unique.append(s)
    
    return unique[:10]

def get_highest_lowest_levels(df):
    """
    Obtiene niveles HH/LL de multiples periodos (como el script Lua):
    HH10/LL10, HH30/LL30, HH60/LL60, HH100/LL100, HH150/LL150, HH200/LL200
    """
    levels = {}
    
    for period in [10, 30, 60, 100, 150, 200]:
        if len(df) >= period:
            levels[f'HH{period}'] = df['high'].tail(period).max()
            levels[f'LL{period}'] = df['low'].tail(period).min()
    
    return levels

def analyze_with_navarro_sr(asset):
    """Analisis completo usando S/R Fractal Navarro"""
    print(f'\n{C}{"="*78}')
    print(f'  ANALIZANDO: {asset}')
    print(f'{"="*78}{X}')
    
    # Obtener datos M1 (necesitamos 200+ velas para todos los niveles)
    df = market_data.get_candles(asset, timeframe=60, num_candles=250)
    if df is None or len(df) < 50:
        print(f'  {R}Sin datos suficientes{X}')
        return None
    
    df = feature_engineer.add_technical_indicators(df)
    
    # 1. S/R FRACTAL (5-velas)
    fractal_res = find_fractal_resistance(df)
    fractal_supp = find_fractal_support(df)
    
    price = df.iloc[-1]['close']
    rsi = df.iloc[-1].get('rsi', 50)
    macd = df.iloc[-1].get('macd', 0)
    macd_sig = df.iloc[-1].get('macd_signal', 0)
    bb_upper = df.iloc[-1].get('bb_high', price)
    bb_lower = df.iloc[-1].get('bb_low', price)
    
    print(f'\n{Y}--- S/R FRACTAL (5 velas) ---{X}')
    print(f'  Precio actual: {price:.5f}')
    
    if fractal_res:
        print(f'  {R}Resistencias fractales:{X}')
        for i, r in enumerate(fractal_res[:5]):
            dist = abs(r - price) / price * 100
            marker = ' <<<< MAS CERCANA' if i == 0 else ''
            print(f'    R{i+1}: {r:.5f} ({dist:.3f}%){marker}')
    
    if fractal_supp:
        print(f'  {G}Soportes fractales:{X}')
        for i, s in enumerate(fractal_supp[:5]):
            dist = abs(price - s) / price * 100
            marker = ' <<<< MAS CERCANO' if i == 0 else ''
            print(f'    S{i+1}: {s:.5f} ({dist:.3f}%){marker}')
    
    # 2. NIVELES HH/LL MULTIPLES
    hh_ll = get_highest_lowest_levels(df)
    
    print(f'\n{Y}--- NIVELES HH/LL (Maximos/Minimos) ---{X}')
    for period in [10, 30, 60, 100, 150, 200]:
        hh_key = f'HH{period}'
        ll_key = f'LL{period}'
        if hh_key in hh_ll:
            hh = hh_ll[hh_key]
            ll = hh_ll[ll_key]
            dist_hh = abs(hh - price) / price * 100
            dist_ll = abs(price - ll) / price * 100
            print(f'  HH{period}: {hh:.5f} ({dist_hh:.3f}%) | LL{period}: {ll:.5f} ({dist_ll:.3f}%)')
    
    # 3. ANALISIS DE OPORTUNIDAD
    print(f'\n{BOLD}{Y}--- ANALISIS DE OPORTUNIDAD ---{X}')
    print(f'  RSI: {rsi:.1f} | MACD: {macd:.5f}/{macd_sig:.5f}')
    print(f'  BB: {bb_lower:.5f} - {bb_upper:.5f}')
    
    # Determinar S/R mas relevantes (los mas cercanos al precio)
    nearest_res = fractal_res[0] if fractal_res else None
    nearest_supp = fractal_supp[0] if fractal_supp else None
    
    # Si no hay fractales, usar HH/LL de 30
    if not nearest_res and 'HH30' in hh_ll:
        nearest_res = hh_ll['HH30']
    if not nearest_supp and 'LL30' in hh_ll:
        nearest_supp = hh_ll['LL30']
    
    if not nearest_res or not nearest_supp:
        print(f'  {Y}Sin S/R claros{X}')
        return None
    
    dist_to_res = abs(nearest_res - price) / price * 100
    dist_to_supp = abs(price - nearest_supp) / price * 100
    
    print(f'\n  S mas cercano: {nearest_supp:.5f} ({dist_to_supp:.3f}%)')
    print(f'  R mas cercana: {nearest_res:.5f} ({dist_to_res:.3f}%)')
    
    # SCORING
    call_score = 0
    put_score = 0
    
    # REGLA DE ORO: Comprar en SOPORTE, Vender en RESISTENCIA
    if dist_to_supp < 0.03:  # Dentro de 0.03% del soporte
        call_score += 40
        print(f'  {G}[+40] Precio en SOPORTE ({dist_to_supp:.3f}%){X}')
    
    if dist_to_res < 0.03:  # Dentro de 0.03% de resistencia
        put_score += 40
        print(f'  {G}[+40] Precio en RESISTENCIA ({dist_to_res:.3f}%){X}')
    
    if rsi < 30:
        call_score += 25
        print(f'  {G}[+25] RSI sobreventa ({rsi:.1f}){X}')
    elif rsi > 70:
        put_score += 25
        print(f'  {G}[+25] RSI sobrecompra ({rsi:.1f}){X}')
    elif rsi < 40:
        call_score += 15
        print(f'  {G}[+15] RSI bajo ({rsi:.1f}){X}')
    elif rsi > 60:
        put_score += 15
        print(f'  {G}[+15] RSI alto ({rsi:.1f}){X}')
    
    if macd > macd_sig:
        call_score += 20
        print(f'  {G}[+20] MACD alcista{X}')
    elif macd < macd_sig:
        put_score += 20
        print(f'  {G}[+20] MACD bajista{X}')
    
    if price <= bb_lower * 1.001:
        call_score += 15
        print(f'  {G}[+15] Precio en BB inferior{X}')
    elif price >= bb_upper * 0.999:
        put_score += 15
        print(f'  {G}[+15] Precio en BB superior{X}')
    
    print(f'\n  SCORE CALL: {call_score}/100')
    print(f'  SCORE PUT:  {put_score}/100')
    
    # Decision
    min_score = 60
    if call_score >= min_score and call_score > put_score:
        signal = 'CALL'
        score = call_score
    elif put_score >= min_score and put_score > call_score:
        signal = 'PUT'
        score = put_score
    else:
        print(f'\n{Y}>>> SIN SENAL <<<{X}')
        return None
    
    print(f'\n{BOLD}{G if signal == "CALL" else R}>>> SENAL: {signal} en {asset} (Score: {score}) <<<{X}')
    
    return signal, score, df

# Ejecutar analisis
print(f'\n{C}INICIANDO ANALISIS CON S/R FRACTAL NAVARRO...{X}')

for asset in assets:
    result = analyze_with_navarro_sr(asset)
    time.sleep(2)

print(f'\n{C}{"="*78}')
print(f'ANALISIS COMPLETADO')
print(f'{"="*78}{X}')
