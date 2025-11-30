"""Script de prueba para verificar conexión a Exnova"""
import sys
from data.market_data import MarketDataHandler
from config import Config

def test_exnova():
    print("=" * 50)
    print("PRUEBA DE CONEXIÓN EXNOVA")
    print("=" * 50)
    
    # Crear handler para Exnova
    handler = MarketDataHandler(broker_name="exnova")
    
    # Intentar conectar
    print(f"\nIntentando conectar con:")
    print(f"Email: {Config.EX_EMAIL}")
    print(f"Password: {'*' * len(Config.EX_PASSWORD)}")
    
    success = handler.connect(Config.EX_EMAIL, Config.EX_PASSWORD)
    
    if success:
        print("\n✅ CONEXIÓN EXITOSA!")
        
        # Obtener balance
        balance = handler.get_balance()
        print(f"💰 Balance: ${balance:.2f}")
        
        # Intentar obtener velas
        print("\nObteniendo velas de EURUSD...")
        df = handler.get_candles("EURUSD", 60, 10)
        
        if not df.empty:
            print(f"✅ Velas obtenidas: {len(df)} registros")
            print("\nÚltimas 3 velas:")
            print(df.tail(3))
        else:
            print("⚠️ No se pudieron obtener velas")
            
        # Probar OTC
        print("\nProbando EURUSD-OTC...")
        df_otc = handler.get_candles("EURUSD-OTC", 60, 10)
        if not df_otc.empty:
            print(f"✅ Velas OTC obtenidas: {len(df_otc)} registros")
        else:
            print("⚠️ OTC no disponible o sin datos")
            
    else:
        print("\n❌ FALLO EN LA CONEXIÓN")
        print("Verifica tus credenciales en .env")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    test_exnova()
