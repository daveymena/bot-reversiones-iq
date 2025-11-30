from config import Config
from iqoptionapi.stable_api import IQ_Option
import time

def check_connection():
    print("--- Verificando Conexión a IQ Option ---")
    print(f"Email: {Config.IQ_EMAIL}")
    # No imprimir contraseña por seguridad
    
    api = IQ_Option(Config.IQ_EMAIL, Config.IQ_PASSWORD)
    check, reason = api.connect()
    
    if check:
        print("✅ Conexión EXITOSA")
        balance = api.get_balance()
        print(f"Balance de cuenta: {balance}")
        print(f"Tipo de balance: {api.get_balance_mode()}")
    else:
        print("❌ Error de conexión")
        print(f"Razón: {reason}")
        print("Intenta verificar tus credenciales o si tienes 2FA activado.")

if __name__ == "__main__":
    check_connection()
