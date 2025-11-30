"""
Cliente API para conectar la GUI con el backend
"""
import requests
import websockets
import asyncio
import json
from typing import Optional, Callable

class TradingBotClient:
    """Cliente para conectarse al backend del bot"""
    
    def __init__(self, server_url: str = "http://localhost:8000"):
        self.server_url = server_url
        self.ws_url = server_url.replace("http", "ws") + "/ws"
        self.ws_connection: Optional[websockets.WebSocketClientProtocol] = None
        self.callbacks = {}
        
    def start_bot(self):
        """Iniciar el bot en el servidor"""
        response = requests.post(f"{self.server_url}/api/start")
        return response.json()
    
    def stop_bot(self):
        """Detener el bot"""
        response = requests.post(f"{self.server_url}/api/stop")
        return response.json()
    
    def pause_bot(self):
        """Pausar el bot"""
        response = requests.post(f"{self.server_url}/api/pause")
        return response.json()
    
    def resume_bot(self):
        """Reanudar el bot"""
        response = requests.post(f"{self.server_url}/api/resume")
        return response.json()
    
    def get_status(self):
        """Obtener estado del bot"""
        response = requests.get(f"{self.server_url}/api/status")
        return response.json()
    
    async def connect_websocket(self, on_message: Callable):
        """Conectar al WebSocket para recibir actualizaciones en tiempo real"""
        async with websockets.connect(self.ws_url) as websocket:
            self.ws_connection = websocket
            async for message in websocket:
                data = json.loads(message)
                on_message(data)
    
    def register_callback(self, event_type: str, callback: Callable):
        """Registrar callback para eventos específicos"""
        self.callbacks[event_type] = callback
