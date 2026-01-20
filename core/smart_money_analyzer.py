"""
Smart Money Analyzer - Sistema de Análisis Institucional
Identifica Order Blocks, FVG, Liquidez y Estructura de Mercado Profesional
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime

class SmartMoneyAnalyzer:
    """
    Analizador avanzado que implementa conceptos de Smart Money:
    - Identificación de Order Blocks (Zonas de oferta/demanda institucional)
    - Detección de Fair Value Gaps (Desequilibrios de mercado)
    - Análisis de Liquidez (Barridos y cacería de stops)
    - Estructura de Mercado (BOS, CHoCH)
    - Sesgo direccional basado en flujo de órdenes
    """
    
    def __init__(self):
        # Parámetros de configuración
        self.ob_min_strength = 2.0  # Multiplicador de volumen/tamaño para OB
        self.fvg_min_size = 0.0001  # Tamaño mínimo para considerar un FVG
        self.liquidity_threshold = 0.0015 # 0.15% para considerar zona de liquidez
        
    def analyze_smart_money_structure(self, df: pd.DataFrame) -> Dict:
        """
        Realiza un análisis completo de Smart Money sobre el DataFrame de velas
        """
        if df.empty or len(df) < 50:
            return self._empty_analysis()
            
        try:
            # 1. Identificar Order Blocks
            order_blocks = self._identify_order_blocks(df)
            
            # 2. Identificar Fair Value Gaps
            fvgs = self._identify_fvgs(df)
            
            # 3. Analizar Estructura (BOS/CHoCH)
            structure = self._analyze_market_structure_smc(df)
            
            # 4. Identificar Zonas de Liquidez y Barridos
            liquidity = self._analyze_liquidity(df)
            
            # 5. Determinar Sesgo Direccional
            directional_bias = self._calculate_directional_bias(df, order_blocks, structure)
            
            # 6. Generar Señal de Entrada
            entry_signal = self._generate_smc_entry_signal(df, order_blocks, fvgs, structure, liquidity)
            
            return {
                'order_blocks': order_blocks,
                'fair_value_gaps': fvgs,
                'market_structure': structure,
                'liquidity_zones': liquidity,
                'directional_bias': directional_bias,
                'entry_signal': entry_signal,
                'confidence': self._calculate_smc_confidence(entry_signal, directional_bias)
            }
            
        except Exception as e:
            print(f"Error en SmartMoneyAnalyzer: {e}")
            return self._empty_analysis()

    def _identify_order_blocks(self, df: pd.DataFrame, limit: int = 10) -> List[Dict]:
        """Identifica bloques de órdenes institucionales (velas de intención)"""
        obs = []
        df_vol_mean = df['volum'].mean() if 'volum' in df.columns else 1
        
        # Recorrer velas recientes (excepto la última en formación)
        for i in range(len(df) - 20, len(df) - 1):
            candle = df.iloc[i]
            prev_candle = df.iloc[i-1]
            next_candle = df.iloc[i+1]
            
            body_size = abs(candle['close'] - candle['open'])
            avg_body = df['close'].diff().abs().tail(50).mean()
            
            # Buscar vela de intención fuerte (Bullish OB)
            # Una vela bajista seguida de un movimiento alcista fuerte que rompe su máximo
            if candle['close'] < candle['open'] and next_candle['close'] > candle['high']:
                if body_size > avg_body * 1.1:
                    obs.append({
                        'type': 'bullish',
                        'price': candle['low'],
                        'high': candle['high'],
                        'low': candle['low'],
                        'level': candle['low'], # Punto de entrada ideal
                        'timestamp': str(df.index[i]),
                        'mitigated': False,
                        'strength': body_size / avg_body
                    })
            
            # Bearish OB
            elif candle['close'] > candle['open'] and next_candle['close'] < candle['low']:
                if body_size > avg_body * 1.1:
                    obs.append({
                        'type': 'bearish',
                        'price': candle['high'],
                        'high': candle['high'],
                        'low': candle['low'],
                        'level': candle['high'],
                        'timestamp': str(df.index[i]),
                        'mitigated': False,
                        'strength': body_size / avg_body
                    })
                    
        # Verificar mitigación (si el precio ya regresó a la zona)
        current_price = df.iloc[-1]['close']
        for ob in obs:
            if ob['type'] == 'bullish' and current_price < ob['low']:
                ob['mitigated'] = True
            elif ob['type'] == 'bearish' and current_price > ob['high']:
                ob['mitigated'] = True
                
        return sorted(obs, key=lambda x: x['strength'], reverse=True)[:limit]

    def _identify_fvgs(self, df: pd.DataFrame) -> List[Dict]:
        """Identifica Fair Value Gaps (Gaps entre mechas)"""
        fvgs = []
        for i in range(len(df) - 3, len(df) - 1):
            c1 = df.iloc[i-1]
            c2 = df.iloc[i]
            c3 = df.iloc[i+1]
            
            # Bullish FVG (Gap entre low de c3 y high de c1)
            if c3['low'] > c1['high']:
                gap_size = c3['low'] - c1['high']
                fvgs.append({
                    'type': 'bullish',
                    'top': c3['low'],
                    'bottom': c1['high'],
                    'size': gap_size,
                    'filled': False # Si el precio ya lo cerró
                })
                
            # Bearish FVG (Gap entre high de c3 y low de c1)
            elif c3['high'] < c1['low']:
                gap_size = c1['low'] - c3['high']
                fvgs.append({
                    'type': 'bearish',
                    'top': c1['low'],
                    'bottom': c3['high'],
                    'size': gap_size,
                    'filled': False
                })
        return fvgs

    def _analyze_market_structure_smc(self, df: pd.DataFrame) -> Dict:
        """Determina BOS (Break of Structure) y CHoCH (Change of Character)"""
        recent_candles = df.tail(20)
        highs = recent_candles['high'].max()
        lows = recent_candles['low'].min()
        last_close = df.iloc[-1]['close']
        
        previous_high = df.iloc[:-21]['high'].tail(50).max() if len(df) > 70 else highs
        previous_low = df.iloc[:-21]['low'].tail(50).min() if len(df) > 70 else lows
        
        bos = None
        choch = None
        trend = "ranging"
        
        if last_close > previous_high:
            bos = {'type': 'bullish', 'level': previous_high}
            trend = "bullish"
        elif last_close < previous_low:
            bos = {'type': 'bearish', 'level': previous_low}
            trend = "bearish"
            
        # CHoCH es más sensible, indica cambio de tendencia local
        if trend == "bullish" and last_close < df['low'].tail(5).min():
            choch = {'type': 'bearish_change', 'level': df['low'].tail(5).min()}
        elif trend == "bearish" and last_close > df['high'].tail(5).max():
            choch = {'type': 'bullish_change', 'level': df['high'].tail(5).max()}
            
        return {
            'trend': trend,
            'bos': bos,
            'choch': choch,
            'high': highs,
            'low': lows
        }

    def _analyze_liquidity(self, df: pd.DataFrame) -> Dict:
        """Identifica piscinas de liquidez (Equal Highs/Lows)"""
        recent = df.tail(50)
        
        # Buscar "Equal Highs" (Resistencias donde hay mucha liquidez arriba)
        highs = recent['high'].values
        eq_highs = []
        for i in range(len(highs)):
            for j in range(i+1, len(highs)):
                if abs(highs[i] - highs[j]) / highs[i] < 0.0003: # Muy cerca
                    eq_highs.append(highs[i])
                    
        # Buscar barridos (Liquidity Sweep)
        last_candle = df.iloc[-1]
        sweep_up = last_candle['high'] > recent['high'].iloc[:-1].max() and last_candle['close'] < recent['high'].iloc[:-1].max()
        sweep_down = last_candle['low'] < recent['low'].iloc[:-1].min() and last_candle['close'] > recent['low'].iloc[:-1].min()
        
        return {
            'equal_highs': list(set(eq_highs))[:3],
            'sweep_up': sweep_up, # Cazó liquidez arriba y regresó (Ojo para PUT)
            'sweep_down': sweep_down # Cazó liquidez abajo y regresó (Ojo para CALL)
        }

    def _calculate_directional_bias(self, df: pd.DataFrame, obs: List[Dict], structure: Dict) -> Dict:
        """Calcula el sesgo institucional"""
        bias = "neutral"
        score = 50
        
        if structure['trend'] == "bullish": score += 20
        elif structure['trend'] == "bearish": score -= 20
        
        bullish_obs = [ob for ob in obs if ob['type'] == 'bullish' and not ob['mitigated']]
        bearish_obs = [ob for ob in obs if ob['type'] == 'bearish' and not ob['mitigated']]
        
        score += len(bullish_obs) * 5
        score -= len(bearish_obs) * 5
        
        if score > 65: bias = "bullish"
        elif score < 35: bias = "bearish"
        
        return {'bias': bias, 'confidence': abs(score - 50) * 2}

    def _generate_smc_entry_signal(self, df: pd.DataFrame, obs: List[Dict], fvgs: List[Dict], structure: Dict, liquidity: Dict) -> Dict:
        """Genera la señal final basada en Smart Money"""
        price = df.iloc[-1]['close']
        should_enter = False
        direction = "HOLD"
        reasons = []
        
        # ESTRATEGIA 1: Retorno a Bullish Order Block + Sweep Down
        bullish_ob = next((ob for ob in obs if ob['type'] == 'bullish' and not ob['mitigated']), None)
        if bullish_ob and price <= bullish_ob['high'] * 1.0005 and price >= bullish_ob['low']:
            if liquidity['sweep_down'] or structure['trend'] == "bullish":
                should_enter = True
                direction = "CALL"
                reasons.append("Retorno a Bullish OB")
                if liquidity['sweep_down']: reasons.append("Liquidación previa detectada")
                
        # ESTRATEGIA 2: Retorno a Bearish Order Block + Sweep Up
        bearish_ob = next((ob for ob in obs if ob['type'] == 'bearish' and not ob['mitigated']), None)
        if bearish_ob and price >= bearish_ob['low'] * 0.9995 and price <= bearish_ob['high']:
            if liquidity['sweep_up'] or structure['trend'] == "bearish":
                should_enter = True
                direction = "PUT"
                reasons.append("Retorno a Bearish OB")
                if liquidity['sweep_up']: reasons.append("Barrido de liquidez superior")

        return {
            'should_enter': should_enter,
            'direction': direction,
            'reasons': reasons
        }

    def _calculate_smc_confidence(self, signal: Dict, bias: Dict) -> float:
        """Calcula confianza entre 0 y 1"""
        if not signal['should_enter']: return 0.0
        
        confidence = 0.7 # Base
        if signal['direction'].lower() == bias['bias']:
            confidence += 0.2
            
        return min(confidence, 0.95)

    def _empty_analysis(self) -> Dict:
        return {
            'order_blocks': [],
            'fair_value_gaps': [],
            'market_structure': {'trend': 'neutral'},
            'entry_signal': {'should_enter': False}
        }
