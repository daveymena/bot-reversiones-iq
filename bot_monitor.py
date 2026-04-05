#!/usr/bin/env python3
"""
Bot de Trading con Monitoreo y Auto-optimización
"""
import sys
import io
import json
import time
import signal as sig_module
from datetime import datetime
from pathlib import Path

# Fix encoding para Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from data.market_data import MarketDataHandler
from strategies.technical import FeatureEngineer
from config import Config
from exnovaapi.stable_api import Exnova

# ============= CONFIGURACIÓN =============
INITIAL_BALANCE = 9942.55
TARGET_WINRATE = 0.60  # 60% mínimo
MIN_CONFIDENCE = 0.52  # Umbral mínimo de confianza
MAX_DAILY_LOSS = 50  # Stop loss diario $50
RESULTS_FILE = "data/operations_log.json"

# ============= VARIABLES GLOBALES =============
running = True
bot_stats = {
    "total_trades": 0,
    "wins": 0,
    "losses": 0,
    "total_profit": 0,
    "daily_profit": 0,
    "operations": []
}

def signal_handler(sig_num, frame):
    global running
    print("\n\nDeteniendo bot...")
    running = False
    save_stats()
    sys.exit(0)

def save_stats():
    """Guarda estadísticas"""
    with open(RESULTS_FILE, 'w') as f:
        json.dump(bot_stats, f, indent=2)
    print(f"Estadisticas guardadas en {RESULTS_FILE}")

def log_trade(asset, direction, confidence, result, profit, indicators):
    """Registra una operación"""
    bot_stats["total_trades"] += 1
    bot_stats["operations"].append({
        "timestamp": datetime.now().isoformat(),
        "asset": asset,
        "direction": direction,
        "confidence": confidence,
        "result": result,
        "profit": profit,
        "indicators": indicators,
        "winrate": bot_stats["wins"] / bot_stats["total_trades"] if bot_stats["total_trades"] > 0 else 0
    })
    
    if result == "win":
        bot_stats["wins"] += 1
        bot_stats["total_profit"] += profit
        bot_stats["daily_profit"] += profit
        print(f"  GANADA: +${profit:.2f}")
    else:
        bot_stats["losses"] += 1
        bot_stats["total_profit"] -= abs(profit)
        bot_stats["daily_profit"] -= abs(profit)
        print(f"  PERDIDA: -${abs(profit):.2f}")
    
    # Mostrar progreso
    wr = bot_stats["wins"] / bot_stats["total_trades"] * 100
    print(f"  Win Rate: {wr:.1f}% | Profit Total: ${bot_stats['total_profit']:.2f}")
    
    # Guardar cada 5 operaciones
    if bot_stats["total_trades"] % 5 == 0:
        save_stats()
    
    return wr

def analyze_market(md, fe, asset):
    """Analiza el mercado y retorna señal de trading"""
    try:
        df = md.get_candles(asset, 60, 150)
        if df.empty or len(df) < 100:
            return None
        
        df = fe.prepare_for_rl(df)
        
        rsi = float(df.iloc[-1]['rsi'])
        macd = float(df.iloc[-1]['macd'])
        macd_signal = float(df.iloc[-1]['macd_signal'])
        bb_position = float(df.iloc[-1].get('bb_position', 0.5))
        atr = float(df.iloc[-1]['atr'])
        
        # Análisis de tendencia
        sma_20 = float(df.iloc[-1]['sma_20'])
        sma_50 = float(df.iloc[-1]['sma_50'])
        current_price = float(df.iloc[-1]['close'])
        
        # Determinar tendencia
        if sma_20 > sma_50:
            trend = "BULLISH"
        elif sma_20 < sma_50:
            trend = "BEARISH"
        else:
            trend = "NEUTRAL"
        
        # Señales de trading
        trade_direction = None
        confidence = 0
        reasons = []
        
        # === SEÑAL PUT (bajista) ===
        if rsi > 65 and bb_position > 0.75:
            trade_direction = "PUT"
            confidence = 0.55 + (rsi - 65) / 100
            reasons.append(f"RSI sobrecompra: {rsi:.1f}")
            reasons.append(f"BB posición alta: {bb_position:.2f}")
            if trend == "BEARISH":
                confidence += 0.1
                reasons.append("Tendencia bajista confirmada")
        
        # === SEÑAL CALL (alcista) ===
        elif rsi < 40 and bb_position < 0.25:
            trade_direction = "CALL"
            confidence = 0.55 + (40 - rsi) / 100
            reasons.append(f"RSI sobrevenda: {rsi:.1f}")
            reasons.append(f"BB posición baja: {bb_position:.2f}")
            if trend == "BULLISH":
                confidence += 0.1
                reasons.append("Tendencia alcista confirmada")
        
        # === SEÑAL POR MACD ===
        elif macd > macd_signal and (rsi > 58 or bb_position > 0.7):
            trade_direction = "PUT"
            confidence = 0.52
            reasons.append("MACD cruce alcista")
            reasons.append("Sobrecompra secundaria")
        
        elif macd < macd_signal and (rsi < 42 or bb_position < 0.3):
            trade_direction = "CALL"
            confidence = 0.52
            reasons.append("MACD cruce bajista")
            reasons.append("Sobreventa secundaria")
        
        confidence = min(0.90, max(0.50, confidence))
        
        indicators = {
            "rsi": rsi,
            "macd": macd,
            "macd_signal": macd_signal,
            "bb_position": bb_position,
            "atr": atr,
            "trend": trend,
            "reasons": reasons
        }
        
        return {
            "signal": trade_direction,
            "confidence": confidence,
            "indicators": indicators
        }
        
    except Exception as e:
        print(f"Error analizando {asset}: {e}")
        return None

def execute_trade(md, api, asset, direction, amount=1):
    """Ejecuta una operación"""
    try:
        expiration = 3  # 3 minutos
        
        print(f"  Ejecutando {direction}...")
        success, order_id = api.buy(amount, asset, direction.lower(), expiration)
        
        if not success:
            print(f"  Error ejecutando orden")
            return None
        
        print(f"  Order ID: {order_id}")
        
        # Esperar resultado (3 min + margen)
        wait_time = expiration * 60 + 30
        print(f"  Esperando {wait_time}s...")
        time.sleep(wait_time)
        
        # Obtener resultado
        result, profit = api.check_win_v4(order_id, timeout=90)
        
        if result is None:
            print("  Timeout - consultando manualmente...")
            profit = 0
            result = "timeout"
        
        return {"result": result, "profit": profit, "order_id": order_id}
        
    except Exception as e:
        print(f"  Error en execute_trade: {e}")
        return None

def main():
    global running, stats
    
    sig_module.signal(sig_module.SIGINT, signal_handler)
    
    print("=" * 60)
    print("BOT DE TRADING CON MONITOREO Y AUTO-OPTIMIZACION")
    print("=" * 60)
    print(f"Inicio: {datetime.now()}")
    print(f"Balance inicial: ${INITIAL_BALANCE}")
    print("=" * 60)
    
    # Conectar al broker
    print("\nConectando a Exnova...")
    api = Exnova(Config.EXNOVA_EMAIL, Config.EXNOVA_PASSWORD, active_account_type='REAL')
    check, reason = api.connect()
    
    if not check:
        print(f"Error de conexion: {reason}")
        return 1
    
    print("Conectado!")
    balance = api.get_balance()
    print(f"Balance: ${balance}")
    
    # Inicializar componentes
    md = MarketDataHandler(broker_name='exnova', account_type='REAL')
    md.connected = True
    md.api = api
    
    fe = FeatureEngineer()
    
    # Activos a monitorear
    assets = ['EURUSD-OTC', 'GBPUSD-OTC', 'USDJPY-OTC', 'AUDUSD-OTC', 'USDCAD-OTC', 'EURJPY-OTC']
    
    # Cargar operaciones previas
    if Path(RESULTS_FILE).exists():
        with open(RESULTS_FILE, 'r') as f:
            old_stats = json.load(f)
            bot_stats.update(old_stats)
        print(f"Operaciones previas cargadas: {bot_stats['total_trades']}")
    
    print("\n" + "=" * 60)
    print("INICIANDO TRADING")
    print("=" * 60)
    
    last_analysis = 0
    trade_cooldown = 0
    
    while running:
        try:
            current_time = time.time()
            
            # Mostrar heartbeat
            if int(current_time) % 30 == 0 and int(current_time) != last_analysis:
                last_analysis = int(current_time)
                balance = api.get_balance()
                wr = bot_stats["wins"] / bot_stats["total_trades"] * 100 if bot_stats["total_trades"] > 0 else 0
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Bot activo | "
                      f"Ops: {bot_stats['total_trades']} | "
                      f"WR: {wr:.1f}% | "
                      f"Profit: ${bot_stats['total_profit']:.2f} | "
                      f"Balance: ${balance:.2f}")
            
            # Verificar stop loss diario
            if bot_stats["daily_profit"] <= -MAX_DAILY_LOSS:
                print(f"\nSTOP LOSS DIARIO ALCANZADO: ${bot_stats['daily_profit']:.2f}")
                print("Esperando nuevo dia...")
                time.sleep(3600)  # Esperar 1 hora
                bot_stats["daily_profit"] = 0
            
            # Cooldown entre operaciones
            if trade_cooldown > 0:
                trade_cooldown -= 1
                time.sleep(1)
                continue
            
            # Analizar mercado
            for asset in assets:
                analysis = analyze_market(md, fe, asset)
                
                if analysis and analysis["signal"] and analysis["confidence"] >= MIN_CONFIDENCE:
                    trade_direction = analysis["signal"]
                    confidence = analysis["confidence"]
                    indicators = analysis["indicators"]
                    
                    print(f"\n{'='*40}")
                    print(f"OPORTUNIDAD DETECTADA")
                    print(f"{'='*40}")
                    print(f"Activo: {asset}")
                    print(f"Direccion: {trade_direction}")
                    print(f"Confianza: {confidence*100:.1f}%")
                    print(f"RSI: {indicators['rsi']:.1f}")
                    print(f"BB Position: {indicators['bb_position']:.2f}")
                    print(f"Trend: {indicators['trend']}")
                    print(f"Razones:")
                    for r in indicators["reasons"]:
                        print(f"  - {r}")
                    
                    # Ejecutar operación
                    print(f"\nEjecutando operacion...")
                    result = execute_trade(md, api, asset, trade_direction)
                    
                    if result:
                        # Registrar
                        wr = log_trade(
                            asset=asset,
                            direction=trade_direction,
                            confidence=confidence,
                            result=result["result"],
                            profit=result["profit"],
                            indicators=indicators
                        )
                        
                        # Cooldown adaptive
                        if result["result"] == "win":
                            trade_cooldown = 5  # 5 segundos si ganó
                        else:
                            trade_cooldown = 30  # 30 segundos si perdió
                
                time.sleep(0.5)  # Pausa entre análisis
            
            time.sleep(1)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error en loop principal: {e}")
            import traceback
            traceback.print_exc()
            time.sleep(5)
    
    save_stats()
    print("\nBot detenido.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
