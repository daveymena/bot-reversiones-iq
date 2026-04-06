FROM python:3.10-slim

WORKDIR /app

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Actualizar pip primero
RUN pip install --upgrade pip setuptools wheel

# Copiar requirements ligero para EasyPanel (sin PyTorch/CUDA)
COPY requirements_easypanel_lite.txt .

# Instalar dependencias
RUN pip install --no-cache-dir --timeout=300 --retries=5 -r requirements_easypanel_lite.txt

# Copiar código completo
COPY . .

# Variables de entorno
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV BROKER_NAME=exnova
ENV ACCOUNT_TYPE=PRACTICE
ENV HEADLESS_MODE=True
ENV BUILD_VERSION=V5-PRODUCTION

# Crear directorios para persistencia
RUN mkdir -p data models logs

# Health check
HEALTHCHECK --interval=60s --timeout=10s --start-period=30s --retries=3 \
  CMD python -c "import os; exit(0 if os.path.exists('data/bot_running.flag') else 1)" || exit 1

# Ejecutar bot headless
CMD ["python", "main_headless.py"]

