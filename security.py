from cryptography.fernet import Fernet
import os

# En producción, esta llave debería estar en una variable de entorno segura
MASTER_KEY = os.getenv("SAAS_MASTER_KEY", Fernet.generate_key().decode())

cipher_suite = Fernet(MASTER_KEY.encode())

def encrypt_password(password: str) -> str:
    if not password: return ""
    return cipher_suite.encrypt(password.encode()).decode()

def decrypt_password(encrypted_password: str) -> str:
    if not encrypted_password: return ""
    return cipher_suite.decrypt(encrypted_password.encode()).decode()
