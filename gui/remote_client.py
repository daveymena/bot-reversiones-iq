"""
Cliente para conectar la GUI local con el backend remoto en Easypanel
"""
import requests
import json
import threading
import websocket
from typing import Callable, Optional
import time


class RemoteBotClient:
    """Cliente que conecta con el backend remoto"""
    
    def __init__(self, backend_url: str):
        """
        Args:
            backend_url: URL del backend (ej: https://tu-bot.easypanel.host)
        """
        self.backend_url = backend_url.rstrip('/')
        self.ws_url = backend_url.replace('https://', 'wss://').replace('http://', 'ws://')
        self.session_id = None
        self.ws = None
        self.ws_thread = None
        self.connected = False
        self.on_message_callback = None
        
    def connect_broker(self, broker: str, email: str, password: str, account_type: str) -> dict:
        """Conectar al broker a través del backend"""
        try:
            response = requests.post(
                f"{self.backend_url}/api/connect",
                json={
                    "broker": broker,
                    "email": email,
                    "password": password,
                    "account_type": account_type,
                    "session_id": self.session_id
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.session_id = data.get('session_id')
                self.connected = True
                return data
            else:
                return {"success": False, "message": f"Error: {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "message": f"Error de conexión: {str(e)}"}
    
    def disconnect_broker(self) -> dict:
        """Desconectar del broker"""
        try:
            if not self.session_id:
                return {"success": False, "message": "No hay sesión activa"}
            
            response = requests.post(
                f"{self.backend_url}/api/disconnect",
                json={"session_id": self.session_id},
                timeout=10
            )
            
            if response.status_code == 200:
                self.connected = False
                self.disconnect_websocket()
                return response.json()
            else:
                return {"success": False, "message": f"Error: {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def get_balance(self) -> float:
        """Obtener balance actual"""
        try:
            if not self.session_id:
                return 0.0
            
            response = requests.post(
                f"{self.backend_url}/api/balance",
                json={"session_id": self.session_id},
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json().get('balance', 0.0)
            return 0.0
            
        except Exception as e:
            print(f"Error obteniendo balance: {e}")
            return 0.0
    
    def get_candles(self, asset: str, timeframe: int = 60, count: int = 100) -> list:
        """Obtener velas históricas"""
        try:
            if not self.session_id:
                return []
            
            response = requests.get(
                f"{self.backend_url}/api/candles/{asset}",
                params={
                    "session_id": self.session_id,
                    "timeframe": timeframe,
                    "count": count
                },
                timeout=15
            )
            
            if response.status_code == 200:
                return response.json().get('candles', [])
            return []
            
        except Exception as e:
            print(f"Error obteniendo velas: {e}")
            return []
    
    def get_assets(self) -> list:
        """Obtener activos disponibles"""
        try:
            if not self.session_id:
                return []
            
            response = requests.get(
                f"{self.backend_url}/api/assets",
                params={"session_id": self.session_id},
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json().get('assets', [])
            return []
            
        except Exception as e:
            print(f"Error obteniendo activos: {e}")
            return []
    
    def execute_trade(self, asset: str, direction: str, amount: float, duration: int) -> dict:
        """Ejecutar operación manual"""
        try:
            if not self.session_id:
                return {"success": False, "message": "No hay sesión activa"}
            
            response = requests.post(
                f"{self.backend_url}/api/trade",
                json={
                    "asset": asset,
                    "direction": direction,
                    "amount": amount,
                    "duration": duration,
                    "session_id": self.session_id
                },
                timeout=15
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"success": False, "message": f"Error: {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def start_bot(self) -> dict:
        """Iniciar bot automático"""
        try:
            if not self.session_id:
                return {"success": False, "message": "No hay sesión activa"}
            
            response = requests.post(
                f"{self.backend_url}/api/bot/start",
                json={"session_id": self.session_id},
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"success": False, "message": f"Error: {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def stop_bot(self) -> dict:
        """Detener bot automático"""
        try:
            if not self.session_id:
                return {"success": False, "message": "No hay sesión activa"}
            
            response = requests.post(
                f"{self.backend_url}/api/bot/stop",
                json={"session_id": self.session_id},
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"success": False, "message": f"Error: {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def change_timeframe(self, timeframe: int) -> dict:
        """Cambiar timeframe del gráfico"""
        try:
            if not self.session_id:
                return {"success": False, "message": "No hay sesión activa"}
            
            response = requests.post(
                f"{self.backend_url}/api/timeframe",
                json={
                    "timeframe": timeframe,
                    "session_id": self.session_id
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"success": False, "message": f"Error: {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def connect_websocket(self, on_message: Callable):
        """Conectar WebSocket para recibir actualizaciones en tiempo real"""
        if not self.session_id:
            print("Error: No hay sesión activa")
            return
        
        self.on_message_callback = on_message
        
        def on_ws_message(ws, message):
            try:
                data = json.loads(message)
                if self.on_message_callback:
                    self.on_message_callback(data)
            except Exception as e:
                print(f"Error procesando mensaje WS: {e}")
        
        def on_ws_error(ws, error):
            print(f"WebSocket error: {error}")
        
        def on_ws_close(ws, close_status_code, close_msg):
            print("WebSocket cerrado")
        
        def on_ws_open(ws):
            print("WebSocket conectado")
        
        def run_ws():
            ws_url = f"{self.ws_url}/ws/{self.session_id}"
            self.ws = websocket.WebSocketApp(
                ws_url,
                on_message=on_ws_message,
                on_error=on_ws_error,
                on_close=on_ws_close,
                on_open=on_ws_open
            )
            self.ws.run_forever()
        
        self.ws_thread = threading.Thread(target=run_ws, daemon=True)
        self.ws_thread.start()
    
    def disconnect_websocket(self):
        """Desconectar WebSocket"""
        if self.ws:
            self.ws.close()
            self.ws = None
    
    def is_connected(self) -> bool:
        """Verificar si está conectado"""
        return self.connected and self.session_id is not None
    
    def get_status(self) -> dict:
        """Obtener estado del backend"""
        try:
            response = requests.get(f"{self.backend_url}/", timeout=5)
            if response.status_code == 200:
                return response.json()
            return {"status": "error"}
        except Exception as e:
            return {"status": "offline", "error": str(e)}
