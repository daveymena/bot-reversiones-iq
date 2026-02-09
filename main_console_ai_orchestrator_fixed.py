#!/usr/bin/env python3
"""
Bot de Trading con IA Orquestador OPTIMIZADO - Versión Consola Profesional
Análisis Top-Down: M5 (Niveles S/R) + M1 (Gatillo/Momentum)
"""

import sys
import os
import time
import signal
import json
from datetime import datetime
import pandas as pd

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
from core.market_structure_analyzer import MarketStructureAnalyzer

# Variable global para control
running = True

class TradingControl:
    """Clase para controlar los resultados y límites del bot"""
    def __init__(self):
        self.wins = 0
        self.losses = 0
        self.total_pnl = 0.0
        self.consecutive_losses = 0
        self.max_consecutive_losses = 3
        self.daily_stop_loss = -20.0  # $ en pérdidas
        self.daily_take_profit = 50.0 # $ en ganancias
        self.max_trades_per_day = 20
        self.trades_count = 0
        self.start_balance = 0.0
        self.last_trade_time = 0
        
    def can_trade(self, current_balance):
        if self.trades_count >= self.max_trades_per_day:
            print(f"🛑 Límite de operaciones diarias alcanzado ({self.max_trades_per_day})")
            return False
        if self.total_pnl <= self.daily_stop_loss:
            print(f"🛑 Stop Loss diario alcanzado: {self.total_pnl:.2f}")
            return False
        if self.total_pnl >= self.daily_take_profit:
            print(f"✅ Take Profit diario alcanzado: {self.total_pnl:.2f}")
            return False
        if self.consecutive_losses >= self.max_consecutive_losses:
            print(f"⚠️ {self.consecutive_losses} pérdidas consecutivas. Deteniendo por seguridad.")
            return False
        
        # Cooldown agresivo (30s)
        elapsed = time.time() - self.last_trade_time
        if elapsed < 30: return False
        return True

    def update_result(self, profit):
        self.trades_count += 1
        self.total_pnl += profit
        self.last_trade_time = time.time()
        if profit > 0:
            self.wins += 1
            self.consecutive_losses = 0
            print(f"💰 RESULTADO: GANADA (+${profit:.2f})")
        else:
            self.losses += 1
            self.consecutive_losses += 1
            print(f"📉 RESULTADO: PERDIDA (${profit:.2f})")
        self.print_summary()

    def print_summary(self):
        print("\n" + "="*40)
        print(f"📊 RESUMEN DE SESIÓN")
        print(f"   Win/Loss: {self.wins}/{self.losses} | PnL: ${self.total_pnl:.2f}")
        print(f"   Trades: {self.trades_count}/{self.max_trades_per_day}")
        print("="*40 + "\n")

# Instancias globales
control = TradingControl()
structure_analyzer = MarketStructureAnalyzer()

def signal_handler(sig, frame):
    global running
    print("\n🛑 Deteniendo bot...")
    running = False
    sys.exit(0)

def get_detailed_context(asset, analysis):
    """Genera contexto rico basado en el análisis Top-Down"""
    sig = analysis['entry_signal']
    ctx = sig['market_context']
    lvls = ctx['levels']
    
    # Formatear niveles para la IA
    res = ", ".join([f"{r:.5f}" for r in lvls['resistances']])
    sup = ", ".join([f"{s:.5f}" for s in lvls['supports']])
    
    context = (
        f"Activo: {asset}\n"
        f"Tendencia (EMA/SMA): {ctx['trend'].upper()}\n"
        f"Zona CRÍTICA: {'CERCA DE RESISTENCIA' if ctx['near_res'] else 'CERCA DE SOPORTE' if ctx['near_sup'] else 'ZONA LIBRE'}\n"
        f"Niveles S/R: [Res]: {res} | [Sup]: {sup}\n"
        f"Razones Técnicas: {', '.join(sig['reasons'])}\n"
    )
    return context

def analyze_opportunity_with_ai(llm_client, asset, m1_df, m5_df):
    """Analiza con IA usando lógica Top-Down (M5 para niveles, M1 para señal)"""
    
    # 1. Análisis Técnico Profesional (Soporte/Resistencia/Momentum)
    analysis = structure_analyzer.analyze_full_context(m1_df, m5_df)
    technical_signal = analysis['entry_signal']
    
    context = get_detailed_context(asset, analysis)
    print(f"\n🔍 Analizando {asset} (M1/M5 Top-Down)...")
    display_context = context.replace('\n', ' | ')
    print(f"📊 {display_context}")
    
    # CAPA 1: IA (Groq/Ollama) con Reglas de Trader Real
    if llm_client.use_groq and llm_client.groq_client:
        try:
            print("   ⚡ Consultando IA con reglas de Soporte/Resistencia...")
            prompt = f"""
            Como TRADER PROFESIONAL de Opciones Binarias:
            {context}
            
            REGLAS DE ORO:
            1. NUNCA compres (CALL) si estamos tocando una RESISTENCIA.
            2. NUNCA vendas (PUT) si estamos tocando un SOPORTE.
            3. Entra en REVERSIÓN si el precio rechaza un nivel con fuerza.
            
            Sugerencia Técnica: {technical_signal['direction']} (Confianza: {technical_signal['confidence']}%)
            
            Responde SOLO JSON: {{"direction": "CALL/PUT/HOLD", "confidence": 0-1.0, "reason": "..."}}
            """
            
            response = llm_client._safe_query(prompt)
            try:
                start, end = response.find('{'), response.rfind('}') + 1
                if start >= 0:
                    decision = json.loads(response[start:end])
                    if decision['direction'] != "HOLD" and decision['confidence'] >= 0.6:
                        print(f"🔥 IA DECIDE: {decision['direction']} ({decision['confidence']*100:.0f}%)")
                        return {
                            'asset': asset, 'direction': decision['direction'], 
                            'confidence': decision['confidence'], 'reason': decision['reason'], 'ai_source': 'AI-Expert'
                        }
            except: pass
        except Exception as e: print(f"⚠️ Error IA: {e}")

    # CAPA 2: FALLBACK TÉCNICO (Solo si es muy seguro)
    if technical_signal['should_enter'] and technical_signal['confidence'] >= 80:
        print(f"🎯 SEÑAL TÉCNICA PURA: {technical_signal['direction']} ({technical_signal['confidence']}%)")
        return {
            'asset': asset, 'direction': technical_signal['direction'],
            'confidence': technical_signal['confidence'] / 100,
            'reason': technical_signal['reasons'][0], 'ai_source': 'Technical'
        }
    
    print("   ⏸️ Sin señales claras o zona de riesgo bloqueada.")
    return None

def execute_trade(market_data, decision):
    """Ejecuta operación de 1-3 min"""
    try:
        asset, direction = decision['asset'], decision['direction']
        amount = Config.CAPITAL_PER_TRADE
        
        print(f"\n🚀 EJECUTANDO: {direction} en {asset} (${amount})")
        print(f"   Razón: {decision['reason']}")
        
        # En binarias, 1-2 minutos suele ser mejor tras rechazo de nivel
        duration = 1 if "Rechazo" in decision['reason'] else 2 
        
        success, order_id = market_data.buy(asset=asset, amount=amount, action=direction.lower(), duration=duration)
        
        if success:
            print(f"✅ ABIERTA ID: {order_id}. Esperando {duration} min...")
            time.sleep(duration * 60 + 5)
            
            profit = 0
            try:
                if market_data.broker_name == "exnova":
                    _, profit = market_data.api.check_win_v4(order_id)
                else:
                    profit = market_data.api.check_win_v3(order_id)
            except: pass
                
            control.update_result(profit)
            return True
        return False
    except Exception as e:
        print(f"❌ Error ejecución: {e}")
        return False

def main():
    signal.signal(signal.SIGINT, signal_handler)
    print("=" * 60)
    print("🤖 BOT DE TRADING IA PROFESIONAL - ANÁLISIS TOP-DOWN (M1/M5)")
    print("📈 Soporte / Resistencia + Bloqueo de Entradas en Zona de Riesgo")
    print("=" * 60)
    
    try:
        llm_client = LLMClient()
        market_data = MarketDataHandler(broker_name=Config.BROKER_NAME, account_type=Config.ACCOUNT_TYPE)
        
        if not market_data.connect(Config.EXNOVA_EMAIL, Config.EXNOVA_PASSWORD):
            print("❌ Error de conexión")
            return
            
        print(f"✅ Conectado. Balance inicial: ${market_data.get_balance():.2f}")
        feature_engineer = FeatureEngineer()
        otc_assets = ['EURUSD-OTC', 'GBPUSD-OTC', 'USDJPY-OTC', 'AUDUSD-OTC']
        
        while running:
            if not control.can_trade(market_data.get_balance()):
                time.sleep(30); continue
            
            print(f"\n🔍 Escaneando con Visión de Trader Profesional... ({datetime.now().strftime('%H:%M:%S')})")
            
            for asset in otc_assets:
                try:
                    # FETCH TOP-DOWN
                    m1_df = market_data.get_candles(asset, 60, 60) # M1 para gatillo
                    m5_df = market_data.get_candles(asset, 300, 100) # M5 para niveles S/R
                    
                    if m1_df.empty or m5_df.empty: continue
                    
                    m1_df = feature_engineer.add_technical_indicators(m1_df)
                    decision = analyze_opportunity_with_ai(llm_client, asset, m1_df, m5_df)
                    
                    if decision:
                        if execute_trade(market_data, decision):
                            time.sleep(30); break
                except Exception as e:
                    print(f"⚠️ Error en {asset}: {e}"); continue
            
            time.sleep(10)
    except Exception as e: print(f"❌ Crítico: {e}")
    finally: print("🛑 Bot finalizado.")

if __name__ == "__main__":
    main()
