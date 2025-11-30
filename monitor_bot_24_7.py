"""
Monitor del Bot 24/7
Verifica que el bot esté funcionando continuamente
"""
import time
import os
from datetime import datetime

def monitor_bot():
    """Monitorea el archivo de logs para verificar que el bot está activo"""
    print("="*60)
    print("🔍 MONITOR BOT 24/7")
    print("="*60)
    print("\nMonitoreando actividad del bot...")
    print("Presiona Ctrl+C para detener el monitor\n")
    
    log_file = "bot_errors.log"
    last_size = 0
    last_activity = time.time()
    no_activity_threshold = 300  # 5 minutos sin actividad = alerta
    
    heartbeat_count = 0
    retrain_count = 0
    error_count = 0
    
    try:
        while True:
            # Verificar si el archivo existe
            if not os.path.exists(log_file):
                print(f"⚠️ Archivo de log no encontrado: {log_file}")
                time.sleep(10)
                continue
            
            # Verificar tamaño del archivo
            current_size = os.path.getsize(log_file)
            
            if current_size > last_size:
                # Hay nueva actividad
                last_activity = time.time()
                last_size = current_size
                
                # Leer últimas líneas
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    recent_lines = lines[-10:] if len(lines) > 10 else lines
                    
                    for line in recent_lines:
                        # Contar eventos importantes
                        if "Bot activo" in line or "💓" in line:
                            heartbeat_count += 1
                            print(f"💓 Heartbeat detectado #{heartbeat_count} - {datetime.now().strftime('%H:%M:%S')}")
                        
                        if "Re-entrenamiento completado" in line:
                            retrain_count += 1
                            print(f"🎓 Re-entrenamiento #{retrain_count} completado - {datetime.now().strftime('%H:%M:%S')}")
                        
                        if "ERROR" in line and "FATAL" in line:
                            error_count += 1
                            print(f"❌ Error fatal detectado #{error_count} - {datetime.now().strftime('%H:%M:%S')}")
                            print(f"   {line.strip()}")
            
            # Verificar tiempo sin actividad
            time_since_activity = time.time() - last_activity
            
            if time_since_activity > no_activity_threshold:
                print(f"\n⚠️ ALERTA: Sin actividad por {int(time_since_activity)}s")
                print(f"   Última actividad: {datetime.fromtimestamp(last_activity).strftime('%H:%M:%S')}")
                print(f"   ¿El bot está detenido?\n")
            
            # Mostrar resumen cada 60 segundos
            if int(time.time()) % 60 == 0:
                print(f"\n📊 Resumen - {datetime.now().strftime('%H:%M:%S')}")
                print(f"   Heartbeats: {heartbeat_count}")
                print(f"   Re-entrenamientos: {retrain_count}")
                print(f"   Errores fatales: {error_count}")
                print(f"   Última actividad: {int(time_since_activity)}s atrás")
                
                if time_since_activity < 120:
                    print(f"   Estado: ✅ Bot activo")
                else:
                    print(f"   Estado: ⚠️ Posible inactividad")
                print()
            
            time.sleep(5)
    
    except KeyboardInterrupt:
        print("\n\n" + "="*60)
        print("📊 RESUMEN FINAL DEL MONITOREO")
        print("="*60)
        print(f"Heartbeats detectados: {heartbeat_count}")
        print(f"Re-entrenamientos: {retrain_count}")
        print(f"Errores fatales: {error_count}")
        print("="*60)
        print("\n✅ Monitor detenido")

if __name__ == "__main__":
    monitor_bot()
