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
        self.api_keys = Config.GROQ_API_KEYS
        self.current_key_index = 0
        self.use_groq = len(self.api_keys) > 0
        self.groq_client = None
        self.last_error = None
        
        self._initialize_groq()

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

    def analyze_market(self, market_summary):
        """
        Envía un resumen del mercado al LLM y obtiene un consejo.
        """
        prompt = f"""
        Actúa como un experto trader de opciones binarias. Analiza los siguientes datos técnicos y dame una recomendación MUY BREVE (máximo 2 frases).
        
        Datos del Mercado:
        {market_summary}
        
        Tu respuesta debe seguir este formato:
        SENTIMIENTO: [ALCISTA/BAJISTA/NEUTRAL]
        CONSEJO: [Tu recomendación estratégica]
        """

        return self._safe_query(prompt)
    
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
                        {"role": "system", "content": "Eres un asistente de trading experto."},
                        {"role": "user", "content": prompt}
                    ],
                    model="llama-3.1-8b-instant",
                    timeout=8
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
        try:
            payload = {
                "model": Config.OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False
            }
            response = requests.post(Config.OLLAMA_URL, json=payload, timeout=45)
            if response.status_code == 200:
                return response.json().get("response", "Sin respuesta")
            else:
                return f"Error Ollama ({response.status_code})"
        except Exception as e:
            return f"Error conexión Ollama local: {e}"

    def analyze_complete_trading_opportunity(self, market_data_summary, smart_money_analysis, 
                                           learning_insights, asset, current_balance):
        """
        OLLAMA COMO ORQUESTADOR PRINCIPAL - Analiza toda la información y toma la decisión final
        """
        
        recent_lessons = self._get_recent_lessons()
        
        prompt = f"""
        ERES EL TRADER PROFESIONAL PRINCIPAL - TOMAS TODAS LAS DECISIONES DE TRADING

        ACTIVO: {asset}
        BALANCE ACTUAL: ${current_balance:.2f}

        === MEMORIA DE TUS OPERACIONES ANTERIORES ===
        {recent_lessons}

        === ANÁLISIS TÉCNICO COMPLETO ===
        {market_data_summary}

        === ANÁLISIS SMART MONEY CONCEPTS ===
        {smart_money_analysis}

        === INSIGHTS DE APRENDIZAJE PROFESIONAL ===
        {learning_insights}

        === TU MISIÓN COMO TRADER PROFESIONAL ===
        
        Analiza TODA esta información como un trader institucional y decide:
        
        1. ¿HAY UNA OPORTUNIDAD REAL DE TRADING?
        2. ¿QUÉ DIRECCIÓN (CALL/PUT)?
        3. ¿CUÁL ES TU NIVEL DE CONFIANZA?
        4. ¿CUÁNTO ARRIESGAR?

        CONCEPTOS CLAVE A EVALUAR:
        - Order Blocks frescos vs mitigados
        - Fair Value Gaps sin llenar
        - Zonas de liquidez institucional
        - Break of Structure (BOS) vs Change of Character (CHoCH)
        - Inducement patterns (trampas de liquidez)
        - Timing de entrada óptimo
        - Confluencias múltiples

        REGLAS DE ORO:
        1. SOLO opera si hay al menos 3 confluencias
        2. EVITA niveles saturados (muchos toques)
        3. BUSCA niveles frescos institucionales
        4. NO persigas el precio - espera retrocesos
        5. CONFIRMA la dirección con estructura de mercado
        6. RESPETA el risk management (máximo 2% por trade)

        RESPONDE ÚNICAMENTE CON ESTE JSON:
        {{
            "should_trade": true/false,
            "direction": "CALL"/"PUT"/null,
            "confidence": 0-100,
            "position_size": 0.0,
            "primary_reason": "Razón principal en 1 frase",
            "confluences": ["lista", "de", "confluencias", "detectadas"],
            "risk_factors": ["lista", "de", "riesgos", "identificados"],
            "market_phase": "accumulation/markup/distribution/markdown/ranging",
            "expected_outcome": "win"/"loss"/"uncertain",
            "timing_quality": "excellent"/"good"/"poor",
            "smart_money_signal": "bullish"/"bearish"/"neutral"
        }}
        """
        
        try:
            response = self._safe_query(prompt)
            return self._parse_trading_decision(response)
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
