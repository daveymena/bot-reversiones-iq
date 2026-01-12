
import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

class KnowledgeOptimizer:
    """
    Optimizador avanzado que aprende de los errores para mejorar la precisión.
    Clasifica operaciones y ajusta rigurosidad basándose en resultados reales.
    """
    def __init__(self, db_path="data/learning_database.json"):
        self.db_path = Path(db_path)
        self.load_db()

    def load_db(self):
        if self.db_path.exists():
            with open(self.db_path, 'r', encoding='utf-8') as f:
                self.db = json.load(f)
        else:
            self.db = {'operations': [], 'patterns_found': {}}

    def analyze_patterns(self):
        ops = self.db.get('operations', [])
        if not ops:
            return "No hay operaciones para analizar."

        # Convertir a DataFrame
        records = []
        for op in ops:
            if not op.get('executed'): continue
            
            strat = op.get('strategy', {})
            details = strat.get('details', {})
            
            record = {
                'id': op.get('id'),
                'asset': op.get('asset'),
                'result': op.get('result', 'unknown'),
                'strategy': strat.get('strategy'),
                'action': strat.get('action'),
                'confidence': strat.get('confidence'),
                'rsi': details.get('rsi', 50),
                'hour': datetime.fromisoformat(op['timestamp']).hour,
                'profit': op.get('profit', 0)
            }
            records.append(record)

        if not records:
            return "No hay operaciones ejecutadas."

        df = pd.DataFrame(records)
        
        patterns = {
            'best_assets': {},
            'dangerous_hours': [],
            'rsi_thresholds': {},
            'forbidden_strategies': [],
            'last_update': datetime.now().isoformat()
        }

        # 1. Clasificar Activos: Estrellas vs Tóxicos
        asset_stats = df.groupby('asset').agg({
            'result': lambda x: (x == 'win').sum() / len(x),
            'profit': 'sum',
            'id': 'count'
        }).rename(columns={'id': 'count', 'result': 'win_rate'})
        
        # Activos con WR < 40% y pérdidas netas son "tóxicos"
        toxic_assets = asset_stats[(asset_stats['win_rate'] < 0.4) & (asset_stats['profit'] < 0)].index.tolist()
        patterns['toxic_assets'] = toxic_assets
        
        # Activos Estrellas (WR > 60%)
        star_assets = asset_stats[asset_stats['win_rate'] > 0.6].index.tolist()
        patterns['best_assets'] = star_assets

        # 2. Análisis de Rigurosidad por Estrategia (RSI)
        # Si perdemos mucho en reversiones, ajustamos el RSI de entrada
        reversals = df[df['strategy'].str.contains('Reversal', na=False)]
        if not reversals.empty:
            # Analizar CALLs perdidos (reversión alcista)
            failed_calls = reversals[(reversals['action'] == 'CALL') & (reversals['result'] == 'loose')]
            if not failed_calls.empty:
                # El RSI promedio de las fallas nos dice dónde NO entrar
                avg_fail_rsi = failed_calls['rsi'].mean()
                # Sugerimos ser más estrictos: entrar más abajo
                safe_rsi_call = avg_fail_rsi - 5
                patterns['rsi_thresholds']['CALL'] = max(20, safe_rsi_call)
            
            # Analizar PUTs perdidos (reversión bajista)
            failed_puts = reversals[(reversals['action'] == 'PUT') & (reversals['result'] == 'loose')]
            if not failed_puts.empty:
                avg_fail_rsi = failed_puts['rsi'].mean()
                safe_rsi_put = avg_fail_rsi + 5
                patterns['rsi_thresholds']['PUT'] = min(80, safe_rsi_put)

        # 3. Horarios Peligrosos
        # Horas donde el WR es < 40%
        hourly_stats = df.groupby('hour')['result'].apply(lambda x: (x == 'win').sum() / len(x))
        patterns['dangerous_hours'] = hourly_stats[hourly_stats < 0.4].index.tolist()

        # 4. Estrategias Fallidas
        strat_stats = df.groupby('strategy')['result'].apply(lambda x: (x == 'win').sum() / len(x))
        patterns['forbidden_strategies'] = strat_stats[strat_stats < 0.35].index.tolist()

        # 5. Análisis Post-Mortem de Tendencia (HTF Failure Analysis)
        # Analizar si las pérdidas ocurren sistemáticamente contra la tendencia mayor
        post_mortem_records = []
        for op in ops:
            if op.get('result') == 'loose' and 'mtf_context' in op:
                mtf = op['mtf_context']
                action = op.get('strategy', {}).get('action')
                trend_m30 = mtf.get('trend_m30')
                
                # ¿Fue contra-tendencia?
                is_counter = (action == 'CALL' and trend_m30 == 'DOWNTREND') or \
                             (action == 'PUT' and trend_m30 == 'UPTREND')
                
                if is_counter:
                    post_mortem_records.append(1)
        
        # Si más del 50% de las pérdidas recientes son por contra-tendencia, activar filtro estricto
        patterns['strict_trend_filter'] = len(post_mortem_records) > 5
        if patterns['strict_trend_filter']:
            patterns['forbidden_strategies'].append("Counter-Trend Operations")

        # Guardar insights
        self.db['patterns_found'] = patterns
        self.save_db()
        
        return patterns

    def save_db(self):
        with open(self.db_path, 'w', encoding='utf-8') as f:
            json.dump(self.db, f, indent=2, default=str)

    def get_refinements_for_asset(self, asset):
        """Devuelve ajustes específicos para un activo"""
        patterns = self.db.get('patterns_found', {})
        
        refinements = {
            'is_toxic': asset in patterns.get('toxic_assets', []),
            'is_star': asset in patterns.get('best_assets', []),
            'rsi_adjust': patterns.get('rsi_thresholds', {}),
            'caution_mode': False
        }
        
        if refinements['is_toxic']:
            refinements['caution_mode'] = True
            
        return refinements

if __name__ == "__main__":
    opt = KnowledgeOptimizer()
    res = opt.analyze_patterns()
    print(json.dumps(res, indent=2))
