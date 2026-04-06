#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo Rápido - Bot con IA (5 minutos)
Simula operaciones y muestra análisis de IA
"""

import sys
import os
import random
from datetime import datetime

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


def print_header(title):
    print(f"\n{B}{'='*80}{X}")
    print(f"{B}{title.center(80)}{X}")
    print(f"{B}{'='*80}{X}\n")


def simulate_trades():
    """Simula 10 operaciones"""
    
    print_header("🤖 BOT DE TRADING CON IA - DEMO RÁPIDO")
    
    analyzer = AITradeAnalyzer()
    corrector = AutoCorrection()
    
    trades_won = 0
    trades_lost = 0
    total_profit = 0
    
    # Generar 10 operaciones simuladas
    print(f"{C}Simulando 10 operaciones...{X}\n")
    
    for i in range(1, 11):
        # Generar operación aleatoria
        is_good_setup = random.random() > 0.5
        
        if is_good_setup:
            # Operación buena (más probabilidad de ganar)
            rsi = random.choice([20, 22, 24, 78, 80, 82])
            macd = random.uniform(0.0002, 0.0005)
            pullback = random.uniform(0.1, 0.3)
            confidence = random.uniform(0.70, 0.85)
            is_win = random.random() > 0.3  # 70% de ganar
        else:
            # Operación mala (más probabilidad de perder)
            rsi = random.uniform(40, 60)
            macd = random.uniform(0.00001, 0.00005)
            pullback = random.choice([0.02, 0.03, 0.6, 0.7])
            confidence = random.uniform(0.40, 0.55)
            is_win = random.random() > 0.7  # 30% de ganar
        
        # Crear trade
        action = 'CALL' if rsi < 50 else 'PUT'
        profit = 1.0 if is_win else -1.0
        total_profit += profit
        
        if is_win:
            trades_won += 1
        else:
            trades_lost += 1
        
        trade_data = {
            'id': f'TRADE_{i}',
            'asset': 'EURUSD-OTC',
            'action': action,
            'result': 'WIN' if is_win else 'LOSS',
            'profit': profit,
            'rsi': rsi,
            'macd': macd,
            'pullback_distance': pullback,
            'confidence': confidence,
            'timestamp': datetime.now().isoformat(),
            'reason': f"RSI {rsi:.1f} + MACD {macd:.6f}",
            'market_condition': 'TRENDING'
        }
        
        # Analizar
        analysis = analyzer.analyze_trade(trade_data)
        
        # Mostrar
        result_color = G if is_win else R
        print(f"{result_color}[{trade_data['result']}]{X} {trade_data['id']} | {action} | "
              f"${profit:+.2f} | Confluencia: {analysis['confluence_score']:.0f}/100 | "
              f"RSI: {rsi:.1f}")
    
    # Resumen
    print_header("📊 RESUMEN DE OPERACIONES")
    
    print(f"Total: {trades_won + trades_lost}")
    print(f"{G}Ganadoras: {trades_won}{X}")
    print(f"{R}Perdedoras: {trades_lost}{X}")
    print(f"Win Rate: {(trades_won / (trades_won + trades_lost) * 100):.1f}%")
    print(f"Ganancia Total: ${total_profit:+.2f}")
    
    # Reporte de IA
    print_header("🤖 ANÁLISIS DE IA")
    
    report = analyzer.generate_improvement_report()
    
    print(f"Total de Operaciones: {report['total_trades']}")
    print(f"Win Rate: {report['win_rate']:.1f}%")
    
    print(f"\n{C}RECOMENDACIONES:{X}")
    if report['recommendations']:
        for rec in report['recommendations']:
            print(f"  ✓ {rec}")
    else:
        print(f"  ✓ Parámetros óptimos")
    
    # Patrones
    print_header("🔍 PATRONES IDENTIFICADOS")
    
    winning = analyzer.get_winning_patterns()
    losing = analyzer.get_losing_patterns()
    
    if winning:
        print(f"{G}OPERACIONES GANADORAS ({winning.get('count', 0)}){X}")
        print(f"  RSI Promedio: {winning.get('avg_rsi', 0):.1f}")
        print(f"  MACD Promedio: {winning.get('avg_macd', 0):.6f}")
        print(f"  Pullback Promedio: {winning.get('avg_pullback', 0):.3f}%")
        print(f"  Confianza Promedio: {winning.get('avg_confidence', 0)*100:.0f}%")
        if winning.get('common_factors'):
            print(f"  Factores Comunes: {list(winning['common_factors'].keys())}")
    
    if losing:
        print(f"\n{R}OPERACIONES PERDEDORAS ({losing.get('count', 0)}){X}")
        print(f"  RSI Promedio: {losing.get('avg_rsi', 0):.1f}")
        print(f"  MACD Promedio: {losing.get('avg_macd', 0):.6f}")
        print(f"  Pullback Promedio: {losing.get('avg_pullback', 0):.3f}%")
        print(f"  Confianza Promedio: {losing.get('avg_confidence', 0)*100:.0f}%")
        if losing.get('common_issues'):
            print(f"  Problemas Comunes: {list(losing['common_issues'].keys())}")
    
    # Correcciones
    print_header("🔧 CORRECCIONES AUTOMÁTICAS")
    
    report['total_trades'] = len(analyzer.trades_history)
    report['duration_hours'] = 0.5
    
    corrections = corrector.analyze_and_correct(report)
    
    print(f"Parámetros Actuales:")
    for param, value in corrector.current_params.items():
        print(f"  {param}: {value}")
    
    if corrections['suggested_changes']:
        print(f"\n{C}CAMBIOS SUGERIDOS:{X}")
        for change in corrections['suggested_changes']:
            print(f"\n  📊 {change['parameter']}")
            print(f"     Actual: {change['current']}")
            print(f"     Sugerido: {change['suggested']}")
            print(f"     Razón: {change['reason']}")
        
        # Aplicar
        corrector.apply_corrections(corrections)
        print(f"\n{G}✅ Correcciones aplicadas (+{corrections['expected_improvement']:.0f}% mejora esperada){X}")
    
    # Mejoras potenciales
    print_header("📈 MEJORAS POTENCIALES DE PRECISIÓN")
    
    improvements = report['precision_improvements']
    print(f"Win Rate Actual: {improvements.get('current_win_rate', 0):.1f}%")
    print(f"Si solo confianza > 75%: {improvements.get('if_only_high_confidence', 0):.1f}%")
    print(f"Si solo RSI extremo: {improvements.get('if_only_strong_rsi', 0):.1f}%")
    print(f"Si solo MACD fuerte: {improvements.get('if_only_strong_macd', 0):.1f}%")
    print(f"Si todos los filtros: {improvements.get('if_all_filters', 0):.1f}%")
    
    print_header("✅ DEMO COMPLETADO")
    print(f"{G}Sistema de IA funcionando correctamente{X}\n")


if __name__ == "__main__":
    simulate_trades()
