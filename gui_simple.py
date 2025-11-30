"""
Interfaz Gráfica Simple y Robusta para el Bot de Trading
Creada desde cero para evitar crashes
"""
import sys
import threading
import time
from datetime import datetime
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QPushButton, QTextEdit, QLabel, 
                               QComboBox, QLineEdit, QGroupBox)
from PySide6.QtCore import QTimer, Signal, QObject
from PySide6.QtGui import QFont

from config import Config
from data.market_data import MarketDataHandler
from strategies.technical import FeatureEngineer
from core.agent import RLAgent
from core.risk import RiskManager
from core.asset_manager import AssetManager
from core.trade_intelligence import TradeIntelligence
from core.continuous_learner import ContinuousLearner
from core.decision_validator import DecisionValidator
from ai.llm_client import LLMClient

class BotSignals(QObject):
    """Señales para comunicación thread-safe"""
    log_signal = Signal(str)
    status_signal = Signal(str)
    balance_signal = Signal(str)

class TradingBot:
    """Bot de trading que corre en thread separado"""
    def __init__(self, signals):
        self.signals = signals
        self.running = False
        self.connected = False
        
        # Componentes
        self.market_data = None
        self.feature_engineer = FeatureEngineer()
        self.agent = RLAgent(model_path=Config.MODEL_PATH)
        self.risk_manager = RiskManager(
            Config.CAPITAL_PER_TRADE,
            Config.STOP_LOSS_PCT,
            Config.TAKE_PROFIT_PCT
        )
        self.asset_manager = None
        self.llm_client = LLMClient()
        self.trade_intelligence = TradeIntelligence(llm_client=self.llm_client)
        self.continuous_learner = None
        self.decision_validator = DecisionValidator()
        
        # Estado
        self.active_trades = []
        self.consecutive_losses = 0
        self.cooldown_until = 0
        
    def log(self, msg):
        """Log thread-safe"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.signals.log_signal.emit(f"[{timestamp}] {msg}")
    
    def connect(self, email, password):
        """Conectar al broker"""
        try:
            self.log("Conectando al broker...")
            self.market_data = MarketDataHandler(
                broker_name=Config.BROKER_NAME,
                account_type=Config.ACCOUNT_TYPE
            )
            
            if Config.BROKER_NAME == "exnova":
                success = self.market_data.connect(email, password)
            else:
                success = self.market_data.connect(email, password)
            
            if success:
                self.connected = True
                self.asset_manager = AssetManager(self.market_data)
                self.continuous_learner = ContinuousLearner(
                    self.agent,
                    self.feature_engineer,
                    self.market_data
                )
                
                # Obtener balance
                try:
                    balance = self.market_data.get_balance()
                    self.signals.balance_signal.emit(f"${balance:.2f}")
                    self.log(f"Conectado exitosamente - Balance: ${balance:.2f}")
                    self.log(f"Modo: {Config.ACCOUNT_TYPE}")
                except:
                    self.log("Conectado exitosamente")
                
                self.signals.status_signal.emit("Conectado")
                return True
            else:
                self.log("Error: No se pudo conectar")
                self.signals.status_signal.emit("Desconectado")
                return False
                
        except Exception as e:
            self.log(f"Error conectando: {e}")
            self.signals.status_signal.emit("Error")
            return False
    
    def start_trading(self):
        """Iniciar trading"""
        if not self.connected:
            self.log("Error: No conectado al broker")
            return
        
        self.running = True
        self.signals.status_signal.emit("Operando")
        self.log("Bot iniciado - Buscando oportunidades...")
        
        # Iniciar en thread separado
        thread = threading.Thread(target=self._trading_loop, daemon=True)
        thread.start()
    
    def stop_trading(self):
        """Detener trading"""
        self.running = False
        self.signals.status_signal.emit("Detenido")
        self.log("Bot detenido")
    
    def _trading_loop(self):
        """Loop principal de trading"""
        try:
            while self.running:
                try:
                    # Verificar cooldown
                    if time.time() < self.cooldown_until:
                        time.sleep(5)
                        continue
                    
                    # Verificar operaciones activas
                    if self.active_trades:
                        self._check_active_trades()
                        time.sleep(2)
                        continue
                    
                    # Buscar oportunidad
                    self.log("Escaneando oportunidades...")
                    opportunity = self.asset_manager.scan_best_opportunity(
                        self.feature_engineer
                    )
                    
                    if not opportunity:
                        self.log("Sin oportunidades claras")
                        time.sleep(10)
                        continue
                    
                    # Ejecutar operación
                    self._execute_trade(opportunity)
                    time.sleep(5)
                    
                except Exception as e:
                    self.log(f"Error en loop: {e}")
                    time.sleep(10)
                    
        except Exception as e:
            self.log(f"Error crítico en trading loop: {e}")
            self.running = False
            self.signals.status_signal.emit("Error")
    
    def _execute_trade(self, opportunity):
        """Ejecutar una operación"""
        try:
            asset = opportunity.get('asset')
            action = opportunity.get('action', 'call')
            score = opportunity.get('score', 0)
            
            self.log(f"Oportunidad: {action.upper()} en {asset} (Score: {score})")
            self.log(f"Ejecutando operación...")
            
            # Obtener datos
            df = self.market_data.get_candles(asset, Config.TIMEFRAME, 200)
            if df.empty:
                self.log("Error: No se pudieron obtener datos")
                return
            
            df = self.feature_engineer.prepare_for_rl(df)
            if df.empty:
                self.log("Error: Datos inválidos")
                return
            
            current_price = df.iloc[-1]['close']
            expiration = 3  # 3 minutos
            
            # Ejecutar en broker
            if Config.BROKER_NAME == "exnova":
                success, order_id = self.market_data.api.buy(
                    Config.CAPITAL_PER_TRADE,
                    asset,
                    action,
                    expiration
                )
            else:
                success, order_id = self.market_data.api.buy(
                    Config.CAPITAL_PER_TRADE,
                    asset,
                    action,
                    expiration
                )
            
            if success:
                self.log(f"✅ Operación ejecutada - ID: {order_id}")
                self.active_trades.append({
                    'id': order_id,
                    'asset': asset,
                    'direction': action,
                    'entry_price': current_price,
                    'entry_time': time.time(),
                    'duration': expiration * 60,
                    'amount': Config.CAPITAL_PER_TRADE
                })
            else:
                self.log("❌ Error ejecutando operación")
                
        except Exception as e:
            self.log(f"Error en ejecución: {e}")
    
    def _check_active_trades(self):
        """Verificar operaciones activas"""
        try:
            for trade in self.active_trades[:]:
                wait_time = trade['duration'] + 10
                if time.time() - trade['entry_time'] >= wait_time:
                    self._process_result(trade)
                    self.active_trades.remove(trade)
        except Exception as e:
            self.log(f"Error verificando trades: {e}")
    
    def _process_result(self, trade):
        """Procesar resultado de operación"""
        try:
            self.log(f"Verificando resultado de operación {trade['id']}...")
            
            # Obtener resultado del broker
            if Config.BROKER_NAME == "exnova":
                result_status, profit = self.market_data.api.check_win_v4(trade['id'])
            else:
                profit = self.market_data.api.check_win_v3(trade['id'])
                result_status = "win" if profit > 0 else "loose"
            
            won = profit > 0
            
            if won:
                self.log(f"✅ GANADA: +${profit:.2f}")
                self.consecutive_losses = 0
            else:
                self.log(f"❌ PERDIDA: ${profit:.2f}")
                self.consecutive_losses += 1
                self.cooldown_until = time.time() + 300  # 5 minutos
                self.log(f"Cooldown: 5 minutos")
            
            # Actualizar balance
            try:
                balance = self.market_data.get_balance()
                self.signals.balance_signal.emit(f"${balance:.2f}")
            except:
                pass
                
        except Exception as e:
            self.log(f"Error procesando resultado: {e}")

class MainWindow(QMainWindow):
    """Ventana principal simple y robusta"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bot de Trading - Interfaz Simple")
        self.setGeometry(100, 100, 900, 600)
        
        # Señales
        self.signals = BotSignals()
        self.signals.log_signal.connect(self.add_log)
        self.signals.status_signal.connect(self.update_status)
        self.signals.balance_signal.connect(self.update_balance)
        
        # Bot
        self.bot = TradingBot(self.signals)
        
        # UI
        self.setup_ui()
        
        # Pre-cargar credenciales
        if Config.BROKER_NAME == "exnova":
            self.txt_email.setText(Config.EX_EMAIL or "")
            self.txt_password.setText(Config.EX_PASSWORD or "")
        else:
            self.txt_email.setText(Config.IQ_EMAIL or "")
            self.txt_password.setText(Config.IQ_PASSWORD or "")
    
    def setup_ui(self):
        """Configurar interfaz"""
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Título
        title = QLabel("🤖 Bot de Trading con IA")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Grupo de conexión
        conn_group = QGroupBox("Conexión")
        conn_layout = QVBoxLayout()
        
        # Email
        email_layout = QHBoxLayout()
        email_layout.addWidget(QLabel("Email:"))
        self.txt_email = QLineEdit()
        email_layout.addWidget(self.txt_email)
        conn_layout.addLayout(email_layout)
        
        # Password
        pass_layout = QHBoxLayout()
        pass_layout.addWidget(QLabel("Password:"))
        self.txt_password = QLineEdit()
        self.txt_password.setEchoMode(QLineEdit.Password)
        pass_layout.addWidget(self.txt_password)
        conn_layout.addLayout(pass_layout)
        
        # Botón conectar
        self.btn_connect = QPushButton("Conectar")
        self.btn_connect.clicked.connect(self.connect_broker)
        conn_layout.addWidget(self.btn_connect)
        
        conn_group.setLayout(conn_layout)
        layout.addWidget(conn_group)
        
        # Grupo de control
        control_group = QGroupBox("Control")
        control_layout = QHBoxLayout()
        
        self.btn_start = QPushButton("Iniciar Bot")
        self.btn_start.clicked.connect(self.start_bot)
        self.btn_start.setEnabled(False)
        control_layout.addWidget(self.btn_start)
        
        self.btn_stop = QPushButton("Detener Bot")
        self.btn_stop.clicked.connect(self.stop_bot)
        self.btn_stop.setEnabled(False)
        control_layout.addWidget(self.btn_stop)
        
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)
        
        # Estado
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("Estado:"))
        self.lbl_status = QLabel("Desconectado")
        status_layout.addWidget(self.lbl_status)
        status_layout.addWidget(QLabel("Balance:"))
        self.lbl_balance = QLabel("$0.00")
        status_layout.addWidget(self.lbl_balance)
        status_layout.addStretch()
        layout.addLayout(status_layout)
        
        # Log
        log_group = QGroupBox("Log de Operaciones")
        log_layout = QVBoxLayout()
        self.txt_log = QTextEdit()
        self.txt_log.setReadOnly(True)
        log_layout.addWidget(self.txt_log)
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)
    
    def connect_broker(self):
        """Conectar al broker"""
        email = self.txt_email.text()
        password = self.txt_password.text()
        
        if not email or not password:
            self.add_log("Error: Email y password requeridos")
            return
        
        self.btn_connect.setEnabled(False)
        self.btn_connect.setText("Conectando...")
        
        # Conectar en thread separado
        def connect_async():
            success = self.bot.connect(email, password)
            if success:
                self.btn_start.setEnabled(True)
                self.btn_connect.setText("Conectado")
            else:
                self.btn_connect.setEnabled(True)
                self.btn_connect.setText("Conectar")
        
        thread = threading.Thread(target=connect_async, daemon=True)
        thread.start()
    
    def start_bot(self):
        """Iniciar bot"""
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.bot.start_trading()
    
    def stop_bot(self):
        """Detener bot"""
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.bot.stop_trading()
    
    def add_log(self, msg):
        """Agregar mensaje al log"""
        self.txt_log.append(msg)
        # Auto-scroll
        scrollbar = self.txt_log.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def update_status(self, status):
        """Actualizar estado"""
        self.lbl_status.setText(status)
    
    def update_balance(self, balance):
        """Actualizar balance"""
        self.lbl_balance.setText(balance)

def main():
    app = QApplication(sys.argv)
    
    # Estilo simple
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error fatal: {e}")
        import traceback
        traceback.print_exc()
        input("Presiona Enter para salir...")
