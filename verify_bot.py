"""
Verificación Completa del Bot de Trading
Verifica dependencias, configuración, brokers y funcionalidad
"""
import sys
import os

print("=" * 70)
print("🔍 VERIFICACIÓN COMPLETA DEL BOT DE TRADING")
print("=" * 70)

# 1. VERIFICAR DEPENDENCIAS
print("\n📦 1. VERIFICANDO DEPENDENCIAS...")
dependencies = {
    'numpy': 'numpy',
    'pandas': 'pandas',
    'ta': 'ta',
    'requests': 'requests',
    'PySide6': 'PySide6',
    'pyqtgraph': 'pyqtgraph',
    'groq': 'groq',
    'ollama': 'ollama',
    'iqoptionapi': 'iqoptionapi',
    'python-dotenv': 'dotenv'
}

missing_deps = []
for name, import_name in dependencies.items():
    try:
        __import__(import_name)
        print(f"   ✅ {name}")
    except ImportError:
        print(f"   ❌ {name} - FALTA")
        missing_deps.append(name)

if missing_deps:
    print(f"\n⚠️ Dependencias faltantes: {', '.join(missing_deps)}")
    print("   Instala con: pip install " + " ".join(missing_deps))
else:
    print("\n✅ Todas las dependencias están instaladas")

# 2. VERIFICAR ARCHIVO .ENV
print("\n📄 2. VERIFICANDO ARCHIVO .ENV...")
env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    print(f"   ✅ Archivo .env encontrado: {env_path}")
    
    # Leer y verificar variables
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = {
        'EXNOVA_EMAIL': os.getenv('EXNOVA_EMAIL'),
        'EXNOVA_PASSWORD': os.getenv('EXNOVA_PASSWORD'),
        'IQ_OPTION_EMAIL': os.getenv('IQ_OPTION_EMAIL'),
        'IQ_OPTION_PASSWORD': os.getenv('IQ_OPTION_PASSWORD'),
        'GROQ_API_KEY': os.getenv('GROQ_API_KEY'),
        'BROKER_NAME': os.getenv('BROKER_NAME', 'exnova'),
        'ACCOUNT_TYPE': os.getenv('ACCOUNT_TYPE', 'PRACTICE')
    }
    
    print("\n   Variables de entorno:")
    for var, value in required_vars.items():
        if value:
            masked = value[:4] + "***" if len(value) > 4 else "***"
            print(f"   ✅ {var}: {masked}")
        else:
            print(f"   ⚠️ {var}: NO CONFIGURADA")
else:
    print(f"   ❌ Archivo .env NO encontrado en: {env_path}")

# 3. VERIFICAR CONFIGURACIÓN
print("\n⚙️ 3. VERIFICANDO CONFIG.PY...")
try:
    from config import Config
    print(f"   ✅ BROKER_NAME: {Config.BROKER_NAME}")
    print(f"   ✅ ACCOUNT_TYPE: {Config.ACCOUNT_TYPE}")
    print(f"   ✅ OLLAMA_URL: {Config.OLLAMA_URL}")
    print(f"   ✅ OLLAMA_MODEL: {Config.OLLAMA_MODEL}")
    print(f"   ✅ OLLAMA_MODEL_FAST: {getattr(Config, 'OLLAMA_MODEL_FAST', 'N/A')}")
    print(f"   ✅ GROQ_API_KEY: {'Configurada' if Config.GROQ_API_KEY else 'NO configurada'}")
except Exception as e:
    print(f"   ❌ Error cargando config: {e}")

# 4. VERIFICAR BROKERS
print("\n🔌 4. VERIFICANDO BROKERS...")
try:
    from data.market_data import MarketDataHandler
    
    # Test Exnova
    print("\n   📊 Exnova:")
    exnova_handler = MarketDataHandler(broker_name="exnova", account_type="PRACTICE")
    exnova_module = exnova_handler._load_broker_module()
    if exnova_module:
        print(f"      ✅ Módulo cargado: {exnova_module}")
    else:
        print("      ❌ No se pudo cargar el módulo")
    
    # Test IQ Option
    print("\n   📊 IQ Option:")
    iq_handler = MarketDataHandler(broker_name="iq", account_type="PRACTICE")
    iq_module = iq_handler._load_broker_module()
    if iq_module:
        print(f"      ✅ Módulo cargado: {iq_module}")
    else:
        print("      ❌ No se pudo cargar el módulo")
        
except Exception as e:
    print(f"   ❌ Error verificando brokers: {e}")
    import traceback
    traceback.print_exc()

# 5. VERIFICAR GROQ
print("\n🤖 5. VERIFICANDO GROQ...")
try:
    from ai.llm_client import LLMClient
    client = LLMClient()
    if client.use_groq and client.groq_client:
        print("   ✅ Cliente Groq inicializado correctamente")
    else:
        print("   ⚠️ Groq no disponible, usando Ollama")
except Exception as e:
    print(f"   ❌ Error verificando Groq: {e}")

# 6. VERIFICAR OLLAMA
print("\n🦙 6. VERIFICANDO OLLAMA...")
try:
    import requests
    from config import Config
    
    # Test de conexión
    payload = {
        "model": Config.OLLAMA_MODEL_FAST if hasattr(Config, 'OLLAMA_MODEL_FAST') else Config.OLLAMA_MODEL,
        "prompt": "Test",
        "stream": False
    }
    
    print(f"   Probando conexión a: {Config.OLLAMA_URL}")
    response = requests.post(Config.OLLAMA_URL, json=payload, timeout=10)
    
    if response.status_code == 200:
        print("   ✅ Ollama responde correctamente")
    else:
        print(f"   ⚠️ Ollama respondió con código: {response.status_code}")
        
except requests.exceptions.Timeout:
    print("   ⚠️ Timeout conectando a Ollama (puede estar ocupado)")
except Exception as e:
    print(f"   ❌ Error verificando Ollama: {e}")

# 7. VERIFICAR COMPONENTES CORE
print("\n🧠 7. VERIFICANDO COMPONENTES CORE...")
components = [
    ('KnowledgeBase', 'core.knowledge_base', 'KnowledgeBase'),
    ('TradeIntelligence', 'core.trade_intelligence', 'TradeIntelligence'),
    ('ObservationalLearner', 'core.observational_learner', 'ObservationalLearner'),
    ('RLAgent', 'core.agent', 'RLAgent'),
    ('LiveTrader', 'core.trader', 'LiveTrader'),
    ('AdvancedMarketAnalysis', 'strategies.advanced_analysis', 'AdvancedMarketAnalysis')
]

for name, module, class_name in components:
    try:
        mod = __import__(module, fromlist=[class_name])
        cls = getattr(mod, class_name)
        print(f"   ✅ {name}")
    except Exception as e:
        print(f"   ❌ {name}: {e}")

# 8. VERIFICAR ARCHIVOS DE DATOS
print("\n📁 8. VERIFICANDO ESTRUCTURA DE DATOS...")
data_dirs = ['data', 'models', 'logs']
for dir_name in data_dirs:
    dir_path = os.path.join(os.path.dirname(__file__), dir_name)
    if os.path.exists(dir_path):
        print(f"   ✅ {dir_name}/")
    else:
        print(f"   ⚠️ {dir_name}/ - NO EXISTE (se creará automáticamente)")
        try:
            os.makedirs(dir_path, exist_ok=True)
            print(f"      ✅ Creado: {dir_path}")
        except Exception as e:
            print(f"      ❌ Error creando: {e}")

# RESUMEN
print("\n" + "=" * 70)
print("📊 RESUMEN DE VERIFICACIÓN")
print("=" * 70)

if not missing_deps:
    print("✅ Dependencias: OK")
else:
    print(f"⚠️ Dependencias: FALTAN {len(missing_deps)}")

if os.path.exists(env_path):
    print("✅ Configuración .env: OK")
else:
    print("❌ Configuración .env: FALTA")

print("\n💡 PRÓXIMOS PASOS:")
if missing_deps:
    print("   1. Instalar dependencias faltantes")
if not os.path.exists(env_path):
    print("   2. Crear archivo .env con credenciales")
print("   3. Ejecutar: python run_modern_gui.py")

print("\n" + "=" * 70)
