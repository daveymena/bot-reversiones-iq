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
            
            # 4. Filtro de Tendencia (SMA 100)
            if 'sma_100' not in df.columns:
                df['sma_100'] = df['close'].rolling(window=100).mean()
            current_sma = df['sma_100'].iloc[-1]
            trend_up = current_price > current_sma
            
            # 5. Filtro de Volatilidad (ATR)
            # Evitar operar si la vela actual es demasiado "grande" comparada con el promedio
            if 'atr' not in df.columns:
                high_low = df['high'] - df['low']
                high_close = abs(df['high'] - df['close'].shift())
                low_close = abs(df['low'] - df['close'].shift())
                tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
                df['atr'] = tr.rolling(window=14).mean()
            
            current_atr = df['atr'].iloc[-1]
            last_candle_range = last_candle['high'] - last_candle['low']
            
            if current_atr > 0 and last_candle_range > current_atr * 3:
                return {'action': 'WAIT', 'confidence': 0, 'reason': f'Volatilidad Extrema (Vela > 3x ATR)'}

            # --- ANÁLISIS PARA CALL (Compra en Banda Inferior) ---
            call_score = 0
            call_reasons = []
            
            # 1. Precio tocó/perforó banda inferior (OBLIGATORIO)
            touched_lower = last_candle['low'] <= bb_low * 1.0002
            if touched_lower:
                call_score += 20
                call_reasons.append(f"Toque Banda Inferior")
            else:
                call_score = 0
            
            if call_score > 0:
                # 2. RSI en sobreventa EXTREMA (OBLIGATORIO)
                # Si el activo es muy volátil (ATR alto), exigimos RSI más bajo
                rsi_limit = 25 if last_candle_range > current_atr else 30
                if rsi <= rsi_limit:
                    call_score += 30
                    call_reasons.append(f"RSI {rsi:.1f} (Límite {rsi_limit})")
                else:
                    call_score = 0
            
            if call_score > 0:
                # 3. Vela de confirmación (OBLIGATORIO)
                # Debe ser alcista y haber cerrado arriba del mínimo previo
                candle_is_bullish = last_candle['close'] > last_candle['open']
                if candle_is_bullish:
                    call_score += 25
                    call_reasons.append("Confirmación Alcista")
                else:
                    call_score = 0
            
            if call_score > 0:
                # 4. Rechazo (Mecha inferior)
                lower_wick = min(last_candle['open'], last_candle['close']) - last_candle['low']
                if last_candle_range > 0 and (lower_wick / last_candle_range) > 0.4:
                    call_score += 15
                    call_reasons.append("Rechazo fuerte (mecha)")
                
                # 5. Tendencia
                if trend_up:
                    call_score += 10
                    call_reasons.append("Tendencia SMA100 Alcista")
                
                # Bonus MACD
                if last_candle['macd'] > last_candle['macd_signal']:
                    call_score += 5
                    call_reasons.append("MACD OK")

            # --- ANÁLISIS PARA PUT (Venta en Banda Superior) ---
            put_score = 0
            put_reasons = []
            
            # 1. Precio tocó/perforó banda superior (OBLIGATORIO)
            touched_upper = last_candle['high'] >= bb_high * 0.9998
            if touched_upper:
                put_score += 20
                put_reasons.append(f"Toque Banda Superior")
            else:
                put_score = 0
            
            if put_score > 0:
                # 2. RSI en sobrecompra EXTREMA (OBLIGATORIO)
                rsi_limit = 75 if last_candle_range > current_atr else 70
                if rsi >= rsi_limit:
                    put_score += 30
                    put_reasons.append(f"RSI {rsi:.1f} (Límite {rsi_limit})")
                else:
                    put_score = 0
            
            if put_score > 0:
                # 3. Vela de confirmación (OBLIGATORIO)
                candle_is_bearish = last_candle['close'] < last_candle['open']
                if candle_is_bearish:
                    put_score += 25
                    put_reasons.append("Confirmación Bajista")
                else:
                    put_score = 0
            
            if put_score > 0:
                # 4. Rechazo (Mecha superior)
                upper_wick = last_candle['high'] - max(last_candle['open'], last_candle['close'])
                if last_candle_range > 0 and (upper_wick / last_candle_range) > 0.4:
                    put_score += 15
                    put_reasons.append("Rechazo fuerte (mecha)")
                
                # 5. Tendencia
                if not trend_up:
                    put_score += 10
                    put_reasons.append("Tendencia SMA100 Bajista")
                
                # Bonus MACD
                if last_candle['macd'] < last_candle['macd_signal']:
                    put_score += 5
                    put_reasons.append("MACD OK")
            
            # --- DECISIÓN FINAL ---
            final_threshold = 85
            
            if call_score >= final_threshold and call_score > put_score:
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
