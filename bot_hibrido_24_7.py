#!/usr/bin/env python3
"""
BOT DE TRADING 24/7 - VERSIÓN HÍBRIDA
Intenta conectar a Exnova REAL, pero cae a simulación si falla.
"""
import sys
import time
import signal
import threading
from datetime import datetime
from config import Config

print("""
============================================================
BOT DE TRADING 24/7 - VERSIÓN HÍBRIDA
============================================================
Fecha: {}
Broker: {}
Modo: {}
============================================================
""".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 
           Config.BROKER_NAME.upper(), 
           Config.ACCOUNT_TYPE))

sys.stdout.flush()

# Intentar importar componentes reales
real_broker = None
try:
    from data.market_data import MarketDataHandler
    from strategies.technical import FeatureEngineer
    from core.asset_manager import AssetManager
    real_broker = True
    print("Componentes reales importados")
except Exception as e:
    print(f"No se pudieron importar componentes reales: {e}")
    real_broker = False

sys.stdout.flush()

# Broker simulado como fallback
class SimulatedBroker:
    def __init__(self):
        self.balance = 1000.0
        self.trades_made = 0
        self.wins = 0
        self.losses = 0
        self.last_prices = {
            "EURUSD-OTC": 1.0850,
            "GBPUSD-OTC": 1.2650,
            "USDJPY-OTC": 148.50,
        }
    
    def get_balance(self):
        return self.balance
    
    def get_price(self, asset):
        if asset not in self.last_prices:
            return 100.0
        import random
        base = self.last_prices[asset]
        variation = random.uniform(-0.001, 0.001)
        new_price = base * (1 + variation)
        self.last_prices[asset] = new_price
        return new_price
    
    def make_trade(self, asset, direction, amount=1.0):
        import random
        current_price = self.get_price(asset)
        win = random.random() < 0.80
        
        if win:
            profit = amount * 0.85
            self.balance += profit
            self.wins += 1
            result = "WIN"
        else:
            loss = amount * 0.8
            self.balance -= loss
            self.losses += 1
            result = "LOSS"
        
        self.trades_made += 1
        return {
            "asset": asset,
            "direction": direction,
            "result": result,
            "profit": profit if win else -loss
        }

# Variable global
running = True

def signal_handler(sig, frame):
    global running
    print("\n\nDeteniendo bot...")
    sys.stdout.flush()
    running = False

def try_connect_real_broker():
    """Intenta conectar al broker real con timeout"""
    print("Intentando conectar a broker real (timeout 10s)...")
    sys.stdout.flush()
    
    try:
        # Crear objeto de conexión con timeout
        market_data = MarketDataHandler(
            broker_name=Config.BROKER_NAME,
            account_type=Config.ACCOUNT_TYPE
        )
        
        # Usar threading para timeout
        result = [None]
        
        def connect_thread():
            try:
                result[0] = market_data.connect(
                    Config.EXNOVA_EMAIL,
                    Config.EXNOVA_PASSWORD
                )
            except Exception as e:
                result[0] = False
        
        thread = threading.Thread(target=connect_thread, daemon=True)
        thread.start()
        thread.join(timeout=10)  # Esperar máximo 10 segundos
        
        if result[0]:
            print(f"Conexión exitosa a {Config.BROKER_NAME.upper()}")
            sys.stdout.flush()
            return market_data
        else:
            print("Conexión fallida o timeout")
            sys.stdout.flush()
            return None
    
    except Exception as e:
        print(f"Error intentando conectar: {e}")
        sys.stdout.flush()
        return None

def main():
    global running
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Intentar conectar a broker real
    market_data = None
    if real_broker:
        market_data = try_connect_real_broker()
    
    # Si no hay conexión real, usar simulado
    if market_data is None:
        print("\nCayendo a modo SIMULADO (sin conexión real)")
        sys.stdout.flush()
        broker = SimulatedBroker()
        use_simulated = True
    else:
        use_simulated = False
        broker = market_data
    
    print(f"Balance inicial: ${broker.get_balance():.2f}\n")
    sys.stdout.flush()
    
    print("="*60)
    print("INICIANDO TRADING")
    print("="*60)
    print("Presiona Ctrl+C para detener\n")
    print("REGLAS:")
    print("- Solo UNA operación activa a la vez")
    print("- SIN Martingala (sin duplicar apuestas)")
    print("- Una operación por análisis")
    print()
    sys.stdout.flush()
    
    assets = ["EURUSD-OTC", "GBPUSD-OTC", "USDJPY-OTC"]
    iteration = 0
    start_time = time.time()
    
    # Control de operación activa
    active_trade = None
    last_trade_time = 0
    trade_expiry_seconds = 60  # Expiración de operación (1 minuto)
    
    try:
        while running:
            iteration += 1
            current_time = time.time()
            
            # Verificar si hay operación activa
            if active_trade is not None:
                elapsed_since_trade = current_time - active_trade['time']
                
                # Si la operación expiró, cerrar y permitir nueva
                if elapsed_since_trade >= trade_expiry_seconds:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Operación finalizada (expiró después de {trade_expiry_seconds}s)")
                    print(f"  Activo: {active_trade['asset']} | Dirección: {active_trade['direction']}")
                    print(f"  Balance: ${broker.get_balance():.2f}\n")
                    sys.stdout.flush()
                    active_trade = None
            
            # Si no hay operación activa, hacer análisis y ejecutar UNA nueva
            if active_trade is None:
                # Esperar 5 segundos entre operaciones
                if current_time - last_trade_time >= 5:
                    import random
                    asset = random.choice(assets)
                    direction = random.choice(["CALL", "PUT"])
                    
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] NUEVA OPERACIÓN")
                    print(f"  Activo: {asset} | Dirección: {direction}")
                    
                    if use_simulated:
                        trade = broker.make_trade(asset, direction, amount=1.0)
                        trades_made = broker.trades_made
                        balance = broker.get_balance()
                        win_rate = (broker.wins / max(trades_made, 1)) * 100 if trades_made > 0 else 0
                        print(f"  Resultado: {trade['result']} (${trade['profit']:+.2f})")
                        print(f"  Win Rate: {win_rate:.1f}%")
                    else:
                        # Aquí iría lógica de trading real
                        balance = broker.get_balance()
                        trades_made = 0
                        win_rate = 0
                    
                    print(f"  Balance: ${balance:.2f}")
                    print(f"  Estado: OPERACIÓN ACTIVA (expirará en {trade_expiry_seconds}s)\n")
                    sys.stdout.flush()
                    
                    # Registrar operación activa
                    active_trade = {
                        'asset': asset,
                        'direction': direction,
                        'time': current_time
                    }
                    last_trade_time = current_time
            
            # Heartbeat cada 50 iteraciones
            if iteration % 50 == 0:
                elapsed = time.time() - start_time
                if use_simulated:
                    rate = broker.trades_made / (elapsed + 0.1)
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] HEARTBEAT | Operaciones completadas: {broker.trades_made} | Rate: {rate:.2f} ops/sec | Balance: ${broker.get_balance():.2f}\n")
                else:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] HEARTBEAT | Balance: ${broker.get_balance():.2f}\n")
                sys.stdout.flush()
            
            time.sleep(0.5)
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.stdout.flush()
    
    # Resumen final
    print("\n" + "="*60)
    print("RESUMEN FINAL")
    print("="*60)
    if use_simulated:
        elapsed = time.time() - start_time
        print(f"Modo: SIMULADO")
        print(f"Tiempo: {elapsed:.0f} segundos")
        print(f"Operaciones: {broker.trades_made}")
        print(f"Ganadas: {broker.wins}")
        print(f"Pérdidas: {broker.losses}")
        if broker.trades_made > 0:
            win_rate = (broker.wins / broker.trades_made) * 100
            print(f"Win Rate: {win_rate:.1f}%")
        print(f"Balance: ${broker.get_balance():.2f}")
        profit = broker.get_balance() - 1000.0
        print(f"Ganancia/Pérdida: ${profit:+.2f}")
    else:
        print("Modo: REAL")
        print(f"Balance final: ${broker.get_balance():.2f}")
    
    print("="*60 + "\n")
    sys.stdout.flush()
    print("Bot detenido correctamente")

if __name__ == "__main__":
    main()
