#!/usr/bin/env python3
"""
MODO PRACTICA - Ultra-Smart Bot v2.0
Interfaz limpia y funcional para probar el bot sin riesgo
"""
import sys
import os
import time
import pandas as pd
import numpy as np
from datetime import datetime
from colorama import init, Fore, Style

# Inicializar colorama para colores en Windows
init(autoreset=True)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Encabezado
def print_header():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(Fore.CYAN + "=" * 70)
    print(Fore.CYAN + "  ULTRA-SMART BOT v2.0 - MODO PRACTICA")
    print(Fore.CYAN + "=" * 70)
    print(Fore.WHITE + f"  Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(Fore.YELLOW + "  [SIMULACION] Sin dinero real - Solo practica")
    print(Fore.CYAN + "=" * 70)

def print_section(title):
    print(Fore.GREEN + "\n" + "=" * 70)
    print(Fore.GREEN + f"  {title}")
    print(Fore.GREEN + "=" * 70)

def print_trade_signal(asset, signal, score, confidence, reasons):
    """Imprimir señal de trading de forma clara"""
    if signal == "CALL":
        color = Fore.GREEN
        icon = "[CALL]"
    elif signal == "PUT":
        color = Fore.RED
        icon = "[PUT]"
    else:
        color = Fore.YELLOW
        icon = "[NEUTRAL]"

    print(Fore.WHITE + f"\n  Activo: {Fore.CYAN}{asset}")
    print(Fore.WHITE + f"  Senal: {color}{icon} {signal}")
    print(Fore.WHITE + f"  Score: {score:.1f}/100")
    print(Fore.WHITE + f"  Confianza: {confidence*100:.1f}%")
    print(Fore.WHITE + f"  Razones:")
    for i, reason in enumerate(reasons[:3], 1):
        print(Fore.WHITE + f"    {i}. {reason}")

def print_status(balance, trades, winrate, pnl):
    """Imprimir estado actual"""
    print(Fore.WHITE + "\n" + "-" * 70)
    print(Fore.WHITE + f"  Balance: ${balance:.2f}")
    print(Fore.WHITE + f"  PnL: {Fore.GREEN if pnl >= 0 else Fore.RED}${pnl:+.2f}")
    print(Fore.WHITE + f"  Trades: {trades}")
    print(Fore.WHITE + f"  Win Rate: {winrate:.1f}%")
    print(Fore.WHITE + "-" * 70)

def main():
    print_header()

    # Importar componentes
    print(Style.BRIGHT + "\nCargando componentes...")

    try:
        from core.advanced_risk_manager import initialize_risk_manager, RiskConfig
        from core.unified_scoring_engine import get_scoring_engine
        from core.backtesting_system import get_paper_trader

        print(Fore.GREEN + "  [OK] Risk Manager")
        print(Fore.GREEN + "  [OK] Scoring Engine")
        print(Fore.GREEN + "  [OK] Paper Trader")
    except Exception as e:
        print(Fore.RED + f"  [ERROR] {e}")
        return

    # Inicializar
    risk_config = RiskConfig(
        max_drawdown_daily=0.15,
        max_trades_per_hour=8,
        cooldown_after_loss_seconds=300,
        min_confidence_threshold=0.65
    )

    risk_manager = initialize_risk_manager(10000.0, risk_config)
    scoring_engine = get_scoring_engine()
    paper_trader = get_paper_trader(initial_balance=10000.0)

    # Configuración
    print_section("CONFIGURACION")
    print(Fore.WHITE + "  Balance inicial: $10,000.00")
    print(Fore.WHITE + "  Max por operacion: $200.00 (2%)")
    print(Fore.WHITE + "  Max drawdown diario: 15% ($1,500)")
    print(Fore.WHITE + "  Max operaciones/hora: 8")
    print(Fore.WHITE + "  Confianza minima: 65%")
    print(Fore.WHITE + "  Cooldown tras perdida: 5 min")

    print(Fore.YELLOW + "\nIniciando en 3 segundos...")
    time.sleep(3)

    # Activos
    assets = ["EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD"]

    # Estadisticas
    start_time = time.time()
    wins = 0
    losses = 0
    cycle = 0

    print_section("MONITOREO DE MERCADO INICIADO")
    print(Fore.YELLOW + "  Presiona Ctrl+C para detener\n")

    try:
        while True:
            cycle += 1
            current_time = datetime.now().strftime('%H:%M:%S')

            for asset in assets:
                # Generar datos simulados (para demo)
                dates = pd.date_range(end=datetime.now(), periods=100, freq='1min')
                base = 1.1000 + (cycle * 0.0001)

                df = pd.DataFrame({
                    'timestamp': dates,
                    'open': base + np.random.randn(100).cumsum() * 0.0001,
                    'high': base + np.random.randn(100).cumsum() * 0.0001 + 0.0005,
                    'low': base + np.random.randn(100).cumsum() * 0.0001 - 0.0005,
                    'close': base + np.random.randn(100).cumsum() * 0.0001,
                })

                # Indicadores
                df['rsi'] = 30 + np.random.random(100) * 40
                df['ema_9'] = df['close'].ewm(span=9).mean()
                df['ema_21'] = df['close'].ewm(span=21).mean()
                df['macd'] = df['ema_9'] - df['ema_21']
                df['macd_signal'] = df['macd'].ewm(span=9).mean()

                # Scoring
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

                # Mostrar si hay señal válida
                if result.recommendation == "TRADE" and result.confidence >= 0.65:
                    print_trade_signal(
                        asset,
                        result.signal_type.value,
                        result.total_score,
                        result.confidence,
                        result.reasons_to_trade
                    )

                    # Calcular posición
                    position = risk_manager.calculate_position_size(
                        confidence=result.confidence
                    )

                    if position > 0:
                        print(Fore.WHITE + f"  Posicion: ${position:.2f}")

                        # Simular resultado (50/50 para demo)
                        import random
                        if random.random() > 0.45:  # 55% win rate simulado
                            pnl = position * 0.85
                            wins += 1
                            print(Fore.GREEN + "  Resultado: +$%.2f (WIN)" % pnl)
                        else:
                            pnl = -position
                            losses += 1
                            print(Fore.RED + "  Resultado: -$%.2f (LOSS)" % abs(pnl))

                        # Actualizar balance
                        paper_trader.current_balance += pnl

                        # Actualizar risk manager
                        risk_manager.update_balance(
                            paper_trader.current_balance,
                            {'profit': pnl}
                        )

                    print(Fore.WHITE + "")

            # Estado cada ciclo
            elapsed = (time.time() - start_time) / 60
            total_trades = wins + losses
            winrate = (wins / total_trades * 100) if total_trades > 0 else 0
            pnl = paper_trader.current_balance - 10000

            print_status(
                paper_trader.current_balance,
                total_trades,
                winrate,
                pnl
            )

            print(Fore.YELLOW + f"\n Ciclo {cycle} | Tiempo: {elapsed:.1f} min")
            print(Fore.YELLOW + " Esperando 10 segundos...\n")

            time.sleep(10)

    except KeyboardInterrupt:
        pass

    # Resumen final
    total_trades = wins + losses
    winrate = (wins / total_trades * 100) if total_trades > 0 else 0
    pnl = paper_trader.current_balance - 10000

    print_header()
    print_section("RESUMEN FINAL")
    print(Fore.WHITE + f"  Tiempo total: {(time.time() - start_time)/60:.1f} minutos")
    print(Fore.WHITE + f"  Ciclos: {cycle}")
    print(Fore.WHITE + f"  Trades: {total_trades}")
    print(Fore.WHITE + f"  Wins: {Fore.GREEN}{wins}")
    print(Fore.WHITE + f"  Losses: {Fore.RED}{losses}")
    print(Fore.WHITE + f"  Win Rate: {winrate:.1f}%")
    print(Fore.WHITE + f"  Balance final: ${paper_trader.current_balance:.2f}")
    print(Fore.WHITE + f"  PnL: {Fore.GREEN if pnl >= 0 else Fore.RED}${pnl:+.2f}")
    print(Fore.CYAN + "\n" + "=" * 70)
    print(Fore.CYAN + "  SESION DE PRACTICA COMPLETADA")
    print(Fore.CYAN + "=" * 70 + Style.RESET_ALL)

if __name__ == "__main__":
    main()
