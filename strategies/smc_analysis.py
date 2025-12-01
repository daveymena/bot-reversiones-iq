"""
Smart Money Concepts (SMC) Analysis
Detecta patrones institucionales: Liquidity Sweeps, BOS, CHoCH
"""
import pandas as pd
import numpy as np

class SMCAnalysis:
    def __init__(self):
        pass
    
    def detect_liquidity_sweep(self, df, lookback=20):
        """
        Detecta toma de liquidez (liquidity sweep)
        Ocurre cuando el precio toca un high/low reciente y revierte
        
        Returns:
            dict: {
                'sweep_detected': bool,
                'sweep_type': 'bullish' or 'bearish',
                'sweep_level': float,
                'confidence': float
            }
        """
        if len(df) < lookback:
            return {'sweep_detected': False}
        
        recent_df = df.tail(lookback)
        last_candle = df.iloc[-1]
        prev_candle = df.iloc[-2]
        
        # Buscar highs y lows recientes
        recent_high = recent_df['high'].max()
        recent_low = recent_df['low'].min()
        
        # Bullish Sweep: Precio toca low reciente y revierte alcista
        if last_candle['low'] <= recent_low and last_candle['close'] > last_candle['open']:
            # Confirmar que hubo reversión (vela alcista después de tocar low)
            if prev_candle['close'] < prev_candle['open']:  # Vela bajista previa
                return {
                    'sweep_detected': True,
                    'sweep_type': 'bullish',
                    'sweep_level': recent_low,
                    'confidence': 0.75
                }
        
        # Bearish Sweep: Precio toca high reciente y revierte bajista
        if last_candle['high'] >= recent_high and last_candle['close'] < last_candle['open']:
            if prev_candle['close'] > prev_candle['open']:  # Vela alcista previa
                return {
                    'sweep_detected': True,
                    'sweep_type': 'bearish',
                    'sweep_level': recent_high,
                    'confidence': 0.75
                }
        
        return {'sweep_detected': False}
    
    def detect_change_of_character(self, df, lookback=30):
        """
        Detecta CHoCH (Change of Character) o BOS (Break of Structure)
        Cambio de tendencia institucional
        
        Returns:
            dict: {
                'choch_detected': bool,
                'direction': 'bullish' or 'bearish',
                'confidence': float
            }
        """
        if len(df) < lookback:
            return {'choch_detected': False}
        
        recent_df = df.tail(lookback)
        
        # Identificar puntos de swing (highs y lows)
        highs = []
        lows = []
        
        for i in range(2, len(recent_df) - 2):
            # Swing high: vela con high mayor a las 2 velas antes y después
            if (recent_df.iloc[i]['high'] > recent_df.iloc[i-1]['high'] and
                recent_df.iloc[i]['high'] > recent_df.iloc[i-2]['high'] and
                recent_df.iloc[i]['high'] > recent_df.iloc[i+1]['high'] and
                recent_df.iloc[i]['high'] > recent_df.iloc[i+2]['high']):
                highs.append((i, recent_df.iloc[i]['high']))
            
            # Swing low
            if (recent_df.iloc[i]['low'] < recent_df.iloc[i-1]['low'] and
                recent_df.iloc[i]['low'] < recent_df.iloc[i-2]['low'] and
                recent_df.iloc[i]['low'] < recent_df.iloc[i+1]['low'] and
                recent_df.iloc[i]['low'] < recent_df.iloc[i+2]['low']):
                lows.append((i, recent_df.iloc[i]['low']))
        
        if len(highs) < 2 or len(lows) < 2:
            return {'choch_detected': False}
        
        # Bullish CHoCH: Rompe un high previo después de hacer un low más alto
        last_high = max(highs, key=lambda x: x[0])
        second_last_high = sorted(highs, key=lambda x: x[0])[-2] if len(highs) > 1 else None
        
        if second_last_high and df.iloc[-1]['close'] > last_high[1]:
            # Precio rompió high previo
            if len(lows) > 0:
                last_low = max(lows, key=lambda x: x[0])
                if last_low[0] > second_last_high[0]:  # Low más reciente que el high roto
                    return {
                        'choch_detected': True,
                        'direction': 'bullish',
                        'confidence': 0.8
                    }
        
        # Bearish CHoCH: Rompe un low previo después de hacer un high más bajo
        last_low = max(lows, key=lambda x: x[0])
        second_last_low = sorted(lows, key=lambda x: x[0])[-2] if len(lows) > 1 else None
        
        if second_last_low and df.iloc[-1]['close'] < last_low[1]:
            if len(highs) > 0:
                last_high = max(highs, key=lambda x: x[0])
                if last_high[0] > second_last_low[0]:
                    return {
                        'choch_detected': True,
                        'direction': 'bearish',
                        'confidence': 0.8
                    }
        
        return {'choch_detected': False}
    
    def detect_confirmation_pattern(self, df):
        """
        Detecta patrones de confirmación antes de entrar
        - Vela de engulfing
        - Pinchazo con mecha larga
        - Momentum fuerte
        
        Returns:
            dict: {
                'confirmed': bool,
                'pattern': str,
                'confidence': float
            }
        """
        if len(df) < 3:
            return {'confirmed': False}
        
        last = df.iloc[-1]
        prev = df.iloc[-2]
        
        # Bullish Engulfing
        if (prev['close'] < prev['open'] and  # Vela bajista previa
            last['close'] > last['open'] and  # Vela alcista actual
            last['close'] > prev['open'] and  # Cierre actual > apertura previa
            last['open'] < prev['close']):    # Apertura actual < cierre previo
            return {
                'confirmed': True,
                'pattern': 'bullish_engulfing',
                'confidence': 0.85
            }
        
        # Bearish Engulfing
        if (prev['close'] > prev['open'] and
            last['close'] < last['open'] and
            last['close'] < prev['open'] and
            last['open'] > prev['close']):
            return {
                'confirmed': True,
                'pattern': 'bearish_engulfing',
                'confidence': 0.85
            }
        
        # Hammer (Bullish Rejection)
        body = abs(last['close'] - last['open'])
        lower_wick = min(last['close'], last['open']) - last['low']
        upper_wick = last['high'] - max(last['close'], last['open'])
        
        if lower_wick > body * 2 and upper_wick < body * 0.5:
            return {
                'confirmed': True,
                'pattern': 'hammer',
                'confidence': 0.75
            }
        
        # Shooting Star (Bearish Rejection)
        if upper_wick > body * 2 and lower_wick < body * 0.5:
            return {
                'confirmed': True,
                'pattern': 'shooting_star',
                'confidence': 0.75
            }
        
        return {'confirmed': False}
    
    def analyze_smc_setup(self, df):
        """
        Análisis completo SMC
        Combina liquidity sweep + CHoCH + confirmation
        
        Returns:
            dict: {
                'valid_setup': bool,
                'direction': 'CALL' or 'PUT',
                'confidence': float,
                'reasons': list
            }
        """
        sweep = self.detect_liquidity_sweep(df)
        choch = self.detect_change_of_character(df)
        confirmation = self.detect_confirmation_pattern(df)
        
        reasons = []
        confidence = 0
        direction = None
        
        # Bullish Setup
        if sweep.get('sweep_detected') and sweep['sweep_type'] == 'bullish':
            confidence += 0.3
            reasons.append("Liquidity sweep alcista")
            direction = 'CALL'
        
        if choch.get('choch_detected') and choch['direction'] == 'bullish':
            confidence += 0.3
            reasons.append("CHoCH alcista")
            if direction is None:
                direction = 'CALL'
        
        if confirmation.get('confirmed') and 'bullish' in confirmation['pattern']:
            confidence += 0.4
            reasons.append(f"Confirmación: {confirmation['pattern']}")
            if direction is None:
                direction = 'CALL'
        
        # Bearish Setup
        if sweep.get('sweep_detected') and sweep['sweep_type'] == 'bearish':
            confidence += 0.3
            reasons.append("Liquidity sweep bajista")
            direction = 'PUT'
        
        if choch.get('choch_detected') and choch['direction'] == 'bearish':
            confidence += 0.3
            reasons.append("CHoCH bajista")
            if direction is None:
                direction = 'PUT'
        
        if confirmation.get('confirmed') and 'bearish' in confirmation['pattern']:
            confidence += 0.4
            reasons.append(f"Confirmación: {confirmation['pattern']}")
            if direction is None:
                direction = 'PUT'
        
        # Requiere al menos 2 factores para ser válido
        valid_setup = len(reasons) >= 2 and confidence >= 0.5
        
        return {
            'valid_setup': valid_setup,
            'direction': direction,
            'confidence': min(confidence, 1.0),
            'reasons': reasons
        }
