
import time
import pandas as pd
import sys
import os
sys.path.insert(0, '.')

# Forzar encoding UTF-8 para evitar errores de consola en Windows
if sys.stdout.encoding != 'utf-8':
    try:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    except:
        pass

from intelligent_learning import IntelligentLearningSystem
import config

def live_analysis_report():
    print("="*60)
    print("ANALIZADOR DE ENGANOS DEL MERCADO - REPORTE LOG")
    print("="*60)
    
    bot = IntelligentLearningSystem()
    print("Sistema cargado. Conectando para analisis en vivo...")
    
    os.environ["HEADLESS_MODE"] = "true"
    
    # Conectar
    if not bot.observer.market_data.connect(config.Config.EXNOVA_EMAIL, config.Config.EXNOVA_PASSWORD):
        print("Error de conexion")
        return

    for asset in bot.priority_assets[:3]:
        print(f"\nANALIZANDO ACTIVO: {asset}")
        try:
            df = bot.observer.market_data.get_candles(asset, 60, 200, time.time())
            if df.empty:
                print(f"   Datos insuficientes para {asset}")
                continue
            
            df = bot.observer.feature_engineer.prepare_for_rl(df)
            
            # 1. Tecnica
            strategy_res = bot.bollinger_rsi_strategy.analyze(df)
            print(f"   Tecnica (Bollinger+RSI): {strategy_res['action']} (Conf: {strategy_res.get('confidence', 0)}%)")
            
            # Intent
            intent = bot.intent_analyzer.analyze_intent(df)
            print(f"   Intencion del Mercado: {intent['intent']} - Fuerza: {intent['strength']:.2f}")
            
            if strategy_res['action'] != 'WAIT':
                # Filtros
                final_res = bot.apply_learned_filters({'asset': asset, 'strategy': strategy_res}, df)
                print(f"   RESULTADO FINAL: {final_res['strategy']['action']} - Conf: {final_res['strategy']['confidence']:.1f}%")
                print(f"   Razon: {final_res['strategy']['reason']}")
            else:
                print(f"   Sin senal clara. Razon: {strategy_res.get('reason', 'N/A')}")
                
        except Exception as e:
            print(f"   Error analizando {asset}: {e}")

    print("\n" + "="*60)
    print("Analisis completado.")
    bot.observer.market_data.disconnect()

if __name__ == "__main__":
    live_analysis_report()
