"""
Script de prueba para las señales de Edinson
"""
from core.signal_parser import SignalParser
import re

# Los ejemplos reales que me diste
PROMPT_EDINSON_1 = """
🧠 Señales GRATIS de Edinson 🤓
━━━━━━━━━━━━━━━━
📊 Probabilidad de Ganar: MEDIA

👉 Abre tu cuenta aquí para operar EN VIVO conmigo todos los días:
https://creaunacuenta.com/
━━━━━━━━━━━━━━━━

🌎 Zona horaria de la Señal: UTC-05:00 Bogotá

📌 Paso 1: En Exnova busca Opciones Binarias y elige el activo llamado:
USD/CHF (OTC).
⏳ Paso 2: Configura el Tiempo de vencimiento en 3 minutos.
🖱️ Paso 3: Da clic en el botón:
🟩▲CALL-SUBE▲🟩
(Asegúrate de dar clic a la ⏱ Hora exacta que es: 21:11)

⏱️ Aún tienes 1 minuto para tomar esta Señal
"""

PROMPT_EDINSON_2 = """
🧠 Señales GRATIS de Edinson 🤓
━━━━━━━━━━━━━━━━
📊 Probabilidad de Ganar: ALTA

👉 Abre tu cuenta aquí para operar EN VIVO conmigo todos los días:
https://creaunacuenta.com/
━━━━━━━━━━━━━━━━

🌎 Zona horaria de la Señal: UTC-05:00 Bogotá

📌 Paso 1: En Exnova busca Opciones Binarias y elige el activo llamado:
GBP/USD (OTC).
⏳ Paso 2: Configura el Tiempo de vencimiento en 2 minutos.
🖱️ Paso 3: Da clic en el botón:
🟥▼PUT-BAJA▼🟥
(Asegúrate de dar clic a la ⏱ Hora exacta que es: 21:23)

⏱️ Aún tienes 2 minutos para tomar esta Señal
"""

def test_edinson():
    print("ANALIZANDO SEÑALES DE EDINSON...")
    parser = SignalParser()
    
    # Probamos con el parser actual (probablemente falle o capture parcial)
    
    for i, msg in enumerate([PROMPT_EDINSON_1, PROMPT_EDINSON_2], 1):
        print(f"\n--- MENSAJE {i} ---")
        signal = parser.parse(msg)
        
        if signal:
            print("✅ SEÑAL DETECTADA:")
            print(f"   Activo: {signal['asset']}")
            print(f"   Dirección: {signal['direction']}")
            print(f"   Expiración: {signal['expiration']} min")
        else:
            print("❌ NO SE DETECTÓ (Necesitamos mejorar el parser)")

if __name__ == "__main__":
    test_edinson()
