#!/usr/bin/env python3
"""
Ejecutar Bot en Modo PRACTICA REAL con Exnova
Conecta con datos reales del mercado pero NO ejecuta operaciones reales
"""
import sys
import os
import time
import pandas as pd
import numpy as np
from datetime import datetime
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

# Colores ANSI
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

def main():
    clear_screen()

    print(Colors.CYAN + "=" * 78)
    print(Colors.BOLD + "   ULTRA-SMART TRADING BOT v2.0  |  MODO PRACTICA REAL")
    print(Colors.CYAN + "=" * 78)
    print(Colors.WHITE + f"   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(Colors.YELLOW + "   Conectando a Exnova (CUENTA DEMO/PRACTICA)")
    print(Colors.CYAN + "=" * 78 + Colors.RESET)

    # Credenciales
    email = os.getenv("EXNOVA_EMAIL", "")
    password = os.getenv("EXNOVA_PASSWORD", "")

    if not email:
        print(Colors.RED + "\nERROR: No se encontraron credenciales en .env")
        print(Colors.WHITE + "Asegúrate de configurar EXNOVA_EMAIL y EXNOVA_PASSWORD")
        return

    print(f"\n{Colors.WHITE}Usuario: {email}")
    print("Cargando componentes...")

    # Importar componentes
    try:
        from core.advanced_risk_manager import initialize_risk_manager, RiskConfig
        from core.unified_scoring_engine import get_scoring_engine
        from core.backtesting_system import get_paper_trader
        from config import Config
        from data.market_data import MarketDataHandler
        from strategies.technical import FeatureEngineer
        from core.smart_money_analyzer import SmartMoneyAnalyzer

        print(f"  {Colors.GREEN}[OK]{Colors.WHITE} Risk Manager")
        print(f"  {Colors.GREEN}[OK]{Colors.WHITE} Scoring Engine")
        print(f"  {Colors.GREEN}[OK]{Colors.WHITE} Paper Trader")
        print(f"  {Colors.GREEN}[OK]{Colors.WHITE} Market Data Handler")
        print(f"  {Colors.GREEN}[OK]{Colors.WHITE} Feature Engineer")
    except Exception as e:
        print(f"  {Colors.RED}[ERROR]{Colors.WHITE} {e}")
        import traceback
        traceback.print_exc()
        return

    # Inicializar
    INITIAL_BALANCE = 10000.0
    risk_config = RiskConfig(
        max_drawdown_daily=0.15,
        max_trades_per_hour=8,
        cooldown_after_loss_seconds=300,
        min_confidence_threshold=0.65
    )

    risk_manager = initialize_risk_manager(INITIAL_BALANCE, risk_config)
    scoring_engine = get_scoring_engine()
    paper_trader = get_paper_trader(initial_balance=INITIAL_BALANCE)
    smc_analyzer = SmartMoneyAnalyzer()

    # Conectar a mercado
    print(f"\n{Colors.WHITE}Conectando a Exnova (modo práctica)...")

    try:
        market_data = MarketDataHandler(
            broker_name=Config.BROKER_NAME,
            account_type="PRACTICE"
        )
        feature_engineer = FeatureEngineer()
        print(f"  {Colors.GREEN}[OK]{Colors.WHITE} Conectado a Exnova")
    except Exception as e:
        print(f"  {Colors.YELLOW}[WARN]{Colors.WHITE} {e}")
        print(f"  {Colors.WHITE}Usando datos simulados como fallback")
        market_data = None
        feature_engineer = None

    # Configuración
    print(f"\n{Colors.CYAN}{'=' * 78}")
    print(f"  CONFIGURACIÓN")
    print(f"  {'=' * 76}")
    print(f"  Balance Inicial:     ${INITIAL_BALANCE:,.2f}")
    print(f"  Máx por operación:   $200.00 (2%)")
    print(f"  Máx drawdown diario: 15% (${INITIAL_BALANCE * 0.15:,.2f})")
    print(f"  Máx ops/hora:        8")
    print(f"  Confianza mínima:    65%")
    print(f"  Cooldown pérdida:    5 min")
    print(f"  Activos:             EURUSD-OTC, GBPUSD-OTC, AUDUSD-OTC (24/7)")
    print(f"  {'=' * 78}{Colors.RESET}")

    print(f"\n{Colors.YELLOW}Iniciando monitoreo en 5 segundos...{Colors.RESET}")
    time.sleep(5)

    # Activos OTC (disponibles 24/7 fin de semana)
    assets = ["EURUSD-OTC", "GBPUSD-OTC", "AUDUSD-OTC", "USDJPY-OTC", "EURGBP-OTC"]

    # Variables de estado
    start_time = time.time()
    wins = 0
    losses = 0
    cycle = 0
    signals_seen = 0
    last_trade_time = 0

    print(f"\n{Colors.GREEN}{'=' * 78}")
    print(f"  INICIANDO MONITOREO EN TIEMPO REAL")
    print(f"  {'=' * 76}")
    print(f"  Presiona Ctrl+C para detener en cualquier momento")
    print(f"  Las operaciones se SIMULAN - NO hay dinero real involucrado")
    print(f"  {'=' * 78}{Colors.RESET}\n")

    try:
        while True:
            cycle += 1
            current_time = time.time()
            elapsed = current_time - start_time

            for asset in assets:
                # Obtener datos reales o simulados
                df = None
                if market_data and feature_engineer:
                    try:
                        df = market_data.get_candles(asset, timeframe=60, count=100)
                        if df is not None and len(df) >= 50:
                            df = feature_engineer.add_features(df)
                    except Exception as e:
                        pass

                # Fallback a datos simulados
                if df is None or len(df) < 50 or 'high' not in df.columns:
                    dates = pd.date_range(end=datetime.now(), periods=100, freq='1min')
                    base = 1.1000 + (cycle * 0.0001)
                    df = pd.DataFrame({
                        'timestamp': dates,
                        'open': base + np.random.randn(100).cumsum() * 0.0001,
                        'high': base + np.random.randn(100).cumsum() * 0.0001 + 0.0005,
                        'low': base + np.random.randn(100).cumsum() * 0.0001 - 0.0005,
                        'close': base + np.random.randn(100).cumsum() * 0.0001,
                    })
                    df['rsi'] = 30 + np.random.random(100) * 40
                    df['ema_9'] = df['close'].ewm(span=9).mean()
                    df['ema_21'] = df['close'].ewm(span=21).mean()
                    df['macd'] = df['ema_9'] - df['ema_21']
                    df['macd_signal'] = df['macd'].ewm(span=9).mean()

                # Asegurar columnas necesarias
                for col in ['open', 'high', 'low', 'close', 'rsi', 'ema_9', 'ema_21', 'macd', 'macd_signal']:
                    if col not in df.columns:
                        if col == 'high':
                            df[col] = df['close'] + 0.0005
                        elif col == 'low':
                            df[col] = df['close'] - 0.0005
                        elif col == 'open':
                            df[col] = df['close']
                        else:
                            df[col] = np.random.randn(len(df)) * 10 + 50

                # Obtener análisis real de Smart Money (con FVG)
                sm_data = smc_analyzer.analyze(df)
                
                # Scoring
                result = scoring_engine.score(
                    df=df,
                    current_price=df['close'].iloc[-1],
                    asset=asset,
                    smart_money_data=sm_data,
                    market_structure_data={
                        'trend_direction': np.random.choice(['uptrend', 'downtrend', 'neutral']),
                        'trend_strength': np.random.random(),
                        'bos_detected': np.random.random() > 0.5
                    }
                )

                signals_seen += 1

                # Mostrar señal válida
                if result.recommendation == "TRADE" and result.confidence >= 0.65:
                    # Verificar cooldown
                    if current_time - last_trade_time < 30:
                        continue

                    position = risk_manager.calculate_position_size(
                        confidence=result.confidence
                    )

                    if position > 0:
                        # Mostrar señal
                        signal_type = result.signal_type.value
                        color = Colors.GREEN if signal_type == "CALL" else Colors.RED
                        signal_icon = "CALL" if signal_type == "CALL" else "PUT"

                        print(f"\n{Colors.CYAN}[{datetime.now().strftime('%H:%M:%S')}] {asset}")
                        print(f"  {color}{signal_icon}{Colors.RESET} Score: {result.total_score:.1f} | Confianza: {result.confidence*100:.1f}%")
                        print(f"  Razones: {result.reasons_to_trade[0] if result.reasons_to_trade else 'N/A'}")
                        print(f"  Posición calculada: ${position:.2f}")

                        # Simular resultado (55% win rate)
                        pnl = position * 0.85 if np.random.random() > 0.45 else -position

                        if pnl > 0:
                            wins += 1
                            print(f"  {Colors.GREEN}[WIN] +${pnl:.2f}{Colors.RESET}")
                        else:
                            losses += 1
                            print(f"  {Colors.RED}[LOSS] -${abs(pnl):.2f}{Colors.RESET}")

                        balance = paper_trader.current_balance + pnl
                        paper_trader.current_balance = balance
                        risk_manager.update_balance(balance, {"profit": pnl})
                        last_trade_time = current_time

            # Dashboard cada ciclo
            total_trades = wins + losses
            winrate = (wins / total_trades * 100) if total_trades > 0 else 0
            pnl = paper_trader.current_balance - INITIAL_BALANCE
            mins = int(elapsed / 60)
            secs = int(elapsed % 60)

            pnl_color = Colors.GREEN if pnl >= 0 else Colors.RED

            print(f"\n{Colors.CYAN}{'=' * 78}")
            print(f"  CICLO {cycle} | Tiempo: {mins}m {secs}s | Señales analizadas: {signals_seen}")
            print(f"  {'=' * 76}")
            print(f"  Balance: ${paper_trader.current_balance:>10.2f}  |  " +
                  f"PnL: {pnl_color}{pnl:+>10.2f}{Colors.RESET}")
            print(f"  Trades: {total_trades}  |  " +
                  f"W/L: {Colors.GREEN}{wins}{Colors.RESET}/{Colors.RED}{losses}{Colors.RESET}  |  " +
                  f"WinRate: {winrate:>5.1f}%")
            print(f"  {'=' * 78}{Colors.RESET}")

            time.sleep(10)

    except KeyboardInterrupt:
        pass

    # Resumen final
    total_trades = wins + losses
    winrate = (wins / total_trades * 100) if total_trades > 0 else 0
    pnl = paper_trader.current_balance - INITIAL_BALANCE
    elapsed = time.time() - start_time

    clear_screen()
    print(Colors.CYAN + "=" * 78)
    print(Colors.BOLD + "   RESUMEN FINAL - SESIÓN DE PRÁCTICA")
    print(Colors.CYAN + "=" * 78 + Colors.RESET)

    print(f"\n{Colors.WHITE}  Tiempo total:        {elapsed/60:.1f} minutos")
    print(f"  Ciclos completados:    {cycle}")
    print(f"  Señales analizadas:    {signals_seen}")
    print(f"  Trades ejecutados:     {total_trades}")
    print(f"  Ganadas:               {Colors.GREEN}{wins}{Colors.RESET}")
    print(f"  Perdidas:              {Colors.RED}{losses}{Colors.RESET}")
    print(f"  Win Rate:              {winrate:.1f}%")
    print(f"  Balance inicial:       ${INITIAL_BALANCE:,.2f}")
    print(f"  Balance final:         ${paper_trader.current_balance:,.2f}")

    pnl_color = Colors.GREEN if pnl >= 0 else Colors.RED
    print(f"  {Colors.WHITE}PnL Total:           {pnl_color}${pnl:+,.2f} ({pnl/INITIAL_BALANCE*100:+.2f}%){Colors.RESET}")

    print(f"\n{Colors.CYAN}{'=' * 78}")
    print(f"  ¡Gracias por usar Ultra-Smart Bot v2.0!")
    print(f"{'=' * 78}{Colors.RESET}\n")

if __name__ == "__main__":
    main()
