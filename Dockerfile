# Dockerfile para Exnova Trading Bot
FROM python:3.11-slim

# Variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar requirements
COPY bot/requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código del bot
COPY bot/ ./bot/

# Crear directorios necesarios
RUN mkdir -p /app/bot/data /app/bot/models /app/bot/logs

# Exponer puerto (si necesitas API en el futuro)
EXPOSE 8000

# Comando de inicio
CMD ["python", "bot/main.py"]
