"""
Trade Evaluator — Auto-evaluación post-operación
Después de cada trade diagnostica exactamente por qué ganó o perdió
y alimenta ese diagnóstico al AdaptiveLearner para que mejore.
"""
import time
from typing import Dict, Optional, List


class TradeEvaluator:
    """
    Evalúa cada operación y produce un diagnóstico estructurado.
    El diagnóstico se usa para:
    1. Ajustar thresholds del AdaptiveLearner
    2. Mostrar en el dashboard qué está aprendiendo el bot
    3. Registro histórico de lecciones aprendidas
    """

    def evaluate(self, trade_record: Dict, context_at_entry: Dict,
                  conditions_at_entry: Dict[str, bool],
                  market_after: Optional[Dict] = None) -> Dict:
        """
        trade_record: {asset, direction, amount, confidence, result, pnl, ...}
        context_at_entry: el contexto completo que devolvió el ContextAnalyzer
        conditions_at_entry: las condiciones que usó el AdaptiveLearner
        market_after: datos del mercado después del trade (opcional)
        """
        result = trade_record.get("result", "UNKNOWN")
        direction = trade_record.get("direction", "CALL")
        asset = trade_record.get("asset", "")

        diagnosis = {
            "trade_id": trade_record.get("order_id", ""),
            "result": result,
            "asset": asset,
            "direction": direction,
            "timestamp": time.time(),
            "primary_cause": "unknown",
            "secondary_causes": [],
            "lessons": [],
            "what_worked": [],
            "what_failed": [],
            "score_accuracy": 0.0,
        }

        if result == "WIN":
            diagnosis = self._evaluate_win(diagnosis, context_at_entry, conditions_at_entry)
        elif result == "LOSS":
            diagnosis = self._evaluate_loss(diagnosis, context_at_entry, conditions_at_entry, market_after)

        return diagnosis

    # ── Evaluación de WIN ─────────────────────────────────────────────────────

    def _evaluate_win(self, diag: Dict, ctx: Dict, conditions: Dict) -> Dict:
        diag["primary_cause"] = "correct_read"
        what_worked = []
        zone_ctx = ctx.get("zone_context", {})

        if zone_ctx.get("zone_strength", 0) >= 0.6:
            what_worked.append(f"Zona fuerte ({zone_ctx['zone_strength']:.2f}) aguantó el precio")
        if zone_ctx.get("trend_aligned"):
            what_worked.append("Operación alineada con la tendencia dominante")
        if ctx.get("momentum", {}).get("rsi_oversold") or ctx.get("momentum", {}).get("rsi_overbought"):
            rsi = ctx.get("momentum", {}).get("rsi_m1", 50)
            what_worked.append(f"RSI en zona extrema ({rsi:.1f})")
        if conditions.get("pattern_strong"):
            what_worked.append("Patrón de vela fuerte confirmó la entrada")
        if conditions.get("mtf_aligned"):
            what_worked.append("Múltiples timeframes alineados")

        if not what_worked:
            what_worked.append("Setup general favorable")

        diag["what_worked"] = what_worked
        diag["lessons"] = [f"✓ {w}" for w in what_worked]
        return diag

    # ── Evaluación de LOSS ────────────────────────────────────────────────────

    def _evaluate_loss(self, diag: Dict, ctx: Dict, conditions: Dict,
                        market_after: Optional[Dict]) -> Dict:
        causes = []
        what_failed = []
        lessons = []
        zone_ctx = ctx.get("zone_context", {})
        momentum = ctx.get("momentum", {})
        dominant_trend = ctx.get("dominant_trend", "neutral")
        direction = diag["direction"]

        # ── Causa 1: Zona débil o sin zona ──
        zone_strength = zone_ctx.get("zone_strength", 0)
        if zone_strength < 0.45:
            causes.append("zone_too_weak")
            what_failed.append(f"Zona muy débil (strength={zone_strength:.2f}, necesita ≥0.45)")
            lessons.append("Aumentar umbral mínimo de fuerza de zona")

        # ── Causa 2: Contra la tendencia ──
        trend_aligned = zone_ctx.get("trend_aligned", True)
        if not trend_aligned:
            causes.append("counter_trend")
            what_failed.append(f"Operación contra la tendencia dominante ({dominant_trend})")
            lessons.append("Evitar operar contra la tendencia a menos que la zona sea muy fuerte (>0.75)")

        # ── Causa 3: RSI no extremo ──
        rsi = momentum.get("rsi_m1", 50)
        direction_lower = direction.lower()
        if direction_lower == "call" and rsi > 55:
            causes.append("rsi_not_extreme")
            what_failed.append(f"CALL con RSI en {rsi:.1f} (no hay sobreventa)")
            lessons.append("Para CALL necesitar RSI < 40 idealmente")
        elif direction_lower == "put" and rsi < 45:
            causes.append("rsi_not_extreme")
            what_failed.append(f"PUT con RSI en {rsi:.1f} (no hay sobrecompra)")
            lessons.append("Para PUT necesitar RSI > 60 idealmente")

        # ── Causa 4: Sin patrón de confirmación ──
        has_strong_pattern = conditions.get("pattern_strong") or conditions.get("pattern_pin_bar") or \
                              conditions.get("pattern_engulfing") or conditions.get("pattern_hammer")
        if not has_strong_pattern:
            causes.append("no_candle_pattern")
            what_failed.append("Sin patrón de vela confirmatorio en la zona")
            lessons.append("Siempre esperar patrón de vela fuerte en la zona (pin bar, engulfing, hammer)")

        # ── Causa 5: MTF no alineado ──
        if not conditions.get("mtf_aligned"):
            causes.append("mtf_not_aligned")
            what_failed.append("Timeframes M1/M5/M15 no alineados en la misma dirección")
            lessons.append("Confirmar que M5 y M15 apuntan en la misma dirección antes de entrar")

        # ── Causa 6: Mercado en fase mala ──
        phase = ctx.get("market_phase", "unknown")
        if phase in ("dead", "volatile_ranging"):
            causes.append("bad_market_phase")
            what_failed.append(f"Mercado en fase desfavorable: {phase}")
            lessons.append("No operar en mercados muertos o con volatilidad errática")

        # ── Causa 7: Setup quality baja ──
        sq = ctx.get("setup_quality", 0)
        if sq < 0.50:
            causes.append("poor_setup_quality")
            what_failed.append(f"Calidad del setup baja ({sq:.2f})")
            lessons.append("Esperar setups con calidad ≥ 0.65")

        # Seleccionar causa primaria (la más impactante)
        priority = ["zone_too_weak", "counter_trend", "bad_market_phase",
                     "no_candle_pattern", "rsi_not_extreme", "poor_setup_quality", "mtf_not_aligned"]
        primary = "unknown"
        for p in priority:
            if p in causes:
                primary = p
                break

        diag["primary_cause"] = primary
        diag["secondary_causes"] = [c for c in causes if c != primary]
        diag["what_failed"] = what_failed
        diag["lessons"] = lessons

        return diag

    def format_for_display(self, diag: Dict) -> List[str]:
        """Formatea el diagnóstico para mostrar en el dashboard."""
        lines = []
        result = diag.get("result", "?")
        icon = "✔" if result == "WIN" else "✘"
        color = "green" if result == "WIN" else "red"

        lines.append(f"[{color}]{icon} Último análisis: {diag['asset']} {diag['direction']}[/{color}]")

        if result == "WIN":
            for w in diag.get("what_worked", [])[:3]:
                lines.append(f"  [green]+ {w}[/green]")
        else:
            for f in diag.get("what_failed", [])[:3]:
                lines.append(f"  [red]− {f}[/red]")
            if diag.get("lessons"):
                lines.append(f"  [yellow]→ {diag['lessons'][0]}[/yellow]")

        return lines
