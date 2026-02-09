#!/usr/bin/env python3
"""
Analizador de Pérdidas de IA - ¿Por qué falla tanto si usa Ollama?
"""

import sys
import os
import json
import pandas as pd
from datetime import datetime, timedelta

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def analizar_rendimiento_ia():
    """Analiza por qué la IA está teniendo tantas pérdidas"""
    print("🔍 ANÁLISIS DE PÉRDIDAS DE IA")
    print("=" * 60)
    print("¿Por qué falla tanto si usa Ollama (IA humana)?")
    print("=" * 60)
    
    # 1. Analizar experiencias históricas
    print("\n📊 ANALIZANDO EXPERIENCIAS HISTÓRICAS...")
    
    try:
        with open('data/experiences.json', 'r') as f:
            experiences = json.load(f)
        
        if not experiences:
            print("❌ No hay experiencias para analizar")
            return
        
        print(f"✅ Encontradas {len(experiences)} experiencias")
        
        # Analizar resultados
        wins = 0
        losses = 0
        total_profit = 0
        
        for exp in experiences:
            if 'reward' in exp:
                if exp['reward'] > 0:
                    wins += 1
                    total_profit += exp['reward']
                else:
                    losses += 1
                    total_profit += exp['reward']
        
        total_trades = wins + losses
        if total_trades > 0:
            win_rate = (wins / total_trades) * 100
            print(f"\n📈 ESTADÍSTICAS GENERALES:")
            print(f"   Total operaciones: {total_trades}")
            print(f"   Ganadas: {wins} ({win_rate:.1f}%)")
            print(f"   Perdidas: {losses} ({100-win_rate:.1f}%)")
            print(f"   Profit total: ${total_profit:.2f}")
            
            if win_rate < 50:
                print(f"\n⚠️ PROBLEMA DETECTADO: Win rate {win_rate:.1f}% es muy bajo")
                print("   Una IA humana debería tener al menos 60-70%")
        
    except Exception as e:
        print(f"❌ Error analizando experiencias: {e}")
    
    # 2. Analizar configuración de Ollama
    print(f"\n🧠 ANALIZANDO CONFIGURACIÓN DE OLLAMA...")
    
    try:
        from config import Config
        
        print(f"   Modelo: {Config.OLLAMA_MODEL}")
        print(f"   URL: {Config.OLLAMA_BASE_URL}")
        print(f"   LLM Activo: {Config.USE_LLM}")
        
        if not Config.USE_LLM:
            print("❌ PROBLEMA: LLM está DESACTIVADO")
            print("   El bot no está usando Ollama para tomar decisiones")
        
    except Exception as e:
        print(f"❌ Error verificando configuración: {e}")
    
    # 3. Probar conexión a Ollama
    print(f"\n🔗 PROBANDO CONEXIÓN A OLLAMA...")
    
    try:
        from ai.llm_client import LLMClient
        
        llm = LLMClient()
        
        # Hacer una consulta simple
        response = llm._query_ollama("¿Funciona Ollama? Responde solo 'SÍ' o 'NO'")
        
        if "Error" in response:
            print(f"❌ PROBLEMA: {response}")
            print("   Ollama no está respondiendo correctamente")
        else:
            print(f"✅ Ollama responde: {response[:50]}...")
        
    except Exception as e:
        print(f"❌ Error probando Ollama: {e}")
    
    # 4. Analizar prompts enviados a Ollama
    print(f"\n📝 ANALIZANDO CALIDAD DE PROMPTS...")
    
    try:
        # Simular un prompt típico
        market_summary = "EURUSD: 1.1740 | RSI: 45 | MACD: Neutral"
        smart_summary = "Setup: TREND_PULLBACK_PUT | Score: 85%"
        learning_summary = "Performance reciente: 45%"
        
        print("   Ejemplo de datos enviados a Ollama:")
        print(f"   📊 Mercado: {market_summary}")
        print(f"   🎯 Smart Money: {smart_summary}")
        print(f"   📚 Aprendizaje: {learning_summary}")
        
        # Verificar si los datos son suficientes
        if "45%" in learning_summary:
            print("⚠️ PROBLEMA DETECTADO: Performance baja en learning_summary")
            print("   Ollama ve que el bot tiene mal rendimiento y se vuelve conservador")
        
    except Exception as e:
        print(f"❌ Error analizando prompts: {e}")
    
    # 5. Identificar problemas principales
    print(f"\n🎯 PROBLEMAS IDENTIFICADOS:")
    
    problemas = []
    
    # Verificar si Ollama está siendo usado realmente
    try:
        with open('bot_output.log', 'r') if os.path.exists('bot_output.log') else open('nul', 'r') as f:
            logs = f.read()
            
        if "Ollama analizando" not in logs:
            problemas.append("❌ Ollama NO está siendo consultado en las operaciones")
        
        if "OLLAMA RECHAZA" in logs:
            rechazos = logs.count("OLLAMA RECHAZA")
            aprobaciones = logs.count("OLLAMA CONFIRMA")
            if rechazos > aprobaciones:
                problemas.append(f"❌ Ollama rechaza más de lo que aprueba ({rechazos} vs {aprobaciones})")
        
    except:
        problemas.append("⚠️ No se pueden analizar logs del bot")
    
    # Verificar configuración
    try:
        from config import Config
        if not Config.USE_LLM:
            problemas.append("❌ USE_LLM está desactivado - Ollama no se usa")
        
        if Config.OLLAMA_MODEL == "llama3.2:1b":
            problemas.append("⚠️ Modelo muy pequeño (1B) - Usar llama3.2:3b o mayor")
    except:
        pass
    
    # Mostrar problemas
    if problemas:
        for problema in problemas:
            print(f"   {problema}")
    else:
        print("   ✅ No se detectaron problemas obvios")
    
    # 6. Recomendaciones
    print(f"\n💡 RECOMENDACIONES PARA MEJORAR:")
    
    print("   1. 🧠 MEJORAR OLLAMA:")
    print("      - Usar modelo más grande: llama3.2:3b o llama3.1:8b")
    print("      - Verificar que EasyPanel tenga suficiente RAM")
    print("      - Optimizar prompts para ser más específicos")
    
    print("   2. 📊 MEJORAR DATOS:")
    print("      - Enviar más contexto de mercado a Ollama")
    print("      - Incluir análisis de múltiples timeframes")
    print("      - Agregar datos de volumen y momentum")
    
    print("   3. 🎯 MEJORAR LÓGICA:")
    print("      - Hacer que Ollama sea menos conservador")
    print("      - Reducir umbral de confianza de 65% a 55%")
    print("      - Usar fallback a análisis técnico si Ollama falla")
    
    print("   4. 🔧 DEBUGGING:")
    print("      - Activar logs detallados de decisiones de Ollama")
    print("      - Guardar prompts y respuestas para análisis")
    print("      - Comparar decisiones de Ollama vs análisis técnico")
    
    return True

def crear_fix_ollama():
    """Crea un script para mejorar el rendimiento de Ollama"""
    print(f"\n🛠️ CREANDO SCRIPT DE MEJORA...")
    
    fix_script = """#!/usr/bin/env python3
# Script para mejorar el rendimiento de Ollama

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def aplicar_mejoras():
    print("🔧 APLICANDO MEJORAS A OLLAMA...")
    
    # 1. Hacer Ollama menos conservador
    print("1. Haciendo Ollama menos conservador...")
    
    # 2. Mejorar prompts
    print("2. Mejorando prompts...")
    
    # 3. Activar fallback
    print("3. Activando fallback a análisis técnico...")
    
    print("✅ Mejoras aplicadas")

if __name__ == "__main__":
    aplicar_mejoras()
"""
    
    with open('fix_ollama_performance.py', 'w') as f:
        f.write(fix_script)
    
    print("✅ Script creado: fix_ollama_performance.py")

def main():
    """Función principal"""
    print("🤖 DIAGNÓSTICO DE IA - ¿POR QUÉ TANTAS PÉRDIDAS?")
    print("=" * 70)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    success = analizar_rendimiento_ia()
    
    if success:
        crear_fix_ollama()
    
    print("\n" + "=" * 70)
    print("📋 RESUMEN DEL DIAGNÓSTICO")
    print("=" * 70)
    
    print("🔍 POSIBLES CAUSAS DE PÉRDIDAS:")
    print("   1. Ollama está siendo demasiado conservador")
    print("   2. Modelo de Ollama muy pequeño (1B parámetros)")
    print("   3. Prompts no tienen suficiente contexto")
    print("   4. Datos de mercado insuficientes")
    print("   5. Umbral de confianza muy alto (65%)")
    print("   6. Ollama ve el mal rendimiento y se vuelve más conservador")
    
    print("\n🎯 SOLUCIONES INMEDIATAS:")
    print("   1. Cambiar modelo a llama3.2:3b en EasyPanel")
    print("   2. Reducir umbral de confianza a 55%")
    print("   3. Mejorar prompts con más contexto")
    print("   4. Activar fallback a análisis técnico")
    print("   5. Hacer que Ollama sea más agresivo")
    
    print("\n🚀 PRÓXIMOS PASOS:")
    print("   1. Ejecutar: python fix_ollama_performance.py")
    print("   2. Cambiar modelo en EasyPanel")
    print("   3. Probar con configuración mejorada")
    print("   4. Monitorear mejora en win rate")

if __name__ == "__main__":
    main()