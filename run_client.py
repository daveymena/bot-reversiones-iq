"""
Cliente de Escritorio - Se conecta al servidor remoto
Este archivo inicia la GUI en modo cliente, conectándose al backend en EasyPanel
"""
import sys
import os
from PySide6.QtWidgets import QApplication, QInputDialog
from gui.modern_main_window_client import ModernMainWindowClient

def get_server_url():
    """Lee o solicita la URL del servidor"""
    config_file = "server_config.txt"
    
    # Intentar leer desde archivo de configuración
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                url = f.read().strip()
                if url:
                    return url
        except:
            pass
    
    # Si no existe o está vacío, solicitar al usuario
    app = QApplication.instance() or QApplication(sys.argv)
    url, ok = QInputDialog.getText(
        None,
        "Configuración del Servidor",
        "Ingresa la URL del servidor backend:\n(ej: https://trading-bot.tudominio.easypanel.host)",
        text="http://localhost:8000"
    )
    
    if ok and url:
        # Guardar para próximas ejecuciones
        try:
            with open(config_file, 'w') as f:
                f.write(url)
        except:
            pass
        return url
    else:
        return "http://localhost:8000"

def main():
    # Obtener URL del servidor
    SERVER_URL = get_server_url()
    
    # Iniciar GUI en modo cliente
    app = QApplication.instance() or QApplication(sys.argv)
    window = ModernMainWindowClient(server_url=SERVER_URL)
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

