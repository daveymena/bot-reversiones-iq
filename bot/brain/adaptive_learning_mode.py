"""
Modo de Aprendizaje Acelerado
Permite al bot operar más frecuentemente durante la fase inicial de aprendizaje
"""
import json
import os
from typing import Dict


class AdaptiveLearningMode:
    """
    Gestiona umbrales adaptativos según la fase de aprendizaje del bot.
    
    Filosofía:
    - Primeros 100 trades: MODO APRENDIZAJE (filtros suaves, opera más)
    - Después de 100 trades: MODO EXPERTO (filtros normales, más selectivo)
    """
    
    def __init__(self, data_file="data/learning_progress.json"):
        self.data_file = data_file
        self.learning_phase_trades = 100  # Trades necesarios para completar aprendizaje
        self.current_trades = 0
        self.phase = "LEARNING"  # LEARNING o EXPERT
        self._load_progress()
    
    def _load_progress(self):
        """Carga progreso desde archivo"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.current_trades = data.get('total_trades', 0)
                    self.phase = data.get('phase', 'LEARNING')
            except Exception:
                pass
    
    def _save_progress(self):
        """Guarda progreso en archivo"""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        try:
            with open(self.data_file, 'w') as f:
                json.dump({
                    'total_trades': self.current_trades,
                    'phase': self.phase,
                    'learning_progress': self.get_learning_progress()
                }, f, indent=2)
        except Exception:
            pass
    
    def record_trade(self):
        """Registra un nuevo trade y actualiza fase si es necesario"""
        self.current_trades += 1
        
        # Cambiar a modo EXPERT después de 100 trades
        if self.current_trades >= self.learning_phase_trades and self.phase == "LEARNING":
            self.phase = "EXPERT"
            print(f"\n🎓 FASE DE APRENDIZAJE COMPLETADA ({self.current_trades} trades)")
            print(f"   Cambiando a MODO EXPERTO - Filtros más selectivos activados\n")
        
        self._save_progress()
    
    def get_thresholds(self) -> Dict[str, float]:
        """
        Retorna umbrales según la fase actual.
        
        MODO APRENDIZAJE: Filtros más suaves para operar más frecuentemente
        MODO EXPERTO: Filtros normales para mayor selectividad
        """
        if self.phase == "LEARNING":
            # MODO APRENDIZAJE: Opera ~5-8 veces/día
            return {
                'min_confidence': 0.55,      # vs 0.65 normal (más permisivo)
                'min_zone_strength': 0.30,   # vs 0.35 normal (acepta zonas más débiles)
                'min_score': 0.35,           # vs 0.45 normal (umbral más bajo)
                'zone_tolerance_pct': 0.0025,  # vs 0.0020 normal (rango más amplio)
                'min_rsi_distance': 8.0,     # vs 10.0 normal (menos estricto)
                'min_zone_hold_rate': 0.40,  # vs 0.45 normal (menos exigente)
            }
        else:
            # MODO EXPERTO: Opera ~2-4 veces/día (más selectivo)
            return {
                'min_confidence': 0.65,
                'min_zone_strength': 0.35,
                'min_score': 0.45,
                'zone_tolerance_pct': 0.0020,
                'min_rsi_distance': 10.0,
                'min_zone_hold_rate': 0.45,
            }
    
    def get_cooldown_multiplier(self) -> float:
        """
        Retorna multiplicador para cooldowns.
        
        MODO APRENDIZAJE: Cooldowns más cortos (0.7x)
        MODO EXPERTO: Cooldowns normales (1.0x)
        """
        return 0.7 if self.phase == "LEARNING" else 1.0
    
    def get_learning_progress(self) -> float:
        """Retorna progreso de aprendizaje (0.0 - 1.0)"""
        return min(1.0, self.current_trades / self.learning_phase_trades)
    
    def get_status_message(self) -> str:
        """Retorna mensaje de estado para el dashboard"""
        if self.phase == "LEARNING":
            progress = self.get_learning_progress() * 100
            remaining = self.learning_phase_trades - self.current_trades
            return f"APRENDIENDO ({progress:.0f}% - {remaining} trades restantes)"
        else:
            return f"EXPERTO ({self.current_trades} trades)"
    
    def should_take_experimental_trade(self, score: float, similar_count: int) -> Dict:
        """
        Decide si tomar un trade experimental (setup nuevo con score bajo).
        
        Solo en MODO APRENDIZAJE y si el setup es nuevo (pocas muestras).
        """
        if self.phase != "LEARNING":
            return {'should_trade': False, 'reason': 'Modo experto - no experimental'}
        
        # Si el setup es nuevo (menos de 5 trades similares)
        if similar_count < 5:
            # Umbral más bajo para setups nuevos
            if score >= 30:  # vs 35-45 normal
                return {
                    'should_trade': True,
                    'position_size_mult': 0.6,  # 60% del tamaño normal
                    'reason': 'EXPERIMENTAL - Aprendiendo setup nuevo',
                    'is_experimental': True
                }
        
        return {'should_trade': False, 'reason': 'Setup ya conocido o score muy bajo'}
    
    def get_phase_emoji(self) -> str:
        """Retorna emoji según la fase"""
        return "🎓" if self.phase == "LEARNING" else "🎯"


# Instancia global
_learning_mode = None

def get_learning_mode() -> AdaptiveLearningMode:
    """Retorna instancia singleton del modo de aprendizaje"""
    global _learning_mode
    if _learning_mode is None:
        _learning_mode = AdaptiveLearningMode()
    return _learning_mode
