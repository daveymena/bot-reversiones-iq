#!/usr/bin/env python3
"""
Bot de Trading Agresivo - Versión optimizada para encontrar más operaciones
"""

import sys
import os
import time
import threading
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar componentes
from data.market_data import MarketDataHandler
from strategies.technical import FeatureEngineer
from core.asset_manager import AssetManager
from core.risk import RiskManager
from ai.llm_client import LLMClient
from config import Config

class TradingBotAgresivo:
    def __init__(self):
        print("🚀 INICIANDO BOT AGRESIVO")
        print("=" * 50)
        
        # Inicializar componentes
        self.market_data = MarketDataHandler()
        self.feature_engineer = FeatureEngineer()
        self.risk_manager = RiskManager()
        self.llm_client = LLMClient()
        
        # Asset manager con configuración agresiva
        self.asset_manager = AssetManager(self.market_data)
        self.asset_manager.min_profit = 60  # Más agresivo
        
        self.running = False
        self.active_trades = []
        self.last_trade_time = 0
        self.min_time_between_trades = 60  # 1 minuto entre trades
        
        # Configuración agresiva
        self.ollama_timeout = 20  # Timeout corto para Ollama
        self.scan_interval = 20   # Escanear cada 20 segundos
        self.last_scan_time = 0
        
    def connect(self):
        """Conectar al broker"""
        print("🔌 Conectando a Exnova...")
        success = self.market_data.connect(Config.EXNOVA_EMAIL, Config.EXNOVA_PASSWORD)
        
        if success:
            print("✅ Conectado exitosamente")
            return True
        else:
            print("❌ Error conectando al broker")
            return False
    
    def start(self):
        """Iniciar el bot"""
        if not self.connect():
            return False
        
        self.running = True
        
        # Obtener activos disponibles
        print("🔍 Verificando activos disponibles...")
        available_assets = self.asset_manager.get_available_otc_assets(verbose=True)
        
        if not available_assets:
            print("❌ No hay activos disponibles")
            return False
        
        self.asset_manager.monitored_assets = available_assets[:5]
        print(f"📊 Monitoreando: {', '.join(self.asset_manager.monitored_assets)}")
        
        # Iniciar bucle principal
        print("\n🎯 INICIANDO BÚSQUEDA AGRESIVA DE OPORTUNIDADES...")
        print("=" * 60)
        
        iteration = 0
        while self.running:
            try:
                iteration += 1
                
                # Verificar trades activos
                self.check_active_trades()
                
                # Solo buscar nuevas oportunidades si no hay trades activos
                if not self.active_trades:
                    # Escanear cada 20 segundos
                    if time.time() - self.last_scan_time >= self.scan_interval:
                        print(f"\n🔍 Escaneo #{iteration} - {datetime.now().strftime('%H:%M:%S')}")
                        
                        opportunity = self.asset_manager.scan_best_opportunity(self.feature_engineer)
                        self.last_scan_time = time.time()
                        
                        if opportunity:
                            print(f"💎 OPORTUNIDAD: {opportunity['asset']} - {opportunity['action']} ({opportunity['score']}%)")
                            
                            # Verificar tiempo mínimo entre trades
                            if time.time() - self.last_trade_time >= self.min_time_between_trades:
                                self.process_opportunity(opportunity)
                            else:
                                remaining = int(self.min_time_between_trades - (time.time() - self.last_trade_time))
                                print(f"⏳ Esperando {remaining}s antes del próximo trade")
                        else:
                            print("⏳ No hay oportunidades claras")
                    else:
                        remaining = int(self.scan_interval - (time.time() - self.last_scan_time))
                        if remaining % 5 == 0 and remaining > 0:
                            print(f"⏱️ Próximo escaneo en {remaining}s...")
                
                time.sleep(1)
                
            except KeyboardInterrupt:
                print("\n🛑 Deteniendo bot...")
                self.running = False
                break
            except Exception as e:
                print(f"❌ Error en bucle principal: {e}")
                time.sleep(5)
        
        print("✅ Bot detenido")
        return True
    
    def process_opportunity(self, opportunity):
        """Procesar una oportunidad detectada"""
        print(f"\n🧠 ANALIZANDO OPORTUNIDAD: {opportunity['asset']}")
        
        # Obtener datos del mercado
        df = self.market_data.get_candles(opportunity['asset'], 60, 100)
        if df.empty:
            print("❌ No se pudieron obtener datos del mercado")
            return
        
        # Aplicar feature engineering
        df = self.feature_engineer.prepare_for_rl(df)
        current_price = df.iloc[-1]['close']
        
        # Preparar datos para análisis
        market_summary = f"{opportunity['asset']}: {current_price:.5f} | RSI: {opportunity['indicators']['rsi']:.1f}"
        smart_summary = f"Setup: {opportunity.get('setup', 'N/A')} | Score: {opportunity['score']}%"
        learning_summary = "Sistema agresivo activo"
        
        # Intentar análisis con Ollama (con timeout corto)
        should_trade = False
        direction = opportunity['action']
        confidence = opportunity['confidence']
        reason = "Análisis técnico"
        
        if Config.USE_LLM:
            print("🧠 Consultando Ollama (timeout 20s)...")
            
            ollama_result = None
            ollama_error = None
            
            def ollama_query():
                nonlocal ollama_result, ollama_error
                try:
                    ollama_result = self.llm_client.analyze_complete_trading_opportunity(
                        market_data_summary=market_summary,
                        smart_money_analysis=smart_summary,
                        learning_insights=learning_summary,
                        asset=opportunity['asset'],
                        current_balance=self.market_data.get_balance()
                    )
                except Exception as e:
                    ollama_error = str(e)
            
            # Ejecutar con timeout
            thread = threading.Thread(target=ollama_query, daemon=True)
            thread.start()
            thread.join(timeout=self.ollama_timeout)
            
            if thread.is_alive():
                print("⏱️ Ollama timeout - usando análisis técnico")
                should_trade = opportunity['score'] >= 70  # Umbral agresivo
                reason = "Timeout Ollama - análisis técnico"
            elif ollama_error:
                print(f"❌ Error Ollama: {ollama_error}")
                should_trade = opportunity['score'] >= 75  # Umbral más alto por error
                reason = "Error Ollama - análisis técnico"
            elif ollama_result:
                should_trade = ollama_result.get('should_trade', False)
                if should_trade:
                    direction = ollama_result['direction']
                    confidence = ollama_result['confidence'] / 100
                    reason = ollama_result['primary_reason']
                    print(f"✅ Ollama APRUEBA: {direction} ({ollama_result['confidence']:.0f}%)")
                else:
                    print(f"⏸️ Ollama RECHAZA: {ollama_result['primary_reason']}")
                    reason = ollama_result['primary_reason']
            else:
                print("⚠️ Ollama sin respuesta - usando análisis técnico")
                should_trade = opportunity['score'] >= 70
                reason = "Ollama sin respuesta - análisis técnico"
        else:
            # Sin Ollama, usar solo análisis técnico
            should_trade = opportunity['score'] >= 65  # Umbral agresivo sin IA
            reason = "Solo análisis técnico"
        
        # Ejecutar trade si se aprueba
        if should_trade:
            print(f"\n🚀 EJECUTANDO TRADE:")
            print(f"   Activo: {opportunity['asset']}")
            print(f"   Dirección: {direction}")
            print(f"   Confianza: {confidence*100:.1f}%")
            print(f"   Razón: {reason}")
            
            self.execute_trade(opportunity['asset'], direction.lower(), current_price)
        else:
            print(f"\n⏸️ TRADE RECHAZADO: {reason}")
    
    def execute_trade(self, asset, direction, current_price):
        """Ejecutar un trade real"""
        try:
            amount = self.risk_manager.get_trade_amount()
            expiration = 3  # 3 minutos por defecto
            
            print(f"💰 Monto: ${amount:.2f} | Expiración: {expiration} min")
            
            # Ejecutar en el broker
            status, trade_id = self.market_data.api.buy(amount, asset, direction, expiration)
            
            if status:
                print(f"✅ Trade ejecutado - ID: {trade_id}")
                
                # Guardar trade activo
                self.active_trades.append({
                    'id': trade_id,
                    'asset': asset,
                    'direction': direction,
                    'amount': amount,
                    'entry_time': time.time(),
                    'entry_price': current_price,
                    'duration': expiration * 60
                })
                
                self.last_trade_time = time.time()
            else:
                print(f"❌ Error ejecutando trade: {trade_id}")
        
        except Exception as e:
            print(f"❌ Error en execute_trade: {e}")
    
    def check_active_trades(self):
        """Verificar trades activos"""
        completed_trades = []
        
        for trade in self.active_trades:
            # Verificar si el trade ha terminado
            if time.time() - trade['entry_time'] >= trade['duration'] + 10:  # +10s margen
                completed_trades.append(trade)
        
        # Procesar trades completados
        for trade in completed_trades:
            self.active_trades.remove(trade)
            self.process_trade_result(trade)
    
    def process_trade_result(self, trade):
        """Procesar resultado de un trade"""
        try:
            print(f"\n📊 Verificando resultado del trade {trade['id']}...")
            
            # Obtener resultado del broker
            if self.market_data.broker_name == "exnova":
                result_status, profit = self.market_data.api.check_win_v4(trade['id'], timeout=30)
            else:
                profit = self.market_data.api.check_win_v3(trade['id'])
                result_status = "win" if profit > 0 else "loose"
            
            won = profit > 0
            
            if won:
                print(f"✅ GANADA: +${profit:.2f}")
                self.risk_manager.update_trade_result(profit)
            else:
                print(f"❌ PERDIDA: ${profit:.2f}")
                self.risk_manager.update_trade_result(profit, {'should_martingale': False, 'reason': 'Pérdida normal'})
            
            # Mostrar balance actualizado
            balance = self.market_data.get_balance()
            print(f"💰 Balance actual: ${balance:.2f}")
            
        except Exception as e:
            print(f"❌ Error verificando resultado: {e}")

def main():
    """Función principal"""
    print("🤖 BOT DE TRADING AGRESIVO")
    print("=" * 50)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Broker: {Config.BROKER_NAME}")
    print(f"Cuenta: {Config.ACCOUNT_TYPE}")
    print("=" * 50)
    
    bot = TradingBotAgresivo()
    
    try:
        bot.start()
    except KeyboardInterrupt:
        print("\n🛑 Bot detenido por el usuario")
    except Exception as e:
        print(f"❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()