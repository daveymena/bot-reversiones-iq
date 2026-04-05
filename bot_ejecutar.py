#!/usr/bin/env python3
"""
BOT TRADING 24/7 - VERSION FINAL
- 1 operación por análisis
- 1 minuto expiración  
- Esperar resultado
- Analizar y aprender
"""
import sys
import time
import signal
from datetime import datetime
from config import Config
from exnovaapi.stable_api import Exnova

running = True
trades_wins = 0
trades_losses = 0

def signal_handler(sig, frame):
    global running
    print("\n>> DETENIENDO <<")
    running = False

def calculate_rsi(prices, period=14):
    if not prices or len(prices) < period + 1:
        return 50
    deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
    gains = [d if d > 0 else 0 for d in deltas]
    losses = [-d if d < 0 else 0 for d in deltas]
    avg_gain = sum(gains[-period:]) / period if gains else 0
    avg_loss = sum(losses[-period:]) / period if losses else 0
    if avg_loss == 0:
        return 100
    return 100 - (100 / (1 + avg_gain/avg_loss))

def get_signal(api, asset):
    """Analiza activo - retorna señal fuerte"""
    try:
        candles = api.get_candles(asset, 60, 30, time.time())
        if not candles or len(candles) < 15:
            return None, None, None
        
        closes = [c['close'] for c in candles]
        rsi = calculate_rsi(closes)
        
        # Señales FUERTES
        if rsi < 25:
            return "call", rsi, "CALL RSI<25"
        elif rsi > 75:
            return "put", rsi, "PUT RSI>75"
        elif rsi < 35 and closes[-1] > closes[-2] > closes[-3]:
            return "call", rsi, "CALL 3 velas SUBIENDO"
        elif rsi > 65 and closes[-1] < closes[-2] < closes[-3]:
            return "put", rsi, "PUT 3 velas BAJANDO"
        
        return None, None, None
    except:
        return None, None, None

def execute_trade(api, asset, direction):
    """Hace UNA operación de 1 minuto"""
    try:
        print(f"    {direction.upper()} en {asset} (1min)...")
        
        result = api.buy(1, asset, direction, 1)
        
        if not result or not result[0]:
            print(f"    Error: {result[1] if result else 'Sin respuesta'}")
            return None
        
        order_id = result[1]
        print(f"    Orden: {order_id} - Esperando 70s...")
        
        # Esperar 70 segundos (1 minuto + buffer)
        time.sleep(70)
        
        # Obtener resultado
        try:
            order_result = api.check_binary_order(order_id)
            return order_result
        except Exception as e:
            print(f"    Error getting result: {e}")
            return None
            
    except Exception as e:
        print(f"    Error: {e}")
        return None

def main():
    global running, trades_wins, trades_losses
    
    signal.signal(signal.SIGINT, signal_handler)
    
    print("\n" + "="*50)
    print("BOT TRADING 24/7 - FINAL")
    print("="*50)
    
    try:
        print("\n[1] Conectando...")
        api = Exnova(Config.EXNOVA_EMAIL, Config.EXNOVA_PASSWORD)
        status, _ = api.connect()
        
        if not status:
            print("ERROR CONEXION")
            return 1
        
        print("CONECTADO!")
        
        bal = api.get_balance()
        balance_inicial = bal
        print(f"Balance inicial: ${bal:.2f}")
        
        api.update_ACTIVES_OPCODE()
        
        assets = ["EURUSD-OTC", "GBPUSD-OTC", "USDJPY-OTC", "AUDUSD-OTC"]
        
        print("\n[2] INICIANDO...")
        print("="*50 + "\n")
        
        iteration = 0
        
        while running:
            iteration += 1
            
            bal = api.get_balance()
            pnl = bal - balance_inicial
            wr = trades_wins / (trades_wins + trades_losses) * 100 if trades_wins + trades_losses else 0
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] #{iteration} Bal:${bal:.2f} PnL:${pnl:.2f} W:{trades_wins} L:{trades_losses} WR:{wr:.0f}%")
            
            signal_found = False
            
            for asset in assets:
                if not running:
                    break
                
                direction, rsi, pattern = get_signal(api, asset)
                
                if direction:
                    print(f"\n*** SEÑAL: {asset} | {pattern} (RSI:{rsi:.0f}) ***")
                    
                    order_result = execute_trade(api, asset, direction)
                    
                    if order_result:
                        result = order_result.get('result', '')
                        profit = order_result.get('profit', 0)
                        
                        if result == 'win':
                            trades_wins += 1
                            print(f"\n>>> GANASTE! +${profit:.2f} <<<")
                        elif result == 'loose':
                            trades_losses += 1
                            print(f"\n>>> PERDISTE <<<")
                        elif result == 'equal':
                            print(f"\n>>> EMPATE <<<")
                        else:
                            print(f"\n>>> resultado: {result} <<<")
                    else:
                        print(">>> OPERACION FALLA <<<")
                    
                    signal_found = True
                    break
            
            if not signal_found:
                print("  Sin señal clara - esperando 20s...")
                time.sleep(20)
            
            time.sleep(3)
            
    except KeyboardInterrupt:
        print("\n\nDETENIDO POR USUARIO")
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()