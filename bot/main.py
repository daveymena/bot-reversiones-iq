#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════╗
║       EXNOVA ULTRA-SMART BOT v4.0 — SISTEMA DE APRENDIZAJE          ║
║  Detecta zonas · Analiza contexto · Aprende de cada operación        ║
╚══════════════════════════════════════════════════════════════════════╝
"""
import sys, os, time, signal, json, threading
from datetime import datetime
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
from rich import box

from config import Config
from data.market_data import MarketDataHandler
from core.advanced_risk_manager import initialize_risk_manager, RiskConfig
from brain.adaptive_learner import get_adaptive_learner
from brain.market_memory import get_market_memory
from brain.trade_evaluator import TradeEvaluator
from engine.intelligent_engine import IntelligentEngine

console = Console()

# ─── Estado global ───────────────────────────────────────────────────────────
state = {
    "running": True,
    "balance": 0.0,
    "initial_balance": 0.0,
    "wins": 0,
    "losses": 0,
    "total_pnl": 0.0,
    "trades": [],
    "log": deque(maxlen=22),
    "cycle": 0,
    "start_time": time.time(),
    "last_trade_time": 0,
    "current_asset": "",
    "status": "INICIANDO",
    "active_order": None,
    "consecutive_losses": 0,
    "best_streak": 0,
    "current_streak": 0,
    "last_signal": {},
    "last_diagnosis": [],
    "zones_by_asset": {},
    "learning_summary": "Acumulando datos...",
    "last_zone_info": "",
}

ASSETS = ["EURUSD-OTC", "GBPUSD-OTC", "AUDUSD-OTC", "EURJPY-OTC"]
INITIAL_BALANCE    = 10_000.0
MIN_CONFIDENCE     = 0.65
TRADE_AMOUNT_PCT   = 0.02
COOLDOWN_AFTER_LOSS = 90
MIN_BETWEEN_TRADES  = 45
MAX_CONSEC_LOSSES   = 4


# ─── Logging ─────────────────────────────────────────────────────────────────

def log(msg: str, level: str = "INFO"):
    now = datetime.now().strftime("%H:%M:%S")
    icons  = {"INFO":"●","WIN":"✔","LOSS":"✘","WARN":"⚠","ERROR":"✖",
              "SIGNAL":"▶","WAIT":"◌","LEARN":"◈","ZONE":"◆"}
    colors = {"INFO":"white","WIN":"green","LOSS":"red","WARN":"yellow",
              "ERROR":"bright_red","SIGNAL":"cyan","WAIT":"dim",
              "LEARN":"magenta","ZONE":"blue"}
    icon  = icons.get(level, "●")
    color = colors.get(level, "white")
    state["log"].append(f"[{now}] [{color}]{icon} {msg}[/{color}]")


# ─── Paneles del dashboard ────────────────────────────────────────────────────

def _wr_color(wr): return "green" if wr >= 62 else "yellow" if wr >= 52 else "red"
def _pnl_color(v): return "green" if v >= 0 else "red"


def make_header() -> Panel:
    elapsed = int(time.time() - state["start_time"])
    h, m, s = elapsed // 3600, (elapsed % 3600) // 60, elapsed % 60
    total = state["wins"] + state["losses"]
    wr = (state["wins"] / total * 100) if total > 0 else 0
    pnl = state["total_pnl"]
    bal = state["balance"]

    learner = get_adaptive_learner()
    global_wr = learner.get_global_winrate()

    title = Text()
    title.append("EXNOVA SMART BOT v4.0", style="bold cyan")
    title.append("  ·  MODO PRÁCTICA  ·  APRENDIZAJE ACTIVO", style="bold yellow")
    title.append(f"  ·  {h:02d}:{m:02d}:{s:02d}", style="white")

    grid = Table.grid(expand=True, padding=(0, 2))
    for _ in range(7): grid.add_column(justify="center")

    grid.add_row(
        f"[dim]Balance[/dim]\n[bold white]${bal:,.2f}[/bold white]",
        f"[dim]PnL[/dim]\n[bold {_pnl_color(pnl)}]{'+' if pnl>=0 else ''}${pnl:.2f}[/bold {_pnl_color(pnl)}]",
        f"[dim]Win Rate[/dim]\n[bold {_wr_color(wr)}]{wr:.1f}%[/bold {_wr_color(wr)}]",
        f"[dim]W / L[/dim]\n[bold green]{state['wins']}[/bold green] / [bold red]{state['losses']}[/bold red]",
        f"[dim]Bot WR aprendido[/dim]\n[bold {'green' if global_wr>=0.55 else 'yellow'}]{global_wr:.1%}[/bold {'green' if global_wr>=0.55 else 'yellow'}]",
        f"[dim]Activo[/dim]\n[bold cyan]{state['current_asset'] or '---'}[/bold cyan]",
        f"[dim]Estado[/dim]\n[bold {'green' if state['status']=='OPERANDO' else 'yellow' if state['status']=='ANALIZANDO' else 'dim'}]{state['status']}[/bold {'green' if state['status']=='OPERANDO' else 'yellow' if state['status']=='ANALIZANDO' else 'dim'}]",
    )
    return Panel(grid, title=title, border_style="cyan", padding=(0,1))


def make_signal_panel() -> Panel:
    sig = state.get("last_signal", {})
    table = Table(box=box.SIMPLE_HEAD, show_header=True, header_style="bold dim",
                  expand=True, padding=(0,1))
    table.add_column("Activo", width=12)
    table.add_column("Señal", width=7, justify="center")
    table.add_column("Acción", width=8, justify="center")
    table.add_column("Score", width=7, justify="center")
    table.add_column("IA", width=11, justify="center")
    table.add_column("Zona", width=10, justify="center")
    table.add_column("Patrón", width=14)
    table.add_column("Exp.", width=10, justify="center")
    table.add_column("Análisis IA", ratio=1)

    if sig:
        s_dir  = sig.get("signal", "NEUTRAL")
        s_col  = "green" if s_dir == "CALL" else "red" if s_dir == "PUT" else "dim"
        act    = sig.get("action", "WAIT")
        a_col  = "bold green" if act == "TRADE" else "dim"
        score  = sig.get("score", 0)
        sc_col = "green" if score >= 65 else "yellow" if score >= 45 else "red"
        zone_str = f"{sig.get('zone', 0):.5f}" if sig.get("zone") else "---"
        pattern  = sig.get("pattern", "---") or "---"

        # IA info
        ai_label = sig.get("ai_label", "")
        ai_score = sig.get("ai_score", 0)
        ai_colors = {
            "EXCELENTE": "bold green", "BUENO": "green",
            "MODERADO": "yellow", "DÉBIL": "orange1",
            "SKIP": "red", "NORMAL": "dim",
        }
        ai_col = ai_colors.get(ai_label, "dim")
        ai_str = f"[{ai_col}]{ai_label}[/{ai_col}] [dim]{ai_score:.0f}[/dim]" if ai_label else "[dim]---[/dim]"

        # Narrativa IA (truncada para caber)
        narrative = (sig.get("ai_narrative", "") or sig.get("reason", "") or "")[:70]

        # Expiración
        exp_min   = sig.get("expiration_minutes", 0)
        exp_label = sig.get("expiration_label", "")
        exp_color = sig.get("expiration_color", "dim")
        exp_str   = f"[{exp_color}]{exp_min}m {exp_label}[/{exp_color}]" if exp_min > 0 else "[dim]---[/dim]"

        table.add_row(
            sig.get("asset", ""),
            f"[{s_col}]{s_dir}[/{s_col}]",
            f"[{a_col}]{act}[/{a_col}]",
            f"[{sc_col}]{score:.0f}[/{sc_col}]",
            ai_str,
            zone_str,
            f"[cyan]{pattern}[/cyan]",
            exp_str,
            f"[dim]{narrative}[/dim]",
        )
    else:
        table.add_row("[dim]---[/dim]", "", "", "", "", "", "", "", "[dim]Escaneando...[/dim]")

    return Panel(table, title="[bold]Última Señal  ·  Motor IA Activo[/bold]", border_style="magenta", padding=(0,1))


def make_zones_panel() -> Panel:
    table = Table(box=box.SIMPLE, show_header=True, header_style="bold dim",
                  expand=True, padding=(0,1))
    table.add_column("Activo", width=13)
    table.add_column("Nivel", width=10, justify="right")
    table.add_column("Tipo", width=11, justify="center")
    table.add_column("Fuerza", width=8, justify="center")
    table.add_column("Toques", width=7, justify="center")
    table.add_column("Hold%", width=7, justify="center")
    table.add_column("Multi-TF", width=9, justify="center")

    memory = get_market_memory()
    rows_added = 0
    for asset in ASSETS:
        zones = memory.get_all_zones(asset, min_strength=0.35)
        for z in zones[:2]:
            if rows_added >= 8:
                break
            zs = z.strength
            zs_col = "green" if zs >= 0.7 else "yellow" if zs >= 0.5 else "red"
            hr = z.hold_rate
            hr_col = "green" if hr >= 0.7 else "yellow"
            t_col = "blue" if z.zone_type == "support" else "red" if z.zone_type == "resistance" else "dim"
            multi = "✔" if z.touches >= 3 else "·"
            table.add_row(
                asset,
                f"{z.level:.5f}",
                f"[{t_col}]{z.zone_type.upper()[:4]}[/{t_col}]",
                f"[{zs_col}]{zs:.2f}[/{zs_col}]",
                str(z.touches),
                f"[{hr_col}]{hr:.0%}[/{hr_col}]",
                f"[green]{multi}[/green]",
            )
            rows_added += 1

    if rows_added == 0:
        table.add_row("[dim]---[/dim]", "", "", "", "", "", "[dim]Detectando zonas...[/dim]")

    return Panel(table, title="[bold]Zonas Activas Detectadas[/bold]", border_style="blue", padding=(0,1))


def make_trades_table() -> Panel:
    table = Table(box=box.SIMPLE_HEAD, show_header=True, header_style="bold dim",
                  expand=True, padding=(0,1))
    table.add_column("Hora", style="dim", width=8)
    table.add_column("Activo", width=12)
    table.add_column("Dir.", width=6, justify="center")
    table.add_column("$", width=8, justify="right")
    table.add_column("Conf.", width=6, justify="center")
    table.add_column("Patrón", width=14)
    table.add_column("Zona.Str", width=8, justify="center")
    table.add_column("Res.", width=6, justify="center")
    table.add_column("PnL", width=9, justify="right")

    for t in reversed(list(state["trades"])[-10:]):
        d_col = "green" if t["direction"] == "CALL" else "red"
        r_col = "green" if t["result"] == "WIN" else "red" if t["result"] == "LOSS" else "yellow"
        pnl = t.get("pnl", 0)
        pnl_str = f"[{'green' if pnl>=0 else 'red'}]{'+' if pnl>=0 else ''}{pnl:.2f}[/]"
        table.add_row(
            t["time"], t["asset"],
            f"[{d_col}]{t['direction']}[/{d_col}]",
            f"${t['amount']:.2f}",
            f"{t['confidence']*100:.0f}%",
            t.get("pattern", "---") or "---",
            f"{t.get('zone_strength', 0):.2f}",
            f"[{r_col}]{t['result']}[/{r_col}]",
            pnl_str,
        )

    if not state["trades"]:
        table.add_row("[dim]---[/dim]", "[dim]Esperando primera operación...[/dim]", "", "", "", "", "", "", "")

    return Panel(table, title="[bold]Historial de Operaciones[/bold]", border_style="blue", padding=(0,1))


def make_learning_panel() -> Panel:
    learner = get_adaptive_learner()
    grid = Table.grid(expand=True, padding=(0,1))
    grid.add_column(justify="left")
    grid.add_column(justify="right")

    wr = learner.get_global_winrate()
    grid.add_row("[dim]Trades aprendidos[/dim]", f"[white]{learner.total_trades}[/white]")
    grid.add_row("[dim]WR aprendido[/dim]", f"[{'green' if wr>=0.55 else 'yellow'}]{wr:.1%}[/]")

    # IA del último análisis
    sig = state.get("last_signal", {})
    ai_label   = sig.get("ai_label", "")
    ai_score   = sig.get("ai_score", 0)
    ai_colors  = {"EXCELENTE":"green","BUENO":"green","MODERADO":"yellow",
                  "DÉBIL":"orange1","SKIP":"red","NORMAL":"dim"}
    if ai_label:
        ai_col = ai_colors.get(ai_label, "dim")
        grid.add_row("[dim]IA último análisis[/dim]",
                     f"[{ai_col}]{ai_label} {ai_score:.0f}[/{ai_col}]")

    top = learner.get_top_conditions(3)
    for c in top:
        name = c["condition"].replace("_", " ")[:18]
        cwr  = c["win_rate"]
        grid.add_row(f"[dim]↑ {name}[/dim]",
                     f"[{'green' if cwr>=0.6 else 'yellow'}]{cwr:.0%}[/]")

    grid.add_row("", "")
    grid.add_row("[dim]Umbral zona[/dim]",     f"[cyan]{learner.get_threshold('min_zone_strength'):.2f}[/cyan]")
    grid.add_row("[dim]Min. score[/dim]",      f"[cyan]{learner.get_min_score():.2f}[/cyan]")

    if state.get("last_diagnosis"):
        grid.add_row("", "")
        for line in state["last_diagnosis"][:3]:
            text = Text.from_markup(line)
            grid.add_row(text, "")

    return Panel(grid, title="[bold]IA + Aprendizaje[/bold]", border_style="magenta", padding=(0,1))


def make_log_panel() -> Panel:
    text = Text()
    for line in list(state["log"])[-16:]:
        text.append_text(Text.from_markup(line + "\n"))
    return Panel(text, title="[bold]Log[/bold]", border_style="dim", padding=(0,1))


def make_risk_panel() -> Panel:
    total = state["wins"] + state["losses"]
    wr = (state["wins"] / total * 100) if total > 0 else 0
    dd = ((state["initial_balance"] - state["balance"]) / state["initial_balance"] * 100) \
         if state["initial_balance"] > 0 else 0
    dd_col = "red" if dd > 10 else "yellow" if dd > 5 else "green"
    elapsed_h = max((time.time() - state["start_time"]) / 3600, 0.01)
    trades_h = total / elapsed_h
    streak = state["current_streak"]
    streak_str = f"[green]+{streak}[/green]" if streak > 0 else f"[red]{streak}[/red]"

    grid = Table.grid(expand=True, padding=(0,1))
    grid.add_column(justify="left"); grid.add_column(justify="right")
    grid.add_row("[dim]Drawdown[/dim]", f"[{dd_col}]{dd:.2f}%[/{dd_col}]")
    grid.add_row("[dim]Trades totales[/dim]", str(total))
    grid.add_row("[dim]Trades/hora[/dim]", f"{trades_h:.1f}")
    grid.add_row("[dim]Racha[/dim]", streak_str)
    grid.add_row("[dim]Mejor racha[/dim]", f"[green]+{state['best_streak']}[/green]")
    grid.add_row("[dim]Pérd. seguidas[/dim]",
                 f"[{'red' if state['consecutive_losses']>=3 else 'white'}]{state['consecutive_losses']}[/]")
    grid.add_row("[dim]Ciclo[/dim]", str(state["cycle"]))
    return Panel(grid, title="[bold]Riesgo[/bold]", border_style="yellow", padding=(0,1))


def build_layout() -> Layout:
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=5),
        Layout(name="signal_row", size=5),
        Layout(name="middle"),
        Layout(name="bottom"),
    )
    layout["middle"].split_row(
        Layout(name="zones", ratio=3),
        Layout(name="risk", ratio=1),
    )
    layout["bottom"].split_row(
        Layout(name="trades", ratio=3),
        Layout(name="right_col", ratio=2),
    )
    layout["right_col"].split_column(
        Layout(name="learning"),
        Layout(name="log_panel"),
    )
    return layout


def update_layout(layout: Layout):
    layout["header"].update(make_header())
    layout["signal_row"].update(make_signal_panel())
    layout["zones"].update(make_zones_panel())
    layout["risk"].update(make_risk_panel())
    layout["trades"].update(make_trades_table())
    layout["learning"].update(make_learning_panel())
    layout["log_panel"].update(make_log_panel())


def record_trade(asset, direction, amount, confidence, result, pnl,
                 pattern="", zone_strength=0.0):
    state["trades"].append({
        "time": datetime.now().strftime("%H:%M:%S"),
        "asset": asset, "direction": direction, "amount": amount,
        "confidence": confidence, "result": result, "pnl": pnl,
        "pattern": pattern, "zone_strength": zone_strength,
    })
    if result == "WIN":
        state["wins"] += 1
        state["consecutive_losses"] = 0
        state["current_streak"] = max(0, state["current_streak"]) + 1
        state["best_streak"] = max(state["best_streak"], state["current_streak"])
    elif result == "LOSS":
        state["losses"] += 1
        state["consecutive_losses"] += 1
        state["current_streak"] = min(0, state["current_streak"]) - 1
    state["total_pnl"] += pnl
    state["balance"] = max(0, state["balance"] + pnl)


# ─── Bucle principal ──────────────────────────────────────────────────────────

def bot_loop(market_data: MarketDataHandler, rm, engine: IntelligentEngine):
    email    = os.getenv("EXNOVA_EMAIL", "")
    password = os.getenv("EXNOVA_PASSWORD", "")
    learner  = get_adaptive_learner()
    memory   = get_market_memory()
    evaluator = TradeEvaluator()

    log("Conectando a Exnova PRACTICE...", "INFO")
    state["status"] = "CONECTANDO"

    if not market_data.connect(email, password):
        log("ERROR: No se pudo conectar. Verificá credenciales.", "ERROR")
        state["status"] = "ERROR"
        return

    try:
        balance = market_data.get_balance()
        balance = float(balance) if balance and float(balance) > 0 else INITIAL_BALANCE
    except Exception:
        balance = INITIAL_BALANCE

    state["balance"] = balance
    state["initial_balance"] = balance
    rm.initialize(balance)
    log(f"Conectado. Balance práctica: ${balance:,.2f}", "INFO")
    log(f"Sistema de aprendizaje cargado. {learner.summary()}", "LEARN")
    log("Iniciando escaneo de zonas y análisis de mercado...", "INFO")
    state["status"] = "ANALIZANDO"

    asset_idx = 0
    last_reconnect = time.time()

    while state["running"]:
        try:
            state["cycle"] += 1
            now = time.time()

            # Reconexión periódica
            if now - last_reconnect > 240:
                if not market_data.is_really_connected():
                    log("Reconectando...", "WARN")
                    market_data.reconnect(email, password)
                last_reconnect = now

            # Cooldown por pérdidas consecutivas
            if state["consecutive_losses"] >= MAX_CONSEC_LOSSES:
                state["status"] = "PAUSA_RIESGO"
                log(f"PAUSA: {state['consecutive_losses']} pérdidas seguidas. Esperando 5 min.", "WARN")
                time.sleep(300)
                state["consecutive_losses"] = 0
                continue

            asset = ASSETS[asset_idx % len(ASSETS)]
            asset_idx += 1
            state["current_asset"] = asset
            state["status"] = "ANALIZANDO"

            # ── Analizar con el motor inteligente ──
            signal = engine.analyze(asset, market_data)

            if signal:
                state["last_signal"] = signal
                action     = signal.get("action", "WAIT")
                confidence = signal.get("confidence", 0)
                score      = signal.get("score", 0)

                if action == "TRADE" and confidence >= MIN_CONFIDENCE:
                    time_since = now - state["last_trade_time"]
                    cooldown_needed = COOLDOWN_AFTER_LOSS if state["consecutive_losses"] > 0 else MIN_BETWEEN_TRADES
                    if time_since < cooldown_needed:
                        log(f"Cooldown: {int(cooldown_needed - time_since)}s más", "WAIT")
                    elif rm.is_stopped:
                        log(f"Risk Manager activo: {rm.stop_reason}", "WARN")
                    else:
                        amount = rm.calculate_position_size(confidence=confidence)
                        if amount > 0:
                            execute_trade(market_data, rm, signal, amount, learner, memory, evaluator)
                elif action == "WAIT":
                    reason = signal.get("reason", "")
                    if reason and "zona" in reason.lower():
                        log(f"{asset} | {reason}", "ZONE")
                    elif reason:
                        log(f"{asset} | {reason}", "WAIT")
                else:
                    log(f"{asset} | Score {score:.0f} | {signal.get('reason', '')} ", "WAIT")

            time.sleep(6)

        except KeyboardInterrupt:
            state["running"] = False
            break
        except Exception as e:
            log(f"Error en loop: {e}", "ERROR")
            time.sleep(5)

    log("Bot detenido.", "INFO")
    state["status"] = "DETENIDO"
    memory.save()


def execute_trade(market_data, rm, signal, amount, learner, memory, evaluator):
    asset      = signal["asset"]
    direction  = signal["signal"]
    confidence = signal["confidence"]
    expiration = signal.get("expiration", 60)
    pattern    = signal.get("pattern", "")
    zone_str   = signal.get("zone_strength", 0.0)
    context    = signal.get("context", {})
    conditions = signal.get("conditions", {})
    zone_obj   = signal.get("zone_object")

    action_str = "call" if direction == "CALL" else "put"
    duration   = max(1, min(5, expiration // 60))

    exp_min   = signal.get("expiration_minutes", expiration // 60)
    exp_label = signal.get("expiration_label", "NORMAL")
    cplx      = signal.get("complexity_score", 50)
    log(f"ENTRANDO: {asset} {direction} ${amount:.2f} | {pattern} | zona={zone_str:.2f} | conf={confidence*100:.0f}% | {exp_min}min [{exp_label}] cplx={cplx:.0f}", "SIGNAL")
    state["status"] = "OPERANDO"
    state["last_trade_time"] = time.time()

    try:
        check, order_id = market_data.buy(asset, amount, action_str, duration)

        if check:
            log(f"Orden abierta: {direction} ${amount:.2f} exp={duration}min", "INFO")
            state["active_order"] = order_id
            time.sleep(expiration + 8)

            # Verificar resultado
            result, pnl = "DRAW", 0.0
            try:
                result_data = market_data.api.check_win_v4(order_id)
                if result_data is not None:
                    profit = float(result_data)
                    if profit > 0:
                        pnl, result = profit, "WIN"
                        log(f"WIN +${profit:.2f} | {asset} {direction}", "WIN")
                    elif profit < 0:
                        pnl, result = -amount, "LOSS"
                        log(f"LOSS -${amount:.2f} | {asset} {direction}", "LOSS")
                    else:
                        pnl, result = 0.0, "DRAW"
                        log(f"EMPATE | {asset} {direction}", "WARN")
                else:
                    pnl, result = -amount * 0.5, "LOSS"
                    log("Sin confirmación de resultado, asumiendo LOSS", "WARN")
            except Exception as e:
                log(f"Error verificando resultado: {e}", "WARN")
                pnl, result = 0.0, "DRAW"

            record_trade(asset, direction, amount, confidence, result, pnl, pattern, zone_str)
            rm.update_balance(state["balance"], {"profit": pnl})

            # ── Auto-evaluación y aprendizaje ──
            # Capturar velas DESPUÉS del trade para detectar entrada prematura
            df_after = None
            try:
                df_after = market_data.get_candles(asset, 60, 20)
            except Exception:
                pass

            trade_record = {
                "asset": asset, "direction": direction, "amount": amount,
                "confidence": confidence, "result": result, "pnl": pnl,
                "pattern": pattern, "order_id": str(order_id),
                "entry_price": signal.get("zone", 0.0) or amount,
                "expiration_minutes": signal.get("expiration_minutes", duration),
            }
            diagnosis = evaluator.evaluate(trade_record, context, conditions,
                                           df_m1_after=df_after)
            learner.learn_from_trade(conditions, result, diagnosis)
            state["last_diagnosis"] = evaluator.format_for_display(diagnosis)

            # Actualizar memoria de zona
            if zone_obj:
                reacted = (result == "WIN" and direction == "CALL" and zone_obj.zone_type == "support") or \
                          (result == "WIN" and direction == "PUT" and zone_obj.zone_type == "resistance")
                memory.add_or_update_zone(asset, zone_obj.level, zone_obj.zone_type, reacted)
                memory.save()

            # Log de aprendizaje
            if result == "LOSS" and diagnosis.get("lessons"):
                log(f"Aprendizaje: {diagnosis['lessons'][0]}", "LEARN")
            elif result == "WIN" and diagnosis.get("what_worked"):
                log(f"Confirmado: {diagnosis['what_worked'][0]}", "LEARN")

        else:
            log(f"Orden rechazada: {order_id}", "ERROR")

    except Exception as e:
        log(f"Error ejecutando trade: {e}", "ERROR")

    state["status"] = "ANALIZANDO"
    state["active_order"] = None


# ─── Entry point ─────────────────────────────────────────────────────────────

def signal_handler(sig, frame):
    state["running"] = False


def main():
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    console.clear()
    console.print(Panel.fit(
        "[bold cyan]EXNOVA ULTRA-SMART BOT v4.0[/bold cyan]\n"
        "[dim]Motor inteligente + Aprendizaje adaptativo + Memoria de zonas[/dim]",
        border_style="cyan"
    ))

    risk_config = RiskConfig(
        max_drawdown_daily=0.10,
        max_trades_per_hour=6,
        cooldown_after_loss_seconds=COOLDOWN_AFTER_LOSS,
        min_confidence_threshold=MIN_CONFIDENCE,
        stop_after_consecutive_losses=MAX_CONSEC_LOSSES,
    )
    rm = initialize_risk_manager(INITIAL_BALANCE, risk_config)
    market_data = MarketDataHandler(broker_name="exnova", account_type="PRACTICE")
    engine = IntelligentEngine()

    state["start_time"] = time.time()

    bot_thread = threading.Thread(
        target=bot_loop, args=(market_data, rm, engine), daemon=True
    )
    bot_thread.start()

    layout = build_layout()
    with Live(layout, console=console, refresh_per_second=2, screen=True):
        while state["running"] or state["status"] not in ("DETENIDO", "ERROR"):
            update_layout(layout)
            time.sleep(0.5)
        update_layout(layout)
        time.sleep(2)

    total = state["wins"] + state["losses"]
    wr = (state["wins"] / total * 100) if total > 0 else 0
    learner = get_adaptive_learner()
    console.print()
    console.print(Panel(
        f"[bold]Resumen Final[/bold]\n\n"
        f"  Trades: {total}  |  [green]{state['wins']}W[/green] / [red]{state['losses']}L[/red]\n"
        f"  Win Rate: [{'green' if wr>=60 else 'yellow'}]{wr:.1f}%[/]\n"
        f"  PnL: [{'green' if state['total_pnl']>=0 else 'red'}]{'+' if state['total_pnl']>=0 else ''}{state['total_pnl']:.2f}[/]\n"
        f"  Balance final: ${state['balance']:.2f}\n\n"
        f"  [dim]Sistema aprendió de {learner.total_trades} trades. WR aprendido: {learner.get_global_winrate():.1%}[/dim]",
        border_style="cyan", title="[bold cyan]BOT DETENIDO[/bold cyan]"
    ))


if __name__ == "__main__":
    main()
