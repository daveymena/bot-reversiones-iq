"""
Filtros Inteligentes basados en Datos Históricos
Consulta la base de datos para tomar decisiones informadas
"""
from database.db_manager import db
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

class IntelligentFilters:
    """
    Filtros que aprenden de datos históricos para mejorar decisiones
    """
    
    def __init__(self):
        self.min_pattern_win_rate = 55.0  # Mínimo 55% win rate
        self.min_pattern_occurrences = 10  # Mínimo 10 ocurrencias para confiar
        self.min_hourly_win_rate = 50.0  # Mínimo 50% win rate por hora
        
    def should_trade(self, asset: str, pattern_type: Optional[str] = None, 
                    current_conditions: Optional[Dict] = None) -> Tuple[bool, str]:
        """
        Decide si se debe operar basándose en datos históricos
        
        Returns:
            (should_trade, reason)
        """
        
        # 1. Verificar rendimiento del activo
        asset_approved, asset_reason = self._check_asset_performance(asset)
        if not asset_approved:
            return False, asset_reason
        
        # 2. Verificar rendimiento del patrón
        if pattern_type:
            pattern_approved, pattern_reason = self._check_pattern_performance(
                pattern_type, asset
            )
            if not pattern_approved:
                return False, pattern_reason
        
        # 3. Verificar hora del día
        hour_approved, hour_reason = self._check_hourly_performance()
        if not hour_approved:
            return False, hour_reason
        
        # 4. Verificar errores comunes
        if current_conditions:
            error_approved, error_reason = self._check_common_errors(current_conditions)
            if not error_approved:
                return False, error_reason
        
        # 5. Verificar racha reciente
        streak_approved, streak_reason = self._check_recent_streak(asset)
        if not streak_approved:
            return False, streak_reason
        
        return True, "✅ Todas las validaciones pasadas"
    
    def _check_asset_performance(self, asset: str) -> Tuple[bool, str]:
        """Verifica el rendimiento histórico del activo"""
        try:
            stats = db.get_performance_stats(days=30, asset=asset)
            
            if not stats or stats.get('total_trades', 0) == 0:
                # No hay datos suficientes, permitir operar
                return True, f"Sin historial para {asset}"
            
            win_rate = stats.get('win_rate', 0)
            total_trades = stats.get('total_trades', 0)
            
            if total_trades < 10:
                # Pocos datos, permitir operar
                return True, f"{asset}: Solo {total_trades} trades históricos"
            
            if win_rate < 45:
                return False, f"❌ {asset} tiene win rate bajo: {win_rate}% (últimos 30 días)"
            
            return True, f"✅ {asset}: {win_rate}% win rate ({total_trades} trades)"
            
        except Exception as e:
            # Si hay error consultando BD, permitir operar
            print(f"[WARNING] Error consultando rendimiento de activo: {e}")
            return True, "Sin datos históricos disponibles"
    
    def _check_pattern_performance(self, pattern_type: str, asset: str) -> Tuple[bool, str]:
        """Verifica el rendimiento histórico del patrón"""
        try:
            patterns = db.get_best_patterns(asset=asset, min_occurrences=5)
            
            # Buscar el patrón específico
            pattern_stats = None
            for p in patterns:
                if p['pattern_type'] == pattern_type:
                    pattern_stats = p
                    break
            
            if not pattern_stats:
                # No hay datos del patrón, permitir operar
                return True, f"Sin historial para patrón {pattern_type}"
            
            win_rate = pattern_stats.get('win_rate', 0)
            occurrences = pattern_stats.get('total_occurrences', 0)
            
            if occurrences < self.min_pattern_occurrences:
                # Pocos datos, permitir operar
                return True, f"Patrón {pattern_type}: Solo {occurrences} ocurrencias"
            
            if win_rate < self.min_pattern_win_rate:
                return False, f"❌ Patrón {pattern_type} tiene win rate bajo: {win_rate}%"
            
            return True, f"✅ Patrón {pattern_type}: {win_rate}% win rate"
            
        except Exception as e:
            print(f"[WARNING] Error consultando rendimiento de patrón: {e}")
            return True, "Sin datos de patrones disponibles"
    
    def _check_hourly_performance(self) -> Tuple[bool, str]:
        """Verifica el rendimiento en la hora actual"""
        try:
            hourly_stats = db.get_performance_by_hour()
            
            if not hourly_stats:
                return True, "Sin datos horarios"
            
            current_hour = datetime.now().hour
            
            # Buscar estadísticas de la hora actual
            hour_stats = None
            for h in hourly_stats:
                if int(h['hour']) == current_hour:
                    hour_stats = h
                    break
            
            if not hour_stats:
                return True, f"Sin datos para hora {current_hour}"
            
            win_rate = hour_stats.get('win_rate', 0)
            total_trades = hour_stats.get('total_trades', 0)
            
            if total_trades < 5:
                return True, f"Hora {current_hour}: Solo {total_trades} trades históricos"
            
            if win_rate < self.min_hourly_win_rate:
                return False, f"❌ Hora {current_hour} tiene win rate bajo: {win_rate}%"
            
            return True, f"✅ Hora {current_hour}: {win_rate}% win rate"
            
        except Exception as e:
            print(f"[WARNING] Error consultando rendimiento horario: {e}")
            return True, "Sin datos horarios disponibles"
    
    def _check_common_errors(self, current_conditions: Dict) -> Tuple[bool, str]:
        """Verifica si las condiciones actuales coinciden con errores comunes"""
        try:
            common_errors = db.get_common_errors(limit=10)
            
            if not common_errors:
                return True, "Sin errores históricos"
            
            # Verificar si las condiciones actuales son similares a errores pasados
            for error in common_errors:
                if error['occurrences'] < 3:
                    continue  # Ignorar errores poco frecuentes
                
                error_conditions = error.get('common_conditions', {})
                
                # Comparar condiciones (simplificado)
                if self._conditions_match(current_conditions, error_conditions):
                    return False, f"❌ Condiciones similares a error: {error['error_type']}"
            
            return True, "✅ No coincide con errores conocidos"
            
        except Exception as e:
            print(f"[WARNING] Error consultando errores comunes: {e}")
            return True, "Sin datos de errores disponibles"
    
    def _check_recent_streak(self, asset: str) -> Tuple[bool, str]:
        """Verifica la racha reciente en el activo"""
        try:
            recent_trades = db.get_recent_trades(limit=5, asset=asset)
            
            if not recent_trades or len(recent_trades) < 3:
                return True, "Sin racha reciente"
            
            # Contar pérdidas consecutivas
            consecutive_losses = 0
            for trade in recent_trades:
                if trade['result'] == 'loss':
                    consecutive_losses += 1
                else:
                    break
            
            if consecutive_losses >= 3:
                return False, f"❌ {consecutive_losses} pérdidas consecutivas en {asset}"
            
            return True, f"✅ Racha aceptable en {asset}"
            
        except Exception as e:
            print(f"[WARNING] Error consultando racha reciente: {e}")
            return True, "Sin datos de racha disponibles"
    
    def _conditions_match(self, current: Dict, historical: Dict, threshold: float = 0.8) -> bool:
        """
        Compara condiciones actuales con históricas
        Retorna True si son similares (>80% de coincidencia)
        """
        if not historical:
            return False
        
        matches = 0
        total = 0
        
        # Comparar indicadores clave
        key_indicators = ['rsi', 'macd', 'volatility', 'trend']
        
        for indicator in key_indicators:
            if indicator in current and indicator in historical:
                total += 1
                current_val = current[indicator]
                historical_val = historical[indicator]
                
                # Para valores numéricos, verificar si están en rango similar
                if isinstance(current_val, (int, float)) and isinstance(historical_val, (int, float)):
                    # Considerar match si están dentro del 20% de diferencia
                    if abs(current_val - historical_val) / max(abs(historical_val), 1) < 0.2:
                        matches += 1
                # Para valores string, comparar directamente
                elif current_val == historical_val:
                    matches += 1
        
        if total == 0:
            return False
        
        similarity = matches / total
        return similarity >= threshold
    
    def get_recommended_confidence(self, asset: str) -> float:
        """
        Recomienda nivel de confianza mínimo basado en rendimiento histórico
        """
        try:
            stats = db.get_performance_stats(days=30, asset=asset)
            
            if not stats or stats.get('total_trades', 0) < 10:
                return 0.65  # Confianza por defecto
            
            win_rate = stats.get('win_rate', 0)
            
            # Ajustar confianza basándose en win rate
            if win_rate >= 70:
                return 0.55  # Relajar confianza si va bien
            elif win_rate >= 60:
                return 0.65  # Confianza normal
            elif win_rate >= 50:
                return 0.75  # Aumentar confianza si va regular
            else:
                return 0.85  # Muy alta confianza si va mal
                
        except Exception as e:
            print(f"[WARNING] Error calculando confianza recomendada: {e}")
            return 0.65
    
    def get_statistics_summary(self) -> Dict:
        """Obtiene resumen de estadísticas para mostrar en GUI"""
        try:
            stats_7d = db.get_performance_stats(days=7)
            stats_30d = db.get_performance_stats(days=30)
            best_patterns = db.get_best_patterns(min_occurrences=10)
            common_errors = db.get_common_errors(limit=5)
            
            return {
                'last_7_days': stats_7d,
                'last_30_days': stats_30d,
                'best_patterns': best_patterns[:5],
                'common_errors': common_errors,
                'total_trades_db': stats_30d.get('total_trades', 0) if stats_30d else 0
            }
        except Exception as e:
            print(f"[WARNING] Error obteniendo resumen: {e}")
            return {}
