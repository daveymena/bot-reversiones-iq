#!/usr/bin/env python3
"""
BOT MAESTRO - SISTEMA DE DOS FASES
Fase 1: Recolección de datos (sin restricciones)
Fase 2: Producción (10 ops/hora, 5 min entre ops)
Transición automática cuando tenga suficientes datos
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
from core.phase_manager import PhaseManager
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

class MasterBot:
    """Bot maestro con dos fases automáticas"""
    
    def __init__(self):
        self.market_data = None
        self.feature_engineer = FeatureEngineer()
        self.learning_system = LearningSystem()
        self.schedule_manager = ScheduleManager(max_trades_per_hour=10, min_interval_seconds=300)
        self.phase_manager = PhaseManager()
        self.llm_client = None
        
        self.assets = ["EURUSD-OTC", "GBPUSD-OTC", "USDJPY-OTC", "AUDUSD-OTC", "NZDUSD-OTC"]
        self.current_asset_idx = 0
        self.capital_per_trade = 1.0
        self.min_confidence = 65
        
        self.cycle_count = 0
    
    def connect(self):
        """Conectar a broker y IA"""
        print("\n" + "="*80)
        print(f"{BOLD}BOT MAESTRO - SISTEMA DE DOS FASES{X}")
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
                print(f'{Y}[WARN] IA no disponible{X}')
            
            return True
            
        except Exception as e:
            print(f'{R}[ERROR] {str(e)}{X}')
            return False
    
    def _get_next_asset(self):
        """Siguiente divisa"""
        asset = self.assets[self.current_asset_idx]
        self.current_asset_idx = (self.current_asset_idx + 1) % len(self.assets)
        return asset
    
    def _find_liquidity_levels(self, df, lookback=100):
        """Encuentra pools de liquidez"""
        if len(df) < 20:
            return [], []
        
        highs = df['high'].tail(lookback).values
        lows = df['low'].tail(lookback).values
        
        buy_side = []
        sell_side = []
        
        for i in range(2, len(highs) - 2):
            is_high = all(highs[i] >= highs[j] for j in range(i-2, i+3) if j != i)
            if is_high:
                buy_side.append(highs[i])
            
            is_low = all(lows[i] <= lows[j] for j in range(i-2, i+3) if j != i)
            if is_low:
                sell_side.append(lows[i])
        
        unique_bsl = []
        for h in sorted(buy_side, reverse=True):
            if not any(abs(h - u) / h < 0.0003 for u in unique_bsl):
                unique_bsl.append(h)
        
        unique_ssl = []
        for l in sorted(sell_side):
            if not any(abs(l - u) / l < 0.0003 for u in unique_ssl):
                unique_ssl.append(l)
        
        return unique_bsl[:10], unique_ssl[:10]
    
    def _detect_sweep(self, df, bsl_levels, ssl_levels):
        """Detecta sweep de liquidez"""
        if len(df) < 3:
            return None
        
        current = df.iloc[-1]
        price = current['close']
        high = current['high']
        low = current['low']
        
        body = abs(current['close'] - current['open'])
        upper_wick = current['high'] - max(current['open'], current['close'])
        lower_wick = min(current['open'], current['close']) - current['low']
        
        for bsl in bsl_levels:
            if high >= bsl * 0.9995 and price < bsl:
                if body > 0 and upper_wick >= body * 1.0:
                    wick_ratio = upper_wick / body
                    confidence = min(80, 50 + int(wick_ratio * 10))
                    return {
                        'signal': 'PUT',
                        'confidence': confidence,
                        'reason': f'Sweep BSL - mecha {wick_ratio:.1f}x'
                    }
        
        for ssl in ssl_levels:
            if low <= ssl * 1.0005 and price > ssl:
                if body > 0 and lower_wick >= body * 1.0:
                    wick_ratio = lower_wick / body
                    confidence = min(80, 50 + int(wick_ratio * 10))
                    return {
                        'signal': 'CALL',
                        'confidence': confidence,
                        'reason': f'Sweep SSL - mecha {wick_ratio:.1f}x'
                    }
        
        return None
    
    def _detect_pullback(self, df, bsl_levels, ssl_levels):
        """Detecta pullback a liquidez"""
        if len(df) < 10:
            return None
        
        price = df.iloc[-1]['close']
        rsi = df.iloc[-1].get('rsi', 50)
        
        # Buscar SSL más cercano
        nearest_ssl = None
        min_dist_ssl = 999
        for ssl in ssl_levels:
            dist = (price - ssl) / ssl * 100
            if 0 < dist < min_dist_ssl:
                min_dist_ssl = dist
                nearest_ssl = ssl
        
        # CALL: Precio cerca de SSL + RSI bajo
        if nearest_ssl and min_dist_ssl < 0.05 and rsi < 50:
            confidence = 60 + int((50 - rsi) / 5)
            return {
                'signal': 'CALL',
                'confidence': min(75, confidence),
                'reason': f'Pullback SSL + RSI {rsi:.1f}'
            }
        
        # Buscar BSL más cercano
        nearest_bsl = None
        min_dist_bsl = 999
        for bsl in bsl_levels:
            dist = (bsl - price) / price * 100
            if 0 < dist < min_dist_bsl:
                min_dist_bsl = dist
                nearest_bsl = bsl
        
        # PUT: Precio cerca de BSL + RSI alto
        if nearest_bsl and min_dist_bsl < 0.05 and rsi > 50:
            confidence = 60 + int((rsi - 50) / 5)
            return {
                'signal': 'PUT',
                'confidence': min(75, confidence),
                'reason': f'Pullback BSL + RSI {rsi:.1f}'
            }
        
        return None
    
    def _analyze_and_trade(self):
        """Analizar y ejecutar operación"""
        
        # En fase PRODUCTION, verificar horario
        if self.phase_manager.is_production():
            can_trade, reason = self.schedule_manager.can_trade()
            if not can_trade:
                return None
        
        asset = self._get_next_asset()
        
        try:
            # Obtener datos
            candles = self.market_data.get_candles(asset, "3m", 100)
            
            if not candles or len(candles) < 20:
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
            
            # Encontrar liquidez
            bsl, ssl = self._find_liquidity_levels(df)
            
            # Detectar sweep
            signal_data = self._detect_sweep(df, bsl, ssl)
            if not signal_data:
                signal_data = self._detect_pullback(df, bsl, ssl)
            
            if not signal_data or signal_data['confidence'] < self.min_confidence:
                return None
            
            signal = signal_data['signal']
            confidence = signal_data['confidence']
            reason = signal_data['reason']
            
            last = df.iloc[-1]
            rsi = last.get('rsi', 50)
            macd_val = last.get('macd', 0)
            
            # Ejecutar
            color = G if signal == "CALL" else R
            print(f"{BOLD}{color}>>> {signal} ${self.capital_per_trade} 3min{X}")
            print(f"Confianza: {confidence}% | RSI: {rsi:.1f} | {reason}")
            
            status, trade_id = self.market_data.api.buy(
                self.capital_per_trade,
                asset,
                signal.lower(),
                3
            )
            
            if not status:
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
                
                # Registrar
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
                
                if self.phase_manager.is_production():
                    self.schedule_manager.record_trade(trade_data)
                
                return trade_data
            
            return None
                
        except Exception as e:
            print(f"{R}[ERROR] {str(e)}{X}")
            return None
    
    def _show_phase_info(self):
        """Mostrar información de fase"""
        phase = self.phase_manager.get_phase()
        status = self.learning_system.get_status()
        phase_status = self.phase_manager.get_status()
        
        print(f"\n{BOLD}{'='*80}{X}")
        
        if phase == "COLLECTION":
            print(f"{Y}FASE 1: RECOLECCIÓN DE DATOS{X}")
            print(f"Operaciones: {status['total_trades']} / {phase_status['requirements']['min_trades']}")
            print(f"Win Rate: {status['win_rate']} / {phase_status['requirements']['min_win_rate']}")
            print(f"Días: {phase_status['days_in_phase']} / {phase_status['requirements']['min_days']}")
            print(f"\n{Y}Recolectando datos sin restricciones...{X}")
        
        else:
            print(f"{G}FASE 2: PRODUCCIÓN{X}")
            schedule = self.schedule_manager.get_status()
            print(f"Operaciones/hora: {schedule['trades_this_hour']}/{schedule['max_per_hour']}")
            print(f"Ganancia/hora: {schedule['total_profit_this_hour']}")
            print(f"Win Rate: {status['win_rate']}")
            print(f"\n{G}Operando con restricciones (10 ops/hora, 5 min entre ops){X}")
        
        print(f"{BOLD}{'='*80}{X}")
    
    def run(self):
        """Ejecutar bot maestro"""
        
        if not self.connect():
            return
        
        print("\n" + "="*80)
        print(f"{BOLD}SISTEMA DE DOS FASES{X}")
        print(f"Fase 1: Recolección (sin restricciones)")
        print(f"Fase 2: Producción (10 ops/hora, 5 min entre ops)")
        print(f"Transición automática cuando tenga suficientes datos")
        print("="*80)
        print(f"Presiona Ctrl+C para detener\n")
        
        try:
            while True:
                try:
                    self.cycle_count += 1
                    
                    # Mostrar info cada 10 ciclos
                    if self.cycle_count % 10 == 0:
                        self._show_phase_info()
                    
                    # Intentar operación
                    result = self._analyze_and_trade()
                    
                    if result:
                        # Verificar transición de fase
                        learning_data = self.learning_system.learning_data
                        if self.phase_manager.check_phase_transition(learning_data):
                            print(f"\n{BOLD}{G}🚀 TRANSICIÓN A FASE 2 - PRODUCCIÓN{X}")
                            self._show_phase_info()
                        
                        # En producción, esperar según horario
                        if self.phase_manager.is_production():
                            self.schedule_manager.wait_for_next_trade()
                        else:
                            # En recolección, esperar menos
                            time.sleep(5)
                    else:
                        time.sleep(5)
                    
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    print(f"{R}[ERROR] {str(e)}{X}")
                    time.sleep(5)
        
        except KeyboardInterrupt:
            pass
        
        self._generate_report()
    
    def _generate_report(self):
        """Generar reporte final"""
        
        status = self.learning_system.get_status()
        phase_status = self.phase_manager.get_status()
        
        print(f"\n\n{BOLD}REPORTE FINAL{X}")
        print("="*80)
        print(f"Fase: {phase_status['current_phase']}")
        print(f"Total operaciones: {status['total_trades']}")
        print(f"Ganancias: {status['wins']}")
        print(f"Pérdidas: {status['losses']}")
        print(f"Win Rate: {status['win_rate']}")
        print(f"Ganancia promedio: {status['avg_profit']}")
        print("="*80)


def main():
    bot = MasterBot()
    bot.run()


if __name__ == "__main__":
    main()
