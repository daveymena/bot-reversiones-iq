"""
Decision Validator - Valida decisiones antes de ejecutar operaciones
Asegura que el bot tenga suficientes datos y análisis antes de operar
"""
import pandas as pd
import numpy as np
from strategies.advanced_analysis import AdvancedMarketAnalysis

class DecisionValidator:
    """
    Valida que una decisión de trading tenga suficiente respaldo
    antes de ejecutar la operación
    """
    def __init__(self):
        self.min_candles_required = 50  # Mínimo de velas reducido
        self.min_confidence = 0.60  # Confianza mínima reducida (60%) - MÁS PERMISIVO
        self.advanced_analysis = AdvancedMarketAnalysis()
        
        # 🧠 LECCIONES APRENDIDAS (se actualizan dinámicamente)
        self.learned_rules = {
            'avoid_neutral_rsi': False,  # PERMITIR operar con RSI 45-55
            'avoid_neutral_bb': False,   # PERMITIR operar en zona neutral de BB
            'avoid_counter_trend': False, # PERMITIR operar contra la tendencia (reversiones)
            'avoid_neutral_momentum': False, # PERMITIR operar sin momentum claro
            'require_extreme_rsi': False, # Priorizar RSI extremo
            'require_bb_extreme': False,  # Priorizar BB extremos
        }
        
    def validate_decision(self, df, action, indicators_analysis, rl_prediction, llm_advice=None):
        """
        Valida una decisión de trading antes de ejecutarla
        
        Args:
            df: DataFrame con datos históricos e indicadores
            action: Acción propuesta (0=HOLD, 1=CALL, 2=PUT)
            indicators_analysis: Análisis de indicadores técnicos
            rl_prediction: Predicción del agente RL
            llm_advice: Consejo del LLM (opcional)
            
        Returns:
            dict: {
                'valid': bool,
                'confidence': float,
                'reasons': list,
                'warnings': list,
                'recommendation': str
            }
        """
        result = {
            'valid': False,
            'confidence': 0.0,
            'reasons': [],
            'warnings': [],
            'recommendation': 'HOLD'
        }
        
        # 1. VALIDAR DATOS SUFICIENTES
        if df is None or df.empty:
            result['warnings'].append("❌ No hay datos de mercado")
            return result
        
        if len(df) < self.min_candles_required:
            result['warnings'].append(f"⚠️ Pocas velas ({len(df)}), se necesitan al menos {self.min_candles_required}")
            return result
        
        result['reasons'].append(f"✅ Datos suficientes ({len(df)} velas)")
        
        # 2. ANÁLISIS AVANZADO DEL MERCADO
        advanced = self.advanced_analysis.full_market_analysis(df)
        
        # Si el análisis avanzado dice NO operar, respetar
        if not advanced['can_trade']:
            result['warnings'].extend(advanced['warnings'])
            result['reasons'].extend(advanced['reasons'])
            result['recommendation'] = 'HOLD'
            return result
        
        # Agregar razones del análisis avanzado
        result['reasons'].extend(advanced['reasons'])
        
        # Ajustar confianza basado en análisis avanzado
        advanced_confidence = advanced['confidence']
        result['reasons'].append(f"📊 Análisis avanzado: {advanced_confidence*100:.0f}% confianza")
        
        # SI EL ANÁLISIS AVANZADO TIENE ALTA CONFIANZA, USARLO DIRECTAMENTE
        if advanced_confidence >= 0.75:
            result['valid'] = True
            result['confidence'] = advanced_confidence
            result['recommendation'] = advanced['recommendation']
            result['reasons'].append(f"⭐ Usando recomendación del análisis avanzado (confianza alta)")
            return result
        
        # 3. VALIDAR INDICADORES CALCULADOS
        required_indicators = ['rsi', 'macd', 'close']
        missing_indicators = [ind for ind in required_indicators if ind not in df.columns]
        
        if missing_indicators:
            result['warnings'].append(f"⚠️ Indicadores faltantes: {missing_indicators}")
            return result
        
        result['reasons'].append("✅ Indicadores calculados correctamente")
        
        # 3. VALIDAR CALIDAD DE DATOS
        # Verificar que no haya demasiados NaN
        nan_percentage = df.isnull().sum().sum() / (len(df) * len(df.columns))
        if nan_percentage > 0.1:  # Más del 10% NaN
            result['warnings'].append(f"⚠️ Demasiados datos faltantes ({nan_percentage*100:.1f}%)")
            return result
        
        result['reasons'].append("✅ Calidad de datos aceptable")
        
        # 4. ANÁLISIS DE INDICADORES TÉCNICOS CON LECCIONES APRENDIDAS
        last_row = df.iloc[-1]
        
        # RSI con validación estricta
        rsi = last_row['rsi']
        rsi_signal = None
        
        # 🧠 LECCIÓN: NO operar con RSI neutral (45-55)
        if self.learned_rules['avoid_neutral_rsi'] and 45 <= rsi <= 55:
            result['warnings'].append(f"❌ RSI neutral ({rsi:.1f}) - Lección aprendida: NO operar")
            result['recommendation'] = 'HOLD'
            return result
        
        if rsi < 30:
            rsi_signal = 'CALL'
            result['reasons'].append(f"📊 RSI: {rsi:.1f} (Sobreventa → CALL)")
        elif rsi > 70:
            rsi_signal = 'PUT'
            result['reasons'].append(f"📊 RSI: {rsi:.1f} (Sobrecompra → PUT)")
        else:
            rsi_signal = 'NEUTRAL'
            result['reasons'].append(f"📊 RSI: {rsi:.1f} (Neutral)")
        
        # MACD
        macd = last_row['macd']
        macd_signal = 'CALL' if macd > 0 else 'PUT'
        result['reasons'].append(f"📊 MACD: {macd:.5f} ({'Alcista' if macd > 0 else 'Bajista'} → {macd_signal})")
        
        # 🧠 VALIDAR BOLLINGER BANDS
        if 'bb_low' in df.columns and 'bb_high' in df.columns:
            bb_low = last_row['bb_low']
            bb_high = last_row['bb_high']
            bb_mid = (bb_low + bb_high) / 2
            price = last_row['close']
            
            # Determinar posición en BB
            if price <= bb_low:
                bb_position = 'LOWER'
                result['reasons'].append(f"📊 Precio en BB inferior (soporte)")
            elif price >= bb_high:
                bb_position = 'UPPER'
                result['reasons'].append(f"📊 Precio en BB superior (resistencia)")
            elif price < bb_mid:
                bb_position = 'BELOW_MID'
                result['reasons'].append(f"📊 Precio en zona neutral (debajo de media)")
            else:
                bb_position = 'ABOVE_MID'
                result['reasons'].append(f"📊 Precio en zona neutral (encima de media)")
            
            # 🧠 LECCIÓN: NO operar en zona neutral de BB
            if self.learned_rules['avoid_neutral_bb']:
                if bb_position in ['BELOW_MID', 'ABOVE_MID']:
                    result['warnings'].append("❌ Precio en zona neutral de BB - Lección aprendida: NO operar")
                    result['recommendation'] = 'HOLD'
                    return result
        
        # 5. VALIDAR CONSENSO
        signals = []
        
        # Señal de indicadores
        if rsi_signal != 'NEUTRAL':
            signals.append(rsi_signal)
        signals.append(macd_signal)
        
        # Señal de RL
        rl_signal = 'HOLD' if action == 0 else ('CALL' if action == 1 else 'PUT')
        if rl_signal != 'HOLD':
            signals.append(rl_signal)
            result['reasons'].append(f"🤖 RL predice: {rl_signal}")
        
        # Señal de LLM
        if llm_advice:
            signals.append(llm_advice)
            result['reasons'].append(f"🧠 LLM recomienda: {llm_advice}")
        
        # Calcular consenso
        if not signals:
            result['warnings'].append("⚠️ No hay señales claras")
            result['recommendation'] = 'HOLD'
            return result
        
        # Contar votos
        call_votes = signals.count('CALL')
        put_votes = signals.count('PUT')
        total_votes = len(signals)
        
        # Determinar recomendación
        if call_votes > put_votes:
            result['recommendation'] = 'CALL'
            result['confidence'] = call_votes / total_votes
        elif put_votes > call_votes:
            result['recommendation'] = 'PUT'
            result['confidence'] = put_votes / total_votes
        else:
            result['recommendation'] = 'HOLD'
            result['confidence'] = 0.5
            result['warnings'].append("⚠️ Señales contradictorias")
        
        # 6. VALIDAR CONFIANZA MÍNIMA
        if result['confidence'] < self.min_confidence:
            result['warnings'].append(f"⚠️ Confianza baja ({result['confidence']*100:.0f}%), se requiere {self.min_confidence*100:.0f}%")
            result['valid'] = False
            result['recommendation'] = 'HOLD'
            return result
        
        # 7. VALIDAR VOLATILIDAD
        if 'atr' in df.columns:
            atr = last_row['atr']
            # Si ATR es muy alto, el mercado es muy volátil
            if atr > df['atr'].mean() * 2:
                result['warnings'].append(f"⚠️ Alta volatilidad (ATR: {atr:.5f})")
                # Reducir confianza
                result['confidence'] *= 0.8
        
        # 8. VALIDAR TENDENCIA CON LECCIONES APRENDIDAS
        if 'sma_20' in df.columns and 'sma_50' in df.columns:
            sma_20 = last_row['sma_20']
            sma_50 = last_row['sma_50']
            price = last_row['close']
            
            # Determinar tendencia
            if sma_20 > sma_50 and price > sma_20:
                trend = 'UPTREND'
                result['reasons'].append("📈 Tendencia alcista confirmada")
                if result['recommendation'] == 'CALL':
                    result['confidence'] *= 1.1  # Aumentar confianza
            elif sma_20 < sma_50 and price < sma_20:
                trend = 'DOWNTREND'
                result['reasons'].append("📉 Tendencia bajista confirmada")
                if result['recommendation'] == 'PUT':
                    result['confidence'] *= 1.1  # Aumentar confianza
            else:
                trend = 'SIDEWAYS'
                result['reasons'].append("↔️ Mercado lateral")
            
            # 🧠 LECCIÓN: NO operar contra la tendencia
            if self.learned_rules['avoid_counter_trend']:
                if trend == 'UPTREND' and result['recommendation'] == 'PUT':
                    result['warnings'].append("❌ PUT contra tendencia alcista - Lección aprendida: NO operar")
                    result['recommendation'] = 'HOLD'
                    return result
                elif trend == 'DOWNTREND' and result['recommendation'] == 'CALL':
                    result['warnings'].append("❌ CALL contra tendencia bajista - Lección aprendida: NO operar")
                    result['recommendation'] = 'HOLD'
                    return result
        
        # 9. DECISIÓN FINAL
        result['confidence'] = min(result['confidence'], 1.0)  # Limitar a 100%
        
        if result['confidence'] >= self.min_confidence and result['recommendation'] != 'HOLD':
            result['valid'] = True
            result['reasons'].append(f"✅ Decisión validada con {result['confidence']*100:.0f}% de confianza")
        else:
            result['valid'] = False
            result['recommendation'] = 'HOLD'
            result['warnings'].append("⚠️ No hay suficiente confianza para operar")
        
        return result
    
    def get_summary(self, validation_result):
        """
        Genera un resumen legible de la validación
        """
        lines = []
        lines.append("=" * 60)
        lines.append("📋 ANÁLISIS DE DECISIÓN")
        lines.append("=" * 60)
        
        # Recomendación
        emoji = "✅" if validation_result['valid'] else "⏸️"
        lines.append(f"\n{emoji} Recomendación: {validation_result['recommendation']}")
        lines.append(f"📊 Confianza: {validation_result['confidence']*100:.0f}%")
        
        # Razones
        if validation_result['reasons']:
            lines.append("\n📝 Análisis:")
            for reason in validation_result['reasons']:
                lines.append(f"   {reason}")
        
        # Advertencias
        if validation_result['warnings']:
            lines.append("\n⚠️ Advertencias:")
            for warning in validation_result['warnings']:
                lines.append(f"   {warning}")
        
        # Decisión final
        lines.append("\n" + "=" * 60)
        if validation_result['valid']:
            lines.append(f"✅ EJECUTAR: {validation_result['recommendation']}")
        else:
            lines.append("⏸️ NO EJECUTAR - Esperar mejor oportunidad")
        lines.append("=" * 60)
        
        return "\n".join(lines)
