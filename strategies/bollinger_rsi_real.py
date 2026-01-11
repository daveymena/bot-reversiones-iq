"""
🎯 ESTRATEGIA BOLLINGER + RSI (Patrón de Entradas Reales)
Basada en análisis de imágenes de entradas ganadoras del Google Drive
"""
import pandas as pd
import numpy as np

class BollingerRSIStrategy:
    """
    Estrategia de reversión en extremos usando:
    - Bandas de Bollinger (20, 2)
    - RSI (14)
    - Patrones de velas
    - MACD (confirmación)
    
    Basada en patrones reales de entradas ganadoras
    """
    
    def __init__(self):
        self.name = "Bollinger+RSI Reversal"
        
    def calculate_indicators(self, df):
        """Calcula todos los indicadores necesarios"""
        # Bandas de Bollinger (20, 2)
        if 'bb_high' not in df.columns or 'bb_mid' not in df.columns or 'bb_low' not in df.columns:
            sma = df['close'].rolling(window=20).mean()
            std = df['close'].rolling(window=20).std()
            df['bb_high'] = sma + (std * 2)
            df['bb_mid'] = sma
            df['bb_low'] = sma - (std * 2)
        
        # RSI (14)
        if 'rsi' not in df.columns:
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD (12, 26, 9)
        if 'macd' not in df.columns:
            exp1 = df['close'].ewm(span=12, adjust=False).mean()
            exp2 = df['close'].ewm(span=26, adjust=False).mean()
            df['macd'] = exp1 - exp2
            df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
            df['macd_hist'] = df['macd'] - df['macd_signal']
        
        return df
    
    def analyze(self, df):
        """
        Analiza el mercado buscando el patrón exacto de las imágenes
        """
        try:
            if len(df) < 50:
                return {'action': 'WAIT', 'confidence': 0, 'reason': 'Datos insuficientes'}
            
            df = self.calculate_indicators(df)
            last_candle = df.iloc[-1]
            prev_candle = df.iloc[-2]
            
            current_price = last_candle['close']
            rsi = last_candle['rsi']
            bb_high = last_candle['bb_high']
            bb_low = last_candle['bb_low']
            bb_mid = last_candle['bb_mid']
            
            # --- ANÁLISIS PARA CALL (Compra en Banda Inferior) ---
            call_score = 0
            call_reasons = []
            
            # 1. Precio tocó/perforó banda inferior
            touched_lower = current_price <= bb_low * 1.001  # Tolerancia 0.1%
            if touched_lower:
                call_score += 25
                call_reasons.append(f"Precio en banda inferior ({bb_low:.5f})")
            
            # 2. RSI en sobreventa EXTREMA (≤30)
            if rsi <= 30:
                call_score += 30
                call_reasons.append(f"RSI sobreventa extrema ({rsi:.1f})")
                if rsi <= 25:
                    call_score += 10  # Bonus por RSI muy bajo
                    call_reasons.append("RSI crítico (<25)")
            
            # 3. Patrón de vela: Rebote confirmado
            candle_is_bullish = last_candle['close'] > last_candle['open']
            prev_was_bearish = prev_candle['close'] < prev_candle['open']
            
            # Calcular mechas
            candle_range = last_candle['high'] - last_candle['low']
            lower_wick = min(last_candle['open'], last_candle['close']) - last_candle['low']
            
            if candle_range > 0:
                lower_wick_ratio = lower_wick / candle_range
                
                # Mecha inferior larga (>40% del rango)
                if lower_wick_ratio > 0.4:
                    call_score += 20
                    call_reasons.append(f"Mecha inferior larga ({lower_wick_ratio*100:.0f}%)")
                
                # Vela alcista después de bajista
                if candle_is_bullish and prev_was_bearish:
                    call_score += 15
                    call_reasons.append("Cambio de tendencia confirmado")
            
            # 4. MACD confirmando (cruce alcista)
            macd_bullish = last_candle['macd'] > last_candle['macd_signal']
            macd_prev_bearish = prev_candle['macd'] < prev_candle['macd_signal']
            
            if macd_bullish:
                call_score += 10
                call_reasons.append("MACD alcista")
                if macd_prev_bearish:  # Cruce reciente
                    call_score += 10
                    call_reasons.append("MACD cruzó al alza")
            
            # --- ANÁLISIS PARA PUT (Venta en Banda Superior) ---
            put_score = 0
            put_reasons = []
            
            # 1. Precio tocó/perforó banda superior
            touched_upper = current_price >= bb_high * 0.999  # Tolerancia 0.1%
            if touched_upper:
                put_score += 25
                put_reasons.append(f"Precio en banda superior ({bb_high:.5f})")
            
            # 2. RSI en sobrecompra EXTREMA (≥70)
            if rsi >= 70:
                put_score += 30
                put_reasons.append(f"RSI sobrecompra extrema ({rsi:.1f})")
                if rsi >= 75:
                    put_score += 10  # Bonus por RSI muy alto
                    put_reasons.append("RSI crítico (>75)")
            
            # 3. Patrón de vela: Rechazo confirmado
            candle_is_bearish = last_candle['close'] < last_candle['open']
            prev_was_bullish = prev_candle['close'] > prev_candle['open']
            
            # Calcular mechas
            upper_wick = last_candle['high'] - max(last_candle['open'], last_candle['close'])
            candle_range = last_candle['high'] - last_candle['low']
            
            if candle_range > 0:
                upper_wick_ratio = upper_wick / candle_range
                
                # Mecha superior larga (>40% del rango)
                if upper_wick_ratio > 0.4:
                    put_score += 20
                    put_reasons.append(f"Mecha superior larga ({upper_wick_ratio*100:.0f}%)")
                
                # Vela bajista después de alcista
                if candle_is_bearish and prev_was_bullish:
                    put_score += 15
                    put_reasons.append("Cambio de tendencia confirmado")
            
            # 4. MACD confirmando (cruce bajista)
            macd_bearish = last_candle['macd'] < last_candle['macd_signal']
            macd_prev_bullish = prev_candle['macd'] > prev_candle['macd_signal']
            
            if macd_bearish:
                put_score += 10
                put_reasons.append("MACD bajista")
                if macd_prev_bullish:  # Cruce reciente
                    put_score += 10
                    put_reasons.append("MACD cruzó a la baja")
            
            # --- DECISIÓN FINAL ---
            # Solo operar si el score es >= 75 (al menos 4/5 condiciones)
            
            if call_score >= 75 and call_score > put_score:
                return {
                    'action': 'CALL',
                    'confidence': min(call_score, 95),
                    'strategy': 'Bollinger+RSI Reversal (Alcista)',
                    'reason': ' | '.join(call_reasons),
                    'details': {
                        'price': current_price,
                        'rsi': rsi,
                        'bb_low': bb_low,
                        'bb_mid': bb_mid,
                        'bb_high': bb_high,
                        'macd': last_candle['macd'],
                        'score': call_score
                    },
                    'expiration': 180  # 3 minutos
                }
            
            elif put_score >= 75 and put_score > call_score:
                return {
                    'action': 'PUT',
                    'confidence': min(put_score, 95),
                    'strategy': 'Bollinger+RSI Reversal (Bajista)',
                    'reason': ' | '.join(put_reasons),
                    'details': {
                        'price': current_price,
                        'rsi': rsi,
                        'bb_low': bb_low,
                        'bb_mid': bb_mid,
                        'bb_high': bb_high,
                        'macd': last_candle['macd'],
                        'score': put_score
                    },
                    'expiration': 180  # 3 minutos
                }
            
            else:
                # No cumple las condiciones mínimas
                max_score = max(call_score, put_score)
                return {
                    'action': 'WAIT',
                    'confidence': max_score,
                    'reason': f'Score insuficiente ({max_score}/100, mínimo 75)'
                }
                
        except Exception as e:
            # Si hay cualquier error, retornar WAIT para no detener el bot
            print(f"❌ Error en BollingerRSIStrategy: {str(e)}")
            return {
                'action': 'WAIT',
                'confidence': 0,
                'reason': f'Error en análisis: {str(e)}'
            }
