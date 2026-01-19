FROM python:3.10-slim

WORKDIR /app

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libglib2.0-0 \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements de la nube (sin GUI para evitar errores libglib)
COPY requirements_cloud.txt .
RUN pip install --no-cache-dir -r requirements_cloud.txt

# Copiar código (Actualizado: V3-0943)
ENV BUILD_VERSION=V3-0943
COPY . .

# Variables de entorno
ENV PYTHONUNBUFFERED=1
ENV BROKER_NAME=exnova
ENV ACCOUNT_TYPE=PRACTICE
ENV HEADLESS_MODE=True

# Crear directorios para persistencia
RUN mkdir -p data models

# Ejecutar el Bot Orquestador (IA Central) por defecto
CMD ["python", "main_headless.py"]
