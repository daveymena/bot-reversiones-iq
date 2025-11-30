"""
Test para verificar qué activos están disponibles
Prueba tanto OTC como normales
"""
import time
from config import Config
from data.market_data import MarketDataHandler

def test_activos():
    print("=" * 70)
    print("🔍 TEST DE ACTIVOS DISPONIBLES")
    print("=" * 70)
    
    # Conectar
    print("\n[1/4] Conectando a Exnova...")
    market_data = MarketDataHandler(broker_name="exnova", account_type="PRACTICE")
    
    if not market_data.connect(Config.EX_EMAIL, Config.EX_PASSWORD):
        print("❌ Error de conexión")
        return
    
    print("✅ Conectado")
    
    # Actualizar códigos
    try:
        market_data.api.update_ACTIVES_OPCODE()
        print("✅ Códigos de activos actualizados")
    except:
        pass
    
    # Test 1: get_all_profit
    print("\n[2/4] Obteniendo rentabilidades...")
    try:
        profits = market_data.api.get_all_profit()
        if profits:
            print(f"✅ Obtenidas rentabilidades de {len(profits)} activos")
            
            # Filtrar OTC
            otc_count = sum(1 for name in profits.keys() if '-OTC' in name)
            normal_count = len(profits) - otc_count
            
            print(f"   📊 Activos OTC: {otc_count}")
            print(f"   📊 Activos normales: {normal_count}")
        else:
            print("⚠️ No se obtuvieron rentabilidades")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Activos OTC específicos
    print("\n[3/4] Probando activos OTC específicos...")
    otc_assets = [
        "EURUSD-OTC", "GBPUSD-OTC", "USDJPY-OTC",
        "AUDUSD-OTC", "USDCAD-OTC", "EURJPY-OTC"
    ]
    
    available_otc = []
    for asset in otc_assets:
        try:
            df = market_data.get_candles(asset, 60, 1, time.time())
            if not df.empty:
                price = df.iloc[-1]['close']
                print(f"   ✅ {asset}: ${price:.5f}")
                available_otc.append(asset)
            else:
                print(f"   ❌ {asset}: Sin datos")
        except Exception as e:
            print(f"   ❌ {asset}: Error - {e}")
    
    print(f"\n   📊 Total OTC disponibles: {len(available_otc)}")
    
    # Test 3: Activos normales
    print("\n[4/4] Probando activos normales...")
    normal_assets = [
        "EURUSD", "GBPUSD", "USDJPY",
        "AUDUSD", "USDCAD", "EURJPY"
    ]
    
    available_normal = []
    for asset in normal_assets:
        try:
            df = market_data.get_candles(asset, 60, 1, time.time())
            if not df.empty:
                price = df.iloc[-1]['close']
                print(f"   ✅ {asset}: ${price:.5f}")
                available_normal.append(asset)
            else:
                print(f"   ❌ {asset}: Sin datos")
        except Exception as e:
            print(f"   ❌ {asset}: Error - {e}")
    
    print(f"\n   📊 Total normales disponibles: {len(available_normal)}")
    
    # Resumen
    print("\n" + "=" * 70)
    print("📊 RESUMEN")
    print("=" * 70)
    print(f"Activos OTC disponibles: {len(available_otc)}")
    if available_otc:
        print("   " + ", ".join(available_otc))
    
    print(f"\nActivos normales disponibles: {len(available_normal)}")
    if available_normal:
        print("   " + ", ".join(available_normal))
    
    if not available_otc and not available_normal:
        print("\n⚠️ ADVERTENCIA: No se encontraron activos disponibles")
        print("   Posibles causas:")
        print("   1. Mercado cerrado (activos normales)")
        print("   2. Problema con la API")
        print("   3. Cuenta no verificada")
    else:
        print("\n✅ Hay activos disponibles para operar")
    
    print("=" * 70)

if __name__ == "__main__":
    test_activos()
