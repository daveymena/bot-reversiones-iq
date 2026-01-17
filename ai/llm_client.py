import os
import requests
import json
try:
    from groq import Groq
except ImportError:
    Groq = None

from config import Config

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
    
    def analyze_entry_timing(self, df, proposed_action, proposed_asset, extra_context=""):
        """
        Analiza el timing óptimo de entrada con un rol de 'Abogado del Diablo'.
        Su objetivo es encontrar razones para NO entrar y evitar trampas.
        """
        if df.empty or len(df) < 10:
            return {'is_optimal': True, 'confidence': 0.5, 'reasoning': "Sin datos"}
        
        last = df.iloc[-1]
        prev = df.iloc[-2]
        
        # Calcular inercia reciente
        momentum = (last['close'] - df.iloc[-5]['close'])
        momentum_dir = "ALCISTA" if momentum > 0 else "BAJISTA"
        
        prompt = f"""
        INSTRUCCIONES: Eres un TRADER ESCÉPTICO. Tu meta es evitar "Bull/Bear Traps".
        
        DATOS ACTUALES:
        - Activo: {proposed_asset}
        - Acción Propuesta: {proposed_action}
        - RSI: {last.get('rsi', 50):.1f}
        - Momentum (5 velas): {momentum_dir}
        - Precio: {last['close']:.5f}
        - Contexto Extra: {extra_context}
        
        REGLAS DE ORO:
        1. No entres en CALL si el momentum es bajista agresivo.
        2. No entres en PUT si el momentum es alcista agresivo.
        3. Si el RSI está cerca de 50, es zona de azar (NO OPTIMO).
        
        RESPONDE SOLO EN FORMATO JSON:
        {{
            "is_optimal": bool,
            "confidence_score": 0-100,
            "reasoning": "Resumen de por qué es óptimo o por qué es una trampa"
        }}
        """
        
        try:
            response = self._safe_query(prompt)
            # Limpieza básica para modelos pequeños que hablan demás
            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = response[start:end]
                data = json.loads(json_str)
                return {
                    'is_optimal': data.get('momento_optimo', True),
                    'confidence': data.get('confianza_entrada', 50) / 100,
                    'recommended_expiration': 1,
                    'wait_time': 0, # Simplificado para evitar alucinaciones
                    'reasoning': data.get('razonamiento', 'AI Check OK')
                }
        except:
            pass
        
        return {'is_optimal': True, 'confidence': 0.5, 'recommended_expiration': 1, 'wait_time': 0, 'reasoning': 'Análisis simple'}

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
            response = requests.post(Config.OLLAMA_URL, json=payload, timeout=12)
            if response.status_code == 200:
                return response.json().get("response", "Sin respuesta")
            else:
                return f"Error Ollama ({response.status_code})"
        except Exception as e:
            return f"Error conexión Ollama local: {e}"
