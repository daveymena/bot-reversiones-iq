"""
DEMO: Ejecuta UNA operación real en IQ Option
Muestra todo el proceso paso a paso
"""
import time
from config import Config
from iqoptionapi.stable_api import IQ_Option

def main():
    print("\n" + "=" * 70)
    print(" 🤖 DEMO - BOT DE TRADING IQ OPTION")
    print("=" * 70)
    
    # Paso 1: Conectar
    print("\n📡 [1/5] Conectando a IQ Option...")
    api = IQ_Option(Config.IQ_EMAIL, Config.IQ_PASSWORD)
    check, reason = api.connect()
    
    if not check:
        print(f"   ❌ Error: {reason}")
        return
    
    print("   ✅ Conectado exitosamente")
    
    # Paso 2: Configurar cuenta DEMO
    print("\n💰 [2/5] Configurando cuenta DEMO...")
    api.change_balance("PRACTICE")
    time.sleep(2)
    
    balance = api.get_balance()
    print(f"   ✅ Balance disponible: ${balance:.2f}")
    
    # Paso 3: Configurar operación
    activo = "EURUSD-OTC"
    monto = 1.0
    direccion = "call"
    duracion = 1
    
    print("\n⚙️  [3/5] Configurando operación...")
    print(f"   📊 Activo: {activo}")
    print(f"   💵 Monto: ${monto}")
    print(f"   📈 Dirección: {direccion.upper()}")
    print(f"   ⏱️  Duración: {duracion} minuto")
    
    # Paso 4: Ejecutar operación
    print("\n🚀 [4/5] Ejecutando operación...")
    try:
        status, order_id = api.buy(monto, activo, direccion, duracion)
        
        if not status:
            print(f"   ❌ Error: {order_id}")
            return
        
        print(f"   ✅ Operación ejecutada")
        print(f"   🆔 Order ID: {order_id}")
        
        # Paso 5: Esperar y verificar resultado
        tiempo_espera = (duracion * 60) + 10
        print(f"\n⏳ [5/5] Esperando resultado ({tiempo_espera} segundos)...")
        
        for i in range(tiempo_espera, 0, -10):
            print(f"   ⏱️  {i} segundos restantes...")
            time.sleep(10)
        
        print("\n📊 Verificando resultado...")
        profit = api.check_win_v3(order_id)
        balance_final = api.get_balance()
        
        # Mostrar resultado
        print("\n" + "=" * 70)
        print(" 📈 RESULTADO DE LA OPERACIÓN")
        print("=" * 70)
        print(f"   Profit/Loss: ${profit:.2f}")
        print(f"   Balance inicial: ${balance:.2f}")
        print(f"   Balance final: ${balance_final:.2f}")
        print(f"   Diferencia: ${balance_final - balance:.2f}")
        
        if profit > 0:
            print("\n   🎉 ¡OPERACIÓN GANADA!")
            print(f"   💰 Ganaste ${profit:.2f}")
        elif profit < 0:
            print("\n   😞 Operación perdida")
            print(f"   💸 Perdiste ${abs(profit):.2f}")
        else:
            print("\n   ⏸️  Operación empatada")
        
        print("=" * 70)
        print("\n✅ El bot de IQ Option funciona correctamente")
        print("   Puedes ejecutar 'python main.py' para usar la GUI completa\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
