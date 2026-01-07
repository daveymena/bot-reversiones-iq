"""
Cliente API para conectar GUI de escritorio con backend en Easypanel
"""
import requests
import json
from typing import Optional, Dict, List
from PySide6.QtCore import QObject, Signal, QThread
from PySide6.QtWebSockets import QWebSocket
from PySide6.QtCore import QUrl

class APIClient(QObject):
    """Cliente para comunicarse con el backend"""
    
    # Señales para actualizar GUI
    connection_changed = Signal(bool)
    balance_updated = Signal(float)
    trade_executed = Signal(dict)
    log_message = Signal(str)
    status_updated = Signal(dict)
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        super().__init__()
        self.base_url = base_url
        self.websocket = None
        self.connected = False
    
    def set_backend_url(self, url: str):
        """Cambiar URL del backend"""
        self.base_url = url.rstrip('/')
        self.log_message.emit(f"🔗 Backend configurado: {self.base_url}")
    
    # ============= REST API =============
    
    def connect_broker(self, email: str = None, password: str = None, 
                       broker: str = "exnova", account_type: str = "PRACTICE") -> bool:
        """Conectar al broker a través del backend"""
        try:
            # Si se proporcionan credenciales, enviarlas
            payload = None
            if email and password:
                payload = {
                    "email": email,
                    "password": password,
                    "broker": broker,
                    "account_type": account_type
                }
            
            response = requests.post(
                f"{self.base_url}/connect", 
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            self.connected = data.get("status") == "connected"
            self.connection_changed.emit(self.connected)
            self.log_message.emit(f"✅ Conectado a {data.get('broker')} ({data.get('account_type')})")
            
            # Conectar WebSocket
            self._connect_websocket()
            
            return True
        except Exception as e:
            self.log_message.emit(f"❌ Error al conectar: {e}")
            return False
    
    def disconnect_broker(self) -> bool:
        """Desconectar del broker"""
        try:
            response = requests.post(f"{self.base_url}/disconnect", timeout=5)
            response.raise_for_status()
            
            self.connected = False
            self.connection_changed.emit(False)
            self.log_message.emit("🔌 Desconectado del broker")
            
            # Desconectar WebSocket
            if self.websocket:
                self.websocket.close()
            
            return True
        except Exception as e:
            self.log_message.emit(f"❌ Error al desconectar: {e}")
            return False
    
    def get_balance(self) -> Optional[float]:
        """Obtener balance actual"""
        try:
            response = requests.get(f"{self.base_url}/balance", timeout=5)
            response.raise_for_status()
            data = response.json()
            
            balance = data.get("balance", 0)
            self.balance_updated.emit(balance)
            return balance
        except Exception as e:
            self.log_message.emit(f"❌ Error al obtener balance: {e}")
            return None
    
    def get_assets(self) -> List[str]:
        """Obtener lista de activos disponibles"""
        try:
            response = requests.get(f"{self.base_url}/assets", timeout=5)
            response.raise_for_status()
            data = response.json()
            return data.get("assets", [])
        except Exception as e:
            self.log_message.emit(f"❌ Error al obtener activos: {e}")
            return []
    
    def start_trading(self) -> bool:
        """Iniciar trading automático"""
        try:
            response = requests.post(f"{self.base_url}/start", timeout=5)
            response.raise_for_status()
            
            self.log_message.emit("🚀 Trading automático iniciado")
            return True
        except Exception as e:
            self.log_message.emit(f"❌ Error al iniciar trading: {e}")
            return False
    
    def stop_trading(self) -> bool:
        """Detener trading automático"""
        try:
            response = requests.post(f"{self.base_url}/stop", timeout=5)
            response.raise_for_status()
            
            self.log_message.emit("⏸️ Trading automático detenido")
            return True
        except Exception as e:
            self.log_message.emit(f"❌ Error al detener trading: {e}")
            return False
    
    def get_status(self) -> Optional[Dict]:
        """Obtener estado completo del bot"""
        try:
            response = requests.get(f"{self.base_url}/status", timeout=5)
            response.raise_for_status()
            data = response.json()
            
            self.status_updated.emit(data)
            return data
        except Exception as e:
            return None
    
    def update_config(self, config: Dict) -> bool:
        """Actualizar configuración del bot"""
        try:
            response = requests.post(
                f"{self.base_url}/config",
                json=config,
                timeout=5
            )
            response.raise_for_status()
            
            self.log_message.emit("⚙️ Configuración actualizada")
            return True
        except Exception as e:
            self.log_message.emit(f"❌ Error al actualizar config: {e}")
            return False
    
    def get_history(self, limit: int = 50) -> List[Dict]:
        """Obtener historial de operaciones"""
        try:
            response = requests.get(
                f"{self.base_url}/history",
                params={"limit": limit},
                timeout=5
            )
            response.raise_for_status()
            data = response.json()
            return data.get("trades", [])
        except Exception as e:
            self.log_message.emit(f"❌ Error al obtener historial: {e}")
            return []
    
    # ============= WEBSOCKET =============
    
    def _connect_websocket(self):
        """Conectar WebSocket para actualizaciones en tiempo real"""
        ws_url = self.base_url.replace("http://", "ws://").replace("https://", "wss://")
        
        self.websocket = QWebSocket()
        self.websocket.connected.connect(self._on_ws_connected)
        self.websocket.disconnected.connect(self._on_ws_disconnected)
        self.websocket.textMessageReceived.connect(self._on_ws_message)
        
        self.websocket.open(QUrl(f"{ws_url}/ws"))
    
    def _on_ws_connected(self):
        """Callback cuando WebSocket se conecta"""
        self.log_message.emit("🔗 WebSocket conectado")
    
    def _on_ws_disconnected(self):
        """Callback cuando WebSocket se desconecta"""
        self.log_message.emit("🔌 WebSocket desconectado")
    
    def _on_ws_message(self, message: str):
        """Callback cuando llega un mensaje por WebSocket"""
        try:
            data = json.loads(message)
            msg_type = data.get("type")
            
            if msg_type == "connection":
                status = data.get("status") == "connected"
                self.connection_changed.emit(status)
            
            elif msg_type == "balance":
                balance = data.get("balance")
                self.balance_updated.emit(balance)
            
            elif msg_type == "trade":
                self.trade_executed.emit(data)
                self.log_message.emit(f"📊 Trade: {data.get('direction')} {data.get('asset')}")
            
            elif msg_type == "log":
                self.log_message.emit(data.get("message", ""))
            
            elif msg_type == "status":
                self.status_updated.emit(data)
        
        except Exception as e:
            print(f"Error procesando mensaje WS: {e}")


class StatusPoller(QThread):
    """Thread para hacer polling del estado del bot"""
    
    status_received = Signal(dict)
    
    def __init__(self, api_client: APIClient, interval: int = 2000):
        super().__init__()
        self.api_client = api_client
        self.interval = interval / 1000  # Convertir a segundos
        self.running = True
    
    def run(self):
        """Loop de polling"""
        import time
        
        while self.running:
            status = self.api_client.get_status()
            if status:
                self.status_received.emit(status)
            
            time.sleep(self.interval)
    
    def stop(self):
        """Detener polling"""
        self.running = False
