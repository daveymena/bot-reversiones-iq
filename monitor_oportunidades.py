"""
🔔 Monitor de Oportunidades del Bot

Este script monitorea los logs del bot y te avisa cuando detecta:
- Score >= 70 (oportunidad potencial)
- Score >= 85 (oportunidad excelente)
- Operación aprobada
- Operación ejecutada
"""

import re
import time
from datetime import datetime

def parse_score_from_log(log_line):
    """Extrae el score de una línea de log"""
    match = re.search(r'Score inicial: (\d+)/100', log_line)
    if match:
        return int(match.group(1))
    return None

def parse_asset_from_log(log_line):
    """Extrae el activo de una línea de log"""
    match = re.search(r'Analizando ([A-Z]+-OTC)', log_line)
    if match:
        return match.group(1)
    return None

def parse_action_from_log(log_line):
    """Extrae la acción propuesta de una línea de log"""
    match = re.search(r'Acción propuesta: (CALL|PUT|NINGUNA)', log_line)
    if match:
        return match.group(1)
    return None

def monitor_opportunities():
    """Monitorea oportunidades en tiempo real"""
    print("=" * 60)
    print("🔔 MONITOR DE OPORTUNIDADES ACTIVADO")
    print("=" * 60)
    print("\n📊 Monitoreando logs del bot...")
    print("⏳ Esperando oportunidades con score >= 70...\n")
    
    current_asset = None
    current_score = None
    current_action = None
    analysis_buffer = []
    
    try:
        # Leer el archivo de log en tiempo real
        log_file = "bot_output.log"
        
        # Si no existe, crear uno vacío
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                f.seek(0, 2)  # Ir al final del archivo
        except FileNotFoundError:
            print(f"⚠️ Archivo {log_file} no encontrado")
            print("💡 El bot debe estar ejecutándose para monitorear")
            return
        
        print("✅ Conectado a los logs del bot\n")
        
        last_notification_time = 0
        
        while True:
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    
                    for line in lines[-100:]:  # Últimas 100 líneas
                        # Detectar inicio de análisis
                        if "Analizando" in line:
                            current_asset = parse_asset_from_log(line)
                            analysis_buffer = [line]
                        
                        # Acumular líneas del análisis
                        elif current_asset and any(x in line for x in ["RSI:", "MACD:", "BB:", "Tendencia:", "Volatilidad:", "Score inicial:", "Acción propuesta:"]):
                            analysis_buffer.append(line)
                        
                        # Detectar score
                        if "Score inicial:" in line:
                            current_score = parse_score_from_log(line)
                        
                        # Detectar acción
                        if "Acción propuesta:" in line:
                            current_action = parse_action_from_log(line)
                            
                            # Si tenemos todo, evaluar
                            if current_asset and current_score and current_action:
                                now = time.time()
                                
                                # Notificar solo si han pasado 30 segundos desde última notificación
                                if now - last_notification_time >= 30:
                                    # 🔥 OPORTUNIDAD EXCELENTE (Score >= 85)
                                    if current_score >= 85 and current_action != "NINGUNA":
                                        print("\n" + "🔥" * 30)
                                        print(f"🔥 ¡OPORTUNIDAD EXCELENTE! Score: {current_score}/100")
                                        print("🔥" * 30)
                                        print(f"📊 Activo: {current_asset}")
                                        print(f"🎯 Acción: {current_action}")
                                        print(f"⭐ Confianza: {current_score}%")
                                        print("\n📋 Análisis completo:")
                                        for buf_line in analysis_buffer:
                                            print(f"   {buf_line.strip()}")
                                        print("🔥" * 30 + "\n")
                                        last_notification_time = now
                                    
                                    # ⚡ OPORTUNIDAD BUENA (Score >= 70)
                                    elif current_score >= 70 and current_action != "NINGUNA":
                                        print("\n" + "⚡" * 30)
                                        print(f"⚡ ¡OPORTUNIDAD DETECTADA! Score: {current_score}/100")
                                        print("⚡" * 30)
                                        print(f"📊 Activo: {current_asset}")
                                        print(f"🎯 Acción: {current_action}")
                                        print(f"✅ Confianza: {current_score}%")
                                        print("\n📋 Análisis completo:")
                                        for buf_line in analysis_buffer:
                                            print(f"   {buf_line.strip()}")
                                        print("⚡" * 30 + "\n")
                                        last_notification_time = now
                                
                                # Reset
                                current_asset = None
                                current_score = None
                                current_action = None
                                analysis_buffer = []
                        
                        # Detectar operación aprobada
                        if "APROBADO - Pasó todas las validaciones" in line:
                            print("\n" + "✅" * 30)
                            print("✅ ¡OPERACIÓN APROBADA!")
                            print("✅" * 30)
                            print(f"   {line.strip()}")
                            print("✅" * 30 + "\n")
                            last_notification_time = time.time()
                        
                        # Detectar operación ejecutada
                        if "Ejecutando CALL" in line or "Ejecutando PUT" in line:
                            print("\n" + "🚀" * 30)
                            print("🚀 ¡OPERACIÓN EJECUTADA!")
                            print("🚀" * 30)
                            print(f"   {line.strip()}")
                            print("🚀" * 30 + "\n")
                            last_notification_time = time.time()
                
                # Esperar 5 segundos antes de revisar de nuevo
                time.sleep(5)
                
            except Exception as e:
                print(f"⚠️ Error leyendo logs: {e}")
                time.sleep(5)
    
    except KeyboardInterrupt:
        print("\n\n" + "=" * 60)
        print("🛑 Monitor detenido por el usuario")
        print("=" * 60)

if __name__ == "__main__":
    monitor_opportunities()
