#!/usr/bin/env python3
"""
BOT TRADING - OPERACION SIMPLE
"""
import time
from datetime import datetime
from config import Config
from exnovaapi.stable_api import Exnova

print("\n" + "="*50)
print("BOT TRADING 24/7 - RUN")
print("="*50)

# Conectar
api = Exnova(Config.EXNOVA_EMAIL, Config.EXNOVA_PASSWORD)
status, _ = api.connect()
print(f"Conectado: {status}")

bal = api.get_balance()
print(f"Balance: ${bal:.2f}")

# Verificar señal
candles = api.get_candles("EURUSD-OTC", 60, 20, time.time())
print(f"Candles: {len(candles) if candles else 0}")

# Comprar
result = api.buy(1, "EURUSD-OTC", "call", 1)
print(f"Compra: {result}")

if result and result[0]:
    order_id = result[1]
    print(f"Orden: {order_id} - esperando...")
    time.sleep(70)
    
    order_result = api.check_binary_order(order_id)
    print(f"Resultado: {order_result}")