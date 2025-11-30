"""
DEMO: Ejecuta UNA operación real en Exnova
Muestra todo el proceso paso a paso
"""
import time
from config import Config
from exnovaapi.stable_api import Exnova

def main():
    print("\n" + "=" * 70)
    print(" 🤖 DEMO - BOT DE TRADING EXNOVA")
    print("=" * 70)
    
    # Paso 1: Conectar
    print("\n📡 [1/5] Conectando a Exnova...")
    api = Exnova(Config.EX_EMAIL, Config.EX_PASSWORD)
    status, message = api.connect()
    
    if not status:
        print(f"   ❌ Error: {message}")
        return
    
    if not api.check_connect():
        print("   ❌ WebSocket no conectado")
        return
    
    print("   ✅ Conectado exitosamente")
    
    # Paso 2: Configurar
    print("\n⚙️  [2/5] Configurando...")
    try:
        api.update_ACTIVES_OPCODE()
        print("   ✅ Códigos de activos actualizados")
    except:
        pass
    
    balance = api.get_balance()
    balance_mode = api.get_balance_mode()
    print(f"   ✅ Balance disponible: ${balance:.2f} ({balance_mode})")
    
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
        buy_status, order_id = api.buy(monto, activo, direccion, duracion)
        
        if not buy_status:
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
        balance_final = api.get_balance()
        diferencia = balance_final - balance
        
        # Mostrar resultado
        print("\n" + "=" * 70)
        print(" 📈 RESULTADO DE LA OPERACIÓN")
        print("=" * 70)
        print(f"   Balance inicial: ${balance:.2f}")
        print(f"   Balance final: ${balance_final:.2f}")
        print(f"   Diferencia: ${diferencia:.2f}")
        
        if diferencia > 0:
            print("\n   🎉 ¡OPERACIÓN GANADA!")
            print(f"   💰 Ganaste ${diferencia:.2f}")
        elif diferencia < 0:
            print("\n   😞 Operación perdida")
            print(f"   💸 Perdiste ${abs(diferencia):.2f}")
        else:
            print("\n   ⏸️  Operación empatada")
        
        print("=" * 70)
        print("\n✅ El bot de Exnova funciona correctamente")
        print("   Puedes ejecutar 'python main.py' para usar la GUI completa\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
