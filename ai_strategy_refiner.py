
"""
🧠 AI STRATEGY REFINER - EL CEREBRO ANALÍTICO DEL BOT
Este módulo permite que la IA (Ollama) analice el historial completo de operaciones,
identifique por qué se está perdiendo y genere "Reglas de Oro" dinámicas.
"""
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from ai.llm_client import LLMClient
import sys

class AIStrategyRefiner:
    def __init__(self, db_path="data/learning_database.json"):
        self.db_path = Path(db_path)
        self.llm = LLMClient()
        self.meta_rules_path = Path("data/meta_rules.json")

    def analyze_and_evolve(self):
        print("\n" + "═"*80)
        print("🤖 INICIANDO PROCESO DE AUTO-EVOLUCIÓN DE LA IA")
        print("═"*80)

        if not self.db_path.exists():
            return "No hay base de datos para analizar."

        with open(self.db_path, 'r', encoding='utf-8') as f:
            db = json.load(f)

        ops = db.get('operations', [])
        if len(ops) < 10:
            return "Datos insuficientes para evolución (mínimo 10 operaciones)."

        # 1. Preparar Digest de Estadísticas para la IA
        digest = self._generate_statistics_digest(ops)
        
        # 2. Consultar a la IA como "Arquitecto Senior de Sistemas"
        evolution_prompt = f"""
        ERES EL ARQUITECTO DE SISTEMAS Y JEFE DE TRADING. 
        Tu misión es analizar el fracaso de este bot y reconstruir su lógica de mercado.
        
        DATOS REALES DEL ÚLTIMO DESEMPEÑO:
        {json.dumps(digest, indent=2)}
        
        INSTRUCCIONES:
        1. Identifica qué PATRÓN LÓGICO está fallando (ej: estamos comprando en caídas que no se detienen).
        2. Define "REGLAS DE ORO" para el filtrado técnico.
        3. Genera una respuesta EXCLUSIVAMENTE EN FORMATO JSON que el bot pueda leer.

        FORMATO REQUERIDO (JSON):
        {{
            "analysis": "Breve explicación de por qué perdemos tanto",
            "forbidden_patterns": ["patron1", "patron2"],
            "dynamic_adjustments": {{
                "asset_rigidity": {{ "EURUSD": 0.9, "GLOBAL": 1.0 }},
                "rsi_extra_buffer": 5,
                "min_confidence_override": 80
            }},
            "market_view_shift": "Cómo debe ver el bot el mercado ahora"
        }}
        """
        
        print("🧠 IA analizando historial de fallos y éxitos...")
        try:
            # Usamos el cliente LLM para una respuesta estructurada
            response_text = self.llm.ask_general(evolution_prompt)
            print(f"🤖 RAW AI Response received ({len(response_text)} chars)")
            
            # Intentar extraer el JSON si la IA puso texto alrededor
            if "{" in response_text:
                start_idx = response_text.find("{")
                end_idx = response_text.rfind("}") + 1
                json_str = response_text[start_idx:end_idx]
                
                try:
                    meta_rules = json.loads(json_str)
                    
                    # 3. Guardar las nuevas Reglas de Oro
                    meta_rules['updated_at'] = datetime.now().isoformat()
                    self.meta_rules_path.parent.mkdir(exist_ok=True)
                    with open(self.meta_rules_path, 'w', encoding='utf-8') as f:
                        json.dump(meta_rules, f, indent=2)
                    
                    print(f"✅ EVOLUCIÓN COMPLETADA: Nuevas Meta-Reglas aplicadas.")
                    print(f"📝 Análisis de la IA: {meta_rules.get('analysis', 'Sin análisis')}")
                    return meta_rules
                except json.JSONDecodeError as je:
                    print(f"❌ Error decodificando JSON de la IA: {je}")
                    print(f"Contenido problemático: {json_str[:200]}...")
            else:
                print("❌ La IA no devolvió un formato JSON válido (falta {).")
                print(f"Respuesta recibida: {response_text[:200]}...")
        except Exception as e:
            print(f"❌ Error en evolución: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _generate_statistics_digest(self, ops):
        df = pd.DataFrame(ops)
        # Limpieza básica
        if 'result' not in df.columns: return "Error: Sin resultados"
        
        wins = df[df['result'] == 'win']
        losses = df[df['result'] == 'loose']
        
        # Agrupar por razón de falla
        reasons_fail = []
        for op in ops:
            if op.get('result') == 'loose':
                reasons_fail.append(op.get('strategy', {}).get('reason', 'N/A'))

        digest = {
            "total_ops": len(df),
            "win_rate": (len(wins) / len(df)) * 100 if len(df) > 0 else 0,
            "top_losing_assets": df[df['result'] == 'loose']['asset'].value_counts().head(3).to_dict(),
            "frequent_failure_reasons": pd.Series(reasons_fail).value_counts().head(5).to_dict(),
            "avg_confidence_on_losses": df[df['result'] == 'loose'].apply(lambda x: x['strategy'].get('confidence', 0) if isinstance(x['strategy'], dict) else 0, axis=1).mean()
        }
        return digest

if __name__ == "__main__":
    refiner = AIStrategyRefiner()
    refiner.analyze_and_evolve()
