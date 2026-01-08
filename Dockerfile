FROM python:3.10-slim

WORKDIR /app

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements de la nube (sin GUI para evitar errores libglib)
COPY requirements_cloud.txt .
RUN pip install --no-cache-dir -r requirements_cloud.txt

# Copiar código (Actualizado: 2026-01-08-0505)
ENV BUILD_VERSION=2026.01.08.0505
COPY . .

# Variables de entorno
ENV PYTHONUNBUFFERED=1
ENV BROKER_NAME=exnova
ENV ACCOUNT_TYPE=PRACTICE
ENV HEADLESS_MODE=True

# Crear directorios para persistencia
RUN mkdir -p data models

# Ejecutar el Bot de Aprendizaje Inteligente por defecto
# Nota: Si prefieres ejecutar la API, puedes cambiar esto a:
# CMD ["uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
CMD ["python", "intelligent_learning.py"]
