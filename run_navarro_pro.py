#!/usr/bin/env python3
"""
BOT EXNOVA - NAVARRO + LIQUIDEZ + RECONEXION AUTOMATICA
Con manejo robusto de reconexion
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

print(C + "="*70)
print("BOT EXNOVA - NAVARRO + RECONEXION AUTOMATICA")
print("="*70)
print(f"Iniciado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*70 + X)

email = os.getenv('EXNOVA_EMAIL', '')
password = os.getenv('EXNOVA_PASSWORD', '')

# Variables globales para reconexion
market_data = None
feature_engineer = FeatureEngineer()
reconnect_count = 0

def conectar_exnova(max_intentos=5):
    """Conecta a Exnova con reintentos"""
    global market_data, reconnect_count
    
    for intento in range(max_intentos):
        try:
            print(f"{Y}Intento de conexion {intento+1}/{max_intentos}...{X}")
            market_data = MarketDataHandler(broker_name='exnova', account_type='PRACTICE')
            
            if market_data.connect(email, password):
                print(f"{G}[OK] CONECTADO{X}")
                reconnect_count += 1
                try:
                    market_data.api.update_ACTIVES_OPCODE()
                except:
                    pass
                return True
            else:
                print(f"{Y}Intento fallido, esperando...{X}")
                time.sleep(3)
        except Exception as e:
            print(f"{Y}Error: {str(e)[:50]}, reintentando...{X}")
            time.sleep(3)
    
    return False

def obtener_datos(asset):
    """Obtiene datos con manejo de errores de red"""
    global market_data
    
    for intento in range(3):
        try:
            df = market_data.get_candles(asset, timeframe=60, num_candles=200)
            if df is not None and len(df) >= 50:
                return df
            time.sleep(2)
        except Exception as e:
            err_str = str(e).lower()
            if 'reconnect' in err_str or 'connection' in err_str or 'getaddrinfo' in err_str:
                print(f"{Y}Conexion perdida, reconectando...{X}")
                if conectar_exnova():
                    time.sleep(3)
                else:
                    time.sleep(10)
            else:
                time.sleep(2)
    return None

# Conexion inicial
if not conectar_exnova():
    print(f"{R}FATAL: No se pudo conectar{X}")
    sys.exit(1)

try:
    balance = market_data.get_balance()
    print(f"{C}Balance: ${balance}{X}")
except:
    balance = 10000.0

# Configuracion
MAX_TRADES_PER_HOUR = 10
MIN_COOLDOWN = 300
MIN_SCORE = 50

assets = ['EURUSD-OTC', 'GBPUSD-OTC', 'AUDUSD-OTC', 'USDJPY-OTC', 'EURJPY-OTC', 'EURGBP-OTC']

wins = 0
losses = 0
start_time = time.time()
last_trade_time = 0
trade_history = []
trades_this_hour = []
hour_start = time.time()

def find_fractal_resistance(df):
    highs = df['high'].values
    resistencias = []
    for i in range(2, len(highs)-2):
        if highs[i] >= highs[i-2] and highs[i] >= highs[i-1] and highs[i] >= highs[i+1] and highs[i] >= highs[i+2]:
            if df['high'].iloc[-1] > highs[i] * 0.98:
                resistencias.append(highs[i])
    unique = []
    for r in sorted(resistencias, reverse=True):
        if not any(abs(r-u)/r < 0.0001 for u in unique):
            unique.append(r)
    return unique[:8]

def find_fractal_support(df):
    lows = df['low'].values
    soportes = []
    for i in range(2, len(lows)-2):
        if lows[i] <= lows[i-2] and lows[i] <= lows[i-1] and lows[i] <= lows[i+1] and lows[i] <= lows[i+2]:
            if df['low'].iloc[-1] < lows[i] * 1.02:
                soportes.append(lows[i])
    unique = []
    for s in sorted(soportes):
        if not any(abs(s-u)/s < 0.0001 for u in unique):
            unique.append(s)
    return unique[:8]

def analyze_asset(asset):
    df = obtener_datos(asset)
    if df is None:
        return None
    
    try:
        df = feature_engineer.add_technical_indicators(df)
        price = df.iloc[-1]['close']
        rsi = df.iloc[-1].get('rsi', 50)
        macd = df.iloc[-1].get('macd', 0)
        macd_sig = df.iloc[-1].get('macd_signal', 0)
        
        current = df.iloc[-1]
        body = abs(current['close'] - current['open'])
        if body == 0: body = 0.00001
        upper_wick = current['high'] - max(current['open'], current['close'])
        lower_wick = min(current['open'], current['close']) - current['low']
        
        resistencias = find_fractal_resistance(df)
        soportes = find_fractal_support(df)
        
        nearest_r = min(resistencias, key=lambda x: abs(x-price)) if resistencias else None
        nearest_s = min(soportes, key=lambda x: abs(x-price)) if soporte else None
        
        dist_r = abs(price-nearest_r)/price*100 if nearest_r else 999
        dist_s = abs(price-nearest_s)/price*100 if nearest_s else 999
        
        call_score = 0
        put_score = 0
        reasons = []
        
        # S/R
        if dist_s < 0.03:
            call_score += 30
            reasons.append(f"cerca S ({dist_s:.2f}%)")
        if dist_r < 0.03:
            put_score += 30
            reasons.append(f"cerca R ({dist_r:.2f}%)")
        
        # RSI
        if rsi < 30:
            call_score += 25
            reasons.append(f"RSI {rsi:.0f}")
        elif rsi > 70:
            put_score += 25
            reasons.append(f"RSI {rsi:.0f}")
        
        # MACD
        if macd > macd_sig:
            call_score += 15
        elif macd < macd_sig:
            put_score += 15
        
        # Liquidez (mecha)
        if nearest_s and dist_s < 0.02 and lower_wick > body * 0.8:
            call_score += 15
            reasons.append("mecha en S")
        if nearest_r and dist_r < 0.02 and upper_wick > body * 0.8:
            put_score += 15
            reasons.append("mecha en R")
        
        if call_score >= MIN_SCORE and call_score > put_score:
            return {"asset": asset, "signal": "CALL", "score": call_score, "reasons": reasons, "rsi": rsi}
        elif put_score >= MIN_SCORE and put_score > call_score:
            return {"asset": asset, "signal": "PUT", "score": put_score, "reasons": reasons, "rsi": rsi}
        
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
    if now - last_trade_time < MIN_COOLDOWN:
        return False, "cooldown"
    return True, "ok"

cycle = 0
try:
    while True:
        cycle += 1
        now = time.time()
        
        print(f"\n--- Ciclo {cycle} | {datetime.now().strftime('%H:%M:%S')} | Reconexiones: {reconnect_count} ---")
        
        puede, reason = can_trade()
        if not puede:
            print(f"{Y}{reason}, esperando...{X}")
            time.sleep(60)
            continue
        
        # Analisis
        opportunities = []
        for asset in assets:
            opp = analyze_asset(asset)
            if opp:
                opportunities.append(opp)
                print(f"  {G if opp['signal']=='CALL' else R}{asset}: {opp['signal']} ({opp['score']}){X}")
        
        if not opportunities:
            print(f"{Y}Sin senales{X}")
            time.sleep(90)
            continue
        
        best = max(opportunities, key=lambda x: x['score'])
        print(f"\n>>> {best['asset']} {best['signal']} (Score: {best['score']})")
        
        if best['score'] >= MIN_SCORE:
            delay = random.randint(3, 8)
            print(f"Ejecutando en {delay}s...")
            time.sleep(delay)
            
            try:
                print(f">>> {best['signal']} {best['asset']} $1 3min")
                status, trade_id = market_data.api.buy(1, best['asset'], best['signal'].lower(), 3)
                
                if status:
                    print(f"ID: {trade_id}")
                    time.sleep(3*60 + 20)
                    
                    # Verificar con reintentos de reconexion
                    result = None
                    for _ in range(5):
                        try:
                            result_status, profit = market_data.api.check_win_v4(trade_id, timeout=60)
                            if result_status:
                                result = (result_status, profit)
                                break
                        except Exception as e:
                            if 'reconnect' in str(e).lower():
                                conectar_exnova()
                            time.sleep(5)
                    
                    if result:
                        won = result[0] == "win"
                        profit = result[1] if won else -1
                        if won:
                            wins += 1
                        else:
                            losses += 1
                        balance += profit
                        last_trade_time = time.time()
                        trades_this_hour.append(last_trade_time)
                        print(f"{G if won else R}{'WIN' if won else 'LOSS'} | ${profit if won else -1}{X}")
                    else:
                        print(f"{Y}TIMEOUT{X}")
            except Exception as e:
                print(f"Error: {e}")
                if 'reconnect' in str(e).lower():
                    conectar_exnova()
        
        # Resumen
        total = wins + losses
        wr = (wins/total*100) if total > 0 else 0
        mins = int((now - start_time)/60)
        pnl = balance - 10000
        print(f"Resumen: {mins}min | W:{wins} L:{losses} | WR:{wr:.0f}% | ${pnl:+.0f}")
        
        time.sleep(random.randint(240, 360))

except KeyboardInterrupt:
    print(f"\n{Y}Detenido{X}")
    if trade_history:
        with open(f"data/navarro_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "w") as f:
            json.dump(trade_history, f, indent=2)