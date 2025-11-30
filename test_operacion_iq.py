"""
Test rápido de ejecución de operación en IQ Option
Ejecuta 1 operación de prueba con 1 minuto de expiración
"""
import time
from config import Config
from iqoptionapi.stable_api import IQ_Option

def test_operacion_iq():
    print("=" * 60)
    print("TEST DE OPERACIÓN - IQ OPTION")
    print("=" * 60)
    
    # Conectar
    print("\n[1/5] Conectando...")
    api = IQ_Option(Config.IQ_EMAIL, Config.IQ_PASSWORD)
    check, reason = api.connect()
    
    if not check:
        print(f"❌ Error: {reason}")
        return False
    
    print("✅ Conectado")
    
    # Cambiar a PRACTICE
    api.change_balance("PRACTICE")
    time.sleep(1)
    
    balance_inicial = api.get_balance()
    print(f"\n[2/5] Balance inicial: ${balance_inicial:.2f}")
    
    # Configurar operación
    activo = "EURUSD-OTC"
    monto = 1  # $1 para prueba
    direccion = "call"  # CALL
    duracion = 1  # 1 minuto
    
    print(f"\n[3/5] Ejecutando operación de prueba...")
    print(f"   Activo: {activo}")
    print(f"   Monto: ${monto}")
    print(f"   Dirección: {direccion.upper()}")
    print(f"   Duración: {duracion} min")
    
    # Ejecutar operación
    try:
        status, order_id = api.buy(monto, activo, direccion, duracion)
        
        if status:
            print(f"✅ Operación ejecutada - ID: {order_id}")
            
            # Esperar resultado
            print(f"\n[4/5] Esperando {duracion} minuto(s) + 10 seg...")
            time.sleep((duracion * 60) + 10)
            
            # Verificar resultado
            print("\n[5/5] Verificando resultado...")
            try:
                profit = api.check_win_v3(order_id)
                
                balance_final = api.get_balance()
                
                print("\n" + "=" * 60)
                print("RESULTADO")
                print("=" * 60)
                print(f"Profit/Loss: ${profit:.2f}")
                print(f"Balance inicial: ${balance_inicial:.2f}")
                print(f"Balance final: ${balance_final:.2f}")
                print(f"Diferencia: ${balance_final - balance_inicial:.2f}")
                
                if profit > 0:
                    print("\n🎉 ¡OPERACIÓN GANADA!")
                elif profit < 0:
                    print("\n😞 Operación perdida")
                else:
                    print("\n⏸️ Operación empatada")
                
                print("=" * 60)
                return True
                
            except Exception as e:
                print(f"⚠️ Error verificando resultado: {e}")
                return False
        else:
            print(f"❌ Fallo en ejecución: {order_id}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_operacion_iq()
