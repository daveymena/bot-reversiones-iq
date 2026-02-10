import pandas as pd
import time
from config import Config

# Importar librerías de brokers
try:
    from iqoptionapi.stable_api import IQ_Option
except ImportError:
    IQ_Option = None

try:
    from exnovaapi.stable_api import Exnova
except ImportError:
    Exnova = None

class MarketDataHandler:
    def __init__(self, broker_name="iq", account_type="PRACTICE"):
        self.broker_name = broker_name
        self.account_type = account_type
        self.api = None
        self.connected = False

    def connect(self, email, password):
        """Conecta al broker seleccionado."""
        print(f"Conectando a {self.broker_name.upper()} ({self.account_type})...")
        
        try:
            if self.broker_name == "iq":
                if IQ_Option is None:
                    print("Error: Librería iqoptionapi no instalada.")
                    return False
                    
                self.api = IQ_Option(email, password)
                check, reason = self.api.connect()
                
                if check:
                    # Cambiar a cuenta PRACTICE o REAL
                    self.api.change_balance(self.account_type)
                    time.sleep(1)  # Esperar a que se aplique el cambio
                    print(f"✅ Conectado a IQ OPTION ({self.account_type})")
                    self.connected = True
                else:
                    print(f"❌ Error de conexión IQ: {reason}")
                    self.connected = False
            
            elif self.broker_name == "exnova":
                if Exnova is None:
                    print("Error: Librería exnovaapi no encontrada.")
                    return False
                    
                # Exnova recibe account_type en constructor
                self.api = Exnova(email, password, active_account_type=self.account_type)
                check, reason = self.api.connect()
                
                if check:
                    # Verificar websocket
                    if self.api.check_connect():
                        # Cambiar a cuenta PRACTICE o REAL
                        self.api.change_balance(self.account_type)
                        time.sleep(1)  # Esperar a que se aplique el cambio
                        print(f"✅ Conectado a EXNOVA ({self.account_type})")
                        # Actualizar códigos de activos
                        try:
                            self.api.update_ACTIVES_OPCODE()
                        except:
                            pass
                        self.connected = True
                    else:
                        print("❌ WebSocket no conectado")
                        self.connected = False
                else:
                    print(f"❌ Error de conexión Exnova: {reason}")
                    self.connected = False
            
            else:
                print(f"Broker desconocido: {self.broker_name}")
                return False

        except Exception as e:
            print(f"❌ Excepción durante conexión: {e}")
            import traceback
            traceback.print_exc()
            self.connected = False
            return False
            
        return self.connected

    def get_candles(self, asset, timeframe, num_candles, end_time=None):
        """Obtiene velas históricas del broker activo."""
        if not self.connected or not self.api:
            return pd.DataFrame()

        try:
            if end_time is None:
                end_time = time.time()
            
            if self.broker_name == "exnova":
                try:
                    # Intentar con 4 argumentos
                    candles = self.api.get_candles(asset, timeframe, num_candles, end_time)
                except TypeError:
                    # Fallback a 3 argumentos si falla
                    print(f"⚠️ Exnova get_candles falló con 4 args, intentando con 3...")
                    candles = self.api.get_candles(asset, timeframe, num_candles)
            else:
                candles = self.api.get_candles(asset, timeframe, num_candles, end_time)
        except Exception as e:
            print(f"Error obteniendo velas: {e}")
            return pd.DataFrame()
        
        if not candles:
            return pd.DataFrame()
            
        # Error handling for cases where the API returns a dict with an error message
        if isinstance(candles, dict):
            if 'message' in candles:
                print(f"⚠️ API Error en get_candles ({asset}): {candles['message']}")
            else:
                print(f"⚠️ API devolvió formato inesperado en get_candles ({asset}): {candles}")
            return pd.DataFrame()
            
        df = pd.DataFrame(candles)
        if not df.empty:
            # Estandarizar columnas
            rename_map = {
                'max': 'high', 
                'min': 'low', 
                'open': 'open', 
                'close': 'close', 
                'volume': 'volume',
                'from': 'timestamp'
            }
            df.rename(columns=rename_map, inplace=True)
            
            # Convertir timestamp
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
                df.set_index('timestamp', inplace=True)
            
            cols = ['open', 'high', 'low', 'close', 'volume']
            for col in cols:
                if col not in df.columns:
                    df[col] = 0.0
            
            df = df[cols].apply(pd.to_numeric, errors='coerce')
        
        return df

    def get_balance(self):
        """Devuelve el balance de la cuenta."""
        if self.connected and self.api:
            try:
                return self.api.get_balance()
            except:
                return 0.0
        return 0.0

    def get_current_price(self, asset):
        """
        Obtiene el precio actual del activo.
        Intenta obtener la vela más reciente posible.
        """
        if not self.connected or not self.api:
            return 0.0
            
        try:
            # Pedir 1 vela actual del timeframe configurado para asegurar consistencia
            candles = self.api.get_candles(asset, 60, 1, time.time())
            
            if candles and isinstance(candles, list) and len(candles) > 0:
                last_candle = candles[-1]
                return float(last_candle['close'])
            
            # Fallback a diccionario si devuelve dict
            if isinstance(candles, dict) and 'close' in candles:
                return float(candles['close'])
                
        except Exception as e:
            print(f"[DEBUG] Error obteniendo precio actual: {e}")
        
        return 0.0

    def get_current_price(self, asset):
        """
        Obtiene el precio actual del activo.
        Intenta obtener la vela más reciente posible.
        """
        if not self.connected or not self.api:
            return 0.0
            
        try:
            # Pedir 1 vela actual del timeframe configurado para asegurar consistencia
            candles = self.api.get_candles(asset, 60, 1, time.time())
            
            if candles and isinstance(candles, list) and len(candles) > 0:
                last_candle = candles[-1]
                return float(last_candle['close'])
            
            # Fallback a diccionario si devuelve dict
            if isinstance(candles, dict) and 'close' in candles:
                return float(candles['close'])
                
        except Exception as e:
            print(f"[DEBUG] Error obteniendo precio actual: {e}")
        
        return 0.0

    def get_open_assets(self, min_profit=75):
        """
        Escanea activos disponibles y devuelve los que están abiertos 
        y tienen un profit mayor a min_profit.
        """
        if not self.connected:
            return []

        open_assets = []
        try:
            # Obtener rentabilidad (profit)
            profits = self.api.get_all_profit()
            
            if not profits:
                return []
            
            for asset_name, data in profits.items():
                profit = 0
                if isinstance(data, dict):
                    if 'turbo' in data:
                        profit = data['turbo']
                    elif 'binary' in data:
                        profit = data['binary']
                else:
                    # Si data es un número directamente
                    profit = data
                
                if profit >= (min_profit / 100.0):
                    open_assets.append({
                        'name': asset_name,
                        'profit': profit * 100,
                        'type': 'turbo' if 'turbo' in str(data) else 'binary'
                    })
                    
        except Exception as e:
            print(f"Error escaneando activos: {e}")
        
        # Ordenar por rentabilidad descendente
        open_assets.sort(key=lambda x: x['profit'], reverse=True)
        return open_assets
    
    def is_really_connected(self):
        """
        Verifica si la conexión está REALMENTE activa
        (no solo la variable self.connected)
        """
        if not self.connected or not self.api:
            return False
        
        try:
            if self.broker_name == "exnova":
                # Verificar websocket
                return self.api.check_connect()
            elif self.broker_name == "iq":
                # Verificar conexión de IQ Option
                try:
                    # Intentar obtener balance como prueba
                    balance = self.api.get_balance()
                    return balance is not None
                except:
                    return False
        except Exception as e:
            print(f"[DEBUG] Error verificando conexión: {e}")
            return False
        
        return False
    
    def reconnect(self, email, password):
        """
        Intenta reconectar al broker
        """
        print(f"🔄 Intentando reconectar a {self.broker_name.upper()}...")
        
        # Marcar como desconectado
        self.connected = False
        
        # Esperar un momento
        time.sleep(2)
        
        # Intentar conectar de nuevo
        return self.connect(email, password)
    
    def buy(self, asset, amount, action, duration):
        """
        Ejecuta una operación buscando la mejor vía disponible (Digital -> Binaria).
        Si falla, intenta automáticamente la variante OTC/Normal contraria.
        """
        if not self.connected or not self.api:
            return False, "No conectado"

        # 1. Intento Principal con el nombre original
        success, result = self._execute_buy_logic(asset, amount, action, duration)
        if success:
            return True, result
            
        # Si falló, analizar si vale la pena reintentar con OTC/Normal
        print(f"⚠️ Falló intento principal en {asset}: {result}")
        
        # Generar nombre alternativo
        if asset.endswith("-OTC"):
            alt_asset = asset.replace("-OTC", "") # Pruebo Normal
        else:
            alt_asset = asset + "-OTC" # Pruebo OTC
            
        print(f"🔄 Intentando FALLBACK automático con: {alt_asset} ...")
        
        # 2. Intento Secundario (Fallback)
        success_alt, result_alt = self._execute_buy_logic(alt_asset, amount, action, duration)
        
        if success_alt:
            print(f"✅ ÉXITO en Fallback: {alt_asset}")
            return True, result_alt
        else:
            return False, f"Falló en {asset} ({result}) y en {alt_asset} ({result_alt})"

    def _execute_buy_logic(self, asset, amount, action, duration):
        """Lógica interna de compra (Digital -> Binaria)"""
        try:
            # A) Intentar Digital (Mejor Payout)
            if duration in [1, 5, 15]:
                try:
                    # Verificar payout digital (proxy de disponibilidad)
                    self.api.subscribe_strike_list(asset, duration)
                    payout = self.api.get_digital_to_payout(asset, duration)
                    
                    if payout and payout > 0:
                        print(f"📦 Digital disponible en {asset} (Payout: {payout}%)")
                        check, order_id = self.api.buy_digital_spot(asset, amount, action, duration)
                        if check:
                            return True, order_id
                    else:
                        print(f"⚠️ Digital no disponible/payout 0 en {asset}")
                except Exception as e:
                    print(f"⚠️ Error check Digital: {e}")

            # B) Intentar Binaria/Turbo (Fallback estándar)
            # Turbo es 1-5 min, Binaria es >15. La API usually maneja esto con 'buy'
            print(f"📦 Intentando Binaria/Turbo en {asset}...")
            check, order_id = self.api.buy(amount, asset, action, duration)
            
            if check:
                return True, order_id
            else:
                return False, f"Rechazado: {order_id}"
                
        except Exception as e:
            return False, str(e)

    def disconnect(self):
        """Desconecta del broker"""
        if self.api:
            try:
                if hasattr(self.api, 'close'):
                    self.api.close()
            except:
                pass
        
        self.connected = False
        self.api = None
        print(f"🔌 Desconectado de {self.broker_name.upper()}")
