#!/usr/bin/env python3
"""
BOT EXNOVA - SMC LIQUIDITY SWEEP TRADER
Opera SOLO cuando detecta:
1. Precio va hacia pool de liquidez (BSL/SSL)
2. Barrido confirmado (rompe nivel pero cierra dentro)
3. Mecha de rechazo grande
4. Entrada en direccion opuesta al sweep
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
print("BOT EXNOVA - SMC LIQUIDITY SWEEP TRADER")
print("="*78)
print(W + f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(Y + "MODO: PRACTICA (DEMO) - Solo entra con sweep confirmado")
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
sweep_history = {}  # Track sweeps per asset

def find_liquidity_levels(df, lookback=100):
    """Encuentra pools de liquidez (highs/lows significativos)"""
    if len(df) < 20:
        return [], []
    
    highs = df['high'].tail(lookback).values
    lows = df['low'].tail(lookback).values
    
    buy_side = []  # Stops arriba de highs
    sell_side = []  # Stops abajo de lows
    
    # Buscar highs/lows con al menos 3 velas a cada lado
    for i in range(3, len(highs) - 3):
        is_high = all(highs[i] >= highs[j] for j in range(i-3, i+4) if j != i)
        if is_high:
            buy_side.append(highs[i])
        
        is_low = all(lows[i] <= lows[j] for j in range(i-3, i+4) if j != i)
        if is_low:
            sell_side.append(lows[i])
    
    # Eliminar duplicados cercanos
    unique_bsl = []
    for h in sorted(buy_side, reverse=True):
        if not any(abs(h - u) / h < 0.0002 for u in unique_bsl):
            unique_bsl.append(h)
    
    unique_ssl = []
    for l in sorted(sell_side):
        if not any(abs(l - u) / l < 0.0002 for u in unique_ssl):
            unique_ssl.append(l)
    
    return unique_bsl[:10], unique_ssl[:10]

def detect_sweep(df, bsl_levels, ssl_levels):
    """
    Detecta sweep de liquidez:
    - Precio rompe nivel pero CIERRA dentro del rango
    - Mecha de rechazo grande (2x+ del cuerpo)
    """
    if len(df) < 3:
        return None
    
    current = df.iloc[-1]
    prev = df.iloc[-2]
    prev2 = df.iloc[-3]
    
    price = current['close']
    high = current['high']
    low = current['low']
    
    body = abs(current['close'] - current['open'])
    upper_wick = current['high'] - max(current['open'], current['close'])
    lower_wick = min(current['open'], current['close']) - current['low']
    
    # Check buy-side sweep (precio rompio BSL pero cerro abajo)
    for bsl in bsl_levels:
        if high > bsl and price < bsl:
            # Mecha superior grande = rechazo
            if upper_wick > body * 1.5 and body > 0:
                dist_swept = (high - bsl) / bsl * 100
                return {
                    'type': 'BUY_SIDE_SWEEP',
                    'level': bsl,
                    'sweep_high': high,
                    'dist_swept': dist_swept,
                    'wick_ratio': upper_wick / body if body > 0 else 999,
                    'signal': 'PUT',
                    'confidence': min(90, 60 + int(upper_wick / body * 10)),
                    'reason': f'Precio rompio BSL {bsl:.5f} pero rechazo con mecha {upper_wick/body:.1f}x cuerpo'
                }
    
    # Check sell-side sweep (precio rompio SSL pero cerro arriba)
    for ssl in ssl_levels:
        if low < ssl and price > ssl:
            # Mecha inferior grande = rechazo
            if lower_wick > body * 1.5 and body > 0:
                dist_swept = (ssl - low) / ssl * 100
                return {
                    'type': 'SELL_SIDE_SWEEP',
                    'level': ssl,
                    'sweep_low': low,
                    'dist_swept': dist_swept,
                    'wick_ratio': lower_wick / body if body > 0 else 999,
                    'signal': 'CALL',
                    'confidence': min(90, 60 + int(lower_wick / body * 10)),
                    'reason': f'Precio rompio SSL {ssl:.5f} pero rechazo con mecha {lower_wick/body:.1f}x cuerpo'
                }
    
    return None

def check_price_approaching_liquidity(df, bsl_levels, ssl_levels):
    """Verifica si el precio se esta acercando a un pool de liquidez"""
    if len(df) < 5:
        return None
    
    price = df.iloc[-1]['close']
    
    # Verificar direccion del precio (ultimas 5 velas)
    recent_closes = df['close'].tail(5).values
    if len(recent_closes) >= 3:
        momentum = recent_closes[-1] - recent_closes[-3]
    else:
        momentum = 0
    
    # Buscar nivel mas cercano en direccion del momentum
    if momentum > 0:  # Subiendo -> buscando BSL
        nearest = None
        min_dist = 999
        for bsl in bsl_levels:
            dist = (bsl - price) / price * 100
            if dist > 0 and dist < min_dist:
                min_dist = dist
                nearest = bsl
        
        if nearest and min_dist < 0.1:  # Dentro de 0.1%
            return {'direction': 'UP', 'target': 'BSL', 'level': nearest, 'dist': min_dist}
    
    elif momentum < 0:  # Bajando -> buscando SSL
        nearest = None
        min_dist = 999
        for ssl in ssl_levels:
            dist = (price - ssl) / price * 100
            if dist > 0 and dist < min_dist:
                min_dist = dist
                nearest = ssl
        
        if nearest and min_dist < 0.1:
            return {'direction': 'DOWN', 'target': 'SSL', 'level': nearest, 'dist': min_dist}
    
    return None

def run_bot():
    global wins, losses, balance, last_trade_time, trade_history, sweep_history
    
    print(f'\n{G}{"="*78}')
    print(f'  EJECUCION INICIADA - SMC SWEEP TRADER')
    print(f'  Reglas:')
    print(f'  1. Esperar sweep de liquidez confirmado')
    print(f'  2. Mecha de rechazo 1.5x+ del cuerpo')
    print(f'  3. Entrar en direccion opuesta al sweep')
    print(f'  4. NO entrar sin sweep')
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
                df = market_data.get_candles(asset, timeframe=60, num_candles=200)
                if df is None or len(df) < 50:
                    continue
                
                df = feature_engineer.add_technical_indicators(df)
                
                price = df.iloc[-1]['close']
                rsi = df.iloc[-1].get('rsi', 50)
                macd = df.iloc[-1].get('macd', 0)
                macd_sig = df.iloc[-1].get('macd_signal', 0)
                
                # Encontrar niveles de liquidez
                bsl_levels, ssl_levels = find_liquidity_levels(df)
                
                # 1. Verificar si hay sweep
                sweep = detect_sweep(df, bsl_levels, ssl_levels)
                
                # 2. Verificar si precio se acerca a liquidez
                approaching = check_price_approaching_liquidity(df, bsl_levels, ssl_levels)
                
                # Mostrar estado
                if sweep or approaching:
                    print(f'\n{C}[{datetime.now().strftime("%H:%M:%S")}] {asset}')
                    print(f'  Precio: {price:.5f} | RSI: {rsi:.1f}')
                    
                    if approaching:
                        print(f'  {Y}ACERCANDOSE A LIQUIDEZ: {approaching["target"]} en {approaching["level"]:.5f} ({approaching["dist"]:.3f}%){X}')
                    
                    if sweep:
                        print(f'  {BOLD}{G if sweep["signal"] == "CALL" else R}SWEEP DETECTADO: {sweep["type"]}{X}')
                        print(f'  Nivel: {sweep["level"]:.5f}')
                        print(f'  Barrido: {sweep["dist_swept"]:.3f}%')
                        print(f'  Mecha/Cuerpo: {sweep["wick_ratio"]:.1f}x')
                        print(f'  Senal: {sweep["signal"]} (Confianza: {sweep["confidence"]}%)')
                        print(f'  Razon: {sweep["reason"]}')
                        
                        # Ejecutar si no hay cooldown
                        if now - last_trade_time >= 120:
                            amount = 1
                            expiration = 3
                            
                            print(f'\n{BOLD}{G if sweep["signal"] == "CALL" else R}>>> EJECUTANDO {sweep["signal"]} - ${amount} - {expiration}min <<<{X}')
                            
                            status, trade_id = market_data.api.buy(amount, asset, sweep['signal'].lower(), expiration)
                            
                            if status:
                                print(f'  {G}[OK] Trade ID: {trade_id}{X}')
                                print(f'  {Y}Esperando {expiration} min...{X}')
                                
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
                                        'signal': sweep['signal'],
                                        'sweep_type': sweep['type'],
                                        'amount': amount,
                                        'won': won,
                                        'profit': actual_profit,
                                        'confidence': sweep['confidence'],
                                        'wick_ratio': sweep['wick_ratio'],
                                        'rsi': rsi
                                    })
                                else:
                                    print(f'  {Y}[TIMEOUT]{X}')
                            else:
                                print(f'  {R}[ERROR] {trade_id}{X}')
                        else:
                            remaining = int(120 - (now - last_trade_time))
                            print(f'  {Y}Cooldown: {remaining}s restantes{X}')
                    else:
                        print(f'  {Y}Esperando sweep para entrar...{X}')
                        
            except Exception as e:
                print(f'  {R}Error {asset}: {e}{X}')
                continue
        
        # Dashboard
        total = wins + losses
        wr = (wins/total*100) if total > 0 else 0
        pnl = balance - 10000.0
        mins = int(elapsed / 60)
        secs = int(elapsed % 60)
        pc = G if pnl >= 0 else R
        print(f'\n{C}Ciclo {cycle} | {mins}m{secs}s | T:{total} | {G}{wins}{X}/{R}{losses}{X} | WR:{wr:.1f}% | {pc}${pnl:+.2f}{X}')
        
        time.sleep(10)

def save_report():
    if trade_history:
        filename = f'data/sweep_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(filename, 'w') as f:
            json.dump(trade_history, f, indent=2)
        print(f'{C}Reporte guardado: {filename}{X}')

try:
    run_bot()
except KeyboardInterrupt:
    print(f'\n\n{Y}Detenido{X}')
    save_report()
