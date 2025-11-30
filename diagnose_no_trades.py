"""
Diagnóstico profundo: ¿Por qué el bot no opera?
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from data.market_data import MarketDataHandler
from config import Config
import time

print("=" * 60)
print("DIAGNÓSTICO: ¿POR QUÉ EL BOT NO OPERA?")
print("=" * 60)

# 1. Verificar conexión al broker
print("\n1️⃣ VERIFICANDO CONEXIÓN AL BROKER...")
try:
    market_data = MarketDataHandler(Config.BROKER_NAME, Config.ACCOUNT_TYPE)
    connected = market_data.connect(Config.EX_EMAIL, Config.EX_PASSWORD)
    
    if connected:
        print(f"✅ Conectado a {Config.BROKER_NAME}")
        print(f"   Tipo de cuenta: {Config.ACCOUNT_TYPE}")
        
        # Verificar balance
        balance = market_data.get_balance()
        print(f"   Balance: ${balance}")
    else:
        print(f"❌ NO se pudo conectar a {Config.BROKER_NAME}")
        print("   SOLUCIÓN: Verifica credenciales en .env")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ Error de conexión: {e}")
    sys.exit(1)

# 2. Verificar datos de mercado
print("\n2️⃣ VERIFICANDO DATOS DE MERCADO...")
test_assets = ["EURUSD", "GBPUSD", "USDJPY", "EURJPY", "AUDUSD"]

available_assets = []
for asset in test_assets:
    try:
        df = market_data.get_candles(asset, 60, 10)
        if not df.empty:
            print(f"✅ {asset}: {len(df)} velas disponibles")
            available_assets.append(asset)
        else:
            print(f"⚠️  {asset}: Sin datos")
    except Exception as e:
        print(f"❌ {asset}: Error - {e}")

if not available_assets:
    print("\n❌ PROBLEMA CRÍTICO: No hay datos de ningún activo")
    print("   El broker puede estar offline o bloqueado")
    sys.exit(1)

print(f"\n✅ Activos disponibles: {len(available_assets)}")

# 3. Simular análisis de una oportunidad
print("\n3️⃣ SIMULANDO ANÁLISIS DE OPORTUNIDAD...")
test_asset = available_assets[0]
print(f"Probando con {test_asset}...")

df = market_data.get_candles(test_asset, 60, 200)
print(f"   Velas obtenidas: {len(df)}")

if len(df) < 50:
    print(f"   ❌ Insuficientes velas (mínimo 50)")
else:
    print(f"   ✅ Suficientes velas para análisis")

# 4. Verificar indicadores
print("\n4️⃣ VERIFICANDO CÁLCULO DE INDICADORES...")
try:
    from features.feature_engineering import FeatureEngineer
    fe = FeatureEngineer()
    df_with_indicators = fe.prepare_for_rl(df)
    
    required_cols = ['rsi', 'macd', 'bb_low', 'bb_high', 'atr']
    missing = [col for col in required_cols if col not in df_with_indicators.columns]
    
    if missing:
        print(f"   ❌ Indicadores faltantes: {missing}")
    else:
        print(f"   ✅ Todos los indicadores calculados")
        
        # Mostrar últimos valores
        last = df_with_indicators.iloc[-1]
        print(f"\n   📊 Valores actuales de {test_asset}:")
        print(f"      RSI: {last['rsi']:.2f}")
        print(f"      MACD: {last['macd']:.5f}")
        print(f"      Precio: {last['close']:.5f}")
        print(f"      ATR: {last['atr']:.5f}")
        
except Exception as e:
    print(f"   ❌ Error calculando indicadores: {e}")

# 5. Verificar validador de decisiones
print("\n5️⃣ VERIFICANDO VALIDADOR DE DECISIONES...")
try:
    from core.decision_validator import DecisionValidator
    validator = DecisionValidator()
    
    # Simular una decisión
    test_action = 1  # CALL
    indicators_analysis = {
        'rsi': last['rsi'],
        'macd': last['macd'],
        'signal': 'CALL'
    }
    
    validation = validator.validate_decision(
        df=df_with_indicators,
        action=test_action,
        indicators_analysis=indicators_analysis,
        rl_prediction=0.7
    )
    
    print(f"   Decisión válida: {validation['valid']}")
    print(f"   Confianza: {validation['confidence']*100:.1f}%")
    print(f"   Recomendación: {validation['recommendation']}")
    
    if not validation['valid']:
        print(f"\n   ❌ RAZONES POR LAS QUE NO OPERA:")
        for warning in validation['warnings']:
            print(f"      • {warning}")
    else:
        print(f"\n   ✅ Esta operación SÍ pasaría la validación")
        
except Exception as e:
    print(f"   ❌ Error en validador: {e}")
    import traceback
    traceback.print_exc()

# 6. Verificar scanner de oportunidades
print("\n6️⃣ VERIFICANDO SCANNER DE OPORTUNIDADES...")
try:
    from strategies.opportunity_scanner import OpportunityScanner
    scanner = OpportunityScanner()
    
    opportunities = scanner.scan_market(market_data, available_assets)
    
    if opportunities:
        print(f"   ✅ {len(opportunities)} oportunidades encontradas:")
        for opp in opportunities[:3]:  # Mostrar top 3
            print(f"      • {opp['asset']}: {opp['action']} (score: {opp['score']:.2f})")
    else:
        print(f"   ⚠️  No se encontraron oportunidades")
        print(f"      Esto puede ser normal si el mercado está lateral")
        
except Exception as e:
    print(f"   ❌ Error en scanner: {e}")

print("\n" + "=" * 60)
print("RESUMEN DEL DIAGNÓSTICO")
print("=" * 60)

print("""
Si el bot NO opera después de 2 días, las causas pueden ser:

1. ❌ El mercado está muy lateral (sin tendencias claras)
2. ❌ Las restricciones son muy estrictas (aunque ya las relajamos)
3. ❌ El scanner no detecta oportunidades con suficiente score
4. ❌ El validador rechaza todas las operaciones

SOLUCIONES:
- Reducir aún más la confianza mínima (actualmente 60%)
- Desactivar temporalmente el validador avanzado
- Forzar operaciones en horarios de alta volatilidad
- Verificar que el broker esté enviando datos en tiempo real
""")

print("=" * 60)
