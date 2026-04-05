#!/usr/bin/env python3
"""
ULTRA-SMART BOT v2.0 - MODO PRACTICA FINAL
Interfaz profesional tipo dashboard
"""
import sys
import os
import time
import pandas as pd
import numpy as np
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Códigos ANSI para colores y control de terminal
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    GRAY = "\033[90m"

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    clear_screen()
    print(Colors.CYAN + "=" * 78)
    print(Colors.BOLD + "   ULTRA-SMART TRADING BOT v2.0  |  MODO PRACTICA")
    print(Colors.CYAN + "=" * 78)
    print(Colors.WHITE + f"   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  |  SIMULACION - Sin riesgo")
    print(Colors.CYAN + "=" * 78 + Colors.RESET)

def print_box(title, content, color=Colors.WHITE):
    print(f"\n{color}+{'-' * 76}+")
    print(f"| {Colors.BOLD}{title}{Colors.RESET}{color}" + " " * (73 - len(title)) + "|")
    print(f"+{'-' * 76}+")
    for line in content.split("\n"):
        print(f"| {line}" + " " * (75 - len(line)) + "|")
    print(f"+{'-' * 76}+{Colors.RESET}")

def print_signal(asset, signal, score, confidence, position, reasons):
    if signal == "CALL":
        color = Colors.GREEN
        icon = ">>> CALL (ALCISTA)"
    else:
        color = Colors.RED
        icon = ">>> PUT (BAJISTA)"

    print(f"\n{color}{Colors.BOLD}{'=' * 78}")
    print(f"  SEÑAL DETECTADA - {asset}")
    print(f"{'=' * 78}{Colors.RESET}")
    print(f"  {icon}")
    print(f"  Score: {score:.1f}/100  |  Confianza: {confidence*100:.1f}%  |  Posición: ${position:.2f}")
    print(f"\n  Razones:")
    for i, r in enumerate(reasons[:3], 1):
        print(f"    {i}. {r}")

def print_dashboard(balance, initial, wins, losses, total_pnl, cycle, elapsed):
    winrate = (wins / (wins + losses) * 100) if (wins + losses) > 0 else 0

    # Barra de estado
    pnl_color = Colors.GREEN if total_pnl >= 0 else Colors.RED
    pnl_icon = "+" if total_pnl >= 0 else ""

    print(f"\n{Colors.CYAN}{'=' * 78}{Colors.RESET}")
    print(f"  {Colors.BOLD}DASHBOARD{Colors.RESET}")
    print(f"  {'=' * 76}")

    # Métricas en una línea
    print(f"  {Colors.WHITE}Balance: ${balance:>10.2f}  |  " +
          f"PnL: {pnl_color}{pnl_icon}${total_pnl:>8.2f}{Colors.RESET}  |  " +
          f"Trades: {wins+losses:>3}  |  " +
          f"W/L: {Colors.GREEN}{wins}{Colors.RESET}/{Colors.RED}{losses}{Colors.RESET}  |  " +
          f"WinRate: {winrate:>5.1f}%")

    # Tiempo
    mins = int(elapsed / 60)
    secs = int(elapsed % 60)
    print(f"  Tiempo: {mins}m {secs}s  |  Ciclo: {cycle}")
    print(f"  {'=' * 76}")

def main():
    print_header()

    # Cargar componentes
    print(f"\n{Colors.WHITE}Cargando componentes del bot...")
    time.sleep(1)

    try:
        from core.advanced_risk_manager import initialize_risk_manager, RiskConfig
        from core.unified_scoring_engine import get_scoring_engine
        from core.backtesting_system import get_paper_trader

        print(f"  {Colors.GREEN}[OK]{Colors.WHITE} Risk Manager - Kelly Criterion")
        print(f"  {Colors.GREEN}[OK]{Colors.WHITE} Scoring Engine - 8 categorías")
        print(f"  {Colors.GREEN}[OK]{Colors.WHITE} Paper Trader - Simulación")
    except Exception as e:
        print(f"  {Colors.RED}[ERROR]{Colors.WHITE} {e}")
        return

    # Inicializar
    risk_config = RiskConfig(
        max_drawdown_daily=0.15,
        max_trades_per_hour=8,
        cooldown_after_loss_seconds=300,
        min_confidence_threshold=0.65
    )

    INITIAL_BALANCE = 10000.0
    risk_manager = initialize_risk_manager(INITIAL_BALANCE, risk_config)
    scoring_engine = get_scoring_engine()
    paper_trader = get_paper_trader(initial_balance=INITIAL_BALANCE)

    # Mostrar configuración
    config_text = f"""Balance Inicial:     ${INITIAL_BALANCE:,.2f}
Máx por operación:   $200.00 (2%)
Máx drawdown diario: 15% (${INITIAL_BALANCE * 0.15:,.2f})
Máx ops/hora:        8
Confianza mínima:    65%
Cooldown pérdida:    5 min"""

    print_box("CONFIGURACIÓN DE RIESGO", config_text, Colors.CYAN)

    print(f"\n{Colors.YELLOW}Iniciando monitoreo en 3 segundos...{Colors.RESET}")
    time.sleep(3)

    # Activos y variables
    assets = ["EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD"]
    start_time = time.time()
    wins = 0
    losses = 0
    cycle = 0
    last_trade_time = 0

    print(f"\n{Colors.GREEN}{'=' * 78}")
    print(f"  MONITOREO DE MERCADO INICIADO")
    print(f"  Analizando activos: {', '.join(assets)}")
    print(f"  Presiona Ctrl+C para detener")
    print(f"{'=' * 78}{Colors.RESET}\n")

    try:
        while True:
            cycle += 1
            current_time = time.time()
            elapsed = current_time - start_time

            for asset in assets:
                # Generar datos simulados
                dates = pd.date_range(end=datetime.now(), periods=100, freq='1min')
                base = 1.1000 + (cycle * 0.0001)

                df = pd.DataFrame({
                    'timestamp': dates,
                    'open': base + np.random.randn(100).cumsum() * 0.0001,
                    'high': base + np.random.randn(100).cumsum() * 0.0001 + 0.0005,
                    'low': base + np.random.randn(100).cumsum() * 0.0001 - 0.0005,
                    'close': base + np.random.randn(100).cumsum() * 0.0001,
                })

                # Indicadores técnicos
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

                # Mostrar señal válida
                if result.recommendation == "TRADE" and result.confidence >= 0.65:
                    # Verificar cooldown
                    if current_time - last_trade_time < 10:
                        continue

                    position = risk_manager.calculate_position_size(
                        confidence=result.confidence
                    )

                    if position > 0:
                        print_signal(
                            asset,
                            result.signal_type.value,
                            result.total_score,
                            result.confidence,
                            position,
                            result.reasons_to_trade
                        )

                        # Simular resultado
                        import random
                        if random.random() > 0.45:  # 55% win rate
                            pnl = position * 0.85
                            wins += 1
                            print(f"\n  {Colors.GREEN}[WIN] +${pnl:.2f}{Colors.RESET}")
                        else:
                            pnl = -position
                            losses += 1
                            print(f"\n  {Colors.RED}[LOSS] -${abs(pnl):.2f}{Colors.RESET}")

                        paper_trader.current_balance += pnl
                        risk_manager.update_balance(paper_trader.current_balance, {'profit': pnl})
                        last_trade_time = current_time

            # Dashboard
            print_dashboard(
                balance=paper_trader.current_balance,
                initial=INITIAL_BALANCE,
                wins=wins,
                losses=losses,
                total_pnl=paper_trader.current_balance - INITIAL_BALANCE,
                cycle=cycle,
                elapsed=elapsed
            )

            # Esperar
            time.sleep(5)

    except KeyboardInterrupt:
        pass

    # Resumen final
    elapsed = time.time() - start_time
    total_trades = wins + losses
    winrate = (wins / total_trades * 100) if total_trades > 0 else 0
    pnl = paper_trader.current_balance - INITIAL_BALANCE

    print_header()
    print_box("RESUMEN FINAL",
        f"Tiempo total:      {elapsed/60:.1f} minutos\n" +
        f"Ciclos:            {cycle}\n" +
        f"Trades totales:    {total_trades}\n" +
        f"Ganadas:           {wins}\n" +
        f"Perdidas:          {losses}\n" +
        f"Win Rate:          {winrate:.1f}%\n" +
        f"Balance final:     ${paper_trader.current_balance:,.2f}\n" +
        f"PnL Total:         {pnl:+,.2f} ({pnl/INITIAL_BALANCE*100:+.2f}%)",
        Colors.GREEN if pnl >= 0 else Colors.RED
    )

    print(f"\n{Colors.CYAN}{'=' * 78}")
    print(f"  SESIÓN DE PRÁCTICA COMPLETADA - Gracias por usar Ultra-Smart Bot v2.0")
    print(f"{'=' * 78}{Colors.RESET}\n")

if __name__ == "__main__":
    main()
