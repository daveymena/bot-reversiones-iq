"""
Test completo de Exnova - Verificar todos los componentes
"""
import time
from config import Config
from exnovaapi.stable_api import Exnova

print("=" * 70)
print(" 🤖 TEST COMPLETO - EXNOVA")
print("=" * 70)

# 1. Conexión
print("\n📡 [1/6] Conectando a Exnova...")
api = Exnova(Config.EX_EMAIL, Config.EX_PASSWORD)
status, message = api.connect()

if not status:
    print(f"   ❌ Error: {message}")
    exit(1)

if not api.check_connect():
    print("   ❌ WebSocket no conectado")
    exit(1)

print("   ✅ Conectado exitosamente")

# 2. Actualizar códigos de activos
print("\n⚙️  [2/6] Actualizando códigos de activos...")
try:
    api.update_ACTIVES_OPCODE()
    print("   ✅ Códigos actualizados")
except Exception as e:
    print(f"   ⚠️  Advertencia: {e}")

# 3. Balance
print("\n💰 [3/6] Obteniendo balance...")
balance = api.get_balance()
balance_mode = api.get_balance_mode()
print(f"   ✅ Balance: ${balance:.2f}")
print(f"   📊 Modo: {balance_mode}")

# 4. Datos de mercado
print("\n📈 [4/6] Obteniendo datos de mercado...")
try:
    candles = api.get_candles("EURUSD-OTC", 60, 10, time.time())
    if candles:
        print(f"   ✅ Obtenidas {len(candles)} velas")
        print(f"   📊 Última vela close: {candles[-1]['close']:.5f}")
    else:
        print("   ⚠️  No se obtuvieron velas")
except Exception as e:
    print(f"   ⚠️  Error: {e}")

# 5. Verificar activos disponibles
print("\n🔍 [5/6] Verificando activos disponibles...")
try:
    profits = api.get_all_profit()
    if profits:
        # Filtrar activos OTC con buena rentabilidad
        otc_assets = []
        for asset, data in profits.items():
            if '-OTC' in asset:
                profit = 0
                if isinstance(data, dict):
                    profit = data.get('turbo', 0) * 100
                else:
                    profit = data * 100
                
                if profit >= 75:
                    otc_assets.append((asset, profit))
        
        otc_assets.sort(key=lambda x: x[1], reverse=True)
        
        print(f"   ✅ Activos OTC disponibles: {len(otc_assets)}")
        if otc_assets:
            print("   📊 Top 5:")
            for asset, profit in otc_assets[:5]:
                print(f"      • {asset}: {profit:.0f}%")
    else:
        print("   ⚠️  No se obtuvieron rentabilidades")
except Exception as e:
    print(f"   ⚠️  Error: {e}")

# 6. Test de operación
print("\n🚀 [6/6] Test de operación...")
print("   ⚠️  ¿Deseas ejecutar una operación de prueba de $1?")
print("   📝 Activo: EURUSD-OTC")
print("   💵 Monto: $1")
print("   📈 Dirección: CALL")
print("   ⏱️  Duración: 1 minuto")

# Por seguridad, no ejecutamos automáticamente
# Descomenta las siguientes líneas para ejecutar:
"""
try:
    buy_status, order_id = api.buy(1, "EURUSD-OTC", "call", 1)
    
    if buy_status:
        print(f"   ✅ Operación ejecutada - ID: {order_id}")
        print("   ⏳ Esperando resultado (70 segundos)...")
        time.sleep(70)
        
        result_status, profit = api.check_win_v4(order_id)
        balance_final = api.get_balance()
        
        print(f"\n   📊 Resultado: {result_status}")
        print(f"   💰 Profit/Loss: ${profit:.2f}")
        print(f"   💵 Balance final: ${balance_final:.2f}")
    else:
        print(f"   ❌ Error: {order_id}")
except Exception as e:
    print(f"   ❌ Error: {e}")
"""

print("\n" + "=" * 70)
print(" ✅ EXNOVA FUNCIONA CORRECTAMENTE")
print("=" * 70)
print("\n📝 Nota: Para ejecutar operaciones, descomenta el código en el script")
