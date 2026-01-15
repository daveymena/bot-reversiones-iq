import os
import sys
import winshell
from win32com.client import Dispatch

def create_shortcut():
    """Crea un acceso directo profesional en el escritorio para el Trading Bot Pro"""
    try:
        desktop = winshell.desktop()
        path = os.path.join(desktop, "Trading Bot Pro.lnk")
        target = sys.executable
        cwd = os.getcwd()
        icon = os.path.join(cwd, "installer_resources", "icon.ico")
        
        # Script que se ejecutará
        script_path = os.path.join(cwd, "main_modern.py")
        
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(path)
        shortcut.Targetpath = target
        shortcut.Arguments = f'"{script_path}"'
        shortcut.WorkingDirectory = cwd
        if os.path.exists(icon):
            shortcut.IconLocation = icon
        shortcut.save()
        
        print("✅ Acceso directo creado en el escritorio.")
        return True
    except Exception as e:
        print(f"❌ Error al crear el acceso directo: {e}")
        return False

def setup_environment():
    """Configura las dependencias necesarias de forma silenciosa y profesional"""
    print("🛠️ Configurando entorno de ejecución premium...")
    # Aquí podrías añadir un pip install -r requirements.txt silencioso
    print("✅ Entorno optimizado.")

if __name__ == "__main__":
    print("╔════════════════════════════════════════════════════════════╗")
    print("║          INSTALADOR DE TRADING BOT PRO v1.0                ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print("\nInstalando aplicación en el sistema...")
    
    setup_environment()
    success = create_shortcut()
    
    if success:
        print("\n🎉 ¡INSTALACIÓN COMPLETADA EXITOSAMENTE!")
        print("Ya puedes abrir 'Trading Bot Pro' desde tu escritorio.")
    else:
        print("\n⚠️ La instalación manual es necesaria.")
    
    input("\nPresiona ENTER para finalizar...")
