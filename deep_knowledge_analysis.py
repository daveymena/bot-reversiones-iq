
import json
import pandas as pd
from pathlib import Path
import sys
import codecs

# Forzar UTF-8 para evitar errores de consola en Windows
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    except:
        pass

def deep_knowledge_analysis():
    db_path = Path("data/learning_database.json")
    if not db_path.exists():
        print("Error: No se encontro la base de datos")
        return

    try:
        with open(db_path, 'r', encoding='utf-8') as f:
            db = json.load(f)
    except Exception as e:
        print(f"Error cargando JSON: {e}")
        return

    ops = db.get('operations', [])
    if not ops:
        print("No hay operaciones registradas")
        return

    # Expandir los diccionarios internos para el DataFrame
    flat_ops = []
    for op in ops:
        flat_op = op.copy()
        if 'strategy' in op and isinstance(op['strategy'], dict):
            for k, v in op['strategy'].items():
                flat_op[f'strat_{k}'] = v
        flat_ops.append(flat_op)

    df = pd.DataFrame(flat_ops)
    
    if 'result' not in df.columns:
        print("No hay resultados registrados")
        return

    # Limpieza de datos
    df['result'] = df['result'].fillna('unknown')
    
    wins = df[df['result'] == 'win']
    losses = df[df['result'] == 'loose']
    
    print("="*60)
    print("ANALISIS PROFUNDO DE OPERACIONES")
    print("="*60)
    print(f"Total: {len(df)} | Wins: {len(wins)} | Losses: {len(losses)}")
    if (len(wins) + len(losses)) > 0:
        wr = (len(wins) / (len(wins) + len(losses))) * 100
        print(f"Win Rate: {wr:.1f}%")
    
    print("\nERRORES POR ACTIVO (TOP 5):")
    if not losses.empty:
        asset_stats = df.groupby('asset').agg(
            total=('result', 'count'),
            losses=('result', lambda x: (x == 'loose').sum()),
            wins=('result', lambda x: (x == 'win').sum())
        )
        asset_stats['wr'] = (asset_stats['wins'] / asset_stats['total']) * 100
        print(asset_stats.sort_values('losses', ascending=False).head(5))

    print("\nANALISIS DE RAZONES DE FALLO:")
    if not losses.empty:
        if 'strat_reason' in losses.columns:
            top_reasons = losses['strat_reason'].value_counts().head(5)
            for reason, count in top_reasons.items():
                print(f" - ({count} veces): {reason[:100]}...")

    print("\nPATRONES DETECTADOS:")
    # Análisis de confianza
    if 'strat_confidence' in df.columns:
        avg_conf_win = wins['strat_confidence'].mean() if not wins.empty else 0
        avg_conf_loss = losses['strat_confidence'].mean() if not losses.empty else 0
        print(f" - Confianza Promedio Ganadoras: {avg_conf_win:.1f}%")
        print(f" - Confianza Promedio Perdedoras: {avg_conf_loss:.1f}%")
        
        # Si la confianza de las perdidas es igual de alta, el bot es "arrogante"
        if avg_conf_loss > 70:
            print(" ! Alerta: El bot tiene alta confianza en sus fallos (Falta de humildad técnica)")

if __name__ == "__main__":
    deep_knowledge_analysis()
