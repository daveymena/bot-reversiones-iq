import os
import requests
import json
import time
try:
    from groq import Groq
except ImportError:
    Groq = None

from config import Config

class LLMClient:
    def __init__(self):
        self.api_keys = Config.GROQ_API_KEYS if hasattr(Config, 'GROQ_API_KEYS') and Config.GROQ_API_KEYS else ([Config.GROQ_API_KEY] if Config.GROQ_API_KEY else [])
        self.current_key_index = 0
        self.use_groq = Config.USE_GROQ and len(self.api_keys) > 0
        self.groq_client = None
        self.last_error = None
        
        if self.use_groq:
            self._initialize_groq()
        else:
            print("[INFO] Groq desactivado o sin llaves. Usando Ollama como motor principal.")

    def _initialize_groq(self):
        if self.use_groq and Groq and self.current_key_index < len(self.api_keys):
            try:
                self.groq_client = Groq(api_key=self.api_keys[self.current_key_index])
                print(f"✅ Cliente Groq #{self.current_key_index + 1} inicializado correctamente.")
            except Exception as e:
                print(f"❌ Error inicializando Groq Key #{self.current_key_index + 1}: {e}")
                self._rotate_key()

    def _rotate_key(self):
        self.current_key_index += 1
        if self.current_key_index < len(self.api_keys):
            print(f"🔄 Rotando a llave Groq #{self.current_key_index + 1}...")
            self._initialize_groq()
        else:
            print("⚠️ Se agotaron las llaves de Groq. Cambiando a Ollama.")
            self.use_groq = False
            self.groq_client = None

    def ask_general(self, prompt):
        """Envía una consulta general al LLM."""
        return self._safe_query(prompt)

    def analyze_complete_trading_opportunity(self, market_data_summary, smart_money_analysis, learning_insights, asset, current_balance):
        """
        🧠 ANÁLISIS INTELIGENTE COMPLETO - Ollama como Cerebro Estratégico
        
        Ollama analiza:
        1. Contexto completo del mercado
        2. Patrones históricos de éxito/fracaso
        3. Confluencia de señales técnicas + Smart Money
        4. Timing óptimo de entrada
        5. Gestión de riesgo adaptativa
        """
        
        # Construir prompt inteligente con contexto completo
        prompt = f"""
Eres un TRADER INSTITUCIONAL EXPERTO con 15 años de experiencia en Smart Money Concepts y Price Action.

🎯 MISIÓN: Analizar esta oportunidad de trading y decidir si ejecutar o esperar.

📊 ACTIVO: {asset}
💰 BALANCE: ${current_balance:.2f}

═══════════════════════════════════════════════════════════════
📈 DATOS DE MERCADO:
{market_data_summary}

💎 ANÁLISIS SMART MONEY:
{smart_money_analysis}

🧠 APRENDIZAJE HISTÓRICO:
{learning_insights}
═══════════════════════════════════════════════════════════════

🎓 TU EXPERTISE - CRITERIOS DE DECISIÓN:

1. CONFLUENCIA DE SEÑALES (Peso: 40%)
   ✅ OPERAR si hay 3+ señales alineadas:
      - FVG (Fair Value Gap) sin llenar
      - Order Block institucional fresco
      - BOS (Break of Structure) confirmado
      - RSI en zona extrema (<30 o >70)
      - Momentum alineado con estructura
   ❌ RECHAZAR si solo hay 1-2 señales débiles

2. SMART MONEY STRUCTURE (Peso: 30%)
   ✅ OPERAR si detectas:
      - Precio mitigando FVG bullish/bearish
      - Liquidez disponible para el movimiento
      - Estructura de mercado clara (HH/HL o LH/LL)
   ❌ RECHAZAR si:
      - Precio en zona de consolidación
      - Estructura confusa o neutral

3. TIMING DE ENTRADA (Peso: 20%)
   ✅ OPERAR si:
      - Precio en zona de valor (no persiguiendo)
      - Retroceso a nivel clave completado
      - Confirmación de reversión presente
   ❌ RECHAZAR si:
      - Precio en extensión extrema
      - Falta confirmación de reversión

4. GESTIÓN DE RIESGO (Peso: 10%)
   ✅ OPERAR si:
      - R:R favorable (mínimo 1:1.5)
      - Stop loss claro identificable
   ❌ RECHAZAR si:
      - Riesgo excesivo o poco claro

═══════════════════════════════════════════════════════════════
⚡ MODO AGRESIVO ACTIVADO:
- Busca oportunidades de probabilidad media-alta (>55%)
- Opera cuando veas confluencia clara
- Prioriza calidad sobre cantidad
- Si hay duda razonable, OPERA (el mercado premia la acción)
═══════════════════════════════════════════════════════════════

📋 RESPONDE ÚNICAMENTE CON JSON VÁLIDO (sin markdown, sin explicaciones extra):
{{
    "should_trade": true/false,
    "direction": "CALL" o "PUT",
    "confidence": 50-95,
    "primary_reason": "Razón principal específica basada en Smart Money (máx 80 caracteres)",
    "risk_factors": ["factor1", "factor2"],
    "smart_money_signal": "strong/medium/weak",
    "suggested_expiration": 3-5,
    "risk_reward_ratio": 1.5-3.0
}}

IMPORTANTE: 
- Si hay 3+ señales alineadas → should_trade: true
- Si solo hay 1-2 señales → should_trade: false
- Confidence debe reflejar la fuerza de la confluencia
- Primary_reason debe ser específico y técnico
"""

        try:
            response = self._safe_query(prompt, timeout=15)
            
            # Limpiar respuesta y extraer JSON
            response = response.strip()
            
            # Buscar el JSON en la respuesta
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                try:
                    decision = json.loads(json_str)
                    
                    # Validar estructura
                    required_keys = ['should_trade', 'direction', 'confidence', 'primary_reason']
                    if all(key in decision for key in required_keys):
                        # Normalizar confidence a 0-100
                        if isinstance(decision['confidence'], (int, float)):
                            if decision['confidence'] <= 1.0:
                                decision['confidence'] = int(decision['confidence'] * 100)
                        
                        # Asegurar valores por defecto
                        decision.setdefault('risk_factors', [])
                        decision.setdefault('smart_money_signal', 'medium')
                        decision.setdefault('suggested_expiration', 3)
                        decision.setdefault('risk_reward_ratio', 1.5)
                        
                        return decision
                    
                except json.JSONDecodeError as e:
                    print(f"[ERROR] JSON inválido de Ollama: {e}")
                    print(f"[DEBUG] Respuesta: {json_str[:200]}")
            
            # Si llegamos aquí, hubo error en el parsing
            return {
                'should_trade': False,
                'direction': 'HOLD',
                'confidence': 0,
                'primary_reason': 'Error en análisis Ollama - Respuesta inválida',
                'risk_factors': ['Timeout o respuesta malformada'],
                'smart_money_signal': 'weak'
            }
            
        except Exception as e:
            print(f"[ERROR] Excepción en analyze_complete_trading_opportunity: {e}")
            return {
                'should_trade': False,
                'direction': 'HOLD',
                'confidence': 0,
                'primary_reason': f'Error en análisis Ollama: {str(e)[:50]}',
                'risk_factors': ['Error de conexión o timeout'],
                'smart_money_signal': 'weak'
            }
    
    def get_visual_description(self, df):
        """Convierte las últimas velas en una descripción visual para la IA"""
        if df.empty: return "Sin datos visuales."
        
        last_5 = df.tail(5)
        desc = []
        for i, (idx, row) in enumerate(last_5.iterrows()):
            color = "VERDE" if row['close'] > row['open'] else "ROJA"
            body_size = abs(row['close'] - row['open'])
            total_range = row['high'] - row['low']
            
            # Tamaño relativo (visual)
            size_desc = "Pequeña"
            if total_range > df['high'].diff().abs().mean() * 1.5: size_desc = "GRANDE"
            elif total_range < df['high'].diff().abs().mean() * 0.5: size_desc = "Diminuta (Doji)"
            
            # Mechas
            upper_wick = row['high'] - max(row['open'], row['close'])
            lower_wick = min(row['open'], row['close']) - row['low']
            wick_desc = ""
            if upper_wick > body_size * 0.5: wick_desc += "Mecha Superior Larga. "
            if lower_wick > body_size * 0.5: wick_desc += "Mecha Inferior Larga. "
            
            desc.append(f"Vela {i+1} ({color}, {size_desc}): {wick_desc}")
            
        return " | ".join(desc)

    def _get_recent_lessons(self):
        """Carga las lecciones aprendidas del historial del bot para entrenamiento continuo"""
        try:
            # Buscar en la carpeta data
            history_path = os.path.join(os.getcwd(), 'data', 'trade_history.json')
            if os.path.exists(history_path):
                with open(history_path, 'r') as f:
                    history = json.load(f)
                    # Extraer las últimas 5 lecciones clave (Wins y Losses)
                    lessons = []
                    for trade in reversed(history[-15:]):
                        if 'lessons' in trade and trade['lessons']:
                            status = "WIN ✅" if trade.get('won') else "LOSS ❌"
                            lessons.append(f"{status}: {trade['lessons'][0]}")
                    
                    if lessons:
                        return "\n".join(lessons[:6])
        except:
            pass
        return "Sin lecciones previas aún. Prioriza niveles institucionales (M15) y evita el agotamiento."

    def analyze_entry_timing(self, df, proposed_action, proposed_asset, extra_context=""):
        """
        Analiza el timing con enfoque VISUAL humano.
        """
        if df.empty or len(df) < 10:
            return {'is_optimal': True, 'confidence': 0.5, 'reasoning': "Sin datos"}
        
        visual_desc = self.get_visual_description(df)
        recent_lessons = self._get_recent_lessons()
        last = df.iloc[-1]
        
        # Calcular inercia reciente
        momentum = (last['close'] - df.iloc[-5]['close'])
        momentum_dir = "ALCISTA" if momentum > 0 else "BAJISTA"
        
        prompt = f"""
        ACTÚA COMO UN TRADER PROFESIONAL DE ÉLITE (SMC/Price Action).
        
        MEMORIA DE OPERACIONES (Lecciones de tus propios trades):
        {recent_lessons}
        
        TU MISIÓN: Detectar si esta entrada {proposed_action} es una TRAMPA o una OPORTUNIDAD REAL en {proposed_asset}.
        
        DESCRIPCIÓN VISUAL DEL GRÁFICO (M1):
        {visual_desc}
        
        DATOS DE BORDE (CRÍTICOS):
        - RSI (14): {last.get('rsi', 50):.1f}
        - Momento (5 velas): {momentum_dir}
        - Información de Contexto: {extra_context}
        
        REGLAS DE ORO (SMC/LIQUIDEZ):
        1. ¿TRAMPA DE LIQUIDEZ? Si hay un soporte/resistencia más fuerte MUY CERCA del actual, es probable que el mercado barra el primero para ir al segundo. RECHAZA (is_optimal=False).
        2. ¿BARRIDO DE STOPS (Sweep)? Si el precio acaba de romper un nivel y está regresando con fuerza y mecha larga, eso es ORO. ACEPTA (is_optimal=True).
        3. ¿NIVEL FRESCO O MITIGADO? Si el precio ha golpeado el nivel muchas veces, el muro está débil. Busca niveles "frescos" no tocados.
        4. No persigas velas gigantes de agotamiento. Espera el retroceso a la RAÍZ.
        
        RESPONDE ÚNICAMENTE CON ESTE JSON:
        {{
            "is_optimal": bool, (SOLO True si hay ventaja de precio y no chocamos con niveles)
            "confidence": 0-100,
            "reasoning": "Resumen técnico de 1 frase (ej: 'Nivel saturado, esperando retroceso válido')"
        }}
        """
        
        try:
            response = self._safe_query(prompt)
            # Limpieza básica
            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = response[start:end]
                try:
                    data = json.loads(json_str)
                except json.JSONDecodeError:
                    # Intento de reparación común: comillas simples
                    import ast
                    try:
                        data = ast.literal_eval(json_str)
                    except:
                        # Fallback a estructura regex o simple
                        print(f"[WARNING] Falló parseo JSON/AST de IA. Respuesta raw: {json_str[:50]}...")
                        return {'is_optimal': True, 'confidence': 60, 'reasoning': "Parse Error (Safe Default)"}

                is_optimal = data.get('is_optimal', False)
                if isinstance(is_optimal, str):
                    is_optimal = is_optimal.lower() == 'true'
                
                return {
                    'is_optimal': is_optimal,
                    'confidence': float(data.get('confidence', 50)),
                    'reasoning': data.get('reasoning', 'AI Visual Check')
                }
        except Exception as e:
            print(f"[WARNING] Error procesando respuesta AI: {e}")
            pass
        
        return {'is_optimal': False, 'confidence': 0.0, 'reasoning': 'Fallback: AI Error/Timeout'}

    def _safe_query(self, prompt, retries=1):
        """Intenta Groq con rotación, si falla usa Ollama"""
        if self.use_groq and self.groq_client:
            try:
                chat_completion = self.groq_client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": "Eres un analista de trading de élite. Responde de forma técnica, precisa y ultra-rápida."},
                        {"role": "user", "content": prompt}
                    ],
                    model="llama-3.3-70b-versatile", # Modelo más potente y rápido en Groq
                    temperature=0.1,
                    max_tokens=500,
                    timeout=10
                )
                return chat_completion.choices[0].message.content
            except Exception as e:
                print(f"⚠️ Error en Groq: {e}")
                self._rotate_key()
                if retries > 0:
                    return self._safe_query(prompt, retries - 1)
        
        # Fallback a Ollama
        return self._query_ollama(prompt)

    def _query_ollama(self, prompt):
        """Consulta mejorada a Ollama con mejor manejo de errores"""
        try:
            payload = {
                "model": Config.OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1, 
                    "num_ctx": 1024,
                    "top_p": 0.9,
                    "repeat_penalty": 1.1
                }
            }
            
            print(f"   🔗 Conectando a Ollama ({Config.OLLAMA_BASE_URL})...")
            
            # Timeout reducido y mejor manejo
            response = requests.post(
                Config.OLLAMA_URL, 
                json=payload, 
                timeout=20,  # Aumentado a 20s
                verify=False,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                ollama_response = result.get("response", "")
                
                if ollama_response and len(ollama_response.strip()) > 0:
                    print(f"   ✅ Ollama respondió ({len(ollama_response)} chars)")
                    return ollama_response
                else:
                    return "Error: Respuesta vacía de Ollama"
            else:
                return f"Error Ollama HTTP {response.status_code}: {response.text[:100]}"
                
        except requests.exceptions.Timeout:
            return "Error: Timeout conectando a Ollama (20s)"
        except requests.exceptions.ConnectionError:
            return "Error: No se puede conectar a Ollama en EasyPanel"
        except Exception as e:
            return f"Error conexión Ollama: {str(e)[:100]}"

    def analyze_complete_trading_opportunity(self, market_data_summary, smart_money_analysis, 
                                           learning_insights, asset, current_balance):
        prompt = f"""
        SISTEMA DE TRADING ULTRA-AGRESIVO (MODO BERSERKER TOTAL).
        Activo: {asset}. Data: {market_data_summary}. SMC: {smart_money_analysis}.
        
        INSTRUCCIONES CRÍTICAS:
        1. Tu objetivo es MÁXIMA FRECUENCIA de trading.
        2. Se te penalizará por ser conservador. SIEMPRE di 'should_trade': true si hay una probabilidad mínima de éxito (>45%).
        3. No busques la perfección. Busca el volumen de operaciones.
        4. Si es CALL o PUT y no es un desastre total, APRUÉBALA.
        
        Responde ÚNICAMENTE con JSON:
        {{
            "should_trade": true,
            "direction": "CALL/PUT",
            "confidence": 45-100,
            "primary_reason": "frase corta",
            "risk_factors": ["dato1", "dato2"]
        }}
        """
        try:
            response = self._safe_query(prompt)
            data = self._parse_trading_decision(response)
            # Garantizar campos mínimos
            if 'risk_factors' not in data: data['risk_factors'] = []
            if 'confluences' not in data: data['confluences'] = []
            return data
        except Exception as e:
            print(f"[ERROR] Error en análisis completo de Ollama: {e}")
            return self._get_safe_default_decision()

    def _parse_trading_decision(self, response):
        """Parsea la respuesta de decisión de trading de Ollama"""
        try:
            # Buscar JSON en la respuesta
            start = response.find('{')
            end = response.rfind('}') + 1
            
            if start >= 0 and end > start:
                json_str = response[start:end]
                
                try:
                    data = json.loads(json_str)
                except json.JSONDecodeError:
                    # Intento con ast.literal_eval para comillas simples
                    import ast
                    try:
                        data = ast.literal_eval(json_str)
                    except:
                        print(f"[WARNING] No se pudo parsear decisión de Ollama: {json_str[:100]}...")
                        return self._get_safe_default_decision()
                
                # Normalizar valores booleanos
                should_trade = data.get('should_trade', False)
                if isinstance(should_trade, str):
                    should_trade = should_trade.lower() in ['true', 'yes', 'si', '1']
                
                return {
                    'should_trade': should_trade,
                    'direction': data.get('direction'),
                    'confidence': float(data.get('confidence', 0)),
                    'position_size': float(data.get('position_size', 0)),
                    'primary_reason': data.get('primary_reason', 'Análisis Ollama'),
                    'confluences': data.get('confluences', []),
                    'risk_factors': data.get('risk_factors', []),
                    'market_phase': data.get('market_phase', 'ranging'),
                    'expected_outcome': data.get('expected_outcome', 'uncertain'),
                    'timing_quality': data.get('timing_quality', 'poor'),
                    'smart_money_signal': data.get('smart_money_signal', 'neutral')
                }
            
        except Exception as e:
            print(f"[ERROR] Error parseando decisión de Ollama: {e}")
        
        return self._get_safe_default_decision()

    
    def _get_aggressive_fallback_decision(self):
        """Decisión agresiva cuando Ollama falla - prioriza volumen"""
        return {
            'should_trade': True,  # Siempre operar en fallback
            'direction': 'CALL',   # Dirección por defecto
            'confidence': 60,      # Confianza media
            'position_size': 0,
            'primary_reason': 'Fallback agresivo - Ollama no disponible',
            'confluences': ['Fallback técnico'],
            'risk_factors': ['Sin análisis de IA'],
            'market_phase': 'ranging',
            'expected_outcome': 'uncertain',
            'timing_quality': 'medium',
            'smart_money_signal': 'neutral'
        }

    def _get_safe_default_decision(self):
        """Decisión segura por defecto cuando Ollama falla"""
        return {
            'should_trade': False,
            'direction': None,
            'confidence': 0,
            'position_size': 0,
            'primary_reason': 'Error en análisis de IA - modo seguro',
            'confluences': [],
            'risk_factors': ['Error de comunicación con Ollama'],
            'market_phase': 'ranging',
            'expected_outcome': 'uncertain',
            'timing_quality': 'poor',
            'smart_money_signal': 'neutral'
        }
