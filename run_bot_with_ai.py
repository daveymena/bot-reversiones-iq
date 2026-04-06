#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bot de Trading con IA - Aprendizaje y Corrección en Tiempo Real
Ejecuta el bot y analiza cada operación con el sistema de IA
"""

import sys
import os
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Configurar encoding
os.environ['PYTHONIOENCODING'] = 'utf-8'
sys.stdout.reconfigure(encoding='utf-8')

# Configurar logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / f"bot_ai_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Importar módulos
from config import Config
from data.market_data import MarketDataHandler
from strategies.technical import FeatureEngineer
from core.ai_trade_analyzer import AITradeAnalyzer
from core.auto_correction import AutoCorrection

# Colores
G = '\033[92m'
R = '\033[91m'
Y = '\033[93m'
B = '\033[94m'
C = '\033[96m'
X = '\033[0m'


class BotWithAI:
    """Bot de trading con análisis de IA integrado"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.running = False
        
        # Inicializar componentes
        self.market_data = None
        self.feature_engineer = FeatureEngineer()
        self.analyzer = AITradeAnalyzer()
        self.corrector = AutoCorrection()
        
        # Estadísticas
        self.trades_executed = 0
        self.trades_won = 0
        self.trades_lost = 0
        self.total_profit = 0
        self.last_trade_time = 0
        
        self.logger.info("=" * 80)
        self.logger.info("🤖 BOT DE TRADING CON IA - APRENDIZAJE Y CORRECCIÓN")
        self.logger.info("=" * 80)
    
    def connect(self):
        """Conectar a broker"""
        try:
            self.logger.info(f"\n🔌 Conectando a {Config.BROKER_NAME.upper()} ({Config.ACCOUNT_TYPE})...")
            
            self.market_data = MarketDataHandler(
                broker_name=Config.BROKER_NAME,
                account_type=Config.ACCOUNT_TYPE
            )
            
            self.market_data.connect(Config.EXNOVA_EMAIL, Config.EXNOVA_PASSWORD)
            
            balance = self.market_data.get_balance()
            self.logger.info(f"✅ Conectado exitosamente")
            self.logger.info(f"💰 Balance: ${balance:.2f}")
            
            return True
        except Exception as e:
            self.logger.error(f"❌ Error conectando: {e}")
            return False
    
    def run(self, duration_minutes=30):
        """Ejecutar bot por X minutos"""
        self.running = True
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        self.logger.info(f"\n⏱️ Ejecutando por {duration_minutes} minutos...")
        self.logger.info(f"Modo: APRENDIZAJE CON IA")
        self.logger.info(f"Inicio: {datetime.now().strftime('%H:%M:%S')}")
        self.logger.info(f"Fin estimado: {(datetime.now() + timedelta(minutes=duration_minutes)).strftime('%H:%M:%S')}\n")
        
        cycle = 0
        
        try:
            while self.running and time.time() < end_time:
                cycle += 1
                now = time.time()
                elapsed = (now - start_time) / 60
                
                # Mostrar progreso cada 5 ciclos
                if cycle % 5 == 0:
                    self.logger.info(f"\n{C}[CICLO {cycle}] Tiempo: {elapsed:.1f}min | Operaciones: {self.trades_executed} | Win Rate: {self._get_win_rate():.1f}%{X}")
                
                # Analizar mercado
                self._analyze_and_trade()
                
                # Cada 10 operaciones, generar reporte
                if self.trades_executed > 0 and self.trades_executed % 10 == 0:
                    self._generate_ai_report()
                
                time.sleep(5)  # Esperar 5 segundos entre ciclos
        
        except KeyboardInterrupt:
            self.logger.info(f"\n{Y}Interrupción del usuario detectada{X}")
        except Exception as e:
            self.logger.error(f"❌ Error en loop principal: {e}", exc_info=True)
        finally:
            self.stop()
    
    def _analyze_and_trade(self):
        """Analizar mercado y ejecutar operación si hay señal"""
        try:
            # Obtener datos
            df = self.market_data.get_candles(Config.DEFAULT_ASSET, timeframe=60, num_candles=100)
            
            if df is None or len(df) < 50:
                return
            
            # Agregar indicadores
            df = self.feature_engineer.add_technical_indicators(df)
            
            # Obtener últimos valores
            last_row = df.iloc[-1]
            rsi = last_row.get('rsi', 50)
            macd = last_row.get('macd', 0)
            price = last_row['close']
            
            # Generar señal simple
            signal = None
            confidence = 0
            pullback = 0
            
            if rsi < 25:
                signal = 'CALL'
                confidence = 0.75
                pullback = 0.15
            elif rsi > 75:
                signal = 'PUT'
                confidence = 0.75
                pullback = 0.15
            
            # Si hay señal y pasó cooldown
            if signal and (time.time() - self.last_trade_time) > 180:
                # Ejecutar operación
                trade_id = f"TRADE_{self.trades_executed + 1}"
                
                try:
                    result = self.market_data.buy(
                        Config.DEFAULT_ASSET,
                        Config.CAPITAL_PER_TRADE,
                        signal,
                        3  # 3 minutos
                    )
                    
                    if result:
                        # Simular resultado (50% win rate para demo)
                        import random
                        is_win = random.random() > 0.5
                        profit = Config.CAPITAL_PER_TRADE if is_win else -Config.CAPITAL_PER_TRADE
                        
                        # Registrar operación
                        self._record_trade(
                            trade_id=trade_id,
                            asset=Config.DEFAULT_ASSET,
                            action=signal,
                            result='WIN' if is_win else 'LOSS',
                            profit=profit,
                            rsi=rsi,
                            macd=macd,
                            pullback_distance=pullback,
                            confidence=confidence,
                            reason=f"RSI {rsi:.1f} + MACD {macd:.6f}"
                        )
                        
                        self.last_trade_time = time.time()
                
                except Exception as e:
                    self.logger.error(f"Error ejecutando operación: {e}")
        
        except Exception as e:
            self.logger.error(f"Error analizando mercado: {e}")
    
    def _record_trade(self, trade_id, asset, action, result, profit, rsi, macd, pullback_distance, confidence, reason):
        """Registrar operación y analizarla con IA"""
        
        # Actualizar estadísticas
        self.trades_executed += 1
        self.total_profit += profit
        
        if result == 'WIN':
            self.trades_won += 1
        else:
            self.trades_lost += 1
        
        # Crear datos de operación
        trade_data = {
            'id': trade_id,
            'asset': asset,
            'action': action,
            'result': result,
            'profit': profit,
            'rsi': rsi,
            'macd': macd,
            'pullback_distance': pullback_distance,
            'confidence': confidence,
            'timestamp': datetime.now().isoformat(),
            'reason': reason,
            'market_condition': 'TRENDING'
        }
        
        # Analizar con IA
        analysis = self.analyzer.analyze_trade(trade_data)
        
        # Mostrar resultado
        result_color = G if result == 'WIN' else R
        self.logger.info(
            f"{result_color}[{result}]{X} {trade_id} | {asset} {action} | "
            f"${profit:+.2f} | Confluencia: {analysis['confluence_score']:.0f}/100 | "
            f"RSI: {rsi:.1f} | MACD: {macd:.6f}"
        )
    
    def _generate_ai_report(self):
        """Generar reporte de IA cada 10 operaciones"""
        self.logger.info(f"\n{B}{'='*80}{X}")
        self.logger.info(f"{B}📊 REPORTE DE IA - OPERACIÓN #{self.trades_executed}{X}")
        self.logger.info(f"{B}{'='*80}{X}")
        
        # Generar reporte
        report = self.analyzer.generate_improvement_report()
        
        self.logger.info(f"\n📈 ESTADÍSTICAS:")
        self.logger.info(f"  Total: {report['total_trades']}")
        self.logger.info(f"  {G}Ganadoras: {report['winning_trades']}{X}")
        self.logger.info(f"  {R}Perdedoras: {report['losing_trades']}{X}")
        self.logger.info(f"  Win Rate: {report['win_rate']:.1f}%")
        self.logger.info(f"  Ganancia Total: ${self.total_profit:+.2f}")
        
        # Recomendaciones
        if report['recommendations']:
            self.logger.info(f"\n💡 RECOMENDACIONES:")
            for rec in report['recommendations']:
                self.logger.info(f"  - {rec}")
        
        # Correcciones automáticas
        report['total_trades'] = len(self.analyzer.trades_history)
        report['duration_hours'] = (time.time() - self.last_trade_time) / 3600 if self.last_trade_time else 0.1
        
        corrections = self.corrector.analyze_and_correct(report)
        
        if corrections['suggested_changes']:
            self.logger.info(f"\n🔧 CORRECCIONES SUGERIDAS:")
            for change in corrections['suggested_changes']:
                self.logger.info(f"  {change['parameter']}: {change['current']} → {change['suggested']}")
                self.logger.info(f"    Razón: {change['reason']}")
            
            # Aplicar correcciones
            self.corrector.apply_corrections(corrections)
            self.logger.info(f"\n✅ Correcciones aplicadas (+{corrections['expected_improvement']:.0f}% mejora esperada)")
        
        self.logger.info(f"\n{B}{'='*80}{X}\n")
    
    def _get_win_rate(self):
        """Calcular win rate actual"""
        if self.trades_executed == 0:
            return 0
        return (self.trades_won / self.trades_executed) * 100
    
    def stop(self):
        """Detener bot"""
        self.running = False
        
        self.logger.info(f"\n{B}{'='*80}{X}")
        self.logger.info(f"{B}📊 RESUMEN FINAL{X}")
        self.logger.info(f"{B}{'='*80}{X}\n")
        
        self.logger.info(f"Operaciones Ejecutadas: {self.trades_executed}")
        self.logger.info(f"{G}Ganadoras: {self.trades_won}{X}")
        self.logger.info(f"{R}Perdedoras: {self.trades_lost}{X}")
        self.logger.info(f"Win Rate: {self._get_win_rate():.1f}%")
        self.logger.info(f"Ganancia Total: ${self.total_profit:+.2f}")
        
        # Reporte final de IA
        if self.trades_executed > 0:
            final_report = self.analyzer.generate_improvement_report()
            
            self.logger.info(f"\n{C}ANÁLISIS FINAL DE IA:{X}")
            self.logger.info(f"  Confluencia Promedio: {sum(t['confluence_score'] for t in self.analyzer.trades_history) / len(self.analyzer.trades_history):.0f}/100")
            
            winning = self.analyzer.get_winning_patterns()
            losing = self.analyzer.get_losing_patterns()
            
            if winning:
                self.logger.info(f"\n  {G}OPERACIONES GANADORAS:{X}")
                self.logger.info(f"    RSI Promedio: {winning.get('avg_rsi', 0):.1f}")
                self.logger.info(f"    MACD Promedio: {winning.get('avg_macd', 0):.6f}")
                self.logger.info(f"    Pullback Promedio: {winning.get('avg_pullback', 0):.3f}%")
                self.logger.info(f"    Confianza Promedio: {winning.get('avg_confidence', 0)*100:.0f}%")
            
            if losing:
                self.logger.info(f"\n  {R}OPERACIONES PERDEDORAS:{X}")
                self.logger.info(f"    RSI Promedio: {losing.get('avg_rsi', 0):.1f}")
                self.logger.info(f"    MACD Promedio: {losing.get('avg_macd', 0):.6f}")
                self.logger.info(f"    Pullback Promedio: {losing.get('avg_pullback', 0):.3f}%")
                self.logger.info(f"    Confianza Promedio: {losing.get('avg_confidence', 0)*100:.0f}%")
        
        self.logger.info(f"\n{B}{'='*80}{X}")
        self.logger.info(f"✅ Bot detenido correctamente")
        self.logger.info(f"📁 Logs guardados en: {log_dir}")
        self.logger.info(f"{B}{'='*80}{X}\n")


def main():
    """Función principal"""
    bot = BotWithAI()
    
    # Conectar
    if not bot.connect():
        sys.exit(1)
    
    # Ejecutar por 30 minutos
    try:
        bot.run(duration_minutes=30)
    except KeyboardInterrupt:
        bot.logger.info(f"\n{Y}Deteniendo bot...{X}")
        bot.stop()


if __name__ == "__main__":
    main()
