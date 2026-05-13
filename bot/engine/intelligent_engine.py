"""
Intelligent Engine v4.0 — El cerebro del bot
No busca señales en cualquier momento.
Primero detecta zonas vivas del gráfico completo,
espera a que el precio llegue a ellas,
analiza el contexto completo,
espera confirmación de vela exacta,
y solo entonces decide si entrar.
"""
import time
import numpy as np
import pandas as pd
from typing import Dict, Optional, List, Tuple

from brain.market_memory import get_market_memory
from brain.zone_detector import ZoneDetector
from brain.context_analyzer import ContextAnalyzer
from brain.adaptive_learner import get_adaptive_learner


class CandlePatternDetector:
    """Detecta patrones de velas de alta precisión."""

    def detect(self, df: pd.DataFrame, expected_direction: str) -> Dict:
        if len(df) < 4:
            return {"pattern": "none", "confirmed": False, "strength": 0.0}

        c1 = df.iloc[-4]
        c2 = df.iloc[-3]
        c3 = df.iloc[-2]
        last = df.iloc[-1]

        o, h, l, c = float(last["open"]), float(last["high"]), float(last["low"]), float(last["close"])
        o3, h3, l3, c3v = float(c3["open"]), float(c3["high"]), float(c3["low"]), float(c3["close"])
        o2, c2v = float(c2["open"]), float(c2["close"])

        body = abs(c - o)
        full_range = h - l if h > l else 0.00001
        upper_wick = h - max(o, c)
        lower_wick = min(o, c) - l
        is_bull = c > o
        is_bear = c < o

        patterns = []

        # ── Pin Bar (rechazo fuerte) ──
        if full_range > 0:
            if lower_wick / full_range >= 0.60 and body / full_range <= 0.30:
                patterns.append(("pin_bar_bullish", 0.85))
            if upper_wick / full_range >= 0.60 and body / full_range <= 0.30:
                patterns.append(("pin_bar_bearish", 0.85))

        # ── Hammer / Shooting Star ──
        if lower_wick >= body * 2.0 and upper_wick <= body * 0.5 and body > 0:
            patterns.append(("hammer", 0.75))
        if upper_wick >= body * 2.0 and lower_wick <= body * 0.5 and body > 0:
            patterns.append(("shooting_star", 0.75))

        # ── Engulfing ──
        if is_bull and o2 > c2v:  # prev bearish
            if c > o2 and o < c2v:
                patterns.append(("bullish_engulfing", 0.80))
        if is_bear and o2 < c2v:  # prev bullish
            if c < o2 and o > c2v:
                patterns.append(("bearish_engulfing", 0.80))

        # ── Doji de reversión ──
        if full_range > 0 and body / full_range <= 0.12:
            if expected_direction == "CALL" and lower_wick > upper_wick:
                patterns.append(("doji_reversal_bull", 0.65))
            elif expected_direction == "PUT" and upper_wick > lower_wick:
                patterns.append(("doji_reversal_bear", 0.65))

        # ── Morning Star / Evening Star (3 velas) ──
        o1v, c1v = float(c1["open"]), float(c1["close"])
        if c1v < o1v and abs(c2v - o2) < abs(c1v - o1v) * 0.4 and is_bull and c > (o1v + c1v) / 2:
            patterns.append(("morning_star", 0.90))
        if c1v > o1v and abs(c2v - o2) < abs(c1v - o1v) * 0.4 and is_bear and c < (o1v + c1v) / 2:
            patterns.append(("evening_star", 0.90))

        if not patterns:
            return {"pattern": "none", "confirmed": False, "strength": 0.0,
                    "conditions": {}}

        # Filtrar por dirección esperada
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
            return {"pattern": "none", "confirmed": False, "strength": 0.0,
                    "all_patterns": [p for p, _ in patterns], "conditions": {}}

        best_pattern, best_strength = max(valid, key=lambda x: x[1])
        conditions = {
            f"pattern_{best_pattern.split('_')[0]}": True,
            "pattern_strong": best_strength >= 0.75,
        }

        return {
            "pattern": best_pattern,
            "confirmed": True,
            "strength": best_strength,
            "all_detected": [p for p, _ in patterns],
            "conditions": conditions,
        }


class IntelligentEngine:
    """
    Motor de inteligencia principal.
    Flujo:
    1. Descargar gráfico completo (H1 + M15 + M5 + M1)
    2. Detectar zonas vivas en todo el histórico
    3. Actualizar memoria del mercado
    4. Verificar si el precio actual está EN una zona fuerte
    5. Si no está en zona → WAIT
    6. Si está en zona → analizar contexto completo
    7. Esperar confirmación de vela exacta en la zona
    8. Puntuar con pesos adaptativos
    9. Decidir si entrar o no
    """

    def __init__(self):
        self.memory = get_market_memory()
        self.zone_detector = ZoneDetector()
        self.context_analyzer = ContextAnalyzer()
        self.learner = get_adaptive_learner()
        self.pattern_detector = CandlePatternDetector()
        self._last_zone_scan: Dict[str, float] = {}
        self._zone_scan_interval = 300  # re-escanear zonas cada 5 minutos

    def analyze(self, asset: str, market_data, fe=None) -> Optional[Dict]:
        """
        Análisis completo del mercado para un activo.
        Devuelve señal estructurada o None si hay error.
        """
        try:
            # ── 1. Descargar datos multi-timeframe ──────────────────────────
            df_m1 = market_data.get_candles(asset, 60, 200)
            if df_m1 is None or len(df_m1) < 30:
                return self._wait("Datos M1 insuficientes", asset)

            df_m5 = market_data.get_candles(asset, 300, 120)
            df_m15 = market_data.get_candles(asset, 900, 60)
            df_h1 = market_data.get_candles(asset, 3600, 30)

            if df_m5 is None or len(df_m5) < 20:
                return self._wait("Datos M5 insuficientes", asset)

            current_price = float(df_m1["close"].iloc[-1])
            if current_price <= 0:
                return self._wait("Precio inválido", asset)

            # ── 2. Escanear/actualizar zonas cada N segundos ─────────────────
            last_scan = self._last_zone_scan.get(asset, 0)
            if time.time() - last_scan > self._zone_scan_interval:
                self._rescan_zones(asset, df_m5, df_m15, df_h1)
                self._last_zone_scan[asset] = time.time()

            # ── 3. ¿Está el precio en una zona fuerte? ───────────────────────
            min_zone_strength = self.learner.get_threshold("min_zone_strength", 0.40)
            nearest_zone = self.memory.get_nearest_strong_zone(
                asset, current_price, tolerance_pct=0.002
            )
            zone_context_summary = self.memory.get_zone_context(asset, current_price)

            if nearest_zone is None or nearest_zone.strength < min_zone_strength:
                # No estamos en ninguna zona fuerte — esperar
                reason = f"Precio lejos de zona fuerte (nearest: {nearest_zone.strength:.2f if nearest_zone else 'N/A'})"
                return {
                    "asset": asset,
                    "action": "WAIT",
                    "signal": "NEUTRAL",
                    "score": 0.0,
                    "confidence": 0.0,
                    "reason": reason,
                    "phase": "buscando_zona",
                    "zone_count": len(self.memory.get_all_zones(asset)),
                    "zone_context": zone_context_summary,
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
            if expected_dir == "NEUTRAL":
                return self._wait("Dirección no clara (señales contradictorias)", asset,
                                   context=context, zone=nearest_zone)

            # ── 5. Verificar fase del mercado ────────────────────────────────
            phase = context.get("market_phase", "unknown")
            if phase == "dead":
                return self._wait("Mercado muerto (sin volatilidad)", asset, context=context)

            # ── 6. Detectar patrón de vela en la zona ───────────────────────
            pattern = self.pattern_detector.detect(df_m1, expected_dir)
            if not pattern["confirmed"]:
                # El precio está en zona pero la vela aún no confirma
                # Esto es MUY importante: evita entrar a destiempo
                detected = pattern.get("all_detected", [])
                reason = f"En zona {nearest_zone.strength:.2f} — esperando vela de confirmación"
                if detected:
                    reason += f" (detectados: {', '.join(detected)})"
                return {
                    "asset": asset,
                    "action": "WAIT",
                    "signal": expected_dir,
                    "score": 35.0,
                    "confidence": context.get("direction_confidence", 0),
                    "reason": reason,
                    "phase": phase,
                    "zone": nearest_zone.level,
                    "zone_strength": nearest_zone.strength,
                    "waiting_for_pattern": True,
                    "context": context,
                }

            # ── 7. Construir condiciones para el AdaptiveLearner ─────────────
            zone_ctx = context.get("zone_context", {})
            momentum = context.get("momentum", {})
            rsi = momentum.get("rsi_m1", 50)
            rsi_distance = abs(rsi - 50)

            conditions = {
                # Zona
                "zone_strength_high": nearest_zone.strength >= 0.70,
                "zone_strength_medium": 0.50 <= nearest_zone.strength < 0.70,
                "zone_multi_tf": getattr(nearest_zone, "notes", []) and "multi_tf" in str(nearest_zone.notes),
                "zone_touch_3plus": nearest_zone.touches >= 3,
                "zone_hold_rate_high": nearest_zone.hold_rate >= 0.70,
                # Tendencia
                "trend_aligned": zone_ctx.get("trend_aligned", False),
                "trend_strong": context.get("dominant_trend") in ("uptrend", "downtrend"),
                "counter_trend": not zone_ctx.get("trend_aligned", True),
                # RSI
                "rsi_extreme": rsi < 25 or rsi > 75,
                "rsi_oversold_sold": rsi < 35 and expected_dir == "CALL",
                "rsi_overbought": rsi > 65 and expected_dir == "PUT",
                "rsi_divergence": momentum.get("bullish_divergence", False) or momentum.get("bearish_divergence", False),
                # Patrones
                "pattern_pin_bar": "pin_bar" in pattern.get("pattern", ""),
                "pattern_engulfing": "engulfing" in pattern.get("pattern", ""),
                "pattern_hammer": pattern.get("pattern", "") in ("hammer", "shooting_star"),
                "pattern_doji_reversal": "doji" in pattern.get("pattern", ""),
                "pattern_morning_star": "star" in pattern.get("pattern", ""),
                "pattern_strong": pattern.get("strength", 0) >= 0.75,
                # MACD
                "macd_cross": abs(momentum.get("macd_hist", 0)) > 0.00001,
                "macd_hist_turning": momentum.get("macd_turning", False),
                # Contexto
                "approach_clean": context.get("before_context", {}).get("approach", "") in
                                   ("falling_to_support", "rising_to_resistance"),
                "mtf_aligned": self._check_mtf_alignment(context, expected_dir),
                "market_phase_ranging": phase == "ranging",
                "market_phase_trending": phase in ("trending_up", "trending_down"),
                "setup_quality_high": context.get("setup_quality", 0) >= 0.65,
            }

            # ── 8. Puntuar con pesos adaptativos ─────────────────────────────
            adaptive_score, breakdown = self.learner.score_conditions(conditions)
            min_score = self.learner.get_min_score()

            # Penalización dura por condiciones críticas ausentes
            hard_penalties = 0.0
            if not zone_ctx.get("trend_aligned", True):
                hard_penalties += 0.10
            if rsi_distance < self.learner.get_threshold("min_rsi_distance", 10.0):
                hard_penalties += 0.05
            if nearest_zone.hold_rate < self.learner.get_threshold("min_zone_hold_rate", 0.55):
                hard_penalties += 0.08

            final_score = max(0.0, adaptive_score - hard_penalties)

            # ── 9. Decisión final ────────────────────────────────────────────
            if final_score >= min_score:
                confidence = self._calculate_confidence(
                    final_score, nearest_zone, context, pattern
                )
                exp_info = self._adaptive_expiration(
                    context, pattern, zone=nearest_zone, conditions=conditions
                )

                return {
                    "asset": asset,
                    "action": "TRADE",
                    "signal": expected_dir,
                    "score": final_score * 100,
                    "confidence": confidence,
                    "expiration": exp_info["seconds"],
                    "expiration_minutes": exp_info["minutes"],
                    "expiration_label": exp_info["label"],
                    "expiration_color": exp_info["color"],
                    "complexity_score": exp_info["complexity_score"],
                    "expiration_reasons": exp_info["reasons"],
                    "reason": self._build_reason(nearest_zone, context, pattern, conditions, exp_info),
                    "phase": phase,
                    "zone": nearest_zone.level,
                    "zone_strength": nearest_zone.strength,
                    "zone_touches": nearest_zone.touches,
                    "zone_hold_rate": nearest_zone.hold_rate,
                    "pattern": pattern.get("pattern", ""),
                    "pattern_strength": pattern.get("strength", 0),
                    "dominant_trend": context.get("dominant_trend"),
                    "rsi": rsi,
                    "setup_quality": context.get("setup_quality", 0),
                    "conditions": conditions,
                    "context": context,
                    "zone_object": nearest_zone,
                    "adaptive_breakdown": breakdown,
                }
            else:
                top_missing = self._top_missing_conditions(conditions, self.learner.weights)
                return {
                    "asset": asset,
                    "action": "WAIT",
                    "signal": expected_dir,
                    "score": final_score * 100,
                    "confidence": final_score,
                    "reason": f"Score {final_score*100:.0f} < {min_score*100:.0f} (faltan: {top_missing})",
                    "phase": phase,
                    "zone": nearest_zone.level,
                    "zone_strength": nearest_zone.strength,
                    "pattern": pattern.get("pattern", ""),
                    "context": context,
                }

        except Exception as e:
            return self._wait(f"Error en análisis: {e}", asset)

    # ── Escaneo de zonas ──────────────────────────────────────────────────────

    def _rescan_zones(self, asset: str, df_m5: pd.DataFrame,
                       df_m15: Optional[pd.DataFrame], df_h1: Optional[pd.DataFrame]):
        """Re-detecta zonas desde el histórico completo y actualiza la memoria."""
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
        """Verifica que M1, M5 y M15 apunten en la misma dirección."""
        expected = "uptrend" if direction == "CALL" else "downtrend"
        s1 = context.get("structure_m1", {}).get("trend", "neutral")
        s5 = context.get("structure_m5", {}).get("trend", "neutral")
        s15 = context.get("structure_m15", {}).get("trend", "neutral")

        aligned_count = sum(1 for s in [s1, s5, s15] if s == expected)
        partial = sum(1 for s in [s1, s5, s15] if s != ("downtrend" if direction == "CALL" else "uptrend"))
        return aligned_count >= 2 or partial >= 2

    def _calculate_confidence(self, score: float, zone, context: Dict, pattern: Dict) -> float:
        """Combina múltiples factores en un confidence final 0-1."""
        base = score
        zone_boost = zone.strength * 0.15
        pattern_boost = pattern.get("strength", 0.5) * 0.10
        quality_boost = context.get("setup_quality", 0.5) * 0.10
        dir_boost = context.get("direction_confidence", 0.5) * 0.10

        raw = base * 0.55 + zone_boost + pattern_boost + quality_boost + dir_boost
        return min(0.96, max(0.50, raw))

    def _adaptive_expiration(self, context: Dict, pattern: Dict,
                              zone=None, conditions: Dict = None) -> Dict:
        """
        Expiración adaptativa 1-5 minutos según la complejidad real del trade.

        SIMPLE   (1 min)  → Todo alineado: zona fuerte ≥0.75, patrón potente,
                            RSI extremo (<25/>75), MTF alineado, tendencia a favor.
        MODERADO (2 min)  → Buena zona, patrón confirmado, MTF mayormente alineado.
        NORMAL   (3 min)  → Señales mixtas pero coherentes. Zona sólida ≥0.55.
        COMPLEJO (4 min)  → Zona parcial, RSI borderline, patrones moderados,
                            contra-tendencia parcial.
        MUY COMP (5 min)  → Zona débil, sin MTF, patrón moderado, mercado rango
                            lento. El precio necesita más tiempo para moverse.

        Devuelve dict con: seconds, minutes, label, complexity_score, reasons
        """
        conditions = conditions or {}
        momentum   = context.get("momentum", {})
        zone_ctx   = context.get("zone_context", {})
        phase      = context.get("market_phase", "ranging")

        zone_strength   = zone.strength if zone else zone_ctx.get("zone_strength", 0.5)
        pattern_str     = pattern.get("strength", 0.5)
        pattern_name    = pattern.get("pattern", "")
        rsi             = momentum.get("rsi_m1", 50)
        rsi_distance    = abs(rsi - 50)
        trend_aligned   = zone_ctx.get("trend_aligned", False)
        mtf_aligned     = conditions.get("mtf_aligned", False)
        setup_quality   = context.get("setup_quality", 0.5)
        dominant_trend  = context.get("dominant_trend", "neutral")

        # ── Calcular puntuación de SIMPLICIDAD (0-100, mayor = más simple = menos tiempo) ──
        simplicity = 0.0
        reasons    = []

        # Zona (0-25 pts)
        if zone_strength >= 0.80:
            simplicity += 25; reasons.append("zona muy fuerte")
        elif zone_strength >= 0.65:
            simplicity += 18; reasons.append("zona fuerte")
        elif zone_strength >= 0.50:
            simplicity += 10; reasons.append("zona moderada")
        else:
            simplicity += 3;  reasons.append("zona débil")

        # Patrón de vela (0-20 pts)
        if pattern_name in ("morning_star", "evening_star"):
            simplicity += 14; reasons.append("patrón 3 velas (star)")
        elif pattern_name in ("bullish_engulfing", "bearish_engulfing"):
            simplicity += 18; reasons.append("engulfing fuerte")
        elif pattern_name in ("pin_bar_bullish", "pin_bar_bearish"):
            if pattern_str >= 0.80:
                simplicity += 20; reasons.append("pin bar potente")
            else:
                simplicity += 14; reasons.append("pin bar moderado")
        elif pattern_name in ("hammer", "shooting_star"):
            simplicity += 16; reasons.append("hammer/shooting star")
        elif "doji" in pattern_name:
            simplicity += 8;  reasons.append("doji (ambiguo)")
        else:
            simplicity += 5

        # RSI (0-20 pts)
        if rsi_distance >= 30:
            simplicity += 20; reasons.append(f"RSI muy extremo ({rsi:.0f})")
        elif rsi_distance >= 20:
            simplicity += 15; reasons.append(f"RSI extremo ({rsi:.0f})")
        elif rsi_distance >= 12:
            simplicity += 9;  reasons.append(f"RSI moderado ({rsi:.0f})")
        else:
            simplicity += 3;  reasons.append(f"RSI neutro ({rsi:.0f})")

        # MTF alignment (0-18 pts)
        if mtf_aligned:
            simplicity += 18; reasons.append("MTF alineado")
        else:
            simplicity += 4

        # Tendencia (0-12 pts)
        if trend_aligned and dominant_trend in ("uptrend", "downtrend"):
            simplicity += 12; reasons.append("con tendencia dominante")
        elif trend_aligned:
            simplicity += 7
        else:
            simplicity += 0;  reasons.append("⚠ contra tendencia (+tiempo)")

        # Fase del mercado (0-5 pts bono/malus)
        if phase in ("trending_up", "trending_down"):
            simplicity += 5;  reasons.append("mercado en tendencia")
        elif phase == "ranging":
            simplicity -= 5;  reasons.append("mercado en rango (lento)")
        elif phase == "dead":
            simplicity -= 10; reasons.append("mercado muerto (muy lento)")

        simplicity = max(0.0, min(100.0, simplicity))

        # ── Mapear simplicidad → minutos ──────────────────────────────────────
        # Patrones de 3 velas necesitan al menos 2 min independientemente
        min_floor = 2 if pattern_name.endswith("star") else 1

        if simplicity >= 80:
            minutes = 1
            label   = "SIMPLE"
            color   = "green"
        elif simplicity >= 62:
            minutes = 2
            label   = "MODERADO"
            color   = "cyan"
        elif simplicity >= 44:
            minutes = 3
            label   = "NORMAL"
            color   = "yellow"
        elif simplicity >= 26:
            minutes = 4
            label   = "COMPLEJO"
            color   = "dark_orange"
        else:
            minutes = 5
            label   = "MUY COMPLEJO"
            color   = "red"

        minutes = max(min_floor, minutes)
        seconds = minutes * 60

        return {
            "seconds":          seconds,
            "minutes":          minutes,
            "label":            label,
            "color":            color,
            "complexity_score": round(100 - simplicity, 1),
            "simplicity_score": round(simplicity, 1),
            "reasons":          reasons,
        }

    def _build_reason(self, zone, context: Dict, pattern: Dict,
                       conditions: Dict, exp_info: Dict = None) -> str:
        parts = []
        parts.append(f"Zona {zone.zone_type} {zone.level:.5f} (str={zone.strength:.2f}, {zone.touches}x)")
        parts.append(f"Patrón: {pattern.get('pattern', '?')}")
        trend = context.get("dominant_trend", "neutral")
        parts.append(f"Tendencia: {trend}")
        rsi = context.get("momentum", {}).get("rsi_m1", 50)
        parts.append(f"RSI={rsi:.1f}")
        if exp_info:
            parts.append(f"Exp: {exp_info['minutes']}min ({exp_info['label']})")
        return " | ".join(parts)

    def _top_missing_conditions(self, conditions: Dict, weights: Dict, n: int = 3) -> str:
        missing = [(k, weights.get(k, 1.0)) for k, v in conditions.items()
                   if not v and weights.get(k, 1.0) > 0.8]
        missing.sort(key=lambda x: -x[1])
        return ", ".join([k for k, _ in missing[:n]]) or "score_bajo"

    def _wait(self, reason: str, asset: str, context: Dict = None, zone=None) -> Dict:
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
