"""
Script de diagnóstico para verificar configuración del bot
"""
import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("DIAGNÓSTICO DE CONFIGURACIÓN DEL BOT")
print("=" * 60)

# Verificar variables de entorno
print("\n📋 VARIABLES DE ENTORNO:")
print(f"EXNOVA_EMAIL: {'✅ Configurado' if os.getenv('EXNOVA_EMAIL') else '❌ NO configurado'}")
print(f"EXNOVA_PASSWORD: {'✅ Configurado' if os.getenv('EXNOVA_PASSWORD') else '❌ NO configurado'}")
print(f"ACCOUNT_TYPE: {os.getenv('ACCOUNT_TYPE', 'PRACTICE (por defecto)')}")
print(f"BROKER_NAME: {os.getenv('BROKER_NAME', 'exnova (por defecto)')}")
print(f"GROQ_API_KEY: {'✅ Configurado' if os.getenv('GROQ_API_KEY') else '❌ NO configurado'}")

# Verificar config.py
from config import Config
print("\n⚙️ CONFIGURACIÓN ACTIVA (config.py):")
print(f"Broker: {Config.BROKER_NAME}")
print(f"Tipo de cuenta: {Config.ACCOUNT_TYPE}")
print(f"Capital por operación: ${Config.CAPITAL_PER_TRADE}")
print(f"Timeframe: {Config.TIMEFRAME}s")
print(f"LLM activado: {Config.USE_LLM}")

# Verificar restricciones del trader
print("\n🔒 RESTRICCIONES DEL TRADER:")
try:
    from core.trader import LiveTrader
    from data.market_data import MarketDataHandler
    
    # Crear instancia temporal para ver configuración
    market_data = MarketDataHandler(Config.BROKER_NAME)
    trader = LiveTrader(market_data)
    
    print(f"Tiempo mínimo entre operaciones: {trader.min_time_between_trades}s")
    print(f"Cooldown después de pérdida: {trader.cooldown_after_loss}s")
    
except Exception as e:
    print(f"Error al verificar trader: {e}")

# Verificar decision_validator
print("\n✅ VALIDADOR DE DECISIONES:")
try:
    from core.decision_validator import DecisionValidator
    validator = DecisionValidator()
    
    print(f"Confianza mínima requerida: {validator.min_confidence * 100}%")
    print(f"Velas mínimas requeridas: {validator.min_candles_required}")
    print(f"Evitar RSI neutral: {validator.learned_rules['avoid_neutral_rsi']}")
    print(f"Evitar BB neutral: {validator.learned_rules['avoid_neutral_bb']}")
    print(f"Evitar contra-tendencia: {validator.learned_rules['avoid_counter_trend']}")
    
except Exception as e:
    print(f"Error al verificar validator: {e}")

print("\n" + "=" * 60)
print("RECOMENDACIONES:")
print("=" * 60)

if os.getenv('ACCOUNT_TYPE', 'PRACTICE') == 'PRACTICE':
    print("⚠️  CUENTA EN MODO PRACTICE")
    print("   Para operar en REAL, edita .env y cambia:")
    print("   ACCOUNT_TYPE=REAL")
else:
    print("✅ CUENTA EN MODO REAL")

print("\n💡 Si el bot no encuentra operaciones:")
print("   1. Verifica que el broker esté conectado")
print("   2. Revisa que haya datos de mercado disponibles")
print("   3. Las restricciones pueden ser muy estrictas")
print("=" * 60)
