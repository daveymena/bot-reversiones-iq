#!/usr/bin/env python3
"""
Launcher para la GUI Moderna del Bot
Detecta automáticamente si debe usar modo local o remoto
"""
import sys
import os
from PySide6.QtWidgets import QApplication, QMessageBox, QInputDialog
from PySide6.QtCore import Qt

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Trading Bot Pro")
    app.setOrganizationName("TradingBot")
    
    # Preguntar modo de operación
    from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QLineEdit, QRadioButton, QButtonGroup
    
    dialog = QDialog()
    dialog.setWindowTitle("🤖 Trading Bot - Modo de Operación")
    dialog.setMinimumWidth(400)
    
    layout = QVBoxLayout()
    
    # Título
    title = QLabel("Selecciona el modo de operación:")
    title.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 10px;")
    layout.addWidget(title)
    
    # Opciones
    btn_group = QButtonGroup()
    
    radio_local = QRadioButton("💻 Modo Local (Bot en esta PC)")
    radio_local.setChecked(True)
    btn_group.addButton(radio_local)
    layout.addWidget(radio_local)
    
    radio_remote = QRadioButton("🌐 Modo Remoto (Backend en Easypanel)")
    btn_group.addButton(radio_remote)
    layout.addWidget(radio_remote)
    
    # URL del backend (solo visible en modo remoto)
    url_label = QLabel("URL del Backend:")
    url_input = QLineEdit()
    url_input.setPlaceholderText("https://tu-bot.easypanel.host")
    url_input.setText(os.getenv("BACKEND_URL", "http://localhost:8000"))
    url_input.setEnabled(False)
    
    layout.addWidget(url_label)
    layout.addWidget(url_input)
    
    # Habilitar/deshabilitar URL según selección
    def on_mode_changed():
        is_remote = radio_remote.isChecked()
        url_label.setEnabled(is_remote)
        url_input.setEnabled(is_remote)
    
    radio_local.toggled.connect(on_mode_changed)
    radio_remote.toggled.connect(on_mode_changed)
    
    # Botón OK
    btn_ok = QPushButton("✅ Continuar")
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
            
            return app.exec()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
