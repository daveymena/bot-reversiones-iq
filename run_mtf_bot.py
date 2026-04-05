#!/usr/bin/env python3
"""
BOT EXNOVA - MTF S/R MACRO + ENTRADA M1
Opera realmente en DEMO usando S/R de M15/M30 y timing M1
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
print("BOT EXNOVA - MTF S/R MACRO + ENTRADA M1")
print("="*78)
print(W + f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(Y + "MODO: PRACTICA (DEMO) - Operaciones REALES")
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

# Estado
wins = 0
losses = 0
start_time = time.time()
last_trade_time = 0
trade_history = []

def find_support_resistance(df, lookback=50):
    """Encuentra S/R con fallback a maximos/minimos si no hay locales"""
    if len(df) < 20:
        return [], []
    
    highs = df['high'].tail(lookback).values
    lows = df['low'].tail(lookback).values
    
    resistances = []
    supports = []
    
    for i in range(2, len(highs) - 2):
        if highs[i] > highs[i-1] and highs[i] > highs[i-2] and \
           highs[i] > highs[i+1] and highs[i] > highs[i+2]:
            resistances.append(highs[i])
    
    for i in range(2, len(lows) - 2):
        if lows[i] < lows[i-1] and lows[i] < lows[i-2] and \
           lows[i] < lows[i+1] and lows[i] < lows[i+2]:
            supports.append(lows[i])
    
    if len(resistances) < 2:
        sorted_highs = sorted(highs, reverse=True)
        for h in sorted_highs[:3]:
            if not any(abs(h - r) / h < 0.001 for r in resistances):
                resistances.append(h)
    
    if len(supports) < 2:
        sorted_lows = sorted(lows)
        for l in sorted_lows[:3]:
            if not any(abs(l - s) / l < 0.001 for s in supports):
                supports.append(l)
    
    resistances = sorted(list(set(resistances)), reverse=True)[:5]
    supports = sorted(list(set(supports)))[:5]
    
    return resistances, supports

def analyze_and_trade(asset):
    """Analisis MTF + ejecucion si hay senal"""
    try:
        # M15 para S/R
        df_m15 = market_data.get_candles(asset, timeframe=900, num_candles=50)
        if df_m15 is None or len(df_m15) < 15:
            return False
        df_m15 = feature_engineer.add_technical_indicators(df_m15)
        m15_res, m15_supp = find_support_resistance(df_m15, lookback=30)
        
        if not m15_res or not m15_supp:
            return False
        
        m15_price = df_m15.iloc[-1]['close']
        nearest_res = min(m15_res, key=lambda x: abs(x - m15_price))
        nearest_supp = min(m15_supp, key=lambda x: abs(x - m15_price))
        
        # M30 para tendencia
        df_m30 = market_data.get_candles(asset, timeframe=1800, num_candles=30)
        if df_m30 is not None and len(df_m30) >= 10:
            df_m30 = feature_engineer.add_technical_indicators(df_m30)
            m30_price = df_m30.iloc[-1]['close']
            m30_rsi = df_m30.iloc[-1].get('rsi', 50)
            sma_10 = df_m30['close'].tail(10).mean()
            m30_trend = 'ALCISTA' if m30_price > sma_10 else 'BAJISTA'
        else:
            m30_trend = 'DESCONOCIDA'
            m30_rsi = 50
        
        # M1 para entrada
        df_m1 = market_data.get_candles(asset, timeframe=60, num_candles=100)
        if df_m1 is None or len(df_m1) < 50:
            return False
        df_m1 = feature_engineer.add_technical_indicators(df_m1)
        m1_price = df_m1.iloc[-1]['close']
        m1_rsi = df_m1.iloc[-1].get('rsi', 50)
        m1_macd = df_m1.iloc[-1].get('macd', 0)
        m1_macd_sig = df_m1.iloc[-1].get('macd_signal', 0)
        bb_upper = df_m1.iloc[-1].get('bb_high', m1_price)
        bb_lower = df_m1.iloc[-1].get('bb_low', m1_price)
        
        dist_to_res = abs(nearest_res - m1_price) / m1_price * 100
        dist_to_supp = abs(m1_price - nearest_supp) / m1_price * 100
        
        # SCORING
        call_score = 0
        put_score = 0
        
        if dist_to_supp < 0.05:
            call_score += 40
        if dist_to_res < 0.05:
            put_score += 40
        
        if m1_rsi < 35:
            call_score += 25
        elif m1_rsi > 65:
            put_score += 25
        
        if m1_macd > m1_macd_sig:
            call_score += 20
        elif m1_macd < m1_macd_sig:
            put_score += 20
        
        if m30_trend == 'ALCISTA':
            call_score += 15
        elif m30_trend == 'BAJISTA':
            put_score += 15
        
        if m1_price <= bb_lower * 1.001:
            call_score += 10
        elif m1_price >= bb_upper * 0.999:
            put_score += 10
        
        # DECISION
        min_score = 60
        
        if call_score >= min_score and call_score > put_score:
            signal = 'CALL'
            score = call_score
        elif put_score >= min_score and put_score > call_score:
            signal = 'PUT'
            score = put_score
        else:
            return False
        
        # Ejecutar operacion
        now = time.time()
        if now - last_trade_time < 120:
            return False
        
        amount = 1
        expiration = 3
        
        print(f'\n{BOLD}{C}[{datetime.now().strftime("%H:%M:%S")}] {asset}{X}')
        print(f'  M15 S/R: S={nearest_supp:.5f} ({dist_to_supp:.3f}%) | R={nearest_res:.5f} ({dist_to_res:.3f}%)')
        print(f'  M30: {m30_trend} | RSI: {m30_rsi:.1f}')
        print(f'  M1: Price={m1_price:.5f} | RSI={m1_rsi:.1f} | MACD={m1_macd:.5f}')
        print(f'  Score CALL: {call_score} | PUT: {put_score}')
        print(f'\n{BOLD}{G if signal == "CALL" else R}>>> EJECUTANDO {signal} en {asset} - ${amount} - {expiration} min (Score: {score}) <<<{X}')
        
        status, trade_id = market_data.api.buy(amount, asset, signal.lower(), expiration)
        
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
                
                trade_history.append({
                    'time': datetime.now().isoformat(),
                    'asset': asset,
                    'signal': signal,
                    'amount': amount,
                    'won': won,
                    'profit': actual_profit,
                    'score': score,
                    'dist_to_supp': dist_to_supp,
                    'dist_to_res': dist_to_res,
                    'm1_rsi': m1_rsi,
                    'm30_trend': m30_trend
                })
            else:
                print(f'  {Y}[TIMEOUT]{X}')
            
            return True
        else:
            print(f'  {R}[ERROR] {trade_id}{X}')
            return False
            
    except Exception as e:
        print(f'  {R}Error: {e}{X}')
        return False

print(f'\n{G}{"="*78}')
print(f'  EJECUCION INICIADA')
print(f'  Presiona Ctrl+C para detener')
print(f'{"="*78}{X}\n')

import signal
signal.signal(signal.SIGINT, lambda s, f: (print(f'\n{Y}Deteniendo...{X}'), sys.exit(0)))

cycle = 0
try:
    while True:
        cycle += 1
        now = time.time()
        elapsed = now - start_time
        
        for asset in assets:
            analyze_and_trade(asset)
            time.sleep(2)
        
        total = wins + losses
        wr = (wins/total*100) if total > 0 else 0
        pnl = balance - 10000.0
        mins = int(elapsed / 60)
        secs = int(elapsed % 60)
        
        pc = G if pnl >= 0 else R
        print(f'\n{C}Ciclo {cycle} | {mins}m{secs}s | Trades: {total} | W/L: {G}{wins}{X}/{R}{losses}{X} | WR: {wr:.1f}% | PnL: {pc}${pnl:+.2f}{X}')
        
        time.sleep(10)

except KeyboardInterrupt:
    print(f'\n\n{Y}Detenido{X}')

total = wins + losses
wr = (wins/total*100) if total > 0 else 0
pnl = balance - 10000.0
elapsed = time.time() - start_time

print(f'\n{C}{"="*78}')
print(f'RESUMEN FINAL')
print(f'{"="*78}')
print(f'Tiempo: {elapsed/60:.1f} min | Trades: {total} | WR: {wr:.1f}%')
print(f'Wins: {wins} | Losses: {losses} | PnL: ${pnl:+.2f}')
print(f'{"="*78}{X}')
