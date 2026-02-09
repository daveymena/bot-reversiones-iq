"""
Parser Inteligente de Señales usando LLM (Groq)
Interpreta mensajes complejos, extrae horarios exactos y valida lógica de trading.
"""
import os
import json
import re
from datetime import datetime, timedelta
from typing import Optional, Dict
from groq import Groq

class SmartSignalParser:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("Falta GROQ_API_KEY en .env")
            
        self.client = Groq(api_key=self.api_key)
        self.system_prompt = """
        Eres un experto analista de trading de opciones binarias.
        Tu tarea es leer mensajes de señales y extraer datos estructurados en JSON.
        
        Debes extraer:
        - "asset": El par de divisas (ej: "EURUSD-OTC", "GBPUSD"). Si no dice OTC pero es fin de semana o común, agrega "-OTC".
        - "direction": "CALL" (compra/sube) o "PUT" (venta/baja).
        - "expiration": Tiempo en minutos (ej: 5, 3, 1). Si no dice, asume 5.
        - "entry_time": Hora exacta de entrada en formato "HH:MM" (24h). Si el mensaje dice "YA" o "AHORA", pon "NOW".
        - "confidence": Nivel de confianza (0.0 a 1.0) basado en el texto (ej: "Probabilidad ALTA" -> 0.9).
        
        IMPORTANTE:
        - Si el mensaje incluye una hora específica (ej: "21:11", "9:00 PM"), úsala para "entry_time".
        - Si el mensaje no es una señal de trading, retorna un JSON con {"is_signal": false}.
        - Tu respuesta debe ser SOLO el JSON válido, sin markdown ni explicaciones.
        """

    def parse_with_ai(self, message: str) -> Optional[Dict]:
        """
        Usa Groq para entender el mensaje y extraer la señal
        """
        try:
            # Preparar prompt
            prompt = f"""
            Analiza este mensaje y extrae la señal:
            '''
            {message}
            '''
            
            Responde SOLO con el JSON.
            """
            
            # Llamar a Groq con Llama 3 (rápido y capaz)
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": self.system_prompt,
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model="llama3-70b-8192",  # Modelo potente para precisión
                temperature=0.1,  # Muy determinista
            )
            
            # Extraer respuesta
            response_content = chat_completion.choices[0].message.content
            
            # Limpiar posible markdown (```json ... ```)
            clean_json = response_content.replace("```json", "").replace("```", "").strip()
            
            data = json.loads(clean_json)
            
            if not data.get("is_signal", True):
                return None
                
            # Normalizar datos
            if "asset" in data:
                data["asset"] = data["asset"].upper().replace("/", "").replace(" ", "")
                if not data["asset"].endswith("-OTC") and "OTC" not in data["asset"]:
                    # Lógica simple: pares usuales
                    if len(data["asset"]) == 6:
                        data["asset"] += "-OTC"
            
            if "direction" in data:
                data["direction"] = data["direction"].lower()
            
            # Calcular segundos de espera si hay hora exacta
            if "entry_time" in data and data["entry_time"] != "NOW":
                data["seconds_to_wait"] = self._calculate_wait_time(data["entry_time"])
            else:
                data["seconds_to_wait"] = 0
                
            return data
            
        except Exception as e:
            print(f"❌ Error en SmartParser: {e}")
            return None

    def _calculate_wait_time(self, target_time_str: str) -> int:
        """
        Calcula cuántos segundos faltan para la hora objetivo
        target_time_str: "21:11" o "09:11 PM"
        """
        try:
            now = datetime.now()
            
            # Intentar parsear hora
            try:
                # Intento formato 24h
                target_time = datetime.strptime(target_time_str, "%H:%M").replace(
                    year=now.year, month=now.month, day=now.day
                )
            except ValueError:
                # Intento formato 12h
                 target_time = datetime.strptime(target_time_str, "%I:%M %p").replace(
                    year=now.year, month=now.month, day=now.day
                )
            
            # Si la hora ya pasó hace poco, podría ser para mañana (o error)
            # Asumimos que es para hoy.
            
            wait_seconds = (target_time - now).total_seconds()
            
            # Si la espera es negativa (ya pasó), pero por poco (ej: 30 seg), ejecutamos ya.
            # Si pasó por mucho, descartamos o asumimos error.
            if wait_seconds < -60: 
                return 0 # Ya pasó hace mucho, ejecutar YA o descartar (decisión de riesgo)
            
            return max(0, int(wait_seconds))
            
        except Exception as e:
            print(f"⚠️ Error calculando tiempo: {e}")
            return 0
