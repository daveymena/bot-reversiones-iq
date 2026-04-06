#!/usr/bin/env python3
"""
BOT PRODUCCIÓN CON APRENDIZAJE CONTINUO
- Máximo 10 operaciones por hora
- 5 minutos entre operaciones
- IA analiza cada operación
- Refina parámetros automáticamente
- Objetivo: Ganancia constante 24/7
"""

import time
import sys
import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.getcwd())

from config import Config
from data.market_data import MarketDataHandler
from strategies.technical import FeatureEngineer
from core.learning_system import LearningSystem
from core.schedule_manager import ScheduleManager
from ai.llm_client import LLMClient
import pandas as pd
import ta

# Colores
G = '\033[92m'
R = '\033[91m'
Y = '\033[93m'
C = '\033[96m'
W = '\033[97m'
X = '\033[0m'
BOLD = '\033[1m'

class ProductionLearningBot:
    """Bot de producción con aprendizaje continuo"""
    
    def __init__(self):
        self.market_data = None
        self.feature_engineer = FeatureEngineer()
        self.learning_system = LearningSystem()
        self.schedule_manager = ScheduleManager(max_trades_per_hour=10, min_interval_seconds=300)
        self.llm_client = None
        
        self.assets = ["EURUSD-OTC", "GBPUSD-OTC", "USDJPY-OTC", "AUDUSD-OTC", "NZDUSD-OTC"]
        self.current_asset_idx = 0
        self.capital_per_trade = 1.0
        self.min_confidence = 65
    
    def connect(self):
        """Conectar a broker y IA"""
        print("\n" + "="*80)
        print(f"{BOLD}BOT PRODUCCIÓN - APRENDIZAJE CONTINUO{X}")
        print("="*80)
        print(f"Conectando a Exnova PRACTICE...")
        
        try:
            email = os.getenv('EXNOVA_EMAIL', '')
            password = os.getenv('EXNOVA_PASSWORD', '')
            
            self.market_data = MarketDataHandler(
                broker_name='exnova',
                account_type='PRACTICE'
            )
            
            if not self.market_data.connect(email, password):
                print(f'{R}[ERROR] No se pudo conectar a Exnova{X}')
                return False
            
            balance = self.market_data.get_balance()
            print(f'{G}[OK] Conectado a Exnova{X}')
            print(f'Balance: ${balance:.2f}')
            
            # Conectar IA
            try:
                self.llm_client = LLMClient()
                print(f'{G}[OK] IA disponible{X}')
            except:
                print(f'{Y}[WARN] IA no disponible (continuando sin IA){X}')
            
            return True
            
        except Exception as e:
            print(f'{R}[ERROR] {str(e)}{X}')
            return False
    
    def _get_next_asset(self):
        """Siguiente divisa en rotación"""
        asset = self.assets[self.current_asset_idx]
        self.current_asset_idx = (self.current_asset_idx + 1) % len(self.assets)
        return asset
    
    def _analyze_and_trade(self):
        """Analizar y ejecutar operación"""
        
        # Verificar si se puede operar
        can_trade, reason = self.schedule_manager.can_trade()
        if not can_trade:
            print(f"{Y}[SCHEDULE] {reason}{X}")
            return None
        
        asset = self._get_next_asset()
        print(f"\n{BOLD}[ANÁLISIS] {asset}{X}")
        
        try:
            # Obtener datos
            candles = self.market_data.get_candles(asset, "3m", 100)
            
            if not candles or len(candles) < 20:
                print(f"{Y}[SKIP] Datos insuficientes{X}")
                return None
            
            # Análisis técnico
            df = pd.DataFrame(candles)
            df['close'] = pd.to_numeric(df['close'], errors='coerce')
            df['open'] = pd.to_numeric(df['open'], errors='coerce')
            df['high'] = pd.to_numeric(df['high'], errors='coerce')
            df['low'] = pd.to_numeric(df['low'], errors='coerce')
            
            df['rsi'] = ta.momentum.RSIIndicator(close=df['close'], window=14).rsi()
            macd = ta.trend.MACD(close=df['close'])
            df['macd'] = macd.macd()
            df['macd_signal'] = macd.macd_signal()
            
            # Lógica de señal
            last = df.iloc[-1]
            rsi = last.get('rsi', 50)
            macd_val = last.get('macd', 0)
            macd_sig = last.get('macd_signal', 0)
            
            signal = None
            confidence = 0
            reason = ""
            
            # RSI extremo
            if rsi < 25:
                signal = "CALL"
                confidence = 70
                reason = f"RSI muy bajo ({rsi:.1f})"
            elif rsi > 75:
                signal = "PUT"
                confidence = 70
                reason = f"RSI muy alto ({rsi:.1f})"
            
            # MACD
            elif macd_val > macd_sig and macd_val > 0.00005:
                signal = "CALL"
                confidence = 65
                reason = f"MACD alcista"
            elif macd_val < macd_sig and macd_val < -0.00005:
                signal = "PUT"
                confidence = 65
                reason = f"MACD bajista"
            
            if not signal or confidence < self.min_confidence:
                print(f"{Y}[SKIP] Sin señal clara{X}")
                return None
            
            # Ejecutar
            color = G if signal == "CALL" else R
            print(f"{BOLD}{color}>>> {signal} ${self.capital_per_trade} 3min{X}")
            print(f"Confianza: {confidence}% | RSI: {rsi:.1f} | Razón: {reason}")
            
            status, trade_id = self.market_data.api.buy(
                self.capital_per_trade,
                asset,
                signal.lower(),
                3
            )
            
            if not status:
                print(f"{R}[ERROR] Fallo en ejecución{X}")
                return None
            
            print(f"{C}ID: {trade_id}{X}")
            
            # Esperar resultado
            print(f"{Y}Esperando 3 min 15 seg...{X}")
            time.sleep(3 * 60 + 15)
            
            result_status, profit = self.market_data.api.check_win_v4(trade_id, timeout=30)
            
            if result_status:
                status_text = "WIN" if result_status == "win" else "LOSS"
                color = G if status_text == "WIN" else R
                print(f"{color}[{status_text}] ${profit:+.2f}{X}")
                
                # Registrar en sistema de aprendizaje
                trade_data = {
                    "timestamp": datetime.now().isoformat(),
                    "asset": asset,
                    "signal": signal,
                    "profit": profit,
                    "status": status_text,
                    "trade_id": trade_id,
                    "confidence": confidence,
                    "rsi": rsi,
                    "macd": macd_val,
                    "reason": reason
                }
                
                self.learning_system.record_trade(trade_data)
                self.schedule_manager.record_trade(trade_data)
                
                # Analizar con IA
                if self.llm_client:
                    ai_analysis = self.learning_system.analyze_with_ai(trade_data)
                    if "analysis" in ai_analysis:
                        print(f"\n{C}[IA ANÁLISIS]{X}")
                        print(f"{ai_analysis['analysis'][:200]}...")
                
                return trade_data
            else:
                print(f"{Y}[TIMEOUT] Sin resultado{X}")
                return None
                
        except Exception as e:
            print(f"{R}[ERROR] {str(e)}{X}")
            import traceback
            traceback.print_exc()
            return None
    
    def run(self):
        """Ejecutar bot continuamente"""
        
        if not self.connect():
            return
        
        print("\n" + "="*80)
        print(f"{BOLD}CONFIGURACIÓN{X}")
        print(f"Máximo: 10 operaciones/hora")
        print(f"Intervalo: 5 minutos entre operaciones")
        print(f"Objetivo: Ganancia constante 24/7")
        print(f"IA: Analiza cada operación para refinar")
        print("="*80)
        print(f"Presiona Ctrl+C para detener\n")
        
        try:
            while True:
                try:
                    # Intentar operación
                    result = self._analyze_and_trade()
                    
                    if result:
                        # Mostrar estado
                        status = self.learning_system.get_status()
                        schedule = self.schedule_manager.get_status()
                        
                        print(f"\n{BOLD}ESTADO{X}")
                        print(f"Operaciones: {status['total_trades']} | "
                              f"Ganancias: {status['wins']} | "
                              f"WR: {status['win_rate']} | "
                              f"Ganancia: {status['avg_profit']}")
                        print(f"Hora: {schedule['trades_this_hour']}/{schedule['max_per_hour']} | "
                              f"Ganancia hora: {schedule['total_profit_this_hour']}")
                        
                        # Mostrar refinamientos
                        if status['refinements']:
                            print(f"\n{BOLD}REFINAMIENTOS{X}")
                            for ref in status['refinements'][:3]:
                                print(f"  {ref}")
                        
                        # Esperar antes de siguiente
                        self.schedule_manager.wait_for_next_trade()
                    else:
                        # Sin operación, esperar menos
                        time.sleep(10)
                    
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    print(f"{R}[ERROR] {str(e)}{X}")
                    time.sleep(10)
        
        except KeyboardInterrupt:
            pass
        
        self._generate_report()
    
    def _generate_report(self):
        """Generar reporte final"""
        
        status = self.learning_system.get_status()
        
        print(f"\n\n{BOLD}REPORTE FINAL{X}")
        print("="*80)
        print(f"Total operaciones: {status['total_trades']}")
        print(f"Ganancias: {status['wins']}")
        print(f"Pérdidas: {status['losses']}")
        print(f"Win Rate: {status['win_rate']}")
        print(f"Ganancia promedio: {status['avg_profit']}")
        print("="*80)


def main():
    bot = ProductionLearningBot()
    bot.run()


if __name__ == "__main__":
    main()
