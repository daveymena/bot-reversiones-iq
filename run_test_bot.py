#!/usr/bin/env python3
"""Test bot con analisis en tiempo real"""
import time, sys, os
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

print(f'{C}=== CONECTANDO A EXNOVA ==={X}')

email = os.getenv('EXNOVA_EMAIL', '')
password = os.getenv('EXNOVA_PASSWORD', '')

market_data = MarketDataHandler(broker_name='exnova', account_type='PRACTICE')

if market_data.connect(email, password):
    print(f'{G}[OK] CONECTADO A EXNOVA{X}')
    
    # Check balance
    try:
        balance = market_data.get_balance()
        print(f'{C}Balance: ${balance}{X}')
    except Exception as e:
        print(f'{Y}Balance: {e}{X}')
    
    # Get available assets
    try:
        market_data.api.update_ACTIVES_OPCODE()
        print(f'{G}[OK] Activos actualizados{X}')
    except Exception as e:
        print(f'{Y}Error activos: {e}{X}')
    
    # Try to get candles
    assets = ['EURUSD-OTC', 'GBPUSD-OTC', 'AUDUSD-OTC']
    feature_engineer = FeatureEngineer()
    
    for asset in assets:
        try:
            df = market_data.get_candles(asset, timeframe=60, num_candles=100)
            if df is not None and len(df) > 0:
                df = feature_engineer.add_features(df)
                last = df.iloc[-1]
                close_price = last['close']
                rsi_val = last.get('rsi', 0)
                print(f'{C}{asset}: Price={close_price:.5f}, RSI={rsi_val:.1f}, Candles={len(df)}{X}')
            else:
                print(f'{R}{asset}: Sin datos{X}')
        except Exception as e:
            print(f'{R}{asset}: Error - {e}{X}')
    
    print(f'{Y}=== ANALIZANDO OPORTUNIDADES ==={X}')
    
    rm = initialize_risk_manager(10000.0, RiskConfig(
        max_drawdown_daily=0.15,
        max_trades_per_hour=8,
        cooldown_after_loss_seconds=300,
        min_confidence_threshold=0.65
    ))
    se = get_scoring_engine()
    
    wins = 0
    losses = 0
    balance = 10000.0
    
    for cycle in range(5):
        print(f'{C}--- Ciclo {cycle+1} ---{X}')
        for asset in assets:
            try:
                df = market_data.get_candles(asset, timeframe=60, num_candles=100)
                if df is not None and len(df) >= 50:
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
                    
                    if r.recommendation == 'TRADE' and r.confidence >= 0.65:
                        sig = r.signal_type.value
                        pos = rm.calculate_position_size(confidence=r.confidence)
                        print(f'{G}  SEÑAL: {asset} {sig} | Score: {r.total_score:.1f} | Conf: {r.confidence*100:.1f}% | Pos: ${pos:.2f}{X}')
                        
                        # Execute trade
                        amount = max(1, min(pos, 100))
                        expiration = 3
                        status, trade_id = market_data.api.buy(amount, asset, sig.lower(), expiration)
                        
                        if status:
                            print(f'{G}  [OK] Trade ejecutado! ID: {trade_id}{X}')
                            print(f'{Y}  Esperando resultado ({expiration} min)...{X}')
                            time.sleep(expiration * 60 + 15)
                            
                            result_status, profit = market_data.api.check_win_v4(trade_id, timeout=90)
                            if result_status is not None:
                                won = result_status == 'win'
                                actual_profit = profit if won else -amount
                                if won:
                                    wins += 1
                                    print(f'{G}  [WIN] +${actual_profit:.2f}{X}')
                                else:
                                    losses += 1
                                    print(f'{R}  [LOSS] ${actual_profit:.2f}{X}')
                                balance += actual_profit
                            else:
                                print(f'{Y}  [TIMEOUT] No se pudo verificar{X}')
                        else:
                            print(f'{R}  [ERROR] {trade_id}{X}')
                    else:
                        print(f'  {asset}: Sin señal (Score: {r.total_score:.1f}, Conf: {r.confidence*100:.1f}%)')
            except Exception as e:
                print(f'{R}  {asset}: Error - {e}{X}')
        time.sleep(10)
    
    total = wins + losses
    wr = (wins/total*100) if total > 0 else 0
    pnl = balance - 10000.0
    
    print(f'{C}=== RESUMEN ==={X}')
    print(f'Trades: {total} | Wins: {wins} | Losses: {losses}')
    print(f'Win Rate: {wr:.1f}%')
    print(f'Balance: ${balance:.2f} | PnL: ${pnl:+.2f}')
    print(f'{C}=== FIN ==={X}')
else:
    print(f'{R}[ERROR] No se pudo conectar{X}')
