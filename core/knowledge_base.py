"""
Knowledge Base - Sistema de Memoria a Largo Plazo
Almacena experiencias de trading y permite buscar situaciones similares del pasado
para evitar cometer los mismos errores.
"""
import json
import os
import numpy as np
import pandas as pd
from datetime import datetime
from config import Config

class KnowledgeBase:
    def __init__(self, db_path="data/knowledge_base.json"):
        self.db_path = db_path
        self.experiences = []
        self.load()
        
    def load(self):
        """Carga la base de conocimientos desde disco"""
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, 'r') as f:
                    self.experiences = json.load(f)
                print(f"📚 Base de conocimientos cargada: {len(self.experiences)} experiencias")
            except Exception as e:
                print(f"⚠️ Error cargando base de conocimientos: {e}")
                self.experiences = []
        else:
            print("📚 Creando nueva base de conocimientos")
            self.experiences = []
            
    def save(self):
        """Guarda la base de conocimientos en disco"""
        try:
            # Asegurar que el directorio existe
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            with open(self.db_path, 'w') as f:
                json.dump(self.experiences, f, indent=2)
        except Exception as e:
            print(f"❌ Error guardando base de conocimientos: {e}")

    def add_experience(self, context, result, analysis):
        """
        Agrega una nueva experiencia a la base de conocimientos
        
        Args:
            context: dict con indicadores y estado del mercado
            result: dict con resultado de la operación (won, profit)
            analysis: dict con análisis de por qué ganó/perdió
        """
        experience = {
            'id': len(self.experiences) + 1,
            'timestamp': datetime.now().isoformat(),
            'context': self._normalize_context(context),
            'result': result,
            'analysis': analysis
        }
        
        self.experiences.append(experience)
        self.save()
        print(f"🧠 Experiencia #{experience['id']} guardada en memoria a largo plazo")

    def find_similar_scenarios(self, current_context, limit=5, threshold=0.8):
        """
        Busca escenarios similares en el pasado
        
        Args:
            current_context: dict con indicadores actuales
            limit: máximo de resultados
            threshold: similitud mínima (0-1)
            
        Returns:
            list: Lista de experiencias similares
        """
        if not self.experiences:
            return []
            
        normalized_current = self._normalize_context(current_context)
        similar_scenarios = []
        
        for exp in self.experiences:
            similarity = self._calculate_similarity(normalized_current, exp['context'])
            
            if similarity >= threshold:
                similar_scenarios.append({
                    'similarity': similarity,
                    'experience': exp
                })
        
        # Ordenar por similitud descendente
        similar_scenarios.sort(key=lambda x: x['similarity'], reverse=True)
        
        return similar_scenarios[:limit]

    def get_win_probability(self, current_context):
        """
        Calcula la probabilidad de éxito basada en situaciones similares
        
        Returns:
            dict: {
                'probability': float (0-1),
                'confidence': float (0-1),
                'similar_count': int,
                'advice': str
            }
        """
        similar = self.find_similar_scenarios(current_context, limit=10, threshold=0.85)
        
        if not similar:
            return {
                'probability': 0.5,
                'confidence': 0.0,
                'similar_count': 0,
                'advice': "Situación nueva, sin datos históricos."
            }
            
        wins = sum(1 for s in similar if s['experience']['result']['won'])
        total = len(similar)
        prob = wins / total
        
        # Calcular confianza basada en cantidad de datos y similitud
        avg_similarity = sum(s['similarity'] for s in similar) / total
        confidence = min(1.0, (total / 5) * avg_similarity)
        
        advice = ""
        if prob > 0.7:
            advice = f"✅ Alta probabilidad de éxito ({prob*100:.0f}%) basada en {total} casos similares."
        elif prob < 0.3:
            advice = f"⛔ Alta probabilidad de fallo ({prob*100:.0f}%) basada en {total} casos similares."
        else:
            advice = f"⚠️ Probabilidad incierta ({prob*100:.0f}%) basada en {total} casos similares."
            
        return {
            'probability': prob,
            'confidence': confidence,
            'similar_count': total,
            'advice': advice
        }

    def _normalize_context(self, context):
        """Normaliza el contexto para comparación"""
        # Extraer solo lo relevante para comparación
        return {
            'rsi': float(context.get('rsi', 50)),
            'macd': float(context.get('macd', 0)),
            'bb_position': context.get('bb_position', 'UNKNOWN'),
            'trend': context.get('trend', 'UNKNOWN'),
            'momentum': context.get('momentum', 'UNKNOWN'),
            'volatility': context.get('volatility', 'UNKNOWN')
        }

    def _calculate_similarity(self, ctx1, ctx2):
        """Calcula similitud entre dos contextos (0-1)"""
        score = 0
        weights = 0
        
        # Comparar RSI (numérico) - Peso 3
        rsi_diff = abs(ctx1['rsi'] - ctx2['rsi'])
        rsi_score = max(0, 1 - (rsi_diff / 20)) # 20 puntos de diferencia es 0 similitud
        score += rsi_score * 3
        weights += 3
        
        # Comparar MACD (signo y magnitud relativa) - Peso 2
        # Simplificado: si tienen mismo signo, es similar
        if (ctx1['macd'] > 0 and ctx2['macd'] > 0) or (ctx1['macd'] < 0 and ctx2['macd'] < 0):
            score += 1 * 2
        elif abs(ctx1['macd']) < 0.0001 and abs(ctx2['macd']) < 0.0001: # Ambos cerca de 0
            score += 1 * 2
        weights += 2
        
        # Comparar Categóricos - Peso 2 c/u
        for field in ['bb_position', 'trend', 'momentum', 'volatility']:
            if ctx1.get(field) == ctx2.get(field):
                score += 1 * 2
            weights += 2
            
        return score / weights
