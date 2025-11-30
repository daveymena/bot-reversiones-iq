import sys
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QDockWidget, QTextEdit, QTabWidget)
from PySide6.QtCore import Slot, Qt
from datetime import datetime

from gui.connection_widget import ConnectionWidget
from gui.status_widget import StatusWidget
from gui.strategy_widget import StrategyWidget
from gui.chart_widget import ChartWidget
from gui.history_widget import HistoryWidget

class MainWindow(QMainWindow):
    def __init__(self, trader_thread):
        super().__init__()
        self.trader = trader_thread
        self.setWindowTitle("Bot de Trading Adaptativo - Pro Interface")
        self.resize(1400, 900)
        
        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        # --- Widget Central (Gráficos y Logs) ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        central_layout = QVBoxLayout(central_widget)
        
        # Gráfico
        self.chart_widget = ChartWidget()
        central_layout.addWidget(self.chart_widget, stretch=2)
        
        # Logs y Tabla (Tabs inferiores)
        bottom_tabs = QTabWidget()
        
        self.txt_log = QTextEdit()
        self.txt_log.setReadOnly(True)
        self.txt_log.setStyleSheet("background-color: #000; color: #0f0; font-family: Consolas;")
        
        self.history_widget = HistoryWidget()
        
        bottom_tabs.addTab(self.txt_log, "Logs del Sistema")
        bottom_tabs.addTab(self.history_widget, "Historial de Operaciones")
        
        central_layout.addWidget(bottom_tabs, stretch=1)

        # --- Docks Laterales (Paneles de Control) ---
        
        # Dock Izquierdo: Conexión y Estado
        left_dock = QDockWidget("Control Principal", self)
        left_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        self.connection_widget = ConnectionWidget()
        self.status_widget = StatusWidget()
        self.strategy_widget = StrategyWidget()
        
        left_layout.addWidget(self.connection_widget)
        left_layout.addWidget(self.status_widget)
        left_layout.addWidget(self.strategy_widget)
        left_layout.addStretch()
        
        left_dock.setWidget(left_widget)
        self.addDockWidget(Qt.LeftDockWidgetArea, left_dock)

    def connect_signals(self):
        # Señales del Trader hacia GUI
        self.trader.signals.log_message.connect(self.log)
        self.trader.signals.error_message.connect(self.log_error)
        self.trader.signals.price_update.connect(self.chart_widget.update_chart)
        self.trader.signals.balance_update.connect(self.status_widget.update_balance)
        
        # Señales de GUI hacia Trader/Lógica
        self.connection_widget.connect_request.connect(self.on_connect_request)
        self.strategy_widget.toggle_bot_signal.connect(self.on_toggle_bot)

    @Slot(str, str, str, str, str)
    def on_connect_request(self, broker, email, password, token, account_type):
        self.log(f"Solicitando conexión a {broker.upper()} ({account_type})...")
        
        # Actualizar config
        from config import Config
        Config.BROKER_NAME = broker
        if broker == "iq":
            Config.IQ_EMAIL = email
            Config.IQ_PASSWORD = password
        else:
            Config.EX_EMAIL = email
            Config.EX_PASSWORD = password
        
        # Conectar en un thread separado para no bloquear la GUI
        from threading import Thread
        def connect_async():
            self.trader.market_data.broker_name = broker
            # Nota: account_type se pasa al API en la inicialización, aquí solo conectamos
            success = self.trader.market_data.connect(email, password)
            if success:
                self.log(f"✅ Conectado exitosamente a {broker.upper()}")
                balance = self.trader.market_data.get_balance()
                self.log(f"💰 Balance ({account_type}): ${balance:.2f}")
                
                # Obtener activo seleccionado
                asset = self.connection_widget.get_selected_asset()
                self.log(f"📊 Activo seleccionado: {asset}")
            else:
                self.log_error(f"❌ Fallo al conectar a {broker.upper()}")
        
        Thread(target=connect_async, daemon=True).start()

    @Slot(bool)
    def on_toggle_bot(self, start):
        if start:
            if not self.trader.isRunning():
                self.trader.start()
            self.trader.paused = False
            self.log("▶️ Bot INICIADO")
        else:
            self.trader.paused = True
            self.log("⏸️ Bot PAUSADO")

    @Slot(str)
    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.txt_log.append(f"[{timestamp}] {message}")
        
        # Detectar resultados de operaciones para actualizar historial y stats
        if "GANADA" in message:
            try:
                parts = message.split(":")
                profit = float(parts[-1].replace("+$", "").strip())
                self.history_widget.add_trade("EURUSD", "CALL/PUT", profit) # Placeholder asset/dir
                # Actualizar stats (racha, etc) - Pendiente implementar lógica completa de stats
            except: pass
        elif "PERDIDA" in message:
             try:
                parts = message.split(":")
                profit = float(parts[-1].replace("-$", "").strip()) * -1
                self.history_widget.add_trade("EURUSD", "CALL/PUT", profit)
             except: pass

    @Slot(str)
    def log_error(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.txt_log.append(f"<span style='color:red'>[{timestamp}] ERROR: {message}</span>")
