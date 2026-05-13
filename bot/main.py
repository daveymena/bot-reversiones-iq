#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║         EXNOVA ULTRA-SMART BOT v3.0 - MODO PRÁCTICA         ║
║      Dashboard en Consola | Estrategias Mejoradas | Rich     ║
╚══════════════════════════════════════════════════════════════╝
"""
import sys, os, time, signal, json, threading
from datetime import datetime, timedelta
from collections import deque

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
from rich.columns import Columns
from rich import box
from rich.style import Style

from config import Config
from data.market_data import MarketDataHandler
from core.advanced_risk_manager import initialize_risk_manager, RiskConfig
from core.unified_scoring_engine import get_scoring_engine
from strategies.technical import FeatureEngineer
from strategies.smart_reversal import SmartReversalStrategy
from strategies.multi_timeframe import MultiTimeframeAnalyzer
from engine.signal_engine import SignalEngine

console = Console()

# ─────────────────────────────────────────────
# ESTADO GLOBAL DEL BOT
# ─────────────────────────────────────────────
state = {
    "running": True,
    "balance": 0.0,
    "initial_balance": 0.0,
    "wins": 0,
    "losses": 0,
    "total_pnl": 0.0,
    "trades": [],           # lista de trades recientes
    "signals": deque(maxlen=100),  # señales analizadas
    "log": deque(maxlen=20),       # mensajes del log
    "cycle": 0,
    "start_time": time.time(),
    "last_trade_time": 0,
    "current_asset": "",
    "status": "INICIANDO",
    "active_order": None,
    "consecutive_losses": 0,
    "best_streak": 0,
    "current_streak": 0,
}

ASSETS_OTC = ["EURUSD-OTC", "GBPUSD-OTC", "AUDUSD-OTC", "EURJPY-OTC"]
ASSETS_NORMAL = ["EURUSD", "GBPUSD", "AUDUSD"]

INITIAL_BALANCE = 10000.0
MIN_CONFIDENCE = 0.68
TRADE_AMOUNT_PCT = 0.02   # 2% del balance por operación
EXPIRATION_SEC = 60       # 1 minuto por defecto
COOLDOWN_AFTER_LOSS = 120 # 2 minutos de cooldown tras pérdida
MIN_BETWEEN_TRADES = 60   # mínimo 1 minuto entre trades


def log(msg: str, level: str = "INFO"):
    now = datetime.now().strftime("%H:%M:%S")
    icons = {"INFO": "●", "WIN": "✔", "LOSS": "✘", "WARN": "⚠", "ERROR": "✖", "SIGNAL": "▶", "WAIT": "◌"}
    colors = {"INFO": "white", "WIN": "green", "LOSS": "red", "WARN": "yellow", "ERROR": "bright_red", "SIGNAL": "cyan", "WAIT": "dim"}
    icon = icons.get(level, "●")
    color = colors.get(level, "white")
    state["log"].append(f"[{now}] [{color}]{icon} {msg}[/{color}]")


def make_header() -> Panel:
    elapsed = int(time.time() - state["start_time"])
    h, m, s = elapsed // 3600, (elapsed % 3600) // 60, elapsed % 60
    total = state["wins"] + state["losses"]
    wr = (state["wins"] / total * 100) if total > 0 else 0
    pnl = state["total_pnl"]
    pnl_color = "green" if pnl >= 0 else "red"
    pnl_sign = "+" if pnl >= 0 else ""

    mode_color = "cyan"
    status_color = "green" if state["status"] == "OPERANDO" else "yellow" if state["status"] == "ANALIZANDO" else "dim"

    title = Text()
    title.append("EXNOVA ULTRA-SMART BOT v3.0", style="bold cyan")
    title.append("  •  ", style="dim")
    title.append("MODO PRÁCTICA", style="bold yellow")
    title.append("  •  ", style="dim")
    title.append(f"{h:02d}:{m:02d}:{s:02d}", style="white")

    grid = Table.grid(expand=True, padding=(0, 2))
    grid.add_column(justify="center")
    grid.add_column(justify="center")
    grid.add_column(justify="center")
    grid.add_column(justify="center")
    grid.add_column(justify="center")
    grid.add_column(justify="center")

    grid.add_row(
        f"[dim]Balance[/dim]\n[bold white]${state['balance']:,.2f}[/bold white]",
        f"[dim]PnL Total[/dim]\n[bold {pnl_color}]{pnl_sign}${pnl:.2f}[/bold {pnl_color}]",
        f"[dim]Win Rate[/dim]\n[bold {'green' if wr >= 60 else 'yellow' if wr >= 50 else 'red'}]{wr:.1f}%[/bold {'green' if wr >= 60 else 'yellow' if wr >= 50 else 'red'}]",
        f"[dim]Wins / Losses[/dim]\n[bold green]{state['wins']}[/bold green] / [bold red]{state['losses']}[/bold red]",
        f"[dim]Activo[/dim]\n[bold cyan]{state['current_asset'] or '---'}[/bold cyan]",
        f"[dim]Estado[/dim]\n[bold {status_color}]{state['status']}[/bold {status_color}]",
    )

    return Panel(grid, title=title, border_style="cyan", padding=(0, 1))


def make_trades_table() -> Panel:
    table = Table(
        box=box.SIMPLE_HEAD,
        show_header=True,
        header_style="bold dim",
        expand=True,
        padding=(0, 1),
    )
    table.add_column("Hora", style="dim", width=8)
    table.add_column("Activo", width=12)
    table.add_column("Dirección", width=8, justify="center")
    table.add_column("Monto", width=8, justify="right")
    table.add_column("Confianza", width=10, justify="center")
    table.add_column("Resultado", width=10, justify="right")
    table.add_column("PnL", width=10, justify="right")

    trades = list(state["trades"])[-12:]
    for t in reversed(trades):
        direction_style = "bold green" if t["direction"] == "CALL" else "bold red"
        result_style = "green" if t["result"] == "WIN" else "red" if t["result"] == "LOSS" else "yellow"
        pnl_val = t.get("pnl", 0)
        pnl_str = f"[{'green' if pnl_val >= 0 else 'red'}]{'+' if pnl_val >= 0 else ''}{pnl_val:.2f}[/{'green' if pnl_val >= 0 else 'red'}]"

        table.add_row(
            t["time"],
            t["asset"],
            f"[{direction_style}]{t['direction']}[/{direction_style}]",
            f"${t['amount']:.2f}",
            f"{t['confidence']*100:.0f}%",
            f"[{result_style}]{t['result']}[/{result_style}]",
            pnl_str,
        )

    if not trades:
        table.add_row("[dim]---[/dim]", "[dim]Esperando señales...[/dim]", "", "", "", "", "")

    return Panel(table, title="[bold]Historial de Operaciones[/bold]", border_style="blue", padding=(0, 1))


def make_log_panel() -> Panel:
    text = Text()
    for line in list(state["log"])[-14:]:
        text.append_text(Text.from_markup(line + "\n"))
    return Panel(text, title="[bold]Log en Tiempo Real[/bold]", border_style="dim", padding=(0, 1))


def make_signals_panel() -> Panel:
    table = Table(box=box.SIMPLE, show_header=True, header_style="bold dim", expand=True, padding=(0, 1))
    table.add_column("Activo", width=12)
    table.add_column("Señal", width=7, justify="center")
    table.add_column("Score", width=7, justify="center")
    table.add_column("Conf.", width=7, justify="center")
    table.add_column("Fase", width=10)
    table.add_column("Acción", width=10, justify="center")

    signals = list(state["signals"])[-8:]
    for s in reversed(signals):
        sig = s.get("signal", "---")
        sig_style = "green" if sig == "CALL" else "red" if sig == "PUT" else "dim"
        score = s.get("score", 0)
        score_style = "green" if score >= 75 else "yellow" if score >= 60 else "red"
        conf = s.get("confidence", 0)
        action = s.get("action", "WAIT")
        action_style = "bold green" if action == "TRADE" else "dim"

        table.add_row(
            s.get("asset", ""),
            f"[{sig_style}]{sig}[/{sig_style}]",
            f"[{score_style}]{score:.0f}[/{score_style}]",
            f"{conf*100:.0f}%",
            s.get("phase", ""),
            f"[{action_style}]{action}[/{action_style}]",
        )

    if not signals:
        table.add_row("[dim]---[/dim]", "", "", "", "[dim]Escaneando...[/dim]", "")

    return Panel(table, title="[bold]Señales Analizadas[/bold]", border_style="magenta", padding=(0, 1))


def make_risk_panel() -> Panel:
    total = state["wins"] + state["losses"]
    wr = (state["wins"] / total * 100) if total > 0 else 0
    dd = ((state["initial_balance"] - state["balance"]) / state["initial_balance"] * 100) if state["initial_balance"] > 0 else 0
    dd_color = "red" if dd > 10 else "yellow" if dd > 5 else "green"
    elapsed_h = (time.time() - state["start_time"]) / 3600
    trades_per_h = total / elapsed_h if elapsed_h > 0.01 else 0
    streak = state["current_streak"]
    streak_str = f"[green]+{streak}[/green]" if streak > 0 else f"[red]{streak}[/red]" if streak < 0 else "[dim]0[/dim]"

    grid = Table.grid(expand=True, padding=(0, 1))
    grid.add_column(justify="left")
    grid.add_column(justify="right")
    grid.add_row("[dim]Drawdown[/dim]", f"[{dd_color}]{dd:.2f}%[/{dd_color}]")
    grid.add_row("[dim]Trades totales[/dim]", f"[white]{total}[/white]")
    grid.add_row("[dim]Trades/hora[/dim]", f"[white]{trades_per_h:.1f}[/white]")
    grid.add_row("[dim]Racha actual[/dim]", streak_str)
    grid.add_row("[dim]Mejor racha[/dim]", f"[green]+{state['best_streak']}[/green]")
    grid.add_row("[dim]Cons. pérdidas[/dim]", f"[{'red' if state['consecutive_losses'] >= 3 else 'white'}]{state['consecutive_losses']}[/{'red' if state['consecutive_losses'] >= 3 else 'white'}]")
    grid.add_row("[dim]Ciclo[/dim]", f"[white]{state['cycle']}[/white]")

    return Panel(grid, title="[bold]Gestión de Riesgo[/bold]", border_style="yellow", padding=(0, 1))


def build_layout() -> Layout:
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=5),
        Layout(name="body"),
        Layout(name="footer", size=16),
    )
    layout["body"].split_row(
        Layout(name="signals", ratio=3),
        Layout(name="risk", ratio=1),
    )
    layout["footer"].split_row(
        Layout(name="trades", ratio=3),
        Layout(name="log", ratio=2),
    )
    return layout


def update_layout(layout: Layout):
    layout["header"].update(make_header())
    layout["signals"].update(make_signals_panel())
    layout["risk"].update(make_risk_panel())
    layout["trades"].update(make_trades_table())
    layout["log"].update(make_log_panel())


def record_trade(asset, direction, amount, confidence, result, pnl):
    state["trades"].append({
        "time": datetime.now().strftime("%H:%M:%S"),
        "asset": asset,
        "direction": direction,
        "amount": amount,
        "confidence": confidence,
        "result": result,
        "pnl": pnl,
    })
    if result == "WIN":
        state["wins"] += 1
        state["consecutive_losses"] = 0
        state["current_streak"] = max(0, state["current_streak"]) + 1
        if state["current_streak"] > state["best_streak"]:
            state["best_streak"] = state["current_streak"]
    elif result == "LOSS":
        state["losses"] += 1
        state["consecutive_losses"] += 1
        state["current_streak"] = min(0, state["current_streak"]) - 1
    state["total_pnl"] += pnl
    state["balance"] += pnl


def bot_loop(market_data: MarketDataHandler, rm, se: any, fe: FeatureEngineer, signal_engine: "SignalEngine"):
    """Loop principal del bot"""
    global ASSETS_OTC

    email = os.getenv("EXNOVA_EMAIL", "")
    password = os.getenv("EXNOVA_PASSWORD", "")

    log("Conectando a Exnova (PRACTICE)...", "INFO")
    state["status"] = "CONECTANDO"

    connected = market_data.connect(email, password)
    if not connected:
        log("ERROR: No se pudo conectar a Exnova. Verificá credenciales.", "ERROR")
        state["status"] = "ERROR"
        return

    # Obtener balance real de la cuenta práctica
    try:
        balance = market_data.get_balance()
        if balance and balance > 0:
            state["balance"] = float(balance)
            state["initial_balance"] = float(balance)
            rm.initialize(float(balance))
            log(f"Conectado. Balance práctica: ${balance:.2f}", "INFO")
        else:
            state["balance"] = INITIAL_BALANCE
            state["initial_balance"] = INITIAL_BALANCE
            rm.initialize(INITIAL_BALANCE)
            log(f"Conectado. Usando balance simulado: ${INITIAL_BALANCE:.2f}", "INFO")
    except Exception as e:
        state["balance"] = INITIAL_BALANCE
        state["initial_balance"] = INITIAL_BALANCE
        rm.initialize(INITIAL_BALANCE)
        log(f"Balance no disponible, usando ${INITIAL_BALANCE:.2f}", "WARN")

    log("Sistema listo. Iniciando escaneo de mercado...", "INFO")
    state["status"] = "ANALIZANDO"

    asset_idx = 0
    last_reconnect_check = time.time()

    while state["running"]:
        try:
            state["cycle"] += 1
            now = time.time()

            # Verificar reconexión cada 5 minutos
            if now - last_reconnect_check > 300:
                if not market_data.is_really_connected():
                    log("Reconectando...", "WARN")
                    market_data.reconnect(email, password)
                last_reconnect_check = now

            # Rotar activos
            asset = ASSETS_OTC[asset_idx % len(ASSETS_OTC)]
            asset_idx += 1
            state["current_asset"] = asset

            # Cooldown global entre trades
            time_since_last = now - state["last_trade_time"]
            if state["consecutive_losses"] >= 3:
                required_cooldown = COOLDOWN_AFTER_LOSS * 2
                if time_since_last < required_cooldown:
                    state["status"] = "COOLDOWN"
                    log(f"Cooldown activo: {int(required_cooldown - time_since_last)}s más (3+ pérdidas seguidas)", "WAIT")
                    time.sleep(10)
                    continue

            # Analizar señal
            state["status"] = "ANALIZANDO"
            result = signal_engine.analyze(asset, market_data, fe)

            if result:
                state["signals"].append(result)

                if result["action"] == "TRADE" and result["confidence"] >= MIN_CONFIDENCE:
                    # Verificar cooldown mínimo
                    if time_since_last < MIN_BETWEEN_TRADES:
                        log(f"Cooldown mínimo: esperando {int(MIN_BETWEEN_TRADES - time_since_last)}s", "WAIT")
                    elif rm.is_stopped:
                        log(f"Risk Manager: {rm.stop_reason}", "WARN")
                    else:
                        # Calcular monto con Kelly
                        amount = rm.calculate_position_size(confidence=result["confidence"])
                        if amount > 0:
                            execute_trade(market_data, rm, asset, result, amount)
            else:
                log(f"Sin datos suficientes para {asset}", "WARN")

            time.sleep(8)

        except KeyboardInterrupt:
            state["running"] = False
            break
        except Exception as e:
            log(f"Error en loop: {e}", "ERROR")
            time.sleep(5)

    log("Bot detenido.", "INFO")
    state["status"] = "DETENIDO"


def execute_trade(market_data: MarketDataHandler, rm, asset: str, signal: dict, amount: float):
    """Ejecuta y monitorea una operación en la cuenta práctica"""
    direction = signal["signal"]  # CALL o PUT
    confidence = signal["confidence"]
    expiration = signal.get("expiration", EXPIRATION_SEC)

    log(f"OPERANDO: {asset} {direction} ${amount:.2f} conf={confidence*100:.0f}%", "SIGNAL")
    state["status"] = "OPERANDO"
    state["last_trade_time"] = time.time()

    try:
        action = "call" if direction == "CALL" else "put"
        duration = max(1, expiration // 60)  # en minutos

        check, order_id = market_data.buy(asset, amount, action, duration)

        if check:
            log(f"Orden abierta: {order_id} | {direction} ${amount:.2f} exp={duration}min", "INFO")
            state["active_order"] = order_id

            # Esperar a que expire la operación
            time.sleep(expiration + 5)

            # Verificar resultado
            try:
                result_data = market_data.api.check_win_v4(order_id)
                if result_data is not None:
                    profit = float(result_data)
                    if profit > 0:
                        pnl = profit
                        res = "WIN"
                        log(f"WIN +${profit:.2f} | {asset} {direction}", "WIN")
                    elif profit == 0:
                        pnl = 0
                        res = "DRAW"
                        log(f"DRAW $0 | {asset} {direction}", "WARN")
                    else:
                        pnl = -amount
                        res = "LOSS"
                        log(f"LOSS -${amount:.2f} | {asset} {direction}", "LOSS")
                else:
                    # Sin resultado: asumir pérdida conservadora
                    pnl = -amount
                    res = "LOSS"
                    log(f"Sin resultado de Exnova, asumiendo LOSS", "WARN")
            except Exception as e:
                log(f"Error verificando resultado: {e}", "WARN")
                pnl = 0
                res = "DRAW"

            record_trade(asset, direction, amount, confidence, res, pnl)
            rm.update_balance(state["balance"], {"profit": pnl})
            state["active_order"] = None

        else:
            log(f"Orden rechazada por Exnova: {order_id}", "ERROR")

    except Exception as e:
        log(f"Error ejecutando trade: {e}", "ERROR")

    state["status"] = "ANALIZANDO"


def signal_handler(sig, frame):
    state["running"] = False
    log("Deteniendo bot (Ctrl+C)...", "WARN")


def main():
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    console.clear()
    console.print(Panel.fit(
        "[bold cyan]EXNOVA ULTRA-SMART BOT v3.0[/bold cyan]\n"
        "[dim]Iniciando componentes...[/dim]",
        border_style="cyan"
    ))

    # Inicializar componentes
    risk_config = RiskConfig(
        max_drawdown_daily=0.10,
        max_trades_per_hour=6,
        cooldown_after_loss_seconds=COOLDOWN_AFTER_LOSS,
        min_confidence_threshold=MIN_CONFIDENCE,
        stop_after_consecutive_losses=4,
    )
    rm = initialize_risk_manager(INITIAL_BALANCE, risk_config)
    se = get_scoring_engine()
    fe = FeatureEngineer()

    market_data = MarketDataHandler(broker_name="exnova", account_type="PRACTICE")

    from engine.signal_engine import SignalEngine
    signal_engine = SignalEngine(se)

    state["start_time"] = time.time()

    # Lanzar bot en thread separado
    bot_thread = threading.Thread(
        target=bot_loop,
        args=(market_data, rm, se, fe, signal_engine),
        daemon=True
    )
    bot_thread.start()

    # Dashboard en vivo
    layout = build_layout()

    with Live(layout, console=console, refresh_per_second=2, screen=True):
        while state["running"] or state["status"] not in ("DETENIDO", "ERROR"):
            update_layout(layout)
            time.sleep(0.5)
        update_layout(layout)
        time.sleep(2)

    # Resumen final
    total = state["wins"] + state["losses"]
    wr = (state["wins"] / total * 100) if total > 0 else 0
    console.print()
    console.print(Panel(
        f"[bold]Resumen Final[/bold]\n\n"
        f"  Trades: {total}  |  Wins: [green]{state['wins']}[/green]  |  Losses: [red]{state['losses']}[/red]\n"
        f"  Win Rate: [{'green' if wr >= 60 else 'yellow'}]{wr:.1f}%[/]\n"
        f"  PnL Total: [{'green' if state['total_pnl'] >= 0 else 'red'}]{'+' if state['total_pnl'] >= 0 else ''}{state['total_pnl']:.2f}[/]\n"
        f"  Balance Final: ${state['balance']:.2f}",
        border_style="cyan",
        title="[bold cyan]BOT DETENIDO[/bold cyan]"
    ))


if __name__ == "__main__":
    main()
