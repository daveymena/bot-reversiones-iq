import pandas as pd
import numpy as np
import os
import sys
import json
import time
from datetime import datetime
from data.market_data import MarketDataHandler
from config import Config

# Asegurar que el path sea correcto
sys.path.append(os.getcwd())

class MarketDeepDive:
    """
    Realiza un análisis masivo de datos históricos para identificar
    los horarios y activos más rentables.
    """
    def __init__(self, days=3):
        self.days = days
        self.market_data = MarketDataHandler(broker_name="exnova", account_type="PRACTICE")
        self.assets = [
            "EURUSD-OTC", "GBPUSD-OTC", "USDJPY-OTC",
            "AUDUSD-OTC", "EURJPY-OTC", "GBPJPY-OTC"
        ]
        self.results = {}

    def run_analysis(self):
        print("\n" + "="*80)
        print(f"🚀 INICIANDO DEEP DIVE DE MERCADO ({self.days} días de historia)")
        print("="*80)

        # Conectar
        email = os.getenv("EXNOVA_EMAIL")
        password = os.getenv("EXNOVA_PASSWORD")
        if not self.market_data.connect(email, password):
            print("❌ No se pudo conectar al broker.")
            return

        for asset in self.assets:
            print(f"\n🔍 Analizando {asset}...")
            # Descargar datos masivos (velas de 1 min)
            total_candles = 1440 * self.days
            df = self.market_data.get_candles(asset, 60, total_candles, time.time())
            
            if df.empty:
                print(f"⚠️ No hay datos para {asset}")
                continue

            print(f"✅ Descargadas {len(df)} velas. Procesando...")
            
            # Analizar rentabilidad por hora con múltiples estrategias
            hour_report = self._deep_analyze_asset(df)
            self.results[asset] = hour_report

        # Guardar resultados
        self._save_results()
        self.market_data.disconnect()
        print("\n" + "="*80)
        print("✅ ANÁLISIS COMPLETADO. Datos guardados en data/market_deep_dive.json")
        print("="*80)

    def _deep_analyze_asset(self, df):
        """Analiza múltiples estrategias y tiempos para encontrar el 'Sweet Spot' horario"""
        df = self._add_indicators(df)
        df['hour'] = df.index.hour
        
        report = {}
        for hour in range(24):
            hour_data = df[df['hour'] == hour]
            if len(hour_data) < 30: continue
            
            best_hour_wr = 0
            best_exp = 2
            total_trades = 0
            
            # Testeamos expiraciones de 1 a 5 min
            for exp in [1, 2, 3, 5]:
                wins = 0
                trades = 0
                for i in range(len(hour_data) - 6):
                    price = hour_data.iloc[i]['close']
                    rsi = hour_data.iloc[i]['rsi']
                    upper = hour_data.iloc[i]['bb_upper']
                    lower = hour_data.iloc[i]['bb_lower']
                    
                    signal = 0 # 1=CALL, 2=PUT
                    # Confluencia RSI + Bollinger
                    if rsi < 35 and price <= lower: signal = 1
                    elif rsi > 65 and price >= upper: signal = 2
                    
                    if signal > 0:
                        trades += 1
                        if (i + exp) < len(hour_data):
                            future = hour_data.iloc[i+exp]['close']
                            if (signal == 1 and future > price) or (signal == 2 and future < price):
                                wins += 1
                
                wr = (wins / trades * 100) if trades >= 5 else 0
                if wr > best_hour_wr:
                    best_hour_wr = wr
                    best_exp = exp
                    total_trades = trades

            report[hour] = {
                'winrate': round(best_hour_wr, 2),
                'best_exp': best_exp,
                'trades_found': total_trades,
                'is_golden': best_hour_wr >= 65 and total_trades >= 5,
                'volatility': round(hour_data['close'].std(), 5)
            }
        return report

    def _add_indicators(self, df):
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        df['rsi'] = 100 - (100 / (1 + (gain / loss)))
        # Bollinger
        df['sma_20'] = df['close'].rolling(window=20).mean()
        df['std'] = df['close'].rolling(window=20).std()
        df['bb_upper'] = df['sma_20'] + (df['std'] * 2)
        df['bb_lower'] = df['sma_20'] - (df['std'] * 2)
        return df.dropna()

    def _save_results(self):
        data_dir = os.path.join(os.getcwd(), 'data')
        if not os.path.exists(data_dir): os.makedirs(data_dir)
        
        path = os.path.join(data_dir, 'market_deep_dive.json')
        with open(path, 'w') as f:
            json.dump(self.results, f, indent=4)

if __name__ == "__main__":
    days = 3
    if len(sys.argv) > 1:
        days = int(sys.argv[1])
    
    analyzer = MarketDeepDive(days=days)
    analyzer.run_analysis()
