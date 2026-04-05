#!/usr/bin/env python3
"""BOT MINIMALISTA"""
import sys
import time
import signal
from config import Config
from data.market_data import MarketDataHandler
from strategies.technical import FeatureEngineer

def main():
    print("BOT INICIADO")
    sys.stdout.flush()
    
    try:
        print("1. Creando MarketData...")
        sys.stdout.flush()
        market_data = MarketDataHandler(
            broker_name=Config.BROKER_NAME,
            account_type=Config.ACCOUNT_TYPE
        )
        
        print("2. Creando FeatureEngineer...")
        sys.stdout.flush()
        feature_engineer = FeatureEngineer()
        
        print("3. Conectando...")
        sys.stdout.flush()
        result = market_data.connect(Config.EXNOVA_EMAIL, Config.EXNOVA_PASSWORD)
        print(f"   Conectado: {result}")
        sys.stdout.flush()
        
        print("4. Obteniendo balance...")
        sys.stdout.flush()
        balance = market_data.get_balance()
        print(f"   Balance: {balance}")
        sys.stdout.flush()
        
        print("5. Bucle de trading...")
        sys.stdout.flush()
        
        for i in range(10):
            print(f"   Iteracion {i+1}...")
            sys.stdout.flush()
            time.sleep(1)
        
        print("BOT COMPLETADO")
        sys.stdout.flush()
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.stdout.flush()

if __name__ == "__main__":
    main()
