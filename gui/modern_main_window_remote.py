"""
Versión remota de la GUI Moderna
Se conecta al backend en Easypanel vía API
"""
from PySide6.QtWidgets import QMainWindow
from gui.modern_main_window import ModernMainWindow
from gui.api_client import APIClient, StatusPoller

class ModernMainWindowRemote(ModernMainWindow):
    """
    Extiende ModernMainWindow para usar API remota
    en lugar de trader local
    """
    
    def __init__(self, backend_url: str):
        # Crear un trader dummy para que el padre no falle
        class DummyTrader:
            def isRunning(self):
                return False
        
        # Inicializar padre con trader dummy
        super().__init__(DummyTrader())
        
        # Reemplazar con API client
        self.api_client = APIClient(backend_url)
        self.status_poller = None
        self.backend_url = backend_url
        
        # Actualizar título
        self.setWindowTitle(f"🤖 Trading Bot Pro - Remoto ({backend_url})")
        
        # Conectar señales remotas (después de que todo esté inicializado)
        QTimer.singleShot(100, self.connect_remote_signals)
        
        # Agregar indicador de modo remoto (después de que add_log exista)
        QTimer.singleShot(200, lambda: self.add_log(f"🌐 Modo Remoto: {backend_url}"))
    
    def connect_remote_signals(self):
        """Conectar señales del API client en lugar del trader"""
        self.api_client.connection_changed.connect(self.on_connection_status_changed)
        self.api_client.balance_updated.connect(self.update_balance)
        self.api_client.log_message.connect(self.add_log)
        self.api_client.status_updated.connect(self.on_remote_status_updated)
        self.api_client.trade_executed.connect(self.on_remote_trade)
    
    def on_connect(self):
        """Override: Conectar vía API con credenciales de la GUI"""
        # Obtener credenciales de la GUI
        email = self.txt_email.text().strip() if hasattr(self, 'txt_email') else ""
        password = self.txt_password.text().strip() if hasattr(self, 'txt_password') else ""
        broker = self.combo_broker.currentText().lower().replace(" ", "") if hasattr(self, 'combo_broker') else "exnova"
        account_type = self.combo_account.currentText() if hasattr(self, 'combo_account') else "PRACTICE"
        
        # Si no hay credenciales en la GUI, usar las del backend (env vars)
        if not email or not password:
            self.add_log("⚠️ Usando credenciales del backend (variables de entorno)")
            email = None
            password = None
        
        self.add_log("🔄 Conectando al backend remoto...")
        self.btn_connect.setEnabled(False)
        
        if self.api_client.connect_broker(email, password, broker, account_type):
            self.btn_disconnect.setEnabled(True)
            
            # Iniciar polling de estado
            self.status_poller = StatusPoller(self.api_client, interval=2000)
            self.status_poller.status_received.connect(self.on_remote_status_updated)
            self.status_poller.start()
            
            # Obtener balance inicial
            self.api_client.get_balance()
        else:
            self.btn_connect.setEnabled(True)
    
    def on_disconnect(self):
        """Override: Desconectar vía API"""
        if self.status_poller:
            self.status_poller.stop()
            self.status_poller.wait()
        
        self.api_client.disconnect_broker()
        self.btn_connect.setEnabled(True)
        self.btn_disconnect.setEnabled(False)
    
    def toggle_bot(self):
        """Override: Iniciar/detener bot vía API"""
        if not hasattr(self, 'bot_running'):
            self.bot_running = False
        
        if not self.bot_running:
            # Iniciar
            if self.api_client.start_trading():
                self.bot_running = True
                self.btn_toggle.setText("⏸️ DETENER BOT")
                self.btn_toggle.setObjectName("btnStop")
                self.btn_toggle.setStyleSheet(self.btn_toggle.styleSheet())  # Refrescar estilo
        else:
            # Detener
            if self.api_client.stop_trading():
                self.bot_running = False
                self.btn_toggle.setText("▶️ INICIAR BOT")
                self.btn_toggle.setObjectName("btnStart")
                self.btn_toggle.setStyleSheet(self.btn_toggle.styleSheet())
    
    def manual_trade(self, direction: str):
        """Override: Ejecutar trade manual vía API"""
        self.add_log(f"⚠️ Trades manuales no disponibles en modo remoto")
        # TODO: Implementar endpoint para trades manuales
    
    def start_training(self):
        """Override: Entrenar modelo vía API"""
        self.add_log(f"⚠️ Entrenamiento no disponible en modo remoto")
        # El entrenamiento se hace en el backend
    
    def retrain_model(self):
        """Override: Re-entrenar modelo vía API"""
        self.add_log(f"⚠️ Re-entrenamiento no disponible en modo remoto")
    
    def on_connection_status_changed(self, connected: bool):
        """Callback cuando cambia el estado de conexión"""
        if connected:
            self.add_log("✅ Conectado al broker (vía backend)")
        else:
            self.add_log("❌ Desconectado del broker")
    
    def on_remote_status_updated(self, status: dict):
        """Callback cuando se actualiza el estado desde el backend"""
        # Actualizar balance
        balance = status.get("balance", 0)
        self.update_balance(balance)
        
        # Actualizar estado de trading
        trading = status.get("trading", False)
        if trading != getattr(self, 'bot_running', False):
            self.bot_running = trading
            if trading:
                self.btn_toggle.setText("⏸️ DETENER BOT")
                self.btn_toggle.setObjectName("btnStop")
            else:
                self.btn_toggle.setText("▶️ INICIAR BOT")
                self.btn_toggle.setObjectName("btnStart")
        
        # Actualizar activo actual
        asset = status.get("current_asset")
        if asset and hasattr(self, 'lbl_chart_asset'):
            self.lbl_chart_asset.setText(f"📊 Activo: {asset}")
    
    def on_remote_trade(self, trade_data: dict):
        """Callback cuando se ejecuta un trade en el backend"""
        direction = trade_data.get("direction", "").upper()
        asset = trade_data.get("asset", "")
        amount = trade_data.get("amount", 0)
        
        self.add_log(f"📊 Trade ejecutado: {direction} {asset} ${amount}")
        
        # Actualizar estadísticas si están disponibles
        if "result" in trade_data:
            result = trade_data["result"]
            if result == "win":
                self.trading_stats['wins'] += 1
                self.trading_stats['total_profit'] += trade_data.get("profit", 0)
            else:
                self.trading_stats['losses'] += 1
                self.trading_stats['total_profit'] -= trade_data.get("loss", 0)
            
            self.update_stats_display()
    
    def update_balance(self, balance: float):
        """Actualizar display de balance"""
        if hasattr(self, 'lbl_balance'):
            self.lbl_balance.setText(f"${balance:.2f}")
    
    def closeEvent(self, event):
        """Override: Limpiar al cerrar"""
        if self.status_poller:
            self.status_poller.stop()
            self.status_poller.wait()
        
        event.accept()
