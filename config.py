"""
Configuración centralizada del bot
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Clase de configuración centralizada"""
    
    # ============= BROKER =============
    BROKER_NAME = os.getenv("BROKER_NAME", "exnova")
    ACCOUNT_TYPE = os.getenv("ACCOUNT_TYPE", "PRACTICE")
    
    # Credenciales Exnova
    EXNOVA_EMAIL = os.getenv("EXNOVA_EMAIL", "")
    EXNOVA_PASSWORD = os.getenv("EXNOVA_PASSWORD", "")
    
    # Credenciales IQ Option
    IQ_OPTION_EMAIL = os.getenv("IQ_OPTION_EMAIL", "")
    IQ_OPTION_PASSWORD = os.getenv("IQ_OPTION_PASSWORD", "")
    
    # ============= TRADING =============
    DEFAULT_ASSET = os.getenv("DEFAULT_ASSET", "EURUSD-OTC")
    CAPITAL_PER_TRADE = float(os.getenv("CAPITAL_PER_TRADE", "1"))
    EXPIRATION_TIME = int(os.getenv("EXPIRATION_TIME", "60"))
    TIMEFRAME = 60  # Timeframe en segundos (1 minuto por defecto)
    
    # Expiración automática vs manual
    AUTO_EXPIRATION = True  # Por defecto, IA decide
    MANUAL_EXPIRATION = 1   # Valor manual si AUTO_EXPIRATION = False
    
    # ============= RISK MANAGEMENT =============
    MAX_MARTINGALE = int(os.getenv("MAX_MARTINGALE", "0"))
    STOP_LOSS_PERCENT = float(os.getenv("STOP_LOSS_PERCENT", "20"))
    TAKE_PROFIT_PERCENT = float(os.getenv("TAKE_PROFIT_PERCENT", "10"))
    
    # ============= HORARIO DE OPERACIÓN =============
    TRADING_START_HOUR = int(os.getenv("TRADING_START_HOUR", "7"))  # 7:00 AM
    TRADING_END_HOUR = int(os.getenv("TRADING_END_HOUR", "9"))      # 9:30 AM
    TRADING_END_MINUTE = int(os.getenv("TRADING_END_MINUTE", "30"))
    MIN_VOLATILITY_TO_START = float(os.getenv("MIN_VOLATILITY_TO_START", "0.05"))  # ATR mínimo para iniciar
    
    # ============= AI/LLM =============
    USE_LLM = os.getenv("USE_LLM", "True").lower() == "true"
    USE_GROQ = os.getenv("USE_GROQ", "True").lower() == "true"
    
    # Soporte para múltiples llaves de Groq con rotación
    GROQ_API_KEYS = [
        os.getenv("VITE_GROQ_API_KEY", os.getenv("GROQ_API_KEY", "")),
        os.getenv("VITE_GROQ_API_KEY_2", ""),
        os.getenv("VITE_GROQ_API_KEY_3", ""),
        os.getenv("VITE_GROQ_API_KEY_4", "")
    ]
    GROQ_API_KEYS = [k for k in GROQ_API_KEYS if k] # Filtrar vacías
    GROQ_API_KEY = GROQ_API_KEYS[0] if GROQ_API_KEYS else ""
    
    OLLAMA_MODEL = os.getenv("VITE_OLLAMA_MODEL", os.getenv("OLLAMA_MODEL", "gemma2:2b"))
    OLLAMA_MODEL_FAST = os.getenv("OLLAMA_MODEL_FAST", "gemma2:2b")
    OLLAMA_BASE_URL = os.getenv("VITE_OLLAMA_BASE_URL", os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"))
    OLLAMA_URL = f"{OLLAMA_BASE_URL}/api/generate" if "ollama" in OLLAMA_BASE_URL else f"{OLLAMA_BASE_URL}/api/generate"
    
    # ============= BACKEND (para GUI remota) =============
    BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
    
    # ============= PATHS =============
    DATA_DIR = "data"
    MODELS_DIR = "models"
    EXPERIENCES_FILE = os.path.join(DATA_DIR, "experiences.json")
    MODEL_PATH = os.path.join(MODELS_DIR, "rl_agent")

# Mantener compatibilidad con imports directos
BROKER_NAME = Config.BROKER_NAME
ACCOUNT_TYPE = Config.ACCOUNT_TYPE
EXNOVA_EMAIL = Config.EXNOVA_EMAIL
EXNOVA_PASSWORD = Config.EXNOVA_PASSWORD
IQ_OPTION_EMAIL = Config.IQ_OPTION_EMAIL
IQ_OPTION_PASSWORD = Config.IQ_OPTION_PASSWORD
DEFAULT_ASSET = Config.DEFAULT_ASSET
CAPITAL_PER_TRADE = Config.CAPITAL_PER_TRADE
EXPIRATION_TIME = Config.EXPIRATION_TIME
TIMEFRAME = Config.TIMEFRAME
MAX_MARTINGALE = Config.MAX_MARTINGALE
STOP_LOSS_PERCENT = Config.STOP_LOSS_PERCENT
TAKE_PROFIT_PERCENT = Config.TAKE_PROFIT_PERCENT
TRADING_START_HOUR = Config.TRADING_START_HOUR
TRADING_END_HOUR = Config.TRADING_END_HOUR
TRADING_END_MINUTE = Config.TRADING_END_MINUTE
MIN_VOLATILITY_TO_START = Config.MIN_VOLATILITY_TO_START
USE_LLM = Config.USE_LLM
USE_GROQ = Config.USE_GROQ
GROQ_API_KEY = Config.GROQ_API_KEY
OLLAMA_MODEL = Config.OLLAMA_MODEL
OLLAMA_MODEL_FAST = Config.OLLAMA_MODEL_FAST
OLLAMA_BASE_URL = Config.OLLAMA_BASE_URL
OLLAMA_URL = Config.OLLAMA_URL
BACKEND_URL = Config.BACKEND_URL
DATA_DIR = Config.DATA_DIR
MODELS_DIR = Config.MODELS_DIR
EXPERIENCES_FILE = Config.EXPERIENCES_FILE
MODEL_PATH = Config.MODEL_PATH
