from intelligent_learning import IntelligentLearningSystem
import time

def run_headless():
    print("🤖 MODO HEADLESS ACTIVADO: BUCLE INFINITO DE APRENDIZAJE 24/7")
    print("💡 El bot se reiniciará automáticamente si la sesión termina.")
    
    while True:
        try:
            system = IntelligentLearningSystem()
            # Duración: 24h, Objetivo: 1000 operaciones
            system.continuous_learning_session(duration_minutes=1440, operations_target=1000)
        except Exception as e:
            print(f"⚠️ Error crítico en ciclo: {e}")
            print("🔄 Reiniciando en 10 segundos...")
            time.sleep(10)

if __name__ == "__main__":
    try:
        run_headless()
    except KeyboardInterrupt:
        print("\n🛑 Detenido por usuario.")
