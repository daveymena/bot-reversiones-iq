"""
Script para verificar en qué modo está operando el bot
"""
from config import Config
from data.market_data import MarketDataHandler
import time

def test_account_mode():
    print("\n" + "="*60)
    print("🔍 VERIFICACIÓN DE MODO DE CUENTA")
    print("="*60)
    
    # Mostrar configuración actual
    print(f"\n📋 Configuración en .env:")
    print(f"   Broker: {Config.BROKER_NAME}")
    print(f"   Tipo de Cuenta: {Config.ACCOUNT_TYPE}")
    
    # Advertencia si es REAL
    if Config.ACCOUNT_TYPE == "REAL":
        print("\n⚠️  ¡ADVERTENCIA! Modo REAL activado")
        print("   Las operaciones usarán dinero real")
        respuesta = input("\n¿Continuar con la prueba? (si/no): ")
        if respuesta.lower() != "si":
            print("❌ Prueba cancelada")
            return
    
    # Conectar
    print(f"\n🔌 Conectando a {Config.BROKER_NAME.upper()}...")
    market_data = MarketDataHandler(
        broker_name=Config.BROKER_NAME,
        account_type=Config.ACCOUNT_TYPE
    )
    
    if Config.BROKER_NAME == "exnova":
        connected = market_data.connect(Config.EX_EMAIL, Config.EX_PASSWORD)
    else:
        connected = market_data.connect(Config.IQ_EMAIL, Config.IQ_PASSWORD)
    
    if not connected:
        print("❌ No se pudo conectar")
        return
    
    # Verificar balance
    print("\n💰 Verificando balance...")
    time.sleep(2)
    
    try:
        if Config.BROKER_NAME == "exnova":
            # Obtener balance de Exnova
            balance_type = market_data.api.get_balance_mode()
            balance = market_data.api.get_balance()
            
            print(f"\n✅ CONEXIÓN EXITOSA")
            print(f"   Modo: {balance_type}")
            print(f"   Balance: ${balance:.2f}")
            
            # Verificar que coincida con la configuración
            if balance_type == Config.ACCOUNT_TYPE:
                print(f"\n✅ Modo correcto: {balance_type}")
            else:
                print(f"\n⚠️  ADVERTENCIA: Modo no coincide")
                print(f"   Esperado: {Config.ACCOUNT_TYPE}")
                print(f"   Actual: {balance_type}")
        
        elif Config.BROKER_NAME == "iq":
            # Obtener balance de IQ Option
            balance_type = market_data.api.get_balance_mode()
            balance = market_data.api.get_balance()
            
            print(f"\n✅ CONEXIÓN EXITOSA")
            print(f"   Modo: {balance_type}")
            print(f"   Balance: ${balance:.2f}")
            
            if balance_type == Config.ACCOUNT_TYPE:
                print(f"\n✅ Modo correcto: {balance_type}")
            else:
                print(f"\n⚠️  ADVERTENCIA: Modo no coincide")
                print(f"   Esperado: {Config.ACCOUNT_TYPE}")
                print(f"   Actual: {balance_type}")
    
    except Exception as e:
        print(f"⚠️  Error verificando balance: {e}")
    
    print("\n" + "="*60)
    print("✅ Verificación completada")
    print("="*60)

if __name__ == "__main__":
    test_account_mode()
