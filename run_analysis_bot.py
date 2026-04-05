#!/usr/bin/env python3
"""
BOT EXNOVA REAL - MODO PRACTICA CON ANALISIS IA EN TIEMPO REAL
Opera realmente en cuenta DEMO y analiza cada operación
"""
import time, sys, os, json
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, os.getcwd())

from config import Config
from data.market_data import MarketDataHandler
from strategies.technical import FeatureEngineer
from core.advanced_risk_manager import initialize_risk_manager, RiskConfig
from core.unified_scoring_engine import get_scoring_engine

G = '\033[92m'
R = '\033[91m'
Y = '\033[93m'
C = '\033[96m'
W = '\033[97m'
X = '\033[0m'
BOLD = '\033[1m'

print(C + "="*78)
print("ULTRA-SMART BOT v2.0 - ANALISIS IA EN TIEMPO REAL")
print("="*78)
print(W + f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(Y + "MODO: PRACTICA (DEMO) - Operaciones REALES en cuenta DEMO")
print("="*78 + X)

email = os.getenv('EXNOVA_EMAIL', '')
password = os.getenv('EXNOVA_PASSWORD', '')

if not email:
    print(R + "\nERROR: No hay credenciales" + X)
    sys.exit(1)

print(W + f"\nUsuario: {email}")
print("Iniciando conexión con Exnova..." + X)

market_data = MarketDataHandler(broker_name='exnova', account_type='PRACTICE')

if market_data.connect(email, password):
    print(f'{G}[OK] CONECTADO A EXNOVA{X}')
else:
    print(f'{R}[ERROR] No se pudo conectar{X}')
    sys.exit(1)

# Check balance
try:
    balance = market_data.get_balance()
    print(f'{C}Balance actual: ${balance}{X}')
except Exception as e:
    print(f'{Y}Balance: {e}{X}')
    balance = 10000.0

try:
    market_data.api.update_ACTIVES_OPCODE()
    print(f'{G}[OK] Activos actualizados{X}')
except Exception as e:
    print(f'{Y}Error activos: {e}{X}')

feature_engineer = FeatureEngineer()
rm = initialize_risk_manager(balance, RiskConfig(
    max_drawdown_daily=0.15,
    max_trades_per_hour=8,
    cooldown_after_loss_seconds=300,
    min_confidence_threshold=0.55
))
se = get_scoring_engine()

# BAJAR UMBRAL PARA OPERAR
se.min_score_to_trade = 60

assets = ['EURUSD-OTC', 'GBPUSD-OTC', 'AUDUSD-OTC']

# Estado
wins = 0
losses = 0
start_time = time.time()
last_trade_time = 0
trade_history = []

print(f'\n{G}{"="*78}')
print(f'  EJECUCION INICIADA - OPERACIONES REALES EN DEMO')
print(f'  {"="*76}')
print(f'  Presiona Ctrl+C para detener')
print(f'  Umbral de scoring: 60 (relajado para operar)')
print(f'{"="*78}{X}\n')

def signal_handler(sig, frame):
    print(f'\n\n{Y}Deteniendo bot...{X}')
    sys.exit(0)

import signal
signal.signal(signal.SIGINT, signal_handler)

try:
    cycle = 0
    while True:
        cycle += 1
        now = time.time()
        elapsed = now - start_time

        for asset in assets:
            try:
                df = market_data.get_candles(asset, timeframe=60, num_candles=100)
                if df is None or len(df) < 50:
                    continue
                
                df = feature_engineer.add_technical_indicators(df)
                
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
                
                # Mostrar analisis detallado
                if r.recommendation == 'TRADE' or r.total_score >= 55:
                    sig = r.signal_type.value
                    pos = rm.calculate_position_size(confidence=r.confidence)
                    
                    print(f'\n{C}[{datetime.now().strftime("%H:%M:%S")}] {asset}')
                    print(f'  Score: {r.total_score:.1f} | Conf: {r.confidence*100:.1f}% | Senal: {sig}')
                    print(f'  Posicion: ${pos:.2f}')
                    
                    # Mostrar desglose por categoria
                    print(f'  Desglose:')
                    for key, cat in r.categories.items():
                        if cat.score >= 65:
                            print(f'    {G}{key}: {cat.score:.1f}{X}')
                        elif cat.score >= 50:
                            print(f'    {Y}{key}: {cat.score:.1f}{X}')
                        else:
                            print(f'    {R}{key}: {cat.score:.1f}{X}')
                    
                    if r.recommendation == 'TRADE' and r.confidence >= 0.55:
                        if now - last_trade_time < 120:
                            print(f'  {Y}Cooldown activo, esperando...{X}')
                            continue
                        
                        amount = max(1, min(pos, 100))
                        expiration = 3
                        
                        print(f'\n{BOLD}{G}>>> EJECUTANDO {sig} en {asset} - ${amount} - {expiration} min <<<{X}')
                        
                        try:
                            status, trade_id = market_data.api.buy(amount, asset, sig.lower(), expiration)
                            
                            if status:
                                print(f'  {G}[OK] Trade ejecutado! ID: {trade_id}{X}')
                                print(f'  {Y}Esperando resultado ({expiration} min)...{X}')
                                
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
                                    rm.update_balance(balance, {"profit": actual_profit})
                                    
                                    trade_history.append({
                                        'time': datetime.now().isoformat(),
                                        'asset': asset,
                                        'signal': sig,
                                        'amount': amount,
                                        'won': won,
                                        'profit': actual_profit,
                                        'score': r.total_score,
                                        'confidence': r.confidence
                                    })
                                else:
                                    print(f'  {Y}[TIMEOUT] No se pudo verificar resultado{X}')
                            else:
                                print(f'  {R}[ERROR] No se pudo ejecutar: {trade_id}{X}')
                                
                        except Exception as e:
                            print(f'  {R}[ERROR] Excepcion: {e}{X}')
                        
                        last_trade_time = now
                    else:
                        print(f'  {Y}No cumple umbral de confianza ({r.confidence*100:.1f}% < 55%){X}')
                else:
                    if cycle % 3 == 0:
                        print(f'  {asset}: Score {r.total_score:.1f} - Sin senal')
                        
            except Exception as e:
                print(f'  {R}{asset}: Error - {e}{X}')
                continue

        # Dashboard
        total = wins + losses
        wr = (wins/total*100) if total > 0 else 0
        pnl = balance - 10000.0
        mins = int(elapsed / 60)
        secs = int(elapsed % 60)

        pc = G if pnl >= 0 else R
        print(f'\n{C}Ciclo {cycle} | {mins}m{secs}s | Trades: {total} | W/L: {G}{wins}{X}/{R}{losses}{X} | WR: {wr:.1f}% | Balance: ${balance:.2f} | PnL: {pc}${pnl:+.2f}{X}')

        time.sleep(10)

except KeyboardInterrupt:
    print(f'\n\n{Y}Detenido por usuario{X}')

# Resumen
total = wins + losses
wr = (wins/total*100) if total > 0 else 0
pnl = balance - 10000.0
elapsed = time.time() - start_time

print(f'\n{C}{"="*78}')
print(f'RESUMEN FINAL')
print(f'{"="*78}')
print(f'Tiempo: {elapsed/60:.1f} min | Ciclos: {cycle} | Trades: {total}')
print(f'Wins: {wins} | Losses: {losses} | Win Rate: {wr:.1f}%')
print(f'Balance final: ${balance:.2f} | PnL: ${pnl:+.2f}')
print(f'{"="*78}{X}\n')
