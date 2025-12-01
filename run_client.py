"""
Cliente de Escritorio - Se conecta al servidor remoto
Este archivo inicia la GUI en modo cliente, conectándose al backend en EasyPanel
"""
import sys
from PySide6.QtWidgets import QApplication
from gui.modern_main_window_client import ModernMainWindowClient

def main():
    # URL del servidor (puede ser configurada por el usuario)
    SERVER_URL = "http://localhost:8000"  # Cambiar a URL de EasyPanel cuando esté desplegado
    
    # Iniciar GUI en modo cliente
    app = QApplication(sys.argv)
    window = ModernMainWindowClient(server_url=SERVER_URL)
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
