from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QPushButton, QRadioButton, QButtonGroup, 
                               QGroupBox, QFormLayout, QComboBox, QCheckBox)
from PySide6.QtCore import Signal

class ConnectionWidget(QWidget):
    connect_request = Signal(str, str, str, str, str) # broker, email, password, token, account_type

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Grupo Broker
        broker_group = QGroupBox("Seleccionar Broker")
        broker_layout = QHBoxLayout()
        self.rb_iq = QRadioButton("IQ Option")
        self.rb_ex = QRadioButton("Exnova")
        self.rb_iq.setChecked(True)
        
        self.bg_broker = QButtonGroup()
        self.bg_broker.addButton(self.rb_iq)
        self.bg_broker.addButton(self.rb_ex)
        
        broker_layout.addWidget(self.rb_iq)
        broker_layout.addWidget(self.rb_ex)
        broker_group.setLayout(broker_layout)
        
        # Grupo Tipo de Cuenta
        account_group = QGroupBox("Tipo de Cuenta")
        account_layout = QHBoxLayout()
        self.rb_demo = QRadioButton("DEMO (Práctica)")
        self.rb_real = QRadioButton("REAL (Dinero Real)")
        self.rb_demo.setChecked(True)
        self.rb_real.setStyleSheet("color: #ff6b6b; font-weight: bold;")
        
        self.bg_account = QButtonGroup()
        self.bg_account.addButton(self.rb_demo)
        self.bg_account.addButton(self.rb_real)
        
        account_layout.addWidget(self.rb_demo)
        account_layout.addWidget(self.rb_real)
        account_group.setLayout(account_layout)
        
        # Grupo Credenciales
        cred_group = QGroupBox("Credenciales")
        form_layout = QFormLayout()
        
        self.txt_email = QLineEdit()
        self.txt_password = QLineEdit()
        self.txt_password.setEchoMode(QLineEdit.Password)
        self.txt_token = QLineEdit() # Opcional
        
        form_layout.addRow("Email:", self.txt_email)
        form_layout.addRow("Password:", self.txt_password)
        form_layout.addRow("Token (Opcional):", self.txt_token)
        
        cred_group.setLayout(form_layout)
        
        # Grupo Activos
        asset_group = QGroupBox("Activos")
        asset_layout = QVBoxLayout()
        
        self.combo_asset = QComboBox()
        self.combo_asset.addItems([
            "EURUSD", "GBPUSD", "USDJPY", "AUDUSD", 
            "USDCAD", "EURJPY", "GBPJPY", "AUDJPY",
            "NZDUSD", "EURGBP"
        ])
        
        self.chk_otc = QCheckBox("Usar OTC (24/7)")
        self.chk_otc.setToolTip("Activa para usar pares OTC cuando el mercado normal esté cerrado")
        
        asset_layout.addWidget(QLabel("Activo Principal:"))
        asset_layout.addWidget(self.combo_asset)
        asset_layout.addWidget(self.chk_otc)
        asset_group.setLayout(asset_layout)
        
        # Botón Conectar
        self.btn_connect = QPushButton("CONECTAR")
        self.btn_connect.setStyleSheet("background-color: #007bff; color: white; font-weight: bold; padding: 8px;")
        self.btn_connect.clicked.connect(self.on_connect_clicked)
        
        layout.addWidget(broker_group)
        layout.addWidget(account_group)
        layout.addWidget(cred_group)
        layout.addWidget(asset_group)
        layout.addWidget(self.btn_connect)
        layout.addStretch()

    def on_connect_clicked(self):
        broker = "iq" if self.rb_iq.isChecked() else "exnova"
        email = self.txt_email.text()
        password = self.txt_password.text()
        token = self.txt_token.text()
        account_type = "PRACTICE" if self.rb_demo.isChecked() else "REAL"
        self.connect_request.emit(broker, email, password, token, account_type)
    
    def get_selected_asset(self):
        asset = self.combo_asset.currentText()
        if self.chk_otc.isChecked():
            asset = asset + "-OTC"
        return asset
