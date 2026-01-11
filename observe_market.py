"""
🔍 OBSERVADOR DE MERCADO EN TIEMPO REAL
Conecta a Exnova y analiza el comportamiento del mercado de opciones binarias
para identificar patrones, oportunidades y momentos óptimos de entrada
"""
import time
import pandas as pd
import numpy as np
from datetime import datetime
from data.market_data import MarketDataHandler
from strategies.technical import FeatureEngineer
from strategies.profitability_filters import ProfitabilityFilters
from core.asset_manager import AssetManager
import config

class MarketObserver:
    """Observa y analiza el mercado en tiempo real"""
    
    def __init__(self):
        # Inicializar con broker y tipo de cuenta desde config
        broker_name = config.Config.BROKER_NAME
        account_type = config.Config.ACCOUNT_TYPE
        
        self.market_data = MarketDataHandler(broker_name=broker_name, account_type=account_type)
        self.feature_engineer = FeatureEngineer()
        self.filters = ProfitabilityFilters()
        self.asset_manager = AssetManager(self.market_data)
        
        # Credenciales desde config
        self.email = config.Config.EXNOVA_EMAIL
        self.password = config.Config.EXNOVA_PASSWORD
        
        # Configuración de observación
        self.observation_interval = 10  # segundos entre observaciones
        self.assets_to_monitor = [
            "EURUSD-OTC", "GBPUSD-OTC", "USDJPY-OTC",
            "AUDUSD-OTC", "USDCAD-OTC", "EURJPY-OTC"
        ]
        
        # Almacenar observaciones
        self.observations = []
        self.opportunities_found = []
        
    def connect(self):
        """Conectar a Exnova"""
        print("=" * 80)
        print("🔌 CONECTANDO A EXNOVA...")
        print("=" * 80)
        
        if not self.email or not self.password:
            print("❌ Error: Credenciales no configuradas en .env")
            print("   Por favor configura EXNOVA_EMAIL y EXNOVA_PASSWORD en tu archivo .env")
            return False
        
        success = self.market_data.connect(self.email, self.password)
        if success:
            print("✅ Conectado exitosamente a Exnova")
            balance = self.market_data.get_balance()
            print(f"💰 Balance: ${balance:.2f}")
            return True
        else:
            print("❌ Error al conectar")
            return False
    
    def observe_asset(self, asset, timeframe=60, candles=100):
        """
        Observa un activo específico y analiza su comportamiento
        
        Returns:
            dict con análisis completo del activo
        """
        try:
            print(f"\n{'='*80}")
            print(f"📊 ANALIZANDO: {asset}")
            print(f"{'='*80}")
            
            # Obtener datos
            df = self.market_data.get_candles(asset, timeframe, candles, time.time())
            
            if df.empty:
                print(f"⚠️ No hay datos disponibles para {asset}")
                return None
            
            # Aplicar indicadores técnicos
            df = self.feature_engineer.prepare_for_rl(df)
            
            if df.empty or len(df) < 50:
                print(f"⚠️ Datos insuficientes después de aplicar indicadores")
                return None
            
            # Análisis del estado actual
            last = df.iloc[-1]
            prev = df.iloc[-2]
            
            current_price = last['close']
            price_change = ((current_price - prev['close']) / prev['close']) * 100
            
            # Determinar tendencia
            sma_20 = last.get('sma_20', current_price)
            sma_50 = last.get('sma_50', current_price)
            
            if sma_20 > sma_50 and current_price > sma_20:
                trend = "📈 ALCISTA"
                trend_strength = ((sma_20 - sma_50) / sma_50) * 100
            elif sma_20 < sma_50 and current_price < sma_20:
                trend = "📉 BAJISTA"
                trend_strength = ((sma_50 - sma_20) / sma_50) * 100
            else:
                trend = "➡️ LATERAL"
                trend_strength = 0
            
            # Análisis de indicadores
            rsi = last.get('rsi', 50)
            macd = last.get('macd', 0)
            macd_signal = last.get('macd_signal', 0)
            bb_high = last.get('bb_high', current_price)
            bb_low = last.get('bb_low', current_price)
            atr = last.get('atr', 0)
            
            # Volatilidad
            volatility = df['close'].tail(20).std()
            avg_volatility = df['close'].std()
            volatility_ratio = volatility / avg_volatility if avg_volatility > 0 else 1
            
            # Determinar señales
            signals = []
            signal_strength = 0
            recommended_action = "⏸️ ESPERAR"
            
            # Señal CALL (compra)
            if rsi < 30:
                signals.append("🟢 RSI en sobreventa")
                signal_strength += 25
                recommended_action = "📞 CALL"
            
            if current_price <= bb_low:
                signals.append("🟢 Precio en banda inferior")
                signal_strength += 20
                if recommended_action == "⏸️ ESPERAR":
                    recommended_action = "📞 CALL"
            
            if macd > macd_signal and macd > 0:
                signals.append("🟢 MACD alcista")
                signal_strength += 15
            
            # Señal PUT (venta)
            if rsi > 70:
                signals.append("🔴 RSI en sobrecompra")
                signal_strength += 25
                if recommended_action == "⏸️ ESPERAR":
                    recommended_action = "📉 PUT"
            
            if current_price >= bb_high:
                signals.append("🔴 Precio en banda superior")
                signal_strength += 20
                if recommended_action == "⏸️ ESPERAR":
                    recommended_action = "📉 PUT"
            
            if macd < macd_signal and macd < 0:
                signals.append("🔴 MACD bajista")
                signal_strength += 15
            
            # Mostrar análisis
            print(f"\n💹 PRECIO ACTUAL: {current_price:.5f}")
            print(f"📊 Cambio: {price_change:+.3f}%")
            print(f"\n🎯 TENDENCIA: {trend} (Fuerza: {trend_strength:.2f}%)")
            print(f"\n📈 INDICADORES:")
            print(f"   RSI: {rsi:.1f} {'🔥 SOBRECOMPRA' if rsi > 70 else '❄️ SOBREVENTA' if rsi < 30 else '⚖️ NEUTRAL'}")
            print(f"   MACD: {macd:.5f} {'📈' if macd > macd_signal else '📉'}")
            print(f"   Bollinger: {bb_low:.5f} ← {current_price:.5f} → {bb_high:.5f}")
            print(f"   ATR: {atr:.5f}")
            print(f"   Volatilidad: {volatility_ratio:.2f}x {'⚡ ALTA' if volatility_ratio > 1.5 else '😴 BAJA' if volatility_ratio < 0.7 else '✅ NORMAL'}")
            
            print(f"\n🎯 SEÑALES DETECTADAS:")
            if signals:
                for signal in signals:
                    print(f"   {signal}")
                print(f"\n💪 Fuerza de señal: {signal_strength}/100")
            else:
                print("   ⚠️ No hay señales claras")
            
            print(f"\n🎬 RECOMENDACIÓN: {recommended_action}")
            
            # Aplicar filtros de rentabilidad
            if recommended_action != "⏸️ ESPERAR":
                action_code = 1 if "CALL" in recommended_action else 2
                filter_result = self.filters.apply_all_filters(df, action_code, asset=asset)
                
                print(f"\n🔍 FILTROS DE RENTABILIDAD:")
                print(f"   Score: {filter_result['score']:.0f}/100")
                print(f"   Estado: {'✅ APROBADO' if filter_result['pass'] else '❌ RECHAZADO'}")
                
                if filter_result['reasons']:
                    print(f"\n   Razones:")
                    for reason in filter_result['reasons'][:5]:  # Mostrar solo las primeras 5
                        print(f"      {reason}")
                
                # Si pasa los filtros, es una oportunidad
                if filter_result['pass'] and signal_strength >= 40:
                    opportunity = {
                        'timestamp': datetime.now(),
                        'asset': asset,
                        'action': recommended_action,
                        'price': current_price,
                        'signal_strength': signal_strength,
                        'filter_score': filter_result['score'],
                        'rsi': rsi,
                        'trend': trend,
                        'volatility': volatility_ratio
                    }
                    self.opportunities_found.append(opportunity)
                    
                    print(f"\n{'🌟'*40}")
                    print(f"🎯 OPORTUNIDAD DETECTADA!")
                    print(f"   Activo: {asset}")
                    print(f"   Acción: {recommended_action}")
                    print(f"   Precio: {current_price:.5f}")
                    print(f"   Confianza: {signal_strength}%")
                    print(f"{'🌟'*40}")
            
            # Guardar observación
            observation = {
                'timestamp': datetime.now(),
                'asset': asset,
                'price': current_price,
                'trend': trend,
                'rsi': rsi,
                'macd': macd,
                'volatility': volatility_ratio,
                'signals': signals,
                'recommended_action': recommended_action,
                'signal_strength': signal_strength
            }
            self.observations.append(observation)
            
            return observation
            
        except Exception as e:
            print(f"❌ Error analizando {asset}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def scan_all_assets(self):
        """Escanea todos los activos monitoreados"""
        print("\n" + "="*80)
        print("🔍 ESCANEANDO TODOS LOS ACTIVOS...")
        print("="*80)
        
        results = []
        for asset in self.assets_to_monitor:
            result = self.observe_asset(asset)
            if result:
                results.append(result)
            time.sleep(2)  # Pequeña pausa entre activos
        
        return results
    
    def find_best_opportunity(self):
        """Encuentra la mejor oportunidad actual"""
        print("\n" + "="*80)
        print("🎯 BUSCANDO MEJOR OPORTUNIDAD...")
        print("="*80)
        
        results = self.scan_all_assets()
        
        if not results:
            print("⚠️ No se encontraron oportunidades")
            return None
        
        # Filtrar solo las que tienen señales fuertes
        strong_signals = [r for r in results if r['signal_strength'] >= 40]
        
        if not strong_signals:
            print("⚠️ No hay señales lo suficientemente fuertes")
            return None
        
        # Ordenar por fuerza de señal
        best = max(strong_signals, key=lambda x: x['signal_strength'])
        
        print(f"\n{'🏆'*40}")
        print(f"🥇 MEJOR OPORTUNIDAD:")
        print(f"   Activo: {best['asset']}")
        print(f"   Acción: {best['recommended_action']}")
        print(f"   Precio: {best['price']:.5f}")
        print(f"   Tendencia: {best['trend']}")
        print(f"   Fuerza: {best['signal_strength']}/100")
        print(f"   RSI: {best['rsi']:.1f}")
        print(f"{'🏆'*40}")
        
        return best
    
    def continuous_observation(self, duration_minutes=30):
        """
        Observación continua del mercado
        
        Args:
            duration_minutes: Duración de la observación en minutos
        """
        print("\n" + "="*80)
        print(f"👁️ INICIANDO OBSERVACIÓN CONTINUA ({duration_minutes} minutos)")
        print("="*80)
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        iteration = 0
        
        while time.time() < end_time:
            iteration += 1
            print(f"\n{'='*80}")
            print(f"🔄 ITERACIÓN #{iteration} - {datetime.now().strftime('%H:%M:%S')}")
            print(f"{'='*80}")
            
            # Buscar mejor oportunidad
            best = self.find_best_opportunity()
            
            # Mostrar resumen de oportunidades encontradas
            if self.opportunities_found:
                print(f"\n📊 RESUMEN DE OPORTUNIDADES:")
                print(f"   Total encontradas: {len(self.opportunities_found)}")
                
                # Agrupar por activo
                by_asset = {}
                for opp in self.opportunities_found:
                    asset = opp['asset']
                    if asset not in by_asset:
                        by_asset[asset] = []
                    by_asset[asset].append(opp)
                
                print(f"\n   Por activo:")
                for asset, opps in by_asset.items():
                    avg_strength = np.mean([o['signal_strength'] for o in opps])
                    print(f"      {asset}: {len(opps)} oportunidades (fuerza promedio: {avg_strength:.0f})")
            
            # Esperar antes de la siguiente iteración
            print(f"\n⏳ Esperando {self.observation_interval} segundos...")
            time.sleep(self.observation_interval)
        
        print(f"\n{'='*80}")
        print(f"✅ OBSERVACIÓN COMPLETADA")
        print(f"{'='*80}")
        self.show_summary()
    
    def show_summary(self):
        """Muestra un resumen de todas las observaciones"""
        if not self.observations:
            print("⚠️ No hay observaciones para mostrar")
            return
        
        print(f"\n{'='*80}")
        print(f"📊 RESUMEN DE OBSERVACIONES")
        print(f"{'='*80}")
        
        print(f"\nTotal de observaciones: {len(self.observations)}")
        print(f"Oportunidades encontradas: {len(self.opportunities_found)}")
        
        # Análisis por activo
        print(f"\n📈 ANÁLISIS POR ACTIVO:")
        by_asset = {}
        for obs in self.observations:
            asset = obs['asset']
            if asset not in by_asset:
                by_asset[asset] = []
            by_asset[asset].append(obs)
        
        for asset, obs_list in by_asset.items():
            avg_rsi = np.mean([o['rsi'] for o in obs_list])
            avg_volatility = np.mean([o['volatility'] for o in obs_list])
            avg_strength = np.mean([o['signal_strength'] for o in obs_list])
            
            print(f"\n   {asset}:")
            print(f"      Observaciones: {len(obs_list)}")
            print(f"      RSI promedio: {avg_rsi:.1f}")
            print(f"      Volatilidad promedio: {avg_volatility:.2f}x")
            print(f"      Fuerza de señal promedio: {avg_strength:.0f}/100")
        
        # Mejores oportunidades
        if self.opportunities_found:
            print(f"\n🌟 TOP 5 MEJORES OPORTUNIDADES:")
            sorted_opps = sorted(self.opportunities_found, 
                                key=lambda x: x['signal_strength'], 
                                reverse=True)[:5]
            
            for i, opp in enumerate(sorted_opps, 1):
                print(f"\n   #{i}:")
                print(f"      Activo: {opp['asset']}")
                print(f"      Acción: {opp['action']}")
                print(f"      Hora: {opp['timestamp'].strftime('%H:%M:%S')}")
                print(f"      Fuerza: {opp['signal_strength']}/100")
                print(f"      RSI: {opp['rsi']:.1f}")


def main():
    """Función principal"""
    observer = MarketObserver()
    
    # Conectar
    if not observer.connect():
        print("❌ No se pudo conectar. Verifica tus credenciales en .env")
        return
    
    print("\n" + "="*80)
    print("🎯 OPCIONES DE OBSERVACIÓN:")
    print("="*80)
    print("1. Escaneo único de todos los activos")
    print("2. Observación continua (30 minutos)")
    print("3. Análisis de un activo específico")
    print("4. Buscar mejor oportunidad ahora")
    
    try:
        choice = input("\nElige una opción (1-4): ").strip()
        
        if choice == "1":
            observer.scan_all_assets()
            observer.show_summary()
        
        elif choice == "2":
            duration = input("¿Cuántos minutos observar? (default: 30): ").strip()
            duration = int(duration) if duration else 30
            observer.continuous_observation(duration)
        
        elif choice == "3":
            print("\nActivos disponibles:")
            for i, asset in enumerate(observer.assets_to_monitor, 1):
                print(f"{i}. {asset}")
            
            asset_choice = input("\nElige un activo (1-6): ").strip()
            if asset_choice.isdigit() and 1 <= int(asset_choice) <= 6:
                asset = observer.assets_to_monitor[int(asset_choice) - 1]
                observer.observe_asset(asset)
            else:
                print("❌ Opción inválida")
        
        elif choice == "4":
            observer.find_best_opportunity()
        
        else:
            print("❌ Opción inválida")
    
    except KeyboardInterrupt:
        print("\n\n⚠️ Observación interrumpida por el usuario")
        observer.show_summary()
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
