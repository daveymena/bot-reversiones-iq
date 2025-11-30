"""
Modelos Matemáticos y Estadísticos Avanzados para Trading
Incluye: Fibonacci, Hurst Exponent, Z-Score, Kelly Criterion
"""
import pandas as pd
import numpy as np

class MathModels:
    def __init__(self):
        pass

    def calculate_fibonacci_levels(self, df, lookback=50):
        """
        Calcula niveles de retroceso de Fibonacci basados en el último High/Low significativo
        """
        if len(df) < lookback:
            return None
            
        recent_data = df.iloc[-lookback:]
        max_price = recent_data['high'].max()
        min_price = recent_data['low'].min()
        diff = max_price - min_price
        
        levels = {
            '0.0': max_price,
            '0.236': max_price - 0.236 * diff,
            '0.382': max_price - 0.382 * diff,
            '0.5': max_price - 0.5 * diff,
            '0.618': max_price - 0.618 * diff,
            '0.786': max_price - 0.786 * diff,
            '1.0': min_price
        }
        
        return levels

    def get_fibonacci_proximity(self, current_price, levels, threshold=0.0005):
        """
        Verifica si el precio está cerca de algún nivel de Fibonacci
        """
        if not levels:
            return None
            
        for level_name, level_price in levels.items():
            if abs(current_price - level_price) < (current_price * threshold):
                return {
                    'level': level_name,
                    'price': level_price,
                    'distance': abs(current_price - level_price)
                }
        return None

    def calculate_hurst_exponent(self, price_series, max_lag=20):
        """
        Calcula el Exponente de Hurst para determinar el régimen de mercado
        H < 0.5: Mean Reverting (Rango)
        H = 0.5: Random Walk (Aleatorio)
        H > 0.5: Trending (Tendencia)
        """
        try:
            lags = range(2, max_lag)
            tau = [np.sqrt(np.std(np.subtract(price_series[lag:], price_series[:-lag]))) for lag in lags]
            poly = np.polyfit(np.log(lags), np.log(tau), 1)
            return poly[0] * 2.0
        except:
            return 0.5

    def calculate_z_score(self, series, window=20):
        """
        Calcula el Z-Score para detectar anomalías estadísticas
        Z > 2: Estadísticamente caro (Venta)
        Z < -2: Estadísticamente barato (Compra)
        """
        if len(series) < window:
            return 0
            
        mean = series.rolling(window=window).mean().iloc[-1]
        std = series.rolling(window=window).std().iloc[-1]
        
        if std == 0:
            return 0
            
        current_value = series.iloc[-1]
        z_score = (current_value - mean) / std
        return z_score

    def kelly_criterion(self, win_rate, payout_ratio):
        """
        Calcula el porcentaje de capital a arriesgar según Kelly
        f* = (bp - q) / b
        b = payout ratio (e.g. 0.85 for 85%)
        p = win probability
        q = loss probability (1-p)
        """
        if payout_ratio <= 0:
            return 0
            
        q = 1 - win_rate
        f = (payout_ratio * win_rate - q) / payout_ratio
        return max(0, f)  # No devolver negativos

    def analyze_market_regime(self, df):
        """
        Analiza el régimen de mercado usando matemáticas
        """
        if len(df) < 50:
            return {'regime': 'UNKNOWN', 'quality': 0}
            
        # 1. Hurst Exponent
        hurst = self.calculate_hurst_exponent(df['close'].values)
        
        # 2. Volatility (ATR relativo)
        if 'atr' not in df.columns:
            import ta
            df['atr'] = ta.volatility.AverageTrueRange(df['high'], df['low'], df['close']).average_true_range()
            
        rel_volatility = df['atr'].iloc[-1] / df['close'].iloc[-1]
        
        regime = 'RANDOM'
        quality = 0.5
        
        if hurst > 0.6:
            regime = 'TRENDING'
            quality = hurst
        elif hurst < 0.4:
            regime = 'MEAN_REVERTING' # Rango
            quality = 1 - hurst
            
        return {
            'regime': regime,
            'hurst': hurst,
            'volatility': rel_volatility,
            'quality': quality
        }
