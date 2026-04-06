#!/usr/bin/env python3
"""
BOT EXNOVA - APRENDIZAJE SMC + PULLBACK
Modo suave: entra con sweeps suaves Y pullbacks a liquidez
Objetivo: generar datos para aprender que funciona y que no
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
print("BOT EXNOVA - MODO APRENDIZAJE (Sweep + Pullback)")
print("="*78)
print(W + f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(Y + "MODO: PRACTICA (DEMO) - Entradas suaves para aprender")
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

def find_liquidity_levels(df, lookback=100):
    """Encuentra pools de liquidez"""
    if len(df) < 20:
        return [], []
    
    highs = df['high'].tail(lookback).values
    lows = df['low'].tail(lookback).values
    
    buy_side = []
    sell_side = []
    
    # Buscar highs/lows con 2 velas a cada lado (mas sensible)
    for i in range(2, len(highs) - 2):
        is_high = all(highs[i] >= highs[j] for j in range(i-2, i+3) if j != i)
        if is_high:
            buy_side.append(highs[i])
        
        is_low = all(lows[i] <= lows[j] for j in range(i-2, i+3) if j != i)
        if is_low:
            sell_side.append(lows[i])
    
    # Unicos
    unique_bsl = []
    for h in sorted(buy_side, reverse=True):
        if not any(abs(h - u) / h < 0.0003 for u in unique_bsl):
            unique_bsl.append(h)
    
    unique_ssl = []
    for l in sorted(sell_side):
        if not any(abs(l - u) / l < 0.0003 for u in unique_ssl):
            unique_ssl.append(l)
    
    return unique_bsl[:10], unique_ssl[:10]

def detect_sweep(df, bsl_levels, ssl_levels):
    """
    Detecta sweep de liquidez (UMBRAL SUAVE):
    - Precio toca o rompe ligeramente el nivel
    - Mecha de rechazo >= 1.0x del cuerpo (antes 1.5x)
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
    
    # Check buy-side sweep (UMBRAL SUAVE: solo tocar o romper levemente)
    for bsl in bsl_levels:
        if high >= bsl * 0.9995 and price < bsl:  # Toco o rompio ligeramente
            if body > 0 and upper_wick >= body * 1.0:  # Mecha >= cuerpo (antes 1.5x)
                dist_swept = (high - bsl) / bsl * 100 if high > bsl else 0
                wick_ratio = upper_wick / body
                confidence = min(80, 50 + int(wick_ratio * 10))
                
                return {
                    'type': 'BUY_SIDE_SWEEP',
                    'level': bsl,
                    'sweep_high': high,
                    'dist_swept': dist_swept,
                    'wick_ratio': wick_ratio,
                    'signal': 'PUT',
                    'confidence': confidence,
                    'entry_type': 'SWEEP',
                    'reason': f'Sweep suave BSL {bsl:.5f} - mecha {wick_ratio:.1f}x cuerpo'
                }
    
    # Check sell-side sweep
    for ssl in ssl_levels:
        if low <= ssl * 1.0005 and price > ssl:
            if body > 0 and lower_wick >= body * 1.0:
                dist_swept = (ssl - low) / ssl * 100 if low < ssl else 0
                wick_ratio = lower_wick / body
                confidence = min(80, 50 + int(wick_ratio * 10))
                
                return {
                    'type': 'SELL_SIDE_SWEEP',
                    'level': ssl,
                    'sweep_low': low,
                    'dist_swept': dist_swept,
                    'wick_ratio': wick_ratio,
                    'signal': 'CALL',
                    'confidence': confidence,
                    'entry_type': 'SWEEP',
                    'reason': f'Sweep suave SSL {ssl:.5f} - mecha {wick_ratio:.1f}x cuerpo'
                }
    
    return None

def detect_pullback_to_liquidity(df, bsl_levels, ssl_levels):
    """
    Detecta pullback a zona de liquidez (MODO APRENDIZAJE):
    - Precio se acerca a BSL/SSL (dentro de 0.05%)
    - RSI confirma (bajo para CALL, alto para PUT)
    - MACD confirma direccion
    """
    if len(df) < 10:
        return None
    
    price = df.iloc[-1]['close']
    rsi = df.iloc[-1].get('rsi', 50)
    macd = df.iloc[-1].get('macd', 0)
    macd_sig = df.iloc[-1].get('macd_signal', 0)
    
    # Buscar BSL mas cercano
    nearest_bsl = None
    min_dist_bsl = 999
    for bsl in bsl_levels:
        dist = (bsl - price) / price * 100
        if dist > 0 and dist < min_dist_bsl:
            min_dist_bsl = dist
            nearest_bsl = bsl
    
    # Buscar SSL mas cercano
    nearest_ssl = None
    min_dist_ssl = 999
    for ssl in ssl_levels:
        dist = (price - ssl) / price * 100
        if dist > 0 and dist < min_dist_ssl:
            min_dist_ssl = dist
            nearest_ssl = ssl
    
    # CALL: Precio cerca de SSL + RSI bajo + MACD alcista
    if nearest_ssl and min_dist_ssl < 0.08:
        score = 0
        reasons = []
        
        if min_dist_ssl < 0.03:
            score += 30
            reasons.append(f'Muy cerca de SSL ({min_dist_ssl:.3f}%)')
        elif min_dist_ssl < 0.08:
            score += 20
            reasons.append(f'Cerca de SSL ({min_dist_ssl:.3f}%)')
        
        if rsi < 35:
            score += 25
            reasons.append(f'RSI sobreventa ({rsi:.1f})')
        elif rsi < 45:
            score += 15
            reasons.append(f'RSI bajo ({rsi:.1f})')
        
        if macd > macd_sig:
            score += 15
            reasons.append('MACD alcista')
        
        # Verificar tendencia (ultimas 5 velas)
        closes = df['close'].tail(5).values
        if closes[-1] > closes[-3]:
            score += 10
            reasons.append('Momentum alcista')
        
        if score >= 45:
            return {
                'type': 'PULLBACK_SSL',
                'level': nearest_ssl,
                'dist': min_dist_ssl,
                'signal': 'CALL',
                'confidence': min(75, score),
                'entry_type': 'PULLBACK',
                'reason': f'Pullback a SSL + {" + ".join(reasons)}'
            }
    
    # PUT: Precio cerca de BSL + RSI alto + MACD bajista
    if nearest_bsl and min_dist_bsl < 0.08:
        score = 0
        reasons = []
        
        if min_dist_bsl < 0.03:
            score += 30
            reasons.append(f'Muy cerca de BSL ({min_dist_bsl:.3f}%)')
        elif min_dist_bsl < 0.08:
            score += 20
            reasons.append(f'Cerca de BSL ({min_dist_bsl:.3f}%)')
        
        if rsi > 65:
            score += 25
            reasons.append(f'RSI sobrecompra ({rsi:.1f})')
        elif rsi > 55:
            score += 15
            reasons.append(f'RSI alto ({rsi:.1f})')
        
        if macd < macd_sig:
            score += 15
            reasons.append('MACD bajista')
        
        closes = df['close'].tail(5).values
        if closes[-1] < closes[-3]:
            score += 10
            reasons.append('Momentum bajista')
        
        if score >= 45:
            return {
                'type': 'PULLBACK_BSL',
                'level': nearest_bsl,
                'dist': min_dist_bsl,
                'signal': 'PUT',
                'confidence': min(75, score),
                'entry_type': 'PULLBACK',
                'reason': f'Pullback a BSL + {" + ".join(reasons)}'
            }
    
    return None

def run_bot():
    global wins, losses, balance, last_trade_time, trade_history
    
    print(f'\n{G}{"="*78}')
    print(f'  MODO APRENDIZAJE ACTIVADO')
    print(f'  Reglas:')
    print(f'  1. Sweep suave (mecha >= 1.0x cuerpo)')
    print(f'  2. Pullback a liquidez + RSI + MACD')
    print(f'  3. Umbral minimo: 65 puntos (mejorado)')
    print(f'  4. Cooldown: 180s entre operaciones (mejorado)')
    print(f'  Objetivo: Generar datos para aprender')
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
                
                bsl_levels, ssl_levels = find_liquidity_levels(df)
                
                # 1. Intentar detectar sweep (prioridad alta)
                signal_data = detect_sweep(df, bsl_levels, ssl_levels)
                
                # 2. Si no hay sweep, intentar pullback
                if not signal_data:
                    signal_data = detect_pullback_to_liquidity(df, bsl_levels, ssl_levels)
                
                if signal_data and signal_data['confidence'] >= 65:  # Aumentado de 45 a 65
                    sig = signal_data['signal']
                    conf = signal_data['confidence']
                    entry_type = signal_data['entry_type']
                    
                    # Cooldown aumentado a 180s (3 minutos)
                    if now - last_trade_time < 180:
                        if cycle % 6 == 0:
                            print(f'  {Y}Cooldown activo ({int(180 - (now - last_trade_time))}s){X}')
                        continue
                    
                    amount = 1
                    expiration = 3
                    
                    color = G if sig == 'CALL' else R
                    print(f'\n{C}[{datetime.now().strftime("%H:%M:%S")}] {asset}')
                    print(f'  {BOLD}{color}>>> {sig} ${amount} {expiration}min [{entry_type}] (Conf: {conf}%){X}')
                    print(f'  Razon: {signal_data["reason"]}')
                    print(f'  RSI: {rsi:.1f} | MACD: {macd:.5f}/{macd_sig:.5f}')
                    
                    status, trade_id = market_data.api.buy(amount, asset, sig.lower(), expiration)
                    
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
                                'signal': sig,
                                'entry_type': entry_type,
                                'pattern_type': signal_data['type'],
                                'amount': amount,
                                'won': won,
                                'profit': actual_profit,
                                'confidence': conf,
                                'rsi': rsi,
                                'macd': macd,
                                'macd_signal': macd_sig
                            })
                        else:
                            print(f'  {Y}[TIMEOUT]{X}')
                    else:
                        print(f'  {R}[ERROR] {trade_id}{X}')
                        
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
        filename = f'data/learning_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(filename, 'w') as f:
            json.dump(trade_history, f, indent=2)
        print(f'{C}Reporte guardado: {filename} ({len(trade_history)} trades){X}')
        
        # Analisis rapido
        if trade_history:
            sweeps = [t for t in trade_history if t['entry_type'] == 'SWEEP']
            pullbacks = [t for t in trade_history if t['entry_type'] == 'PULLBACK']
            
            sweep_wr = (sum(1 for t in sweeps if t['won']) / len(sweeps) * 100) if sweeps else 0
            pullback_wr = (sum(1 for t in pullbacks if t['won']) / len(pullbacks) * 100) if pullbacks else 0
            
            print(f'{Y}Analisis:')
            print(f'  Sweeps: {len(sweeps)} trades, WR: {sweep_wr:.1f}%')
            print(f'  Pullbacks: {len(pullbacks)} trades, WR: {pullback_wr:.1f}%{X}')

try:
    run_bot()
except KeyboardInterrupt:
    print(f'\n\n{Y}Detenido{X}')
    save_report()
