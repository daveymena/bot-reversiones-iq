#!/usr/bin/env python3
"""
IA Local Ultra-Liviana para Análisis de Trading
No depende de servidores externos, funciona 100% local
"""

import pandas as pd
import numpy as np
from datetime import datetime
import json

class LocalAIAnalyzer:
    """
    IA local que simula análisis inteligente usando lógica determinística
    Ultra-rápida y confiable para trading
    """
    
    def __init__(self):
        self.name = "LocalAI"
        self.version = "1.0"
        
        # Patrones aprendidos (simulados)
        self.patterns = {
            'rsi_oversold': {'threshold': 30, 'action': 'CALL', 'confidence': 0.75},
            'rsi_overbought': {'threshold': 70, 'action': 'PUT', 'confidence': 0.75},
            'rsi_extreme_oversold': {'threshold': 20, 'action': 'CALL', 'confidence': 0.85},
            'rsi_extreme_overbought': {'threshold': 80, 'action': 'PUT', 'confidence': 0.85},
            'macd_bullish': {'threshold': 0.0001, 'action': 'CALL', 'confidence': 0.60},
            'macd_bearish': {'threshold': -0.0001, 'action': 'PUT', 'confidence': 0.60},
        }
        
        # Configuración de confluencias
        self.min_confluence_signals = 2
        self.min_confidence = 0.55
        
    def analyze_market_opportunity(self, asset, df, market_data=None):
        """
        Analiza oportunidad de mercado usando IA local
        
        Args:
            asset: Nombre del activo
            df: DataFrame con datos OHLC e indicadores
            market_data: Datos adicionales del mercado
            
        Returns:
            dict: Decisión de trading o None
        """
        
        if df.empty or len(df) < 10:
            return None
        
        try:
            # Obtener última vela
            last_candle = df.iloc[-1]
            
            # Extraer indicadores
            rsi = last_candle.get('rsi', 50)
            macd = last_candle.get('macd', 0)
            price = last_candle['close']
            
            print(f"🤖 LocalAI analizando {asset}...")
            print(f"   📊 RSI: {rsi:.1f} | MACD: {macd:.5f} | Precio: {price:.5f}")
            
            # Detectar señales
            signals = self._detect_signals(rsi, macd, df)
            
            if not signals:
                print("   ⏸️ Sin señales detectadas")
                return None
            
            # Calcular confluencias
            decision = self._calculate_confluence(signals, asset)
            
            if decision:
                print(f"   ✅ LocalAI APRUEBA: {decision['direction']} ({decision['confidence']*100:.0f}%)")
                print(f"   📋 Señales: {', '.join([s['name'] for s in signals])}")
                return decision
            else:
                print("   ⏸️ Confluencias insuficientes")
                return None
                
        except Exception as e:
            print(f"   ❌ Error en LocalAI: {e}")
            return None
    
    def _detect_signals(self, rsi, macd, df):
        """Detecta señales técnicas"""
        signals = []
        
        # 1. Señales RSI
        if rsi <= 20:
            signals.append({
                'name': 'RSI_EXTREME_OVERSOLD',
                'action': 'CALL',
                'confidence': 0.85,
                'value': rsi
            })
        elif rsi <= 30:
            signals.append({
                'name': 'RSI_OVERSOLD',
                'action': 'CALL',
                'confidence': 0.70,
                'value': rsi
            })
        elif rsi >= 80:
            signals.append({
                'name': 'RSI_EXTREME_OVERBOUGHT',
                'action': 'PUT',
                'confidence': 0.85,
                'value': rsi
            })
        elif rsi >= 70:
            signals.append({
                'name': 'RSI_OVERBOUGHT',
                'action': 'PUT',
                'confidence': 0.70,
                'value': rsi
            })
        
        # 2. Señales MACD
        if macd > 0.0002:  # MACD fuertemente alcista
            signals.append({
                'name': 'MACD_STRONG_BULLISH',
                'action': 'CALL',
                'confidence': 0.65,
                'value': macd
            })
        elif macd > 0.0001:  # MACD alcista
            signals.append({
                'name': 'MACD_BULLISH',
                'action': 'CALL',
                'confidence': 0.55,
                'value': macd
            })
        elif macd < -0.0002:  # MACD fuertemente bajista
            signals.append({
                'name': 'MACD_STRONG_BEARISH',
                'action': 'PUT',
                'confidence': 0.65,
                'value': macd
            })
        elif macd < -0.0001:  # MACD bajista
            signals.append({
                'name': 'MACD_BEARISH',
                'action': 'PUT',
                'confidence': 0.55,
                'value': macd
            })
        
        # 3. Análisis de momentum (últimas 3 velas)
        if len(df) >= 3:
            last_3 = df.tail(3)
            
            # 3 velas consecutivas del mismo color
            if all(last_3['close'] < last_3['open']):  # 3 rojas
                signals.append({
                    'name': 'THREE_RED_CANDLES',
                    'action': 'CALL',  # Posible rebote
                    'confidence': 0.60,
                    'value': 3
                })
            elif all(last_3['close'] > last_3['open']):  # 3 verdes
                signals.append({
                    'name': 'THREE_GREEN_CANDLES',
                    'action': 'PUT',  # Posible corrección
                    'confidence': 0.60,
                    'value': 3
                })
        
        # 4. Análisis de volatilidad
        if len(df) >= 20:
            recent_volatility = df.tail(20)['close'].std()
            avg_volatility = df['close'].std()
            
            if recent_volatility > avg_volatility * 1.5:
                # Alta volatilidad - ser más conservador
                for signal in signals:
                    signal['confidence'] *= 0.9
        
        return signals
    
    def _calculate_confluence(self, signals, asset):
        """Calcula confluencias y toma decisión final"""
        
        if len(signals) < 1:
            return None
        
        # Separar señales por dirección
        call_signals = [s for s in signals if s['action'] == 'CALL']
        put_signals = [s for s in signals if s['action'] == 'PUT']
        
        # Calcular confianza promedio por dirección
        call_confidence = np.mean([s['confidence'] for s in call_signals]) if call_signals else 0
        put_confidence = np.mean([s['confidence'] for s in put_signals]) if put_signals else 0
        
        # Decidir dirección
        if len(call_signals) > len(put_signals) and call_confidence >= self.min_confidence:
            direction = 'CALL'
            confidence = call_confidence
            active_signals = call_signals
        elif len(put_signals) > len(call_signals) and put_confidence >= self.min_confidence:
            direction = 'PUT'
            confidence = put_confidence
            active_signals = put_signals
        elif len(call_signals) == len(put_signals):
            # Empate - usar la de mayor confianza
            if call_confidence > put_confidence and call_confidence >= self.min_confidence:
                direction = 'CALL'
                confidence = call_confidence
                active_signals = call_signals
            elif put_confidence >= self.min_confidence:
                direction = 'PUT'
                confidence = put_confidence
                active_signals = put_signals
            else:
                return None
        else:
            return None
        
        # Verificar confianza mínima
        if confidence < self.min_confidence:
            return None
        
        # Crear razón descriptiva
        signal_names = [s['name'] for s in active_signals]
        reason = f"LocalAI: {', '.join(signal_names[:2])}"  # Máximo 2 nombres
        
        return {
            'asset': asset,
            'direction': direction,
            'confidence': confidence,
            'reason': reason,
            'ai_source': 'LocalAI',
            'signals_count': len(active_signals),
            'signals': signal_names
        }
    
    def get_status(self):
        """Retorna estado de la IA local"""
        return {
            'name': self.name,
            'version': self.version,
            'status': 'active',
            'response_time': '< 1ms',
            'patterns_loaded': len(self.patterns),
            'min_confidence': self.min_confidence
        }
    
    def quick_decision(self, rsi, macd, asset="UNKNOWN"):
        """Decisión ultra-rápida basada solo en RSI y MACD"""
        
        # Lógica ultra-simple para máxima velocidad
        if rsi <= 25:
            return {
                'direction': 'CALL',
                'confidence': 0.75,
                'reason': f'RSI extremo ({rsi:.1f})',
                'ai_source': 'LocalAI-Fast'
            }
        elif rsi >= 75:
            return {
                'direction': 'PUT',
                'confidence': 0.75,
                'reason': f'RSI extremo ({rsi:.1f})',
                'ai_source': 'LocalAI-Fast'
            }
        elif macd > 0.0002:
            return {
                'direction': 'CALL',
                'confidence': 0.60,
                'reason': f'MACD fuerte ({macd:.5f})',
                'ai_source': 'LocalAI-Fast'
            }
        elif macd < -0.0002:
            return {
                'direction': 'PUT',
                'confidence': 0.60,
                'reason': f'MACD fuerte ({macd:.5f})',
                'ai_source': 'LocalAI-Fast'
            }
        else:
            return None