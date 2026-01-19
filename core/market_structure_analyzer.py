"""Sistema de Análisis de Estructura de Mercado REAL"""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class MarketStructureAnalyzer:
    def __init__(self):
        self.min_candles_for_analysis = 50
    
    def analyze_full_context(self, candles: pd.DataFrame) -> Dict:
        """
        Realiza un análisis técnico REAL de la estructura del mercado.
        Calcula tendencias, momentum y advierte sobre operaciones contra-tendencia.
        """
        if len(candles) < self.min_candles_for_analysis:
            return self._no_signal("Insuficientes velas")
        
        try:
            df = candles.copy()
            
            # 1. CALCULO DE INDICADORES DE ESTRUCTURA
            # SMAs para tendencia
            df['sma_20'] = df['close'].rolling(window=20).mean()
            df['sma_50'] = df['close'].rolling(window=50).mean()
            
            last = df.iloc[-1]
            prev = df.iloc[-2]
            
            # 2. DEFINIR TENDENCIA
            trend = "neutral"
            trend_strength = 0
            
            if last['sma_20'] > last['sma_50']:
                trend = "bullish"
                # Fuerza: Distancia entre medias
                dist = (last['sma_20'] - last['sma_50']) / last['sma_50']
                trend_strength = min(100, dist * 10000) # Normalizar
            elif last['sma_20'] < last['sma_50']:
                trend = "bearish"
                dist = (last['sma_50'] - last['sma_20']) / last['sma_50']
                trend_strength = min(100, dist * 10000)
            
            # 3. ANALISIS DE MOMENTUM (Velas recientes)
            # Mirar últimas 3 velas
            last_3 = df.iloc[-3:]
            closes = last_3['close'].values
            opens = last_3['open'].values
            
            momentum_state = "neutral"
            bearish_candles = np.sum(closes < opens)
            bullish_candles = np.sum(closes > opens)
            
            if bearish_candles == 3:
                momentum_state = "strong_bearish"
            elif bullish_candles == 3:
                momentum_state = "strong_bullish"
            elif bearish_candles == 2:
                momentum_state = "bearish"
            elif bullish_candles == 2:
                momentum_state = "bullish"
                
            # 4. DECISIÓN DE ESTRUCTURA
            should_enter = False
            direction = None
            reasons = []
            warnings = []
            confidence = 50
            
            # Lógica de Validación de Estructura
            
            # A) Si TENDENCIA y MOMENTUM coinciden -> SEÑAL FUERTE A FAVOR
            if trend == "bullish" and momentum_state in ["bullish", "strong_bullish"]:
                should_enter = True
                direction = "CALL"
                confidence = 85 + (5 if momentum_state == "strong_bullish" else 0)
                reasons.append(f"Tendencia Alcista (Fuerza {trend_strength:.0f})")
                reasons.append("Momentum a favor (Velas verdes)")
                
            elif trend == "bearish" and momentum_state in ["bearish", "strong_bearish"]:
                should_enter = True
                direction = "PUT"
                confidence = 85 + (5 if momentum_state == "strong_bearish" else 0)
                reasons.append(f"Tendencia Bajista (Fuerza {trend_strength:.0f})")
                reasons.append("Momentum a favor (Velas rojas)")
                
            # B) Si queremos CONTRA-TENDENCIA (Reversión), necesitamos confirmación
            #    El "placebo" anterior aprobaba todo. Ahora filtramos.
            else:
                # Estamos en escenario de posible reversión o ruido
                should_enter = False # Por defecto esperar
                confidence = 0
                
                # Caso Reversión Alcista (Esperamos CALL en tendencia bajista)
                if trend == "bearish":
                    if momentum_state == "strong_bearish":
                        warnings.append("⚠️ CAÍDA LIBRE: Momentum bajista fuerte. Peligroso operar CALL.")
                        should_enter = False
                    elif momentum_state == "bullish": # Empieza a girar (2 velas verdes)
                        should_enter = True
                        direction = "CALL"
                        confidence = 65 # Menor confianza por ser contra-tendencia
                        reasons.append("Posible reversión alcista (2 velas verdes en tendencia bajista)")
                    else:
                        warnings.append("Tendencia bajista dominante. Esperando giro claro.")

                # Caso Reversión Bajista (Esperamos PUT en tendencia alcista)
                elif trend == "bullish":
                    if momentum_state == "strong_bullish":
                        warnings.append("⚠️ COHETE: Momentum alcista fuerte. Peligroso operar PUT.")
                        should_enter = False
                    elif momentum_state == "bearish": # Empieza a girar (2 velas rojas)
                        should_enter = True
                        direction = "PUT"
                        confidence = 65
                        reasons.append("Posible reversión bajista (2 velas rojas en tendencia alcista)")
                    else:
                        warnings.append("Tendencia alcista dominante. Esperando giro claro.")

            entry_signal = {
                "should_enter": should_enter,
                "should_wait": not should_enter,
                "direction": direction if direction else "NONE",
                "confidence": confidence,
                "reasons": reasons,
                "warnings": warnings,
                "market_context": {"phase": trend, "momentum": momentum_state}
            }
            
            return {
                "market_phase": trend,
                "structure": {"trend": trend, "strength": trend_strength},
                "momentum": {"state": momentum_state, "strength": 0},
                "entry_signal": entry_signal,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return self._no_signal(f"Error en analisis: {str(e)}")
    
    def _no_signal(self, reason: str) -> Dict:
        return {
            "market_phase": "unknown",
            "structure": {"trend": "neutral", "strength": 0},
            "momentum": {"state": "neutral", "strength": 0},
            "entry_signal": {
                "should_enter": False,
                "should_wait": True,
                "direction": "NONE",
                "confidence": 0,
                "reasons": [],
                "warnings": [reason]
            }
        }
    
    def get_human_readable_analysis(self, analysis: Dict) -> str:
        lines = ["=" * 60, "📊 ANÁLISIS DE ESTRUCTURA REAL", "=" * 60]
        st = analysis['structure']
        mo = analysis['momentum']
        lines.append(f"Tendencia: {st['trend'].upper()} (Fuerza: {st['strength']:.1f})")
        lines.append(f"Momentum : {mo['state'].upper()}")
        
        entry = analysis['entry_signal']
        lines.extend(["\n" + "=" * 60, "🎯 SEÑAL DE ESTRUCTURA", "=" * 60])
        
        if entry['should_enter']:
            lines.append(f"✅ CONFIRMADO: {entry['direction']} - Confianza: {entry['confidence']}%")
            for r in entry['reasons']:
                lines.append(f"   - {r}")
        else:
            lines.append("⏳ ESPERAR / NO OPERAR")
            for w in entry['warnings']:
                lines.append(f"   ⚠️ {w}")
        
        lines.append("=" * 60)
        return "\n".join(lines)
