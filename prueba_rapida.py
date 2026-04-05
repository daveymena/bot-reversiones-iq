#!/usr/bin/env python3
"""Prueba rapida del Ultra-Smart Bot v2.0"""
import sys, os, time
sys.path.insert(0, os.getcwd())

from core.unified_scoring_engine import get_scoring_engine
from core.advanced_risk_manager import initialize_risk_manager, RiskConfig
import pandas as pd, numpy as np
from datetime import datetime

print("=" * 60)
print("ULTRA-SMART BOT v2.0 - PRUEBA RAPIDA")
print("=" * 60)

# Inicializar
rm = initialize_risk_manager(10000.0, RiskConfig())
se = get_scoring_engine()

balance = 10000.0
wins = 0
losses = 0

print("Balance inicial: $10000.00")
print("Iniciando 10 ciclos de prueba...\n")

for i in range(10):
    # Datos simulados
    df = pd.DataFrame({
        "open": 1.1 + np.random.randn(100).cumsum() * 0.0001,
        "high": 1.1 + np.random.randn(100).cumsum() * 0.0001 + 0.0005,
        "low": 1.1 + np.random.randn(100).cumsum() * 0.0001 - 0.0005,
        "close": 1.1 + np.random.randn(100).cumsum() * 0.0001,
        "rsi": 30 + np.random.random(100) * 40,
    })
    df["ema_9"] = df["close"].ewm(span=9).mean()
    df["ema_21"] = df["close"].ewm(span=21).mean()
    df["macd"] = df["ema_9"] - df["ema_21"]
    df["macd_signal"] = df["macd"].ewm(span=9).mean()

    # Scoring
    r = se.score(
        df=df,
        current_price=df["close"].iloc[-1],
        asset="EUR/USD",
        smart_money_data={
            "order_block_hit": True,
            "fvg_detected": False,
            "liquidity_grab": False,
            "premium_discount": 0.4
        },
        market_structure_data={
            "trend_direction": "uptrend",
            "trend_strength": 0.7,
            "bos_detected": True
        }
    )

    if r.recommendation == "TRADE" and r.confidence >= 0.65:
        pos = rm.calculate_position_size(confidence=r.confidence)
        if pos > 0:
            # Simular resultado
            pnl = pos * 0.85 if np.random.random() > 0.45 else -pos
            if pnl > 0:
                wins += 1
            else:
                losses += 1
            balance += pnl
            rm.update_balance(balance, {"profit": pnl})
            estado = "WIN" if pnl > 0 else "LOSS"
            print(f"Ciclo {i+1}: {r.signal_type.value} score={r.total_score:.1f} | {estado} {pnl:+.2f} | Balance=${balance:.2f}")

print("")
print("=" * 60)
print("RESULTADO FINAL")
print("=" * 60)
total = wins + losses
wr = (wins / total * 100) if total > 0 else 0
pnl = balance - 10000
print(f"Trades: {total} | Wins: {wins} | Losses: {losses}")
print(f"Win Rate: {wr:.1f}%")
print(f"Balance: ${balance:.2f} | PnL: ${pnl:+.2f}")
print("=" * 60)
