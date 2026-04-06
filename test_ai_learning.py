#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Testing - IA Aprendizaje y Corrección
Prueba el sistema de análisis y corrección automática
"""

import sys
import json
import os
from datetime import datetime, timedelta

# Configurar encoding
os.environ['PYTHONIOENCODING'] = 'utf-8'
sys.stdout.reconfigure(encoding='utf-8')

from core.ai_trade_analyzer import AITradeAnalyzer
from core.auto_correction import AutoCorrection

# Colores para output
G = '\033[92m'
R = '\033[91m'
Y = '\033[93m'
B = '\033[94m'
X = '\033[0m'


def generate_sample_trades():
    """Genera operaciones de ejemplo para testing"""
    trades = [
        # Operaciones ganadoras
        {
            'id': '1',
            'asset': 'EURUSD-OTC',
            'action': 'CALL',
            'entry_price': 1.0850,
            'exit_price': 1.0860,
            'result': 'WIN',
            'profit': 1.0,
            'rsi': 22.5,
            'macd': 0.00025,
            'pullback_distance': 0.15,
            'confidence': 0.78,
            'timestamp': datetime.now().isoformat(),
            'reason': 'Pullback a SSL + RSI sobreventa + MACD alcista',
            'market_condition': 'TRENDING'
        },
        {
            'id': '2',
            'asset': 'GBPUSD-OTC',
            'action': 'PUT',
            'entry_price': 1.2650,
            'exit_price': 1.2640,
            'result': 'WIN',
            'profit': 1.0,
            'rsi': 78.5,
            'macd': -0.00032,
            'pullback_distance': 0.18,
            'confidence': 0.82,
            'timestamp': (datetime.now() - timedelta(minutes=5)).isoformat(),
            'reason': 'Pullback a SSL + RSI sobrecompra + MACD bajista',
            'market_condition': 'TRENDING'
        },
        {
            'id': '3',
            'asset': 'EURUSD-OTC',
            'action': 'CALL',
            'entry_price': 1.0840,
            'exit_price': 1.0850,
            'result': 'WIN',
            'profit': 1.0,
            'rsi': 24.0,
            'macd': 0.00018,
            'pullback_distance': 0.12,
            'confidence': 0.75,
            'timestamp': (datetime.now() - timedelta(minutes=10)).isoformat(),
            'reason': 'Pullback a SSL + RSI sobreventa',
            'market_condition': 'TRENDING'
        },
        
        # Operaciones perdedoras
        {
            'id': '4',
            'asset': 'EURUSD-OTC',
            'action': 'CALL',
            'entry_price': 1.0855,
            'exit_price': 1.0850,
            'result': 'LOSS',
            'profit': -1.0,
            'rsi': 45.0,
            'macd': 0.00002,
            'pullback_distance': 0.024,
            'confidence': 0.45,
            'timestamp': (datetime.now() - timedelta(minutes=15)).isoformat(),
            'reason': 'RSI neutral + MACD débil + Pullback insuficiente',
            'market_condition': 'RANGING'
        },
        {
            'id': '5',
            'asset': 'GBPUSD-OTC',
            'action': 'CALL',
            'entry_price': 1.2645,
            'exit_price': 1.2640,
            'result': 'LOSS',
            'profit': -1.0,
            'rsi': 39.2,
            'macd': -0.00020,
            'pullback_distance': 0.018,
            'confidence': 0.45,
            'timestamp': (datetime.now() - timedelta(minutes=20)).isoformat(),
            'reason': 'RSI neutral + MACD bajista + Pullback débil',
            'market_condition': 'RANGING'
        },
        {
            'id': '6',
            'asset': 'EURUSD-OTC',
            'action': 'PUT',
            'entry_price': 1.0860,
            'exit_price': 1.0865,
            'result': 'LOSS',
            'profit': -1.0,
            'rsi': 52.0,
            'macd': 0.00001,
            'pullback_distance': 0.08,
            'confidence': 0.50,
            'timestamp': (datetime.now() - timedelta(minutes=25)).isoformat(),
            'reason': 'RSI neutral + MACD casi cero',
            'market_condition': 'RANGING'
        },
    ]
    
    return trades


def print_header(title):
    """Imprime encabezado"""
    print(f"\n{B}{'='*80}{X}")
    print(f"{B}{title.center(80)}{X}")
    print(f"{B}{'='*80}{X}\n")


def print_trade_analysis(analyzer, trades):
    """Imprime análisis de cada operación"""
    print_header("ANÁLISIS DETALLADO DE OPERACIONES")
    
    for trade in trades:
        analysis = analyzer.analyze_trade(trade)
        
        result_color = G if trade['result'] == 'WIN' else R
        print(f"{result_color}[{trade['result']}]{X} {trade['id']} - {trade['asset']} {trade['action']}")
        print(f"  Ganancia: ${trade['profit']}")
        print(f"  Indicadores: RSI={trade['rsi']:.1f}, MACD={trade['macd']:.6f}, Pullback={trade['pullback_distance']:.3f}%")
        print(f"  Confianza: {trade['confidence']*100:.0f}%")
        print(f"  Calidad Indicadores: {analysis['indicators_quality']['overall_score']:.0f}/100")
        print(f"  Calidad Entrada: {analysis['entry_quality']['entry_score']:.0f}/100")
        print(f"  Confluencia: {analysis['confluence_score']:.0f}/100")
        
        if analysis['precision_factors']:
            print(f"  ✅ Factores de Precisión: {', '.join(analysis['precision_factors'])}")
        
        if analysis['improvement_areas']:
            print(f"  ⚠️ Áreas de Mejora: {', '.join(analysis['improvement_areas'])}")
        
        print()


def print_patterns(analyzer):
    """Imprime patrones identificados"""
    print_header("PATRONES IDENTIFICADOS")
    
    winning = analyzer.get_winning_patterns()
    losing = analyzer.get_losing_patterns()
    
    print(f"{G}OPERACIONES GANADORAS ({winning.get('count', 0)}){X}")
    print(f"  RSI Promedio: {winning.get('avg_rsi', 0):.1f}")
    print(f"  MACD Promedio: {winning.get('avg_macd', 0):.6f}")
    print(f"  Pullback Promedio: {winning.get('avg_pullback', 0):.3f}%")
    print(f"  Confianza Promedio: {winning.get('avg_confidence', 0)*100:.0f}%")
    if winning.get('common_factors'):
        print(f"  Factores Comunes: {winning['common_factors']}")
    
    print(f"\n{R}OPERACIONES PERDEDORAS ({losing.get('count', 0)}){X}")
    print(f"  RSI Promedio: {losing.get('avg_rsi', 0):.1f}")
    print(f"  MACD Promedio: {losing.get('avg_macd', 0):.6f}")
    print(f"  Pullback Promedio: {losing.get('avg_pullback', 0):.3f}%")
    print(f"  Confianza Promedio: {losing.get('avg_confidence', 0)*100:.0f}%")
    if losing.get('common_issues'):
        print(f"  Problemas Comunes: {losing['common_issues']}")


def print_improvement_report(analyzer):
    """Imprime reporte de mejoras"""
    print_header("REPORTE DE MEJORAS")
    
    report = analyzer.generate_improvement_report()
    
    print(f"Total de Operaciones: {report['total_trades']}")
    print(f"{G}Ganadoras: {report['winning_trades']}{X}")
    print(f"{R}Perdedoras: {report['losing_trades']}{X}")
    print(f"Win Rate: {report['win_rate']:.1f}%")
    
    print(f"\n{B}RECOMENDACIONES:{X}")
    for i, rec in enumerate(report['recommendations'], 1):
        print(f"  {i}. {rec}")
    
    print(f"\n{B}MEJORAS POTENCIALES DE PRECISIÓN:{X}")
    improvements = report['precision_improvements']
    print(f"  Win Rate Actual: {improvements.get('current_win_rate', 0):.1f}%")
    print(f"  Si solo confianza > 75%: {improvements.get('if_only_high_confidence', 0):.1f}%")
    print(f"  Si solo RSI extremo: {improvements.get('if_only_strong_rsi', 0):.1f}%")
    print(f"  Si solo MACD fuerte: {improvements.get('if_only_strong_macd', 0):.1f}%")
    print(f"  Si todos los filtros: {improvements.get('if_all_filters', 0):.1f}%")


def print_corrections(corrector, report):
    """Imprime correcciones sugeridas"""
    print_header("CORRECCIONES AUTOMÁTICAS SUGERIDAS")
    
    corrections = corrector.analyze_and_correct(report)
    
    print(f"Parámetros Actuales:")
    for param, value in corrector.current_params.items():
        print(f"  {param}: {value}")
    
    print(f"\n{B}CAMBIOS SUGERIDOS:{X}")
    for change in corrections['suggested_changes']:
        print(f"\n  📊 {change['parameter']}")
        print(f"     Actual: {change['current']}")
        print(f"     Sugerido: {change['suggested']}")
        print(f"     Razón: {change['reason']}")
    
    print(f"\n{G}Mejora Esperada: +{corrections['expected_improvement']:.0f}% en win rate{X}")
    
    return corrections


def main():
    """Función principal"""
    print(f"\n{B}{'='*80}{X}")
    print(f"{B}{'SISTEMA DE IA - APRENDIZAJE Y CORRECCIÓN'.center(80)}{X}")
    print(f"{B}{'='*80}{X}")
    
    # Generar operaciones de ejemplo
    trades = generate_sample_trades()
    print(f"\n✅ Generadas {len(trades)} operaciones de ejemplo")
    
    # Crear analizador
    analyzer = AITradeAnalyzer()
    print(f"✅ Analizador de IA inicializado")
    
    # Analizar cada operación
    print_trade_analysis(analyzer, trades)
    
    # Mostrar patrones
    print_patterns(analyzer)
    
    # Generar reporte
    report = analyzer.generate_improvement_report()
    print_improvement_report(analyzer)
    
    # Correcciones automáticas
    corrector = AutoCorrection()
    report['total_trades'] = len(trades)
    report['duration_hours'] = 0.5  # 30 minutos
    
    corrections = print_corrections(corrector, report)
    
    # Aplicar correcciones
    print(f"\n{B}{'='*80}{X}")
    print(f"{B}{'APLICANDO CORRECCIONES'.center(80)}{X}")
    print(f"{B}{'='*80}{X}\n")
    
    if corrector.apply_corrections(corrections):
        print(f"{G}✅ Correcciones aplicadas exitosamente{X}\n")
        
        print(f"Parámetros Nuevos:")
        for param, value in corrector.get_current_params().items():
            print(f"  {param}: {value}")
    
    # Exportar configuración
    print(f"\n{B}Configuración Exportada:{X}")
    print(corrector.export_params_to_config())
    
    print(f"\n{G}✅ Testing completado{X}\n")


if __name__ == "__main__":
    main()
