
import json
import pandas as pd
from pathlib import Path
from datetime import datetime

class KnowledgeOptimizer:
    def __init__(self, db_path="data/learning_database.json"):
        self.db_path = Path(db_path)
        with open(self.db_path, 'r', encoding='utf-8') as f:
            self.db = json.load(f)

    def analyze_patterns(self):
        ops = self.db.get('operations', [])
        if not ops:
            return "No hay operaciones para analizar."

        # Convertir a DataFrame para análisis fácil
        records = []
        for op in ops:
            # Manejar diferentes formatos de grabación
            strat = op.get('strategy', {})
            move = op.get('movement', {})
            
            record = {
                'asset': op.get('asset'),
                'action': strat.get('action'),
                'strategy_name': strat.get('strategy'),
                'confidence': strat.get('confidence'),
                'executed': op.get('executed', False),
                'result': op.get('result'),
                'profit': op.get('profit', 0),
                'volatility': move.get('volatility_pct', 0),
                'trend': move.get('trend', 'LATERAL'),
                'adx': strat.get('details', {}).get('adx', 0)
            }
            records.append(record)

        df = pd.DataFrame(records)
        executed_df = df[df['executed'] == True].copy()
        
        patterns = {
            'best_assets': {},
            'volatility_correlation': {},
            'strategy_performance': {},
            'last_update': datetime.now().isoformat()
        }

        if not executed_df.empty:
            # Rendimiento por activo
            asset_perf = executed_df.groupby('asset')['profit'].sum().to_dict()
            patterns['best_assets'] = asset_perf

            # Rendimiento por estrategia
            strat_perf = executed_df.groupby('strategy_name').apply(
                lambda x: (x['result'] == 'win').sum() / len(x) if len(x) > 0 else 0
            ).to_dict()
            patterns['strategy_performance'] = strat_perf

            # Analizar correlación de volatilidad
            wins = executed_df[executed_df['result'] == 'win']
            if not wins.empty:
                patterns['volatility_correlation']['avg_win_volatility'] = wins['volatility'].mean()
                patterns['volatility_correlation']['min_win_volatility'] = wins['volatility'].min()

        # Actualizar base de datos
        self.db['patterns_found'] = patterns
        
        # Guardar cambios
        with open(self.db_path, 'w', encoding='utf-8') as f:
            json.dump(self.db, f, indent=2)

        return patterns

if __name__ == "__main__":
    optimizer = KnowledgeOptimizer()
    results = optimizer.analyze_patterns()
    print("✅ Patrones analizados y base de datos actualizada.")
    print(json.dumps(results, indent=2))
