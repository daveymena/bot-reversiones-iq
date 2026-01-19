import pandas as pd
import numpy as np
from datetime import datetime
import time

class MarketProfiler:
    """
    Analiza el pasado reciente (API) para optimizar la rentabilidad.
    Elegir el mejor tiempo de expiración y el punto de entrada exacto.
    """
    def __init__(self, market_data):
        self.market_data = market_data
        self.profiles = {} # Cache de perfiles por activo

    def profile_asset(self, asset):
        """Descarga datos y encuentra el 'Punto Dulce' de rentabilidad"""
        try:
            print(f"📊 PERFILANDO: {asset} (Buscando tiempo de expiración óptimo)...")
            # Descargamos 500 velas de 1 min para el análisis
            df = self.market_data.get_candles(asset, 60, 500)
            if df.empty:
                print(f"⚠️ API no devolvió datos para {asset}")
                return None
            
            print(f"✅ {len(df)} velas obtenidas. Analizando puntos de entrada...")

            # Simulamos entradas en puntos de sobreventa/sobrecompra (RSI)
            results = {1: 0, 2: 0, 3: 0, 5: 0} # Victorias por minuto
            entries = 0

            # Calcular RSI si no existe
            if 'rsi' not in df.columns:
                print("      ℹ️ Calculando RSI localmente...")
                delta = df['close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                df['rsi'] = 100 - (100 / (1 + rs))

            # Analizamos los últimos 400 cierres
            for i in range(50, len(df) - 6):
                rsi = df.iloc[i].get('rsi', 50)
                price = df.iloc[i]['close']

                # Simular CALL si RSI < 45 (Aún más flexible)
                if rsi < 45:
                    entries += 1
                    for mins in [1, 2, 3, 5]:
                        if (i + mins) < len(df):
                            future_price = df.iloc[i + mins]['close']
                            if future_price > price: results[mins] += 1
                
                # Simular PUT si RSI > 55
                elif rsi > 55:
                    entries += 1
                    for mins in [1, 2, 3, 5]:
                        if (i + mins) < len(df):
                            future_price = df.iloc[i + mins]['close']
                            if future_price < price: results[mins] += 1

            # Analizar el mejor tiempo de expiración
            print(f"      - Entradas simuladas encontradas: {entries}")
            if entries == 0: 
                print(f"      ⚠️ No hay suficientes señales en el historial para {asset}")
                return None

            best_time = 1
            best_winrate = 0
            
            for mins, wins in results.items():
                winrate = (wins / entries) * 100
                if winrate > best_winrate:
                    best_winrate = winrate
                    best_time = mins

            profile = {
                'asset': asset,
                'best_expiration': best_time,
                'winrate_stat': round(best_winrate, 2),
                'reversal_quality': "ALTA" if best_winrate > 60 else "NORMAL",
                'last_update': time.time(),
                'analysis_timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'raw_stats': {str(m): round((r/entries)*100, 2) for m, r in results.items()}
            }
            
            self.profiles[asset] = profile
            self._save_to_disk() # Guardar permanentemente
            print(f"✅ PERFIL COMPLETADO: {asset} | Mejor a {best_time} MIN ({best_winrate:.1f}% Winrate)")
            return profile

        except Exception as e:
            print(f"❌ Error perfilando {asset}: {e}")
            return None

    def _save_to_disk(self):
        """Guarda los perfiles en un archivo JSON para inspección del usuario"""
        import json
        import os
        try:
            data_dir = os.path.join(os.getcwd(), 'data')
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
            
            path = os.path.join(data_dir, 'market_profiles.json')
            with open(path, 'w') as f:
                json.dump(self.profiles, f, indent=4)
        except Exception as e:
            print(f"⚠️ No se pudo guardar el perfil en disco: {e}")

    def get_best_expiration(self, asset):
        """Devuelve el tiempo óptimo para el activo según la estadística actual"""
        if asset in self.profiles:
            # Si el perfil tiene menos de 2 horas, es válido
            if time.time() - self.profiles[asset]['last_update'] < 7200:
                return self.profiles[asset]['best_expiration']
        return 3 # 3 minutos por defecto
