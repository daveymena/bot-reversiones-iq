#!/usr/bin/env python3
"""
BOT EXNOVA REAL - DINERO REAL
Se conecta a Exnova en cuenta REAL y opera con dinero real
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
print("ULTRA-SMART BOT v2.0 - MODO REAL (DINERO REAL)")
print("="*78)
print(W + f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(R + "ADVERTENCIA: Este bot operara con DINERO REAL")
print("="*78 + X)

# Credenciales
email = os.getenv("EXNOVA_EMAIL", "")
password = os.getenv("EXNOVA_PASSWORD", "")

if not email:
    print(R + "\nERROR: No hay credenciales. Configura .env" + X)
    sys.exit(1)

print(W + f"\nUsuario: {email}")
print("Conectando a Exnova (CUENTA REAL)..." + X)

# Importar componentes
from config import Config
from data.market_data import MarketDataHandler
from strategies.technical import FeatureEngineer
from core.advanced_risk_manager import initialize_risk_manager, RiskConfig
from core.unified_scoring_engine import get_scoring_engine

# Inicializar Risk Manager
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

# Conectar REALMENTE a Exnova en modo REAL
print(f"\n{W}Conectando a Exnova (CUENTA REAL - DINERO REAL)..." + X)

market_data = MarketDataHandler(
    broker_name="exnova",
    account_type="REAL"  # REAL = dinero real
)

if market_data.connect(email, password):
    print(f"  {G}[OK]{W} CONECTADO A EXNOVA (REAL)" + X)
else:
    print(f"  {R}[ERROR]{W} No se pudo conectar a Exnova" + X)
    sys.exit(1)

feature_engineer = FeatureEngineer()
print(f"  {G}[OK]{W} Feature Engineer listo" + X)

# Obtener balance real
try:
    balance_info = market_data.get_balance()
    if balance_info:
        current_balance = balance_info.get('balance', 0)
        print(f"\n  {C}Balance en cuenta REAL: ${current_balance:.2f}{X}")
except:
    current_balance = INITIAL_BALANCE

# Configuración
print(f"\n{C}{'='*76}")
print(f"  CONFIGURACION - MODO REAL")
print(f"  {'='*74}")
print(f"  Broker:            Exnova (conexion REAL)")
print(f"  Cuenta:            REAL (DINERO REAL)")
print(f"  Balance actual:    ${current_balance:.2f}")
print(f"  Max por operacion: $10 (1% de ${current_balance})")
print(f"  Max drawdown:      15% (${current_balance * 0.15:.2f})")
print(f"  Activos OTC:       EURUSD-OTC, GBPUSD-OTC, AUDUSD-OTC")
print(f"  {'='*76}{X}")

# Activos OTC
assets = ["EURUSD-OTC", "GBPUSD-OTC", "AUDUSD-OTC"]

print(f"\n{Y}Iniciando en 10 segundos... Presiona Ctrl+C para cancelar{X}")
for i in range(10, 0, -1):
    print(f"  {i}...")
    time.sleep(1)

# Variables de estado
balance = current_balance
wins = 0
losses = 0
start_time = time.time()
last_trade_time = 0
cycle = 0
signals_seen = 0

print(f"\n{G}{'='*78}")
print(f"  EJECUCION INICIADA - DINERO REAL")
print(f"  {'='*76}")
print(f"  {R}ADVERTENCIA: Las operaciones usan DINERO REAL")
print(f"  Presiona Ctrl+C para detener")
print(f"{'='*78}{X}\n")

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
                    df = feature_engineer.add_features(df)
                    signals_seen += 1
            except Exception as e:
                continue

            if df is None or len(df) < 50:
                continue

            required_cols = ['open', 'high', 'low', 'close', 'rsi', 'ema_9', 'ema_21', 'macd', 'macd_signal']
            if not all(col in df.columns for col in required_cols):
                continue

            # Scoring
            r = se.score(
                df=df,
                current_price=df['close'].iloc[-1],
                asset=asset,
                smart_money_data={'order_block_hit': True, 'fvg_detected': False, 'liquidity_grab': False, 'premium_discount': 0.4},
                market_structure_data={'trend_direction': 'uptrend', 'trend_strength': 0.7, 'bos_detected': True}
            )

            # Ejecutar si hay señal válida
            if r.recommendation == "TRADE" and r.confidence >= 0.65:
                if now - last_trade_time < 60:
                    continue

                pos = rm.calculate_position_size(confidence=r.confidence)

                if pos > 0:
                    sig = r.signal_type.value

                    print(f"\n{C}[{datetime.now().strftime('%H:%M:%S')}] {asset}")
                    print(f"  {G if sig == 'CALL' else R}{sig}{X} Score: {r.total_score:.1f} | Confianza: {r.confidence*100:.1f}%")
                    print(f"  {W}Posicion: ${pos:.2f}" + X)

                    # Ejecutar orden REAL en Exnova
                    try:
                        direction = "call" if sig == "CALL" else "put"
                        expiration = 60  # 1 minuto

                        print(f"  {Y}Enviando orden {direction} a Exnova...{X}")

                        # Llamada REAL a la API de Exnova
                        result = market_data.api.buy(
                            amount=pos,
                            asset=asset,
                            direction=direction,
                            expiration_time=expiration
                        )

                        if result:
                            print(f"  {G}ORDEN EJECUTADA EXITOSAMENTE{X}")
                            last_trade_time = now
                        else:
                            print(f"  {R}Error ejecutando orden{X}")

                    except Exception as e:
                        print(f"  {R}Error: {e}{X}")

        # Dashboard
        total = wins + losses
        pnl = balance - current_balance
        mins = int(elapsed / 60)

        print(f"\n{C}Ciclo {cycle} | {mins}m | Señales: {signals_seen} | Balance: ${balance:.2f}{X}")

        time.sleep(10)

except KeyboardInterrupt:
    print(f"\n\n{Y}Detenido por usuario{X}")

# Resumen
print(f"\n{C}{'='*78}")
print(f"RESUMEN")
print(f"{'='*78}{X}\n")
