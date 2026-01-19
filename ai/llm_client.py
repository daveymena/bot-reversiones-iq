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
        
        return {'is_optimal': True, 'confidence': 50, 'reasoning': 'Fallback Analysis'}

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
