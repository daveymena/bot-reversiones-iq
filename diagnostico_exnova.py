"""
Script de diagnóstico para identificar el problema de Exnova
"""
import sys
import os

print("=" * 60)
print("DIAGNÓSTICO DE EXNOVA")
print("=" * 60)

# 1. Verificar que exnovaapi existe
print("\n[1] Verificando módulo exnovaapi...")
try:
    import exnovaapi
    print(f"✅ Módulo encontrado en: {exnovaapi.__file__}")
except ImportError as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

# 2. Verificar versión de websocket
print("\n[2] Verificando websocket-client...")
try:
    import websocket
    print(f"✅ websocket-client instalado")
    print(f"   Versión: {websocket.__version__ if hasattr(websocket, '__version__') else 'Desconocida'}")
except ImportError:
    print("❌ websocket-client NO instalado")
    print("   Solución: pip install websocket-client")

# 3. Verificar otras dependencias
print("\n[3] Verificando dependencias...")
deps = {
    'requests': 'HTTP client',
    'json': 'JSON parser',
    'threading': 'Threading support',
    'ssl': 'SSL support'
}

for dep, desc in deps.items():
    try:
        __import__(dep)
        print(f"✅ {dep}: {desc}")
    except ImportError:
        print(f"❌ {dep}: NO encontrado")

# 4. Test de conexión básica
print("\n[4] Test de conexión básica...")
try:
    from exnovaapi.stable_api import Exnova
    from config import Config
    
    print("Inicializando API...")
    api = Exnova(Config.EX_EMAIL, Config.EX_PASSWORD)
    print("✅ API inicializada")
    
    print("\nIntentando conectar (esto puede tomar tiempo)...")
    print("NOTA: Si se queda aquí, el problema es el websocket")
    
    import signal
    import time
    
    # Timeout de 10 segundos
    def timeout_handler(signum, frame):
        raise TimeoutError("Conexión tomó demasiado tiempo")
    
    # En Windows no funciona signal.alarm, usar threading
    from threading import Thread, Event
    
    result = {'status': None, 'message': None, 'error': None}
    stop_event = Event()
    
    def connect_thread():
        try:
            status, message = api.connect()
            result['status'] = status
            result['message'] = message
        except Exception as e:
            result['error'] = str(e)
        finally:
            stop_event.set()
    
    thread = Thread(target=connect_thread)
    thread.daemon = True
    thread.start()
    
    # Esperar máximo 15 segundos
    stop_event.wait(timeout=15)
    
    if not stop_event.is_set():
        print("\n⚠️ TIMEOUT: La conexión está bloqueada")
        print("\nPROBLEMA IDENTIFICADO:")
        print("  - El websocket se está bloqueando durante la conexión")
        print("  - Esto es un problema conocido con algunas versiones de websocket-client")
        print("\nSOLUCIONES POSIBLES:")
        print("  1. Actualizar websocket-client:")
        print("     pip install --upgrade websocket-client")
        print("  2. Usar una versión específica:")
        print("     pip install websocket-client==1.6.4")
        print("  3. Verificar firewall/antivirus")
    else:
        if result['error']:
            print(f"\n❌ Error: {result['error']}")
        elif result['status']:
            print(f"\n✅ CONEXIÓN EXITOSA: {result['message']}")
        else:
            print(f"\n❌ CONEXIÓN FALLIDA: {result['message']}")
    
except Exception as e:
    print(f"\n❌ Error durante diagnóstico: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("FIN DEL DIAGNÓSTICO")
print("=" * 60)
