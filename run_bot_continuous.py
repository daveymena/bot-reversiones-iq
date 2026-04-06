#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bot Continuo - Ejecuta múltiples ciclos y recopila estadísticas
"""

import sys
import os
import random
import json
from datetime import datetime
from pathlib import Path

os.environ['PYTHONIOENCODING'] = 'utf-8'
sys.stdout.reconfigure(encoding='utf-8')

from core.ai_trade_analyzer import AITradeAnalyzer
from core.auto_correction import AutoCorrection

# Colores
G = '\033[92m'
R = '\033[91m'
Y = '\033[93m'
B = '\033[94m'
C = '\033[96m'
X = '\033[0m'


class ContinuousBot:
    """Bot que ejecuta continuamente y recopila estadísticas"""
    
    def __init__(self):
        self.analyzer = AITradeAnalyzer()
        self.corrector = AutoCorrection()
        self.all_trades = []
        self.cycle_stats = []
        self.start_time = datetime.now()
    
    def run_cycle(self, num_trades=10):
        """Ejecutar un ciclo de N operaciones"""
        
        trades_won = 0
        trades_lost = 0
        total_profit = 0
        
        for i in range(num_trades):
            # Generar operación
            is_good_setup = random.random() > 0.5
            
            if is_good_setup:
                rsi = random.choice([20, 22, 24, 78, 80, 82])
                macd = random.uniform(0.0002, 0.0005)
                pullback = random.uniform(0.1, 0.3)
                confidence = random.uniform(0.70, 0.85)
                is_win = random.random() > 0.3
            else:
                rsi = random.uniform(40, 60)
                macd = random.uniform(0.00001, 0.00005)
                pullback = random.choice([0.02, 0.03, 0.6, 0.7])
                confidence = random.uniform(0.40, 0.55)
                is_win = random.random() > 0.7
            
            action = 'CALL' if rsi < 50 else 'PUT'
            profit = 1.0 if is_win else -1.0
            total_profit += profit
            
            if is_win:
                trades_won += 1
            else:
                trades_lost += 1
            
            trade_data = {
                'id': f'TRADE_{len(self.all_trades) + 1}',
                'asset': 'EURUSD-OTC',
                'action': action,
                'result': 'WIN' if is_win else 'LOSS',
                'profit': profit,
                'rsi': rsi,
                'macd': macd,
                'pullback_distance': pullback,
                'confidence': confidence,
                'timestamp': datetime.now().isoformat(),
                'reason': f"RSI {rsi:.1f}",
                'market_condition': 'TRENDING'
            }
            
            analysis = self.analyzer.analyze_trade(trade_data)
            self.all_trades.append({
                'trade': trade_data,
                'analysis': analysis
            })
        
        # Estadísticas del ciclo
        win_rate = (trades_won / num_trades * 100) if num_trades > 0 else 0
        
        cycle_stat = {
            'cycle': len(self.cycle_stats) + 1,
            'trades': num_trades,
            'won': trades_won,
            'lost': trades_lost,
            'win_rate': win_rate,
            'profit': total_profit,
            'timestamp': datetime.now().isoformat()
        }
        
        self.cycle_stats.append(cycle_stat)
        
        return cycle_stat
    
    def print_cycle_summary(self, cycle_stat):
        """Imprimir resumen del ciclo"""
        cycle = cycle_stat['cycle']
        trades = cycle_stat['trades']
        won = cycle_stat['won']
        lost = cycle_stat['lost']
        win_rate = cycle_stat['win_rate']
        profit = cycle_stat['profit']
        
        profit_color = G if profit > 0 else R
        
        print(f"\n{C}[CICLO {cycle}]{X} | "
              f"Operaciones: {trades} | "
              f"{G}Ganadoras: {won}{X} | "
              f"{R}Perdedoras: {lost}{X} | "
              f"Win Rate: {win_rate:.1f}% | "
              f"{profit_color}Ganancia: ${profit:+.2f}{X}")
    
    def print_overall_stats(self):
        """Imprimir estadísticas generales"""
        
        total_trades = len(self.all_trades)
        total_won = sum(1 for t in self.all_trades if t['trade']['result'] == 'WIN')
        total_lost = total_trades - total_won
        total_profit = sum(t['trade']['profit'] for t in self.all_trades)
        overall_win_rate = (total_won / total_trades * 100) if total_trades > 0 else 0
        
        print(f"\n{B}{'='*80}{X}")
        print(f"{B}📊 ESTADÍSTICAS GENERALES{X}")
        print(f"{B}{'='*80}{X}\n")
        
        print(f"Total de Operaciones: {total_trades}")
        print(f"{G}Ganadoras: {total_won}{X}")
        print(f"{R}Perdedoras: {total_lost}{X}")
        print(f"Win Rate General: {overall_win_rate:.1f}%")
        print(f"Ganancia Total: ${total_profit:+.2f}")
        
        # Promedio por ciclo
        if self.cycle_stats:
            avg_win_rate = sum(c['win_rate'] for c in self.cycle_stats) / len(self.cycle_stats)
            avg_profit = sum(c['profit'] for c in self.cycle_stats) / len(self.cycle_stats)
            
            print(f"\nPromedio por Ciclo:")
            print(f"  Win Rate: {avg_win_rate:.1f}%")
            print(f"  Ganancia: ${avg_profit:+.2f}")
        
        # Análisis de IA
        print(f"\n{C}ANÁLISIS DE IA:{X}")
        
        report = self.analyzer.generate_improvement_report()
        print(f"  Confluencia Promedio: {sum(t['analysis']['confluence_score'] for t in self.all_trades) / len(self.all_trades):.0f}/100")
        
        winning = self.analyzer.get_winning_patterns()
        losing = self.analyzer.get_losing_patterns()
        
        if winning:
            print(f"\n  {G}OPERACIONES GANADORAS:{X}")
            print(f"    RSI Promedio: {winning.get('avg_rsi', 0):.1f}")
            print(f"    MACD Promedio: {winning.get('avg_macd', 0):.6f}")
            print(f"    Confianza Promedio: {winning.get('avg_confidence', 0)*100:.0f}%")
        
        if losing:
            print(f"\n  {R}OPERACIONES PERDEDORAS:{X}")
            print(f"    RSI Promedio: {losing.get('avg_rsi', 0):.1f}")
            print(f"    MACD Promedio: {losing.get('avg_macd', 0):.6f}")
            print(f"    Confianza Promedio: {losing.get('avg_confidence', 0)*100:.0f}%")
        
        # Recomendaciones
        if report['recommendations']:
            print(f"\n  {Y}RECOMENDACIONES:{X}")
            for rec in report['recommendations']:
                print(f"    - {rec}")
    
    def save_stats(self):
        """Guardar estadísticas en JSON"""
        stats_file = Path("logs") / f"bot_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        stats_file.parent.mkdir(exist_ok=True)
        
        data = {
            'start_time': self.start_time.isoformat(),
            'end_time': datetime.now().isoformat(),
            'total_cycles': len(self.cycle_stats),
            'total_trades': len(self.all_trades),
            'cycle_stats': self.cycle_stats,
            'overall_stats': {
                'total_won': sum(1 for t in self.all_trades if t['trade']['result'] == 'WIN'),
                'total_lost': sum(1 for t in self.all_trades if t['trade']['result'] == 'LOSS'),
                'total_profit': sum(t['trade']['profit'] for t in self.all_trades),
                'win_rate': (sum(1 for t in self.all_trades if t['trade']['result'] == 'WIN') / len(self.all_trades) * 100) if self.all_trades else 0
            }
        }
        
        with open(stats_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"\n✅ Estadísticas guardadas en: {stats_file}")


def main():
    """Función principal"""
    
    print(f"\n{B}{'='*80}{X}")
    print(f"{B}{'🤖 BOT CONTINUO CON IA - MÚLTIPLES CICLOS'.center(80)}{X}")
    print(f"{B}{'='*80}{X}\n")
    
    bot = ContinuousBot()
    
    try:
        # Ejecutar 5 ciclos de 10 operaciones cada uno
        for cycle in range(1, 6):
            print(f"\n{C}Ejecutando ciclo {cycle}/5...{X}")
            cycle_stat = bot.run_cycle(num_trades=10)
            bot.print_cycle_summary(cycle_stat)
        
        # Mostrar estadísticas finales
        bot.print_overall_stats()
        
        # Guardar estadísticas
        bot.save_stats()
        
        print(f"\n{G}✅ Bot completado exitosamente{X}\n")
    
    except KeyboardInterrupt:
        print(f"\n{Y}Interrupción del usuario{X}")
        bot.print_overall_stats()
        bot.save_stats()
    except Exception as e:
        print(f"\n{R}❌ Error: {e}{X}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
