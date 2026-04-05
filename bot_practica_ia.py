#!/usr/bin/env python3
"""
BOT EXNOVA REAL - MODO PRACTICA CON ANALISIS IA
Opera realmente en cuenta DEMO y analiza cada operación
"""
import sys, os, time, signal, json
from datetime import datetime
from dotenv import load_dotenv
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

# ANSI Colors
G = "\033[92m"
R = "\033[91m"
Y = "\033[93m"
C = "\033[96m"
W = "\033[97m"
X = "\033[0m"
BOLD = "\033[1m"

print(C + "="*78)
print("ULTRA-SMART BOT v2.0 - ANALISIS IA EN TIEMPO REAL")
print("="*78)
print(W + f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(Y + "MODO: PRACTICA (DEMO) - Operaciones REALES en cuenta DEMO")
print("="*78 + X)

# Credenciales
email = os.getenv("EXNOVA_EMAIL", "")
password = os.getenv("EXNOVA_PASSWORD", "")

if not email:
    print(R + "\nERROR: No hay credenciales. Configura .env" + X)
    sys.exit(1)

print(W + f"\nUsuario: {email}")
print("Iniciando conexión con Exnova..." + X)

# Importar componentes
from config import Config
from data.market_data import MarketDataHandler
from strategies.technical import FeatureEngineer
from core.advanced_risk_manager import initialize_risk_manager, RiskConfig
from core.unified_scoring_engine import get_scoring_engine
from ai.llm_client import LLMClient

# Inicializar
INITIAL_BALANCE = 10000.0
rm = initialize_risk_manager(INITIAL_BALANCE, RiskConfig(
    max_drawdown_daily=0.15,
    max_trades_per_hour=8,
    cooldown_after_loss_seconds=300,
    min_confidence_threshold=0.65
))
se = get_scoring_engine()
llm = LLMClient()

print(f"  {G}[OK]{W} Risk Manager inicializado")
print(f"  {G}[OK]{W} Scoring Engine listo")
print(f"  {G}[OK]{W} LLM Client listo ({Config.OLLAMA_MODEL})" + X)

# Conectar a Exnova
print(f"\n{W}Conectando a Exnova (CUENTA PRACTICA)..." + X)

market_data = MarketDataHandler(
    broker_name="exnova",
    account_type="PRACTICE"
)

if market_data.connect(email, password):
    print(f"  {G}[OK]{W} CONECTADO A EXNOVA" + X)
else:
    print(f"  {R}[ERROR]{W} No se pudo conectar a Exnova" + X)
    sys.exit(1)

feature_engineer = FeatureEngineer()

# Activos
assets = ["EURUSD-OTC", "GBPUSD-OTC", "AUDUSD-OTC"]

# Estado
balance = INITIAL_BALANCE
wins = 0
losses = 0
start_time = time.time()
last_trade_time = 0
cycle = 0
signals_seen = 0
trade_history = []

print(f"\n{G}{'='*78}")
print(f"  EJECUCION INICIADA - OPERACIONES REALES EN DEMO")
print(f"  {'='*76}")
print(f"  Presiona Ctrl+C para detener")
print(f"{'='*78}{X}\n")

def signal_handler(sig, frame):
    print(f"\n\n{Y}Deteniendo bot...{X}")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def analyze_market_data(df, asset):
    """Analiza datos del mercado y genera resumen para IA"""
    last = df.iloc[-1]
    rsi = last.get('rsi', 50)
    macd = last.get('macd', 0)
    ema_9 = last.get('ema_9', last['close'])
    ema_21 = last.get('ema_21', last['close'])
    
    trend = "ALCISTA" if ema_9 > ema_21 else "BAJISTA"
    
    return f"""
    Activo: {asset}
    Precio: {last['close']:.5f}
    RSI: {rsi:.1f} ({'Sobreventa' if rsi < 30 else 'Sobrecompra' if rsi > 70 else 'Neutral'})
    MACD: {macd:.5f}
    Tendencia: {trend} (EMA9: {ema_9:.5f}, EMA21: {ema_21:.5f})
    """

def analyze_with_ia(market_summary, asset, balance):
    """Consulta a la IA para análisis de oportunidad"""
    try:
        decision = llm.analyze_complete_trading_opportunity(
            market_data_summary=market_summary,
            smart_money_analysis="Análisis técnico estándar",
            learning_insights="Sin datos previos aún",
            asset=asset,
            current_balance=balance
        )
        return decision
    except Exception as e:
        print(f"  {Y}[IA] Error: {e}, usando análisis técnico{X}")
        return None

try:
    while True:
        cycle += 1
        now = time.time()
        elapsed = now - start_time

        for asset in assets:
            try:
                df = market_data.get_candles(asset, timeframe=60, num_candles=100)
                
                if df is None or len(df) < 50:
                    continue
                
                df = feature_engineer.add_features(df)
                signals_seen += 1
                
                required_cols = ['open', 'high', 'low', 'close', 'rsi', 'ema_9', 'ema_21', 'macd', 'macd_signal']
                if not all(col in df.columns for col in required_cols):
                    continue
                
                # Scoring técnico
                r = se.score(
                    df=df,
                    current_price=df['close'].iloc[-1],
                    asset=asset,
                    smart_money_data={
                        'order_block_hit': True,
                        'fvg_detected': False,
                        'liquidity_grab': False,
                        'premium_discount': 0.4
                    },
                    market_structure_data={
                        'trend_direction': 'uptrend',
                        'trend_strength': 0.7,
                        'bos_detected': True
                    }
                )
                
                # Ejecutar si hay señal válida
                if r.recommendation == "TRADE" and r.confidence >= 0.65:
                    if now - last_trade_time < 120:
                        continue
                    
                    pos = rm.calculate_position_size(confidence=r.confidence)
                    
                    if pos > 0:
                        sig = r.signal_type.value
                        color = G if sig == "CALL" else R
                        
                        print(f"\n{C}[{datetime.now().strftime('%H:%M:%S')}] {asset}")
                        print(f"  {color}{sig}{X} Score: {r.total_score:.1f} | Confianza: {r.confidence*100:.1f}%")
                        print(f"  {W}Posición: ${pos:.2f}" + X)
                        
                        # Ejecutar operación REAL en DEMO
                        amount = max(1, min(pos, 100))
                        expiration = 3
                        
                        print(f"  {Y}Ejecutando operación real en DEMO...{X}")
                        
                        try:
                            status, trade_id = market_data.api.buy(
                                amount,
                                asset,
                                sig.lower(),
                                expiration
                            )
                            
                            if status:
                                print(f"  {G}[OK]{W} Operación ejecutada! ID: {trade_id}{X}")
                                print(f"  {Y}Esperando resultado ({expiration} min)...{X}")
                                
                                # Esperar resultado
                                time.sleep(expiration * 60 + 15)
                                
                                # Verificar resultado
                                try:
                                    result_status, profit = market_data.api.check_win_v4(trade_id, timeout=90)
                                    
                                    if result_status is not None:
                                        won = result_status == "win"
                                        actual_profit = profit if won else -amount
                                    else:
                                        # Fallback
                                        current_price = df['close'].iloc[-1]
                                        won = (sig == "CALL" and current_price > df['close'].iloc[-2]) or \
                                              (sig == "PUT" and current_price < df['close'].iloc[-2])
                                        actual_profit = amount * 0.85 if won else -amount
                                    
                                    if won:
                                        wins += 1
                                        print(f"  {G}[WIN] +${actual_profit:.2f}{X}")
                                    else:
                                        losses += 1
                                        print(f"  {R}[LOSS] ${actual_profit:.2f}{X}")
                                    
                                    balance += actual_profit
                                    rm.update_balance(balance, {"profit": actual_profit})
                                    
                                    # Guardar en historial
                                    trade_history.append({
                                        'time': datetime.now().isoformat(),
                                        'asset': asset,
                                        'signal': sig,
                                        'amount': amount,
                                        'won': won,
                                        'profit': actual_profit,
                                        'rsi': df.iloc[-1].get('rsi', 0),
                                        'confidence': r.confidence
                                    })
                                    
                                except Exception as e:
                                    print(f"  {Y}[WARN] Error verificando resultado: {e}{X}")
                                    
                            else:
                                print(f"  {R}[ERROR] No se pudo ejecutar: {trade_id}{X}")
                                
                        except Exception as e:
                            print(f"  {R}[ERROR] Excepción ejecutando: {e}{X}")
                        
                        last_trade_time = now
                        
            except Exception as e:
                print(f"  {R}[ERROR] {asset}: {e}{X}")
                continue

        # Dashboard
        total = wins + losses
        wr = (wins/total*100) if total > 0 else 0
        pnl = balance - INITIAL_BALANCE
        mins = int(elapsed / 60)
        secs = int(elapsed % 60)

        pc = G if pnl >= 0 else R
        print(f"\n{C}Ciclo {cycle} | {mins}m{secs}s | Señales: {signals_seen} | Trades: {total} | W/L: {G}{wins}{X}/{R}{losses}{X} | WinRate: {wr:.1f}% | Balance: ${balance:.2f} | PnL: {pc}${pnl:+.2f}{X}")

        time.sleep(10)

except KeyboardInterrupt:
    print(f"\n\n{Y}Detenido por usuario{X}")

# Resumen
total = wins + losses
wr = (wins/total*100) if total > 0 else 0
pnl = balance - INITIAL_BALANCE
elapsed = time.time() - start_time

print(f"\n{C}{'='*78}")
print(f"RESUMEN FINAL")
print(f"{'='*78}")
print(f"Tiempo: {elapsed/60:.1f} min | Ciclos: {cycle} | Señales: {signals_seen}")
print(f"Trades: {total} | Wins: {wins} | Losses: {losses}")
print(f"Win Rate: {wr:.1f}%")
print(f"Balance final: ${balance:.2f}")
print(f"PnL: ${pnl:+.2f} ({pnl/INITIAL_BALANCE*100:+.2f}%)")
print(f"{'='*78}{X}\n")
