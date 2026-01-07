"""
🇪🇺 ESTUDIO DETALLADO EURUSD - SUBIDAS Y BAJADAS
Analiza vela por vela el comportamiento exacto del Euro
"""
import time
import pandas as pd
from datetime import datetime
import sys
sys.path.insert(0, '.')

from data.market_data import MarketDataHandler
import config

def detailed_study(duration_minutes=15):
    market_data = MarketDataHandler(broker_name=config.Config.BROKER_NAME, 
                                   account_type=config.Config.ACCOUNT_TYPE)
    
    print("\n" + "="*80)
    print("🇪🇺 ANALIZADOR DE PRECISIÓN: EURUSD")
    print(f"   Iniciando estudio de {duration_minutes} minutos")
    print("="*80)
    
    if not market_data.connect(config.Config.EXNOVA_EMAIL, config.Config.EXNOVA_PASSWORD):
        print("❌ Error de conexión")
        return

    asset = "EURUSD-OTC"
    history = []
    
    print(f"\n📡 Monitoreando {asset} en tiempo real...")
    print(f"{'Hora':<10} | {'Precio':<10} | {'Tipo':<8} | {'Fuerza':<8} | {'Racha':<5}")
    print("-" * 50)
    
    start_time = time.time()
    last_candle_time = None
    
    current_streak = 0
    current_type = None
    
    try:
        while time.time() - start_time < duration_minutes * 60:
            # Pedir últimas 2 velas para ver el cierre de la más reciente
            df = market_data.get_candles(asset, 60, 2, time.time())
            
            if not df.empty:
                last_candle = df.iloc[-1]
                candle_time = df.index[-1]
                
                if candle_time != last_candle_time:
                    last_candle_time = candle_time
                    
                    price = last_candle['close']
                    open_p = last_candle['open']
                    c_type = "🟢 SUBE" if price > open_p else "🔴 BAJA" if price < open_p else "⚪ DOJI"
                    strength = abs(price - open_p)
                    
                    if c_type == current_type:
                        current_streak += 1
                    else:
                        current_type = c_type
                        current_streak = 1
                    
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    print(f"{timestamp:<10} | {price:<10.5f} | {c_type:<8} | {strength:<8.5f} | {current_streak:<5}")
                    
                    history.append({
                        'timestamp': timestamp,
                        'price': price,
                        'type': c_type,
                        'strength': strength,
                        'streak': current_streak
                    })
            
            time.sleep(10) # Poll every 10 seconds to detect new candle
            
    except KeyboardInterrupt:
        print("\n⚠️ Estudio interrumpido")
    
    print("\n" + "="*80)
    print("📊 RESULTADOS DEL ESTUDIO EURUSD")
    print("="*80)
    
    if history:
        df_hist = pd.DataFrame(history)
        subidas = len(df_hist[df_hist['type'] == '🟢 SUBE'])
        bajadas = len(df_hist[df_hist['type'] == '🔴 BAJA'])
        max_streak = df_hist['streak'].max()
        
        print(f"✅ Velas analizadas: {len(history)}")
        print(f"✅ Total subidas: {subidas}")
        print(f"✅ Total bajadas: {bajadas}")
        print(f"✅ Racha máxima detectada: {max_streak}")
        
        # Guardar para el bot
        with open("data/eurusd_precision_study.json", "w") as f:
            import json
            json.dump(history, f, indent=2)
        print("\n💾 Datos de precisión guardados en data/eurusd_precision_study.json")
    else:
        print("❌ No se recolectaron datos")

if __name__ == "__main__":
    detailed_study(10) # 10 minutos de estudio intensivo
