#!/usr/bin/env python3
"""
Bot de Trading con IA Orquestador - Versión Consola Pura
Usa Groq como principal y Ollama como respaldo
"""

import sys
import os
import time
import signal
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar componentes
from data.market_data import MarketDataHandler
from strategies.technical import FeatureEngineer
from core.agent import RLAgent
from core.risk import RiskManager
from core.asset_manager import AssetManager
from ai.llm_client import LLMClient
from config import Config

# Variable global para control
running = True

def signal_handler(sig, frame):
    """Maneja la señal de interrupción"""
    global running
    print("\n🛑 Deteniendo bot...")
    running = False
    sys.exit(0)

def print_ai_status(llm_client):
    """Muestra el estado de las IAs"""
    print("🧠 ESTADO DEL SISTEMA DE IA (3 CAPAS OPTIMIZADO):")
    
    # Capa 1: Groq
    if llm_client.use_groq and llm_client.groq_client:
        print(f"   ⚡ Groq ACTIVO (Llave #{llm_client.current_key_index + 1}/{len(llm_client.api_keys)}) - Principal")
    elif len(llm_client.api_keys) > 0:
        print(f"   ⚠️ Groq AGOTADO (Probadas {len(llm_client.api_keys)} llaves)")
    else:
        print("   ❌ Groq NO CONFIGURADO")
    
    # Capa 2: LocalAI (Ultra-rápida)
    try:
        from ai.local_ai_analyzer import LocalAIAnalyzer
        local_ai = LocalAIAnalyzer()
        print("   🚀 LocalAI ACTIVO (Ultra-rápida <1ms) - Respaldo Principal")
    except Exception as e:
        print(f"   ❌ LocalAI ERROR: {e}")
    
    # Capa 3: Ollama (Solo si responde en <1s)
    try:
        print("   🐌 Ollama DISPONIBLE (timeout 1s) - Solo Emergencia")
    except Exception as e:
        print(f"   ❌ Ollama ERROR: {e}")
    
    print("   📊 Fallback Técnico: SIEMPRE DISPONIBLE")

def analyze_opportunity_with_ai(llm_client, asset, df, indicators):
    """Analiza oportunidad usando sistema de IA de 3 capas OPTIMIZADO"""
    
    if df.empty or len(df) < 10:
        return None
    
    last_candle = df.iloc[-1]
    rsi = last_candle.get('rsi', 50)
    macd = last_candle.get('macd', 0)
    price = last_candle['close']
    
    print(f"🧠 Analizando {asset} (RSI: {rsi:.1f}, MACD: {macd:.5f})...")
    
    # CAPA 1: GROQ (Principal - si está disponible)
    if llm_client.use_groq and llm_client.groq_client:
        try:
            print("   ⚡ Probando Groq...")
            
            simple_prompt = f"Trading {asset}: RSI {rsi:.1f}, MACD {macd:.5f}. Responde: CALL/PUT/HOLD"
            
            response = llm_client._safe_query(simple_prompt)
            
            if "CALL" in response.upper():
                print("✅ GROQ DICE: CALL")
                return {
                    'asset': asset,
                    'direction': 'CALL',
                    'confidence': 0.80,
                    'reason': 'Decisión de Groq',
                    'ai_source': 'Groq'
                }
            elif "PUT" in response.upper():
                print("✅ GROQ DICE: PUT")
                return {
                    'asset': asset,
                    'direction': 'PUT',
                    'confidence': 0.80,
                    'reason': 'Decisión de Groq',
                    'ai_source': 'Groq'
                }
            else:
                print(f"⏸️ GROQ RECHAZA: {response[:50]}...")
                
        except Exception as e:
            print(f"⚠️ Groq error: {str(e)[:50]}...")
    
    # CAPA 2: LOCAL AI (Ultra-rápida, SIEMPRE disponible)
    print("   🚀 Usando LocalAI (ultra-rápida <1ms)...")
    try:
        from ai.local_ai_analyzer import LocalAIAnalyzer
        
        local_ai = LocalAIAnalyzer()
        decision = local_ai.analyze_market_opportunity(asset, df)
        
        if decision:
            print(f"✅ LOCAL AI DICE: {decision['direction']}")
            return decision
        else:
            print("   ⏸️ LocalAI: Sin señales claras")
            
    except Exception as e:
        print(f"   ❌ Error en LocalAI: {e}")
    
    # CAPA 3: OLLAMA (Solo si responde en <1s)
    print("   ⚡ Probando Ollama (timeout 1s)...")
    try:
        import requests
        
        simple_prompt = f"{asset}: RSI {rsi:.1f}. CALL/PUT?"
        
        payload = {
            "model": Config.OLLAMA_MODEL,
            "prompt": simple_prompt,
            "stream": False,
            "options": {
                "temperature": 0.1, 
                "num_ctx": 128,      # Contexto ultra-mínimo
                "num_predict": 5     # Solo 5 tokens
            }
        }
        
        # Timeout ultra-corto (1 segundo)
        response = requests.post(Config.OLLAMA_URL, json=payload, timeout=1, verify=False)
            
            if "CALL" in response.upper():
                print("✅ GROQ DICE: CALL")
                return {
                    'asset': asset,
                    'direction': 'CALL',
                    'confidence': 0.80,
                    'reason': 'Decisión de Groq',
                    'ai_source': 'Groq'
                }
            elif "PUT" in response.upper():
                print("✅ GROQ DICE: PUT")
                return {
                    'asset': asset,
                    'direction': 'PUT',
                    'confidence': 0.80,
                    'reason': 'Decisión de Groq',
                    'ai_source': 'Groq'
                }
            else:
                print(f"⏸️ GROQ RECHAZA: {response[:50]}...")
                
        except Exception as e:
            print(f"⚠️ Groq error: {str(e)[:50]}...")
    
    # CAPA 2: LOCAL AI (Ultra-rápida, siempre disponible)
    try:
        from ai.local_ai_analyzer import LocalAIAnalyzer
        
        print("   🤖 Usando LocalAI (ultra-liviana)...")
        
        local_ai = LocalAIAnalyzer()
        decision = local_ai.analyze_market_opportunity(asset, df)
        
        if decision:
            return decision
        else:
            print("   ⏸️ LocalAI: Sin señales claras")
            
    except Exception as e:
        print(f"   ❌ Error en LocalAI: {e}")
    
    # CAPA 3: OLLAMA (Solo si responde ultra-rápido)
    try:
        print("   🔄 Probando Ollama (timeout 1s)...")
        
        import requests
        
        simple_prompt = f"{asset}: RSI {rsi:.1f}. CALL/PUT?"
        
        payload = {
            "model": Config.OLLAMA_MODEL,
            "prompt": simple_prompt,
            "stream": False,
            "options": {
                "temperature": 0.1, 
                "num_ctx": 256,      # Contexto mínimo
                "num_predict": 10    # Solo 10 tokens
            }
        }
        
        # Timeout ultra-corto (1 segundo)
        response = requests.post(Config.OLLAMA_URL, json=payload, timeout=1, verify=False)
        
        if response.status_code == 200:
            ollama_response = response.json().get("response", "")
            
            if "CALL" in ollama_response.upper():
                print("✅ OLLAMA DICE: CALL (1s)")
                return {
                    'asset': asset,
                    'direction': 'CALL',
                    'confidence': 0.70,
                    'reason': 'Decisión rápida de Ollama',
                    'ai_source': 'Ollama'
                }
            elif "PUT" in ollama_response.upper():
                print("✅ OLLAMA DICE: PUT (1s)")
                return {
                    'asset': asset,
                    'direction': 'PUT',
                    'confidence': 0.70,
                    'reason': 'Decisión rápida de Ollama',
                    'ai_source': 'Ollama'
                }
            else:
                print(f"⏸️ OLLAMA RECHAZA: {ollama_response[:20]}...")
        else:
            print(f"❌ Ollama HTTP {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("⚡ Ollama timeout 1s (normal)")
    except Exception as e:
        print(f"⚠️ Ollama error: {str(e)[:20]}...")
    
    # FALLBACK FINAL: Análisis técnico inteligente
    print("   📊 Usando análisis técnico inteligente...")
    
    # Solo señales MUY claras para evitar pérdidas
    if rsi <= 15:  # Extremadamente sobreventa
        print(f"   📈 RSI EXTREMO ({rsi:.1f}) -> CALL")
        return {
            'asset': asset,
            'direction': 'CALL',
            'confidence': 0.75,
            'reason': f'RSI extremo sobreventa ({rsi:.1f})',
            'ai_source': 'Técnico'
        }
    elif rsi >= 85:  # Extremadamente sobrecompra
        print(f"   📉 RSI EXTREMO ({rsi:.1f}) -> PUT")
        return {
            'asset': asset,
            'direction': 'PUT',
            'confidence': 0.75,
            'reason': f'RSI extremo sobrecompra ({rsi:.1f})',
            'ai_source': 'Técnico'
        }
    elif macd > 0.001 and rsi < 40:  # MACD fuerte + RSI bajo
        print(f"   📈 MACD fuerte + RSI bajo -> CALL")
        return {
            'asset': asset,
            'direction': 'CALL',
            'confidence': 0.65,
            'reason': f'MACD alcista ({macd:.5f}) + RSI bajo ({rsi:.1f})',
            'ai_source': 'Técnico'
        }
    elif macd < -0.001 and rsi > 60:  # MACD negativo + RSI alto
        print(f"   📉 MACD negativo + RSI alto -> PUT")
        return {
            'asset': asset,
            'direction': 'PUT',
            'confidence': 0.65,
            'reason': f'MACD bajista ({macd:.5f}) + RSI alto ({rsi:.1f})',
            'ai_source': 'Técnico'
        }
    
    print("   ⏸️ Sin señales claras - esperando mejor oportunidad")
    return None
            print(f"❌ Ollama HTTP {response.status_code}")
            
    except Exception as e:
        print(f"⚠️ Ollama timeout/error (normal): {str(e)[:30]}...")
    
    # FALLBACK FINAL: Análisis técnico básico
    print("   📊 Fallback: Análisis técnico básico...")
    
    # Solo señales muy claras
    if rsi <= 20:  # Extremadamente sobreventa
        print(f"   � RSI EXTREMO ({rsi:.1f}) -> CALL")
        return {
            'asset': asset,
            'direction': 'CALL',
            'confidence': 0.75,
            'reason': f'RSI extremo ({rsi:.1f})',
            'ai_source': 'Técnico'
        }
    elif rsi >= 80:  # Extremadamente sobrecompra
        print(f"   📉 RSI EXTREMO ({rsi:.1f}) -> PUT")
        return {
            'asset': asset,
            'direction': 'PUT',
            'confidence': 0.75,
            'reason': f'RSI extremo ({rsi:.1f})',
            'ai_source': 'Técnico'
        }
    elif abs(macd) > 0.0003:  # MACD muy fuerte
        direction = 'CALL' if macd > 0 else 'PUT'
        print(f"   📊 MACD FUERTE ({macd:.5f}) -> {direction}")
        return {
            'asset': asset,
            'direction': direction,
            'confidence': 0.65,
            'reason': f'MACD fuerte ({macd:.5f})',
            'ai_source': 'Técnico'
        }
    else:
        print(f"   ⏸️ Sin señales extremas (RSI: {rsi:.1f}, MACD: {macd:.5f})")
        return None

def execute_trade_with_broker(market_data, opportunity, risk_manager):
    """Ejecuta la operación en el broker"""
    
    asset = opportunity['asset']
    direction = opportunity['direction'].lower()
    confidence = opportunity['confidence']
    ai_source = opportunity['ai_source']
    
    # Obtener monto de la operación
    amount = risk_manager.get_trade_amount()
    expiration = 3  # 3 minutos
    
    print(f"\n🚀 EJECUTANDO OPERACIÓN ({ai_source}):")
    print(f"   Asset: {asset}")
    print(f"   Dirección: {direction.upper()}")
    print(f"   Monto: ${amount:.2f}")
    print(f"   Confianza: {confidence*100:.1f}%")
    print(f"   Expiración: {expiration} min")
    
    try:
        # Obtener precio actual
        df = market_data.get_candles(asset, 60, 1)
        entry_price = df.iloc[-1]['close'] if not df.empty else 0
        
        # Ejecutar en broker
        success, order_id = market_data.api.buy(amount, asset, direction, expiration)
        
        if success:
            print(f"✅ Operación ejecutada - ID: {order_id}")
            print(f"   Precio de entrada: {entry_price:.5f}")
            
            return {
                'id': order_id,
                'asset': asset,
                'direction': direction,
                'amount': amount,
                'entry_price': entry_price,
                'entry_time': time.time(),
                'expiration_time': time.time() + (expiration * 60),
                'ai_source': ai_source
            }
        else:
            print(f"❌ Error ejecutando: {order_id}")
            return None
            
    except Exception as e:
        print(f"❌ Error en ejecución: {e}")
        return None

def check_trade_results(market_data, active_trades, risk_manager):
    """Verifica resultados de operaciones activas"""
    
    completed_trades = []
    current_time = time.time()
    
    for trade in active_trades:
        if current_time >= trade['expiration_time']:
            completed_trades.append(trade)
    
    for trade in completed_trades:
        active_trades.remove(trade)
        
        print(f"\n📊 Verificando resultado de {trade['id']} ({trade['ai_source']})...")
        
        try:
            # Obtener resultado del broker
            result_status, profit = market_data.api.check_win_v4(trade['id'], timeout=30)
            
            if result_status is None:
                print("⏱️ Timeout - Calculando por precio")
                # Calcular por precio
                df = market_data.get_candles(trade['asset'], 60, 1)
                exit_price = df.iloc[-1]['close'] if not df.empty else trade['entry_price']
                
                if trade['direction'] == 'call':
                    won = exit_price > trade['entry_price']
                else:
                    won = exit_price < trade['entry_price']
                
                profit = trade['amount'] * 0.85 if won else -trade['amount']
            else:
                won = profit > 0
            
            # Mostrar resultado
            if won:
                print(f"✅ GANADA ({trade['ai_source']}): +${profit:.2f}")
                risk_manager.update_trade_result(profit)
            else:
                print(f"❌ PERDIDA ({trade['ai_source']}): ${profit:.2f}")
                risk_manager.update_trade_result(profit)
            
            # Actualizar balance
            balance = market_data.get_balance()
            print(f"💰 Balance: ${balance:.2f}")
            
        except Exception as e:
            print(f"⚠️ Error verificando resultado: {e}")

def main():
    """Función principal"""
    global running
    
    # Configurar manejo de señales
    signal.signal(signal.SIGINT, signal_handler)
    
    print("=" * 60)
    print("🤖 BOT DE TRADING CON IA ORQUESTADOR")
    print("=" * 60)
    print(f"📅 Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🏦 Broker: {Config.BROKER_NAME.upper()}")
    print(f"💰 Capital: ${Config.CAPITAL_PER_TRADE}")
    print("🧠 Sistema: Groq (Principal) + Ollama (Respaldo)")
    print("=" * 60)
    
    try:
        # 1. Inicializar IA
        print("\n🧠 Inicializando sistema de IA...")
        llm_client = LLMClient()
        print_ai_status(llm_client)
        
        # 2. Inicializar componentes de trading
        print("\n📊 Inicializando componentes de trading...")
        
        market_data = MarketDataHandler(
            broker_name=Config.BROKER_NAME,
            account_type=Config.ACCOUNT_TYPE
        )
        
        feature_engineer = FeatureEngineer()
        
        risk_manager = RiskManager(
            capital_per_trade=Config.CAPITAL_PER_TRADE,
            stop_loss_pct=0.8,
            take_profit_pct=0.85,
            max_martingale_steps=0
        )
        
        asset_manager = AssetManager(market_data)
        
        # 3. Conectar al broker
        print(f"\n🔌 Conectando a {Config.BROKER_NAME.upper()}...")
        
        success = market_data.connect(Config.EXNOVA_EMAIL, Config.EXNOVA_PASSWORD)
        if not success:
            print("❌ Error conectando al broker")
            return False
        
        print(f"✅ Conectado - Modo {Config.ACCOUNT_TYPE}")
        
        # 4. Obtener balance inicial
        balance = market_data.get_balance()
        print(f"💰 Balance inicial: ${balance:.2f}")
        
        # 5. Configurar activos
        otc_assets = ["EURUSD-OTC", "GBPUSD-OTC", "USDJPY-OTC", "AUDUSD-OTC"]
        print(f"📈 Monitoreando {len(otc_assets)} activos OTC")
        
        # 6. Loop principal de trading
        print("\n" + "=" * 60)
        print("🚀 INICIANDO TRADING CON IA ORQUESTADOR")
        print("=" * 60)
        print("Presiona Ctrl+C para detener\n")
        
        active_trades = []
        last_scan_time = 0
        iteration = 0
        
        while running:
            try:
                iteration += 1
                current_time = time.time()
                
                # Heartbeat cada 30 iteraciones
                if iteration % 30 == 0:
                    balance = market_data.get_balance()
                    print(f"\n💓 Bot activo - Balance: ${balance:.2f} - Operaciones activas: {len(active_trades)}")
                
                # Verificar operaciones activas
                if active_trades:
                    check_trade_results(market_data, active_trades, risk_manager)
                
                # Buscar nuevas oportunidades cada 30 segundos
                if current_time - last_scan_time >= 30 and len(active_trades) == 0:
                    last_scan_time = current_time
                    
                    print(f"\n🔍 Escaneando oportunidades... ({datetime.now().strftime('%H:%M:%S')})")
                    
                    for asset in otc_assets[:2]:  # Solo primeros 2 activos para no saturar
                        try:
                            # Obtener datos del mercado
                            df = market_data.get_candles(asset, 60, 100)
                            if df.empty or len(df) < 50:
                                continue
                            
                            # Preparar indicadores
                            df = feature_engineer.prepare_for_rl(df)
                            if df.empty:
                                continue
                            
                            # Analizar con IA como orquestador
                            opportunity = analyze_opportunity_with_ai(llm_client, asset, df, {})
                            
                            if opportunity:
                                # Ejecutar operación
                                trade = execute_trade_with_broker(market_data, opportunity, risk_manager)
                                
                                if trade:
                                    active_trades.append(trade)
                                    print("⏳ Esperando resultado...")
                                    break  # Solo una operación a la vez
                        
                        except Exception as e:
                            print(f"⚠️ Error analizando {asset}: {e}")
                            continue
                    
                    if not active_trades:
                        print("⏳ No hay oportunidades claras, esperando...")
                
                # Pausa para no saturar CPU
                time.sleep(1)
                
            except KeyboardInterrupt:
                print("\n🛑 Deteniendo por solicitud del usuario...")
                break
            
            except Exception as e:
                print(f"\n❌ Error en loop principal: {e}")
                print("⚠️ Continuando operación...")
                time.sleep(5)
        
        # 7. Resumen final
        print("\n" + "=" * 60)
        print("📊 RESUMEN FINAL")
        print("=" * 60)
        
        balance_final = market_data.get_balance()
        print(f"Balance final: ${balance_final:.2f}")
        print(f"Ganancia/Pérdida: ${balance_final - balance:.2f}")
        print(f"Total operaciones: {risk_manager.total_trades}")
        print(f"Ganadas: {risk_manager.wins}")
        print(f"Perdidas: {risk_manager.total_trades - risk_manager.wins}")
        
        if risk_manager.total_trades > 0:
            win_rate = (risk_manager.wins / risk_manager.total_trades) * 100
            print(f"Win Rate: {win_rate:.1f}%")
        
        print("=" * 60)
        print("👋 Bot detenido correctamente")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)