"""
Interfaz Cliente para el Bot de Trading
Versión que se conecta al servidor remoto en EasyPanel
"""
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from datetime import datetime
import sys
sys.path.insert(0, '.')

from backend.api.client import TradingBotClient
from gui.modern_main_window import ModernMainWindow

class ModernMainWindowClient(ModernMainWindow):
    """
    Versión Cliente de la GUI
    Hereda de ModernMainWindow pero usa TradingBotClient para conectarse al servidor
    """
    
    def __init__(self, server_url="http://localhost:8000"):
        self.server_url = server_url
        self.api_client = TradingBotClient(server_url)
        
        # Crear un trader "mock" para compatibilidad con la GUI base
        # La GUI espera un objeto trader, así que creamos uno dummy
        class DummyTrader(QThread):
            def __init__(self):
                super().__init__()
                self.running = False
                self.paused = False
                # Crear signals compatibles
                from PySide6.QtCore import Signal
                class Signals(QObject):
                    log_message = Signal(str)
                    error_message = Signal(str)
                    balance_update = Signal(float)
                    chart_update = Signal(float, float)
                    trade_signal = Signal(str, str)
                    trading_stats = Signal(int, int, float)
                    indicators_update = Signal(dict)
                
                self.signals = Signals()
            
            def run(self):
                pass
        
        dummy_trader = DummyTrader()
        
        # Inicializar la GUI base con el trader dummy
        super().__init__(dummy_trader)
        
        # Sobrescribir título para indicar modo cliente
        self.setWindowTitle(f"🤖 Trading Bot Pro - Client Mode ({server_url})")
        
        # Iniciar polling del servidor
        self.start_server_polling()
    
    def start_server_polling(self):
        """Inicia polling periódico al servidor para actualizar la GUI"""
        self.poll_timer = QTimer()
        self.poll_timer.timeout.connect(self.update_from_server)
        self.poll_timer.start(2000)  # Actualizar cada 2 segundos
    
    def update_from_server(self):
        """Obtiene estado del servidor y actualiza la GUI"""
        try:
            status = self.api_client.get_status()
            if status:
                # Actualizar balance
                if 'balance' in status:
                    self.update_balance_safe(status['balance'])
                
                # Actualizar stats
                if 'profit' in status:
                    wins = status.get('wins', 0)
                    losses = status.get('losses', 0)
                    self.update_trading_stats_safe(wins, losses, status['profit'])
                
                # Actualizar estado del bot
                if 'running' in status:
                    if status['running']:
                        self.log_safe("🟢 Bot activo en servidor")
                    
        except Exception as e:
            self.log_error_safe(f"Error conectando al servidor: {e}")
    
    def on_connect(self):
        """Sobrescrito para conectarse al servidor remoto"""
        try:
            # Enviar comando de conexión al servidor
            result = self.api_client.start_bot()
            if result.get('status') == 'started':
                self.log_safe("✅ Conectado al servidor remoto")
                self.log_safe(f"🌐 URL: {self.server_url}")
            else:
                self.log_error_safe(f"❌ Error: {result.get('message')}")
        except Exception as e:
            self.log_error_safe(f"❌ No se pudo conectar al servidor: {e}")
            self.log_error_safe("Verifica que el servidor esté ejecutándose")
    
    def on_disconnect(self):
        """Sobrescrito para desconectarse del servidor"""
        try:
            result = self.api_client.stop_bot()
            if result.get('status') == 'stopped':
                self.log_safe("🔴 Desconectado del servidor")
        except Exception as e:
            self.log_error_safe(f"Error al desconectar: {e}")
    
    def closeEvent(self, event):
        """Cierre limpio del cliente"""
        try:
            print("[CLIENT] Cerrando aplicación...")
            
            # Detener polling
            if hasattr(self, 'poll_timer'):
                self.poll_timer.stop()
            
            print("[CLIENT] Cliente cerrado correctamente")
            event.accept()
        except Exception as e:
            print(f"[CLIENT ERROR] Error al cerrar: {e}")
            event.accept()
