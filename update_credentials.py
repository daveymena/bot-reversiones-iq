"""
Script para actualizar credenciales en .env de forma segura
"""
import os

env_path = "C:\\trading\\.env"
new_email = "kennethcelorio@gmail.com"
new_password = "6715320davey"

print(f"Actualizando .env con: {new_email}")

try:
    with open(env_path, 'r') as f:
        lines = f.readlines()
    
    new_lines = []
    updated_email = False
    updated_pass = False
    
    for line in lines:
        if line.startswith("IQ_OPTION_EMAIL="):
            new_lines.append(f"IQ_OPTION_EMAIL={new_email}\n")
            updated_email = True
        elif line.startswith("IQ_OPTION_PASSWORD="):
            new_lines.append(f"IQ_OPTION_PASSWORD={new_password}\n")
            updated_pass = True
        else:
            new_lines.append(line)
            
    if not updated_email:
        new_lines.append(f"\nIQ_OPTION_EMAIL={new_email}\n")
    if not updated_pass:
        new_lines.append(f"IQ_OPTION_PASSWORD={new_password}\n")
        
    with open(env_path, 'w') as f:
        f.writelines(new_lines)
        
    print("✅ Archivo .env actualizado correctamente")
    
except Exception as e:
    print(f"❌ Error actualizando .env: {e}")
