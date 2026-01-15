import sys
import os
import time
from PySide6.QtWidgets import QApplication, QMessageBox, QInputDialog, QSplashScreen, QProgressBar
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QColor, QLinearGradient

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Trading Bot Pro")
    app.setOrganizationName("TradingBot")
    
    # Splash Screen Premium
    splash_pix = QPixmap(600, 400)
    splash_pix.fill(QColor("#0f111a"))
    
    splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
    splash.show()
    
    # Mensaje de Carga en el Splash
    splash.showMessage("🚀 INITIALIZING TRADING ENGINE...", Qt.AlignBottom | Qt.AlignCenter, QColor("#00d4aa"))
    
    # Simular carga de módulos pesados con estilo
    for i in range(1, 101):
        if i == 20: splash.showMessage("🧠 LOADING AI MODELS...", Qt.AlignBottom | Qt.AlignCenter, QColor("#00d4aa"))
        if i == 50: splash.showMessage("📊 SYNCHRONIZING INDICATORS...", Qt.AlignBottom | Qt.AlignCenter, QColor("#00d4aa"))
        if i == 80: splash.showMessage("🛡️ SECURING CONNECTION...", Qt.AlignBottom | Qt.AlignCenter, QColor("#00d4aa"))
        
        # splash.repaint() # No necesario con timer pero bueno para simular
        time.sleep(0.01) # Simulación de carga rápida
    
    splash.showMessage("✅ SYSTEM READY", Qt.AlignBottom | Qt.AlignCenter, QColor("#00d4aa"))
    time.sleep(0.5)
    
    # Preguntar modo de operación
    from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QLineEdit, QRadioButton, QButtonGroup
    
    dialog = QDialog()
    dialog.setWindowTitle("🚀 Trading Bot Pro - Setup")
    dialog.setMinimumWidth(500)
    dialog.setMinimumHeight(350)
    
    # Estilo Premium para el Diálogo
    dialog.setStyleSheet("""
        QDialog {
            background-color: #0f111a;
            border: 1px solid #1e2235;
            border-radius: 15px;
        }
        QLabel {
            color: #ffffff;
            font-family: 'Segoe UI', Arial;
        }
        QRadioButton {
            color: #a0a8c0;
            font-size: 14px;
            padding: 10px;
            background-color: #161925;
            border-radius: 8px;
            margin-bottom: 5px;
        }
        QRadioButton:hover {
            background-color: #1e2235;
            color: #ffffff;
        }
        QRadioButton:checked {
            background-color: #252b45;
            border: 1px solid #00d4aa;
            color: #00d4aa;
        }
        QLineEdit {
            background-color: #161925;
            border: 1px solid #2d3142;
            border-radius: 6px;
            padding: 10px;
            color: #ffffff;
        }
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #00d4aa, stop:1 #00b894);
            color: #0f111a;
            border: none;
            border-radius: 8px;
            padding: 12px;
            font-size: 15px;
            font-weight: bold;
        }
        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #00e6bd, stop:1 #00d4aa);
        }
    """)
    
    layout = QVBoxLayout()
    layout.setContentsMargins(30, 30, 30, 30)
    layout.setSpacing(15)
    
    # Header con Icono
    header_layout = QHBoxLayout()
    icon_label = QLabel("🤖")
    icon_label.setStyleSheet("font-size: 40px;")
    header_layout.addWidget(icon_label)
    
    title_layout = QVBoxLayout()
    title = QLabel("TRADING BOT PRO")
    title.setStyleSheet("font-size: 24px; font-weight: 900; color: #00d4aa; letter-spacing: 2px;")
    subtitle = QLabel("The most advanced AI-powered trading solution")
    subtitle.setStyleSheet("font-size: 12px; color: #636e72;")
    title_layout.addWidget(title)
    title_layout.addWidget(subtitle)
    header_layout.addLayout(title_layout)
    header_layout.addStretch()
    layout.addLayout(header_layout)
    
    layout.addSpacing(10)
    
    # Opciones de Modo
    mode_label = QLabel("SELECCIONA MODO DE INSTALACIÓN:")
    mode_label.setStyleSheet("font-size: 11px; font-weight: bold; color: #636e72; text-transform: uppercase;")
    layout.addWidget(mode_label)
    
    btn_group = QButtonGroup(dialog)
    
    radio_local = QRadioButton("💻 INSTALACIÓN LOCAL (MÁXIMO RENDIMIENTO)")
    radio_local.setChecked(True)
    btn_group.addButton(radio_local)
    layout.addWidget(radio_local)
    
    radio_remote = QRadioButton("🌐 CONEXIÓN REMOTA (SaaS / CLOUD)")
    btn_group.addButton(radio_remote)
    layout.addWidget(radio_remote)
    
    # Sección Remota
    remote_section = QWidget()
    remote_layout = QVBoxLayout(remote_section)
    remote_layout.setContentsMargins(0, 0, 0, 0)
    
    url_label = QLabel("ENDPOINT DEL SERVIDOR:")
    url_label.setStyleSheet("font-size: 11px; font-weight: bold; color: #636e72;")
    url_input = QLineEdit()
    url_input.setPlaceholderText("https://api.tradingbotpro.cloud")
    url_input.setText(os.getenv("BACKEND_URL", "http://localhost:8000"))
    
    remote_layout.addWidget(url_label)
    remote_layout.addWidget(url_input)
    remote_section.setVisible(False)
    layout.addWidget(remote_section)
    
    # Conexión lógica
    def on_mode_changed():
        is_remote = radio_remote.isChecked()
        remote_section.setVisible(is_remote)
    
    radio_local.toggled.connect(on_mode_changed)
    radio_remote.toggled.connect(on_mode_changed)
    
    layout.addStretch()
    
    # Botón Principal
    btn_ok = QPushButton("🚀 INSTALAR Y COMENZAR")
    btn_ok.clicked.connect(dialog.accept)
    layout.addWidget(btn_ok)
    
    dialog.setLayout(layout)
    
    if dialog.exec() == QDialog.Accepted:
        if radio_local.isChecked():
            # Modo local - inicializar todos los componentes
            from core.trader import LiveTrader
            from core.agent import RLAgent
            from core.risk import RiskManager
            from core.asset_manager import AssetManager
            from data.market_data import MarketDataHandler
            from strategies.technical import FeatureEngineer
            from gui.modern_main_window import ModernMainWindow
            
            # Inicializar componentes
            from config import Config
            
            market_data = MarketDataHandler()
            feature_engineer = FeatureEngineer()
            agent = RLAgent()
            risk_manager = RiskManager(
                capital_per_trade=Config.CAPITAL_PER_TRADE,
                stop_loss_pct=Config.STOP_LOSS_PERCENT,
                take_profit_pct=Config.TAKE_PROFIT_PERCENT
            )
            asset_manager = AssetManager(market_data)
            
            # Crear trader con todos los componentes
            trader = LiveTrader(
                market_data=market_data,
                feature_engineer=feature_engineer,
                agent=agent,
                risk_manager=risk_manager,
                asset_manager=asset_manager
            )
            
            window = ModernMainWindow(trader)
            window.show()
            splash.finish(window)
            
            return app.exec()
        else:
            # Modo remoto - usar GUI con API client
            backend_url = url_input.text().strip()
            if not backend_url:
                QMessageBox.warning(None, "Error", "Debes ingresar la URL del backend")
                return 1
            
            from gui.modern_main_window_remote import ModernMainWindowRemote
            
            window = ModernMainWindowRemote(backend_url)
            window.show()
            splash.finish(window)
            
            return app.exec()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
