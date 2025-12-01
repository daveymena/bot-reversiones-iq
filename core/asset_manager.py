import time
from data.market_data import MarketDataHandler
from strategies.math_models import MathModels
from strategies.smc_analysis import SMCAnalysis

class AssetManager:
    def __init__(self, market_data: MarketDataHandler):
        self.market_data = market_data
        self.current_asset = "EURUSD-OTC"
        self.current_type = "turbo" # turbo o binary
        self.min_profit = 70 # % mínimo para operar (reducido de 75 a 70)
        self.math_models = MathModels()
        self.smc_analysis = SMCAnalysis()
        
        # 🎯 MODO MULTI-DIVISA
        self.multi_asset_mode = True  # Monitorear múltiples activos
        self.monitored_assets = []  # Activos siendo monitoreados
        self.asset_scores = {}  # Scores de cada activo
        
        # Lista de activos OTC disponibles 24/7
        self.otc_assets = [
            "EURUSD-OTC", "GBPUSD-OTC", "USDJPY-OTC",
            "AUDUSD-OTC", "USDCAD-OTC", "EURJPY-OTC",
            "EURGBP-OTC", "GBPJPY-OTC", "AUDJPY-OTC"
        ]
        
        # Lista de activos normales (horario de mercado)
        self.normal_assets = [
            "EURUSD", "GBPUSD", "USDJPY",
            "AUDUSD", "USDCAD", "EURJPY"
        ]

    def find_best_asset(self, prefer_otc=True):
        """
        Busca el mejor activo disponible para operar.
        
        Args:
            prefer_otc: Si True, prioriza activos OTC (disponibles 24/7)
        """
        if not self.market_data.connected:
            print("⚠️ No conectado al broker")
            return None
        
        print("🔍 Escaneando mercado en busca de oportunidades...")
        
        try:
            # Obtener todos los activos con sus rentabilidades
            assets = self.market_data.get_open_assets(self.min_profit)
            
            if assets:
                # Filtrar por OTC si se prefiere
                if prefer_otc:
                    otc_assets = [a for a in assets if '-OTC' in a['name']]
                    if otc_assets:
                        best_asset = otc_assets[0]
                        print(f"💎 Mejor activo OTC: {best_asset['name']} (Profit: {best_asset['profit']:.0f}%)")
                        self.current_asset = best_asset['name']
                        self.current_type = best_asset['type']
                        return self.current_asset
                
                # Si no hay OTC o no se prefiere, usar el mejor disponible
                best_asset = assets[0]
                print(f"💎 Mejor activo: {best_asset['name']} (Profit: {best_asset['profit']:.0f}%)")
                self.current_asset = best_asset['name']
                self.current_type = best_asset['type']
                return self.current_asset
            
            # Si no se encontraron activos con get_open_assets, probar manualmente
            print("⚠️ No se encontraron activos con get_open_assets()")
            print("🔄 Probando activos OTC manualmente...")
            
            # Probar cada activo OTC
            for asset in self.otc_assets:
                try:
                    # Intentar obtener una vela para verificar si está disponible
                    df = self.market_data.get_candles(asset, 60, 1, time.time())
                    if not df.empty:
                        print(f"✅ Activo disponible: {asset}")
                        self.current_asset = asset
                        return asset
                except:
                    continue
            
            print("⚠️ No se encontraron activos OTC disponibles")
            
            # Como último recurso, probar activos normales
            print("🔄 Probando activos normales...")
            for asset in self.normal_assets:
                try:
                    df = self.market_data.get_candles(asset, 60, 1, time.time())
                    if not df.empty:
                        print(f"✅ Activo disponible: {asset}")
                        self.current_asset = asset
                        return asset
                except:
                    continue
            
            print("❌ No se encontraron activos operables")
            return None
            
        except Exception as e:
            print(f"❌ Error buscando activos: {e}")
            import traceback
            traceback.print_exc()
            return None

    def get_available_otc_assets(self, verbose=False):
        """
        Devuelve lista de activos OTC disponibles
        Verifica cada activo y solo incluye los que tienen datos
        """
        available = []
        unavailable = []
        
        if verbose:
            print("🔍 Verificando disponibilidad de activos...")
        
        for asset in self.otc_assets:
            try:
                df = self.market_data.get_candles(asset, 60, 1, time.time())
                if not df.empty:
                    available.append(asset)
                    if verbose:
                        print(f"   ✅ {asset} - Disponible")
                else:
                    unavailable.append(asset)
                    if verbose:
                        print(f"   ❌ {asset} - No disponible")
            except Exception as e:
                unavailable.append(asset)
                if verbose:
                    print(f"   ❌ {asset} - Error: {e}")
                continue
        
        if verbose:
            print(f"\n📊 Resumen:")
            print(f"   Disponibles: {len(available)}")
            print(f"   No disponibles: {len(unavailable)}")
        
        return available
    
    def update_available_assets(self):
        """
        Actualiza la lista de activos disponibles
        Debe llamarse periódicamente para mantener la lista actualizada
        """
        new_available = self.get_available_otc_assets(verbose=False)
        
        # Detectar cambios
        added = set(new_available) - set(self.monitored_assets)
        removed = set(self.monitored_assets) - set(new_available)
        
        if added:
            print(f"✅ Activos agregados: {', '.join(added)}")
        
        if removed:
            print(f"❌ Activos removidos: {', '.join(removed)}")
        
        # Actualizar lista
        self.monitored_assets = new_available
        
        return {
            'available': new_available,
            'added': list(added),
            'removed': list(removed),
            'total': len(new_available)
        }

    def check_asset_status(self):
        """Verifica si el activo actual sigue siendo válido."""
        try:
            df = self.market_data.get_candles(self.current_asset, 60, 1, time.time())
            return not df.empty
        except:
            return False
    
    def scan_best_opportunity(self, feature_engineer=None):
        """
        🎯 ESCANEA MÚLTIPLES ACTIVOS Y ELIGE EL MEJOR MOMENTO
        
        Analiza todos los activos monitoreados y devuelve el que tiene:
        - Mejor setup técnico
        - Mayor probabilidad de éxito
        - Momento óptimo para operar
        
        Returns:
            dict: {
                'asset': str,
                'score': float (0-100),
                'action': str (CALL/PUT),
                'confidence': float (0-1),
                'indicators': dict,
                'reasoning': str
            } o None si no hay oportunidades
        """
        if not self.market_data.connected:
            return None
        
        # Obtener lista de activos a monitorear
        if not self.monitored_assets:
            self.monitored_assets = self.get_available_otc_assets()
            if not self.monitored_assets:
                return None
        
        best_opportunity = None
        best_score = 0
        
        for asset in self.monitored_assets:
            try:
                # Obtener datos del activo
                df = self.market_data.get_candles(asset, 60, 100, time.time())
                if df.empty or len(df) < 50:
                    continue
                
                # Aplicar feature engineering si está disponible
                if feature_engineer:
                    df = feature_engineer.prepare_for_rl(df)
                
                # Analizar el activo
                analysis = self._analyze_asset_opportunity(df, asset)
                
                if analysis and analysis['score'] > best_score:
                    best_score = analysis['score']
                    best_opportunity = analysis
                    
            except Exception as e:
                continue
        
        # Solo retornar si encontró una oportunidad REAL (score >= 50) - Reducido para más operaciones
        if best_opportunity and best_opportunity['score'] >= 50:
            return best_opportunity
        
        return None
    
    def _analyze_asset_opportunity(self, df, asset):
        """
        Analiza un activo específico y calcula su score de oportunidad
        
        Returns:
            dict con análisis o None si no hay oportunidad
        """
        if df.empty or len(df) < 20:
            return None
        
        last = df.iloc[-1]
        score = 0
        signals = []
        action = None
        
        # 1. ANÁLISIS MATEMÁTICO AVANZADO (30 puntos)
        math_score = 0
        
        # A) Régimen de Mercado (Hurst)
        regime = self.math_models.analyze_market_regime(df)
        if regime['regime'] == 'TRENDING':
            signals.append(f"Régimen Tendencial (H={regime['hurst']:.2f})")
        elif regime['regime'] == 'MEAN_REVERTING':
            signals.append(f"Régimen Rango (H={regime['hurst']:.2f})")
            
        # B) Z-Score (Anomalías estadísticas)
        z_score = self.math_models.calculate_z_score(df['close'])
        if z_score < -2:
            math_score += 15
            signals.append(f"Z-Score Bajo ({z_score:.2f}) -> Rebote probable")
            if action is None: action = "CALL"
        elif z_score > 2:
            math_score += 15
            signals.append(f"Z-Score Alto ({z_score:.2f}) -> Corrección probable")
            if action is None: action = "PUT"
            
        # C) Fibonacci
        fib_levels = self.math_models.calculate_fibonacci_levels(df)
        fib_prox = self.math_models.get_fibonacci_proximity(last['close'], fib_levels)
        if fib_prox:
            math_score += 15
            signals.append(f"Soporte/Resistencia Fibo ({fib_prox['level']})")
            
        score += math_score

        # 2. RSI (20 puntos)
        rsi = last.get('rsi', 50)
        if rsi < 30:
            score += 20
            signals.append("RSI sobreventa fuerte")
            if regime['regime'] == 'MEAN_REVERTING': score += 10 # Bonificación en rango
            if action is None: action = "CALL"
        elif rsi < 40:
            score += 10
            signals.append("RSI sobreventa moderada")
            if action is None: action = "CALL"
        elif rsi > 70:
            score += 20
            signals.append("RSI sobrecompra fuerte")
            if regime['regime'] == 'MEAN_REVERTING': score += 10 # Bonificación en rango
            if action is None: action = "PUT"
        elif rsi > 60:
            score += 10
            signals.append("RSI sobrecompra moderada")
            if action is None: action = "PUT"
        
        # 3. MACD (15 puntos)
        macd = last.get('macd', 0)
        macd_signal = last.get('macd_signal', 0)
        if macd > macd_signal:
            score += 15
            signals.append("MACD Cruz Alcista")
            if regime['regime'] == 'TRENDING': score += 10 # Bonificación en tendencia
            if action is None: action = "CALL"
        elif macd < macd_signal:
            score += 15
            signals.append("MACD Cruz Bajista")
            if regime['regime'] == 'TRENDING': score += 10 # Bonificación en tendencia
            if action is None: action = "PUT"
        
        # 4. Bollinger Bands (20 puntos)
        if 'bb_low' in df.columns:
            bb_low = last.get('bb_low', 0)
            bb_high = last.get('bb_high', 0)
            price = last['close']
            
            if price <= bb_low:
                score += 20
                signals.append("Precio en BB inferior")
                if action is None: action = "CALL"
            elif price >= bb_high:
                score += 20
                signals.append("Precio en BB superior")
                if action is None: action = "PUT"
        
        # 5. Tendencia y Volatilidad (15 puntos)
        sma_20 = df['close'].tail(20).mean()
        sma_50 = df['close'].tail(50).mean() if len(df) >= 50 else sma_20
        
        if sma_20 > sma_50:
            score += 10
            signals.append("Tendencia Alcista")
        elif sma_20 < sma_50:
            score += 10
            signals.append("Tendencia Bajista")
            
        volatility = df['close'].tail(10).std()
        if volatility > df['close'].std():
            score += 5
            signals.append("Alta Volatilidad")
        
        # 6. SMC Analysis (Smart Money Concepts) - 20 puntos bonus
        try:
            smc_setup = self.smc_analysis.analyze_smc_setup(df)
            if smc_setup['valid_setup']:
                score += 20
                signals.append(f"SMC Setup: {', '.join(smc_setup['reasons'])}")
                # Sobrescribir acción si SMC tiene dirección clara
                if smc_setup['direction']:
                    action = smc_setup['direction']
        except:
            pass  # Si falla SMC, continuar con análisis normal
        
        # Solo retornar si hay una acción clara y score >= 50 (más permisivo)
        if action and score >= 50:
            return {
                'asset': asset,
                'score': score,
                'action': action,
                'confidence': min(score / 100, 0.95),
                'indicators': {
                    'rsi': rsi,
                    'macd': macd,
                    'price': last['close']
                },
                'reasoning': ", ".join(signals)
            }
        
        return None
