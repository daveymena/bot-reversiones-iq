#!/usr/bin/env python3
"""
Script para reparar el archivo experiences.json corrupto
"""
import json
import os
import shutil
from datetime import datetime

def reparar_experiences():
    """Repara o crea nuevo archivo de experiencias"""
    
    experiences_file = "data/experiences.json"
    backup_file = f"data/experiences_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    # Crear carpeta data si no existe
    os.makedirs("data", exist_ok=True)
    
    # Si existe el archivo, hacer backup
    if os.path.exists(experiences_file):
        print(f"📦 Creando backup: {backup_file}")
        try:
            shutil.copy(experiences_file, backup_file)
            print(f"✅ Backup creado")
        except Exception as e:
            print(f"⚠️ Error creando backup: {e}")
    
    # Intentar cargar y reparar
    experiences = []
    
    if os.path.exists(experiences_file):
        print(f"🔧 Intentando reparar {experiences_file}...")
        
        try:
            with open(experiences_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Intentar cargar como JSON
            try:
                experiences = json.loads(content)
                print(f"✅ Archivo válido, contiene {len(experiences)} experiencias")
                return
            except json.JSONDecodeError as e:
                print(f"❌ Error JSON en línea {e.lineno}, columna {e.colno}")
                print(f"   Mensaje: {e.msg}")
                
                # Intentar recuperar experiencias válidas
                print("🔧 Intentando recuperar experiencias válidas...")
                
                # Buscar todas las experiencias completas
                import re
                pattern = r'\{[^}]*"state":[^}]*"action":[^}]*"reward":[^}]*"next_state":[^}]*"done":[^}]*"metadata":[^}]*\}'
                matches = re.findall(pattern, content, re.DOTALL)
                
                for match in matches:
                    try:
                        exp = json.loads(match)
                        experiences.append(exp)
                    except:
                        continue
                
                print(f"✅ Recuperadas {len(experiences)} experiencias válidas")
        
        except Exception as e:
            print(f"❌ Error leyendo archivo: {e}")
    
    # Crear archivo nuevo limpio
    print(f"📝 Creando archivo limpio con {len(experiences)} experiencias...")
    
    try:
        with open(experiences_file, 'w', encoding='utf-8') as f:
            json.dump(experiences, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Archivo reparado exitosamente")
        print(f"📊 Total experiencias: {len(experiences)}")
        
        if len(experiences) > 0:
            print(f"📈 Primera experiencia: {experiences[0].get('metadata', {}).get('asset', 'N/A')}")
            print(f"📈 Última experiencia: {experiences[-1].get('metadata', {}).get('asset', 'N/A')}")
    
    except Exception as e:
        print(f"❌ Error escribiendo archivo: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("="*60)
    print("REPARADOR DE EXPERIENCES.JSON")
    print("="*60)
    print()
    
    success = reparar_experiences()
    
    print()
    print("="*60)
    if success:
        print("✅ REPARACIÓN COMPLETADA")
    else:
        print("❌ REPARACIÓN FALLIDA")
    print("="*60)
    print()
