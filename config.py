import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

class Config:
    # --- Credenciales Brokers ---
    # Solo Exnova (IQ Option eliminado por bloqueo)
    EX_EMAIL = os.getenv("EXNOVA_EMAIL")
    EX_PASSWORD = os.getenv("EXNOVA_PASSWORD")
    
    # Broker Activo: Siempre 'exnova'
    BROKER_NAME = "exnova"
    
    # Tipo de Cuenta: 'PRACTICE' o 'REAL'
    ACCOUNT_TYPE = os.getenv("ACCOUNT_TYPE", "PRACTICE")

    # --- Configuración de Trading ---
    CAPITAL_PER_TRADE = 1.0  # USD o EUR
    STOP_LOSS_PCT = 0.05     # 5% de pérdida máxima diaria
    TAKE_PROFIT_PCT = 0.10   # 10% de ganancia meta diaria
    TIMEFRAME = 60           # 1 minuto (en segundos)
    
    # --- Configuración de Expiración ---
    AUTO_EXPIRATION = True   # True: IA decide (1-5 min), False: usar MANUAL_EXPIRATION
    MANUAL_EXPIRATION = 1    # Minutos (solo se usa si AUTO_EXPIRATION = False)
    
    # --- Configuración de RL ---
    TIMESTEPS = 10000
    MODEL_PATH = "models/rl_agent"
    DATA_PATH = "data/history.csv"

    # --- Configuración de IA Generativa (LLM) ---
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    OLLAMA_MODEL = "llama3.2:3b" 
    OLLAMA_MODEL_FAST = "gemma2:2b"
    # URL base proporcionada por usuario + endpoint
    OLLAMA_URL = "https://davey-ollama2.mapf5v.easypanel.host/api/generate"
    USE_LLM = True # Activar/Desactivar consejos de IA

    # --- Configuración de GUI ---
    THEME = "Dark" # Dark / Light
    UPDATE_INTERVAL_MS = 1000 # Actualización de gráficos cada 1s

    @staticmethod
    def validate():
        if not Config.EX_EMAIL or not Config.EX_PASSWORD:
            print("ADVERTENCIA: Credenciales de Exnova faltantes en .env")
        if Config.USE_LLM and not Config.GROQ_API_KEY:
            print("NOTA: GROQ_API_KEY no encontrada. Se usará solo Ollama si está disponible.")
