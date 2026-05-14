"""
Feature Engineer — Extracción de features avanzados para ML
Convierte el estado del mercado en 100+ features numéricos
"""
import numpy as np
import pandas as pd
from typing import Dict, List
from datetime import datetime


class FeatureEngineer:
    """
    Extrae features del estado del mercado para alimentar modelos ML
    """
    
    def __init__(self):
        self.feature_names = []
        self._build_feature_names()
    
    def extract(self, market_state: Dict) -> np.ndarray:
        """
        Extrae todos los features del estado del mercado
        
        Args:
            market_state: Dict con df_m1, df_m5, zone, context, pattern, etc.
        
        Returns:
            Array numpy con ~100 features normalizados
        """
        features = []
        
        # 1. Features de zona (10 features)
        features.extend(self._zone_features(market_state.get('zone')))
        
        # 2. Features de patrón (15 features)
        features.extend(self._pattern_features(market_state.get('pattern')))
        
        # 3. Features de indicadores técnicos (30 features)
        features.extend(self._technical_indicators(
            market_state.get('df_m1'),
            market_state.get('df_m5'),
            market_state.get('df_m15')
        ))
        
        # 4. Features de contexto (20 features)
        features.extend(self._context_features(market_state.get('context')))
        
        # 5. Features de timing (10 features)
        features.extend(self._timing_features(market_state.get('timing')))
        
        # 6. Features de condiciones (25 features)
        features.extend(self._condition_features(market_state.get('conditions', {})))
        
        # 7. Features temporales (8 features)
        features.extend(self._temporal_features())
        
        # 8. Features de microestructura (12 features)
        features.extend(self._microstructure_features(market_state.get('df_m1')))
        
        return np.array(features, dtype=np.float32)
    
    def _zone_features(self, zone) -> List[float]:
        """Features relacionados con la zona"""
        if zone is None:
            return [0.0] * 10
        
        return [
            float(zone.strength),
            float(zone.touches),
            float(zone.hold_rate),
            float(zone.holds),
            float(zone.breaks),
            float(zone.avg_reaction_pips),
            1.0 if zone.zone_type == "support" else 0.0,
            1.0 if zone.zone_type == "resistance" else 0.0,
            1.0 if zone.touches >= 3 else 0.0,  # multi-TF
            float((datetime.now().timestamp() - zone.last_touch_ts) / 3600),  # horas desde último toque
        ]
    
    def _pattern_features(self, pattern: Dict) -> List[float]:
        """Features del patrón de vela"""
        if not pattern:
            return [0.0] * 15
        
        pattern_name = pattern.get('pattern', 'none')
        
        # One-hot encoding de patrones
        patterns = ['pin_bar', 'hammer', 'engulfing', 'star', 'doji', 'none']
        pattern_encoding = [1.0 if p in pattern_name else 0.0 for p in patterns]
        
        return pattern_encoding + [
            float(pattern.get('strength', 0)),
            1.0 if pattern.get('confirmed', False) else 0.0,
            1.0 if pattern.get('candle_confirmed', False) else 0.0,
            float(len(pattern.get('all_detected', []))),
            1.0 if pattern.get('used_closed_candle', False) else 0.0,
            float(pattern.get('signal_candle_info', {}).get('body_pct', 0)),
            float(pattern.get('signal_candle_info', {}).get('lower_wick_pct', 0)),
            float(pattern.get('signal_candle_info', {}).get('upper_wick_pct', 0)),
        ]
    
    def _technical_indicators(self, df_m1, df_m5, df_m15) -> List[float]:
        """Indicadores técnicos en múltiples timeframes"""
        features = []
        
        for df, name in [(df_m1, 'm1'), (df_m5, 'm5'), (df_m15, 'm15')]:
            if df is None or len(df) < 20:
                features.extend([0.0] * 10)
                continue
            
            # RSI
            rsi = self._calculate_rsi(df, 14)
            features.append(float(rsi))
            features.append(float(abs(rsi - 50)))  # distancia de neutral
            
            # MACD
            macd, signal, hist = self._calculate_macd(df)
            features.append(float(macd))
            features.append(float(hist))
            
            # Bollinger Bands
            bb_upper, bb_lower, bb_mid = self._calculate_bollinger(df)
            current_price = float(df.iloc[-1]['close'])
            bb_position = (current_price - bb_lower) / (bb_upper - bb_lower) if bb_upper > bb_lower else 0.5
            features.append(float(bb_position))
            
            # ATR (volatilidad)
            atr = self._calculate_atr(df, 14)
            features.append(float(atr))
            
            # ADX (fuerza de tendencia)
            adx = self._calculate_adx(df, 14)
            features.append(float(adx))
            
            # Momentum
            momentum = float(df.iloc[-1]['close']) / float(df.iloc[-10]['close']) - 1.0
            features.append(momentum)
            
            # Volume (si disponible)
            if 'volume' in df.columns:
                vol_ratio = float(df.iloc[-1]['volume']) / float(df['volume'].tail(20).mean())
                features.append(vol_ratio)
            else:
                features.append(1.0)
            
            # Tendencia (slope de MA20)
            ma20 = df['close'].tail(20).mean()
            ma20_prev = df['close'].tail(25).head(20).mean()
            trend_slope = (ma20 - ma20_prev) / ma20_prev if ma20_prev > 0 else 0.0
            features.append(float(trend_slope))
        
        return features
    
    def _context_features(self, context: Dict) -> List[float]:
        """Features del contexto de mercado"""
        if not context:
            return [0.0] * 20
        
        zone_ctx = context.get('zone_context', {})
        momentum = context.get('momentum', {})
        
        # Tendencia
        trend = context.get('dominant_trend', 'neutral')
        trend_encoding = [
            1.0 if trend == 'uptrend' else 0.0,
            1.0 if trend == 'downtrend' else 0.0,
            1.0 if trend == 'neutral' else 0.0,
        ]
        
        # Fase de mercado
        phase = context.get('market_phase', 'unknown')
        phase_encoding = [
            1.0 if phase == 'trending_up' else 0.0,
            1.0 if phase == 'trending_down' else 0.0,
            1.0 if phase == 'ranging' else 0.0,
            1.0 if phase == 'dead' else 0.0,
        ]
        
        return trend_encoding + phase_encoding + [
            float(zone_ctx.get('zone_strength', 0)),
            1.0 if zone_ctx.get('trend_aligned', False) else 0.0,
            float(zone_ctx.get('distance_to_zone', 0)),
            float(momentum.get('rsi_m1', 50)),
            float(momentum.get('rsi_m5', 50)),
            float(momentum.get('macd_hist', 0)),
            1.0 if momentum.get('bullish_divergence', False) else 0.0,
            1.0 if momentum.get('bearish_divergence', False) else 0.0,
            float(context.get('setup_quality', 0)),
            float(context.get('volatility', 0)),
            float(zone_ctx.get('approach_quality', 0)),
            1.0 if context.get('before_context', {}).get('approach') == 'falling_to_support' else 0.0,
            1.0 if context.get('before_context', {}).get('approach') == 'rising_to_resistance' else 0.0,
        ]
    
    def _timing_features(self, timing: Dict) -> List[float]:
        """Features de timing de entrada"""
        if not timing:
            return [0.0] * 10
        
        return [
            1.0 if timing.get('valid', False) else 0.0,
            1.0 if timing.get('zone_touched', False) else 0.0,
            float(timing.get('rejection_wick_pct', 0)),
            float(timing.get('distance_from_zone', 0)),
            1.0 if timing.get('issue') == 'zone_not_touched' else 0.0,
            1.0 if timing.get('issue') == 'late_entry' else 0.0,
            1.0 if timing.get('issue') == 'no_rejection_wick' else 0.0,
            0.0,  # reserved
            0.0,  # reserved
            0.0,  # reserved
        ]
    
    def _condition_features(self, conditions: Dict) -> List[float]:
        """Features de condiciones booleanas"""
        if not conditions:
            return [0.0] * 25
        
        # Convertir todas las condiciones a float
        return [
            1.0 if conditions.get('zone_strength_high', False) else 0.0,
            1.0 if conditions.get('zone_strength_medium', False) else 0.0,
            1.0 if conditions.get('zone_multi_tf', False) else 0.0,
            1.0 if conditions.get('zone_touch_3plus', False) else 0.0,
            1.0 if conditions.get('zone_hold_rate_high', False) else 0.0,
            1.0 if conditions.get('trend_aligned', False) else 0.0,
            1.0 if conditions.get('trend_strong', False) else 0.0,
            1.0 if conditions.get('counter_trend', False) else 0.0,
            1.0 if conditions.get('rsi_extreme', False) else 0.0,
            1.0 if conditions.get('rsi_oversold_sold', False) else 0.0,
            1.0 if conditions.get('rsi_overbought', False) else 0.0,
            1.0 if conditions.get('rsi_divergence', False) else 0.0,
            1.0 if conditions.get('pattern_strong', False) else 0.0,
            1.0 if conditions.get('has_any_pattern', False) else 0.0,
            1.0 if conditions.get('macd_cross', False) else 0.0,
            1.0 if conditions.get('macd_hist_turning', False) else 0.0,
            1.0 if conditions.get('approach_clean', False) else 0.0,
            1.0 if conditions.get('mtf_aligned', False) else 0.0,
            1.0 if conditions.get('market_phase_ranging', False) else 0.0,
            1.0 if conditions.get('market_phase_trending', False) else 0.0,
            1.0 if conditions.get('setup_quality_high', False) else 0.0,
            1.0 if conditions.get('rejection_visible', False) else 0.0,
            1.0 if conditions.get('candle_confirming', False) else 0.0,
            0.0,  # reserved
            0.0,  # reserved
        ]
    
    def _temporal_features(self) -> List[float]:
        """Features temporales (hora, día, sesión)"""
        now = datetime.now()
        hour = now.hour
        day_of_week = now.weekday()
        
        # Sesión de trading
        is_asia = 1.0 if 0 <= hour < 8 else 0.0
        is_europe = 1.0 if 8 <= hour < 16 else 0.0
        is_usa = 1.0 if 13 <= hour < 22 else 0.0
        is_overlap = 1.0 if 13 <= hour < 16 else 0.0  # Europa + USA
        
        return [
            float(hour) / 24.0,  # normalizado
            float(day_of_week) / 7.0,
            is_asia,
            is_europe,
            is_usa,
            is_overlap,
            1.0 if day_of_week < 5 else 0.0,  # día laboral
            1.0 if 9 <= hour <= 17 else 0.0,  # horario principal
        ]
    
    def _microstructure_features(self, df_m1) -> List[float]:
        """Features de microestructura de mercado"""
        if df_m1 is None or len(df_m1) < 10:
            return [0.0] * 12
        
        recent = df_m1.tail(10)
        
        # Ratio de velas alcistas/bajistas
        bullish_candles = sum(1 for _, row in recent.iterrows() if row['close'] > row['open'])
        bull_ratio = bullish_candles / len(recent)
        
        # Tamaño promedio de cuerpo
        avg_body = recent.apply(lambda row: abs(row['close'] - row['open']), axis=1).mean()
        
        # Tamaño promedio de rango
        avg_range = recent.apply(lambda row: row['high'] - row['low'], axis=1).mean()
        
        # Ratio cuerpo/rango
        body_range_ratio = avg_body / avg_range if avg_range > 0 else 0.5
        
        # Volatilidad reciente (std de returns)
        returns = recent['close'].pct_change().dropna()
        volatility = returns.std() if len(returns) > 0 else 0.0
        
        # Momentum de corto plazo
        short_momentum = (float(recent.iloc[-1]['close']) / float(recent.iloc[0]['close']) - 1.0)
        
        # Higher highs / Lower lows
        highs = recent['high'].values
        lows = recent['low'].values
        higher_highs = sum(1 for i in range(1, len(highs)) if highs[i] > highs[i-1])
        lower_lows = sum(1 for i in range(1, len(lows)) if lows[i] < lows[i-1])
        
        return [
            float(bull_ratio),
            float(avg_body),
            float(avg_range),
            float(body_range_ratio),
            float(volatility),
            float(short_momentum),
            float(higher_highs) / (len(highs) - 1) if len(highs) > 1 else 0.0,
            float(lower_lows) / (len(lows) - 1) if len(lows) > 1 else 0.0,
            float(recent['high'].max()),
            float(recent['low'].min()),
            float(recent['close'].mean()),
            float(recent['close'].std()),
        ]
    
    # ── Cálculo de indicadores técnicos ───────────────────────────────────────
    
    @staticmethod
    def _calculate_rsi(df: pd.DataFrame, period: int = 14) -> float:
        """Calcula RSI"""
        if len(df) < period + 1:
            return 50.0
        
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else 50.0
    
    @staticmethod
    def _calculate_macd(df: pd.DataFrame, fast=12, slow=26, signal=9):
        """Calcula MACD"""
        if len(df) < slow + signal:
            return 0.0, 0.0, 0.0
        
        ema_fast = df['close'].ewm(span=fast).mean()
        ema_slow = df['close'].ewm(span=slow).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal).mean()
        histogram = macd_line - signal_line
        
        return (
            float(macd_line.iloc[-1]),
            float(signal_line.iloc[-1]),
            float(histogram.iloc[-1])
        )
    
    @staticmethod
    def _calculate_bollinger(df: pd.DataFrame, period=20, std_dev=2):
        """Calcula Bollinger Bands"""
        if len(df) < period:
            mid = float(df['close'].mean())
            return mid, mid, mid
        
        mid = df['close'].rolling(window=period).mean()
        std = df['close'].rolling(window=period).std()
        upper = mid + (std * std_dev)
        lower = mid - (std * std_dev)
        
        return (
            float(upper.iloc[-1]),
            float(lower.iloc[-1]),
            float(mid.iloc[-1])
        )
    
    @staticmethod
    def _calculate_atr(df: pd.DataFrame, period=14) -> float:
        """Calcula Average True Range"""
        if len(df) < period + 1:
            return 0.0
        
        high = df['high']
        low = df['low']
        close = df['close'].shift(1)
        
        tr1 = high - low
        tr2 = abs(high - close)
        tr3 = abs(low - close)
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        
        return float(atr.iloc[-1]) if not pd.isna(atr.iloc[-1]) else 0.0
    
    @staticmethod
    def _calculate_adx(df: pd.DataFrame, period=14) -> float:
        """Calcula Average Directional Index"""
        if len(df) < period + 1:
            return 0.0
        
        high = df['high']
        low = df['low']
        close = df['close']
        
        plus_dm = high.diff()
        minus_dm = low.diff()
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm > 0] = 0
        
        tr = pd.concat([
            high - low,
            abs(high - close.shift(1)),
            abs(low - close.shift(1))
        ], axis=1).max(axis=1)
        
        atr = tr.rolling(window=period).mean()
        plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
        minus_di = 100 * (abs(minus_dm).rolling(window=period).mean() / atr)
        
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(window=period).mean()
        
        return float(adx.iloc[-1]) if not pd.isna(adx.iloc[-1]) else 0.0
    
    def _build_feature_names(self):
        """Construye lista de nombres de features para referencia"""
        self.feature_names = [
            # Zona (10)
            'zone_strength', 'zone_touches', 'zone_hold_rate', 'zone_holds',
            'zone_breaks', 'zone_avg_reaction', 'zone_is_support', 'zone_is_resistance',
            'zone_multi_tf', 'zone_hours_since_touch',
            
            # Patrón (15)
            'pattern_pin_bar', 'pattern_hammer', 'pattern_engulfing', 'pattern_star',
            'pattern_doji', 'pattern_none', 'pattern_strength', 'pattern_confirmed',
            'pattern_candle_confirmed', 'pattern_count', 'pattern_closed_candle',
            'pattern_body_pct', 'pattern_lower_wick', 'pattern_upper_wick', 'pattern_reserved',
            
            # Indicadores M1 (10)
            'm1_rsi', 'm1_rsi_dist', 'm1_macd', 'm1_macd_hist', 'm1_bb_position',
            'm1_atr', 'm1_adx', 'm1_momentum', 'm1_volume_ratio', 'm1_trend_slope',
            
            # Indicadores M5 (10)
            'm5_rsi', 'm5_rsi_dist', 'm5_macd', 'm5_macd_hist', 'm5_bb_position',
            'm5_atr', 'm5_adx', 'm5_momentum', 'm5_volume_ratio', 'm5_trend_slope',
            
            # Indicadores M15 (10)
            'm15_rsi', 'm15_rsi_dist', 'm15_macd', 'm15_macd_hist', 'm15_bb_position',
            'm15_atr', 'm15_adx', 'm15_momentum', 'm15_volume_ratio', 'm15_trend_slope',
            
            # Contexto (20)
            'trend_uptrend', 'trend_downtrend', 'trend_neutral',
            'phase_trending_up', 'phase_trending_down', 'phase_ranging', 'phase_dead',
            'ctx_zone_strength', 'ctx_trend_aligned', 'ctx_distance_to_zone',
            'ctx_rsi_m1', 'ctx_rsi_m5', 'ctx_macd_hist',
            'ctx_bullish_div', 'ctx_bearish_div', 'ctx_setup_quality',
            'ctx_volatility', 'ctx_approach_quality',
            'ctx_falling_to_support', 'ctx_rising_to_resistance',
            
            # Timing (10)
            'timing_valid', 'timing_zone_touched', 'timing_rejection_wick',
            'timing_distance', 'timing_not_touched', 'timing_late_entry',
            'timing_no_wick', 'timing_reserved1', 'timing_reserved2', 'timing_reserved3',
            
            # Condiciones (25)
            'cond_zone_high', 'cond_zone_medium', 'cond_zone_multi_tf',
            'cond_zone_3plus', 'cond_zone_hold_high', 'cond_trend_aligned',
            'cond_trend_strong', 'cond_counter_trend', 'cond_rsi_extreme',
            'cond_rsi_oversold', 'cond_rsi_overbought', 'cond_rsi_div',
            'cond_pattern_strong', 'cond_has_pattern', 'cond_macd_cross',
            'cond_macd_turning', 'cond_approach_clean', 'cond_mtf_aligned',
            'cond_phase_ranging', 'cond_phase_trending', 'cond_setup_high',
            'cond_rejection_visible', 'cond_candle_confirming',
            'cond_reserved1', 'cond_reserved2',
            
            # Temporal (8)
            'time_hour_norm', 'time_day_norm', 'time_asia', 'time_europe',
            'time_usa', 'time_overlap', 'time_weekday', 'time_main_hours',
            
            # Microestructura (12)
            'micro_bull_ratio', 'micro_avg_body', 'micro_avg_range',
            'micro_body_range_ratio', 'micro_volatility', 'micro_short_momentum',
            'micro_higher_highs', 'micro_lower_lows', 'micro_max_high',
            'micro_min_low', 'micro_mean_close', 'micro_std_close',
        ]
    
    def get_feature_count(self) -> int:
        """Retorna el número total de features"""
        return len(self.feature_names)
