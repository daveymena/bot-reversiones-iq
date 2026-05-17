# -*- coding: utf-8 -*-
"""
Ejecuta el bot Exnova en modo texto (stdout) para monitoreo desde consola.
"""
import sys, os, time, threading

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'bot'))

from dotenv import load_dotenv
load_dotenv()

from config import Config
from data.market_data import MarketDataHandler
from core.advanced_risk_manager import initialize_risk_manager, RiskConfig
from brain.adaptive_learner import get_adaptive_learner
from brain.market_memory import get_market_memory
from brain.trade_evaluator import TradeEvaluator
from brain.adaptive_learning_mode import get_learning_mode
from engine.intelligent_engine import IntelligentEngine

# ─── Constantes ─────────────────────────────────────────────────────────────
ASSETS = ["EURUSD-OTC", "GBPUSD-OTC", "AUDUSD-OTC", "EURJPY-OTC"]
INITIAL_BALANCE    = 10_000.0
MIN_CONFIDENCE     = 0.50
COOLDOWN_AFTER_LOSS = 30
MIN_BETWEEN_TRADES  = 45
MIN_BETWEEN_SAME_ASSET = 180
MAX_CONSEC_LOSSES   = 5
PAUSE_AFTER_WIN_STREAK = 3
PAUSE_DURATION = 120

# ─── Estado global ──────────────────────────────────────────────────────────
from collections import deque

state = {
    "running": True,
    "balance": 0.0, "initial_balance": 0.0,
    "wins": 0, "losses": 0, "total_pnl": 0.0,
    "trades": [],
    "cycle": 0, "start_time": time.time(),
    "last_trade_time": 0, "current_asset": "",
    "status": "INICIANDO", "active_order": None,
    "consecutive_losses": 0, "best_streak": 0, "current_streak": 0,
    "last_signal": {}, "last_diagnosis": [],
    "last_trade_by_asset": {}, "rejection_stats": {},
}

def log(msg, level="INFO"):
    now = time.strftime("%H:%M:%S")
    print(f"[{now}] [{level}] {msg}")

# ─── Trade execution ────────────────────────────────────────────────────────

def execute_trade(market_data, rm, signal, amount, learner, memory, evaluator):
    asset = signal["asset"]
    direction = signal["signal"]
    confidence = signal["confidence"]
    expiration = signal.get("expiration", 60)
    pattern = signal.get("pattern", "")
    zone_str = signal.get("zone_strength", 0.0)
    context = signal.get("context", {})
    conditions = signal.get("conditions", {})
    zone_obj = signal.get("zone_object")

    action_str = "call" if direction == "CALL" else "put"
    duration = max(1, min(5, expiration // 60))
    exp_min = signal.get("expiration_minutes", duration)

    log(f"ENTRANDO: {asset} {direction} ${amount:.2f} | {pattern} | zona={zone_str:.2f} | conf={confidence*100:.0f}% | {exp_min}min")
    state["status"] = "OPERANDO"
    state["last_trade_time"] = time.time()

    try:
        check, order_id = market_data.buy(asset, amount, action_str, duration)
        if check:
            log(f"Orden abierta: {direction} ${amount:.2f} exp={duration}min")
            state["active_order"] = order_id
            time.sleep(expiration + 8)

            result, pnl = "DRAW", 0.0
            try:
                result_data = market_data.api.check_win_v4(order_id)
                if result_data is not None:
                    if isinstance(result_data, tuple):
                        _, profit = result_data
                        profit = float(profit) if profit is not None else 0.0
                    elif isinstance(result_data, (int, float)):
                        profit = float(result_data)
                    else:
                        profit = 0.0

                    if profit > 0:
                        pnl, result = profit, "WIN"
                        log(f"WIN +${profit:.2f} | {asset} {direction} | patron={pattern} zona={zone_str:.2f}")
                    elif profit < 0:
                        pnl, result = -amount, "LOSS"
                        log(f"LOSS -${amount:.2f} | {asset} {direction} | patron={pattern} zona={zone_str:.2f}")
                    else:
                        log(f"DRAW | {asset} {direction}")
                else:
                    pnl, result = -amount * 0.5, "LOSS"
                    log("Sin confirmacion, asumiendo LOSS")
            except Exception as e:
                log(f"Error verificando resultado: {e}")
                pnl, result = 0.0, "DRAW"

            # Record trade
            state["trades"].append({
                "time": time.strftime("%H:%M:%S"), "asset": asset,
                "direction": direction, "amount": amount,
                "confidence": confidence, "result": result, "pnl": pnl,
                "pattern": pattern, "zone_strength": zone_str,
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
            rm.update_balance(state["balance"], {"profit": pnl})

            learning_mode = get_learning_mode()
            learning_mode.record_trade()

            # Post-trade analysis
            df_after = None
            try:
                df_after = market_data.get_candles(asset, 60, 20)
            except:
                pass

            trade_record = {
                "asset": asset, "direction": direction, "amount": amount,
                "confidence": confidence, "result": result, "pnl": pnl,
                "pattern": pattern, "order_id": str(order_id),
                "entry_price": signal.get("zone", 0.0) or amount,
                "expiration_minutes": signal.get("expiration_minutes", duration),
            }
            diagnosis = evaluator.evaluate(trade_record, context, conditions, df_m1_after=df_after)
            learner.learn_from_trade(conditions, result, diagnosis)
            state["last_diagnosis"] = evaluator.format_for_display(diagnosis)

            if result == "LOSS":
                cause = diagnosis.get("primary_cause", "unknown")
                log(f"[ANALISIS] Perdida por: {cause} | {diagnosis.get('lessons', ['-'])[0]}")
            elif result == "WIN":
                good = diagnosis.get("what_worked", ["-"])[0]
                log(f"[ANALISIS] Ganancia por: {good}")

            if zone_obj:
                reacted = (result == "WIN" and direction == "CALL" and zone_obj.zone_type == "support") or \
                          (result == "WIN" and direction == "PUT" and zone_obj.zone_type == "resistance")
                memory.add_or_update_zone(asset, zone_obj.level, zone_obj.zone_type, reacted)
                memory.save()

            state["status"] = "ANALIZANDO"
            state["active_order"] = None
            return True
        else:
            log(f"Orden rechazada: {order_id}")
            state["status"] = "ANALIZANDO"
            state["active_order"] = None
            return False
    except Exception as e:
        log(f"Error ejecutando trade: {e}")
        state["status"] = "ANALIZANDO"
        state["active_order"] = None
        return False

# ─── Bucle principal ────────────────────────────────────────────────────────

def bot_loop(market_data, rm, engine):
    email = os.getenv("EXNOVA_EMAIL", "")
    password = os.getenv("EXNOVA_PASSWORD", "")
    learner = get_adaptive_learner()
    memory = get_market_memory()
    evaluator = TradeEvaluator()

    log("Conectando a Exnova PRACTICE...")
    state["status"] = "CONECTANDO"
    if not market_data.connect(email, password):
        log("ERROR: No se pudo conectar.")
        state["status"] = "ERROR"
        return

    try:
        balance = market_data.get_balance()
        balance = float(balance) if balance and float(balance) > 0 else INITIAL_BALANCE
    except:
        balance = INITIAL_BALANCE

    state["balance"] = balance
    state["initial_balance"] = balance
    rm.initialize(balance)
    log(f"Conectado. Balance: ${balance:,.2f}")
    log(f"Aprendizaje: {learner.summary()}")
    state["status"] = "ANALIZANDO"

    asset_idx = 0
    last_reconnect = time.time()
    day_trades = 0

    print(f"\n{'='*60}")
    print(f"BOT OPERATIVO - Monitoreando {len(ASSETS)} activos")
    print(f"{'='*60}\n")

    while state["running"]:
        try:
            state["cycle"] += 1
            now = time.time()

            # Reconexion
            if now - last_reconnect > 240:
                if not market_data.is_really_connected():
                    log("Reconectando...")
                    market_data.reconnect(email, password)
                last_reconnect = now

            # Cooldown por perdidas
            if state["consecutive_losses"] >= MAX_CONSEC_LOSSES:
                state["status"] = "PAUSA_RIESGO"
                log(f"PAUSA: {state['consecutive_losses']} perdidas seguidas. 5min.")
                time.sleep(300)
                state["consecutive_losses"] = 0
                continue

            # Pausa post-racha
            if state["current_streak"] >= PAUSE_AFTER_WIN_STREAK:
                state["status"] = "PAUSA_WIN_STREAK"
                log(f"Pausa post-racha: {state['current_streak']} wins. {PAUSE_DURATION}s.")
                time.sleep(PAUSE_DURATION)
                state["current_streak"] = 0
                continue

            # Rotar activos
            asset = ASSETS[asset_idx % len(ASSETS)]
            asset_idx += 1
            state["current_asset"] = asset

            # Analizar
            signal = engine.analyze(asset, market_data)

            if signal:
                state["last_signal"] = signal
                action = signal.get("action", "WAIT")
                confidence = signal.get("confidence", 0)
                score = signal.get("score", 0)

                if action == "TRADE" and confidence >= MIN_CONFIDENCE:
                    time_since = now - state["last_trade_time"]
                    learning_mode = get_learning_mode()
                    cooldown_mult = learning_mode.get_cooldown_multiplier()
                    cooldown_needed = int((COOLDOWN_AFTER_LOSS if state["consecutive_losses"] > 0 else MIN_BETWEEN_TRADES) * cooldown_mult)
                    last_asset = state["last_trade_by_asset"].get(asset, 0)
                    
                    if time_since < cooldown_needed:
                        pass  # silent cooldown
                    elif (now - last_asset) < MIN_BETWEEN_SAME_ASSET:
                        pass
                    elif rm.is_stopped:
                        log(f"RM activo: {rm.stop_reason}")
                    else:
                        amount = rm.calculate_position_size(confidence=confidence)
                        if amount > 0:
                            executed = execute_trade(market_data, rm, signal, amount, learner, memory, evaluator)
                            if executed:
                                day_trades += 1
                                state["last_trade_by_asset"][asset] = time.time()
                        else:
                            log(f"RM: amount=0 (conf={confidence:.2f})")
                elif action == "WAIT":
                    reason = signal.get("reason", "")
                    if reason and "zona" in reason.lower():
                        log(f"{asset} | {reason}")

            # Status periodico
            if state["cycle"] % 10 == 0:
                total = state["wins"] + state["losses"]
                wr = (state["wins"] / total * 100) if total > 0 else 0
                elapsed = int(time.time() - state["start_time"])
                sig = state.get("last_signal", {})
                print(f"[{elapsed}s] #{state['cycle']} {asset} | "
                      f"Trades:{total} W/L:{state['wins']}/{state['losses']} WR:{wr:.1f}% "
                      f"PnL:${state['total_pnl']:.2f} Bal:${state['balance']:.2f} | "
                      f"{state['status']}")
                if sig and sig.get('action') == 'TRADE':
                    print(f"  -> {sig['signal']} Score={sig.get('score',0):.0f} Conf={sig.get('confidence',0):.2f} "
                          f"Patron={sig.get('pattern','?')} IA={sig.get('ai_label','?')}")

            time.sleep(6)

        except KeyboardInterrupt:
            state["running"] = False
            break
        except Exception as e:
            log(f"Error en loop: {e}")
            time.sleep(5)

    log("Bot detenido.")
    state["status"] = "DETENIDO"
    memory.save()

# ─── Entry point ────────────────────────────────────────────────────────────

def main():
    risk_config = RiskConfig(
        max_drawdown_daily=0.10, max_trades_per_hour=6,
        cooldown_after_loss_seconds=COOLDOWN_AFTER_LOSS,
        min_confidence_threshold=MIN_CONFIDENCE,
        stop_after_consecutive_losses=MAX_CONSEC_LOSSES,
    )
    rm = initialize_risk_manager(INITIAL_BALANCE, risk_config)
    market_data = MarketDataHandler(broker_name="exnova", account_type="PRACTICE")
    engine = IntelligentEngine()
    state["start_time"] = time.time()

    bot_loop(market_data, rm, engine)

    # Resumen final
    total = state["wins"] + state["losses"]
    wr = (state["wins"] / total * 100) if total > 0 else 0
    print(f"\n{'='*60}")
    print(f"RESUMEN FINAL")
    print(f"{'='*60}")
    print(f"Duracion: {int(time.time() - state['start_time'])}s")
    print(f"Trades: {total} | W: {state['wins']} L: {state['losses']}")
    print(f"Win Rate: {wr:.1f}%")
    print(f"PnL: ${state['total_pnl']:.2f}")
    print(f"Balance: ${state['balance']:.2f}")
    print(f"Mejor racha: +{state['best_streak']}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
