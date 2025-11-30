"""
Script de Análisis de Rentabilidad en Tiempo Real
Ejecuta el ciclo completo del bot (Análisis -> Decisión -> Ejecución) en cuenta PRACTICE
para evaluar el comportamiento y la rentabilidad del diseño actual.
"""
import time
import pandas as pd
from config import Config
from data.market_data import MarketDataHandler
from strategies.technical import FeatureEngineer
from core.agent import RLAgent
from core.risk import RiskManager

def run_analysis():
    print("\n" + "=" * 60)
    print(" 📊 ANÁLISIS DE RENTABILIDAD EN TIEMPO REAL")
    print("=" * 60)

    # 1. Inicializar componentes
    print("\n[1] Inicializando componentes...")
    
    # Usar Exnova o IQ según config, forzamos Exnova si es posible por ser más estable, o IQ si el usuario prefiere
    # El usuario tiene archivos de IQ y Exnova. Probemos IQ primero ya que vimos logs de IQ antes.
    # Pero el usuario mencionó "analicemos el bot".
    # Usaremos la configuración por defecto o detectaremos cuál funciona.
    
    broker = "iq" # Default
    if Config.BROKER_NAME:
        broker = Config.BROKER_NAME
        
    print(f"   Broker: {broker.upper()}")
    
    market_data = MarketDataHandler(broker_name=broker, account_type="PRACTICE")
    feature_engineer = FeatureEngineer()
    agent = RLAgent(model_path=Config.MODEL_PATH)
    risk_manager = RiskManager(Config.CAPITAL_PER_TRADE, Config.STOP_LOSS_PCT, Config.TAKE_PROFIT_PCT)

    # 2. Conectar
    print("\n[2] Conectando...")
    if broker == "iq":
        connected = market_data.connect(Config.IQ_EMAIL, Config.IQ_PASSWORD)
    else:
        connected = market_data.connect(Config.EX_EMAIL, Config.EX_PASSWORD)
        
    if not connected:
        print("❌ No se pudo conectar. Revisa credenciales.")
        return

    # 3. Cargar Modelo
    print("\n[3] Cargando modelo IA...")
    try:
        agent.load()
        print("   ✅ Modelo cargado")
    except:
        print("   ⚠️ No se encontró modelo entrenado. El bot usará comportamiento aleatorio/básico.")

    # 4. Bucle de Análisis (5 iteraciones)
    asset = "EURUSD-OTC" # Activo muy líquido
    print(f"\n[4] Iniciando análisis en {asset} (5 iteraciones)...")
    
    wins = 0
    losses = 0
    ties = 0
    
    for i in range(1, 21):
        print(f"\n--- Iteración {i}/20 ---")
        
        # A. Obtener datos
        print("   📥 Obteniendo datos de mercado...")
        df = market_data.get_candles(asset, 60, 100) # 1 min, 100 velas
        
        if df.empty:
            print("   ❌ Error obteniendo velas. Reintentando...")
            time.sleep(2)
            continue
            
        current_price = df.iloc[-1]['close']
        print(f"   Precio actual: {current_price}")

        # B. Calcular indicadores
        print("   🧮 Calculando indicadores...")
        try:
            df_features = feature_engineer.prepare_for_rl(df)
            rsi = df_features.iloc[-1]['rsi']
            print(f"   RSI: {rsi:.2f}")
        except Exception as e:
            print(f"   ❌ Error en indicadores: {e}")
            continue

        # C. Predicción IA
        print("   🤖 Consultando IA...")
        action = 0
        try:
            obs = df_features.iloc[-10:].values # Últimas 10 velas
            # Asegurar forma correcta si es necesario
            if len(df_features) >= 10:
                # Pasamos df_features como contexto para el optimizador
                action = agent.predict(obs, df_context=df_features)
                if hasattr(action, 'item'): action = action.item()
                action = int(action)
        except Exception as e:
            print(f"   ⚠️ Error en predicción IA: {e}")
        
        # FORZAR OPERACIÓN PARA PRUEBA DE SISTEMA
        forced = False
        if action == 0 and i in [5, 10, 15]:
            print(f"   ⚠️ FORZANDO OPERACIÓN DE PRUEBA (Iteración {i})")
            action = 1 if i % 2 != 0 else 2 # Alternar CALL/PUT
            forced = True

        actions_map = {0: "HOLD", 1: "CALL", 2: "PUT"}
        decision = actions_map.get(action, "HOLD")
        print(f"   DECISIÓN IA: {decision} {'(FORZADA)' if forced else ''}")
        
        # D. Ejecutar si hay señal
        if action in [1, 2]:
            direction = "call" if action == 1 else "put"
            amount = risk_manager.get_trade_amount()
            
            print(f"   🚀 Ejecutando {direction.upper()} de ${amount}...")
            
            if broker == "iq":
                status, order_id = market_data.api.buy(amount, asset, direction, 1)
            else: # Exnova
                status, order_id = market_data.api.buy_digital_spot(asset, amount, direction, 1)
                
            if status:
                print(f"   ✅ Operación enviada (ID: {order_id})")
                print("   ⏳ Esperando resultado (60s)...")
                
                # Esperar resultado
                time.sleep(65) 
                
                # Verificar
                profit = 0
                if broker == "iq":
                    profit = market_data.api.check_win_v3(order_id)
                else:
                    # Exnova check win logic might differ, assuming similar for now or check_win_v3/v4
                    try:
                        profit = market_data.api.check_win_v3(order_id)
                    except:
                        # Fallback para Exnova si check_win_v3 falla
                        try:
                             status_win, profit_val = market_data.api.check_win_v4(order_id)
                             profit = profit_val
                        except:
                             profit = 0
                
                print(f"   💰 Profit: ${profit:.2f}")
                
                if profit > 0:
                    print("   🎉 GANADA")
                    wins += 1
                    risk_manager.update_trade_result(profit)
                elif profit < 0:
                    print("   😞 PERDIDA")
                    losses += 1
                    risk_manager.update_trade_result(profit)
                else:
                    print("   😐 EMPATE")
                    ties += 1
            else:
                print(f"   ❌ Error ejecutando orden: {order_id}")
        else:
            print("   zzz Sin señal clara. Esperando siguiente ciclo...")
            time.sleep(2) # Espera corta si no opera
            
    # 5. Resumen
    print("\n" + "=" * 60)
    print(" 📈 RESUMEN DE ANÁLISIS")
    print("=" * 60)
    print(f"   Operaciones: {wins + losses + ties}")
    print(f"   Ganadas: {wins}")
    print(f"   Perdidas: {losses}")
    print(f"   Empates: {ties}")
    
    win_rate = 0
    if (wins + losses) > 0:
        win_rate = (wins / (wins + losses)) * 100
        
    print(f"   Win Rate: {win_rate:.2f}%")
    
    print("\nCONCLUSIÓN PRELIMINAR:")
    if win_rate > 55:
        print("   ✅ El bot muestra potencial de rentabilidad.")
    else:
        print("   ⚠️ El bot necesita mejoras en la estrategia o entrenamiento.")
        print("   Sugerencia: Mejorar indicadores, aumentar entrenamiento o filtrar señales.")

if __name__ == "__main__":
    run_analysis()
