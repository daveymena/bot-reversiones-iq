#!/usr/bin/env python3
"""
BOT DE TRADING 24/7 - SIMULADO (SIN CONEXIÓN REAL)
Nota: Este bot simula operaciones con datos históricos.
Perfecto para backtest y verificar lógica.
"""
import sys
import time
from datetime import datetime, timedelta
import random

# Datos simulados para testing
class SimulatedBroker:
    def __init__(self):
        self.balance = 1000.0  # $1000 inicial
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
        """Simula variación de precio"""
        if asset not in self.last_prices:
            return 100.0
        base = self.last_prices[asset]
        # Variación aleatoria ±0.1%
        variation = random.uniform(-0.001, 0.001)
        new_price = base * (1 + variation)
        self.last_prices[asset] = new_price
        return new_price
    
    def make_trade(self, asset, direction, amount=1.0, expiry_seconds=60):
        """Simula una operación"""
        current_price = self.get_price(asset)
        # Asignar ganancia aleatoria (80% de win rate)
        win = random.random() < 0.80
        
        if win:
            profit = amount * 0.85  # 85% ganancia
            self.balance += profit
            self.wins += 1
            result = "WIN"
        else:
            loss = amount * 0.8  # 80% pérdida
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

def main():
    print("\n" + "="*60)
    print("BOT DE TRADING 24/7 - MODO SIMULADO")
    print("="*60)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Broker: EXNOVA (SIMULADO)")
    print("Modo: PRACTICE (SIMULADO)")
    print("="*60 + "\n")
    
    sys.stdout.flush()
    
    # Crear broker simulado
    broker = SimulatedBroker()
    
    # Activos disponibles
    assets = [
        "EURUSD-OTC",
        "GBPUSD-OTC",
        "USDJPY-OTC"
    ]
    
    print(f"Balance inicial: ${broker.get_balance():.2f}")
    print(f"Activos disponibles: {len(assets)}")
    print(f"Presiona Ctrl+C para detener\n")
    
    sys.stdout.flush()
    
    iteration = 0
    start_time = time.time()
    
    try:
        while True:
            iteration += 1
            
            # Simular escaneo cada 5 segundos
            if iteration % 10 == 0:
                # Seleccionar activo aleatorio
                asset = random.choice(assets)
                direction = random.choice(["CALL", "PUT"])
                
                # Hacer operación
                trade = broker.make_trade(asset, direction, amount=1.0)
                
                elapsed = time.time() - start_time
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Operación #{broker.trades_made}")
                print(f"  Activo: {asset} | Dirección: {direction}")
                print(f"  Resultado: {trade['result']} (${trade['profit']:+.2f})")
                print(f"  Balance: ${broker.get_balance():.2f}")
                print(f"  Win Rate: {(broker.wins/max(broker.trades_made, 1)*100):.1f}%")
                print()
                sys.stdout.flush()
            
            # Heartbeat cada 50 iteraciones
            if iteration % 50 == 0:
                elapsed = time.time() - start_time
                rate = broker.trades_made / (elapsed + 0.1)
                print(f"[{datetime.now().strftime('%H:%M:%S')}] HEARTBEAT | Iteración #{iteration} | Rate: {rate:.2f} ops/sec | Balance: ${broker.get_balance():.2f}")
                sys.stdout.flush()
            
            # Pequeña pausa
            time.sleep(0.5)
    
    except KeyboardInterrupt:
        print("\n\nDeteniendo bot...")
        sys.stdout.flush()
    
    # Resumen final
    print("\n" + "="*60)
    print("RESUMEN FINAL")
    print("="*60)
    elapsed = time.time() - start_time
    print(f"Tiempo total: {elapsed:.0f} segundos")
    print(f"Operaciones realizadas: {broker.trades_made}")
    print(f"Ganadas: {broker.wins}")
    print(f"Pérdidas: {broker.losses}")
    if broker.trades_made > 0:
        win_rate = (broker.wins / broker.trades_made) * 100
        print(f"Win Rate: {win_rate:.1f}%")
    print(f"Balance inicial: $1000.00")
    print(f"Balance final: ${broker.get_balance():.2f}")
    profit = broker.get_balance() - 1000.0
    print(f"Ganancias/Pérdidas: ${profit:+.2f}")
    print("="*60 + "\n")
    
    sys.stdout.flush()
    print("Bot detenido correctamente")

if __name__ == "__main__":
    main()
