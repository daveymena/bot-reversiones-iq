"""
Decision Validator - Valida decisiones antes de ejecutar operaciones
Asegura que el bot tenga suficientes datos y análisis antes de operar
"""
import pandas as pd
import numpy as np
from strategies.advanced_analysis import AdvancedMarketAnalysis
from strategies.profitability_filters import ProfitabilityFilters

class DecisionValidator:
    """
    Valida que una decisión de trading tenga suficiente respaldo
    antes de ejecutar la operación
    """
    def __init__(self):
        self.min_candles_required = 100  # Mínimo de velas para análisis SERIO
        self.min_confidence = 0.75  # Confianza mínima (75%) - MÁS ESTRICTO para evitar pérdidas
        self.advanced_analysis = AdvancedMarketAnalysis()
        self.profitability_filters = ProfitabilityFilters()  # 🎯 NUEVO: Filtros de rentabilidad
        
        # 🧠 LECCIONES APRENDIDAS (se actualizan dinámicamente)
        self.learned_rules = {
            'avoid_neutral_rsi': True,  # NO operar con RSI 45-55
            'avoid_neutral_bb': True,   # NO operar en zona neutral de BB
            'avoid_counter_trend': True, # NO operar contra la tendencia
            'avoid_neutral_momentum': True, # NO operar sin momentum claro
            'require_extreme_rsi': False, # Priorizar RSI extremo
            'require_bb_extreme': False,  # Priorizar BB extremos
        }
        
        # 🆕 MEJORA 2: Parámetros para resistencias históricas
        self.resistance_lookback = 100  # Velas a analizar para resistencias
        self.resistance_tolerance = 0.002  # 0.2% de tolerancia
        
        # 🆕 MEJORA 3: Parámetros para confirmación de reversión
        self.require_reversal_confirmation = True
        self.min_confirmation_candles = 2  # Mínimo 2 velas de confirmación
        
        # 🆕 MEJORA 4: Parámetros para análisis de momentum
        self.momentum_lookback = 10  # Velas para calcular momentum
        self.strong_momentum_threshold = 0.5  # Umbral de momentum fuerte
        
        # 🆕 MEJORA 6: Parámetros para volatilidad mínima
        self.require_min_volatility = True
        self.min_volatility_atr = 0.0005  # ATR mínimo (0.05% del precio)
        self.volatility_lookback = 20  # Velas para calcular volatilidad
        
        # 🆕 MEJORA 7: Parámetros para timing óptimo de entrada
        self.require_optimal_timing = True
        self.min_impulse_strength = 1.2  # Vela debe ser 1.2x más grande que promedio
        self.min_pullback_candles = 2    # Mínimo 2 velas de pullback
        
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
        
        # 🆕 MEJORA 6: VALIDAR VOLATILIDAD MÍNIMA
        is_valid, message, atr_value = self.check_minimum_volatility(df)
        if not is_valid:
            result['warnings'].append(message)
            result['recommendation'] = 'HOLD'
            result['valid'] = False
            return result
        
        # 🆕 MEJORA 6B: VALIDAR MOVIMIENTO DE PRECIO
        is_valid, message = self.check_price_movement(df)
        if not is_valid:
            result['warnings'].append(message)
            result['recommendation'] = 'HOLD'
            result['valid'] = False
            return result
        
        # Si llegamos aquí, hay buena volatilidad
        if atr_value > 0:
            result['reasons'].append(f"✅ Volatilidad adecuada (ATR: {atr_value*100:.3f}%)")
        
        # 🆕 MEJORA 7: VERIFICAR TIMING ÓPTIMO DE ENTRADA (antes del análisis avanzado)
        # Esto es crítico - verificar ANTES de gastar recursos en análisis completo
        if action != 0:  # Solo si hay una acción propuesta (CALL o PUT)
            direction = 'CALL' if action == 1 else 'PUT'
            can_enter, timing_msg = self.wait_for_optimal_entry(df, direction)
            
            if not can_enter:
                result['warnings'].append(timing_msg)
                result['recommendation'] = 'HOLD'
                result['valid'] = False
                result['reasons'].append("⏳ Esperando timing óptimo de entrada...")
                return result
            else:
                if timing_msg:
                    result['reasons'].append(timing_msg)
        
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
        
        # 🎯 APLICAR FILTROS DE RENTABILIDAD PRIMERO (CRÍTICO)
        action_num = 1 if advanced['recommendation'] == 'CALL' else (2 if advanced['recommendation'] == 'PUT' else 0)
        
        # Si no hay acción clara, no aplicar filtros
        if action_num == 0:
            result['valid'] = False
            result['recommendation'] = 'HOLD'
            result['warnings'].append("⚠️ No hay acción clara para validar")
            return result
        
        profitability_check = self.profitability_filters.apply_all_filters(df, action_num)
        
        # Agregar razones y warnings de filtros de rentabilidad
        result['reasons'].extend(profitability_check['reasons'])
        result['warnings'].extend(profitability_check['warnings'])
        
        # 🚨 FILTROS DE RENTABILIDAD SON OBLIGATORIOS - Si no pasan, RECHAZAR
        if not profitability_check['pass']:
            result['valid'] = False
            result['confidence'] = profitability_check['score'] / 100
            result['recommendation'] = 'HOLD'
            result['warnings'].append(f"❌ Filtros de rentabilidad NO pasados (Score: {profitability_check['score']:.0f}/100)")
            result['reasons'].append("⏸️ Esperando condiciones más favorables...")
            return result
        
        # ✅ Si pasa los filtros, usar el score como boost de confianza
        result['reasons'].append(f"🎯 Filtros de rentabilidad PASADOS (Score: {profitability_check['score']:.0f}/100)")
        
        # Combinar confianza del análisis avanzado con score de filtros
        combined_confidence = advanced_confidence * (profitability_check['score'] / 100)
        
        # SI PASA FILTROS Y TIENE CONFIANZA ACEPTABLE, APROBAR
        if combined_confidence >= 0.60:  # Reducido de 0.70 a 0.60
            result['valid'] = True
            result['confidence'] = combined_confidence
            result['recommendation'] = advanced['recommendation']
            result['reasons'].append(f"⭐ Operación APROBADA (Confianza combinada: {combined_confidence*100:.0f}%)")
            return result
        else:
            result['valid'] = False
            result['confidence'] = combined_confidence
            result['recommendation'] = 'HOLD'
            result['warnings'].append(f"⚠️ Confianza combinada insuficiente ({combined_confidence*100:.0f}% < 60%)")
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
            
            # 🚫 REGLA CRÍTICA: NO hacer CALL en resistencia (BB superior)
            if bb_position == 'UPPER' and action == 1:  # action 1 = CALL
                result['warnings'].append("❌ CALL en resistencia (BB superior) - RECHAZADO")
                result['recommendation'] = 'HOLD'
                result['valid'] = False
                return result
            
            # 🚫 REGLA CRÍTICA: NO hacer PUT en soporte (BB inferior)
            if bb_position == 'LOWER' and action == 2:  # action 2 = PUT
                result['warnings'].append("❌ PUT en soporte (BB inferior) - RECHAZADO")
                result['recommendation'] = 'HOLD'
                result['valid'] = False
                return result
            
            # 🚫 REGLA ADICIONAL: NO hacer CALL cerca de resistencia (margen de seguridad)
            bb_range = bb_high - bb_low
            upper_danger_zone = bb_high - (bb_range * 0.2)  # 20% superior de BB
            lower_danger_zone = bb_low + (bb_range * 0.2)   # 20% inferior de BB
            
            if price >= upper_danger_zone and action == 1:  # CALL cerca de resistencia
                result['warnings'].append("⚠️ CALL muy cerca de resistencia - RECHAZADO por seguridad")
                result['recommendation'] = 'HOLD'
                result['valid'] = False
                return result
            
            if price <= lower_danger_zone and action == 2:  # PUT cerca de soporte
                result['warnings'].append("⚠️ PUT muy cerca de soporte - RECHAZADO por seguridad")
                result['recommendation'] = 'HOLD'
                result['valid'] = False
                return result
            
            # 🆕 MEJORA 2: Verificar resistencias históricas
            is_valid, message = self.check_historical_resistance(df, price, action)
            if not is_valid:
                result['warnings'].append(message)
                result['recommendation'] = 'HOLD'
                result['valid'] = False
                return result
            
            # 🆕 MEJORA 3: Verificar confirmación de reversión
            is_valid, message = self.check_reversal_confirmation(df, action, bb_position)
            if not is_valid:
                result['warnings'].append(message)
                result['recommendation'] = 'HOLD'
                result['valid'] = False
                return result
            
            # 🧠 LECCIÓN: NO operar en zona neutral de BB
            if self.learned_rules['avoid_neutral_bb']:
                if bb_position in ['BELOW_MID', 'ABOVE_MID']:
                    result['warnings'].append("❌ Precio en zona neutral de BB - Lección aprendida: NO operar")
                    result['recommendation'] = 'HOLD'
                    return result
        
        # 🆕 MEJORA 4: Verificar momentum
        is_valid, message = self.check_momentum_strength(df, action)
        if not is_valid:
            result['warnings'].append(message)
            result['recommendation'] = 'HOLD'
            result['valid'] = False
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

    # 🆕 MEJORA 2: Detectar resistencias históricas
    def check_historical_resistance(self, df, current_price, action):
        """
        Detecta si el precio está cerca de una resistencia histórica
        
        Returns:
            (bool, str): (es_valido, mensaje)
        """
        try:
            # Analizar últimas N velas
            recent_data = df.tail(self.resistance_lookback)
            
            # Encontrar máximos locales (resistencias)
            highs = recent_data['high'].rolling(window=5, center=True).max()
            resistance_levels = []
            
            for i in range(2, len(highs) - 2):
                if highs.iloc[i] == recent_data['high'].iloc[i]:
                    # Es un máximo local
                    if highs.iloc[i] > highs.iloc[i-1] and highs.iloc[i] > highs.iloc[i+1]:
                        resistance_levels.append(highs.iloc[i])
            
            # Encontrar mínimos locales (soportes)
            lows = recent_data['low'].rolling(window=5, center=True).min()
            support_levels = []
            
            for i in range(2, len(lows) - 2):
                if lows.iloc[i] == recent_data['low'].iloc[i]:
                    # Es un mínimo local
                    if lows.iloc[i] < lows.iloc[i-1] and lows.iloc[i] < lows.iloc[i+1]:
                        support_levels.append(lows.iloc[i])
            
            # Verificar si precio actual está cerca de resistencia (para CALL)
            if action == 1:  # CALL
                for resistance in resistance_levels:
                    distance = abs(current_price - resistance) / resistance
                    if distance < self.resistance_tolerance:
                        return False, f"❌ Resistencia histórica detectada en {resistance:.5f} (distancia: {distance*100:.2f}%)"
            
            # Verificar si precio actual está cerca de soporte (para PUT)
            elif action == 2:  # PUT
                for support in support_levels:
                    distance = abs(current_price - support) / support
                    if distance < self.resistance_tolerance:
                        return False, f"❌ Soporte histórico detectado en {support:.5f} (distancia: {distance*100:.2f}%)"
            
            return True, None
            
        except Exception as e:
            # Si falla, permitir la operación (no bloquear por error)
            return True, None
    
    # 🆕 MEJORA 3: Confirmar reversión con velas
    def check_reversal_confirmation(self, df, action, bb_position):
        """
        Verifica que haya confirmación de reversión antes de operar
        
        Returns:
            (bool, str): (es_valido, mensaje)
        """
        try:
            if not self.require_reversal_confirmation:
                return True, None
            
            # Solo requerir confirmación en soportes/resistencias
            if bb_position not in ['LOWER', 'UPPER']:
                return True, None
            
            # Analizar últimas 3 velas
            last_candles = df.tail(3)
            
            if action == 1 and bb_position == 'LOWER':  # CALL en soporte
                # Contar velas alcistas (close > open)
                bullish_candles = (last_candles['close'] > last_candles['open']).sum()
                
                if bullish_candles < self.min_confirmation_candles:
                    return False, f"⏳ Esperando confirmación alcista ({bullish_candles}/{self.min_confirmation_candles} velas verdes)"
            
            elif action == 2 and bb_position == 'UPPER':  # PUT en resistencia
                # Contar velas bajistas (close < open)
                bearish_candles = (last_candles['close'] < last_candles['open']).sum()
                
                if bearish_candles < self.min_confirmation_candles:
                    return False, f"⏳ Esperando confirmación bajista ({bearish_candles}/{self.min_confirmation_candles} velas rojas)"
            
            return True, None
            
        except Exception as e:
            return True, None
    
    # 🆕 MEJORA 4: Analizar momentum
    def check_momentum_strength(self, df, action):
        """
        Verifica que no estemos operando contra un momentum muy fuerte
        
        Returns:
            (bool, str): (es_valido, mensaje)
        """
        try:
            # Calcular momentum de las últimas N velas
            recent_closes = df['close'].tail(self.momentum_lookback)
            momentum = recent_closes.diff().mean()
            
            # Calcular volatilidad para determinar si el momentum es "fuerte"
            volatility = df['close'].tail(self.momentum_lookback).std()
            
            # Momentum es "fuerte" si supera el umbral * volatilidad
            strong_momentum_threshold = volatility * self.strong_momentum_threshold
            
            # Verificar si operamos contra momentum fuerte
            if abs(momentum) > strong_momentum_threshold:
                if momentum > 0 and action == 2:  # Momentum alcista, queremos PUT
                    return False, f"❌ Momentum alcista muy fuerte ({momentum:.5f}), no hacer PUT"
                elif momentum < 0 and action == 1:  # Momentum bajista, queremos CALL
                    return False, f"❌ Momentum bajista muy fuerte ({momentum:.5f}), no hacer CALL"
            
            return True, None
            
        except Exception as e:
            return True, None

    # 🆕 MEJORA 6: Verificar volatilidad mínima
    def check_minimum_volatility(self, df):
        """
        Verifica que haya suficiente volatilidad para operar
        Evita operar en mercados planos (falsas alarmas)
        
        Returns:
            (bool, str, float): (es_valido, mensaje, atr_value)
        """
        try:
            if not self.require_min_volatility:
                return True, None, 0
            
            # Calcular ATR (Average True Range) - Medida estándar de volatilidad
            recent_data = df.tail(self.volatility_lookback)
            
            # True Range = max(high-low, abs(high-prev_close), abs(low-prev_close))
            high_low = recent_data['high'] - recent_data['low']
            high_close = abs(recent_data['high'] - recent_data['close'].shift(1))
            low_close = abs(recent_data['low'] - recent_data['close'].shift(1))
            
            true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            atr = true_range.mean()
            
            # Normalizar ATR por el precio actual (para comparar entre activos)
            current_price = df.iloc[-1]['close']
            atr_percentage = atr / current_price
            
            # Verificar si la volatilidad es suficiente
            if atr_percentage < self.min_volatility_atr:
                return False, f"⏸️ Volatilidad insuficiente (ATR: {atr_percentage*100:.3f}% < {self.min_volatility_atr*100:.3f}%) - Mercado plano", atr_percentage
            
            return True, None, atr_percentage
            
        except Exception as e:
            # Si falla el cálculo, permitir la operación (no bloquear por error)
            return True, None, 0
    
    # 🆕 MEJORA 6B: Verificar que el movimiento sea significativo
    def check_price_movement(self, df):
        """
        Verifica que haya movimiento de precio significativo en las últimas velas
        
        Returns:
            (bool, str): (es_valido, mensaje)
        """
        try:
            # Analizar últimas 10 velas
            last_10 = df.tail(10)
            
            # Calcular rango de precio (high - low) promedio
            avg_range = (last_10['high'] - last_10['low']).mean()
            current_price = df.iloc[-1]['close']
            
            # Rango debe ser al menos 0.03% del precio
            min_range = current_price * 0.0003
            
            if avg_range < min_range:
                return False, f"⏸️ Movimiento de precio insuficiente (rango: {avg_range:.5f} < {min_range:.5f}) - Mercado estancado"
            
            return True, None
            
        except Exception as e:
            return True, None
    
    # 🆕 MEJORA 7: Timing óptimo de entrada
    def detect_pullback(self, df, direction):
        """
        Detecta si hubo un pullback (retroceso) en las velas anteriores
        No en las últimas 2 velas (que deben ser el impulso)
        
        Returns:
            (bool, str): (hay_pullback, mensaje)
        """
        try:
            # Analizar velas 3-7 (antes del impulso)
            # Las últimas 2 velas deben ser el impulso, no el pullback
            last_10 = df.tail(10)
            pullback_window = last_10.iloc[-7:-2]  # Velas 3-7 desde el final
            
            if len(pullback_window) < 3:
                return True, None  # No hay suficientes datos, permitir
            
            if direction == 'CALL':
                # Para CALL, buscar retroceso bajista en velas 3-7
                # (antes del impulso alcista final)
                bearish_candles = (pullback_window['close'] < pullback_window['open']).sum()
                
                if bearish_candles >= self.min_pullback_candles:
                    return True, "✅ Pullback detectado (consolidación bajista antes de impulso)"
                else:
                    # Verificar si el precio está muy alto (sin retroceso)
                    current_price = df.iloc[-1]['close']
                    price_5_candles_ago = df.iloc[-6]['close']
                    
                    if current_price > price_5_candles_ago * 1.001:  # Subió >0.1% sin retroceso
                        return False, "⏳ Esperando pullback (precio subió sin retroceso)"
                    else:
                        return True, None  # Movimiento lateral, permitir
            
            elif direction == 'PUT':
                # Para PUT, buscar retroceso alcista en velas 3-7
                bullish_candles = (pullback_window['close'] > pullback_window['open']).sum()
                
                if bullish_candles >= self.min_pullback_candles:
                    return True, "✅ Pullback detectado (consolidación alcista antes de impulso)"
                else:
                    # Verificar si el precio está muy bajo (sin retroceso)
                    current_price = df.iloc[-1]['close']
                    price_5_candles_ago = df.iloc[-6]['close']
                    
                    if current_price < price_5_candles_ago * 0.999:  # Bajó >0.1% sin retroceso
                        return False, "⏳ Esperando pullback (precio bajó sin retroceso)"
                    else:
                        return True, None  # Movimiento lateral, permitir
            
            return False, "⚠️ Dirección no válida"
            
        except Exception as e:
            # Si falla, permitir la operación
            return True, None
    
    def confirm_momentum_impulse(self, df, direction):
        """
        Confirma que hay impulso (momentum) en la dirección correcta
        
        Returns:
            (bool, str, float): (hay_impulso, mensaje, fuerza)
        """
        try:
            # Calcular momentum de última vela
            last_candle = df.iloc[-1]
            
            # Tamaño de la vela actual
            candle_size = abs(last_candle['close'] - last_candle['open'])
            
            # Tamaño promedio de últimas 10 velas
            avg_candle_size = abs(df['close'].tail(10) - df['open'].tail(10)).mean()
            
            # Fuerza del impulso
            impulse_strength = candle_size / avg_candle_size if avg_candle_size > 0 else 0
            
            if direction == 'CALL':
                # Para CALL, última vela debe ser alcista y fuerte
                is_bullish = last_candle['close'] > last_candle['open']
                
                if is_bullish and impulse_strength >= self.min_impulse_strength:
                    return True, f"✅ Impulso alcista confirmado (fuerza: {impulse_strength:.2f}x)", impulse_strength
                elif is_bullish:
                    return False, f"⏳ Impulso débil (fuerza: {impulse_strength:.2f}x < {self.min_impulse_strength}x)", impulse_strength
                else:
                    return False, "❌ Última vela bajista, no hay impulso alcista", impulse_strength
            
            elif direction == 'PUT':
                # Para PUT, última vela debe ser bajista y fuerte
                is_bearish = last_candle['close'] < last_candle['open']
                
                if is_bearish and impulse_strength >= self.min_impulse_strength:
                    return True, f"✅ Impulso bajista confirmado (fuerza: {impulse_strength:.2f}x)", impulse_strength
                elif is_bearish:
                    return False, f"⏳ Impulso débil (fuerza: {impulse_strength:.2f}x < {self.min_impulse_strength}x)", impulse_strength
                else:
                    return False, "❌ Última vela alcista, no hay impulso bajista", impulse_strength
            
            return False, "⚠️ Dirección no válida", 0
            
        except Exception as e:
            return True, None, 0
    
    def wait_for_optimal_entry(self, df, direction):
        """
        Verifica si es el momento óptimo de entrada
        
        Returns:
            (bool, str): (entrar_ahora, razón)
        """
        try:
            if not self.require_optimal_timing:
                return True, None
            
            # 1. Verificar pullback
            has_pullback, pullback_msg = self.detect_pullback(df, direction)
            
            if not has_pullback:
                return False, pullback_msg
            
            # 2. Verificar impulso
            has_impulse, impulse_msg, strength = self.confirm_momentum_impulse(df, direction)
            
            if not has_impulse:
                return False, impulse_msg
            
            # 3. Verificar que no estamos en extremo
            last_price = df.iloc[-1]['close']
            
            if 'bb_high' in df.columns and 'bb_low' in df.columns:
                bb_high = df.iloc[-1]['bb_high']
                bb_low = df.iloc[-1]['bb_low']
                bb_mid = (bb_high + bb_low) / 2
                
                if direction == 'CALL':
                    # Para CALL, no entrar si ya está muy arriba
                    if last_price > bb_mid + (bb_high - bb_mid) * 0.5:
                        return False, "⚠️ Precio muy alto para CALL (cerca de BB superior)"
                
                elif direction == 'PUT':
                    # Para PUT, no entrar si ya está muy abajo
                    if last_price < bb_mid - (bb_mid - bb_low) * 0.5:
                        return False, "⚠️ Precio muy bajo para PUT (cerca de BB inferior)"
            
            # 4. TODO OK - Entrar ahora
            return True, f"🎯 TIMING ÓPTIMO - Pullback + Impulso ({strength:.2f}x) + Posición favorable"
            
        except Exception as e:
            # Si falla, permitir la operación
            return True, None
