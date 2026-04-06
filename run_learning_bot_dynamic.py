#!/usr/bin/env python3
"""
BOT EXNOVA - APRENDIZAJE SMC + PULLBACK CON EXPIRACIÓN DINÁMICA
Calcula la expiración según la complejidad de la operación (1-5 minutos)
"""
import time, sys, os, json
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, os.getcwd())

from config import Config
from data.market_data import MarketDataHandler
from strategies.technical import FeatureEngineer
import pandas as pd
import ta

G = '\033[92m'
R = '\033[91m'
Y = '\033[93m'
C = '\033[96m'
W = '\033[97m'
X = '\033[0m'
BOLD = '\033[1m'

print(C + "="*78)
print("BOT EXNOVA - MODO APRENDIZAJE (Sweep + Pullback) CON EXPIRACIÓN DINÁMICA")
print("="*78)
print(W + f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(Y + "MODO: PRACTICA (DEMO) - Expiración dinámica 1-5 minutos según complejidad")
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
    
    for i in range(2, len(highs) - 2):
        is_high = all(highs[i] >= highs[j] for j in range(i-2, i+3) if j != i)
        if is_high:
            buy_side.append(highs[i])
        
        is_low = all(lows[i] <= lows[j] for j in range(i-2, i+3) if j != i)
        if is_low:
            sell_side.append(lows[i])
    
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
    """Detecta sweep de liquidez"""
    if len(df) < 3:
        return None
    
    current = df.iloc[-1]
    price = current['close']
    high = current['high']
    low = current['low']
    
    body = abs(current['close'] - current['open'])
    upper_wick = current['high'] - max(current['open'], current['close'])
    lower_wick = min(current['open'], current['close']) - current['low']
    
    for bsl in bsl_levels:
        if high >= bsl * 0.9995 and price < bsl:
            if body > 0 and upper_wick >= body * 1.0:
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
                    'reason': f'Sweep suave BSL {bsl:.5f} - mecha {wick_ratio:.1f}x cuerpo',
                    'complexity': 2  # Sweep = complejidad media
                }
    
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
                    'reason': f'Sweep suave SSL {ssl:.5f} - mecha {wick_ratio:.1f}x cuerpo',
                    'complexity': 2
                }
    
    return None

def detect_pullback_to_liquidity(df, bsl_levels, ssl_levels):
    """Detecta pullback a zona de liquidez con scoring mejorado"""
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
    
    # Pullback a BSL + RSI bajo
    if nearest_bsl and min_dist_bsl < 0.05:
        score = 45
        reasons = []
        
        if min_dist_bsl < 0.03:
            score += 30
            reasons.append(f'Muy cerca de BSL ({min_dist_bsl:.3f}%)')
        elif min_dist_bsl < 0.08:
            score += 20
            reasons.append(f'Cerca de BSL ({min_dist_bsl:.3f}%)')
        
        if rsi < 35:
            score += 25
            reasons.append(f'RSI sobreventa ({rsi:.1f})')
        elif rsi < 50:
            score += 15
            reasons.append(f'RSI bajo ({rsi:.1f})')
        
        if macd > macd_sig and macd > 0:
            score += 10
            reasons.append('MACD alcista')
        
        closes = df['close'].tail(5).values
        if closes[-1] > closes[-3]:
            score += 10
            reasons.append('Momentum alcista')
        
        if score >= 65:
            # Calcular complejidad (1-5)
            complexity = 1
            if min_dist_bsl < 0.02:
                complexity = 5  # Muy cerca = más complejo
            elif min_dist_bsl < 0.03:
                complexity = 4
            elif min_dist_bsl < 0.04:
                complexity = 3
            elif min_dist_bsl < 0.05:
                complexity = 2
            
            return {
                'type': 'PULLBACK_BSL',
                'level': nearest_bsl,
                'distance': min_dist_bsl,
                'signal': 'CALL',
                'confidence': score,
                'entry_type': 'PULLBACK',
                'reason': ' + '.join(reasons),
                'complexity': complexity
            }
    
    # Buscar SSL mas cercano
    nearest_ssl = None
    min_dist_ssl = 999
    for ssl in ssl_levels:
        dist = (price - ssl) / ssl * 100
        if dist > 0 and dist < min_dist_ssl:
            min_dist_ssl = dist
            nearest_ssl = ssl
    
    # Pullback a SSL + RSI alto
    if nearest_ssl and min_dist_ssl < 0.05:
        score = 45
        reasons = []
        
        if min_dist_ssl < 0.03:
            score += 30
            reasons.append(f'Muy cerca de SSL ({min_dist_ssl:.3f}%)')
        elif min_dist_ssl < 0.08:
            score += 20
            reasons.append(f'Cerca de SSL ({min_dist_ssl:.3f}%)')
        
        if rsi > 65:
            score += 25
            reasons.append(f'RSI sobrecompra ({rsi:.1f})')
        elif rsi > 50:
            score += 15
            reasons.append(f'RSI alto ({rsi:.1f})')
        
        if macd < macd_sig and macd < 0:
            score += 10
            reasons.append('MACD bajista')
        
        closes = df['close'].tail(5).values
        if closes[-1] < closes[-3]:
            score += 10
            reasons.append('Momentum bajista')
        
        if score >= 65:
            # Calcular complejidad (1-5)
            complexity = 1
            if min_dist_ssl < 0.02:
                complexity = 5  # Muy cerca = más complejo
            elif min_dist_ssl < 0.03:
                complexity = 4
            elif min_dist_ssl < 0.04:
                complexity = 3
            elif min_dist_ssl < 0.05:
                complexity = 2
            
            return {
                'type': 'PULLBACK_SSL',
                'level': nearest_ssl,
                'distance': min_dist_ssl,
                'signal': 'PUT',
                'confidence': score,
                'entry_type': 'PULLBACK',
                'reason': ' + '.join(reasons),
                'complexity': complexity
            }
    
    return None

def calculate_expiration(complexity):
    """
    Calcula expiración según complejidad
    Complejidad 1-5 = Expiración 1-5 minutos
    """
    return max(1, min(5, complexity))

def run_bot():
    global last_trade_time, trade_history
    
    print(f'\n{BOLD}MODO APRENDIZAJE ACTIVADO{X}')
    print(f'Reglas:')
    print(f'1. Sweep suave (mecha >= 1.0x cuerpo)')
    print(f'2. Pullback a liquidez + RSI + MACD')
    print(f'3. Umbral minimo: 65 puntos (mejorado)')
    print(f'4. Cooldown: 180s entre operaciones (mejorado)')
    print(f'5. Expiración dinámica: 1-5 minutos según complejidad')
    print(f'Objetivo: Generar datos para aprender')
    print(f'Presiona Ctrl+C para detener')
    print("="*78 + "\n")
    
    assets = ["EURUSD-OTC", "GBPUSD-OTC", "USDJPY-OTC", "AUDUSD-OTC", "NZDUSD-OTC"]
    asset_idx = 0
    cycle = 0
    start_time = datetime.now()
    
    try:
        while True:
            cycle += 1
            now = time.time()
            elapsed = int((datetime.now() - start_time).total_seconds())
            mins = elapsed // 60
            secs = elapsed % 60
            
            asset = assets[asset_idx % len(assets)]
            asset_idx += 1
            
            try:
                candles = market_data.get_candles(asset, "3m", 100)
                
                if not candles or len(candles) < 20:
                    status = f'{Y}[SKIP] Sin datos{X}'
                else:
                    df = pd.DataFrame(candles)
                    df['close'] = pd.to_numeric(df['close'], errors='coerce')
                    df['open'] = pd.to_numeric(df['open'], errors='coerce')
                    df['high'] = pd.to_numeric(df['high'], errors='coerce')
                    df['low'] = pd.to_numeric(df['low'], errors='coerce')
                    
                    df['rsi'] = ta.momentum.RSIIndicator(close=df['close'], window=14).rsi()
                    macd = ta.trend.MACD(close=df['close'])
                    df['macd'] = macd.macd()
                    df['macd_signal'] = macd.macd_signal()
                    
                    bsl, ssl = find_liquidity_levels(df)
                    
                    signal_data = detect_sweep(df, bsl, ssl)
                    if not signal_data:
                        signal_data = detect_pullback_to_liquidity(df, bsl, ssl)
                    
                    if signal_data and signal_data['confidence'] >= 65:
                        if now - last_trade_time >= 180:
                            sig = signal_data['signal']
                            conf = signal_data['confidence']
                            entry_type = signal_data['entry_type']
                            
                            amount = 1
                            complexity = signal_data.get('complexity', 3)
                            expiration = calculate_expiration(complexity)
                            
                            color = G if sig == 'CALL' else R
                            print(f'\n{C}[{datetime.now().strftime("%H:%M:%S")}] {asset}')
                            print(f'  {BOLD}{color}>>> {sig} ${amount} {expiration}min [{entry_type}] (Conf: {conf}%){X}')
                            print(f'  Complejidad: {complexity}/5 | Expiración: {expiration} min')
                            print(f'  Razon: {signal_data["reason"]}')
                            
                            rsi = df.iloc[-1].get('rsi', 50)
                            macd_val = df.iloc[-1].get('macd', 0)
                            macd_sig = df.iloc[-1].get('macd_signal', 0)
                            print(f'  RSI: {rsi:.1f} | MACD: {macd_val:.5f}/{macd_sig:.5f}')
                            
                            status, trade_id = market_data.api.buy(amount, asset, sig.lower(), expiration)
                            
                            if status:
                                print(f'  {G}[OK] ID: {trade_id} | Esperando...{X}')
                                time.sleep(expiration * 60 + 15)
                                
                                result_status, profit = market_data.api.check_win_v4(trade_id, timeout=90)
                                
                                if result_status:
                                    won = result_status == 'win'
                                    trade_history.append({
                                        'asset': asset,
                                        'signal': sig,
                                        'result': 'WIN' if won else 'LOSS',
                                        'profit': profit,
                                        'expiration': expiration,
                                        'complexity': complexity
                                    })
                                    
                                    result_color = G if won else R
                                    print(f'  {result_color}[{"WIN" if won else "LOSS"}] ${profit:+.2f}{X}')
                                    
                                    last_trade_time = now
                                else:
                                    print(f'  {Y}[UNKNOWN]{X}')
                            else:
                                print(f'  {R}[FAILED]{X}')
                            
                            status = f'{G}[TRADE]{X}'
                        else:
                            status = f'{Y}[COOLDOWN]{X}'
                    else:
                        status = f'{Y}[SKIP]{X}'
                
                wins = sum(1 for t in trade_history if t['result'] == 'WIN')
                total = len(trade_history)
                wr = (wins * 100 // total) if total > 0 else 0
                profit = sum(t['profit'] for t in trade_history)
                
                try:
                    current_balance = market_data.get_balance()
                except:
                    current_balance = balance
                
                print(f'Ciclo {cycle} | {mins}m{secs}s | T:{total} | {wins}/{total} | WR:{wr}% | ${current_balance:+.2f}', end='\r')
                
            except Exception as e:
                print(f'{R}Error: {str(e)}{X}')
            
            time.sleep(10)
    
    except KeyboardInterrupt:
        print(f'\n\n{Y}Bot detenido{X}')
        save_report()

def save_report():
    """Guarda reporte"""
    if trade_history:
        wins = sum(1 for t in trade_history if t['result'] == 'WIN')
        total = len(trade_history)
        profit = sum(t['profit'] for t in trade_history)
        
        print(f'\n{BOLD}REPORTE FINAL{X}')
        print(f'Total: {total} | Ganancias: {wins} ({wins*100//total}%) | Ganancia: ${profit:+.2f}')
        
        with open('bot_report.json', 'w') as f:
            json.dump(trade_history, f, indent=2)

if __name__ == '__main__':
    run_bot()
