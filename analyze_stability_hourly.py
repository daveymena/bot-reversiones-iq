
"""
📊 ANALIZADOR DE ESTABILIDAD POR HORAS Y ESTRATEGIAS
Identifica qué horarios son más seguros y qué estrategias rinden mejor en cada franja.
"""
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
import sys

def analyze_stability():
    # Asegurar codificación UTF-8
    if sys.stdout.encoding != 'utf-8':
        try: sys.stdout.reconfigure(encoding='utf-8')
        except: pass

    learning_file = Path("data/learning_database.json")
    if not learning_file.exists():
        print("❌ No se encontró la base de datos de aprendizaje.")
        return

    with open(learning_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    ops = data.get('operations', [])
    if not ops:
        print("❌ No hay operaciones registradas para analizar.")
        return

    # Convertir a DataFrame para facilitar el análisis
    df_list = []
    for op in ops:
        # Extraer hora de la operación
        ts = op.get('timestamp')
        if not ts: continue
        
        try:
            dt = datetime.fromisoformat(ts)
            hour = dt.hour
        except:
            hour = op.get('hour', 0)

        # Determinar estrategia
        strat = op.get('strategy', {})
        if isinstance(strat, str):
            strat_name = strat
        else:
            strat_name = strat.get('strategy') or strat.get('name') or "Unknown"

        df_list.append({
            'hour': hour,
            'asset': op.get('asset'),
            'strategy': strat_name,
            'result': op.get('result'),
            'profit': op.get('profit', 0)
        })

    df = pd.DataFrame(df_list)
    
    print("\n" + "="*80)
    print("🧠 REPORTE DE ESTABILIDAD Y RENTABILIDAD")
    print("="*80)

    # 1. Rendimiento General por Hora (Stability)
    print("\n⏰ 1. ESTABILIDAD POR HORARIO (Win Rate):")
    hourly_stats = df.groupby('hour')['result'].value_counts(normalize=True).unstack().fillna(0)
    if 'win' in hourly_stats.columns:
        hourly_stats = hourly_stats.sort_values(by='win', ascending=False)
        for hour, row in hourly_stats.iterrows():
            total = len(df[df['hour'] == hour])
            wr = row['win'] * 100
            status = "✅ ESTABLE" if wr >= 65 else "⚠️ VOLÁTIL" if wr >= 50 else "❌ PELIGROSO"
            print(f"   Franja {hour:02d}:00 - {wr:5.1f}% WR ({total:3} ops) -> {status}")
    else:
        print("   Sin datos de victorias suficientes.")

    # 2. Rendimiento por Estrategia
    print("\n🎯 2. EFECTIVIDAD POR ESTRATEGIA:")
    strat_stats = df.groupby('strategy')['result'].value_counts(normalize=True).unstack().fillna(0)
    if 'win' in strat_stats.columns:
        strat_stats = strat_stats.sort_values(by='win', ascending=False)
        for strat, row in strat_stats.iterrows():
            total = len(df[df['strategy'] == strat])
            wr = row['win'] * 100
            print(f"   {strat:20}: {wr:5.1f}% WR ({total:3} ops)")

    # 3. Combinación Ganadora (Hora + Estrategia)
    print("\n🌟 3. LAS MEJORES COMBINACIONES (Sugerencias):")
    combo = df.groupby(['hour', 'strategy'])['result'].value_counts(normalize=True).unstack().fillna(0)
    if 'win' in combo.columns:
        best_combos = combo[combo['win'] >= 0.7].sort_values(by='win', ascending=False)
        count = 0
        for (hour, strat), row in best_combos.head(10).iterrows():
            total = len(df[(df['hour'] == hour) & (df['strategy'] == strat)])
            if total >= 2: # Al menos 2 ops para ser estadísticamente "algo" relevante
                print(f"   Hora {hour:02d}:00 con {strat:15} -> {row['win']*100:.1f}% WR")
                count += 1
        if count == 0: print("   Buscando más datos para patrones de oro...")

    print("\n" + "="*80)

if __name__ == "__main__":
    analyze_stability()
