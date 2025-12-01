"""
Interfaz Moderna para el Bot de Trading
Diseño inspirado en plataformas profesionales de trading
"""
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from datetime import datetime
import pyqtgraph as pg
import time
import numpy as np

class CandlestickItem(pg.GraphicsObject):
    def __init__(self, data):
        pg.GraphicsObject.__init__(self)
        self.data = data  # data must have fields: time, open, close, min, max
        self.generatePicture()

    def generatePicture(self):
        self.picture = QPicture()
        p = QPainter(self.picture)
        p.setPen(pg.mkPen('w'))
        w = (self.data[1][0] - self.data[0][0]) / 3.
        for (t, open, close, min, max) in self.data:
            p.drawLine(QPointF(t, min), QPointF(t, max))
            if open > close:
                p.setBrush(pg.mkBrush('r'))
            else:
                p.setBrush(pg.mkBrush('g'))
            p.drawRect(QRectF(t-w, open, w*2, close-open))
        p.end()

    def paint(self, p, *args):
        p.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        return QRectF(self.picture.boundingRect())

class ModernMainWindow(QMainWindow):
    def __init__(self, trader_thread):
        super().__init__()
        self.trader = trader_thread
        self.setWindowTitle("🤖 Trading Bot Pro - AI Powered")
        self.resize(1600, 1000)
        
        # Tema oscuro moderno
        self.setup_dark_theme()
        self.setup_ui()
        self.connect_signals()
        
        # Redirigir prints de consola a la GUI
        self.setup_console_redirect()
    
    def setup_dark_theme(self):
        """Aplica tema oscuro profesional estilo trading moderno"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a1d2e;
            }
            QWidget {
                background-color: #1a1d2e;
                color: #c5c9d1;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 13px;
            }
            QPushButton {
                background-color: #22252f;
                border: 1px solid #2d3142;
                border-radius: 8px;
                padding: 10px 20px;
                color: #c5c9d1;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #2d3142;
                border: 1px solid #3d4260;
            }
            QPushButton:pressed {
                background-color: #3d4260;
            }
            QPushButton#btnStart {
                background-color: #00d4aa;
                color: #1a1d2e;
                border: none;
                font-weight: bold;
            }
            QPushButton#btnStart:hover {
                background-color: #00e6bd;
            }
            QPushButton#btnStop {
                background-color: #ff4757;
                color: white;
                border: none;
                font-weight: bold;
            }
            QPushButton#btnStop:hover {
                background-color: #ff6b7a;
            }
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
                background-color: #22252f;
                border: 1px solid #2d3142;
                border-radius: 6px;
                padding: 8px;
                color: #c5c9d1;
            }
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {
                border: 1px solid #00d4aa;
            }
            QGroupBox {
                background-color: #1e2130;
                border: 1px solid #2d3142;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 15px;
                font-weight: 600;
            }
            QGroupBox::title {
                color: #00d4aa;
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 5px;
            }
            QTextEdit {
                background-color: #16181f;
                border: 1px solid #2d3142;
                border-radius: 8px;
                color: #00d4aa;
                font-family: 'Consolas', 'Courier New', monospace;
                padding: 10px;
            }
            QLabel {
                color: #c5c9d1;
            }
            QLabel#lblBalance {
                color: #00d4aa;
                font-size: 24px;
                font-weight: bold;
            }
            QLabel#lblProfit {
                font-size: 18px;
                font-weight: bold;
            }
            QCheckBox, QRadioButton {
                color: #c5c9d1;
                spacing: 8px;
            }
            QCheckBox::indicator, QRadioButton::indicator {
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid #2d3142;
                background-color: #22252f;
            }
            QCheckBox::indicator:checked, QRadioButton::indicator:checked {
                background-color: #00d4aa;
                border-color: #00d4aa;
            }
            QRadioButton::indicator {
                border-radius: 9px;
            }
            QTabWidget::pane {
                border: 1px solid #2d3142;
                border-radius: 8px;
                background-color: #1e2130;
            }
            QTabBar::tab {
                background-color: #22252f;
                border: 1px solid #2d3142;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                color: #8b8f9a;
            }
            QTabBar::tab:selected {
                background-color: #1e2130;
                border-bottom-color: #1e2130;
                color: #00d4aa;
                font-weight: 600;
            }
            QTabBar::tab:hover {
                color: #c5c9d1;
            }
            QScrollBar:vertical {
                background-color: #22252f;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #2d3142;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #3d4260;
            }
            QProgressBar {
                background-color: #22252f;
                border: 1px solid #2d3142;
                border-radius: 6px;
                text-align: center;
                color: #c5c9d1;
            }
            QProgressBar::chunk {
                background-color: #00d4aa;
                border-radius: 5px;
            }
            QTableWidget {
                background-color: #1e2130;
                border: 1px solid #2d3142;
                border-radius: 8px;
                gridline-color: #2d3142;
            }
            QTableWidget::item {
                padding: 5px;
                color: #c5c9d1;
            }
            QTableWidget::item:selected {
                background-color: #2d3142;
            }
            QHeaderView::section {
                background-color: #22252f;
                color: #8b8f9a;
                padding: 8px;
                border: none;
                border-bottom: 1px solid #2d3142;
                font-weight: 600;
            }
        """)
    
    def setup_ui(self):
        """Configura la interfaz principal"""
        # Widget central
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Panel izquierdo (Controles)
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel, stretch=1)
        
        # Panel central (Gráfico y Trading)
        center_panel = self.create_center_panel()
        main_layout.addWidget(center_panel, stretch=3)
        
        # Panel derecho (Estrategias y Stats)
        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel, stretch=1)
        
        # Verificar estado del modelo al iniciar
        self.check_model_status()
        
        # Inicializar estadísticas
        self.trading_stats = {
            'wins': 0,
            'losses': 0,
            'total_profit': 0.0,
            'streak': 0
        }
    
    def create_left_panel(self):
        """Panel izquierdo - Conexión y Configuración"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)
        
        # Logo/Título
        title = QLabel("🤖 Trading Bot")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #00d4aa;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Grupo de Conexión
        conn_group = QGroupBox("📡 Conexión")
        conn_layout = QVBoxLayout()
        
        # Broker
        conn_layout.addWidget(QLabel("Broker:"))
        self.combo_broker = QComboBox()
        self.combo_broker.addItems(["Exnova", "IQ Option"])
        conn_layout.addWidget(self.combo_broker)
        
        # Email
        conn_layout.addWidget(QLabel("Email:"))
        self.txt_email = QLineEdit()
        self.txt_email.setPlaceholderText("tu@email.com")
        conn_layout.addWidget(self.txt_email)
        
        # Password
        conn_layout.addWidget(QLabel("Password:"))
        self.txt_password = QLineEdit()
        self.txt_password.setEchoMode(QLineEdit.Password)
        self.txt_password.setPlaceholderText("••••••••")
        conn_layout.addWidget(self.txt_password)
        
        # Tipo de cuenta
        conn_layout.addWidget(QLabel("Cuenta:"))
        self.combo_account = QComboBox()
        self.combo_account.addItems(["PRACTICE", "REAL"])
        conn_layout.addWidget(self.combo_account)
        
        # Botones conectar/desconectar
        btn_layout = QHBoxLayout()
        
        self.btn_connect = QPushButton("🔌 CONECTAR")
        self.btn_connect.clicked.connect(self.on_connect)
        btn_layout.addWidget(self.btn_connect)
        
        self.btn_disconnect = QPushButton("🔌 DESCONECTAR")
        self.btn_disconnect.clicked.connect(self.on_disconnect)
        self.btn_disconnect.setEnabled(False)
        self.btn_disconnect.setStyleSheet("background-color: #dc3545; color: white;")
        btn_layout.addWidget(self.btn_disconnect)
        
        conn_layout.addLayout(btn_layout)
        
        conn_group.setLayout(conn_layout)
        layout.addWidget(conn_group)
        
        # Grupo de Activo
        asset_group = QGroupBox("📊 Activo")
        asset_layout = QVBoxLayout()
        
        self.combo_asset = QComboBox()
        self.combo_asset.addItems([
            "EURUSD-OTC", "GBPUSD-OTC", "USDJPY-OTC",
            "AUDUSD-OTC", "USDCAD-OTC", "EURJPY-OTC"
        ])
        asset_layout.addWidget(self.combo_asset)
        
        self.chk_otc = QCheckBox("Usar OTC (24/7)")
        self.chk_otc.setChecked(True)
        asset_layout.addWidget(self.chk_otc)
        
        asset_group.setLayout(asset_layout)
        layout.addWidget(asset_group)
        
        # Grupo de Trading
        trading_group = QGroupBox("💰 Trading")
        trading_layout = QFormLayout()
        
        self.spin_amount = QDoubleSpinBox()
        self.spin_amount.setRange(1, 10000)
        self.spin_amount.setValue(1)
        self.spin_amount.setPrefix("$ ")
        trading_layout.addRow("Monto:", self.spin_amount)
        
        self.spin_duration = QSpinBox()
        self.spin_duration.setRange(1, 60)
        self.spin_duration.setValue(1)
        self.spin_duration.setSuffix(" min")
        trading_layout.addRow("Duración:", self.spin_duration)
        
        trading_group.setLayout(trading_layout)
        layout.addWidget(trading_group)
        
        # Grupo de Expiración
        expiration_group = QGroupBox("⏱️ Tiempo de Expiración")
        expiration_layout = QVBoxLayout()
        
        # Modo automático (IA decide)
        self.radio_auto_expiration = QRadioButton("🤖 Automático (IA decide 1-5 min)")
        self.radio_auto_expiration.setChecked(True)
        self.radio_auto_expiration.setToolTip("Groq analiza el mercado y recomienda el mejor tiempo")
        self.radio_auto_expiration.toggled.connect(self.on_expiration_mode_changed)
        expiration_layout.addWidget(self.radio_auto_expiration)
        
        # Modo manual (usuario decide)
        manual_layout = QHBoxLayout()
        self.radio_manual_expiration = QRadioButton("👤 Manual:")
        self.radio_manual_expiration.setToolTip("Usar siempre el tiempo que configures")
        self.radio_manual_expiration.toggled.connect(self.on_expiration_mode_changed)
        manual_layout.addWidget(self.radio_manual_expiration)
        
        self.spin_manual_expiration = QSpinBox()
        self.spin_manual_expiration.setRange(1, 15)
        self.spin_manual_expiration.setValue(1)
        self.spin_manual_expiration.setSuffix(" min")
        self.spin_manual_expiration.setEnabled(False)
        self.spin_manual_expiration.valueChanged.connect(self.on_manual_expiration_changed)
        manual_layout.addWidget(self.spin_manual_expiration)
        
        expiration_layout.addLayout(manual_layout)
        
        expiration_group.setLayout(expiration_layout)
        layout.addWidget(expiration_group)
        
        # Botón para limpiar experiencias
        btn_clear = QPushButton("🗑️ Limpiar Experiencias")
        btn_clear.clicked.connect(self.on_clear_experiences)
        btn_clear.setStyleSheet("background-color: #ffc107; color: #0a0e27;")
        btn_clear.setToolTip("Elimina experiencias viejas para empezar de cero")
        layout.addWidget(btn_clear)
        
        layout.addStretch()
        return panel
    
    def create_center_panel(self):
        """Panel central - Gráfico y Controles de Trading"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)
        
        # Header con balance y stats
        header = self.create_header()
        layout.addWidget(header)
        
        # Gráfico
        chart_group = QGroupBox("📈 Gráfico en Tiempo Real")
        chart_layout = QVBoxLayout()
        
        # Header del gráfico con activo actual
        chart_header = QHBoxLayout()
        self.lbl_current_asset = QLabel("Activo: --")
        self.lbl_current_asset.setStyleSheet("font-size: 16px; font-weight: bold; color: #00d4aa;")
        chart_header.addWidget(self.lbl_current_asset)
        chart_header.addStretch()
        chart_layout.addLayout(chart_header)
        
        # Usar pyqtgraph para gráficos más rápidos
        self.chart = pg.PlotWidget()
        self.chart.setBackground('#16181f')
        self.chart.showGrid(x=True, y=True, alpha=0.2)
        self.chart.setLabel('left', 'Precio', color='#c5c9d1')
        self.chart.setLabel('bottom', 'Tiempo', color='#c5c9d1')
        
        # Configurar estilo del gráfico
        self.chart.getAxis('left').setPen(pg.mkPen(color='#2d3142', width=1))
        self.chart.getAxis('bottom').setPen(pg.mkPen(color='#2d3142', width=1))
        self.chart.getAxis('left').setTextPen(pg.mkPen(color='#c5c9d1'))
        self.chart.getAxis('bottom').setTextPen(pg.mkPen(color='#c5c9d1'))
        
        # Datos del gráfico
        self.candle_data = []  # Para almacenar OHLC (Open, High, Low, Close)
        self.max_candles = 100  # Mostrar últimas 100 velas
        
        # Items para velas japonesas
        self.candle_items = []  # Lista de velas dibujadas
        
        # Colores para velas
        self.bull_color = '#00d4aa'  # Verde para velas alcistas
        self.bear_color = '#ff4757'  # Rojo para velas bajistas
        
        # Agregar líneas de referencia
        self.buy_markers = []  # Marcadores de compra
        self.sell_markers = []  # Marcadores de venta
        
        chart_layout.addWidget(self.chart)
        chart_group.setLayout(chart_layout)
        layout.addWidget(chart_group, stretch=2)
        
        # Botones de trading
        trading_buttons = self.create_trading_buttons()
        layout.addWidget(trading_buttons)
        
        # Logs
        log_group = QGroupBox("📝 Logs del Sistema")
        log_layout = QVBoxLayout()
        
        self.txt_log = QTextEdit()
        self.txt_log.setReadOnly(True)
        self.txt_log.setMaximumHeight(200)
        log_layout.addWidget(self.txt_log)
        
        log_group.setLayout(log_layout)
        layout.addWidget(log_group, stretch=1)
        
        return panel
    
    def create_header(self):
        """Header con balance y estadísticas"""
        header = QWidget()
        header.setMaximumHeight(100)
        layout = QHBoxLayout(header)
        
        # Balance
        balance_widget = QWidget()
        balance_layout = QVBoxLayout(balance_widget)
        balance_layout.setSpacing(5)
        
        lbl_balance_title = QLabel("💰 Balance")
        lbl_balance_title.setStyleSheet("font-size: 14px; color: #888;")
        self.lbl_balance = QLabel("$0.00")
        self.lbl_balance.setObjectName("lblBalance")
        
        balance_layout.addWidget(lbl_balance_title)
        balance_layout.addWidget(self.lbl_balance)
        layout.addWidget(balance_widget)
        
        # Profit del día
        profit_widget = QWidget()
        profit_layout = QVBoxLayout(profit_widget)
        profit_layout.setSpacing(5)
        
        lbl_profit_title = QLabel("📊 Profit Hoy")
        lbl_profit_title.setStyleSheet("font-size: 14px; color: #888;")
        self.lbl_profit = QLabel("$0.00")
        self.lbl_profit.setObjectName("lblProfit")
        self.lbl_profit.setStyleSheet("color: #00d4aa;")
        
        profit_layout.addWidget(lbl_profit_title)
        profit_layout.addWidget(self.lbl_profit)
        layout.addWidget(profit_widget)
        
        # Win Rate
        winrate_widget = QWidget()
        winrate_layout = QVBoxLayout(winrate_widget)
        winrate_layout.setSpacing(5)
        
        lbl_winrate_title = QLabel("🎯 Win Rate")
        lbl_winrate_title.setStyleSheet("font-size: 14px; color: #888;")
        self.lbl_winrate = QLabel("0%")
        self.lbl_winrate.setStyleSheet("font-size: 18px; font-weight: bold; color: #00d4aa;")
        
        winrate_layout.addWidget(lbl_winrate_title)
        winrate_layout.addWidget(self.lbl_winrate)
        layout.addWidget(winrate_widget)
        
        # Operaciones
        trades_widget = QWidget()
        trades_layout = QVBoxLayout(trades_widget)
        trades_layout.setSpacing(5)
        
        lbl_trades_title = QLabel("📈 Operaciones")
        lbl_trades_title.setStyleSheet("font-size: 14px; color: #888;")
        self.lbl_trades = QLabel("0")
        self.lbl_trades.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        trades_layout.addWidget(lbl_trades_title)
        trades_layout.addWidget(self.lbl_trades)
        layout.addWidget(trades_widget)
        
        layout.addStretch()
        return header
    
    def create_trading_buttons(self):
        """Botones de control de trading"""
        widget = QWidget()
        widget.setMaximumHeight(80)
        layout = QHBoxLayout(widget)
        
        # Botón CALL
        self.btn_call = QPushButton("📈 CALL")
        self.btn_call.setMinimumHeight(50)
        self.btn_call.setStyleSheet("""
            QPushButton {
                background-color: #00d4aa;
                color: #0a0e27;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00e6bd;
            }
        """)
        self.btn_call.clicked.connect(lambda: self.manual_trade("call"))
        layout.addWidget(self.btn_call)
        
        # Botón START/STOP
        self.btn_toggle = QPushButton("▶️ INICIAR BOT")
        self.btn_toggle.setObjectName("btnStart")
        self.btn_toggle.setMinimumHeight(50)
        self.btn_toggle.setMinimumWidth(200)
        self.btn_toggle.clicked.connect(self.toggle_bot)
        layout.addWidget(self.btn_toggle)
        
        # Botón PUT
        self.btn_put = QPushButton("📉 PUT")
        self.btn_put.setMinimumHeight(50)
        self.btn_put.setStyleSheet("""
            QPushButton {
                background-color: #ff4757;
                color: white;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff6b7a;
            }
        """)
        self.btn_put.clicked.connect(lambda: self.manual_trade("put"))
        layout.addWidget(self.btn_put)
        
        return widget
    
    def create_right_panel(self):
        """Panel derecho - Estrategias, Entrenamiento y Análisis"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)
        
        # Tabs para organizar mejor
        tabs = QTabWidget()
        
        # Tab 1: Estrategias
        strategy_tab = self.create_strategy_tab()
        tabs.addTab(strategy_tab, "🎯 Estrategias")
        
        # Tab 2: Entrenamiento
        training_tab = self.create_training_tab()
        tabs.addTab(training_tab, "🎓 Entrenamiento")
        
        # Tab 3: Análisis
        analysis_tab = self.create_analysis_tab()
        tabs.addTab(analysis_tab, "📊 Análisis")
        
        layout.addWidget(tabs)
        return panel
    
    def create_strategy_tab(self):
        """Tab de estrategias"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Estrategias activas
        strategy_group = QGroupBox("🎯 Estrategias Activas")
        strategy_layout = QVBoxLayout()
        
        self.chk_rl = QCheckBox("🤖 Reinforcement Learning")
        self.chk_rl.setChecked(True)
        self.chk_rl.setToolTip("Usa el agente RL entrenado para tomar decisiones")
        strategy_layout.addWidget(self.chk_rl)
        
        self.chk_martingale = QCheckBox("📊 Martingala Inteligente")
        self.chk_martingale.setChecked(True)
        self.chk_martingale.setToolTip("Aplica martingala solo cuando el análisis lo recomienda")
        strategy_layout.addWidget(self.chk_martingale)
        
        self.chk_llm = QCheckBox("🧠 Análisis LLM (Groq)")
        self.chk_llm.setChecked(True)
        self.chk_llm.setToolTip("Usa IA generativa para análisis adicional")
        strategy_layout.addWidget(self.chk_llm)
        
        self.chk_auto_train = QCheckBox("🔄 Auto-Entrenamiento")
        self.chk_auto_train.setChecked(False)
        self.chk_auto_train.setToolTip("Re-entrena automáticamente cada 24h")
        strategy_layout.addWidget(self.chk_auto_train)
        
        strategy_group.setLayout(strategy_layout)
        layout.addWidget(strategy_group)
        
        # Configuración de riesgo
        risk_group = QGroupBox("⚠️ Gestión de Riesgo")
        risk_layout = QFormLayout()
        
        self.spin_stop_loss = QDoubleSpinBox()
        self.spin_stop_loss.setRange(1, 50)
        self.spin_stop_loss.setValue(5)
        self.spin_stop_loss.setSuffix("%")
        risk_layout.addRow("Stop Loss:", self.spin_stop_loss)
        
        self.spin_take_profit = QDoubleSpinBox()
        self.spin_take_profit.setRange(1, 100)
        self.spin_take_profit.setValue(10)
        self.spin_take_profit.setSuffix("%")
        risk_layout.addRow("Take Profit:", self.spin_take_profit)
        
        self.spin_max_martingale = QSpinBox()
        self.spin_max_martingale.setRange(0, 5)
        self.spin_max_martingale.setValue(3)
        risk_layout.addRow("Max Martingala:", self.spin_max_martingale)
        
        risk_group.setLayout(risk_layout)
        layout.addWidget(risk_group)
        
        # Indicadores en tiempo real
        indicators_group = QGroupBox("📊 Indicadores Técnicos")
        indicators_layout = QVBoxLayout()
        
        self.lbl_rsi = QLabel("RSI: --")
        self.lbl_macd = QLabel("MACD: --")
        self.lbl_bb = QLabel("Bollinger: --")
        self.lbl_atr = QLabel("ATR: --")
        
        indicators_layout.addWidget(self.lbl_rsi)
        indicators_layout.addWidget(self.lbl_macd)
        indicators_layout.addWidget(self.lbl_bb)
        indicators_layout.addWidget(self.lbl_atr)
        
        indicators_group.setLayout(indicators_layout)
        layout.addWidget(indicators_group)
        
        layout.addStretch()
        return widget
    
    def create_training_tab(self):
        """Tab de entrenamiento"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Estado del modelo
        model_group = QGroupBox("🤖 Estado del Modelo RL")
        model_layout = QVBoxLayout()
        
        self.lbl_model_status = QLabel("❌ No entrenado")
        self.lbl_model_status.setStyleSheet("font-size: 14px; font-weight: bold;")
        model_layout.addWidget(self.lbl_model_status)
        
        self.lbl_model_info = QLabel("Entrena el modelo para comenzar")
        self.lbl_model_info.setStyleSheet("color: #888;")
        model_layout.addWidget(self.lbl_model_info)
        
        model_group.setLayout(model_layout)
        layout.addWidget(model_group)
        
        # Configuración de entrenamiento
        train_config_group = QGroupBox("⚙️ Configuración")
        train_config_layout = QFormLayout()
        
        self.spin_train_candles = QSpinBox()
        self.spin_train_candles.setRange(500, 10000)
        self.spin_train_candles.setValue(2000)
        self.spin_train_candles.setSingleStep(500)
        train_config_layout.addRow("Velas:", self.spin_train_candles)
        
        self.spin_timesteps = QSpinBox()
        self.spin_timesteps.setRange(1000, 100000)
        self.spin_timesteps.setValue(10000)
        self.spin_timesteps.setSingleStep(1000)
        train_config_layout.addRow("Timesteps:", self.spin_timesteps)
        
        train_config_group.setLayout(train_config_layout)
        layout.addWidget(train_config_group)
        
        # Botones de entrenamiento
        self.btn_train = QPushButton("🎓 ENTRENAR MODELO")
        self.btn_train.setMinimumHeight(40)
        self.btn_train.clicked.connect(self.start_training)
        layout.addWidget(self.btn_train)
        
        self.btn_retrain = QPushButton("🔄 RE-ENTRENAR (Datos Recientes)")
        self.btn_retrain.setMinimumHeight(40)
        self.btn_retrain.clicked.connect(self.retrain_model)
        layout.addWidget(self.btn_retrain)
        
        # Progreso de entrenamiento
        progress_group = QGroupBox("📈 Progreso")
        progress_layout = QVBoxLayout()
        
        self.progress_train = QProgressBar()
        self.progress_train.setTextVisible(True)
        progress_layout.addWidget(self.progress_train)
        
        self.lbl_train_status = QLabel("Esperando...")
        self.lbl_train_status.setStyleSheet("color: #888;")
        progress_layout.addWidget(self.lbl_train_status)
        
        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)
        
        # Métricas de entrenamiento
        metrics_group = QGroupBox("📊 Métricas")
        metrics_layout = QVBoxLayout()
        
        self.txt_train_metrics = QTextEdit()
        self.txt_train_metrics.setReadOnly(True)
        self.txt_train_metrics.setMaximumHeight(150)
        self.txt_train_metrics.setPlaceholderText("Las métricas aparecerán aquí...")
        metrics_layout.addWidget(self.txt_train_metrics)
        
        metrics_group.setLayout(metrics_layout)
        layout.addWidget(metrics_group)
        
        layout.addStretch()
        return widget
    
    def create_analysis_tab(self):
        """Tab de análisis"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Estadísticas de trading
        stats_group = QGroupBox("📊 Estadísticas de Trading")
        stats_layout = QGridLayout()
        
        # Fila 1
        stats_layout.addWidget(QLabel("Total Operaciones:"), 0, 0)
        self.lbl_total_trades = QLabel("0")
        self.lbl_total_trades.setStyleSheet("font-weight: bold;")
        stats_layout.addWidget(self.lbl_total_trades, 0, 1)
        
        stats_layout.addWidget(QLabel("Ganadas:"), 0, 2)
        self.lbl_wins = QLabel("0")
        self.lbl_wins.setStyleSheet("font-weight: bold; color: #00d4aa;")
        stats_layout.addWidget(self.lbl_wins, 0, 3)
        
        # Fila 2
        stats_layout.addWidget(QLabel("Perdidas:"), 1, 0)
        self.lbl_losses = QLabel("0")
        self.lbl_losses.setStyleSheet("font-weight: bold; color: #ff4757;")
        stats_layout.addWidget(self.lbl_losses, 1, 1)
        
        stats_layout.addWidget(QLabel("Win Rate:"), 1, 2)
        self.lbl_winrate_detail = QLabel("0%")
        self.lbl_winrate_detail.setStyleSheet("font-weight: bold;")
        stats_layout.addWidget(self.lbl_winrate_detail, 1, 3)
        
        # Fila 3
        stats_layout.addWidget(QLabel("Profit Total:"), 2, 0)
        self.lbl_total_profit = QLabel("$0.00")
        self.lbl_total_profit.setStyleSheet("font-weight: bold; font-size: 14px;")
        stats_layout.addWidget(self.lbl_total_profit, 2, 1)
        
        stats_layout.addWidget(QLabel("Racha Actual:"), 2, 2)
        self.lbl_streak = QLabel("0")
        self.lbl_streak.setStyleSheet("font-weight: bold;")
        stats_layout.addWidget(self.lbl_streak, 2, 3)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        # Análisis de martingala
        martingale_group = QGroupBox("📊 Estado Martingala")
        martingale_layout = QVBoxLayout()
        
        self.lbl_martingale_level = QLabel("Nivel: 0")
        self.lbl_martingale_level.setStyleSheet("font-size: 14px;")
        martingale_layout.addWidget(self.lbl_martingale_level)
        
        self.lbl_next_amount = QLabel("Próximo monto: $1.00")
        martingale_layout.addWidget(self.lbl_next_amount)
        
        martingale_group.setLayout(martingale_layout)
        layout.addWidget(martingale_group)
        
        # Señales y recomendaciones
        signals_group = QGroupBox("🔔 Señales y Análisis")
        signals_layout = QVBoxLayout()
        
        self.txt_signals = QTextEdit()
        self.txt_signals.setReadOnly(True)
        self.txt_signals.setPlaceholderText("Las señales aparecerán aquí...")
        signals_layout.addWidget(self.txt_signals)
        
        signals_group.setLayout(signals_layout)
        layout.addWidget(signals_group)
        
        # Últimas operaciones
        history_group = QGroupBox("📜 Últimas Operaciones")
        history_layout = QVBoxLayout()
        
        self.table_history = QTableWidget()
        self.table_history.setColumnCount(5)
        self.table_history.setHorizontalHeaderLabels([
            "Hora", "Activo", "Tipo", "Monto", "Resultado"
        ])
        self.table_history.horizontalHeader().setStretchLastSection(True)
        self.table_history.setMaximumHeight(200)
        history_layout.addWidget(self.table_history)
        
        history_group.setLayout(history_layout)
        layout.addWidget(history_group)
        
        layout.addStretch()
        return widget
    
    def connect_signals(self):
        """Conecta señales del trader con protección contra errores"""
        try:
            self.trader.signals.log_message.connect(self.log_safe)
            self.trader.signals.error_message.connect(self.log_error_safe)
            self.trader.signals.balance_update.connect(self.update_balance_safe)
            self.trader.signals.price_update.connect(self.update_chart_safe)
            self.trader.signals.trade_signal.connect(self.on_trade_signal_safe)
            self.trader.signals.stats_update.connect(self.update_trading_stats_safe)
            self.trader.signals.new_candle.connect(self.update_indicators_safe)
        except Exception as e:
            print(f"[ERROR] Error conectando señales: {e}")
    
    # ============================================
    # MÉTODOS SAFE (con protección total)
    # ============================================
    
    @Slot(str)
    def log_safe(self, message):
        """Versión segura de log que nunca falla"""
        try:
            self.log(message)
        except Exception as e:
            print(f"[GUI ERROR] Error en log: {e}")
            # Intentar log básico
            try:
                self.txt_log.append(str(message))
            except:
                pass
    
    @Slot(str)
    def log_error_safe(self, message):
        """Versión segura de log_error que nunca falla"""
        try:
            self.log_error(message)
        except Exception as e:
            print(f"[GUI ERROR] Error en log_error: {e}")
            try:
                self.txt_log.append(f"ERROR: {message}")
            except:
                pass
    
    @Slot(float)
    def update_balance_safe(self, balance):
        """Versión segura de update_balance que nunca falla"""
        try:
            self.update_balance(balance)
        except Exception as e:
            print(f"[GUI ERROR] Error actualizando balance: {e}")
    
    @Slot(float, float)
    def update_chart_safe(self, timestamp, price):
        """Versión segura de update_chart que nunca falla"""
        try:
            self.update_chart(timestamp, price)
        except Exception as e:
            # Silenciar errores de gráfico para no saturar logs
            pass
    
    @Slot(str, str)
    def on_trade_signal_safe(self, action, asset):
        """Versión segura de on_trade_signal que nunca falla"""
        try:
            self.on_trade_signal(action, asset)
        except Exception as e:
            print(f"[GUI ERROR] Error en trade signal: {e}")

    @Slot(int, int, float)
    def update_trading_stats_safe(self, wins, losses, profit):
        """Versión segura de update_trading_stats"""
        try:
            self.update_trading_stats(wins, losses, profit)
        except Exception as e:
            print(f"[GUI ERROR] Error actualizando stats: {e}")

    @Slot(object)
    def update_indicators_safe(self, data):
        """Versión segura de update_indicators"""
        try:
            self.update_indicators(data)
        except Exception as e:
            # print(f"[GUI ERROR] Error actualizando indicadores: {e}")
            pass
    
    # ============================================
    # MÉTODOS ORIGINALES (ahora con más protección)
    # ============================================
    
    @Slot(str, str)
    def on_trade_signal(self, action, asset):
        """Maneja señal de operación para marcar en el gráfico"""
        try:
            if hasattr(self, 'price_data') and self.price_data:
                current_price = self.price_data[-1]
                self.mark_trade_on_chart(current_price, action)
                self.log(f"📍 Operación marcada en gráfico: {action} @ {current_price:.5f}")
        except Exception as e:
            pass
    
    @Slot()
    def on_connect(self):
        """Maneja la conexión al broker (sin congelar la GUI)"""
        broker = self.combo_broker.currentText().lower().replace(" ", "")
        if "exnova" in broker:
            broker = "exnova"
        else:
            broker = "iq"
        
        email = self.txt_email.text()
        password = self.txt_password.text()
        account_type = self.combo_account.currentText()
        
        if not email or not password:
            self.log_error("Email y password son requeridos")
            return
        
        self.log(f"Conectando a {broker.upper()}...")
        self.btn_connect.setEnabled(False)
        self.btn_connect.setText("⏳ Conectando...")
        
        # Procesar eventos de Qt para evitar congelamiento
        QApplication.processEvents()
        
        # Conectar en thread separado
        from threading import Thread
        def connect_async():
            try:
                from config import Config
                Config.BROKER_NAME = broker
                
                self.trader.market_data.broker_name = broker
                self.trader.market_data.account_type = account_type
                
                # Conectar
                success = self.trader.market_data.connect(email, password)
                
                # Usar QMetaObject.invokeMethod para actualizar GUI de forma segura
                if success:
                    QMetaObject.invokeMethod(self, "on_connect_success",
                                            Qt.QueuedConnection,
                                            Q_ARG(str, broker))
                else:
                    QMetaObject.invokeMethod(self, "on_connect_failed",
                                            Qt.QueuedConnection,
                                            Q_ARG(str, broker))
            except Exception as e:
                print(f"[ERROR] Error en conexión: {e}")
                QMetaObject.invokeMethod(self, "on_connect_failed",
                                        Qt.QueuedConnection,
                                        Q_ARG(str, broker))
        
        Thread(target=connect_async, daemon=True).start()
    
    @Slot(str)
    def on_connect_success(self, broker):
        """Callback cuando la conexión es exitosa"""
        try:
            self.log(f"✅ Conectado a {broker.upper()}")
            balance = self.trader.market_data.get_balance()
            self.update_balance(balance)
            self.btn_connect.setText("✅ CONECTADO")
            self.btn_connect.setStyleSheet("background-color: #00d4aa; color: #0a0e27;")
            self.btn_disconnect.setEnabled(True)
            
            # Resetear contador
            self.trader.continuous_learner.last_retrain_count = len(
                self.trader.continuous_learner.experience_buffer.experiences
            )
            self.log("✅ Sistema de aprendizaje inicializado")
        except Exception as e:
            print(f"[ERROR] Error en on_connect_success: {e}")
    
    @Slot(str)
    def on_connect_failed(self, broker):
        """Callback cuando la conexión falla"""
        try:
            self.log_error(f"Error al conectar a {broker.upper()}")
            self.btn_connect.setEnabled(True)
            self.btn_connect.setText("🔌 CONECTAR")
            self.btn_connect.setStyleSheet("")
        except Exception as e:
            print(f"[ERROR] Error en on_connect_failed: {e}")
    
    def on_disconnect(self):
        """Desconecta del broker"""
        try:
            # Detener el bot si está corriendo
            if self.trader.running:
                self.trader.running = False
                self.trader.paused = False
                self.btn_toggle.setText("▶️ INICIAR BOT")
                self.btn_toggle.setObjectName("btnStart")
                self.btn_toggle.setStyle(self.btn_toggle.style())
                self.log("⏹️ Bot detenido")
            
            # Desconectar
            if self.trader.market_data.api:
                self.trader.market_data.connected = False
                self.trader.market_data.api = None
            
            self.log("🔌 Desconectado del broker")
            
            # Actualizar botones
            self.btn_connect.setEnabled(True)
            self.btn_connect.setText("🔌 CONECTAR")
            self.btn_connect.setStyleSheet("")
            self.btn_disconnect.setEnabled(False)
            
            # Actualizar balance
            self.update_balance(0)
            
        except Exception as e:
            self.log_error(f"Error al desconectar: {e}")
    
    def on_clear_experiences(self):
        """Limpia las experiencias guardadas"""
        from PySide6.QtWidgets import QMessageBox
        
        reply = QMessageBox.question(
            self,
            'Confirmar',
            '¿Estás seguro de que quieres eliminar todas las experiencias guardadas?\n\nEsto reiniciará el aprendizaje del bot.',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # Limpiar buffer de experiencias
                self.trader.continuous_learner.experience_buffer.clear()
                
                # Resetear contador
                self.trader.continuous_learner.last_retrain_count = 0
                
                self.log("✅ Experiencias eliminadas - El bot empezará de cero")
                
            except Exception as e:
                self.log_error(f"Error al limpiar experiencias: {e}")
    
    @Slot()
    def toggle_bot(self):
        """Inicia/detiene el bot"""
        if not self.trader.isRunning():
            self.trader.start()
            self.btn_toggle.setText("⏸️ DETENER BOT")
            self.btn_toggle.setObjectName("btnStop")
            self.btn_toggle.setStyle(self.btn_toggle.style())
            self.log("▶️ Bot iniciado")
        else:
            self.trader.paused = not self.trader.paused
            if self.trader.paused:
                self.btn_toggle.setText("▶️ REANUDAR BOT")
                self.btn_toggle.setObjectName("btnStart")
                self.log("⏸️ Bot pausado")
            else:
                self.btn_toggle.setText("⏸️ DETENER BOT")
                self.btn_toggle.setObjectName("btnStop")
                self.log("▶️ Bot reanudado")
            self.btn_toggle.setStyle(self.btn_toggle.style())
    
    def manual_trade(self, direction):
        """Ejecuta operación manual"""
        if not self.trader.market_data.connected:
            self.log_error("Debes conectarte primero")
            return
        
        asset = self.combo_asset.currentText()
        amount = self.spin_amount.value()
        duration = self.spin_duration.value()
        
        self.log(f"Ejecutando {direction.upper()} manual en {asset}...")
        
        # Ejecutar en thread separado
        from threading import Thread
        def trade_async():
            try:
                status, order_id = self.trader.market_data.api.buy(
                    amount, asset, direction, duration
                )
                if status:
                    self.log(f"✅ Operación ejecutada - ID: {order_id}")
                else:
                    self.log_error(f"Error: {order_id}")
            except Exception as e:
                self.log_error(f"Error: {e}")
        
        Thread(target=trade_async, daemon=True).start()
    
    @Slot(str)
    def log(self, message):
        """Agrega mensaje al log con formato mejorado (ultra seguro)"""
        try:
            # Convertir a string por si acaso
            message = str(message)
            
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            # Limitar número de líneas (máximo 500)
            try:
                if self.txt_log.document().lineCount() > 500:
                    cursor = self.txt_log.textCursor()
                    cursor.movePosition(QTextCursor.Start)
                    cursor.movePosition(QTextCursor.Down, QTextCursor.KeepAnchor, 100)
                    cursor.removeSelectedText()
            except:
                pass
            
            # Detectar tipo de mensaje y aplicar color
            try:
                if any(emoji in message for emoji in ['✅', '🚀', '💎', '📈', '♾️']):
                    color = '#00d4aa'
                elif any(emoji in message for emoji in ['❌', '⚠️', '🛑']):
                    color = '#ff4757'
                elif any(emoji in message for emoji in ['⏳', '⏱️', '🔍', '📊', '💓']):
                    color = '#ffc107'
                elif any(emoji in message for emoji in ['🎯', '🧠', '💡', '🎓']):
                    color = '#5dade2'
                else:
                    color = '#c5c9d1'
            except:
                color = '#c5c9d1'
            
            # Formatear mensaje con HTML
            try:
                # Escapar caracteres HTML problemáticos
                message_safe = message.replace('<', '&lt;').replace('>', '&gt;')
                formatted_message = f'<span style="color: #00d4aa; font-weight: 600;">[{timestamp}]</span> <span style="color: {color};">{message_safe}</span>'
            except:
                formatted_message = f"[{timestamp}] {message}"
            
            # Agregar al log
            self.txt_log.append(formatted_message)
            
            # Auto-scroll al final
            try:
                scrollbar = self.txt_log.verticalScrollBar()
                scrollbar.setValue(scrollbar.maximum())
            except:
                pass
            
            # También imprimir en consola para debugging
            print(f"[{timestamp}] {message}")
        
        except Exception as e:
            # Último recurso: log básico
            try:
                self.txt_log.append(str(message))
                print(f"[LOG ERROR] {e}: {message}")
            except:
                print(f"[CRITICAL LOG ERROR] No se pudo agregar log: {message}")
    
    @Slot(str)
    def log_error(self, message):
        """Agrega error al log (ultra seguro)"""
        try:
            message = str(message)
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            try:
                message_safe = message.replace('<', '&lt;').replace('>', '&gt;')
                formatted_message = f'<span style="color: #00d4aa; font-weight: 600;">[{timestamp}]</span> <span style="color: #ff4757; font-weight: 600;">❌ {message_safe}</span>'
            except:
                formatted_message = f"[{timestamp}] ERROR: {message}"
            
            self.txt_log.append(formatted_message)
            
            # Auto-scroll al final
            try:
                scrollbar = self.txt_log.verticalScrollBar()
                scrollbar.setValue(scrollbar.maximum())
            except:
                pass
            
            # También imprimir en consola
            print(f"[{timestamp}] ERROR: {message}")
        
        except Exception as e:
            try:
                self.txt_log.append(f"ERROR: {message}")
                print(f"[ERROR LOG ERROR] {e}: {message}")
            except:
                print(f"[CRITICAL ERROR] No se pudo agregar error: {message}")
    
    @Slot(float)
    def update_balance(self, balance):
        """Actualiza el balance"""
        self.lbl_balance.setText(f"${balance:.2f}")
    
    @Slot(float, float)
    def update_chart(self, timestamp, price):
        """Actualiza el gráfico sin congelar la GUI"""
        try:
            # Limitar actualizaciones (solo cada 15 segundos)
            current_time = time.time()
            if not hasattr(self, 'last_chart_update'):
                self.last_chart_update = 0
            
            if current_time - self.last_chart_update < 15:
                return  # Saltar actualización
            
            self.last_chart_update = current_time
            
            # Verificaciones rápidas
            if not hasattr(self, 'trader') or not hasattr(self.trader, 'market_data'):
                return
            
            if not self.trader.market_data.connected:
                return
            
            # Actualizar en thread separado para no congelar GUI
            from threading import Thread
            def update_async():
                try:
                    # Obtener activo actual
                    current_asset = getattr(self.trader, 'current_asset', 'EURUSD-OTC')
                    
                    # Obtener velas (reducido a 20 para máximo rendimiento)
                    df = self.trader.market_data.get_candles(current_asset, 60, 20)
                    
                    if df is None or df.empty or len(df) < 2:
                        return
                    
                    # Actualizar GUI de forma segura
                    QMetaObject.invokeMethod(self, "update_chart_data",
                                            Qt.QueuedConnection,
                                            Q_ARG(str, current_asset),
                                            Q_ARG(object, df))
                except:
                    pass
            
            Thread(target=update_async, daemon=True).start()
        
        except Exception as e:
            pass
    
    @Slot(str, object)
    def update_chart_data(self, asset, df):
        """Actualiza los datos del gráfico usando CandlestickItem optimizado"""
        try:
            # Actualizar label del activo
            if hasattr(self, 'lbl_current_asset'):
                self.lbl_current_asset.setText(f"📊 Activo: {asset}")
            
            # Preparar datos para CandlestickItem: (t, open, close, min, max)
            data = []
            # Tomar solo las últimas 50 velas para rendimiento
            df_subset = df.tail(50)
            
            for i, (idx, row) in enumerate(df_subset.iterrows()):
                data.append((float(i), float(row['open']), float(row['close']), float(row['low']), float(row['high'])))
            
            # Remover item anterior
            if hasattr(self, 'candlestick_item') and self.candlestick_item:
                self.chart.removeItem(self.candlestick_item)
            
            # Limpiar items antiguos si existen (de la versión anterior)
            if hasattr(self, 'candle_items'):
                for item in self.candle_items:
                    try:
                        self.chart.removeItem(item)
                    except: pass
                self.candle_items = []
            
            # Crear y añadir nuevo item
            self.candlestick_item = CandlestickItem(data)
            self.chart.addItem(self.candlestick_item)
            
            # Auto-ajustar rango
            if len(data) > 0:
                min_price = df_subset['low'].min()
                max_price = df_subset['high'].max()
                if min_price > 0 and max_price > 0:
                    padding = (max_price - min_price) * 0.1
                    self.chart.setYRange(min_price - padding, max_price + padding, padding=0)
                    self.chart.setXRange(-1, len(data), padding=0)
            
            # Procesar eventos para mantener GUI responsive
            QApplication.processEvents()
        
        except Exception as e:
            print(f"[GUI ERROR] Error actualizando gráfico: {e}")
    
    def draw_candlestick(self, x, open_price, high, low, close):
        """Dibuja una vela japonesa individual"""
        try:
            # Determinar color (alcista o bajista)
            is_bullish = close >= open_price
            color = self.bull_color if is_bullish else self.bear_color
            
            # Ancho de la vela
            width = 0.6
            
            # Dibujar mecha (high-low)
            wick = pg.PlotDataItem(
                [x, x],
                [low, high],
                pen=pg.mkPen(color=color, width=1)
            )
            self.chart.addItem(wick)
            self.candle_items.append(wick)
            
            # Dibujar cuerpo (open-close)
            body_height = abs(close - open_price)
            body_y = min(open_price, close)
            
            # Crear rectángulo para el cuerpo
            body = pg.QtWidgets.QGraphicsRectItem(
                x - width/2,
                body_y,
                width,
                body_height if body_height > 0 else 0.00001
            )
            
            # Configurar color y borde
            body.setPen(pg.mkPen(color=color, width=1))
            body.setBrush(pg.mkBrush(color=color))
            
            self.chart.addItem(body)
            self.candle_items.append(body)
        
        except Exception as e:
            pass
    
    @Slot()
    def start_training(self):
        """Inicia el entrenamiento del modelo (sin congelar GUI)"""
        if not self.trader.market_data.connected:
            self.log_error("Debes conectarte primero para obtener datos")
            return
        
        asset = self.combo_asset.currentText()
        num_candles = self.spin_train_candles.value()
        timesteps = self.spin_timesteps.value()
        
        self.log(f"🎓 Iniciando entrenamiento...")
        self.log(f"   Activo: {asset}")
        self.log(f"   Velas: {num_candles}")
        self.log(f"   Timesteps: {timesteps}")
        
        self.btn_train.setEnabled(False)
        self.btn_train.setText("⏳ Entrenando...")
        self.progress_train.setValue(0)
        self.lbl_train_status.setText("Obteniendo datos...")
        
        # Procesar eventos para actualizar GUI
        QApplication.processEvents()
        
        # Entrenar en thread separado
        from threading import Thread
        def train_async():
            try:
                # Obtener datos
                QMetaObject.invokeMethod(self.lbl_train_status, "setText",
                                        Qt.QueuedConnection,
                                        Q_ARG(str, "Descargando datos históricos..."))
                
                df = self.trader.market_data.get_candles(asset, 60, num_candles, time.time())
                
                if df.empty:
                    QMetaObject.invokeMethod(self, "log_error",
                                            Qt.QueuedConnection,
                                            Q_ARG(str, "No se pudieron obtener datos"))
                    QMetaObject.invokeMethod(self.btn_train, "setEnabled",
                                            Qt.QueuedConnection,
                                            Q_ARG(bool, True))
                    QMetaObject.invokeMethod(self.btn_train, "setText",
                                            Qt.QueuedConnection,
                                            Q_ARG(str, "🎓 ENTRENAR MODELO"))
                    return
                
                QMetaObject.invokeMethod(self.progress_train, "setValue",
                                        Qt.QueuedConnection,
                                        Q_ARG(int, 20))
                QMetaObject.invokeMethod(self, "log",
                                        Qt.QueuedConnection,
                                        Q_ARG(str, f"✅ Descargadas {len(df)} velas"))
                
                # Procesar indicadores
                QMetaObject.invokeMethod(self.lbl_train_status, "setText",
                                        Qt.QueuedConnection,
                                        Q_ARG(str, "Calculando indicadores técnicos..."))
                
                df_processed = self.trader.feature_engineer.prepare_for_rl(df)
                
                if df_processed.empty:
                    QMetaObject.invokeMethod(self, "log_error",
                                            Qt.QueuedConnection,
                                            Q_ARG(str, "Error procesando indicadores"))
                    QMetaObject.invokeMethod(self.btn_train, "setEnabled",
                                            Qt.QueuedConnection,
                                            Q_ARG(bool, True))
                    QMetaObject.invokeMethod(self.btn_train, "setText",
                                            Qt.QueuedConnection,
                                            Q_ARG(str, "🎓 ENTRENAR MODELO"))
                    return
                
                QMetaObject.invokeMethod(self.progress_train, "setValue",
                                        Qt.QueuedConnection,
                                        Q_ARG(int, 40))
                QMetaObject.invokeMethod(self, "log",
                                        Qt.QueuedConnection,
                                        Q_ARG(str, f"✅ Indicadores calculados ({df_processed.shape[1]} features)"))
                
                # Crear entorno
                QMetaObject.invokeMethod(self.lbl_train_status, "setText",
                                        Qt.QueuedConnection,
                                        Q_ARG(str, "Creando entorno de simulación..."))
                
                from env.trading_env import BinaryOptionsEnv
                from stable_baselines3.common.vec_env import DummyVecEnv
                
                env = DummyVecEnv([lambda: BinaryOptionsEnv(
                    df=df_processed,
                    window_size=10,
                    initial_balance=1000
                )])
                
                QMetaObject.invokeMethod(self.progress_train, "setValue",
                                        Qt.QueuedConnection,
                                        Q_ARG(int, 50))
                QMetaObject.invokeMethod(self, "log",
                                        Qt.QueuedConnection,
                                        Q_ARG(str, "✅ Entorno creado"))
                
                # Entrenar
                QMetaObject.invokeMethod(self.lbl_train_status, "setText",
                                        Qt.QueuedConnection,
                                        Q_ARG(str, f"Entrenando modelo ({timesteps} pasos)..."))
                
                self.trader.agent.env = env
                
                import time
                start_time = time.time()
                self.trader.agent.train(timesteps=timesteps)
                elapsed = time.time() - start_time
                
                QMetaObject.invokeMethod(self.progress_train, "setValue",
                                        Qt.QueuedConnection,
                                        Q_ARG(int, 100))
                QMetaObject.invokeMethod(self, "log",
                                        Qt.QueuedConnection,
                                        Q_ARG(str, f"✅ Entrenamiento completado en {elapsed:.1f}s"))
                
                # Actualizar estado
                QMetaObject.invokeMethod(self.lbl_model_status, "setText",
                                        Qt.QueuedConnection,
                                        Q_ARG(str, "✅ Modelo Entrenado"))
                QMetaObject.invokeMethod(self.lbl_model_info, "setText",
                                        Qt.QueuedConnection,
                                        Q_ARG(str, f"Entrenado con {len(df_processed)} velas"))
                
                # Métricas
                metrics_text = f"""
Entrenamiento Completado:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Activo: {asset}
• Velas: {len(df_processed)}
• Features: {df_processed.shape[1]}
• Timesteps: {timesteps}
• Tiempo: {elapsed:.1f}s
• Modelo: {self.trader.agent.model_path}.zip
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                """
                QMetaObject.invokeMethod(self.txt_train_metrics, "setText",
                                        Qt.QueuedConnection,
                                        Q_ARG(str, metrics_text))
                
                QMetaObject.invokeMethod(self.btn_train, "setEnabled",
                                        Qt.QueuedConnection,
                                        Q_ARG(bool, True))
                QMetaObject.invokeMethod(self.btn_train, "setText",
                                        Qt.QueuedConnection,
                                        Q_ARG(str, "🎓 ENTRENAR MODELO"))
                QMetaObject.invokeMethod(self.lbl_train_status, "setText",
                                        Qt.QueuedConnection,
                                        Q_ARG(str, "✅ Listo"))
                
            except Exception as e:
                QMetaObject.invokeMethod(self, "log_error",
                                        Qt.QueuedConnection,
                                        Q_ARG(str, f"Error en entrenamiento: {e}"))
                import traceback
                traceback.print_exc()
                QMetaObject.invokeMethod(self.btn_train, "setEnabled",
                                        Qt.QueuedConnection,
                                        Q_ARG(bool, True))
                QMetaObject.invokeMethod(self.btn_train, "setText",
                                        Qt.QueuedConnection,
                                        Q_ARG(str, "🎓 ENTRENAR MODELO"))
                QMetaObject.invokeMethod(self.lbl_train_status, "setText",
                                        Qt.QueuedConnection,
                                        Q_ARG(str, "❌ Error"))
        
        Thread(target=train_async, daemon=True).start()
    
    @Slot()
    def retrain_model(self):
        """Re-entrena el modelo con datos recientes"""
        if not self.trader.market_data.connected:
            self.log_error("Debes conectarte primero")
            return
        
        self.log("🔄 Re-entrenando con datos recientes...")
        
        from threading import Thread
        def retrain_async():
            try:
                from core.auto_trainer import AutoTrainer
                auto_trainer = AutoTrainer(
                    self.trader.market_data,
                    self.trader.feature_engineer
                )
                
                asset = self.combo_asset.currentText()
                success = auto_trainer.train_on_recent_data(asset, num_candles=1440)
                
                if success:
                    self.log("✅ Re-entrenamiento completado")
                    self.lbl_model_status.setText("✅ Modelo Actualizado")
                else:
                    self.log_error("Error en re-entrenamiento")
            except Exception as e:
                self.log_error(f"Error: {e}")
        
        Thread(target=retrain_async, daemon=True).start()
    
    def update_indicators(self, data):
        """Actualiza los indicadores en la interfaz"""
        if data is None:
            return
            
        # Manejar DataFrame o Series
        if isinstance(data, pd.DataFrame):
            if data.empty: return
            last_row = data.iloc[-1]
        else:
            # Asumir que es Series o dict (una vela)
            last_row = data
        
        # RSI
        if 'rsi' in last_row:
            rsi = last_row['rsi']
            color = "#ff4757" if rsi > 70 else "#00d4aa" if rsi < 30 else "#e0e0e0"
            self.lbl_rsi.setText(f"RSI: {rsi:.1f}")
            self.lbl_rsi.setStyleSheet(f"color: {color}; font-weight: bold;")
        
        # MACD
        if 'macd' in last_row:
            macd = last_row['macd']
            color = "#00d4aa" if macd > 0 else "#ff4757"
            self.lbl_macd.setText(f"MACD: {macd:.5f}")
            self.lbl_macd.setStyleSheet(f"color: {color}; font-weight: bold;")
        
        # Bollinger
        if 'bb_width' in last_row:
            bb = last_row['bb_width']
            self.lbl_bb.setText(f"BB Width: {bb:.5f}")
        
        # ATR
        if 'atr' in last_row:
            atr = last_row['atr']
            self.lbl_atr.setText(f"ATR: {atr:.5f}")
    
    def update_trading_stats(self, wins, losses, total_profit):
        """Actualiza estadísticas de trading"""
        total = wins + losses
        
        self.lbl_total_trades.setText(str(total))
        self.lbl_wins.setText(str(wins))
        self.lbl_losses.setText(str(losses))
        
        if total > 0:
            winrate = (wins / total) * 100
            self.lbl_winrate.setText(f"{winrate:.1f}%")
            self.lbl_winrate_detail.setText(f"{winrate:.1f}%")
        
        # Profit
        color = "#00d4aa" if total_profit >= 0 else "#ff4757"
        self.lbl_profit.setText(f"${total_profit:.2f}")
        self.lbl_profit.setStyleSheet(f"color: {color}; font-size: 18px; font-weight: bold;")
        self.lbl_total_profit.setText(f"${total_profit:.2f}")
        self.lbl_total_profit.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 14px;")
    
    def add_trade_to_history(self, asset, trade_type, amount, result):
        """Agrega operación al historial"""
        row = self.table_history.rowCount()
        self.table_history.insertRow(row)
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        self.table_history.setItem(row, 0, QTableWidgetItem(timestamp))
        self.table_history.setItem(row, 1, QTableWidgetItem(asset))
        self.table_history.setItem(row, 2, QTableWidgetItem(trade_type))
        self.table_history.setItem(row, 3, QTableWidgetItem(f"${amount:.2f}"))
        
        result_item = QTableWidgetItem(f"${result:.2f}")
        if result > 0:
            result_item.setForeground(QColor("#00d4aa"))
        else:
            result_item.setForeground(QColor("#ff4757"))
        self.table_history.setItem(row, 4, result_item)
        
        # Scroll al final
        self.table_history.scrollToBottom()
        
        # Limitar a 50 filas
        if self.table_history.rowCount() > 50:
            self.table_history.removeRow(0)
    
    def update_martingale_status(self, level, next_amount):
        """Actualiza estado de martingala"""
        self.lbl_martingale_level.setText(f"Nivel: {level}")
        self.lbl_next_amount.setText(f"Próximo monto: ${next_amount:.2f}")
        
        if level > 0:
            self.lbl_martingale_level.setStyleSheet("font-size: 14px; color: #ff4757; font-weight: bold;")
        else:
            self.lbl_martingale_level.setStyleSheet("font-size: 14px; color: #00d4aa;")
    
    def add_signal(self, signal_text):
        """Agrega señal al panel de análisis"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.txt_signals.append(f'<span style="color: #00d4aa;">[{timestamp}]</span> {signal_text}')
    
    def check_model_status(self):
        """Verifica si hay un modelo entrenado"""
        import os
        from config import Config
        
        if os.path.exists(Config.MODEL_PATH + ".zip"):
            self.lbl_model_status.setText("✅ Modelo Cargado")
            self.lbl_model_status.setStyleSheet("font-size: 14px; font-weight: bold; color: #00d4aa;")
            self.lbl_model_info.setText("Modelo listo para operar")
            self.log("✅ Modelo RL encontrado y cargado")
        else:
            self.lbl_model_status.setText("❌ No Entrenado")
            self.lbl_model_status.setStyleSheet("font-size: 14px; font-weight: bold; color: #ff4757;")
            self.lbl_model_info.setText("Entrena el modelo antes de operar")
            self.log("⚠️ No se encontró modelo entrenado")

    def on_expiration_mode_changed(self):
        """Maneja el cambio de modo de expiración"""
        from config import Config
        
        if self.radio_auto_expiration.isChecked():
            # Modo automático
            Config.AUTO_EXPIRATION = True
            self.spin_manual_expiration.setEnabled(False)
            self.log("⏱️ Modo de expiración: AUTOMÁTICO (IA decide)")
        else:
            # Modo manual
            Config.AUTO_EXPIRATION = False
            self.spin_manual_expiration.setEnabled(True)
            Config.MANUAL_EXPIRATION = self.spin_manual_expiration.value()
            self.log(f"⏱️ Modo de expiración: MANUAL ({Config.MANUAL_EXPIRATION} min)")
    
    def on_manual_expiration_changed(self, value):
        """Actualiza el tiempo de expiración manual"""
        from config import Config
        Config.MANUAL_EXPIRATION = value
        if not Config.AUTO_EXPIRATION:
            self.log(f"⏱️ Tiempo de expiración actualizado: {value} min")

    def setup_console_redirect(self):
        """Redirige los prints de consola a la GUI (ultra optimizado para evitar congelamiento)"""
        import sys
        
        class ConsoleRedirect:
            def __init__(self, log_callback):
                self.log_callback = log_callback
                self.buffer = ""
                self.last_log_time = time.time()
                self.skip_patterns = ['Próximo escaneo', 'QFont', 'Iteración #', 'DEBUG']
            
            def write(self, text):
                try:
                    # Acumular texto
                    self.buffer += text
                    
                    # Limitar frecuencia de logs (máximo cada 0.5 segundos para evitar congelamiento)
                    current_time = time.time()
                    if current_time - self.last_log_time < 0.5:
                        return
                    
                    # Si hay un salto de línea, enviar el mensaje
                    if '\n' in self.buffer:
                        lines = self.buffer.split('\n')
                        for line in lines[:-1]:  # Todas menos la última (incompleta)
                            if line.strip():  # Solo si no está vacía
                                # Filtrar mensajes repetitivos y debug
                                if not any(skip in line for skip in self.skip_patterns):
                                    # Usar QMetaObject para thread-safety
                                    try:
                                        QMetaObject.invokeMethod(
                                            self.log_callback.__self__,
                                            "log",
                                            Qt.QueuedConnection,
                                            Q_ARG(str, line.strip())
                                        )
                                    except:
                                        pass
                        self.buffer = lines[-1]  # Guardar la línea incompleta
                        self.last_log_time = current_time
                except:
                    pass
            
            def flush(self):
                try:
                    if self.buffer.strip():
                        QMetaObject.invokeMethod(
                            self.log_callback.__self__,
                            "log",
                            Qt.QueuedConnection,
                            Q_ARG(str, self.buffer.strip())
                        )
                        self.buffer = ""
                except:
                    pass
        
        # Redirigir stdout (prints normales) - DESACTIVADO para evitar congelamiento
        # sys.stdout = ConsoleRedirect(self.log)
        
        # Mantener stdout original para debugging
        print("[GUI] Redirección de consola desactivada para mejor rendimiento")

    def mark_trade_on_chart(self, price, trade_type):
        """Marca una operación en el gráfico"""
        try:
            # Obtener posición X (última vela)
            x_pos = len(self.candle_items) // 2 if self.candle_items else 0
            
            # Color según tipo de operación
            if trade_type.upper() == 'CALL':
                color = '#00d4aa'  # Verde
                symbol = 't'  # Triángulo hacia arriba
            else:
                color = '#ff4757'  # Rojo
                symbol = 't1'  # Triángulo hacia abajo
            
            # Agregar marcador
            scatter = pg.ScatterPlotItem(
                [x_pos],
                [price],
                size=20,
                pen=pg.mkPen(color=color, width=2),
                brush=pg.mkBrush(color=color),
                symbol=symbol
            )
            self.chart.addItem(scatter)
            
            # Guardar referencia
            if trade_type.upper() == 'CALL':
                self.buy_markers.append(scatter)
            else:
                self.sell_markers.append(scatter)
            
        except Exception as e:
            pass
    
    def clear_chart(self):
        """Limpia el gráfico"""
        try:
            # Limpiar velas
            for item in self.candle_items:
                self.chart.removeItem(item)
            self.candle_items = []
            
            # Limpiar marcadores
            for marker in self.buy_markers + self.sell_markers:
                self.chart.removeItem(marker)
            self.buy_markers = []
            self.sell_markers = []
            
            self.candle_data = []
        except Exception as e:
            print(f"[GUI ERROR] Error limpiando gráfico: {e}")
    
    def closeEvent(self, event):
        """Maneja el cierre de la ventana de forma segura"""
        try:
            print("\n[GUI] Cerrando aplicación...")
            
            # Detener el bot si está corriendo
            if hasattr(self, 'trader') and self.trader:
                if self.trader.isRunning():
                    print("[GUI] Deteniendo bot...")
                    self.trader.running = False
                    self.trader.paused = False
                    
                    # Intentar detener el thread de forma ordenada
                    if not self.trader.wait(3000):  # Esperar máximo 3 segundos
                        print("[GUI] Forzando detención del thread...")
                        self.trader.quit()
                        if not self.trader.wait(1000):
                            print("[GUI] Terminando thread forzosamente...")
                            self.trader.terminate()
                            self.trader.wait()
            
            # Desconectar del broker y cerrar WebSocket
            if hasattr(self, 'trader') and hasattr(self.trader, 'market_data'):
                if self.trader.market_data and self.trader.market_data.connected:
                    print("[GUI] Desconectando del broker...")
                    try:
                        # Cerrar API/WebSocket si existe
                        if hasattr(self.trader.market_data, 'api') and self.trader.market_data.api:
                            if hasattr(self.trader.market_data.api, 'close'):
                                self.trader.market_data.api.close()
                        self.trader.market_data.connected = False
                    except Exception as e:
                        print(f"[GUI] Error desconectando: {e}")
            
            print("[GUI] Aplicación cerrada correctamente")
            event.accept()
        
        except Exception as e:
            print(f"[GUI ERROR] Error al cerrar: {e}")
            # Forzar cierre de todos modos
            event.accept()
