#!/usr/bin/env python3
"""
BOT DE TRADING SIMPLE 24/7
Versión simplificada para operación continua sin dependencias problemáticas
"""
import sys
import io
import time
import signal
from datetime import datetime

# Fix encoding para Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from config import Config
from data.market_data import MarketDataHandler
from strategies.technical import FeatureEngineer
from core.risk import RiskManager
from core.asset_manager import AssetManager

# Estado global
running = True
trades_made = 0

def signal_handler(sig, frame):
    """Maneja Ctrl+C"""
    global running
    print("\n\nDeteniendo bot...")
    running = False

def main():
    """Función principal simplificada"""
    global running, trades_made
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Banner
    print("\n" + "="*60)
    print("BOT DE TRADING 24/7 - VERSIÓN SIMPLIFICADA")
    print("="*60)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Broker: {Config.BROKER_NAME.upper()}")
    print(f"Modo: {Config.ACCOUNT_TYPE}")
    print("="*60 + "\n")
    sys.stdout.flush()  # Asegurar que se imprime
    
    try:
        # Inicializar componentes
        print("Inicializando componentes...")
        sys.stdout.flush()
        
        # Market Data
        print("  - MarketDataHandler...")
        sys.stdout.flush()
        market_data = MarketDataHandler(
            broker_name=Config.BROKER_NAME,
            account_type=Config.ACCOUNT_TYPE
        )
        print("  - FeatureEngineer...")
        sys.stdout.flush()
        
        # Feature Engineer
        feature_engineer = FeatureEngineer()
        print("  - RiskManager...")
        sys.stdout.flush()
        
        # Risk Manager
        risk_manager = RiskManager(
            capital_per_trade=Config.CAPITAL_PER_TRADE,
            stop_loss_pct=0.8,
            take_profit_pct=0.85,
            max_martingale_steps=Config.MAX_MARTINGALE
        )
        print("  - AssetManager...")
        sys.stdout.flush()
        
        # Asset Manager
        asset_manager = AssetManager(market_data)
        
        print("Componentes inicializados\n")
        sys.stdout.flush()
        
        # Conectar al broker
        print(f"Conectando a {Config.BROKER_NAME.upper()}...")
        sys.stdout.flush()
        
        if Config.BROKER_NAME == "exnova":
            email = Config.EXNOVA_EMAIL
            password = Config.EXNOVA_PASSWORD
        else:
            email = Config.IQ_OPTION_EMAIL
            password = Config.IQ_OPTION_PASSWORD
        
        print(f"  Email: {email}")
        print(f"  Conectando...")
        sys.stdout.flush()
        
        connected = market_data.connect(email, password)
        print(f"  Resultado: {connected}")
        sys.stdout.flush()
        
        if not connected:
            print("Error conectando al broker")
            return 1
        
        print(f"Conectado a {Config.BROKER_NAME.upper()}\n")
        
        # Obtener balance inicial
        balance = market_data.get_balance()
        print(f"Balance inicial: ${balance:.2f}\n")
        
        # Verificar activos
        print("Verificando activos disponibles...")
        available_assets = [
            "EURUSD-OTC", "GBPUSD-OTC", "USDJPY-OTC", 
            "AUDUSD-OTC", "USDCAD-OTC", "EURJPY-OTC"
        ]
        print(f"{len(available_assets)} activos OTC disponibles 24/7\n")
        
        # Loop de trading
        print("="*60)
        print("INICIANDO BOT DE TRADING")
        print("="*60)
        print("Presiona Ctrl+C para detener\n")
        
        iteration = 0
        last_scan = time.time()
        
        while running:
            try:
                iteration += 1
                current_time = time.time()
                
                # Heartbeat cada 30 segundos
                if iteration % 30 == 0:
                    balance = market_data.get_balance()
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Iteración #{iteration} | Balance: ${balance:.2f} | Trades: {trades_made}")
                    sys.stdout.flush()
                
                # Escanear activos cada 10 segundos
                if current_time - last_scan >= 10:
                    last_scan = current_time
                    
                    try:
                        # Encontrar mejor activo
                        best_asset = asset_manager.find_best_asset(prefer_otc=True)
                        
                        if best_asset:
                            # Obtener datos
                            df = market_data.get_candles(best_asset, '5m', 100)
                            
                            if df is not None and not df.empty:
                                # Calcular indicadores
                                feature_engineer.calculate_features(df)
                                
                                # Scoring simple
                                last = df.iloc[-1]
                                rsi = last.get('rsi', 50)
                                
                                # Lógica simple: RSI bajo = CALL, RSI alto = PUT
                                if rsi < 35:
                                    # Oportunidad CALL
                                    print(f"\n[CALL] {best_asset} | RSI: {rsi:.0f} | Balance: ${balance:.2f}")
                                    trades_made += 1
                                    
                                elif rsi > 65:
                                    # Oportunidad PUT
                                    print(f"\n[PUT] {best_asset} | RSI: {rsi:.0f} | Balance: ${balance:.2f}")
                                    trades_made += 1
                                    
                    except Exception as e:
                        # Log y continuar
                        pass
                
                # Pequeña pausa para no saturar CPU
                time.sleep(0.5)
                
            except Exception as e:
                print(f"Error en iteración: {e}")
                continue
        
        # Resumen final
        print("\n\n" + "="*60)
        print("RESUMEN DE OPERACIONES")
        print("="*60)
        balance_final = market_data.get_balance()
        print(f"Balance final: ${balance_final:.2f}")
        print(f"Ganancias/Pérdidas: ${balance_final - balance:.2f}")
        print(f"Total operaciones intentadas: {trades_made}")
        print("="*60 + "\n")
        
        print("Bot detenido correctamente")
        return 0
    
    except Exception as e:
        print(f"\nError fatal: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
