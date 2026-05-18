"""
Intelligent Engine v4.1 — Motor con timing de entrada preciso
El error previo: detectaba patrones en velas ABIERTAS (aún formándose).
Fix: solo opera sobre velas CERRADAS + valida que la vela actual confirme el movimiento.
"""
import time
import numpy as np
import pandas as pd
from typing import Dict, Optional, List, Tuple

from brain.market_memory import get_market_memory
from brain.zone_detector import ZoneDetector
from brain.context_analyzer import ContextAnalyzer
from brain.adaptive_learner import get_adaptive_learner
from brain.market_ai import MarketAI
from brain.market_session import get_market_session
from brain.zone_reaction_history import get_zone_history


# ─── Diagnóstico de entrada prematura ────────────────────────────────────────

class PrematureEntryDiagnostic:
    """
    Analiza si una pérdida fue por entrada prematura:
    el precio eventualmente llegó al objetivo pero después de que la operación expiró.
    """
    @staticmethod
    def was_premature(entry_price: float, direction: str,
                       candles_after: pd.DataFrame, expiration_minutes: int) -> Dict:
        if candles_after is None or len(candles_after) < 2:
            return {"premature": False, "reason": "sin datos post-trade"}

        target_reached_at = None
        candles_checked = min(len(candles_after), expiration_minutes * 3)

        for i, (_, row) in enumerate(candles_after.head(candles_checked).iterrows()):
            if direction == "CALL":
                if float(row["high"]) > entry_price * 1.0003:
                    target_reached_at = i + 1
                    break
            else:
                if float(row["low"]) < entry_price * 0.9997:
                    target_reached_at = i + 1
                    break

        # Buscar cuánto tardó el precio en llegar al objetivo
        target_reached_late = None
        for i, (_, row) in enumerate(candles_after.iterrows()):
            if direction == "CALL":
                if float(row["high"]) > entry_price * 1.0003:
                    target_reached_late = i + 1
                    break
            else:
                if float(row["low"]) < entry_price * 0.9997:
                    target_reached_late = i + 1
                    break

        was_premature = (target_reached_at is None and target_reached_late is not None and
                          target_reached_late > expiration_minutes)

        return {
            "premature": was_premature,
            "target_reached_candle": target_reached_late,
            "expiration_candles": expiration_minutes,
            "diagnosis": (
                f"Entrada prematura: precio llegó al objetivo en vela {target_reached_late} "
                f"pero la operación expiró en {expiration_minutes} velas"
                if was_premature else
                "No fue entrada prematura"
            ),
        }


# ─── Detector de patrones en velas CERRADAS ──────────────────────────────────

class CandlePatternDetector:
    """
    Detecta patrones SOLO en velas completamente cerradas.

    Regla fundamental:
    - La vela de señal siempre es df.iloc[-2] (última CERRADA)
    - La vela actual df.iloc[-1] (en formación) solo se usa para confirmar
      que el movimiento ya inició
    - Nunca se entra basándose en la vela actual abierta
    """

    def detect(self, df: pd.DataFrame, expected_direction: str) -> Dict:
        if len(df) < 5:
            return self._no_pattern("Datos insuficientes")

        # ── Velas de referencia (todas CERRADAS) ──────────────────────────────
        anchor = df.iloc[-5]   # vela -5 (contexto)
        c3     = df.iloc[-4]   # vela -4
        c2     = df.iloc[-3]   # vela -3
        signal = df.iloc[-2]   # VELA DE SEÑAL (última cerrada) ← aquí se detecta el patrón
        current = df.iloc[-1]  # vela actual (solo para confirmar dirección inicial)

        # Datos de la vela de señal (cerrada)
        o  = float(signal["open"])
        h  = float(signal["high"])
        l  = float(signal["low"])
        c  = float(signal["close"])

        body       = abs(c - o)
        full_range = h - l if h > l else 1e-8
        upper_wick = h - max(o, c)
        lower_wick = min(o, c) - l
        is_bull    = c > o
        is_bear    = c < o

        # Datos velas anteriores
        o2, c2v = float(c2["open"]), float(c2["close"])
        o3, c3v = float(c3["open"]), float(c3["close"])
        oa, ca  = float(anchor["open"]), float(anchor["close"])

        # Vela actual (en formación) — solo para confirmar
        cur_o   = float(current["open"])
        cur_c   = float(current["close"])
        cur_moving_up   = cur_c > cur_o
        cur_moving_down = cur_c < cur_o

        patterns = []

        # ── Pin Bar (mecha dominante = rechazo fuerte) ───────────────────────
        if full_range > 0:
            # Pin bar alcista: mecha inferior ≥60% del rango, cuerpo ≤30%
            if lower_wick / full_range >= 0.60 and body / full_range <= 0.30:
                # La mecha debe ser al menos 2x el cuerpo
                if lower_wick >= body * 1.8 or body < full_range * 0.15:
                    strength = 0.82 + min(lower_wick / full_range - 0.60, 0.15)
                    patterns.append(("pin_bar_bullish", round(strength, 2)))

            # Pin bar bajista: mecha superior ≥60% del rango, cuerpo ≤30%
            if upper_wick / full_range >= 0.60 and body / full_range <= 0.30:
                if upper_wick >= body * 1.8 or body < full_range * 0.15:
                    strength = 0.82 + min(upper_wick / full_range - 0.60, 0.15)
                    patterns.append(("pin_bar_bearish", round(strength, 2)))

        # ── Hammer / Shooting Star ───────────────────────────────────────────
        if body > 0:
            if lower_wick >= body * 2.2 and upper_wick <= body * 0.4:
                patterns.append(("hammer", 0.78))
            if upper_wick >= body * 2.2 and lower_wick <= body * 0.4:
                patterns.append(("shooting_star", 0.78))

        # ── Engulfing fuerte ─────────────────────────────────────────────────
        # Alcista: vela signal es bull Y envuelve completamente a c2 (bearish)
        if is_bull and c2v < o2:  # c2 fue bajista
            if c > o2 and o <= c2v:  # envuelve completamente
                body_ratio = body / max(abs(c2v - o2), 1e-8)
                if body_ratio >= 1.1:
                    patterns.append(("bullish_engulfing", 0.83 + min(body_ratio - 1.1, 0.10)))
        # Bajista: vela signal es bear Y envuelve completamente a c2 (bullish)
        if is_bear and c2v > o2:  # c2 fue alcista
            if c < o2 and o >= c2v:
                body_ratio = body / max(abs(c2v - o2), 1e-8)
                if body_ratio >= 1.1:
                    patterns.append(("bearish_engulfing", 0.83 + min(body_ratio - 1.1, 0.10)))

        # ── Morning Star / Evening Star (3 velas cerradas) ───────────────────
        # Morning Star: c3 bearish grande → c2 pequeña → signal bullish
        c3_bear  = c3v < o3 and abs(c3v - o3) > full_range * 0.5
        c2_small = abs(c2v - o2) < abs(c3v - o3) * 0.35
        sig_bull = is_bull and c > (o3 + c3v) / 2
        if c3_bear and c2_small and sig_bull:
            patterns.append(("morning_star", 0.92))

        # Evening Star: c3 bullish grande → c2 pequeña → signal bearish
        c3_bull  = c3v > o3 and abs(c3v - o3) > full_range * 0.5
        sig_bear = is_bear and c < (o3 + c3v) / 2
        if c3_bull and c2_small and sig_bear:
            patterns.append(("evening_star", 0.92))

        # ── Doji de reversión (señal ambigua, solo si muy extremo) ───────────
        if full_range > 0 and body / full_range <= 0.10:
            if expected_direction == "CALL" and lower_wick / full_range >= 0.40:
                patterns.append(("doji_reversal_bull", 0.62))
            elif expected_direction == "PUT" and upper_wick / full_range >= 0.40:
                patterns.append(("doji_reversal_bear", 0.62))

        if not patterns:
            return self._no_pattern("Sin patrón en vela cerrada", signal_candle_info={
                "body_pct": body / full_range if full_range > 0 else 0,
                "lower_wick_pct": lower_wick / full_range if full_range > 0 else 0,
                "upper_wick_pct": upper_wick / full_range if full_range > 0 else 0,
            })

        # ── Filtrar por dirección esperada ────────────────────────────────────
        bullish_patterns = {"pin_bar_bullish", "hammer", "bullish_engulfing",
                            "doji_reversal_bull", "morning_star"}
        bearish_patterns = {"pin_bar_bearish", "shooting_star", "bearish_engulfing",
                            "doji_reversal_bear", "evening_star"}

        if expected_direction == "CALL":
            valid = [(p, s) for p, s in patterns if p in bullish_patterns]
        elif expected_direction == "PUT":
            valid = [(p, s) for p, s in patterns if p in bearish_patterns]
        else:
            valid = patterns

        if not valid:
            return self._no_pattern(
                f"Patrón detectado ({[p for p,_ in patterns]}) no coincide con dirección {expected_direction}",
                all_detected=[p for p, _ in patterns]
            )

        best_pattern, best_strength = max(valid, key=lambda x: x[1])

        # ── Confirmación por la vela actual ───────────────────────────────────
        # La vela actual (abierta) debe estar comenzando a moverse en la dirección correcta
        # Si va en contra, el patrón aún no está confirmado por el mercado
        candle_confirming = (
            (expected_direction == "CALL" and (cur_c >= cur_o or cur_c > c)) or
            (expected_direction == "PUT"  and (cur_c <= cur_o or cur_c < c))
        )

        # Para patrones fuertes, la confirmación de vela actual es opcional
        # Para patrones débiles (doji), es obligatoria
        requires_current_confirmation = best_strength < 0.75
        if requires_current_confirmation and not candle_confirming:
            return self._no_pattern(
                f"Patrón {best_pattern} detectado en vela cerrada pero vela actual no confirma — esperando",
                all_detected=[p for p, _ in patterns],
                waiting_confirmation=True,
            )

        conditions = {
            f"pattern_{best_pattern.split('_')[0]}": True,
            "pattern_strong": best_strength >= 0.80,
        }

        return {
            "pattern": best_pattern,
            "confirmed": True,
            "strength": min(best_strength, 0.97),
            "all_detected": [p for p, _ in patterns],
            "conditions": conditions,
            "candle_confirmed": candle_confirming,
            "used_closed_candle": True,   # garantía de que no es prematura
        }

    @staticmethod
    def _no_pattern(reason: str, all_detected: list = None,
                    signal_candle_info: dict = None,
                    waiting_confirmation: bool = False) -> Dict:
        return {
            "pattern": "none",
            "confirmed": False,
            "strength": 0.0,
            "conditions": {},
            "reason": reason,
            "all_detected": all_detected or [],
            "waiting_confirmation": waiting_confirmation,
            "signal_candle_info": signal_candle_info or {},
        }


# ─── Validador de timing de entrada ──────────────────────────────────────────

class EntryTimingValidator:
    """
    Valida que el momento de entrada sea preciso:
    - El precio debe estar DENTRO de la zona (no aproximándose)
    - El rechazo debe ser evidente en el histórico de velas
    - No debe haber ya comenzado el movimiento (entrada tardía)
    """

    def validate(self, df_m1: pd.DataFrame, zone_level: float,
                  zone_type: str, direction: str,
                  zone_distance_pct: float = 0.0) -> Dict:
        if len(df_m1) < 6:
            return {"valid": True, "reason": "datos insuficientes para validar"}

        # ── 1. Verificar que la vela de señal tocó la zona ───────────────────
        signal_candle = df_m1.iloc[-2]  # última cerrada
        s_low  = float(signal_candle["low"])
        s_high = float(signal_candle["high"])
        s_close = float(signal_candle["close"])
        # Tolerancia adaptativa: más amplia si la zona está lejos
        tol_pct = min(0.0008 + zone_distance_pct * 0.3, 0.005)
        tol = zone_level * tol_pct

        zone_was_touched = (
            (zone_type == "support"    and s_low   <= zone_level + tol) or
            (zone_type == "resistance" and s_high  >= zone_level - tol) or
            abs(s_close - zone_level) <= tol * 2
        )

        if not zone_was_touched:
            return {
                "valid": False,
                "reason": f"La vela de señal no tocó la zona {zone_level:.5f} (low={s_low:.5f}, high={s_high:.5f})",
                "issue": "zone_not_touched",
            }

        # ── 2. Verificar que no empezó ya el movimiento ───────────────────────
        # Si la zona está lejos, permitir más distancia
        current_close = float(df_m1.iloc[-1]["close"])
        distance_from_zone = abs(current_close - zone_level) / zone_level
        max_allowed = 0.0020 + zone_distance_pct * 1.5

        if distance_from_zone > max_allowed:
            return {
                "valid": False,
                "reason": f"El movimiento ya comenzó — precio alejado {distance_from_zone*100:.2f}% de la zona (entrada tardía)",
                "issue": "late_entry",
            }

        # ── 3. Verificar rechazo real en la zona (no solo rozó) ──────────────
        # La mecha de rechazo debe ser visible
        body     = abs(float(signal_candle["close"]) - float(signal_candle["open"]))
        rng      = float(signal_candle["high"]) - float(signal_candle["low"])
        wick_pct = 0.0
        if rng > 0:
            if zone_type == "support":
                lower_wick = float(signal_candle["low"])
                lower_wick = min(float(signal_candle["open"]), float(signal_candle["close"])) - lower_wick
                wick_pct = lower_wick / rng
            else:
                upper_wick = float(signal_candle["high"])
                upper_wick -= max(float(signal_candle["open"]), float(signal_candle["close"]))
                wick_pct = upper_wick / rng

        if wick_pct < 0.20:
            return {
                "valid": False,
                "reason": f"Sin rechazo visible en la zona (mecha={wick_pct:.1%}, necesita ≥20%)",
                "issue": "no_rejection_wick",
            }

        return {
            "valid": True,
            "reason": "Timing válido — vela cerrada tocó zona con rechazo visible",
            "zone_touched": zone_was_touched,
            "rejection_wick_pct": wick_pct,
            "distance_from_zone": distance_from_zone,
        }


# ─── Motor principal ──────────────────────────────────────────────────────────

class IntelligentEngine:
    """
    Motor de inteligencia v4.1 — Timing de entrada preciso.

    Flujo corregido:
    1. Descargar gráfico completo (H1 + M15 + M5 + M1)
    2. Detectar zonas desde histórico
    3. Verificar que precio está EN zona fuerte (tolerancia ≤0.1%)
    4. Detectar patrón SOLO en vela cerrada (df.iloc[-2])
    5. Validar timing: zona realmente tocada + rechazo visible + no entrada tardía
    6. Analizar contexto completo
    7. Puntuar con pesos adaptativos
    8. Decidir — si pasa todos los filtros, entrar
    """

    def __init__(self):
        self.memory           = get_market_memory()
        self.zone_detector    = ZoneDetector()
        self.context_analyzer = ContextAnalyzer()
        self.learner          = get_adaptive_learner()
        self.pattern_detector = CandlePatternDetector()
        self.timing_validator = EntryTimingValidator()
        self.market_ai        = MarketAI()
        self.session          = get_market_session()
        self.zone_history     = get_zone_history()
        self._last_zone_scan: Dict[str, float] = {}
        self._zone_scan_interval = 300
        self._start_time = time.time()
        self._warmup_seconds = 90  # 90s de observación antes de operar

    def analyze(self, asset: str, market_data, fe=None) -> Optional[Dict]:
        try:
            # ── 0. Warm-up — no operar inmediatamente al arrancar ────────────
            if time.time() - self._start_time < self._warmup_seconds:
                remaining = int(self._warmup_seconds - (time.time() - self._start_time))
                return self._wait(f"Warm-up: observando mercado {remaining}s más", asset)

            # ── 1. Datos multi-timeframe ─────────────────────────────────────
            df_m1 = market_data.get_candles(asset, 60, 200)
            if df_m1 is None or len(df_m1) < 30:
                return self._wait("Datos M1 insuficientes", asset)

            df_m5  = market_data.get_candles(asset, 300, 120)
            df_m15 = market_data.get_candles(asset, 900, 60)
            df_h1  = market_data.get_candles(asset, 3600, 30)

            if df_m5 is None or len(df_m5) < 20:
                return self._wait("Datos M5 insuficientes", asset)

            # Precio de referencia = cierre de la última vela CERRADA
            current_price = float(df_m1.iloc[-2]["close"])
            if current_price <= 0:
                return self._wait("Precio inválido", asset)

            # ── 2. Escanear zonas ────────────────────────────────────────────
            last_scan = self._last_zone_scan.get(asset, 0)
            if time.time() - last_scan > self._zone_scan_interval:
                self._rescan_zones(asset, df_m5, df_m15, df_h1)
                self._last_zone_scan[asset] = time.time()

            # ── 3. Sesión de mercado — adaptar parámetros al horario actual ──
            session_name, session_params = self.session.get_current_session()
            # ATR para detectar volatilidad real
            atr_pct = self._calc_atr_pct(df_m1)
            session_name, session_params = self.session.get_adaptive_params(0.50, atr_pct)
            # Tolerancia dinámica según ATR, limitada a 0.25%
            atr_based_tolerance = min(atr_pct * 2.0, 0.0025)
            config_tolerance = session_params.get("zone_tolerance", 0.0020)
            zone_tolerance = max(atr_based_tolerance, min(config_tolerance, 0.0025))
            min_zone_strength = max(
                self.learner.get_threshold("min_zone_strength", 0.35),
                session_params.get("min_zone_strength", 0.35)
            )

            # ── 4. ¿Está el precio EN una zona fuerte? ───────────────────────
            soft_penalties = 0.0
            nearest_zone = self.memory.get_nearest_strong_zone(
                asset, current_price, tolerance_pct=zone_tolerance
            )
            zone_context_summary = self.memory.get_zone_context(asset, current_price)

            if nearest_zone is None or nearest_zone.strength < min_zone_strength:
                # ¿Hay zona aunque esté lejos (hasta 1.2%)? Si sí, permitir con penalización
                wide_zone = self.memory.get_nearest_strong_zone(asset, current_price, tolerance_pct=0.012)
                if wide_zone and wide_zone.strength >= min_zone_strength * 0.85:
                    nearest_zone = wide_zone
                    soft_penalties += 0.10  # penalizar por zona lejana
                else:
                    any_zone = self.memory.get_nearest_strong_zone(asset, current_price, tolerance_pct=0.01)
                    dist_str = ""
                    if any_zone:
                        dist_pct = abs(any_zone.level - current_price) / current_price * 100
                        dist_str = f" | Zona más cercana: {any_zone.level:.5f} a {dist_pct:.2f}%"
                    return {
                        "asset": asset, "action": "WAIT", "signal": "NEUTRAL",
                        "score": 0.0, "confidence": 0.0,
                        "reason": f"[{session_name}] Precio lejos de zona{dist_str}",
                        "phase": "buscando_zona",
                        "zone_count": len(self.memory.get_all_zones(asset)),
                        "zone_context": zone_context_summary,
                        "session": session_name,
                    }

            # ── 4. Analizar contexto completo ────────────────────────────────
            context = self.context_analyzer.analyze(
                df_m1, df_m5,
                df_m15 if df_m15 is not None and len(df_m15) >= 10 else df_m5,
                df_h1 if df_h1 is not None and len(df_h1) >= 5 else None,
                zone=nearest_zone,
                current_price=current_price,
            )
            expected_dir = context.get("expected_direction", "NEUTRAL")
            phase = context.get("market_phase", "unknown")

            if phase == "dead":
                return self._wait(f"[{session_name}] Mercado muerto — sin volatilidad", asset, context=context)

            # ── REGLA IRROMPIBLE: La zona manda la dirección ─────────────────
            # Soporte → solo CALL. Resistencia → solo PUT. Sin excepciones.
            zone_mandated_dir = "CALL" if nearest_zone.zone_type == "support" else "PUT"
            # Si el contexto dice lo contrario, advertir pero respetar la zona
            if expected_dir != "NEUTRAL" and expected_dir != zone_mandated_dir:
                # Contexto contradice la zona — solo operar si la zona es muy fuerte
                if nearest_zone.strength < 0.75:
                    return self._wait(
                        f"Zona {nearest_zone.zone_type} dice {zone_mandated_dir} "
                        f"pero contexto dice {expected_dir} — zona no suficientemente fuerte para contra-señal",
                        asset, context=context
                    )
            expected_dir = zone_mandated_dir

            # ── 4b. FILTRO DE TENDENCIA UNÁNIME — no operar contra tendencia fuerte ──
            # Si todos los TFs (M1, M5, M15, H1) muestran la misma tendencia,
            # es señal de que la tendencia es demasiado fuerte para operar en contra.
            tf_list = [
                context.get("structure_m1", {}).get("trend", "neutral"),
                context.get("structure_m5", {}).get("trend", "neutral"),
                context.get("structure_m15", {}).get("trend", "neutral"),
                context.get("structure_h1", {}).get("trend", "neutral"),
            ]
            unanimous_trend = None
            for t_dir in ("uptrend", "downtrend"):
                aligned = [t for t in tf_list if t == t_dir]
                against = [t for t in tf_list if t == ("downtrend" if t_dir == "uptrend" else "uptrend")]
                if len(aligned) >= 3 and len(against) == 0:
                    unanimous_trend = t_dir
                    break

            if unanimous_trend:
                going_against = (unanimous_trend == "uptrend" and expected_dir == "PUT") or \
                               (unanimous_trend == "downtrend" and expected_dir == "CALL")
                if going_against:
                    # No bloquear, solo penalizar fuerte (0.20 al score) + log
                    soft_penalties += 0.12

            # ── 4c. FILTRO POR SESIÓN: Bloqueo direccional ───────────────────
            if session_params.get("block_bullish_patterns", False) and expected_dir == "CALL":
                return self._wait(
                    f"[{session_name}] Operaciones CALL bloqueadas por bajo rendimiento histórico",
                    asset, context=context
                )

            # ── 5. Detectar patrón en vela CERRADA (df.iloc[-2]) ────────────
            pattern = self.pattern_detector.detect(df_m1, expected_dir)

            # ── 6. Validar timing — BLOQUEANTE ───────────────────────────────
            # Sin rechazo visible en la zona = no entrar. Sin excepciones.
            zone_dist_pct = abs(current_price - nearest_zone.level) / nearest_zone.level
            timing = self.timing_validator.validate(
                df_m1, nearest_zone.level, nearest_zone.zone_type,
                expected_dir, zone_distance_pct=zone_dist_pct
            )
            if not timing["valid"]:
                issue = timing.get("issue", "")
                reason = timing.get("reason", "Timing inválido")
                # Registrar por qué se rechazó para el dashboard
                return self._wait(f"Timing: {reason[:70]}", asset, context=context)

            # ── 6b. Patrón requerido — con fallback a micro-estructura o timing ──
            if not pattern.get("confirmed", False):
                # Si no hay patrón clásico: ¿hay micro-estructura + timing válido?
                micro = self._check_micro_structure(df_m1, expected_dir)
                zone_str_check = nearest_zone.strength if nearest_zone else 0
                rsi_check = context.get("momentum", {}).get("rsi_m1", 50)
                rsi_ok = rsi_check < 30 or rsi_check > 70
                if micro and zone_str_check >= max(0.55, min_zone_strength * 0.85):
                    # micro-estructura aceptable con zona decente
                    pattern = {
                        "pattern": "micro_structure",
                        "confirmed": True,
                        "strength": 0.55,
                        "conditions": {},
                        "candle_confirmed": True,
                    }
                elif timing.get("rejection_wick_pct", 0) >= 0.20:
                    # Sin patrón clásico ni micro, pero el timing muestra rechazo real
                    pattern = {
                        "pattern": "zone_rejection",
                        "confirmed": True,
                        "strength": 0.50,
                        "conditions": {},
                        "candle_confirmed": True,
                    }
                else:
                    return self._wait(
                        "Sin patrón de reversión en vela cerrada",
                        asset, context=context
                    )
            # Rechazar patrones muy débiles
            if pattern.get("strength", 0) < 0.50:
                return self._wait(
                    f"Patrón débil ({pattern.get('strength',0):.2f})",
                    asset, context=context
                )

            # ── 7. Condiciones para AdaptiveLearner ──────────────────────────
            zone_ctx  = context.get("zone_context", {})
            momentum  = context.get("momentum", {})
            rsi       = momentum.get("rsi_m1", 50)
            rsi_dist  = abs(rsi - 50)
            pattern_name = pattern.get("pattern", "")
            has_pattern  = pattern.get("confirmed", False)

            mtf_aligned = self._check_mtf_alignment(context, expected_dir if expected_dir != "NEUTRAL" else "CALL")

            conditions = {
                # Zona
                "zone_strength_high":   nearest_zone.strength >= 0.70,
                "zone_strength_medium": 0.45 <= nearest_zone.strength < 0.70,
                "zone_multi_tf":        nearest_zone.touches >= 3,
                "zone_touch_3plus":     nearest_zone.touches >= 2,
                "zone_hold_rate_high":  nearest_zone.hold_rate >= 0.60,
                # Tendencia
                "trend_aligned":   zone_ctx.get("trend_aligned", False),
                "trend_strong":    context.get("dominant_trend") in ("uptrend", "downtrend"),
                "counter_trend":   not zone_ctx.get("trend_aligned", True),
                # RSI
                "rsi_extreme":       rsi < 28 or rsi > 72,
                "rsi_oversold_sold": rsi < 38 and expected_dir == "CALL",
                "rsi_overbought":    rsi > 62 and expected_dir == "PUT",
                "rsi_divergence":    (momentum.get("bullish_divergence") or
                                      momentum.get("bearish_divergence", False)),
                # Patrones (detectados en vela CERRADA)
                "pattern_pin_bar":       "pin_bar"   in pattern_name,
                "pattern_engulfing":     "engulfing"  in pattern_name,
                "pattern_hammer":        pattern_name in ("hammer", "shooting_star"),
                "pattern_doji_reversal": "doji"       in pattern_name,
                "pattern_morning_star":  "star"       in pattern_name,
                "pattern_strong":        pattern.get("strength", 0) >= 0.75,
                "has_any_pattern":       has_pattern,
                # MACD
                "macd_cross":        abs(momentum.get("macd_hist", 0)) > 1e-5,
                "macd_hist_turning": momentum.get("macd_turning", False),
                # Contexto y timing
                "approach_clean":   context.get("before_context", {}).get("approach", "") in
                                    ("falling_to_support", "rising_to_resistance"),
                "mtf_aligned":      mtf_aligned,
                "market_phase_ranging":  phase == "ranging",
                "market_phase_trending": phase in ("trending_up", "trending_down"),
                "setup_quality_high":    context.get("setup_quality", 0) >= 0.55,
                "rejection_visible":     timing.get("rejection_wick_pct", 0) >= 0.20,
                "candle_confirming":     pattern.get("candle_confirmed", False),
            }

            # ── 8. Historial de zona + análisis de primera visita ────────────
            zone_history_analysis = self.zone_history.get_zone_analysis(
                asset, nearest_zone.level, nearest_zone.zone_type, session_name
            )
            is_first_visit = self.zone_history.is_first_visit(
                asset, nearest_zone.level, nearest_zone.zone_type
            )
            # Si la zona rompió la última vez, ser más cauteloso
            if zone_history_analysis.get("last_broke", False):
                if nearest_zone.strength < 0.80:
                    return self._wait(
                        f"Zona rompió en último toque — esperando confirmación de recuperación",
                        asset, context=context
                    )

            # ── 8b. MarketAI — análisis inteligente holístico ─────────────────
            # IMPORTANTE: La IA ya NO puede cambiar la dirección mandada por la zona
            try:
                ai_verdict = self.market_ai.analyze(
                    df_m1=df_m1, df_m5=df_m5, df_m15=df_m15, df_h1=df_h1,
                    zone_level=nearest_zone.level,
                    zone_type=nearest_zone.zone_type,
                    zone_strength=nearest_zone.strength,
                    zone_touches=nearest_zone.touches,
                    zone_hold_rate=nearest_zone.hold_rate,
                    pattern_name=pattern_name,
                    pattern_strength=pattern.get("strength", 0.5),
                    context=context,
                )
                ai_score     = ai_verdict.score
                ai_conf      = ai_verdict.confidence
                ai_dir       = ai_verdict.direction
                ai_label     = ai_verdict.setup_label
                ai_narrative = ai_verdict.narrative
                ai_should    = ai_verdict.should_trade

                # La IA NO puede cambiar la dirección de la zona — solo puede bloquear
                # Si la IA dice dirección contraria a la zona con score alto → SKIP
                if ai_dir != "NEUTRAL" and ai_dir != expected_dir and ai_score >= 75 and nearest_zone.strength >= 0.80:
                    return self._wait(
                        f"IA contradice zona ({ai_dir} vs {expected_dir}) con score {ai_score:.0f} — skip",
                        asset, context=context
                    )

                if ai_label == "SKIP" and ai_score < 25:
                    return {
                        "asset": asset, "action": "WAIT", "signal": expected_dir,
                        "score": ai_score, "confidence": ai_conf,
                        "reason": f"IA: {ai_label} — {ai_narrative[:60]}",
                        "phase": phase, "zone": nearest_zone.level,
                        "zone_strength": nearest_zone.strength,
                        "pattern": pattern_name, "context": context,
                        "ai_narrative": ai_narrative, "ai_label": ai_label,
                        "session": session_name,
                    }

            except Exception as ai_err:
                ai_score = 50.0; ai_conf = 0.5; ai_dir = expected_dir
                ai_label = "NORMAL"; ai_narrative = f"IA no disponible: {ai_err}"
                ai_should = True

            # ── 9. Puntuación combinada ───────────────────────────────────────
            adaptive_score, breakdown = self.learner.score_conditions(conditions)
            min_score = self.learner.get_min_score()

            # Bonus por primera visita a la zona (señal más limpia)
            first_visit_bonus = 0.05 if is_first_visit else 0.0
            # Bonus por historial positivo de la zona en esta sesión
            zone_hist_hr = zone_history_analysis.get("session_hold_rate", 0.5)
            zone_hist_bonus = max(0.0, (zone_hist_hr - 0.5) * 0.10)

            if not zone_ctx.get("trend_aligned", True):
                soft_penalties += 0.03
            if rsi_dist < self.learner.get_threshold("min_rsi_distance", 8.0):
                soft_penalties += 0.02
            if nearest_zone.hold_rate < self.learner.get_threshold("min_zone_hold_rate", 0.45):
                soft_penalties += 0.02
            if not timing["valid"]:
                soft_penalties += 0.03

            adaptive_adjusted = max(0.0, adaptive_score - soft_penalties + first_visit_bonus + zone_hist_bonus)

            # 50% AdaptiveLearner + 50% MarketAI
            ai_normalized = ai_score / 100.0
            final_score = adaptive_adjusted * 0.50 + ai_normalized * 0.50

            # ── 10. Umbral mínimo adaptado a la sesión ────────────────────────
            session_min_conf = session_params.get("min_confidence", 0.40)
            effective_min = max(self.learner.get_min_score() * 0.75, session_min_conf - 0.12)
            if ai_label in ("EXCELENTE", "BUENO"):
                effective_min = max(0.25, effective_min - 0.15)
            elif ai_label == "MODERADO":
                effective_min = effective_min * 0.85
            elif ai_label in ("DEBIL",):
                effective_min = min(effective_min, 0.50)

            if final_score >= effective_min:
                confidence = self._calculate_confidence(
                    final_score, nearest_zone, context, pattern, timing
                )
                confidence = confidence * 0.40 + ai_conf * 0.60
                # Ajuste de confianza por sesión
                session_quality = self.session.get_session_quality()
                confidence = confidence * (0.85 + session_quality * 0.15)

                # Expiración basada en historial de la zona + sesión
                pips_per_min = atr_pct * current_price * 10000 / 1.0  # pips por minuto aprox
                hist_exp = self.zone_history.get_optimal_expiration(
                    asset, nearest_zone.level, nearest_zone.zone_type, pips_per_min
                )
                exp_info = self._adaptive_expiration(
                    context, pattern, zone=nearest_zone, conditions=conditions
                )
                # Usar el mayor entre el histórico y el calculado (más conservador)
                best_exp_seconds = max(exp_info["seconds"], hist_exp)
                best_exp_seconds = self.session.should_adjust_expiration(best_exp_seconds)
                exp_info["seconds"] = best_exp_seconds
                exp_info["minutes"] = best_exp_seconds // 60

                narrative = (
                    f"[{session_name}] {nearest_zone.zone_type.upper()} {nearest_zone.level:.5f} "
                    f"{'(1ra visita)' if is_first_visit else '(revisita)'} | "
                    f"{ai_narrative or ''}"
                )

                return {
                    "asset": asset,
                    "action": "TRADE",
                    "signal": expected_dir,
                    "score": final_score * 100,
                    "confidence": min(0.95, confidence),
                    "expiration": exp_info["seconds"],
                    "expiration_minutes": exp_info["minutes"],
                    "expiration_label": exp_info["label"],
                    "expiration_color": exp_info["color"],
                    "complexity_score": exp_info["complexity_score"],
                    "expiration_reasons": exp_info["reasons"],
                    "reason": narrative,
                    "phase": phase,
                    "zone": nearest_zone.level,
                    "zone_strength": nearest_zone.strength,
                    "zone_touches": nearest_zone.touches,
                    "zone_hold_rate": nearest_zone.hold_rate,
                    "pattern": pattern_name,
                    "pattern_strength": pattern.get("strength", 0),
                    "dominant_trend": context.get("dominant_trend"),
                    "rsi": rsi,
                    "setup_quality": context.get("setup_quality", 0),
                    "rejection_wick": timing.get("rejection_wick_pct", 0),
                    "conditions": conditions,
                    "context": context,
                    "zone_object": nearest_zone,
                    "adaptive_breakdown": breakdown,
                    "timing": timing,
                    "ai_score": ai_score,
                    "ai_label": ai_label,
                    "ai_narrative": ai_narrative,
                    "ai_evidence_for": ai_verdict.evidence_for if 'ai_verdict' in dir() else [],
                    "session": session_name,
                    "is_first_visit": is_first_visit,
                    "zone_history": zone_history_analysis,
                }
            else:
                top_missing = self._top_missing(conditions, self.learner.weights)
                return {
                    "asset": asset,
                    "action": "WAIT",
                    "signal": expected_dir,
                    "score": final_score * 100,
                    "confidence": final_score,
                    "reason": f"[{session_name}] IA:{ai_label} score={final_score*100:.0f} | {top_missing}",
                    "phase": phase,
                    "zone": nearest_zone.level,
                    "zone_strength": nearest_zone.strength,
                    "pattern": pattern_name,
                    "context": context,
                    "ai_score": ai_score,
                    "ai_label": ai_label,
                    "ai_narrative": ai_narrative,
                    "session": session_name,
                }

        except Exception as e:
            return self._wait(f"Error en análisis: {e}", asset)

    # ── Micro-estructura: análisis fino de velas para detectar reversión ─────

    def _check_micro_structure(self, df_m1: pd.DataFrame, expected_dir: str) -> bool:
        """
        Analiza micro-estructura de las últimas 3-5 velas cerradas para detectar
        señales sutiles de reversión cuando no hay patrón clásico evidente.
        
        Busca:
        - Cambios en el momentum (velas cada vez más pequeñas)
        - Mechas de rechazo acumulativas
        - Divergencias en el volumen relativo
        - Cambios en la presión compradora/vendedora
        """
        if len(df_m1) < 8:
            return False
            
        try:
            # Últimas 5 velas cerradas (no incluir la actual en formación)
            recent = df_m1.iloc[-6:-1]  # velas -6 a -2
            signal_candle = df_m1.iloc[-2]  # vela de señal
            
            # Datos básicos
            opens  = recent["open"].astype(float).values
            highs  = recent["high"].astype(float).values  
            lows   = recent["low"].astype(float).values
            closes = recent["close"].astype(float).values
            
            # Análisis de momentum decreciente
            bodies = np.abs(closes - opens)
            ranges = highs - lows
            
            # 1. ¿Las velas se están haciendo más pequeñas? (momentum perdiendo fuerza)
            momentum_weakening = False
            if len(bodies) >= 3:
                # Comparar últimas 2 velas con las 2 anteriores
                recent_avg = np.mean(bodies[-2:])
                earlier_avg = np.mean(bodies[-4:-2])
                if recent_avg < earlier_avg * 0.75:  # 25% más pequeñas
                    momentum_weakening = True
            
            # 2. Análisis de mechas acumulativas (rechazo creciente)
            rejection_building = False
            if expected_dir == "CALL":
                # Para CALL, buscar mechas inferiores crecientes
                lower_wicks = np.minimum(opens, closes) - lows
                wick_ratios = lower_wicks / np.maximum(ranges, 1e-8)
                # ¿Las últimas 2 velas tienen mechas inferiores significativas?
                if len(wick_ratios) >= 2 and np.mean(wick_ratios[-2:]) > 0.25:
                    rejection_building = True
            else:  # PUT
                # Para PUT, buscar mechas superiores crecientes  
                upper_wicks = highs - np.maximum(opens, closes)
                wick_ratios = upper_wicks / np.maximum(ranges, 1e-8)
                if len(wick_ratios) >= 2 and np.mean(wick_ratios[-2:]) > 0.25:
                    rejection_building = True
            
            # 3. Patrón de indecisión creciente
            indecision_pattern = False
            if len(bodies) >= 3:
                # Cuerpos cada vez más pequeños relativos al rango
                body_ratios = bodies / np.maximum(ranges, 1e-8)
                if np.mean(body_ratios[-2:]) < 0.40:  # Últimas velas con cuerpos <40% del rango
                    indecision_pattern = True
            
            # 4. Cambio en la dirección de cierre
            direction_shift = False
            if len(closes) >= 4:
                # ¿Las últimas 2 velas cerraron en dirección opuesta a las 2 anteriores?
                recent_direction = "up" if closes[-1] > closes[-3] else "down"
                earlier_direction = "up" if closes[-3] > closes[-5] else "down"
                expected_recent = "up" if expected_dir == "CALL" else "down"
                
                if recent_direction == expected_recent and recent_direction != earlier_direction:
                    direction_shift = True
            
            # 5. Análisis de la vela de señal específica
            signal_quality = False
            s_open = float(signal_candle["open"])
            s_high = float(signal_candle["high"])
            s_low = float(signal_candle["low"])
            s_close = float(signal_candle["close"])
            s_body = abs(s_close - s_open)
            s_range = s_high - s_low
            
            if s_range > 0:
                if expected_dir == "CALL":
                    # Para CALL: vela con mecha inferior prominente y cierre en parte alta
                    lower_wick = min(s_open, s_close) - s_low
                    close_position = (s_close - s_low) / s_range  # 0=low, 1=high
                    if lower_wick / s_range > 0.30 and close_position > 0.60:
                        signal_quality = True
                else:  # PUT
                    # Para PUT: vela con mecha superior prominente y cierre en parte baja
                    upper_wick = s_high - max(s_open, s_close)
                    close_position = (s_high - s_close) / s_range  # 0=high, 1=low
                    if upper_wick / s_range > 0.30 and close_position > 0.60:
                        signal_quality = True
            
            # Decisión: necesitamos al menos 1 de las 5 condiciones (más permisivo para generar señales)
            conditions_met = sum([
                momentum_weakening,
                rejection_building, 
                indecision_pattern,
                direction_shift,
                signal_quality
            ])
            
            return conditions_met >= 1
            
        except Exception:
            return False

    # ── Escaneo de zonas ──────────────────────────────────────────────────────

    def _rescan_zones(self, asset: str, df_m5: pd.DataFrame,
                       df_m15: Optional[pd.DataFrame], df_h1: Optional[pd.DataFrame]):
        try:
            detected = self.zone_detector.detect_multi_tf(
                df_m5=df_m5,
                df_m15=df_m15 if df_m15 is not None and len(df_m15) >= 10 else df_m5,
                df_h1=df_h1 if df_h1 is not None and len(df_h1) >= 5 else None,
            )
            if detected:
                self.memory.bulk_add_zones(asset, detected)
                self.memory.purge_weak_zones(asset, min_strength=0.20)
                self.memory.save()
        except Exception:
            pass

    # ── Utilidades ────────────────────────────────────────────────────────────

    def _check_mtf_alignment(self, context: Dict, direction: str) -> bool:
        expected = "uptrend" if direction == "CALL" else "downtrend"
        s1  = context.get("structure_m1",  {}).get("trend", "neutral")
        s5  = context.get("structure_m5",  {}).get("trend", "neutral")
        s15 = context.get("structure_m15", {}).get("trend", "neutral")
        sh1 = context.get("structure_h1",  {}).get("trend", "neutral")
        opposite = "downtrend" if direction == "CALL" else "uptrend"
        # H1 tiene doble peso — si H1 está en contra, es señal débil
        all_tfs = [s1, s5, s15, sh1, sh1]  # sh1 cuenta doble
        aligned = sum(1 for s in all_tfs if s == expected)
        against = sum(1 for s in all_tfs if s == opposite)
        return aligned >= 3 or (aligned >= 2 and against == 0)

    def _calc_atr_pct(self, df_m1) -> float:
        """Calcula ATR como porcentaje del precio para medir volatilidad actual"""
        try:
            if df_m1 is None or len(df_m1) < 15:
                return 0.001
            highs  = df_m1["high"].values[-15:]
            lows   = df_m1["low"].values[-15:]
            closes = df_m1["close"].values[-15:]
            trs = []
            for i in range(1, len(highs)):
                tr = max(highs[i] - lows[i],
                         abs(highs[i] - closes[i-1]),
                         abs(lows[i]  - closes[i-1]))
                trs.append(tr)
            atr = float(sum(trs) / len(trs)) if trs else 0.001
            price = float(closes[-1]) if closes[-1] > 0 else 1.0
            return atr / price
        except Exception:
            return 0.001

    def _calculate_confidence(self, score: float, zone, context: Dict,
                               pattern: Dict, timing: Dict = None) -> float:
        base         = score
        zone_boost   = zone.strength   * 0.12
        pattern_boost = pattern.get("strength", 0.5) * 0.10
        quality_boost = context.get("setup_quality", 0.5) * 0.08
        dir_boost     = context.get("direction_confidence", 0.5) * 0.08
        timing_boost  = 0.05 if timing and timing.get("rejection_wick_pct", 0) >= 0.40 else 0.0
        raw = base * 0.57 + zone_boost + pattern_boost + quality_boost + dir_boost + timing_boost
        return min(0.95, max(0.65, raw))

    def _adaptive_expiration(self, context: Dict, pattern: Dict,
                              zone=None, conditions: Dict = None) -> Dict:
        """
        Expiración adaptativa 1-5 minutos según complejidad real del trade.
        Simple (todo alineado) → 1 min. Complejo (señales mixtas) → 5 min.
        """
        conditions  = conditions or {}
        momentum    = context.get("momentum", {})
        zone_ctx    = context.get("zone_context", {})
        phase       = context.get("market_phase", "ranging")
        zone_str    = zone.strength if zone else zone_ctx.get("zone_strength", 0.5)
        pattern_str = pattern.get("strength", 0.5)
        pattern_name = pattern.get("pattern", "")
        rsi          = momentum.get("rsi_m1", 50)
        rsi_dist     = abs(rsi - 50)
        trend_aligned = zone_ctx.get("trend_aligned", False)
        mtf_aligned   = conditions.get("mtf_aligned", False)
        dominant_trend = context.get("dominant_trend", "neutral")

        simplicity = 0.0
        reasons    = []

        # Zona (0-25 pts)
        if zone_str >= 0.80:
            simplicity += 25; reasons.append("zona muy fuerte")
        elif zone_str >= 0.65:
            simplicity += 18; reasons.append("zona fuerte")
        elif zone_str >= 0.50:
            simplicity += 10; reasons.append("zona moderada")
        else:
            simplicity += 3;  reasons.append("zona débil")

        # Patrón (0-22 pts) — bonus por ser de vela cerrada siempre
        if pattern_name in ("morning_star", "evening_star"):
            simplicity += 15; reasons.append("star pattern (3 velas)")
        elif "engulfing" in pattern_name:
            simplicity += 19; reasons.append("engulfing fuerte")
        elif "pin_bar" in pattern_name:
            pts = 22 if pattern_str >= 0.85 else 16
            simplicity += pts; reasons.append(f"pin bar {'potente' if pts==22 else 'moderado'}")
        elif pattern_name in ("hammer", "shooting_star"):
            simplicity += 17; reasons.append("hammer/shooting star")
        elif "doji" in pattern_name:
            simplicity += 8;  reasons.append("doji (ambiguo → +tiempo)")
        else:
            simplicity += 5

        # RSI (0-20 pts)
        if rsi_dist >= 30:
            simplicity += 20; reasons.append(f"RSI muy extremo ({rsi:.0f})")
        elif rsi_dist >= 20:
            simplicity += 15; reasons.append(f"RSI extremo ({rsi:.0f})")
        elif rsi_dist >= 12:
            simplicity += 9
        else:
            simplicity += 3;  reasons.append(f"RSI neutro ({rsi:.0f}) → +tiempo")

        # MTF alignment (0-18 pts)
        if mtf_aligned:
            simplicity += 18; reasons.append("MTF alineados")
        else:
            simplicity += 3

        # Tendencia (0-12 pts)
        if trend_aligned and dominant_trend in ("uptrend", "downtrend"):
            simplicity += 12; reasons.append("con tendencia")
        elif trend_aligned:
            simplicity += 6
        else:
            reasons.append("contra tendencia → +tiempo")

        # Fase (bono/malus)
        if phase in ("trending_up", "trending_down"):
            simplicity += 5;  reasons.append("mercado en tendencia")
        elif phase == "ranging":
            simplicity -= 5
        elif phase == "dead":
            simplicity -= 12; reasons.append("mercado lento → +tiempo")

        # Rechazo visible en timing (+5 bono)
        if conditions.get("rejection_visible"):
            simplicity += 5; reasons.append("rechazo visible en zona")

        simplicity = max(0.0, min(100.0, simplicity))

        # Star patterns necesitan mínimo 2 min
        min_floor = 3  # mínimo 3 minutos para dar tiempo al precio a reaccionar

        if simplicity >= 82:
            minutes, label, color = 1, "SIMPLE",       "green"
        elif simplicity >= 64:
            minutes, label, color = 2, "MODERADO",     "cyan"
        elif simplicity >= 46:
            minutes, label, color = 3, "NORMAL",        "yellow"
        elif simplicity >= 28:
            minutes, label, color = 4, "COMPLEJO",      "dark_orange"
        else:
            minutes, label, color = 5, "MUY COMPLEJO", "red"

        minutes = max(min_floor, minutes)

        return {
            "seconds":          minutes * 60,
            "minutes":          minutes,
            "label":            label,
            "color":            color,
            "complexity_score": round(100 - simplicity, 1),
            "simplicity_score": round(simplicity, 1),
            "reasons":          reasons,
        }

    def _build_reason(self, zone, context: Dict, pattern: Dict,
                       conditions: Dict, exp_info: Dict = None,
                       timing: Dict = None) -> str:
        parts = [
            f"Zona {zone.zone_type} {zone.level:.5f} (str={zone.strength:.2f}, {zone.touches}x)",
            f"Patrón: {pattern.get('pattern','?')} [vela cerrada]",
            f"Tendencia: {context.get('dominant_trend','?')}",
            f"RSI={context.get('momentum',{}).get('rsi_m1',50):.1f}",
        ]
        if timing:
            parts.append(f"Rechazo={timing.get('rejection_wick_pct',0):.0%}")
        if exp_info:
            parts.append(f"Exp: {exp_info['minutes']}min [{exp_info['label']}]")
        return " | ".join(parts)

    def _top_missing(self, conditions: Dict, weights: Dict, n: int = 3) -> str:
        missing = [(k, weights.get(k, 1.0)) for k, v in conditions.items()
                   if not v and weights.get(k, 1.0) > 0.8]
        missing.sort(key=lambda x: -x[1])
        return ", ".join(k for k, _ in missing[:n]) or "score_bajo"

    def _wait(self, reason: str, asset: str,
               context: Dict = None, zone=None) -> Dict:
        return {
            "asset": asset,
            "action": "WAIT",
            "signal": "NEUTRAL",
            "score": 0.0,
            "confidence": 0.0,
            "reason": reason,
            "phase": context.get("market_phase", "?") if context else "?",
            "zone": zone.level if zone else None,
            "zone_strength": zone.strength if zone else 0.0,
        }
