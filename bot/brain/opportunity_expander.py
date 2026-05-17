"""
Opportunity Expander — Encuentra MÁS oportunidades de calidad
Sin bajar los estándares, pero siendo menos restrictivo en combinaciones válidas.

Filosofía:
- No todos los factores tienen que ser perfectos simultáneamente
- Un setup EXCELENTE en 2-3 factores puede compensar debilidad en otros
- Más operaciones = más aprendizaje = mejor bot
"""
import numpy as np
from typing import Dict, List


class OpportunityExpander:
    """
    Expande oportunidades válidas sin sacrificar calidad.
    
    Estrategia:
    1. Identifica el "factor dominante" del setup
    2. Si ese factor es EXCELENTE, relaja otros requisitos
    3. Permite combinaciones alternativas de factores
    """
    
    def __init__(self):
        # Factores que pueden ser "dominantes" (compensar otros)
        self.dominant_factors = {
            'zone_strength': {
                'excellent': 0.85,  # Zona muy fuerte
                'good': 0.70,
                'acceptable': 0.50
            },
            'pattern_strength': {
                'excellent': 0.88,  # Patrón muy claro
                'good': 0.75,
                'acceptable': 0.60
            },
            'rsi_extreme': {
                'excellent': 25,    # RSI < 25 o > 75
                'good': 30,         # RSI < 30 o > 70
                'acceptable': 35    # RSI < 35 o > 65
            },
            'divergence': {
                'excellent': True,  # Divergencia confirmada
                'good': False,
                'acceptable': False
            },
            'mtf_alignment': {
                'excellent': 3,     # 3 timeframes alineados
                'good': 2,          # 2 timeframes alineados
                'acceptable': 1     # 1 timeframe alineado
            }
        }
    
    def evaluate_opportunity(self, signal: Dict, context: Dict) -> Dict:
        """
        Evalúa si una oportunidad rechazada debería ser aceptada.
        
        Returns:
            {
                'should_trade': bool,
                'reason': str,
                'confidence_boost': float,
                'dominant_factor': str
            }
        """
        # Si ya fue aceptada, no hacer nada
        if signal.get('action') == 'TRADE':
            return {'should_trade': True, 'reason': 'Ya aceptada'}
        
        # Analizar factores dominantes
        dominant_analysis = self._analyze_dominant_factors(signal, context)
        
        # Si hay un factor EXCELENTE, considerar aceptar
        if dominant_analysis['has_excellent_factor']:
            return self._evaluate_with_dominant_factor(signal, context, dominant_analysis)
        
        # Si hay múltiples factores BUENOS, considerar aceptar
        if dominant_analysis['good_factors_count'] >= 3:
            return self._evaluate_with_multiple_good_factors(signal, context, dominant_analysis)
        
        # Si no hay factores dominantes, mantener rechazo
        return {
            'should_trade': False,
            'reason': 'Sin factores dominantes suficientes',
            'confidence_boost': 0.0
        }
    
    def _analyze_dominant_factors(self, signal: Dict, context: Dict) -> Dict:
        """Analiza qué factores son dominantes en este setup"""
        analysis = {
            'excellent_factors': [],
            'good_factors': [],
            'has_excellent_factor': False,
            'good_factors_count': 0
        }
        
        # 1. Zona
        zone_strength = signal.get('zone_strength', 0)
        if zone_strength >= self.dominant_factors['zone_strength']['excellent']:
            analysis['excellent_factors'].append('zone_strength')
        elif zone_strength >= self.dominant_factors['zone_strength']['good']:
            analysis['good_factors'].append('zone_strength')
        
        # 2. Patrón
        pattern_strength = signal.get('pattern_strength', 0)
        if pattern_strength >= self.dominant_factors['pattern_strength']['excellent']:
            analysis['excellent_factors'].append('pattern_strength')
        elif pattern_strength >= self.dominant_factors['pattern_strength']['good']:
            analysis['good_factors'].append('pattern_strength')
        
        # 3. RSI extremo
        rsi = context.get('momentum', {}).get('rsi_m1', 50)
        rsi_dist = abs(rsi - 50)
        if rsi < self.dominant_factors['rsi_extreme']['excellent'] or rsi > (100 - self.dominant_factors['rsi_extreme']['excellent']):
            analysis['excellent_factors'].append('rsi_extreme')
        elif rsi < self.dominant_factors['rsi_extreme']['good'] or rsi > (100 - self.dominant_factors['rsi_extreme']['good']):
            analysis['good_factors'].append('rsi_extreme')
        
        # 4. Divergencia
        momentum = context.get('momentum', {})
        if momentum.get('bullish_divergence') or momentum.get('bearish_divergence'):
            analysis['excellent_factors'].append('divergence')
        
        # 5. Alineación MTF
        conditions = signal.get('conditions', {})
        if conditions.get('mtf_aligned'):
            mtf_count = sum([
                context.get('structure_m1', {}).get('trend') in ('uptrend', 'downtrend'),
                context.get('structure_m5', {}).get('trend') in ('uptrend', 'downtrend'),
                context.get('structure_m15', {}).get('trend') in ('uptrend', 'downtrend')
            ])
            if mtf_count >= 3:
                analysis['excellent_factors'].append('mtf_alignment')
            elif mtf_count >= 2:
                analysis['good_factors'].append('mtf_alignment')
        
        analysis['has_excellent_factor'] = len(analysis['excellent_factors']) > 0
        analysis['good_factors_count'] = len(analysis['good_factors'])
        
        return analysis
    
    def _evaluate_with_dominant_factor(self, signal: Dict, context: Dict, 
                                       dominant_analysis: Dict) -> Dict:
        """
        Evalúa si aceptar basándose en un factor EXCELENTE.
        
        Regla: Si hay 1 factor EXCELENTE + 1 factor BUENO, aceptar
        """
        excellent = dominant_analysis['excellent_factors']
        good = dominant_analysis['good_factors']
        
        # Necesita al menos 1 excelente + 1 bueno
        if len(excellent) >= 1 and (len(good) >= 1 or len(excellent) >= 2):
            confidence_boost = 0.08  # +8% confianza
            
            # Si hay 2 excelentes, boost mayor
            if len(excellent) >= 2:
                confidence_boost = 0.12
            
            return {
                'should_trade': True,
                'reason': f"Factor dominante EXCELENTE: {', '.join(excellent)}",
                'confidence_boost': confidence_boost,
                'dominant_factor': excellent[0],
                'supporting_factors': good
            }
        
        return {
            'should_trade': False,
            'reason': 'Factor excelente sin suficiente soporte',
            'confidence_boost': 0.0
        }
    
    def _evaluate_with_multiple_good_factors(self, signal: Dict, context: Dict,
                                             dominant_analysis: Dict) -> Dict:
        """
        Evalúa si aceptar basándose en múltiples factores BUENOS.
        
        Regla: Si hay 3+ factores BUENOS, aceptar
        """
        good = dominant_analysis['good_factors']
        
        if len(good) >= 3:
            confidence_boost = 0.05  # +5% confianza
            
            return {
                'should_trade': True,
                'reason': f"Múltiples factores BUENOS convergentes: {', '.join(good)}",
                'confidence_boost': confidence_boost,
                'supporting_factors': good
            }
        
        return {
            'should_trade': False,
            'reason': 'Insuficientes factores buenos',
            'confidence_boost': 0.0
        }
    
    def suggest_alternative_setups(self, signal: Dict, context: Dict) -> List[Dict]:
        """
        Sugiere setups alternativos que podrían ser válidos.
        
        Útil para logging y debugging.
        """
        suggestions = []
        
        # Sugerencia 1: Esperar mejor patrón
        if signal.get('zone_strength', 0) >= 0.70 and signal.get('pattern_strength', 0) < 0.70:
            suggestions.append({
                'type': 'wait_for_pattern',
                'message': 'Zona fuerte detectada - esperar patrón más claro',
                'wait_candles': 3
            })
        
        # Sugerencia 2: Esperar RSI más extremo
        rsi = context.get('momentum', {}).get('rsi_m1', 50)
        if 35 < rsi < 65 and signal.get('zone_strength', 0) >= 0.60:
            suggestions.append({
                'type': 'wait_for_rsi',
                'message': f'RSI neutral ({rsi:.0f}) - esperar extremo (<30 o >70)',
                'current_rsi': rsi
            })
        
        # Sugerencia 3: Cambiar timeframe de expiración
        if signal.get('pattern_strength', 0) >= 0.75:
            suggestions.append({
                'type': 'adjust_expiration',
                'message': 'Patrón fuerte - considerar expiración más larga (4-5 min)',
                'suggested_expiration': 5
            })
        
        return suggestions


class SmartThresholdAdjuster:
    """
    Ajusta umbrales dinámicamente según condiciones de mercado.
    
    Objetivo: Operar más en mercados favorables, menos en desfavorables.
    """
    
    def __init__(self):
        self.base_thresholds = {
            'min_confidence': 0.65,
            'min_zone_strength': 0.35,
            'min_score': 0.45
        }
        self.market_conditions = {
            'favorable': 0,    # Contador de condiciones favorables
            'unfavorable': 0   # Contador de condiciones desfavorables
        }
    
    def adjust_thresholds(self, context: Dict, recent_results: List[Dict]) -> Dict:
        """
        Ajusta umbrales basándose en:
        1. Condiciones actuales de mercado
        2. Resultados recientes
        """
        adjusted = self.base_thresholds.copy()
        
        # 1. Ajuste por volatilidad
        volatility = context.get('volatility', {}).get('atr_pct', 0.01)
        if volatility > 0.02:  # Alta volatilidad
            # Mercado volátil = más oportunidades pero más riesgo
            # Mantener umbrales normales
            pass
        elif volatility < 0.008:  # Baja volatilidad
            # Mercado muerto = pocas oportunidades
            # Relajar umbrales ligeramente para no quedarse sin operar
            adjusted['min_confidence'] -= 0.03
            adjusted['min_zone_strength'] -= 0.05
        
        # 2. Ajuste por fase de mercado
        phase = context.get('market_phase', 'unknown')
        if phase == 'ranging':
            # Ranging = mejor para reversiones en zonas
            # Relajar umbrales
            adjusted['min_confidence'] -= 0.02
            adjusted['min_score'] -= 0.03
        elif phase in ('trending_up', 'trending_down'):
            # Trending = reversiones más difíciles
            # Mantener umbrales estrictos
            pass
        
        # 3. Ajuste por resultados recientes
        if len(recent_results) >= 5:
            recent_wins = sum(1 for r in recent_results[-5:] if r.get('result') == 'WIN')
            win_rate = recent_wins / 5
            
            if win_rate >= 0.70:  # 70%+ win rate
                # Racha ganadora = condiciones favorables
                # Relajar umbrales para capitalizar
                adjusted['min_confidence'] -= 0.03
                adjusted['min_score'] -= 0.05
            elif win_rate <= 0.30:  # 30%- win rate
                # Racha perdedora = condiciones desfavorables
                # Endurecer umbrales para proteger capital
                adjusted['min_confidence'] += 0.05
                adjusted['min_score'] += 0.08
        
        # Límites de seguridad
        adjusted['min_confidence'] = max(0.55, min(0.75, adjusted['min_confidence']))
        adjusted['min_zone_strength'] = max(0.25, min(0.50, adjusted['min_zone_strength']))
        adjusted['min_score'] = max(0.35, min(0.60, adjusted['min_score']))
        
        return adjusted
    
    def get_adjustment_summary(self, original: Dict, adjusted: Dict) -> str:
        """Genera resumen de ajustes para logging"""
        changes = []
        for key in original:
            if abs(original[key] - adjusted[key]) > 0.01:
                direction = "↓" if adjusted[key] < original[key] else "↑"
                changes.append(f"{key}: {original[key]:.2f} {direction} {adjusted[key]:.2f}")
        
        if not changes:
            return "Sin ajustes"
        
        return " | ".join(changes)
