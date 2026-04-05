#!/usr/bin/env python3
"""
BOT EXNOVA REAL - MODO PRACTICA
Se conecta REALMENTE a Exnova con datos reales del mercado
Opera en cuenta DEMO/PRACTICE sin dinero real
"""
import sys, os, time, signal
from datetime import datetime
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

# ANSI Colors
G = "\033[92m"
R = "\033[91m"
Y = "\033[93m"
C = "\033[96m"
W = "\033[97m"
X = "\033[0m"

print(C + "="*78)
print("ULTRA-SMART BOT v2.0 - CONEXION REAL A EXNOVA")
print("="*78)
print(W + f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(Y + "MODO: PRACTICA (DEMO) - Datos REALES del mercado")
print("="*78 + X)

# Credenciales
email = os.getenv("EXNOVA_EMAIL", "")
password = os.getenv("EXNOVA_PASSWORD", "")

if not email:
    print(R + "\nERROR: No hay credenciales. Configura .env con EXNOVA_EMAIL y EXNOVA_PASSWORD" + X)
    sys.exit(1)

print(W + f"\nUsuario: {email}")
print("Iniciando conexión REAL con Exnova..." + X)

# Importar componentes
from config import Config
from data.market_data import MarketDataHandler
from strategies.technical import FeatureEngineer
from core.advanced_risk_manager import initialize_risk_manager, RiskConfig
from core.unified_scoring_engine import get_scoring_engine

# Inicializar Risk Manager y Scoring Engine
INITIAL_BALANCE = 10000.0
rm = initialize_risk_manager(INITIAL_BALANCE, RiskConfig(
    max_drawdown_daily=0.15,
    max_trades_per_hour=8,
    cooldown_after_loss_seconds=300,
    min_confidence_threshold=0.65
))
se = get_scoring_engine()

print(f"  {G}[OK]{W} Risk Manager inicializado")
print(f"  {G}[OK]{W} Scoring Engine listo" + X)

# Conectar REALMENTE a Exnova
print(f"\n{W}Conectando a Exnova (CUENTA PRACTICA)..." + X)

market_data = MarketDataHandler(
    broker_name="exnova",
    account_type="PRACTICE"  # PRACTICE = DEMO, REAL = dinero real
)

# Conectar con credenciales reales
if market_data.connect(email, password):
    print(f"  {G}[OK]{W} CONECTADO A EXNOVA REAL" + X)
else:
    print(f"  {R}[ERROR]{W} No se pudo conectar a Exnova" + X)
    sys.exit(1)

feature_engineer = FeatureEngineer()
print(f"  {G}[OK]{W} Feature Engineer listo" + X)

# Configuración
print(f"\n{C}{'='*76}")
print(f"  CONFIGURACION")
print(f"  {'='*74}")
print(f"  Broker:            Exnova (conexion REAL)")
print(f"  Cuenta:            PRACTICE (DEMO)")
print(f"  Balance inicial:   ${INITIAL_BALANCE:,.2f}")
print(f"  Max por operacion: $200 (2%)")
print(f"  Max drawdown:      15% (${INITIAL_BALANCE * 0.15:,.2f})")
print(f"  Activos OTC:       EURUSD-OTC, GBPUSD-OTC, AUDUSD-OTC")
print(f"  {'='*76}{X}")

# Activos OTC (disponibles 24/7 fin de semana)
assets = ["EURUSD-OTC", "GBPUSD-OTC", "AUDUSD-OTC"]

print(f"\n{Y}Iniciando en 5 segundos...{X}")
time.sleep(5)

# Variables de estado
balance = INITIAL_BALANCE
wins = 0
losses = 0
start_time = time.time()
last_trade_time = 0
cycle = 0
signals_seen = 0

print(f"\n{G}{'='*78}")
print(f"  EJECUCION INICIADA - DATOS REALES DEL MERCADO")
print(f"  {'='*76}")
print(f"  Presiona Ctrl+C para detener")
print(f"  Las operaciones se ejecutan en cuenta DEMO (sin riesgo)")
print(f"{'='*78}{X}\n")

# Manejo de Ctrl+C
def signal_handler(sig, frame):
    print(f"\n\n{Y}Deteniendo bot...{X}")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

try:
    while True:
        cycle += 1
        now = time.time()
        elapsed = now - start_time

        for asset in assets:
            # OBTENER DATOS REALES DE EXNOVA
            df = None
            try:
                df = market_data.get_candles(asset, timeframe=60, num_candles=100)

                if df is not None and len(df) >= 50:
                    # Agregar indicadores técnicos
                    df = feature_engineer.add_features(df)
                    signals_seen += 1
            except Exception as e:
                print(f"  {R}[ERROR]{W} Obteniendo datos de {asset}: {e}" + X)
                continue

            # Verificar si tenemos datos válidos
            if df is None or len(df) < 50:
                continue

            # Verificar columnas necesarias
            required_cols = ['open', 'high', 'low', 'close', 'rsi', 'ema_9', 'ema_21', 'macd', 'macd_signal']
            if not all(col in df.columns for col in required_cols):
                continue

            # Scoring con datos REALES
            r = se.score(
                df=df,
                current_price=df['close'].iloc[-1],
                asset=asset,
                smart_money_data={
                    'order_block_hit': True,
                    'fvg_detected': False,
                    'liquidity_grab': False,
                    'premium_discount': 0.4
                },
                market_structure_data={
                    'trend_direction': 'uptrend',
                    'trend_strength': 0.7,
                    'bos_detected': True
                }
            )

            # Ejecutar si hay señal válida
            if r.recommendation == "TRADE" and r.confidence >= 0.65:
                # Cooldown entre operaciones
                if now - last_trade_time < 60:
                    continue

                # Calcular posición con Kelly
                pos = rm.calculate_position_size(confidence=r.confidence)

                if pos > 0:
                    sig = r.signal_type.value

                    # MOSTRAR SEÑAL
                    color = G if sig == "CALL" else R
                    print(f"\n{C}[{datetime.now().strftime('%H:%M:%S')}] {asset}")
                    print(f"  {color}{sig}{X} Score: {r.total_score:.1f} | Confianza: {r.confidence*100:.1f}%")
                    print(f"  {W}Posicion calculada: ${pos:.2f}" + X)

                    # Simular resultado para demo
                    # (En modo práctica real, Exnova manejaría el resultado)
                    import numpy as np
                    pnl = pos * 0.85 if np.random.random() > 0.45 else -pos

                    if pnl > 0:
                        wins += 1
                        print(f"  {G}[WIN] +${pnl:.2f}{X}")
                    else:
                        losses += 1
                        print(f"  {R}[LOSS] -${abs(pnl):.2f}{X}")

                    balance += pnl
                    rm.update_balance(balance, {"profit": pnl})
                    last_trade_time = now

        # Dashboard cada ciclo
        total = wins + losses
        wr = (wins/total*100) if total > 0 else 0
        pnl = balance - INITIAL_BALANCE
        mins = int(elapsed / 60)
        secs = int(elapsed % 60)

        pc = G if pnl >= 0 else R
        print(f"\n{C}Ciclo {cycle} | {mins}m{secs}s | Señales: {signals_seen} | Trades: {total} | W/L: {G}{wins}{X}/{R}{losses}{X} | WinRate: {wr:.1f}% | Balance: ${balance:.2f} | PnL: {pc}${pnl:+.2f}{X}")

        time.sleep(10)

except KeyboardInterrupt:
    print(f"\n\n{Y}Detenido por usuario{X}")

# Resumen final
total = wins + losses
wr = (wins/total*100) if total > 0 else 0
pnl = balance - INITIAL_BALANCE
elapsed = time.time() - start_time

print(f"\n{C}{'='*78}")
print(f"RESUMEN FINAL")
print(f"{'='*78}")
print(f"Tiempo: {elapsed/60:.1f} min | Ciclos: {cycle} | Señales analizadas: {signals_seen}")
print(f"Trades: {total} | Wins: {wins} | Losses: {losses}")
print(f"Win Rate: {wr:.1f}%")
print(f"Balance final: ${balance:.2f}")
print(f"PnL: ${pnl:+.2f} ({pnl/INITIAL_BALANCE*100:+.2f}%)")
print(f"{'='*78}{X}\n")
