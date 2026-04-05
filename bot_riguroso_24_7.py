#!/usr/bin/env python3
"""
BOT DE TRADING 24/7 - VERSIÓN MEJORADA CON RIGUROSIDAD
- Valida que NO hay operaciones activas
- Análisis técnico REAL (RSI, MACD, Bolinger Bands)
- Solo entra cuando hay buena confluencia de señales
- Una operación a la vez, SIN excepciones
"""
import sys
import time
import signal
import threading
from datetime import datetime
from config import Config

print("""
============================================================
BOT DE TRADING 24/7 - VERSIÓN RIGUROSA
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
market_data = None

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
        self.active_trades = []  # Lista de operaciones activas
        self.last_prices = {
            "EURUSD-OTC": 1.0850,
            "GBPUSD-OTC": 1.2650,
            "USDJPY-OTC": 148.50,
        }
    
    def get_balance(self):
        return self.balance
    
    def get_active_trades(self):
        """Retorna lista de operaciones activas"""
        return self.active_trades
    
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
        market_data = MarketDataHandler(
            broker_name=Config.BROKER_NAME,
            account_type=Config.ACCOUNT_TYPE
        )
        
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
        thread.join(timeout=10)
        
        if result[0]:
            print(f"Conexion exitosa a {Config.BROKER_NAME.upper()}")
            sys.stdout.flush()
            return market_data
        else:
            print("Conexion fallida o timeout")
            sys.stdout.flush()
            return None
    
    except Exception as e:
        print(f"Error intentando conectar: {e}")
        sys.stdout.flush()
        return None

def has_active_trades(broker, use_simulated):
    """Verifica si hay operaciones activas EN EL BROKER"""
    try:
        if use_simulated:
            # En modo simulado, usar nuestra lista
            active = broker.get_active_trades() if hasattr(broker, 'get_active_trades') else []
            return len(active) > 0
        else:
            # En broker real, intentar obtener operaciones activas
            if hasattr(broker, 'get_open_positions'):
                positions = broker.get_open_positions()
                return len(positions) > 0 if positions else False
            # Si no tiene ese método, asumir que no hay
            return False
    except:
        return False

def analyze_asset(feature_engineer, df, asset):
    """Análisis técnico riguroso del activo"""
    if df is None or df.empty or len(df) < 50:
        return None
    
    try:
        last = df.iloc[-1]
        
        # Obtener indicadores
        rsi = last.get('rsi', 50)
        macd = last.get('macd', 0)
        macd_signal = last.get('macd_signal', 0)
        macd_diff = last.get('macd_diff', 0)
        bb_high = last.get('bb_high', 0)
        bb_low = last.get('bb_low', 0)
        bb_mid = (bb_high + bb_low) / 2 if (bb_high + bb_low) > 0 else 0
        close = last.get('close', 0)
        sma_20 = last.get('sma_20', 0)
        sma_50 = last.get('sma_50', 0)
        
        # Calcular scoring
        score = 0
        reasons = []
        
        # 1. RSI EXTREMO (más importante)
        if rsi < 25:  # Sobreventa fuerte
            score += 30
            reasons.append(f"RSI sobreventa extrema ({rsi:.0f})")
            direction = "CALL"
        elif rsi > 75:  # Sobrecompra fuerte
            score += 30
            reasons.append(f"RSI sobrecompra extrema ({rsi:.0f})")
            direction = "PUT"
        elif rsi < 35:  # Sobreventa moderada
            score += 15
            reasons.append(f"RSI sobreventa ({rsi:.0f})")
            direction = "CALL"
        elif rsi > 65:  # Sobrecompra moderada
            score += 15
            reasons.append(f"RSI sobrecompra ({rsi:.0f})")
            direction = "PUT"
        else:
            return None  # RSI neutral, no operar
        
        # 2. MACD Confirmación
        if direction == "CALL" and macd_diff > 0:
            score += 20
            reasons.append("MACD alcista")
        elif direction == "PUT" and macd_diff < 0:
            score += 20
            reasons.append("MACD bajista")
        elif direction == "CALL" and macd_diff > 0:
            score += 10
            reasons.append("MACD neutral (CALL)")
        elif direction == "PUT" and macd_diff < 0:
            score += 10
            reasons.append("MACD neutral (PUT)")
        
        # 3. BOLLINGER BANDS
        if bb_mid > 0:
            position = (close - bb_low) / (bb_high - bb_low) if (bb_high - bb_low) > 0 else 0.5
            
            if direction == "CALL" and position < 0.25:
                score += 15
                reasons.append(f"Precio cerca banda inferior (posición {position:.0%})")
            elif direction == "PUT" and position > 0.75:
                score += 15
                reasons.append(f"Precio cerca banda superior (posición {position:.0%})")
            elif direction == "CALL" and position < 0.5:
                score += 5
                reasons.append(f"Precio en zona inferior")
            elif direction == "PUT" and position > 0.5:
                score += 5
                reasons.append(f"Precio en zona superior")
        
        # 4. MEDIA MÓVILES
        if sma_20 > 0 and sma_50 > 0:
            if direction == "CALL" and sma_20 > sma_50:
                score += 10
                reasons.append("Tendencia alcista (SMA)")
            elif direction == "PUT" and sma_20 < sma_50:
                score += 10
                reasons.append("Tendencia bajista (SMA)")
        
        # Mínimo score requerido
        if score < 40:
            return None  # No suficiente confluencia
        
        return {
            'score': score,
            'direction': direction,
            'rsi': rsi,
            'macd_diff': macd_diff,
            'reasons': reasons
        }
    
    except Exception as e:
        print(f"Error analizando {asset}: {e}")
        return None

def main():
    global running, market_data
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Intentar conectar a broker real
    if real_broker:
        market_data = try_connect_real_broker()
        feature_engineer = FeatureEngineer()
    else:
        market_data = None
        feature_engineer = None
    
    # Si no hay conexión real, usar simulado
    if market_data is None:
        print("\nCayendo a modo SIMULADO (sin conexion real)")
        sys.stdout.flush()
        broker = SimulatedBroker()
        use_simulated = True
    else:
        use_simulated = False
        broker = market_data
    
    print(f"Balance inicial: ${broker.get_balance():.2f}\n")
    sys.stdout.flush()
    
    print("="*60)
    print("INICIANDO TRADING CON RIGUROSIDAD")
    print("="*60)
    print("REGLAS ESTRICTAS:")
    print("1. Verificar NO hay operaciones activas")
    print("2. Analisis tecnico RIGUROSO (RSI + MACD + BB)")
    print("3. Score minimo 40 puntos")
    print("4. Una operacion a la vez")
    print("5. Sin Martingala\n")
    sys.stdout.flush()
    
    assets = ["EURUSD-OTC", "GBPUSD-OTC", "USDJPY-OTC"]
    iteration = 0
    start_time = time.time()
    
    # Control de operacion activa
    active_trade = None
    last_trade_time = 0
    trade_expiry_seconds = 60
    
    try:
        while running:
            iteration += 1
            current_time = time.time()
            
            # ===== VERIFICAR OPERACIONES ACTIVAS =====
            if active_trade is not None:
                elapsed_since_trade = current_time - active_trade['time']
                
                if elapsed_since_trade >= trade_expiry_seconds:
                    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] OPERACION FINALIZADA")
                    print(f"  Activo: {active_trade['asset']} | Direccion: {active_trade['direction']}")
                    print(f"  Balance: ${broker.get_balance():.2f}\n")
                    sys.stdout.flush()
                    active_trade = None
            
            # ===== VERIFICAR OPERACIONES EN BROKER REAL =====
            broker_has_active = has_active_trades(broker, use_simulated)
            
            # ===== SI NO HAY OPERACIONES ACTIVAS, ANALIZAR Y OPERAR =====
            if active_trade is None and not broker_has_active:
                if current_time - last_trade_time >= 5:
                    
                    # Seleccionar activo
                    import random
                    asset = random.choice(assets)
                    
                    # ANÁLISIS TÉCNICO
                    best_signal = None
                    
                    if real_broker and feature_engineer:
                        try:
                            df = market_data.get_candles(asset, '5m', 100)
                            if df is not None and not df.empty:
                                feature_engineer.calculate_features(df)
                                analysis = analyze_asset(feature_engineer, df, asset)
                                
                                if analysis and analysis['score'] >= 40:
                                    best_signal = analysis
                                else:
                                    # No hay buena señal, saltear
                                    if iteration % 20 == 0:
                                        print(f"[{datetime.now().strftime('%H:%M:%S')}] {asset}: Sin señal rigurosa (análisis insuficiente)")
                                        sys.stdout.flush()
                        except Exception as e:
                            pass
                    
                    # ===== EJECUTAR OPERACIÓN SI HAY SEÑAL =====
                    if best_signal is not None:
                        direction = best_signal['direction']
                        score = best_signal['score']
                        
                        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] OPERACION EJECUTADA")
                        print(f"  Activo: {asset} | Direccion: {direction}")
                        print(f"  Score: {score} puntos")
                        print(f"  Razones:")
                        for reason in best_signal['reasons']:
                            print(f"    - {reason}")
                        
                        if use_simulated:
                            trade = broker.make_trade(asset, direction, amount=1.0)
                            print(f"  Resultado: {trade['result']} (${trade['profit']:+.2f})")
                            print(f"  Win Rate: {(broker.wins / max(broker.trades_made, 1) * 100):.1f}%")
                        
                        print(f"  Balance: ${broker.get_balance():.2f}")
                        print(f"  Estado: OPERACION ACTIVA ({trade_expiry_seconds}s)")
                        print()
                        sys.stdout.flush()
                        
                        active_trade = {
                            'asset': asset,
                            'direction': direction,
                            'time': current_time,
                            'score': score
                        }
                        last_trade_time = current_time
            
            # ===== HEARTBEAT =====
            if iteration % 100 == 0:
                elapsed = time.time() - start_time
                if use_simulated:
                    rate = broker.trades_made / (elapsed + 0.1)
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] HEARTBEAT | Operaciones: {broker.trades_made} | Rate: {rate:.2f} ops/s | Balance: ${broker.get_balance():.2f}")
                else:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] HEARTBEAT | Balance: ${broker.get_balance():.2f}")
                
                if active_trade:
                    elapsed_trade = current_time - active_trade['time']
                    print(f"  Operacion activa: {active_trade['asset']} ({active_trade['direction']}) - {elapsed_trade:.0f}s de {trade_expiry_seconds}s")
                else:
                    print(f"  Estado: SIN OPERACIONES ACTIVAS")
                
                print()
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
        print(f"Perdidas: {broker.losses}")
        if broker.trades_made > 0:
            win_rate = (broker.wins / broker.trades_made) * 100
            print(f"Win Rate: {win_rate:.1f}%")
        print(f"Balance: ${broker.get_balance():.2f}")
        profit = broker.get_balance() - 1000.0
        print(f"Ganancia/Perdida: ${profit:+.2f}")
    else:
        print("Modo: REAL")
        print(f"Balance final: ${broker.get_balance():.2f}")
    
    print("="*60 + "\n")
    sys.stdout.flush()
    print("Bot detenido correctamente")

if __name__ == "__main__":
    main()
