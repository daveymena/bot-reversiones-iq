#!/usr/bin/env python3
"""
SMC LIQUIDITY DETECTOR
Detecta:
- Liquidity pools (highs/lows anteriores)
- Liquidity sweep (barrido de stops)
- BOS/CHoCH despues del sweep
- Entrada solo DESPUES del sweep con confirmacion
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
print("SMC LIQUIDITY DETECTOR - MTF")
print("="*78)
print(W + f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
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
    market_data.api.update_ACTIVES_OPCODE()
except: pass

feature_engineer = FeatureEngineer()
assets = ['EURUSD-OTC', 'GBPUSD-OTC', 'AUDUSD-OTC']

def detect_liquidity_pools(df):
    """
    Detecta pools de liquidez (donde estan los stops):
    - Buy-side liquidity: arriba de highs anteriores
    - Sell-side liquidity: abajo de lows anteriores
    """
    if len(df) < 20:
        return {'buy_side': [], 'sell_side': []}
    
    buy_side = []
    sell_side = []
    
    # Buscar highs/lows significativos (mas de 5 velas a cada lado)
    for i in range(5, len(df) - 5):
        # High significativo = buy-side liquidity
        is_high = True
        for j in range(i-5, i+6):
            if j != i and df['high'].iloc[j] >= df['high'].iloc[i]:
                is_high = False
                break
        if is_high:
            buy_side.append({
                'price': df['high'].iloc[i],
                'index': i,
                'time': df.index[i],
                'strength': 0
            })
        
        # Low significativo = sell-side liquidity
        is_low = True
        for j in range(i-5, i+6):
            if j != i and df['low'].iloc[j] <= df['low'].iloc[i]:
                is_low = False
                break
        if is_low:
            sell_side.append({
                'price': df['low'].iloc[i],
                'index': i,
                'time': df.index[i],
                'strength': 0
            })
    
    # Calcular fuerza (cuantas veces fue testeado)
    current_price = df.iloc[-1]['close']
    for pool in buy_side:
        tests = sum(1 for h in df['high'] if abs(h - pool['price']) / pool['price'] < 0.0002)
        pool['strength'] = tests
    
    for pool in sell_side:
        tests = sum(1 for l in df['low'] if abs(l - pool['price']) / pool['price'] < 0.0002)
        pool['strength'] = tests
    
    # Ordenar por cercania al precio actual
    buy_side.sort(key=lambda x: abs(x['price'] - current_price))
    sell_side.sort(key=lambda x: abs(x['price'] - current_price))
    
    return {
        'buy_side': buy_side[:10],
        'sell_side': sell_side[:10]
    }

def detect_liquidity_sweep(df, liquidity_pools):
    """
    Detecta si el precio acaba de hacer sweep/barrido de liquidez:
    - Precio rompe un high/low pero CIERRA dentro del rango
    - Esto indica barrido de stops, no breakout real
    """
    if len(df) < 10:
        return None
    
    current = df.iloc[-1]
    prev = df.iloc[-2]
    prev2 = df.iloc[-3] if len(df) > 2 else prev
    
    sweeps = []
    
    # Check buy-side sweep (barrido de stops arriba)
    for pool in liquidity_pools['buy_side']:
        pool_price = pool['price']
        
        # Precio rompio el high pero cerro abajo
        if current['high'] > pool_price and current['close'] < pool_price:
            # Mecha superior larga = rechazo
            upper_wick = current['high'] - max(current['open'], current['close'])
            body = abs(current['close'] - current['open'])
            
            if upper_wick > body * 1.5:  # Mecha 1.5x mas grande que cuerpo
                sweeps.append({
                    'type': 'BUY_SIDE_SWEEP',
                    'level': pool_price,
                    'sweep_high': current['high'],
                    'sweep_amount': (current['high'] - pool_price) / pool_price * 100,
                    'wick_size': upper_wick,
                    'body_size': body,
                    'signal': 'PUT',  # Despues de sweep buy-side, esperar PUT
                    'confidence': 80 if upper_wick > body * 2 else 60
                })
    
    # Check sell-side sweep (barrido de stops abajo)
    for pool in liquidity_pools['sell_side']:
        pool_price = pool['price']
        
        # Precio rompio el low pero cerro arriba
        if current['low'] < pool_price and current['close'] > pool_price:
            # Mecha inferior larga = rechazo
            lower_wick = min(current['open'], current['close']) - current['low']
            body = abs(current['close'] - current['open'])
            
            if lower_wick > body * 1.5:
                sweeps.append({
                    'type': 'SELL_SIDE_SWEEP',
                    'level': pool_price,
                    'sweep_low': current['low'],
                    'sweep_amount': (pool_price - current['low']) / pool_price * 100,
                    'wick_size': lower_wick,
                    'body_size': body,
                    'signal': 'CALL',  # Despues de sweep sell-side, esperar CALL
                    'confidence': 80 if lower_wick > body * 2 else 60
                })
    
    return sweeps[0] if sweeps else None

def detect_market_structure(df):
    """
    Detecta estructura de mercado:
    - HH/HL = uptrend
    - LH/LL = downtrend
    - BOS (Break of Structure)
    - CHoCH (Change of Character)
    """
    if len(df) < 30:
        return {'trend': 'UNKNOWN', 'bos': None, 'choch': None}
    
    # Encontrar swing highs/lows
    swing_highs = []
    swing_lows = []
    
    for i in range(3, len(df) - 3):
        if df['high'].iloc[i] > df['high'].iloc[i-1] and df['high'].iloc[i] > df['high'].iloc[i-2] and \
           df['high'].iloc[i] > df['high'].iloc[i+1] and df['high'].iloc[i] > df['high'].iloc[i+2]:
            swing_highs.append({'price': df['high'].iloc[i], 'index': i})
        
        if df['low'].iloc[i] < df['low'].iloc[i-1] and df['low'].iloc[i] < df['low'].iloc[i-2] and \
           df['low'].iloc[i] < df['low'].iloc[i+1] and df['low'].iloc[i] < df['low'].iloc[i+2]:
            swing_lows.append({'price': df['low'].iloc[i], 'index': i})
    
    if len(swing_highs) < 2 or len(swing_lows) < 2:
        return {'trend': 'UNKNOWN', 'bos': None, 'choch': None}
    
    # Determinar tendencia
    last_high = swing_highs[-1]['price']
    prev_high = swing_highs[-2]['price']
    last_low = swing_lows[-1]['price']
    prev_low = swing_lows[-2]['price']
    
    if last_high > prev_high and last_low > prev_low:
        trend = 'UPTREND'
    elif last_high < prev_high and last_low < prev_low:
        trend = 'DOWNTREND'
    else:
        trend = 'RANGE'
    
    # Detectar BOS
    bos = None
    current_price = df.iloc[-1]['close']
    
    if trend == 'UPTREND' and current_price > last_high:
        bos = {'type': 'BOS_BULLISH', 'level': last_high}
    elif trend == 'DOWNTREND' and current_price < last_low:
        bos = {'type': 'BOS_BEARISH', 'level': last_low}
    
    # Detectar CHoCH (cambio de caracter)
    choch = None
    if trend == 'UPTREND' and current_price < last_low:
        choch = {'type': 'CHOCH_BEARISH', 'level': last_low}
    elif trend == 'DOWNTREND' and current_price > last_high:
        choch = {'type': 'CHOCH_BULLISH', 'level': last_high}
    
    return {
        'trend': trend,
        'bos': bos,
        'choch': choch,
        'last_high': last_high,
        'last_low': last_low,
        'swing_highs': swing_highs[-3:],
        'swing_lows': swing_lows[-3:]
    }

def analyze_asset(asset):
    """Analisis completo SMC"""
    print(f'\n{C}{"="*78}')
    print(f'  ANALIZANDO: {asset}')
    print(f'{"="*78}{X}')
    
    # Obtener datos
    df = market_data.get_candles(asset, timeframe=60, num_candles=250)
    if df is None or len(df) < 50:
        print(f'  {R}Sin datos suficientes{X}')
        return
    
    df = feature_engineer.add_technical_indicators(df)
    
    # 1. ESTRUCTURA DE MERCADO
    structure = detect_market_structure(df)
    print(f'\n{Y}--- ESTRUCTURA DE MERCADO ---{X}')
    print(f'  Tendencia: {structure["trend"]}')
    if structure['bos']:
        print(f'  {G}BOS detectado: {structure["bos"]["type"]} en {structure["bos"]["level"]:.5f}{X}')
    if structure['choch']:
        print(f'  {R}CHoCH detectado: {structure["choch"]["type"]} en {structure["choch"]["level"]:.5f}{X}')
    
    # 2. LIQUIDITY POOLS
    liquidity = detect_liquidity_pools(df)
    print(f'\n{Y}--- LIQUIDITY POOLS ---{X}')
    
    if liquidity['buy_side']:
        print(f'  {R}Buy-side Liquidity (stops arriba):{X}')
        for i, pool in enumerate(liquidity['buy_side'][:5]):
            dist = abs(pool['price'] - df.iloc[-1]['close']) / pool['price'] * 100
            print(f'    BSL{i+1}: {pool["price"]:.5f} ({dist:.3f}%) - Fuerza: {pool["strength"]}')
    
    if liquidity['sell_side']:
        print(f'  {G}Sell-side Liquidity (stops abajo):{X}')
        for i, pool in enumerate(liquidity['sell_side'][:5]):
            dist = abs(pool['price'] - df.iloc[-1]['close']) / pool['price'] * 100
            print(f'    SSL{i+1}: {pool["price"]:.5f} ({dist:.3f}%) - Fuerza: {pool["strength"]}')
    
    # 3. DETECTAR SWEEP
    sweep = detect_liquidity_sweep(df, liquidity)
    print(f'\n{Y}--- LIQUIDITY SWEEP ---{X}')
    
    if sweep:
        print(f'  {BOLD}{G if sweep["signal"] == "CALL" else R}SWEEP DETECTADO: {sweep["type"]}{X}')
        print(f'  Nivel: {sweep["level"]:.5f}')
        print(f'  Barrido: {sweep["sweep_amount"]:.3f}%')
        print(f'  Senal: {sweep["signal"]} (Confianza: {sweep["confidence"]}%)')
        print(f'  {Y}>>> El precio tomo liquidez y rechazo = oportunidad en direccion opuesta{X}')
    else:
        print(f'  {Y}Sin sweep reciente{X}')
        print(f'  {Y}>>> Esperando barrido de liquidez para entrar{X}')
    
    # 4. ANALISIS COMPLETO
    price = df.iloc[-1]['close']
    rsi = df.iloc[-1].get('rsi', 50)
    macd = df.iloc[-1].get('macd', 0)
    macd_sig = df.iloc[-1].get('macd_signal', 0)
    
    print(f'\n{Y}--- ANALISIS SMC COMPLETO ---{X}')
    print(f'  Precio: {price:.5f} | RSI: {rsi:.1f} | MACD: {macd:.5f}/{macd_sig:.5f}')
    
    # Determinar direccion basada en SMC
    signal = None
    confidence = 0
    reason = ''
    
    # Si hay sweep, operar en direccion del sweep
    if sweep:
        signal = sweep['signal']
        confidence = sweep['confidence']
        reason = f'{sweep["type"]} detectado - precio tomo liquidez y rechazo'
    
    # Si no hay sweep, buscar entrada en pullback
    else:
        # En uptrend: esperar pullback a soporte/SSL
        if structure['trend'] == 'UPTREND':
            if liquidity['sell_side']:
                nearest_ssl = liquidity['sell_side'][0]
                dist = abs(price - nearest_ssl['price']) / price * 100
                
                if dist < 0.05 and rsi < 40:
                    signal = 'CALL'
                    confidence = 70
                    reason = f'Uptrend + pullback a SSL ({dist:.3f}%) + RSI bajo'
                elif dist < 0.1 and rsi < 45:
                    signal = 'CALL'
                    confidence = 55
                    reason = f'Uptrend + cerca de SSL ({dist:.3f}%) + RSI bajo'
        
        # En downtrend: esperar pullback a resistencia/BSL
        elif structure['trend'] == 'DOWNTREND':
            if liquidity['buy_side']:
                nearest_bsl = liquidity['buy_side'][0]
                dist = abs(price - nearest_bsl['price']) / price * 100
                
                if dist < 0.05 and rsi > 60:
                    signal = 'PUT'
                    confidence = 70
                    reason = f'Downtrend + pullback a BSL ({dist:.3f}%) + RSI alto'
                elif dist < 0.1 and rsi > 55:
                    signal = 'PUT'
                    confidence = 55
                    reason = f'Downtrend + cerca de BSL ({dist:.3f}%) + RSI alto'
    
    if signal:
        print(f'\n{BOLD}{G if signal == "CALL" else R}>>> SENAL: {signal} (Confianza: {confidence}%){X}')
        print(f'  Razon: {reason}')
    else:
        print(f'\n{Y}>>> SIN SENAL: Esperando setup SMC claro{X}')
    
    return signal, confidence, df

# Ejecutar analisis
print(f'\n{C}INICIANDO ANALISIS SMC LIQUIDITY...{X}')

for asset in assets:
    analyze_asset(asset)
    time.sleep(2)

print(f'\n{C}{"="*78}')
print(f'ANALISIS COMPLETADO')
print(f'{"="*78}{X}')
