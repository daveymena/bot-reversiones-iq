#!/usr/bin/env python3
"""
Bot Practica OTC - Fin de Semana
Ejecucion automatica sin interaccion
"""
import sys, os, time
sys.path.insert(0, os.getcwd())

from core.unified_scoring_engine import get_scoring_engine
from core.advanced_risk_manager import initialize_risk_manager, RiskConfig
import pandas as pd, numpy as np
from datetime import datetime

print("=" * 70)
print("ULTRA-SMART BOT v2.0 - MODO PRACTICA OTC")
print("=" * 70)
print(f"Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("Activos: EURUSD-OTC, GBPUSD-OTC, AUDUSD-OTC (disponibles 24/7)")
print("=" * 70)

# Inicializar
rm = initialize_risk_manager(10000.0, RiskConfig(
    max_drawdown_daily=0.15,
    max_trades_per_hour=8,
    min_confidence_threshold=0.65
))
se = get_scoring_engine()

balance = 10000.0
wins = 0
losses = 0
start = time.time()

# Activos OTC
assets = ["EURUSD-OTC", "GBPUSD-OTC", "AUDUSD-OTC"]

print("\nIniciando monitoreo...\n")

try:
    cycle = 0
    while cycle < 20:  # 20 ciclos para prueba
        cycle += 1

        for asset in assets:
            # Datos simulados OTC
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
                df=df, current_price=df["close"].iloc[-1], asset=asset,
                smart_money_data={
                    "order_block_hit": np.random.random() > 0.5,
                    "fvg_detected": np.random.random() > 0.5,
                    "liquidity_grab": np.random.random() > 0.7,
                    "premium_discount": np.random.random()
                },
                market_structure_data={
                    "trend_direction": np.random.choice(["uptrend", "downtrend", "neutral"]),
                    "trend_strength": np.random.random(),
                    "bos_detected": np.random.random() > 0.5
                }
            )

            if r.recommendation == "TRADE" and r.confidence >= 0.65:
                pos = rm.calculate_position_size(confidence=r.confidence)
                if pos > 0:
                    pnl = pos * 0.85 if np.random.random() > 0.45 else -pos
                    if pnl > 0:
                        wins += 1
                        estado = "WIN"
                        color_pnl = f"+{pnl:.2f}"
                    else:
                        losses += 1
                        estado = "LOSS"
                        color_pnl = f"{pnl:.2f}"

                    balance += pnl
                    rm.update_balance(balance, {"profit": pnl})
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] {asset:12s} {r.signal_type.value:4s} score={r.total_score:5.1f} | {estado:4s} {color_pnl:>9s} | Balance=${balance:.2f}")

        time.sleep(3)

except KeyboardInterrupt:
    print("\n\nDetenido por usuario")

# Resumen
elapsed = (time.time() - start) / 60
total = wins + losses
wr = (wins / total * 100) if total > 0 else 0
pnl = balance - 10000

print("\n" + "=" * 70)
print("RESUMEN FINAL")
print("=" * 70)
print(f"Tiempo:           {elapsed:.1f} minutos")
print(f"Ciclos:           {cycle}")
print(f"Trades:           {total} ({wins} wins / {losses} losses)")
print(f"Win Rate:         {wr:.1f}%")
print(f"Balance final:    ${balance:.2f}")
print(f"PnL:              ${pnl:+.2f} ({pnl/10000*100:+.2f}%)")
print("=" * 70)
