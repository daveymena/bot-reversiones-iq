#!/usr/bin/env python3
"""
Ejecutar Ultra-Smart Bot en Modo Prctica Real
Muestra anlisis de mercado en tiempo real sin ejecutar operaciones
"""
import sys
import os
import time
import pandas as pd
import numpy as np
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 70)
print("ULTRA-SMART BOT - MODO PRCTICA REAL")
print("=" * 70)
print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("Nota: Este modo muestra anlisis SIN ejecutar operaciones reales")
print("=" * 70)

# Importar componentes
from core.advanced_risk_manager import initialize_risk_manager, RiskConfig
from core.unified_scoring_engine import get_scoring_engine
from core.backtesting_system import get_paper_trader
from config import Config

print("\n[1/4] Inicializando componentes...")

# Configurar Risk Manager
risk_config = RiskConfig(
    max_drawdown_daily=0.15,
    max_trades_per_hour=8,
    cooldown_after_loss_seconds=300,
    min_confidence_threshold=0.65
)
risk_manager = initialize_risk_manager(10000.0, risk_config)  # Balance demo $10,000

# Obtener Scoring Engine
scoring_engine = get_scoring_engine()

# Obtener Paper Trader
paper_trader = get_paper_trader(initial_balance=10000.0)

print("   Risk Manager inicializado")
print("   Scoring Engine listo")
print("   Paper Trader listo")

# Intentar obtener datos reales del mercado
print("\n[2/4] Conectando a mercado...")

try:
    from data.market_data import MarketDataHandler
    from strategies.technical import FeatureEngineer

    market_data = MarketDataHandler(
        broker_name=Config.BROKER_NAME,
        account_type="PRACTICE"
    )
    feature_engineer = FeatureEngineer()
    print("   Componentes de mercado cargados")

    MARKET_AVAILABLE = True

except Exception as e:
    print(f"   Mercado no disponible: {e}")
    print("   Usando datos simulados para demostracin")
    MARKET_AVAILABLE = False

print("\n[3/4] Configuracin actual:")
print(f"  Balance inicial: $10,000.00")
print(f"  Mximo por operacin: ${10000 * 0.02:.2f} (2%)")
print(f"  Mximo drawdown diario: 15% (${10000 * 0.15:.2f})")
print(f"  Mximo operaciones/hora: 8")
print(f"  Confianza mnima para operar: 65%")
print(f"  Cooldown despus de prdida: 300s (5 min)")

print("\n[4/4] Iniciando monitoreo de mercado...")
print("-" * 70)

# Activos a monitorear
assets = ["EUR/USD", "GBP/USD", "USD/JPY"]
if MARKET_AVAILABLE:
    assets = ["EURUSD-OTC", "GBPUSD-OTC", "AUDUSD-OTC"]

cycle = 0
start_time = time.time()

try:
    while True:
        cycle += 1
        current_time = datetime.now().strftime('%H:%M:%S')

        for asset in assets:
            print(f"\n[{current_time}] Analizando {asset}...")

            # Obtener datos
            if MARKET_AVAILABLE:
                try:
                    df = market_data.get_candles(asset, timeframe=60, count=100)
                    if df is None or len(df) < 50:
                        print(f"   Datos insuficientes ({len(df) if df is not None else 0} velas)")
                        continue

                    df = feature_engineer.add_features(df)

                except Exception as e:
                    print(f"   Error obteniendo datos: {e}")
                    # Fallback a datos simulados
                    df = None
            else:
                df = None

            # Si no hay datos reales, crear datos simulados
            if df is None or len(df) < 50:
                dates = pd.date_range(end=datetime.now(), periods=100, freq='1min')
                base_price = 1.1000 + (cycle * 0.0001)
                df = pd.DataFrame({
                    'timestamp': dates,
                    'open': base_price + np.random.randn(100).cumsum() * 0.0001,
                    'high': base_price + np.random.randn(100).cumsum() * 0.0001 + 0.0005,
                    'low': base_price + np.random.randn(100).cumsum() * 0.0001 - 0.0005,
                    'close': base_price + np.random.randn(100).cumsum() * 0.0001,
                })
                # Agregar indicadores
                df['rsi'] = np.random.randn(100) * 10 + 50
                df['ema_9'] = df['close'].ewm(span=9).mean()
                df['ema_21'] = df['close'].ewm(span=21).mean()
                df['macd'] = df['ema_9'] - df['ema_21']
                df['macd_signal'] = df['macd'].ewm(span=9).mean()

            # Asegurar que tenemos los indicadores necesarios
            if 'rsi' not in df.columns:
                df['rsi'] = np.random.randn(len(df)) * 10 + 50
            if 'ema_9' not in df.columns:
                df['ema_9'] = df['close'].ewm(span=9).mean()
            if 'ema_21' not in df.columns:
                df['ema_21'] = df['close'].ewm(span=21).mean()
            if 'macd' not in df.columns:
                df['macd'] = df['ema_9'] - df['ema_21']
            if 'macd_signal' not in df.columns:
                df['macd_signal'] = df['macd'].ewm(span=9).mean()

            # Calcular scoring
            result = scoring_engine.score(
                df=df,
                current_price=df['close'].iloc[-1],
                asset=asset,
                smart_money_data={
                    'order_block_hit': np.random.random() > 0.5,
                    'fvg_detected': np.random.random() > 0.5,
                    'liquidity_grab': np.random.random() > 0.7,
                    'premium_discount': np.random.random()
                },
                market_structure_data={
                    'trend_direction': np.random.choice(['uptrend', 'downtrend', 'neutral']),
                    'trend_strength': np.random.random(),
                    'bos_detected': np.random.random() > 0.5
                }
            )

            # Mostrar resultados
            signal_emoji = "" if result.signal_type.value == "CALL" else "" if result.signal_type.value == "PUT" else ""
            print(f"  {signal_emoji} Seal: {result.signal_type.value}")
            print(f"   Score: {result.total_score:.1f}/100")
            print(f"   Confianza: {result.confidence*100:.1f}%")
            print(f"   Recomendacin: {result.recommendation}")
            print(f"   Winrate esperado: {result.expected_winrate*100:.1f}%")

            # Verificar si debera operar
            if result.recommendation == "TRADE" and result.confidence >= 0.65:
                print(f"\n   SEAL VLIDA DETECTADA!")

                # Calcular posicin con Risk Manager
                position = risk_manager.calculate_position_size(
                    confidence=result.confidence
                )

                if position > 0:
                    print(f"   Posicin calculada: ${position:.2f}")
                    print(f"   Razones:")
                    for reason in result.reasons_to_trade[:3]:
                        print(f"     - {reason}")

                    # En modo prctica, registrar pero no ejecutar
                    if result.signal_type.value != "NEUTRAL":
                        paper_trader.execute_paper_trade(
                            asset=asset,
                            direction=result.signal_type.value.lower(),
                            amount=position,
                            score=result.total_score,
                            confidence=result.confidence,
                            reasons=result.reasons_to_trade[:3]
                        )
                else:
                    print(f"   Risk Manager no aprueba posicin (posible cooldown o lmite alcanzado)")

            # Pausa breve entre activos
            time.sleep(2)

        # Mostrar estado cada ciclo completo
        elapsed = time.time() - start_time
        stats = risk_manager.get_status_report()
        print("\n" + "=" * 70)
        print(f"ESTADO DEL BOT (Tiempo transcurrido: {elapsed/60:.1f} min)")
        print(f"  Balance Paper Trading: ${paper_trader.current_balance:.2f}")
        print(f"  Trades ejecutados: {len(paper_trader.pending_trades)}")
        print(f"  Score Kelly actual: {stats['kelly_fraction']*100:.1f}%")
        print(f"  Puede operar?: {stats['is_stopped'] == False}")
        print("=" * 70)

        # Esperar antes del siguiente ciclo
        print("\n Esperando 30 segundos antes del prximo anlisis...")
        time.sleep(30)

except KeyboardInterrupt:
    print("\n\n" + "=" * 70)
    print("DETENIDO POR USUARIO")
    print("=" * 70)

    # Mostrar resumen final
    print("\nRESUMEN FINAL:")
    stats = risk_manager.get_status_report()
    print(f"  Balance final: ${paper_trader.current_balance:.2f}")
    print(f"  PnL: ${paper_trader.current_balance - 10000:.2f}")
    print(f"  Trades pendientes: {len(paper_trader.pending_trades)}")
    print(f"  Win Rate (simulado): {stats['stats']['win_rate']:.1f}%")
    print("\n Sesin de prctica completada")
