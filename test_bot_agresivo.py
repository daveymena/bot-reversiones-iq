#!/usr/bin/env python3
"""
Test del bot en modo agresivo - Encuentra más operaciones
"""

import sys
import os
import time
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_bot_agresivo():
    """Prueba el bot con configuración más agresiva"""
    print("🚀 INICIANDO BOT EN MODO AGRESIVO")
    print("=" * 50)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    try:
        # Importar componentes necesarios
        from data.market_data import MarketDataHandler
        from strategies.technical import FeatureEngineer
        from core.asset_manager import AssetManager
        from ai.llm_client import LLMClient
        from config import Config
        
        print("📊 Inicializando componentes...")
        
        # Crear instancias
        market_data = MarketDataHandler()
        feature_engineer = FeatureEngineer()
        llm_client = LLMClient()
        
        # Conectar al broker
        print("🔌 Conectando a Exnova...")
        success = market_data.connect(Config.EXNOVA_EMAIL, Config.EXNOVA_PASSWORD)
        
        if not success:
            print("❌ Error conectando al broker")
            return False
        
        print("✅ Conectado exitosamente")
        
        # Crear asset manager
        asset_manager = AssetManager(market_data)
        
        # Hacer el sistema más agresivo
        print("⚡ Configurando modo AGRESIVO...")
        asset_manager.min_profit = 60  # Reducir de 70 a 60
        
        # Obtener activos disponibles
        print("🔍 Verificando activos disponibles...")
        available_assets = asset_manager.get_available_otc_assets(verbose=True)
        
        if not available_assets:
            print("❌ No hay activos disponibles")
            return False
        
        asset_manager.monitored_assets = available_assets[:5]  # Monitorear top 5
        
        print(f"📊 Monitoreando: {', '.join(asset_manager.monitored_assets)}")
        
        # Buscar oportunidades en bucle
        print("\n🎯 BUSCANDO OPORTUNIDADES (Modo Agresivo)...")
        print("=" * 50)
        
        max_attempts = 10
        opportunities_found = 0
        
        for attempt in range(max_attempts):
            print(f"\n🔍 Intento {attempt + 1}/{max_attempts}")
            
            # Escanear oportunidades
            opportunity = asset_manager.scan_best_opportunity(feature_engineer)
            
            if opportunity:
                opportunities_found += 1
                print(f"💎 OPORTUNIDAD #{opportunities_found} ENCONTRADA:")
                print(f"   Activo: {opportunity['asset']}")
                print(f"   Acción: {opportunity['action']}")
                print(f"   Score: {opportunity['score']}")
                print(f"   Confianza: {opportunity['confidence']*100:.1f}%")
                print(f"   Setup: {opportunity.get('setup', 'N/A')}")
                print(f"   Razón: {opportunity.get('reasoning', 'N/A')}")
                
                # Probar análisis de Ollama (con timeout corto)
                if Config.USE_LLM:
                    print("🧠 Probando análisis de Ollama...")
                    try:
                        # Preparar datos para Ollama
                        market_summary = f"{opportunity['asset']}: {opportunity['indicators']['price']:.5f} | RSI: {opportunity['indicators']['rsi']:.1f} | Tendencia: {opportunity['indicators']['trend']}"
                        smart_summary = f"Setup: {opportunity.get('setup', 'N/A')} | Confianza: {opportunity['confidence']*100:.0f}%"
                        learning_summary = "Sistema inicializándose"
                        
                        # Consultar Ollama con timeout
                        import threading
                        import time
                        
                        ollama_result = None
                        ollama_error = None
                        
                        def ollama_query():
                            nonlocal ollama_result, ollama_error
                            try:
                                ollama_result = llm_client.analyze_complete_trading_opportunity(
                                    market_data_summary=market_summary,
                                    smart_money_analysis=smart_summary,
                                    learning_insights=learning_summary,
                                    asset=opportunity['asset'],
                                    current_balance=1000.0
                                )
                            except Exception as e:
                                ollama_error = str(e)
                        
                        # Ejecutar con timeout de 20 segundos
                        thread = threading.Thread(target=ollama_query, daemon=True)
                        thread.start()
                        thread.join(timeout=20)
                        
                        if thread.is_alive():
                            print("   ⏱️ Ollama tardó más de 20s - TIMEOUT")
                        elif ollama_error:
                            print(f"   ❌ Error en Ollama: {ollama_error}")
                        elif ollama_result:
                            if ollama_result.get('should_trade'):
                                print(f"   ✅ Ollama APRUEBA: {ollama_result['direction']} ({ollama_result['confidence']:.0f}%)")
                                print(f"   💡 Razón: {ollama_result['primary_reason']}")
                            else:
                                print(f"   ⏸️ Ollama RECHAZA: {ollama_result['primary_reason']}")
                        else:
                            print("   ⚠️ Ollama no respondió correctamente")
                    
                    except Exception as e:
                        print(f"   ❌ Error probando Ollama: {e}")
                
                print("   " + "="*40)
            else:
                print("   ⏳ No hay oportunidades claras en este momento")
            
            # Esperar un poco antes del siguiente intento
            if attempt < max_attempts - 1:
                print("   ⏱️ Esperando 10 segundos...")
                time.sleep(10)
        
        # Resumen final
        print("\n" + "=" * 50)
        print("📊 RESUMEN DEL TEST AGRESIVO")
        print("=" * 50)
        print(f"Intentos realizados: {max_attempts}")
        print(f"Oportunidades encontradas: {opportunities_found}")
        print(f"Tasa de detección: {(opportunities_found/max_attempts)*100:.1f}%")
        
        if opportunities_found > 0:
            print("✅ El sistema está detectando oportunidades correctamente")
            print("💡 Recomendación: El bot debería funcionar bien en modo real")
        else:
            print("⚠️ No se detectaron oportunidades")
            print("💡 Recomendación: Revisar configuración o condiciones del mercado")
        
        return opportunities_found > 0
        
    except Exception as e:
        print(f"❌ Error en test agresivo: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_bot_agresivo()
    if success:
        print("\n🎉 Test completado exitosamente")
    else:
        print("\n❌ Test falló")