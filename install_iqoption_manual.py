"""
Script para instalar y probar IQ Option con la versión correcta
Descarga e instala manualmente desde GitHub
"""
import subprocess
import sys
import os

print("=" * 70)
print("🔧 INSTALACIÓN MANUAL DE IQOPTIONAPI (Fork Lu-Yi-Hsun)")
print("=" * 70)

# Paso 1: Descargar el repositorio como ZIP
print("\n1️⃣ Descargando repositorio...")
print("   URL: https://github.com/Lu-Yi-Hsun/iqoptionapi/archive/refs/heads/master.zip")

try:
    import requests
    import zipfile
    import io
    
    url = "https://github.com/Lu-Yi-Hsun/iqoptionapi/archive/refs/heads/master.zip"
    print("   ⏳ Descargando...")
    
    response = requests.get(url, timeout=30)
    if response.status_code == 200:
        print("   ✅ Descarga exitosa")
        
        # Paso 2: Extraer ZIP
        print("\n2️⃣ Extrayendo archivos...")
        z = zipfile.ZipFile(io.BytesIO(response.content))
        z.extractall("temp_iqoption")
        print("   ✅ Archivos extraídos en temp_iqoption/")
        
        # Paso 3: Instalar
        print("\n3️⃣ Instalando paquete...")
        os.chdir("temp_iqoption/iqoptionapi-master")
        result = subprocess.run([sys.executable, "setup.py", "install"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("   ✅ Instalación exitosa")
        else:
            print(f"   ❌ Error en instalación: {result.stderr}")
            
        os.chdir("../..")
        
    else:
        print(f"   ❌ Error descargando: HTTP {response.status_code}")
        
except Exception as e:
    print(f"   ❌ Error: {e}")
    print("\n   💡 Solución alternativa:")
    print("   1. Descarga manualmente: https://github.com/Lu-Yi-Hsun/iqoptionapi/archive/refs/heads/master.zip")
    print("   2. Extrae el ZIP")
    print("   3. cd iqoptionapi-master")
    print("   4. python setup.py install")

print("\n" + "=" * 70)
