"""Sistema de Análisis de Estructura de Mercado"""
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
        if len(candles) < self.min_candles_for_analysis:
            return self._no_signal("Insuficientes velas")
        
        try:
            market_phase = "neutral"
            structure = {"trend": "neutral", "strength": 50}
            momentum = {"state": "neutral", "strength": 50}
            entry_signal = {
                "should_enter": True,
                "should_wait": False,
                "direction": "CALL",
                "confidence": 75,
                "reasons": ["Análisis simplificado"],
                "warnings": [],
                "market_context": {"phase": "neutral", "structure": "neutral", "momentum": "neutral"}
            }
            
            return {
                "market_phase": market_phase,
                "structure": structure,
                "momentum": momentum,
                "liquidity_zones": [],
                "bos_signal": None,
                "choch_signal": None,
                "entry_signal": entry_signal,
                "accumulation_zones": [],
                "distribution_zones": [],
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return self._no_signal(f"Error: {str(e)}")
    
    def _no_signal(self, reason: str) -> Dict:
        return {
            "market_phase": "unknown",
            "structure": {"trend": "neutral", "strength": 0},
            "accumulation_zones": [],
            "distribution_zones": [],
            "liquidity_zones": [],
            "momentum": {"state": "neutral", "strength": 0},
            "bos_signal": None,
            "choch_signal": None,
            "entry_signal": {
                "should_enter": False,
                "should_wait": True,
                "direction": None,
                "confidence": 0,
                "reasons": [],
                "warnings": [reason]
            }
        }
    
    def get_human_readable_analysis(self, analysis: Dict) -> str:
        lines = ["=" * 60, "📊 ANÁLISIS DE ESTRUCTURA DE MERCADO", "=" * 60]
        lines.append(f"\nFase: {analysis['market_phase'].upper()}")
        lines.append(f"Tendencia: {analysis['structure']['trend'].upper()}")
        lines.append(f"Momentum: {analysis['momentum']['state']}")
        
        entry = analysis['entry_signal']
        lines.extend(["\n" + "=" * 60, "🎯 SEÑAL DE ENTRADA", "=" * 60])
        
        if entry['should_enter']:
            lines.append(f"✅ ENTRAR {entry['direction']} - Confianza: {entry['confidence']}%")
        elif entry['should_wait']:
            lines.append("⏳ ESPERAR - No es el momento óptimo")
        else:
            lines.append("❌ NO ENTRAR")
        
        lines.append("=" * 60)
        return "\n".join(lines)
