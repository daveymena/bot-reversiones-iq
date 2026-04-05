#!/usr/bin/env python3
"""
BOT EXNOVA - ANALISIS MULTI-TIMEFRAME CON S/R MACRO
Usa M15/M30 para soportes/resistencias y M1 para entrada precisa
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
print("ANALISIS MULTI-TIMEFRAME: S/R MACRO + ENTRADA M1")
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
    market_data.api.update_ACTIVES_OPCODE()
except: pass

feature_engineer = FeatureEngineer()

assets = ['EURUSD-OTC', 'GBPUSD-OTC', 'AUDUSD-OTC']

def find_support_resistance(df, lookback=50):
    """Encuentra niveles de S/R reales en el timeframe dado"""
    if len(df) < 20:
        return [], []
    
    highs = df['high'].tail(lookback).values
    lows = df['low'].tail(lookback).values
    
    # Encontrar maximos y minimos locales
    resistances = []
    supports = []
    
    # Metodo 1: Maximos/minimos locales (requiere 2 velas a cada lado)
    for i in range(2, len(highs) - 2):
        if highs[i] > highs[i-1] and highs[i] > highs[i-2] and \
           highs[i] > highs[i+1] and highs[i] > highs[i+2]:
            resistances.append(highs[i])
    
    for i in range(2, len(lows) - 2):
        if lows[i] < lows[i-1] and lows[i] < lows[i-2] and \
           lows[i] < lows[i+1] and lows[i] < lows[i+2]:
            supports.append(lows[i])
    
    # Metodo 2: Si no se encontraron suficientes, usar maximos/minimos absolutos
    if len(resistances) < 2:
        # Agregar los highs mas altos como resistencias
        sorted_highs = sorted(highs, reverse=True)
        for h in sorted_highs[:3]:
            if not any(abs(h - r) / h < 0.001 for r in resistances):
                resistances.append(h)
    
    if len(supports) < 2:
        # Agregar los lows mas bajos como soportes
        sorted_lows = sorted(lows)
        for l in sorted_lows[:3]:
            if not any(abs(l - s) / l < 0.001 for s in supports):
                supports.append(l)
    
    # Ordenar y tomar los mas relevantes
    resistances = sorted(list(set(resistances)), reverse=True)[:5]
    supports = sorted(list(set(supports)))[:5]
    
    return resistances, supports

def analyze_multi_timeframe(asset):
    """Analisis completo: S/R de M15/M30 + entrada M1"""
    print(f'\n{C}{"="*78}')
    print(f'  ANALIZANDO: {asset}')
    print(f'{"="*78}{X}')
    
    # 1. OBTENER M15 (Soportes/Resistencias MACRO)
    try:
        df_m15 = market_data.get_candles(asset, timeframe=900, num_candles=50)
        if df_m15 is not None and len(df_m15) >= 20:
            df_m15 = feature_engineer.add_technical_indicators(df_m15)
            m15_res, m15_supp = find_support_resistance(df_m15, lookback=30)
            
            print(f'\n{Y}--- M15 (Soportes/Resistencias MACRO) ---{X}')
            print(f'  Velas analizadas: {len(df_m15)}')
            
            if m15_res:
                print(f'  {R}Resistencias M15:{X}')
                for i, res in enumerate(m15_res[:3]):
                    print(f'    R{i+1}: {res:.5f}')
            else:
                print(f'  {R}No se detectaron resistencias claras en M15{X}')
            
            if m15_supp:
                print(f'  {G}Soportes M15:{X}')
                for i, supp in enumerate(m15_supp[:3]):
                    print(f'    S{i+1}: {supp:.5f}')
            else:
                print(f'  {G}No se detectaron soportes claros en M15{X}')
            
            # Precio actual en contexto M15
            m15_price = df_m15.iloc[-1]['close']
            print(f'  Precio M15: {m15_price:.5f}')
            
            # Determinar zona M15
            nearest_res = min(m15_res, key=lambda x: abs(x - m15_price)) if m15_res else None
            nearest_supp = min(m15_supp, key=lambda x: abs(x - m15_price)) if m15_supp else None
            dist_to_res = abs(nearest_res - m15_price) / m15_price * 100 if nearest_res else 999
            dist_to_supp = abs(m15_price - nearest_supp) / m15_price * 100 if nearest_supp else 999
            
            if nearest_res:
                print(f'  Distancia a R mas cercana: {dist_to_res:.3f}%')
            if nearest_supp:
                print(f'  Distancia a S mas cercana: {dist_to_supp:.3f}%')
        else:
            print(f'{R}  Sin datos M15 suficientes{X}')
            m15_res, m15_supp = [], []
            nearest_res, nearest_supp = None, None
            dist_to_res, dist_to_supp = 999, 999
    except Exception as e:
        print(f'{R}  Error M15: {e}{X}')
        m15_res, m15_supp = [], []
        nearest_res, nearest_supp = None, None
        dist_to_res, dist_to_supp = 999, 999
    
    # 2. OBTENER M30 (Confirmacion de tendencia)
    try:
        df_m30 = market_data.get_candles(asset, timeframe=1800, num_candles=30)
        if df_m30 is not None and len(df_m30) >= 10:
            df_m30 = feature_engineer.add_technical_indicators(df_m30)
            m30_price = df_m30.iloc[-1]['close']
            m30_rsi = df_m30.iloc[-1].get('rsi', 50)
            
            # Tendencia M30
            if len(df_m30) >= 10:
                sma_10 = df_m30['close'].tail(10).mean()
                m30_trend = 'ALCISTA' if m30_price > sma_10 else 'BAJISTA'
            else:
                m30_trend = 'DESCONOCIDA'
            
            print(f'\n{Y}--- M30 (Tendencia MACRO) ---{X}')
            print(f'  Precio M30: {m30_price:.5f}')
            print(f'  RSI M30: {m30_rsi:.1f}')
            print(f'  Tendencia M30: {m30_trend}')
        else:
            m30_trend = 'DESCONOCIDA'
            m30_rsi = 50
    except Exception as e:
        print(f'{R}  Error M30: {e}{X}')
        m30_trend = 'DESCONOCIDA'
        m30_rsi = 50
    
    # 3. OBTENER M1 (Punto de entrada preciso)
    try:
        df_m1 = market_data.get_candles(asset, timeframe=60, num_candles=100)
        if df_m1 is not None and len(df_m1) >= 50:
            df_m1 = feature_engineer.add_technical_indicators(df_m1)
            m1_price = df_m1.iloc[-1]['close']
            m1_rsi = df_m1.iloc[-1].get('rsi', 50)
            m1_macd = df_m1.iloc[-1].get('macd', 0)
            m1_macd_sig = df_m1.iloc[-1].get('macd_signal', 0)
            
            # Bollinger M1
            bb_upper = df_m1.iloc[-1].get('bb_high', m1_price)
            bb_lower = df_m1.iloc[-1].get('bb_low', m1_price)
            
            print(f'\n{Y}--- M1 (PUNTO DE ENTRADA) ---{X}')
            print(f'  Precio M1: {m1_price:.5f}')
            print(f'  RSI M1: {m1_rsi:.1f}')
            print(f'  MACD: {m1_macd:.5f} / Signal: {m1_macd_sig:.5f}')
            print(f'  BB Upper: {bb_upper:.5f} | BB Lower: {bb_lower:.5f}')
            
            # Determinar posicion respecto a S/R M15
            if nearest_res and nearest_supp:
                dist_m1_to_res = abs(nearest_res - m1_price) / m1_price * 100
                dist_m1_to_supp = abs(m1_price - nearest_supp) / m1_price * 100
                
                print(f'\n  Posicion M1 respecto a S/R M15:')
                print(f'    Distancia a R M15: {dist_m1_to_res:.3f}%')
                print(f'    Distancia a S M15: {dist_m1_to_supp:.3f}%')
                
                # ANALISIS DE OPORTUNIDAD
                print(f'\n{BOLD}{Y}--- ANALISIS DE OPORTUNIDAD ---{X}')
                
                # REGLA DE ORO: Comprar en SOPORTE, Vender en RESISTENCIA
                # El precio debe estar CERCA del soporte para CALL, CERCA de resistencia para PUT
                
                # CALL: Precio cerca de SOPORTE M15, RSI M1 bajo, MACD cruzando arriba
                near_support = dist_m1_to_supp < 0.05  # Dentro de 0.05% del soporte
                rsi_oversold = m1_rsi < 35
                macd_bullish = m1_macd > m1_macd_sig
                
                # PUT: Precio cerca de RESISTENCIA M15, RSI M1 alto, MACD cruzando abajo
                near_resistance = dist_m1_to_res < 0.05  # Dentro de 0.05% de resistencia
                rsi_overbought = m1_rsi > 65
                macd_bearish = m1_macd < m1_macd_sig
                
                # Calcular score
                call_score = 0
                put_score = 0
                
                if near_support:
                    call_score += 40
                    print(f'  {G}[+40] Precio cerca de SOPORTE M15 ({dist_m1_to_supp:.3f}%){X}')
                else:
                    print(f'  {R}[-00] Precio LEJOS de soporte M15 ({dist_m1_to_supp:.3f}%){X}')
                
                if near_resistance:
                    put_score += 40
                    print(f'  {G}[+40] Precio cerca de RESISTENCIA M15 ({dist_m1_to_res:.3f}%){X}')
                else:
                    print(f'  {R}[-00] Precio LEJOS de resistencia M15 ({dist_m1_to_res:.3f}%){X}')
                
                if rsi_oversold:
                    call_score += 25
                    print(f'  {G}[+25] RSI M1 sobreventa ({m1_rsi:.1f}){X}')
                elif rsi_overbought:
                    put_score += 25
                    print(f'  {G}[+25] RSI M1 sobrecompra ({m1_rsi:.1f}){X}')
                else:
                    print(f'  {Y}[+00] RSI M1 neutral ({m1_rsi:.1f}){X}')
                
                if macd_bullish:
                    call_score += 20
                    print(f'  {G}[+20] MACD M1 alcista{X}')
                elif macd_bearish:
                    put_score += 20
                    print(f'  {G}[+20] MACD M1 bajista{X}')
                
                # Tendencia M30 a favor
                if m30_trend == 'ALCISTA':
                    call_score += 15
                    print(f'  {G}[+15] Tendencia M30 alcista (a favor de CALL){X}')
                elif m30_trend == 'BAJISTA':
                    put_score += 15
                    print(f'  {G}[+15] Tendencia M30 bajista (a favor de PUT){X}')
                
                # Precio entre BB
                if m1_price <= bb_lower * 1.001:
                    call_score += 10
                    print(f'  {G}[+10] Precio en BB inferior (zona de compra){X}')
                elif m1_price >= bb_upper * 0.999:
                    put_score += 10
                    print(f'  {G}[+10] Precio en BB superior (zona de venta){X}')
                
                print(f'\n  SCORE CALL: {call_score}/100')
                print(f'  SCORE PUT:  {put_score}/100')
                
                # Decision
                min_score = 60
                if call_score >= min_score and call_score > put_score:
                    print(f'\n{BOLD}{G}>>> SENAL: CALL en {asset} (Score: {call_score}) <<<{X}')
                    print(f'  Razon: Precio en soporte M15 + RSI bajo + confirmacion M1')
                    return 'CALL', call_score, df_m1
                elif put_score >= min_score and put_score > call_score:
                    print(f'\n{BOLD}{R}>>> SENAL: PUT en {asset} (Score: {put_score}) <<<{X}')
                    print(f'  Razon: Precio en resistencia M15 + RSI alto + confirmacion M1')
                    return 'PUT', put_score, df_m1
                else:
                    print(f'\n{Y}>>> SIN SENAL: Scores insuficientes <<<{X}')
                    return None, max(call_score, put_score), df_m1
            else:
                print(f'\n{Y}  Sin S/R claros en M15, no se puede analizar{X}')
                return None, 0, df_m1
        else:
            print(f'{R}  Sin datos M1 suficientes{X}')
            return None, 0, None
    except Exception as e:
        print(f'{R}  Error M1: {e}{X}')
        return None, 0, None

# Ejecutar analisis
print(f'\n{C}INICIANDO ANALISIS MULTI-TIMEFRAME...{X}')

for asset in assets:
    signal, score, df = analyze_multi_timeframe(asset)
    time.sleep(2)

print(f'\n{C}{"="*78}')
print(f'ANALISIS COMPLETADO')
print(f'{"="*78}{X}')
