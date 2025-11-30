"""
Actualiza el archivo .env con las credenciales de IQ Option
"""
import os

env_path = "C:\\trading\\.env"

# Leer contenido actual
with open(env_path, 'r') as f:
    lines = f.readlines()

# Agregar credenciales de IQ Option si no existen
iq_email_exists = any('IQ_OPTION_EMAIL' in line for line in lines)
iq_pass_exists = any('IQ_OPTION_PASSWORD' in line for line in lines)

new_lines = []
for line in lines:
    new_lines.append(line)

# Agregar al final si no existen
if not iq_email_exists:
    new_lines.append("\n# IQ Option Credentials\n")
    new_lines.append("IQ_OPTION_EMAIL=deinermena25@gmail.com\n")
    
if not iq_pass_exists:
    new_lines.append("IQ_OPTION_PASSWORD=6715320daveymena15.D\n")

# Escribir de vuelta
with open(env_path, 'w') as f:
    f.writelines(new_lines)

print("✅ Credenciales de IQ Option agregadas al .env")
print("\nContenido actualizado:")
with open(env_path, 'r') as f:
    print(f.read())
