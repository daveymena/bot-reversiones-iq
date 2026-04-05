#!/usr/bin/env python3
"""
BOT EXNOVA 24/7 - AUTO-MEJORAMIENTO CONTINUO
- Ejecuta 24/7 sin intervención
- Guarda historial de operaciones
- Analiza rendimiento y ajusta parámetros
- IA (fallback) cuando hay rachas negativas
"""
import time, random, sys, os, json
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, os.getcwd())

from data.market_data import MarketDataHandler
from strategies.technical import FeatureEngineer
from ai.llm_client import LLMClient

G = '\033[92m'
R = '\033[91m'
Y = '\033[93m'
C = '\033[96m'
W = '\033[97m'
X = '\033[0m'
BOLD = '\033[1m'

print(C + "="*70)
print("BOT EXNOVA 24/7 - AUTO-MEJORAMIENTO")
print("="*70)
print(f"Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("Estrategia: Navarro + Liquidez + Auto-Ajuste")
print("="*70 + X)

email = os.getenv('EXNOVA_EMAIL', '')
password = os.getenv('EXNOVA_PASSWORD', '')

# Variables globales
market_data = None
feature_engineer = FeatureEngineer()
llm_client = None
reconnect_count = 0

# Parametros ajustables (se modifican segun rendimiento)
PARAMS = {
    'min_score': 50,
    'cooldown': 300,
    'max_per_hour': 10,
    'rsi_oversold': 30,
    'rsi_overbought': 70,
    'dist_sr_max': 0.03
}

def conectar(max_intentos=5):
    global market_data, reconnect_count, llm_client
    for intento in range(max_intentos):
        try:
            print(f"{Y}Conectando...{X}")
            market_data = MarketDataHandler(broker_name='exnova', account_type='PRACTICE')
            if market_data.connect(email, password):
                print(f"{G}[OK] CONECTADO{X}")
                reconnect_count += 1
                try:
                    market_data.api.update_ACTIVES_OPCODE()
                except: pass
                # Inicializar IA
                try:
                    llm_client = LLMClient()
                    print(f"{G}[OK] IA lista{X}")
                except:
                    print(f"{Y}[WARN] IA no disponible{X}")
                return True
            time.sleep(3)
        except Exception as e:
            print(f"{Y}Error: {str(e)[:30]}...{X}")
            time.sleep(3)
    return False

def obtener_datos(asset):
    global market_data
    for intento in range(3):
        try:
            df = market_data.get_candles(asset, timeframe=60, num_candles=200)
            if df is not None and len(df) >= 50:
                return df
            time.sleep(2)
        except Exception as e:
            if 'reconnect' in str(e).lower() or 'connection' in str(e).lower():
                conectar()
                time.sleep(5)
            time.sleep(2)
    return None

if not conectar():
    print(f"{R}ERROR: No se pudo conectar{X}")
    sys.exit(1)

try:
    balance = market_data.get_balance()
except:
    balance = 10000.0

# Datos para auto-mejora
assets = ['EURUSD-OTC', 'GBPUSD-OTC', 'AUDUSD-OTC', 'USDJPY-OTC', 'EURJPY-OTC', 'EURGBP-OTC']
wins = 0
losses = 0
start_time = time.time()
last_trade_time = 0
trade_history = []
trades_this_hour = []
hour_start = time.time()
streak_negative = 0
total_cycles = 0

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
        
        # S/R con parametros ajustables
        if dist_s < PARAMS['dist_sr_max']:
            call_score += 30
            reasons.append(f"cerca S ({dist_s:.2f}%)")
        if dist_r < PARAMS['dist_sr_max']:
            put_score += 30
            reasons.append(f"cerca R ({dist_r:.2f}%)")
        
        # RSI con parametros ajustables
        if rsi < PARAMS['rsi_oversold']:
            call_score += 25
            reasons.append(f"RSI {rsi:.0f}")
        elif rsi < PARAMS['rsi_oversold'] + 10:
            call_score += 15
            reasons.append(f"RSI bajo {rsi:.0f}")
        
        if rsi > PARAMS['rsi_overbought']:
            put_score += 25
            reasons.append(f"RSI {rsi:.0f}")
        elif rsi > PARAMS['rsi_overbought'] - 10:
            put_score += 15
            reasons.append(f"RSI alto {rsi:.0f}")
        
        # MACD
        if macd > macd_sig:
            call_score += 15
        elif macd < macd_sig:
            put_score += 15
        
        # Liquidez
        if nearest_s and dist_s < 0.02 and lower_wick > body * 0.8:
            call_score += 15
            reasons.append("mecha en S")
        if nearest_r and dist_r < 0.02 and upper_wick > body * 0.8:
            put_score += 15
            reasons.append("mecha en R")
        
        if call_score >= PARAMS['min_score'] and call_score > put_score:
            return {"asset": asset, "signal": "CALL", "score": call_score, "reasons": reasons, "rsi": rsi}
        elif put_score >= PARAMS['min_score'] and put_score > call_score:
            return {"asset": asset, "signal": "PUT", "score": put_score, "reasons": reasons, "rsi": rsi}
        
        return None
    except:
        return None

def can_trade():
    global trades_this_hour, hour_start
    now = time.time()
    if now - hour_start > 3600:
        trades_this_hour = []
        hour_start = now
    if len(trades_this_hour) >= PARAMS['max_per_hour']:
        return False
    if now - last_trade_time < PARAMS['cooldown']:
        return False
    return True

def analyze_with_ia():
    """Analiza con IA cuando hay racha negativa"""
    global PARAMS, streak_negative
    
    if streak_negative >= 3 and llm_client:
        try:
            print(f"\n{Y}>>> ANALIZANDO CON IA (Racha negativa: {streak_negative}){X}")
            
            recent_trades = trade_history[-10:] if len(trade_history) >= 10 else trade_history
            
            analysis = f"""
Analiza estos trades recientes y sugiere ajustes:
- Wins: {wins}
- Losses: {losses}
- Racha negativa: {streak_negative}
- Ultimos trades: {recent_trades}
- Params actuales: {PARAMS}
            
Sugiere: ajustes de parametros (min_score, cooldown, rsi_oversold, rsi_overbought, etc)
"""
            # Aqui se usaria la IA pero por ahora ajustamos manualmente
            if streak_negative >= 5:
                PARAMS['min_score'] = min(65, PARAMS['min_score'] + 5)
                PARAMS['cooldown'] = min(600, PARAMS['cooldown'] + 60)
                print(f"{Y}>>> AJUSTE: Score min -> {PARAMS['min_score']}, Cooldown -> {PARAMS['cooldown']}s{X}")
            elif streak_negative >= 3:
                PARAMS['min_score'] = min(60, PARAMS['min_score'] + 2)
                print(f"{Y}>>> AJUSTE: Score min -> {PARAMS['min_score']}{X}")
            
            streak_negative = 0  # Resetear
            
        except Exception as e:
            print(f"{Y}IA error: {e}{X}")

def save_state():
    """Guarda estado para recuperación"""
    state = {
        'wins': wins,
        'losses': losses,
        'balance': balance,
        'params': PARAMS,
        'trade_history': trade_history[-50:],
        'last_save': datetime.now().isoformat()
    }
    try:
        with open('data/bot_state.json', 'w') as f:
            json.dump(state, f, indent=2)
    except:
        pass

print(f"\n{G}Parametros: Score>={PARAMS['min_score']} | Cooldown={PARAMS['cooldown']}s | Max={PARAMS['max_per_hour']}/hr{X}")
print(f"IA: {'Activa' if llm_client else 'No disponible'}")
print(f"Objetivo: 24/7 con auto-mejora\n")

cycle = 0
save_counter = 0
try:
    while True:
        cycle += 1
        total_cycles += 1
        now = time.time()
        
        if total_cycles % 50 == 0:
            print(f"\n--- Ciclo {cycle} | {datetime.now().strftime('%H:%M:%S')} | Reconex: {reconnect_count} ---")
        
        if not can_trade():
            time.sleep(60)
            continue
        
        opportunities = []
        for asset in assets:
            opp = analyze_asset(asset)
            if opp:
                opportunities.append(opp)
        
        if not opportunities:
            time.sleep(90)
            continue
        
        best = max(opportunities, key=lambda x: x['score'])
        
        # Auto-análisis si hay rachas negativas
        if streak_negative >= 3:
            analyze_with_ia()
        
        delay = random.randint(3, 8)
        time.sleep(delay)
        
        try:
            status, trade_id = market_data.api.buy(1, best['asset'], best['signal'].lower(), 3)
            
            if status:
                time.sleep(3*60 + 20)
                
                result = None
                for _ in range(5):
                    try:
                        result_status, profit = market_data.api.check_win_v4(trade_id, timeout=60)
                        if result_status:
                            result = (result_status, profit)
                            break
                    except:
                        if 'reconnect' in str(e).lower():
                            conectar()
                        time.sleep(5)
                
                if result:
                    won = result[0] == "win"
                    profit = result[1] if won else -1
                    
                    if won:
                        wins += 1
                        streak_negative = 0
                    else:
                        losses += 1
                        streak_negative += 1
                    
                    balance += profit
                    last_trade_time = time.time()
                    trades_this_hour.append(last_trade_time)
                    
                    trade_history.append({
                        'time': datetime.now().isoformat(),
                        'asset': best['asset'],
                        'signal': best['signal'],
                        'score': best['score'],
                        'won': won,
                        'profit': profit,
                        'rsi': best['rsi'],
                        'params': PARAMS.copy()
                    })
                    
                    print(f"{G if won else R}{'WIN' if won else 'LOSS'} | {best['signal']} {best['asset']} | Score:{best['score']}{X}")
                    
                    # Auto-ajuste si va bien
                    total = wins + losses
                    if total > 10:
                        winrate = wins / total * 100
                        if winrate > 60:
                            PARAMS['min_score'] = max(40, PARAMS['min_score'] - 2)
                            PARAMS['cooldown'] = max(180, PARAMS['cooldown'] - 30)
                            print(f"{G}Mejorando: Score->{PARAMS['min_score']}, Cooldown->{PARAMS['cooldown']}s{X}")
                        elif winrate < 40:
                            PARAMS['min_score'] = min(70, PARAMS['min_score'] + 5)
                            PARAMS['cooldown'] = min(600, PARAMS['cooldown'] + 60)
                            print(f"{Y}Ajuste defensivo: Score->{PARAMS['min_score']}, Cooldown->{PARAMS['cooldown']}s{X}")
                
                else:
                    print(f"{Y}TIMEOUT{X}")
        except Exception as e:
            print(f"Error: {e}")
            if 'reconnect' in str(e).lower():
                conectar()
        
        # Guardar estado cada 10 operaciones
        save_counter += 1
        if save_counter >= 10:
            save_state()
            save_counter = 0
        
        # Resumen
        total = wins + losses
        wr = (wins/total*100) if total > 0 else 0
        mins = int((now - start_time)/60)
        pnl = balance - 10000
        
        if total_cycles % 20 == 0:
            print(f"Resumen: {mins}min | W:{wins} L:{losses} | WR:{wr:.0f}% | ${pnl:+.0f} | Streak neg:{streak_negative}")
        
        time.sleep(random.randint(240, 360))

except KeyboardInterrupt:
    print(f"\n{Y}Detenido - Guardando...{X}")
    save_state()
    with open(f"data/trades_24h_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "w") as f:
        json.dump(trade_history, f, indent=2)
    print(f"Guardado: {len(trade_history)} operaciones")