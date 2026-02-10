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
                # Retornamos None pero con indicadores para aprendizaje si se desea forzar
                return None
            
            # Calcular confluencias
            decision = self._calculate_confluence(signals, asset)
            
            if decision:
                print(f"   ✅ LocalAI APRUEBA: {decision['direction']} ({decision['confidence']*100:.0f}%)")
                print(f"   📋 Señales: {', '.join([s['name'] for s in signals])}")
                
                # Adjuntar indicadores para aprendizaje
                decision['indicators'] = {'rsi': float(rsi), 'macd': float(macd)}
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
            signals.append({'name': 'RSI_EXTREME_OVERSOLD', 'action': 'CALL', 'confidence': 0.85, 'value': rsi})
        elif rsi <= 30:
            signals.append({'name': 'RSI_OVERSOLD', 'action': 'CALL', 'confidence': 0.70, 'value': rsi})
        elif rsi >= 80:
            signals.append({'name': 'RSI_EXTREME_OVERBOUGHT', 'action': 'PUT', 'confidence': 0.85, 'value': rsi})
        elif rsi >= 70:
            signals.append({'name': 'RSI_OVERBOUGHT', 'action': 'PUT', 'confidence': 0.70, 'value': rsi})
        
        # 2. Señales MACD
        if macd > 0.0002: signals.append({'name': 'MACD_STRONG_BULLISH', 'action': 'CALL', 'confidence': 0.65, 'value': macd})
        elif macd > 0.0001: signals.append({'name': 'MACD_BULLISH', 'action': 'CALL', 'confidence': 0.55, 'value': macd})
        elif macd < -0.0002: signals.append({'name': 'MACD_STRONG_BEARISH', 'action': 'PUT', 'confidence': 0.65, 'value': macd})
        elif macd < -0.0001: signals.append({'name': 'MACD_BEARISH', 'action': 'PUT', 'confidence': 0.55, 'value': macd})
        
        # 3. Análisis de momentum (últimas 3 velas)
        if len(df) >= 3:
            last_3 = df.tail(3)
            if all(last_3['close'] < last_3['open']): # 3 rojas
                signals.append({'name': 'THREE_RED_CANDLES', 'action': 'CALL', 'confidence': 0.60, 'value': 3})
            elif all(last_3['close'] > last_3['open']): # 3 verdes
                signals.append({'name': 'THREE_GREEN_CANDLES', 'action': 'PUT', 'confidence': 0.60, 'value': 3})
        
        # 4. Análisis de volatilidad
        if len(df) >= 20:
            recent_volatility = df.tail(20)['close'].std()
            avg_volatility = df['close'].std()
            if recent_volatility > avg_volatility * 1.5:
                for signal in signals: signal['confidence'] *= 0.9
        
        return signals
    
    def _calculate_confluence(self, signals, asset):
        """Calcula confluencias y toma decisión final"""
        if len(signals) < 1:
            return None
        
        call_signals = [s for s in signals if s['action'] == 'CALL']
        put_signals = [s for s in signals if s['action'] == 'PUT']
        
        call_confidence = np.mean([s['confidence'] for s in call_signals]) if call_signals else 0
        put_confidence = np.mean([s['confidence'] for s in put_signals]) if put_signals else 0
        
        direction, confidence, active_signals = None, 0, []
        
        if len(call_signals) > len(put_signals) and call_confidence >= self.min_confidence:
            direction, confidence, active_signals = 'CALL', call_confidence, call_signals
        elif len(put_signals) > len(call_signals) and put_confidence >= self.min_confidence:
            direction, confidence, active_signals = 'PUT', put_confidence, put_signals
        elif len(call_signals) == len(put_signals):
            if call_confidence > put_confidence and call_confidence >= self.min_confidence:
                direction, confidence, active_signals = 'CALL', call_confidence, call_signals
            elif put_confidence >= self.min_confidence:
                direction, confidence, active_signals = 'PUT', put_confidence, put_signals
        
        if not direction or confidence < self.min_confidence:
            return None
        
        signal_names = [s['name'] for s in active_signals]
        return {
            'asset': asset,
            'direction': direction,
            'confidence': confidence,
            'reason': f"LocalAI: {', '.join(signal_names[:2])}",
            'ai_source': 'LocalAI',
            'signals_count': len(active_signals),
            'signals': signal_names
        }

    def evaluate_trade_safety(self, asset, direction, expiration=5):
        """Evalúa si es seguro operar basado en memoria y horario"""
        try:
            with open('data/experiences.json', 'r') as f:
                memory = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            memory = []
            
        today = datetime.now().strftime('%Y-%m-%d')
        recent_losses = 0
        
        for exp in memory:
            if exp.get('date') == today and exp.get('asset') == asset:
                if exp.get('result') == 'LOSS':
                    recent_losses += 1
                else:
                    recent_losses = 0
        
        if recent_losses >= 2:
            return False, f"🛑 Memoria: {recent_losses} pérdidas seguidas hoy en {asset}. Evitando."
            
        hour = datetime.now().hour
        if 14 <= hour <= 16:
             return False, "🛑 Horario de baja volatilidad (14-16h). Riesgoso."

        return True, "✅ Aprobado por IA Local"

    def record_experience(self, asset, direction, result, indicators=None):
        """Guarda resultado para aprendizaje"""
        experience = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'time': datetime.now().strftime('%H:%M:%S'),
            'asset': asset,
            'direction': direction,
            'result': result,
            'indicators': indicators or {}
        }
        
        filepath = 'data/experiences.json'
        try:
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                data = []
            
            data.append(experience)
            if len(data) > 1000: data = data[-1000:]
                
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=4)
                
            print(f"📝 Experiencia registrada: {asset} {direction} -> {result}")
        except Exception as e:
            print(f"❌ Error guardando experiencia: {e}")

    def get_status(self):
        return {
            'name': self.name,
            'version': self.version,
            'status': 'active',
            'response_time': '< 1ms',
            'patterns_loaded': len(self.patterns),
            'min_confidence': self.min_confidence
        }
    
    def quick_decision(self, rsi, macd, asset="UNKNOWN"):
        """Decisión ultra-rápida basada solo en indicadores básicos"""
        if rsi <= 25: return {'direction': 'CALL', 'confidence': 0.75, 'reason': f'RSI extremo ({rsi:.1f})', 'ai_source': 'LocalAI-Fast'}
        elif rsi >= 75: return {'direction': 'PUT', 'confidence': 0.75, 'reason': f'RSI extremo ({rsi:.1f})', 'ai_source': 'LocalAI-Fast'}
        elif macd > 0.0002: return {'direction': 'CALL', 'confidence': 0.60, 'reason': f'MACD fuerte ({macd:.5f})', 'ai_source': 'LocalAI-Fast'}
        elif macd < -0.0002: return {'direction': 'PUT', 'confidence': 0.60, 'reason': f'MACD fuerte ({macd:.5f})', 'ai_source': 'LocalAI-Fast'}
        return None