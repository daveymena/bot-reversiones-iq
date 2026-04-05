"""
🧠 SISTEMA DE ANÁLISIS PROFUNDO POST-OPERACIÓN
Analiza por qué cada operación perdió/ganó y aprende patrones
"""
import json
import time
from datetime import datetime
from pathlib import Path
import pandas as pd

class DeepAnalysis:
    def __init__(self):
        self.analysis_file = Path("data/deep_analysis.json")
        self.history = self._load_history()
        self.patterns = {}
        self.adjustments = {
            'confidence_threshold': 80,
            'asset_blacklist': [],
            'asset_whitelist': [],
            'timing_restrictions': {},
            'direction_bias': {}
        }
        
    def _load_history(self):
        if self.analysis_file.exists():
            try:
                with open(self.analysis_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except: pass
        return {'operations': [], 'patterns': {}, 'insights': []}
    
    def _save_history(self):
        self.analysis_file.parent.mkdir(exist_ok=True, parents=True)
        with open(self.analysis_file, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, indent=2, default=str)
    
    def analyze_operation(self, operation_data):
        """
        Análisis profundo de una operación
        operation_data: {
            'asset': str,
            'direction': str,  # CALL/PUT
            'profit': float,
            'confidence': float,
            'reason': str,
            'entry_price': float,
            'exit_price': float,
            'entry_time': datetime,
            'market_state': dict  # RSI, Bollinger, Trend, etc.
        }
        """
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'asset': operation_data.get('asset'),
            'direction': operation_data.get('direction'),
            'profit': operation_data.get('profit'),
            'outcome': 'WIN' if operation_data.get('profit', 0) > 0 else 'LOSS',
            'confidence': operation_data.get('confidence', 0),
            'reason': operation_data.get('reason', ''),
            'failure_reasons': [],
            'success_factors': [],
            'pattern_flags': []
        }
        
        profit = operation_data.get('profit', 0)
        confidence = operation_data.get('confidence', 0)
        reason = operation_data.get('reason', '').lower()
        
        # ANÁLISIS DE PÉRDIDAS
        if profit <= 0:
            analysis['failure_reasons'].extend(self._analyze_loss_reasons(operation_data))
        
        # ANÁLISIS DE ÉXITOS
        else:
            analysis['success_factors'].extend(self._analyze_success_factors(operation_data))
        
        # DETECTAR PATRONES REPETITIVOS
        pattern_flags = self._detect_patterns(operation_data, analysis)
        analysis['pattern_flags'] = pattern_flags
        
        # GUARDAR Y APRENDER
        self.history['operations'].append(analysis)
        self._prune_old_operations()
        self._save_history()
        
        # APLICAR AJUSTES SI ES NECESARIO
        self._apply_learning(analysis)
        
        self.print_analysis(analysis)
        return analysis
    
    def _analyze_loss_reasons(self, op):
        reasons = []
        profit = op.get('profit', 0)
        confidence = op.get('confidence', 0)
        direction = op.get('direction', '')
        reason = op.get('reason', '').lower()
        market = op.get('market_state', {})
        
        # 1. Alta confianza pero perdió = fallo del análisis
        if confidence >= 85 and profit <= 0:
            reasons.append('HIGH_CONF_LOSS')
        
        # 2. Operación en resistencia/soporte incorrecto
        if 'resistencia' in reason or 'resistance' in reason:
            if direction == 'CALL':
                reasons.append('CALL_NEAR_RESISTANCE')
        if 'soporte' in reason or 'support' in reason:
            if direction == 'PUT':
                reasons.append('PUT_NEAR_SUPPORT')
        
        # 3. RSI en zona extrema
        rsi = market.get('rsi', 50)
        if rsi > 70 and direction == 'CALL':
            reasons.append('RSI_OVERBOUGHT_CALL')
        elif rsi < 30 and direction == 'PUT':
            reasons.append('RSI_OVERSOLD_PUT')
        
        # 4. Tendencia en contra
        trend = market.get('trend', 'neutral')
        if trend == 'down' and direction == 'CALL':
            reasons.append('AGAINST_TREND')
        elif trend == 'up' and direction == 'PUT':
            reasons.append('AGAINST_TREND')
        
        # 5. Baja confianza
        if confidence < 75:
            reasons.append('LOW_CONFIDENCE_ENTRY')
        
        return reasons
    
    def _analyze_success_factors(self, op):
        factors = []
        profit = op.get('profit', 0)
        confidence = op.get('confidence', 0)
        direction = op.get('direction', '')
        reason = op.get('reason', '').lower()
        market = op.get('market_state', {})
        
        # 1. Rechazo de nivel
        if 'rechaz' in reason or 'reject' in reason:
            factors.append('LEVEL_REJECTION')
        
        # 2. Confianza alta
        if confidence >= 80:
            factors.append('HIGH_CONFIDENCE')
        
        # 3. RSI en zona de reversión
        rsi = market.get('rsi', 50)
        if (rsi < 35 and direction == 'CALL') or (rsi > 65 and direction == 'PUT'):
            factors.append('RSI_REVERSAL_ZONE')
        
        # 4. Con la tendencia
        trend = market.get('trend', 'neutral')
        if (trend == 'up' and direction == 'CALL') or (trend == 'down' and direction == 'PUT'):
            factors.append('WITH_TREND')
        
        return factors
    
    def _detect_patterns(self, op, analysis):
        flags = []
        
        # Revisar últimas 5 operaciones del mismo asset
        asset = op.get('asset')
        recent_ops = [o for o in self.history['operations'] 
                      if o.get('asset') == asset][-5:]
        
        if len(recent_ops) >= 3:
            losses = [o for o in recent_ops if o.get('outcome') == 'LOSS']
            if len(losses) >= 3:
                flags.append('ASSET_CONSECUTIVE_LOSSES')
                
                # Agregar a blacklist temporal
                if asset not in self.adjustments['asset_blacklist']:
                    self.adjustments['asset_blacklist'].append(asset)
        
        # Patrón de dirección específica
        if len(recent_ops) >= 3:
            dir_losses = [o for o in recent_ops 
                         if o.get('direction') == op.get('direction') and o.get('outcome') == 'LOSS']
            if len(dir_losses) >= 3:
                direction = op.get('direction')
                if asset not in self.adjustments['direction_bias']:
                    self.adjustments['direction_bias'][asset] = {}
                self.adjustments['direction_bias'][asset][direction] = 'AVOID'
                flags.append(f'{direction}_DIRECTION_BLOCKED')
        
        # Patrón de timing (hora del día)
        hour = op.get('entry_time').hour if isinstance(op.get('entry_time'), datetime) else 0
        hour_losses = [o for o in self.history['operations'] 
                      if isinstance(o.get('timestamp'), str) and 
                      datetime.fromisoformat(o['timestamp']).hour == hour and
                      o.get('outcome') == 'LOSS'][-5:]
        
        if len(hour_losses) >= 4:
            self.adjustments['timing_restrictions'][hour] = 'AVOID'
            flags.append(f'HOUR_{hour}_AVOID')
        
        return flags
    
    def _apply_learning(self, analysis):
        """Ajusta parámetros dinámicamente basándose en el aprendizaje"""
        
        outcome = analysis.get('outcome')
        
        # Si perdió con alta confianza, aumentar threshold
        if outcome == 'LOSS' and analysis.get('confidence', 0) >= 85:
            self.adjustments['confidence_threshold'] = min(95, 
                self.adjustments['confidence_threshold'] + 2)
        
        # Si ganó consistentemente con cierto asset, whitelist
        asset = analysis.get('asset')
        if outcome == 'WIN':
            if asset not in self.adjustments['asset_whitelist']:
                recent = [o for o in self.history['operations'] 
                         if o.get('asset') == asset][-5:]
                wins = [o for o in recent if o.get('outcome') == 'WIN']
                if len(wins) >= 3:
                    self.adjustments['asset_whitelist'].append(asset)
        
        # Persistir ajustes
        self._save_adjustments()
    
    def _save_adjustments(self):
        adj_path = Path("data/adjustments.json")
        adj_path.parent.mkdir(exist_ok=True, parents=True)
        with open(adj_path, 'w', encoding='utf-8') as f:
            json.dump(self.adjustments, f, indent=2)
    
    def _prune_operations(self):
        """Mantiene solo últimas 200 operaciones"""
        if len(self.history['operations']) > 200:
            self.history['operations'] = self.history['operations'][-200:]
    
    def get_recommendations(self, asset=None):
        """Devuelve recomendaciones basadas en aprendizaje"""
        recs = {
            'min_confidence': self.adjustments['confidence_threshold'],
            'avoid_assets': self.adjustments['asset_blacklist'][:],
            'preferred_assets': self.adjustments['asset_whitelist'][:],
            'avoid_hours': list(self.adjustments['timing_restrictions'].keys()),
            'pattern_warnings': []
        }
        
        # Analizar patrones si hay suficientes datos
        if len(self.history['operations']) >= 10:
            recent = self.history['operations'][-10:]
            wins = sum(1 for o in recent if o.get('outcome') == 'WIN')
            win_rate = wins / len(recent)
            
            recs['recent_win_rate'] = round(win_rate * 100, 1)
            
            if win_rate < 0.4:
                recs['pattern_warnings'].append('BAJA TASA DE ACIERTO - CONSERVADOR')
        
        if asset and asset in self.adjustments.get('direction_bias', {}):
            biased = self.adjustments['direction_bias'][asset]
            recs['direction_guidance'] = biased
        
        return recs
    
    def print_analysis(self, analysis):
        outcome = analysis.get('outcome')
        print(f"\n{'='*50}")
        print(f"🔬 ANÁLISIS PROFUNDO - {outcome}")
        print(f"{'='*50}")
        print(f"   Asset: {analysis.get('asset')} | Dir: {analysis.get('direction')}")
        print(f"   Confianza: {analysis.get('confidence')}%")
        
        if outcome == 'LOSS':
            print(f"   ❌ RAZONES DE FALLO:")
            for reason in analysis.get('failure_reasons', []):
                print(f"      - {reason}")
        else:
            print(f"   ✅ FACTORES DE ÉXITO:")
            for factor in analysis.get('success_factors', []):
                print(f"      + {factor}")
        
        if analysis.get('pattern_flags'):
            print(f"   ⚠️ PATRONES DETECTADOS: {', '.join(analysis['pattern_flags'])}")
        
        print(f"{'='*50}\n")
    
    def get_stats_summary(self):
        """Resumen de estadísticas"""
        ops = self.history.get('operations', [])
        if not ops:
            return "Sin operaciones aún"
        
        total = len(ops)
        wins = sum(1 for o in ops if o.get('outcome') == 'WIN')
        losses = total - wins
        
        return {
            'total_operations': total,
            'wins': wins,
            'losses': losses,
            'win_rate': round(wins/total*100, 1) if total > 0 else 0,
            'confidence_threshold': self.adjustments['confidence_threshold'],
            'avoid_assets': len(self.adjustments['asset_blacklist']),
            'preferred_assets': len(self.adjustments['asset_whitelist'])
        }