import subprocess
import time
import sys
import os

def run_system():
    print("🚀 INICIANDO SISTEMA NEURAL ANTIGRAVITY (SaaS Mode)...")
    
    # Asegurar que existan los logs
    if not os.path.exists("logs"):
        os.makedirs("logs")

    def start_bridge():
        print("🌐 Iniciando API Bridge...")
        return subprocess.Popen(
            [sys.executable, "api_bridge.py"],
            stdout=open("logs/bridge_stdout.log", "a"),
            stderr=open("logs/bridge_stderr.log", "a")
        )

    def start_bot():
        print("🧠 Iniciando Bot de Trading...")
        return subprocess.Popen(
            [sys.executable, "main_telegram_bot.py"],
            stdout=open("logs/bot_stdout.log", "a"),
            stderr=open("logs/bot_stderr.log", "a")
        )

    bridge = start_bridge()
    time.sleep(5)
    bot = start_bot()
    
    try:
        while True:
            # Verificar Dashboard
            if bridge.poll() is not None:
                print("⚠️ API Bridge caído. Reiniciando en 5s...")
                time.sleep(5)
                bridge = start_bridge()
            
            # Verificar Bot
            if bot.poll() is not None:
                print("⚠️ El Bot se detuvo. Revisando logs y reiniciando...")
                # Pequeña pausa para no saturar si hay un error constante
                time.sleep(10)
                bot = start_bot()
                
            time.sleep(15)
    except KeyboardInterrupt:
        print("\n🛑 Apagando sistema...")
        bridge.terminate()
        bot.terminate()

if __name__ == "__main__":
    run_system()
