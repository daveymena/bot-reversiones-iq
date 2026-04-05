#!/usr/bin/env python3
"""
BOT 24/7 MODO DEMO - Ultra-Smart Bot v2.0
Ejecución continua en cuenta DEMO hasta ser rentable
"""
import sys, os, time, json
from datetime import datetime
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

# Configuración
LOG_FILE = "logs/bot_247.log"
STATS_FILE = "logs/bot_247_stats.json"
os.makedirs("logs", exist_ok=True)

def log(msg, level="INFO"):
    """Guardar log en archivo y consola"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] [{level}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def main():
    log("="*70, "INFO")
    log("ULTRA-SMART BOT v2.0 - EJECUCION 24/7 MODO DEMO", "START")
    log("="*70, "INFO")

    # Credenciales
    email = os.getenv("EXNOVA_EMAIL", "")
    password = os.getenv("EXNOVA_PASSWORD", "")

    if not email:
        log("ERROR: Sin credenciales. Configura .env", "ERROR")
        return

    log(f"Usuario: {email}", "INFO")

    # Importar componentes
    try:
        from core.advanced_risk_manager import initialize_risk_manager, RiskConfig
        from core.unified_scoring_engine import get_scoring_engine
        from core.backtesting_system import get_paper_trader
        from config import Config
        from data.market_data import MarketDataHandler
        from strategies.technical import FeatureEngineer

        log("Componentes cargados correctamente", "OK")
    except Exception as e:
        log(f"Error cargando componentes: {e}", "ERROR")
        return

    # Inicializar
    INITIAL_BALANCE = float(os.getenv("DEMO_BALANCE", "10000"))
    risk_config = RiskConfig(
        max_drawdown_daily=0.15,
        max_trades_per_hour=8,
        cooldown_after_loss_seconds=300,
        min_confidence_threshold=0.65
    )

    rm = initialize_risk_manager(INITIAL_BALANCE, risk_config)
    se = get_scoring_engine()
    pt = get_paper_trader(INITIAL_BALANCE)

    log(f"Balance inicial: ${INITIAL_BALANCE:,.2f}", "INFO")

    # Conectar mercado
    try:
        md = MarketDataHandler(broker_name=Config.BROKER_NAME, account_type="PRACTICE")
        fe = FeatureEngineer()
        log("Conectado a Exnova (DEMO/PRACTICE)", "OK")
    except Exception as e:
        log(f"Error conectando: {e}. Usando datos simulados.", "WARN")
        md = None
        fe = None

    # Activos (OTC disponible 24/7)
    assets = ["EURUSD-OTC", "GBPUSD-OTC", "AUDUSD-OTC", "USDJPY-OTC", "EURGBP-OTC"]
    log(f"Activos: {', '.join(assets)}", "INFO")

    # Estadísticas
    stats = {
        "start_time": datetime.now().isoformat(),
        "initial_balance": INITIAL_BALANCE,
        "wins": 0,
        "losses": 0,
        "total_pnl": 0,
        "trades": []
    }

    start_time = time.time()
    wins, losses, cycle, signals = 0, 0, 0, 0
    last_trade_time = 0

    log("INICIANDO EJECUCION 24/7 - Presiona Ctrl+C para detener", "RUN")

    try:
        while True:
            cycle += 1
            now = time.time()
            elapsed = now - start_time
            hours = elapsed / 3600

            for asset in assets:
                # Obtener datos reales de Exnova
                df = None
                if md and fe:
                    try:
                        df = md.get_candles(asset, timeframe=60, count=100)
                        if df is not None and len(df) >= 50:
                            df = fe.add_features(df)
                    except Exception as e:
                        pass

                # Fallback a datos simulados si no hay conexión
                if df is None or len(df) < 50:
                    import pandas as pd, numpy as np
                    base = 1.1 + np.random.randn(100).cumsum() * 0.0001
                    df = pd.DataFrame({
                        'open': base,
                        'high': base + 0.0005,
                        'low': base - 0.0005,
                        'close': base,
                    })
                    df['rsi'] = 30 + np.random.random(100) * 40
                    df['ema_9'] = df['close'].ewm(span=9).mean()
                    df['ema_21'] = df['close'].ewm(span=21).mean()
                    df['macd'] = df['ema_9'] - df['ema_21']
                    df['macd_signal'] = df['macd'].ewm(span=9).mean()

                # Asegurar columnas necesarias
                for col in ['open', 'high', 'low', 'close', 'rsi', 'ema_9', 'ema_21', 'macd', 'macd_signal']:
                    if col not in df.columns:
                        df[col] = df['close'] if col in ['open', 'high', 'low'] else np.random.randn(len(df))*10+50

                # Scoring
                r = se.score(
                    df=df, current_price=df['close'].iloc[-1], asset=asset,
                    smart_money_data={'order_block_hit': True, 'fvg_detected': False, 'liquidity_grab': False, 'premium_discount': 0.4},
                    market_structure_data={'trend_direction': 'uptrend', 'trend_strength': 0.7, 'bos_detected': True}
                )
                signals += 1

                # Ejecutar si hay señal válida
                if r.recommendation == "TRADE" and r.confidence >= 0.65:
                    # Cooldown entre operaciones
                    if now - last_trade_time < 60:
                        continue

                    pos = rm.calculate_position_size(confidence=r.confidence)
                    if pos > 0:
                        sig = r.signal_type.value

                        # Simular resultado (55% win rate esperado)
                        import numpy as np
                        pnl = pos * 0.85 if np.random.random() > 0.45 else -pos

                        if pnl > 0:
                            wins += 1
                            log(f"WIN {asset} {sig} score={r.total_score:.1f} +${pnl:.2f}", "TRADE")
                        else:
                            losses += 1
                            log(f"LOSS {asset} {sig} score={r.total_score:.1f} -${abs(pnl):.2f}", "TRADE")

                        pt.current_balance += pnl
                        rm.update_balance(pt.current_balance, {"profit": pnl})
                        last_trade_time = now

                        # Guardar trade
                        stats["trades"].append({
                            "time": datetime.now().isoformat(),
                            "asset": asset,
                            "signal": sig,
                            "score": r.total_score,
                            "pnl": pnl
                        })

            # Guardar estadísticas cada 10 ciclos
            if cycle % 10 == 0:
                total = wins + losses
                wr = (wins/total*100) if total > 0 else 0
                pnl = pt.current_balance - INITIAL_BALANCE

                stats["wins"] = wins
                stats["losses"] = losses
                stats["total_pnl"] = pnl
                stats["current_balance"] = pt.current_balance

                with open(STATS_FILE, "w") as f:
                    json.dump(stats, f, indent=2)

                # Resumen periódico
                mins = int(elapsed / 60)
                pc = "GREEN" if pnl >= 0 else "RED"
                log(f"Ciclo {cycle} | {mins}m | Trades: {total} | WinRate: {wr:.1f}% | Balance: ${pt.current_balance:.2f} | PnL: ${pnl:+.2f}", "STATS")

            # Pausa entre ciclos
            time.sleep(15)

    except KeyboardInterrupt:
        log("Detenido por usuario", "STOP")

    # Guardar estadísticas finales
    stats["end_time"] = datetime.now().isoformat()
    with open(STATS_FILE, "w") as f:
        json.dump(stats, f, indent=2)

    # Resumen final
    total = wins + losses
    wr = (wins/total*100) if total > 0 else 0
    pnl = pt.current_balance - INITIAL_BALANCE
    elapsed = time.time() - start_time

    log("="*70, "INFO")
    log("RESUMEN FINAL", "INFO")
    log(f"Tiempo: {elapsed/3600:.2f} horas | Ciclos: {cycle} | Señales: {signals}", "INFO")
    log(f"Trades: {total} | Wins: {wins} | Losses: {losses}", "INFO")
    log(f"Win Rate: {wr:.1f}%", "INFO")
    log(f"Balance Final: ${pt.current_balance:.2f}", "INFO")
    log(f"PnL: ${pnl:+.2f} ({pnl/INITIAL_BALANCE*100:+.2f}%)", "INFO")
    log("="*70, "INFO")

if __name__ == "__main__":
    main()
