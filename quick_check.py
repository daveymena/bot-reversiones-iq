
import pandas as pd
from data.market_data import MarketDataHandler
from config import Config

def analyze_now():
    handler = MarketDataHandler()
    if not handler.connect():
        print("Error conectando")
        return
    
    asset = "USDCAD-OTC"
    df = handler.get_candles(asset, 60, 50)
    if df.empty:
        print("No hay datos")
        return
        
    last = df.iloc[-1]
    major_high = df['high'].max()
    major_low = df['low'].min()
    price = last['close']
    
    print(f"\n--- ANALISIS EXPRESS {asset} ---")
    print(f"Precio Actual: {price}")
    print(f"RSI: {last.get('rsi', 'N/A')}")
    print(f"Resistencia Max (50m): {major_high}")
    print(f"Soporte Min (50m): {major_low}")
    
    dist_to_high = (major_high - price) / price * 100
    print(f"Distancia a Techo: {dist_to_high:.4f}%")
    
    if dist_to_high < 0.03:
        print("❌ NO CONFIABLE PARA CALL: Demasiado cerca de la resistencia.")
    elif price > df['sma_20'].iloc[-1] and last.get('rsi', 50) > 60:
        print("✅ FUERZA ALCISTA: Pero cuidado con el retroceso.")
    else:
        print("🟡 NEUTRAL: Esperando confirmación.")

if __name__ == "__main__":
    analyze_now()
