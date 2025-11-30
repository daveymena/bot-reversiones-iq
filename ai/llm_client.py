import os
import requests
import json
try:
    from groq import Groq
except ImportError:
    Groq = None

from config import Config

class LLMClient:
    def __init__(self):
        self.use_groq = bool(Config.GROQ_API_KEY)
        self.groq_client = None
        
        if self.use_groq and Groq:
            try:
                self.groq_client = Groq(api_key=Config.GROQ_API_KEY)
                print("✅ Cliente Groq inicializado.")
            except Exception as e:
                print(f"Error inicializando Groq: {e}")
                self.use_groq = False
        
        if not self.use_groq:
            print("ℹ️ Usando Ollama (Local) como backend de IA.")

    def analyze_market(self, market_summary):
        """
        Envía un resumen del mercado al LLM y obtiene un consejo.
        market_summary: str con datos técnicos (RSI, Tendencia, etc.)
        """
        prompt = f"""
        Actúa como un experto trader de opciones binarias. Analiza los siguientes datos técnicos y dame una recomendación MUY BREVE (máximo 2 frases).
        
        Datos del Mercado:
        {market_summary}
        
        Tu respuesta debe seguir este formato:
        SENTIMIENTO: [ALCISTA/BAJISTA/NEUTRAL]
        CONSEJO: [Tu recomendación estratégica]
        """

        if self.use_groq and self.groq_client:
            return self._query_groq(prompt)
        else:
            # Usar modelo rápido para análisis de mercado general
            return self._query_ollama(prompt, use_fast_model=True)
    
    def analyze_entry_timing(self, df, proposed_action, proposed_asset, expiration_minutes=1):
        """
        🎯 GROQ COMO ANALISTA EXPERTO DE TIMING
        
        Analiza:
        1. ¿Es AHORA el momento óptimo de entrada?
        2. ¿Cuántos segundos esperar para entrada perfecta?
        3. ¿Qué tiempo de expiración maximiza probabilidad de éxito?
        4. ¿Qué tan favorable es esta operación?
        
        Args:
            df: DataFrame con datos e indicadores
            proposed_action: Acción propuesta (CALL/PUT)
            proposed_asset: Activo a operar
            expiration_minutes: Tiempo de expiración propuesto
            
        Returns:
            dict: {
                'is_optimal': bool,
                'confidence': float (0-1),
                'recommended_expiration': int (minutos),
                'wait_time': int (segundos),
                'reasoning': str
            }
        """
        if df.empty or len(df) < 20:
            return {
                'is_optimal': False,
                'confidence': 0,
                'recommended_expiration': 1,
                'wait_time': 0,
                'reasoning': "Datos insuficientes"
            }
        
        # Preparar contexto detallado
        last = df.iloc[-1]
        prev = df.iloc[-2] if len(df) >= 2 else last
        
        # Calcular cambios recientes
        price_change = ((last['close'] - prev['close']) / prev['close']) * 100
        rsi_change = last.get('rsi', 50) - prev.get('rsi', 50)
        
        # Volatilidad reciente
        recent_volatility = df['close'].tail(10).std()
        avg_volatility = df['close'].std()
        
        # Detectar momentum
        momentum = "FUERTE" if abs(price_change) > 0.05 else "MODERADO" if abs(price_change) > 0.02 else "DÉBIL"
        
        # Detectar tendencia
        sma_20 = df['close'].tail(20).mean()
        trend = "ALCISTA" if last['close'] > sma_20 else "BAJISTA"
        
        prompt = f"""
Eres un ANALISTA EXPERTO de timing en opciones binarias. Tu trabajo es OPTIMIZAR el momento de entrada y tiempo de expiración.

📊 SITUACIÓN ACTUAL:
Activo: {proposed_asset}
Acción propuesta: {proposed_action}
Precio: {last['close']:.5f}
Cambio último minuto: {price_change:.3f}%
Momentum: {momentum}
Tendencia: {trend}

📈 INDICADORES TÉCNICOS:
RSI: {last.get('rsi', 50):.1f} (cambio: {rsi_change:.1f})
MACD: {last.get('macd', 0):.5f}
ATR: {last.get('atr', 0):.5f}
Volatilidad reciente: {recent_volatility:.5f}
Volatilidad promedio: {avg_volatility:.5f}

🎯 TU MISIÓN:
1. ¿Es AHORA el momento PERFECTO para {proposed_action}?
2. Si no, ¿cuántos segundos esperar? (0-60s)
3. ¿Qué expiración maximiza éxito? (1-5 min)
4. ¿Confianza en esta entrada? (0-100%)

CRITERIOS:
- Momentum fuerte + RSI extremo = entrada inmediata
- Volatilidad alta = expiración más corta (1 min)
- Tendencia clara = expiración más larga (3-5 min)
- Momentum débil = esperar confirmación

Responde SOLO en formato JSON:
{{
    "momento_optimo": true/false,
    "esperar_segundos": 0-60,
    "expiracion_minutos": 1-5,
    "confianza_entrada": 0-100,
    "razonamiento": "máximo 15 palabras"
}}
"""
        
        try:
            if self.use_groq and self.groq_client:
                response = self._query_groq(prompt)
            else:
                response = self._query_ollama(prompt)
            
            # Intentar parsear JSON
            import json
            # Extraer JSON de la respuesta
            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = response[start:end]
                data = json.loads(json_str)
                
                return {
                    'is_optimal': data.get('momento_optimo', False),
                    'confidence': data.get('confianza_entrada', 0) / 100,
                    'recommended_expiration': data.get('expiracion_minutos', 1),
                    'wait_time': data.get('esperar_segundos', 0),
                    'reasoning': data.get('razonamiento', '')
                }
            else:
                # Fallback si no puede parsear
                return {
                    'is_optimal': True,
                    'confidence': 0.5,
                    'recommended_expiration': 1,
                    'wait_time': 0,
                    'reasoning': 'No se pudo analizar timing'
                }
        except Exception as e:
            print(f"Error en análisis de timing: {e}")
            return {
                'is_optimal': True,
                'confidence': 0.5,
                'recommended_expiration': 1,
                'wait_time': 0,
                'reasoning': f'Error: {e}'
            }

    def get_consensus_decision(self, market_summary, asset):
        """
        🤖 CONSENSO MULTI-AGENTE
        Simula 3 expertos debatiendo la operación:
        1. El Estratega (Tendencia macro)
        2. El Francotirador (Timing micro)
        3. El Gestor de Riesgo (Capital y Probabilidad)
        
        Returns:
            dict: {
                'consensus': 'CALL'/'PUT'/'HOLD',
                'confidence': float,
                'votes': dict,
                'reasoning': str
            }
        """
        prompt = f"""
        Actúa como un COMITÉ DE TRADING de 3 expertos analizando {asset}.
        
        DATOS DEL MERCADO:
        {market_summary}
        
        PERSONAS:
        1. 🧠 EL ESTRATEGA: Analiza la tendencia general y estructura. Si la tendencia es débil, vota HOLD.
        2. 🎯 EL FRANCOTIRADOR: Analiza el punto exacto de entrada. Si el timing no es perfecto, vota HOLD.
        3. 🛡️ EL GESTOR DE RIESGO: Analiza volatilidad y probabilidad. Si el riesgo es alto, vota HOLD.
        
        TU MISIÓN:
        Simula el debate y llega a un CONSENSO.
        
        REGLAS:
        - Para operar (CALL/PUT), se necesitan al menos 2 votos a favor y NINGÚN veto del Gestor de Riesgo.
        - Si hay duda, el consenso es HOLD.
        
        Responde SOLO en JSON:
        {{
            "voto_estratega": "CALL/PUT/HOLD",
            "razon_estratega": "breve motivo",
            "voto_francotirador": "CALL/PUT/HOLD",
            "razon_francotirador": "breve motivo",
            "voto_riesgo": "CALL/PUT/HOLD",
            "razon_riesgo": "breve motivo",
            "decision_final": "CALL/PUT/HOLD",
            "confianza_consenso": 0-100,
            "explicacion_final": "resumen del consenso"
        }}
        """
        
        try:
            if self.use_groq and self.groq_client:
                response = self._query_groq(prompt)
            else:
                response = self._query_ollama(prompt)
                
            # Parsear JSON
            import json
            import re
            
            # Limpiar respuesta
            response = response.strip()
            response = re.sub(r'```json\s*', '', response)
            response = re.sub(r'```\s*', '', response)
            
            start = response.find('{')
            end = response.rfind('}') + 1
            
            if start >= 0 and end > start:
                json_str = response[start:end]
                data = json.loads(json_str)
                
                return {
                    'consensus': data.get('decision_final', 'HOLD'),
                    'confidence': data.get('confianza_consenso', 0) / 100,
                    'votes': {
                        'strategist': data.get('voto_estratega'),
                        'sniper': data.get('voto_francotirador'),
                        'risk_manager': data.get('voto_riesgo')
                    },
                    'reasoning': data.get('explicacion_final', '')
                }
            else:
                return {
                    'consensus': 'HOLD',
                    'confidence': 0,
                    'votes': {},
                    'reasoning': "Error parseando consenso"
                }
                
        except Exception as e:
            print(f"Error en consenso multi-agente: {e}")
            return {
                'consensus': 'HOLD',
                'confidence': 0,
                'votes': {},
                'reasoning': f"Error: {e}"
            }

    def _query_groq(self, prompt):
        try:
            chat_completion = self.groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "Eres un sistema experto de trading financiero. Responde SOLO en JSON."},
                    {"role": "user", "content": prompt}
                ],
                model="llama-3.1-8b-instant",
                temperature=0.1 # Baja temperatura para respuestas más estructuradas
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            return f"Error Groq: {e}"

    def _query_ollama(self, prompt, use_fast_model=False):
        try:
            model = Config.OLLAMA_MODEL_FAST if use_fast_model and hasattr(Config, 'OLLAMA_MODEL_FAST') else Config.OLLAMA_MODEL
            
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "num_ctx": 4096 # Aumentar contexto
                }
            }
            # Timeout aumentado a 120s como solicitó el usuario
            response = requests.post(Config.OLLAMA_URL, json=payload, timeout=120)
            
            if response.status_code == 200:
                return response.json().get("response", "Sin respuesta")
            else:
                return f"Error Ollama: {response.status_code} - {response.text}"
        except requests.exceptions.Timeout:
            return "Error Ollama: Timeout (120s)"
        except Exception as e:
            return f"Error conexión Ollama: {e}"
