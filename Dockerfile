# ─────────────────────────────────────────────────────────────────────────────
# Exnova Trading Bot — Dockerfile para EasyPanel
# Motor de trading inteligente + IA de razonamiento continuo
# ─────────────────────────────────────────────────────────────────────────────
FROM python:3.11-slim

# Entorno limpio y reproducible
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Dependencias del sistema mínimas
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Directorio de trabajo
WORKDIR /app

# 1. Instalar dependencias primero (cacheado si no cambian)
COPY bot/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 2. Copiar el código del bot
COPY bot/ ./bot/

# 3. Crear directorios persistentes (datos, logs, modelos)
RUN mkdir -p /app/bot/data \
             /app/bot/logs \
             /app/bot/brain

# 4. Variables de entorno requeridas (sobreescribir en EasyPanel)
# Credenciales Exnova
ENV EXNOVA_EMAIL="" \
    EXNOVA_PASSWORD="" \
    # OpenCode AI
    OPENCODE_BASE_URL="https://tecnovariedades-provedor-ia.er7iaf.easypanel.host/v1" \
    OPENCODE_API_KEY="" \
    OPENCODE_MODEL_FAST="opencode/deepseek-v4-flash-free" \
    OPENCODE_MODEL_DEEP="opencode/qwen3.6-plus-free" \
    # GitHub (fallback)
    GITHUB_TOKEN="" \
    # Configuración
    MIN_CONFIDENCE="0.70" \
    MAX_CONSEC_LOSSES="3" \
    LOG_LEVEL="INFO"

# Puerto (para healthcheck futuro / API)
EXPOSE 8000

# Healthcheck — el bot siempre escribe en logs
HEALTHCHECK --interval=60s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import os, time; f='/app/bot/logs/bot.log'; \
        exit(0) if os.path.exists(f) and (time.time()-os.path.getmtime(f))<300 else exit(1)" \
    || exit 1

# Arrancar el bot
CMD ["python", "bot/main.py"]
