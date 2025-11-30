import pandas as pd
import time
from config import Config

# NO importar brokers aquí para evitar conflictos de websocket
# Se importarán dinámicamente cuando se necesiten

class MarketDataHandler:
    def __init__(self, broker_name="iq", account_type="PRACTICE"):
        self.broker_name = broker_name
        self.account_type = account_type
        self.api = None
        self.connected = False
        self._broker_module = None  # Módulo del broker cargado dinámicamente

    def _load_broker_module(self):
        """
        Carga el módulo de Exnova (único broker soportado)
        """
        if self._broker_module is not None:
            return self._broker_module
            
        try:
            print("📦 Cargando módulo Exnova...")
            from exnovaapi.stable_api import Exnova
            self._broker_module = Exnova
            print("✅ Módulo Exnova cargado")
            return self._broker_module
            
        except ImportError as e:
            print(f"❌ Error importando Exnova: {e}")
            return None
        except Exception as e:
            print(f"❌ Error inesperado cargando broker: {e}")
            import traceback
            traceback.print_exc()
            return None

    def connect(self, email, password):
        """Conecta al broker seleccionado."""
        print(f"Conectando a {self.broker_name.upper()} ({self.account_type})...")
        
        # Cargar módulo del broker dinámicamente
        BrokerClass = self._load_broker_module()
        if BrokerClass is None:
            print(f"❌ No se pudo cargar el módulo del broker {self.broker_name}")
            return False
        
        try:
            # Exnova recibe account_type en constructor
            self.api = BrokerClass(email, password, active_account_type=self.account_type)
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
            candles = self.api.get_candles(asset, timeframe, num_candles, end_time)
        except Exception as e:
            print(f"Error obteniendo velas: {e}")
            return pd.DataFrame()
        
        if not candles:
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
