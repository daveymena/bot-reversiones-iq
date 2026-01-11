import subprocess
import time
import sys

def run_system():
    print("🚀 INICIANDO SISTEMA NEURAL ANTIGRAVITY...")
    
    # 1. Iniciar el API Bridge (Dashboard)
    print("🌐 Iniciando API Bridge en puerto 8080...")
    bridge = subprocess.Popen([sys.executable, "api_bridge.py"])
    
    # Esperar un poco a que el bridge esté listo
    time.sleep(3)
    
    # 2. Iniciar el Bot de Trading
    print("🧠 Iniciando Bot de Aprendizaje Inteligente...")
    bot = subprocess.Popen([sys.executable, "intelligent_learning.py"])
    
    try:
        # Mantener ambos procesos corriendo
        while True:
            if bridge.poll() is not None:
                print("⚠️ API Bridge se detuvo. Reiniciando...")
                bridge = subprocess.Popen([sys.executable, "api_bridge.py"])
            
            if bot.poll() is not None:
                print("⚠️ El Bot se detuvo. Reiniciando...")
                bot = subprocess.Popen([sys.executable, "intelligent_learning.py"])
                
            time.sleep(10)
    except KeyboardInterrupt:
        print("\n🛑 Apagando sistema...")
        bridge.terminate()
        bot.terminate()

if __name__ == "__main__":
    run_system()
