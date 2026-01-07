"""
🔄 ESTRATEGIA SMART REVERSAL
Ideal para mercados laterales o canales de tendencia.
Identifica agotamiento en niveles de soporte/resistencia y opera la reversión.
"""
import pandas as pd
import numpy as np

class SmartReversalStrategy:
    def __init__(self):
        pass

    def calculate_indicators(self, df):
        """Asegura que los indicadores necesarios estén presentes"""
        # RSI ya viene del FeatureEngineer, pero por si acaso:
        if 'rsi' not in df.columns:
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['rsi'] = 100 - (100 / (1 + rs))
        
        # Bandas de Bollinger para volatilidad y límites
        if 'bb_high' not in df.columns:
            sma = df['close'].rolling(window=20).mean()
            std = df['close'].rolling(window=20).std()
            df['bb_high'] = sma + (std * 2)
            df['bb_low'] = sma - (std * 2)
        
        return df

    def find_levels(self, df, window=20):
        """Identifica niveles locales de soporte y resistencia"""
        recent = df.tail(window)
        resistance = recent['high'].max()
        support = recent['low'].min()
        return support, resistance

    def analyze(self, df):
        """Analiza el mercado para buscar reversiones"""
        if len(df) < 50:
            return {'action': 'WAIT', 'confidence': 0, 'reason': 'Datos insuficientes'}

        df = self.calculate_indicators(df)
        last_candle = df.iloc[-1]
        prev_candle = df.iloc[-2]
        
        current_price = last_candle['close']
        rsi = last_candle['rsi']
        support, resistance = self.find_levels(df)
        
        # --- LÓGICA PARA CALL (Reversión al Alza) ---
        # 1. Precio cerca o debajo del soporte o banda inferior
        at_bottom = current_price <= support * 1.0001 or current_price <= last_candle['bb_low']
        # 2. RSI en sobreventa (o cerca)
        oversold = rsi < 35
        # 3. Vela de rechazo (mecha inferior larga o cambio de color)
        rejection_low = (last_candle['low'] < last_candle['open']) and (abs(last_candle['low'] - min(last_candle['open'], last_candle['close'])) > abs(last_candle['open'] - last_candle['close']))
        
        if at_bottom and oversold:
            confidence = 60
            if rejection_low: confidence += 20
            if rsi < 30: confidence += 10
            
            return {
                'action': 'CALL',
                'confidence': min(confidence, 95),
                'strategy': 'Smart Reversal (Alcista)',
                'reason': f'Reversión en soporte {support:.5f} con RSI {rsi:.1f}',
                'details': {
                    'price': current_price,
                    'support': support,
                    'rsi': rsi,
                    'bb_low': last_candle['bb_low']
                },
                'expiration': 120 # 2 minutos para el rebote
            }

        # --- LÓGICA PARA PUT (Reversión a la Baja) ---
        # 1. Precio cerca o arriba de la resistencia o banda superior
        at_top = current_price >= resistance * 0.9999 or current_price >= last_candle['bb_high']
        # 2. RSI en sobrecompra (o cerca)
        overbought = rsi > 65
        # 3. Vela de rechazo (mecha superior larga)
        rejection_high = (last_candle['high'] > last_candle['open']) and (abs(last_candle['high'] - max(last_candle['open'], last_candle['close'])) > abs(last_candle['open'] - last_candle['close']))
        
        if at_top and overbought:
            confidence = 60
            if rejection_high: confidence += 20
            if rsi > 70: confidence += 10
            
            return {
                'action': 'PUT',
                'confidence': min(confidence, 95),
                'strategy': 'Smart Reversal (Bajista)',
                'reason': f'Reversión en resistencia {resistance:.5f} con RSI {rsi:.1f}',
                'details': {
                    'price': current_price,
                    'resistance': resistance,
                    'rsi': rsi,
                    'bb_high': last_candle['bb_high']
                },
                'expiration': 120 # 2 minutos
            }

        return {'action': 'WAIT', 'confidence': 0, 'reason': 'No hay condiciones de reversión'}
