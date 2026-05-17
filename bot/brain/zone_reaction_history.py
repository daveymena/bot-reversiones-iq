"""
Zone Reaction History — Memoria detallada de cómo reaccionó el precio en cada zona
No solo cuenta toques — registra QUÉ pasó cada vez que el precio llegó a esa zona.

Para cada toque registra:
- ¿Rebotó o rompió?
- ¿Cuántas velas tardó en moverse?
- ¿Cuántos pips se movió?
- ¿Había patrón de vela en ese momento?
- ¿Cuál era la sesión de mercado?
- ¿Era primera visita o revisita?
"""
import json
import os
import time
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict, field


@dataclass
class ZoneTouchEvent:
    """Un evento de toque de zona con toda la información relevante"""
    timestamp: float
    price_at_touch: float
    direction_expected: str      # CALL o PUT
    result: str                  # HOLD, BREAK, UNKNOWN
    pips_moved: float            # cuánto se movió después
    candles_to_move: int         # cuántas velas tardó en moverse
    had_pattern: bool
    pattern_name: str
    session: str                 # OVERLAP_EU_US, EUROPE, AMERICA, ASIA, PACIFIC
    was_first_visit: bool        # primera vez en esta zona en las últimas 24h
    rsi_at_touch: float
    trend_aligned: bool


@dataclass
class ZoneProfile:
    """Perfil completo de comportamiento de una zona"""
    asset: str
    level: float
    zone_type: str               # support, resistance
    touch_events: List[dict] = field(default_factory=list)

    # Estadísticas calculadas
    total_touches: int = 0
    successful_holds: int = 0
    breaks: int = 0
    avg_pips_on_hold: float = 0.0
    avg_candles_to_move: float = 0.0

    # Por sesión
    session_stats: Dict = field(default_factory=dict)

    # Primera visita vs revisita
    first_visit_hold_rate: float = 0.0
    revisit_hold_rate: float = 0.0

    # Con patrón vs sin patrón
    with_pattern_hold_rate: float = 0.0
    without_pattern_hold_rate: float = 0.0

    # Última actividad
    last_touch_ts: float = 0.0
    last_result: str = "UNKNOWN"

    def add_touch(self, event: ZoneTouchEvent):
        """Registra un nuevo toque y recalcula estadísticas"""
        self.touch_events.append(asdict(event))
        self.last_touch_ts = event.timestamp
        self.last_result = event.result
        self._recalculate_stats()

    def _recalculate_stats(self):
        """Recalcula todas las estadísticas desde los eventos"""
        if not self.touch_events:
            return

        events = self.touch_events
        self.total_touches = len(events)
        holds = [e for e in events if e["result"] == "HOLD"]
        breaks = [e for e in events if e["result"] == "BREAK"]
        self.successful_holds = len(holds)
        self.breaks = len(breaks)

        if holds:
            self.avg_pips_on_hold = sum(e["pips_moved"] for e in holds) / len(holds)
            self.avg_candles_to_move = sum(e["candles_to_move"] for e in holds) / len(holds)

        # Estadísticas por sesión
        self.session_stats = {}
        for e in events:
            sess = e.get("session", "UNKNOWN")
            if sess not in self.session_stats:
                self.session_stats[sess] = {"holds": 0, "breaks": 0, "total": 0}
            self.session_stats[sess]["total"] += 1
            if e["result"] == "HOLD":
                self.session_stats[sess]["holds"] += 1
            elif e["result"] == "BREAK":
                self.session_stats[sess]["breaks"] += 1

        # Primera visita vs revisita
        first_visits = [e for e in events if e.get("was_first_visit", True)]
        revisits = [e for e in events if not e.get("was_first_visit", True)]

        if first_visits:
            fv_holds = sum(1 for e in first_visits if e["result"] == "HOLD")
            self.first_visit_hold_rate = fv_holds / len(first_visits)
        if revisits:
            rv_holds = sum(1 for e in revisits if e["result"] == "HOLD")
            self.revisit_hold_rate = rv_holds / len(revisits)

        # Con patrón vs sin patrón
        with_pat = [e for e in events if e.get("had_pattern", False)]
        without_pat = [e for e in events if not e.get("had_pattern", False)]

        if with_pat:
            wp_holds = sum(1 for e in with_pat if e["result"] == "HOLD")
            self.with_pattern_hold_rate = wp_holds / len(with_pat)
        if without_pat:
            wop_holds = sum(1 for e in without_pat if e["result"] == "HOLD")
            self.without_pattern_hold_rate = wop_holds / len(without_pat)

    def get_hold_rate(self) -> float:
        if self.total_touches == 0:
            return 0.5
        return self.successful_holds / self.total_touches

    def get_session_hold_rate(self, session: str) -> float:
        """Hold rate específico para una sesión"""
        stats = self.session_stats.get(session, {})
        total = stats.get("total", 0)
        if total == 0:
            return self.get_hold_rate()  # fallback al global
        return stats.get("holds", 0) / total

    def get_expected_pips(self, session: str = None) -> float:
        """Pips esperados de rebote en esta zona"""
        if self.avg_pips_on_hold > 0:
            return self.avg_pips_on_hold
        return 10.0  # default conservador

    def get_optimal_expiration(self, pips_per_minute: float = 8.0) -> int:
        """
        Calcula la expiración óptima basada en el historial de esta zona.
        pips_per_minute: velocidad promedio del mercado actual
        """
        expected_pips = self.get_expected_pips()
        if pips_per_minute <= 0:
            pips_per_minute = 8.0
        minutes_needed = expected_pips / pips_per_minute
        # Agregar 50% de margen de seguridad
        optimal_minutes = max(1, min(5, int(minutes_needed * 1.5)))
        return optimal_minutes * 60  # en segundos

    def was_recently_touched(self, within_candles_m5: int = 3) -> bool:
        """¿Fue tocada esta zona recientemente? (para detectar revisitas)"""
        if not self.touch_events:
            return False
        last_touch = self.last_touch_ts
        # 3 velas M5 = 15 minutos
        threshold = within_candles_m5 * 5 * 60
        return (time.time() - last_touch) < threshold

    def get_analysis_summary(self, session: str = None) -> Dict:
        """Resumen del análisis de esta zona para el motor de decisión"""
        hold_rate = self.get_session_hold_rate(session) if session else self.get_hold_rate()
        recent_events = self.touch_events[-5:] if len(self.touch_events) >= 5 else self.touch_events
        recent_holds = sum(1 for e in recent_events if e["result"] == "HOLD")
        recent_hold_rate = recent_holds / len(recent_events) if recent_events else hold_rate

        return {
            "hold_rate": hold_rate,
            "recent_hold_rate": recent_hold_rate,
            "total_touches": self.total_touches,
            "avg_pips": self.avg_pips_on_hold,
            "avg_candles": self.avg_candles_to_move,
            "last_result": self.last_result,
            "was_recently_touched": self.was_recently_touched(),
            "first_visit_hold_rate": self.first_visit_hold_rate,
            "revisit_hold_rate": self.revisit_hold_rate,
            "with_pattern_hold_rate": self.with_pattern_hold_rate,
            "session_hold_rate": hold_rate,
            "is_reliable": self.total_touches >= 3 and hold_rate >= 0.55,
            "last_broke": self.last_result == "BREAK",
        }


class ZoneReactionHistory:
    """
    Gestiona el historial de reacciones de todas las zonas.
    Persiste en JSON junto con el estado de aprendizaje.
    """

    def __init__(self, persist_path: str = "brain/zone_reactions.json"):
        self.persist_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "..", persist_path
        )
        self.profiles: Dict[str, Dict[str, ZoneProfile]] = {}
        # key: "ASSET_level" -> ZoneProfile
        self._load()

    def _zone_key(self, asset: str, level: float) -> str:
        return f"{asset}_{level:.5f}"

    def get_or_create_profile(self, asset: str, level: float,
                               zone_type: str) -> ZoneProfile:
        key = self._zone_key(asset, level)
        if key not in self.profiles:
            self.profiles[key] = ZoneProfile(
                asset=asset, level=level, zone_type=zone_type
            )
        return self.profiles[key]

    def record_touch(self, asset: str, level: float, zone_type: str,
                      result: str, pips_moved: float, candles_to_move: int,
                      had_pattern: bool, pattern_name: str,
                      session: str, rsi: float, trend_aligned: bool,
                      price_at_touch: float):
        """Registra un toque de zona con resultado conocido"""
        profile = self.get_or_create_profile(asset, level, zone_type)

        # Detectar si es primera visita (no tocada en últimas 3 velas M5)
        was_first = not profile.was_recently_touched(within_candles_m5=3)

        event = ZoneTouchEvent(
            timestamp=time.time(),
            price_at_touch=price_at_touch,
            direction_expected="CALL" if zone_type == "support" else "PUT",
            result=result,
            pips_moved=pips_moved,
            candles_to_move=candles_to_move,
            had_pattern=had_pattern,
            pattern_name=pattern_name,
            session=session,
            was_first_visit=was_first,
            rsi_at_touch=rsi,
            trend_aligned=trend_aligned,
        )
        profile.add_touch(event)
        self._save()

    def get_zone_analysis(self, asset: str, level: float,
                           zone_type: str, session: str = None) -> Dict:
        """
        Obtiene el análisis histórico de una zona.
        Si no hay historial, retorna valores conservadores.
        """
        key = self._zone_key(asset, level)
        if key not in self.profiles:
            return {
                "hold_rate": 0.5,
                "recent_hold_rate": 0.5,
                "total_touches": 0,
                "avg_pips": 10.0,
                "avg_candles": 2.0,
                "last_result": "UNKNOWN",
                "was_recently_touched": False,
                "first_visit_hold_rate": 0.5,
                "revisit_hold_rate": 0.5,
                "with_pattern_hold_rate": 0.5,
                "session_hold_rate": 0.5,
                "is_reliable": False,
                "last_broke": False,
                "no_history": True,
            }
        profile = self.profiles[key]
        return profile.get_analysis_summary(session)

    def is_first_visit(self, asset: str, level: float, zone_type: str) -> bool:
        """¿Es la primera visita a esta zona en las últimas 15 minutos?"""
        key = self._zone_key(asset, level)
        if key not in self.profiles:
            return True
        return not self.profiles[key].was_recently_touched(within_candles_m5=3)

    def get_optimal_expiration(self, asset: str, level: float,
                                zone_type: str, pips_per_minute: float) -> int:
        """Expiración óptima basada en historial de esta zona específica"""
        key = self._zone_key(asset, level)
        if key not in self.profiles:
            return 120  # 2 minutos por defecto
        return self.profiles[key].get_optimal_expiration(pips_per_minute)

    def _save(self):
        try:
            os.makedirs(os.path.dirname(self.persist_path), exist_ok=True)
            data = {}
            for key, profile in self.profiles.items():
                data[key] = {
                    "asset": profile.asset,
                    "level": profile.level,
                    "zone_type": profile.zone_type,
                    "touch_events": profile.touch_events[-100:],  # últimos 100
                    "total_touches": profile.total_touches,
                    "successful_holds": profile.successful_holds,
                    "breaks": profile.breaks,
                    "avg_pips_on_hold": profile.avg_pips_on_hold,
                    "avg_candles_to_move": profile.avg_candles_to_move,
                    "session_stats": profile.session_stats,
                    "first_visit_hold_rate": profile.first_visit_hold_rate,
                    "revisit_hold_rate": profile.revisit_hold_rate,
                    "with_pattern_hold_rate": profile.with_pattern_hold_rate,
                    "without_pattern_hold_rate": profile.without_pattern_hold_rate,
                    "last_touch_ts": profile.last_touch_ts,
                    "last_result": profile.last_result,
                }
            with open(self.persist_path, "w") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    def _load(self):
        if not os.path.exists(self.persist_path):
            return
        try:
            with open(self.persist_path, "r") as f:
                data = json.load(f)
            for key, d in data.items():
                profile = ZoneProfile(
                    asset=d["asset"],
                    level=d["level"],
                    zone_type=d["zone_type"],
                    touch_events=d.get("touch_events", []),
                    total_touches=d.get("total_touches", 0),
                    successful_holds=d.get("successful_holds", 0),
                    breaks=d.get("breaks", 0),
                    avg_pips_on_hold=d.get("avg_pips_on_hold", 0.0),
                    avg_candles_to_move=d.get("avg_candles_to_move", 0.0),
                    session_stats=d.get("session_stats", {}),
                    first_visit_hold_rate=d.get("first_visit_hold_rate", 0.0),
                    revisit_hold_rate=d.get("revisit_hold_rate", 0.0),
                    with_pattern_hold_rate=d.get("with_pattern_hold_rate", 0.0),
                    without_pattern_hold_rate=d.get("without_pattern_hold_rate", 0.0),
                    last_touch_ts=d.get("last_touch_ts", 0.0),
                    last_result=d.get("last_result", "UNKNOWN"),
                )
                self.profiles[key] = profile
        except Exception:
            pass


# Singleton
_history: Optional[ZoneReactionHistory] = None


def get_zone_history() -> ZoneReactionHistory:
    global _history
    if _history is None:
        _history = ZoneReactionHistory()
    return _history
