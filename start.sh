#!/bin/bash

echo "🤖 Trading Bot Pro v2.0 - Inicio Rápido"
echo "========================================"
echo ""

# Verificar Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker no está instalado"
    echo "Instala Docker desde: https://docs.docker.com/get-docker/"
    exit 1
fi

# Verificar Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose no está instalado"
    echo "Instala Docker Compose desde: https://docs.docker.com/compose/install/"
    exit 1
fi

# Verificar archivo .env
if [ ! -f .env ]; then
    echo "⚠️  Archivo .env no encontrado"
    echo "Creando .env desde .env.example..."
    cp .env.example .env
    echo "✅ Archivo .env creado"
    echo ""
    echo "⚠️  IMPORTANTE: Edita el archivo .env con tus credenciales antes de continuar"
    echo "Presiona Enter cuando hayas configurado el .env..."
    read
fi

echo "🚀 Iniciando servicios..."
echo ""

# Construir imágenes
echo "📦 Construyendo imágenes Docker..."
docker-compose build

# Iniciar servicios
echo "▶️  Iniciando contenedores..."
docker-compose up -d

# Esperar a que los servicios estén listos
echo "⏳ Esperando a que los servicios estén listos..."
sleep 10

# Verificar estado
echo ""
echo "📊 Estado de los servicios:"
docker-compose ps

echo ""
echo "✅ ¡Trading Bot iniciado exitosamente!"
echo ""
echo "🌐 Accede a:"
echo "   - Frontend Web: http://localhost:3000"
echo "   - Backend API:  http://localhost:8000"
echo "   - API Docs:     http://localhost:8000/docs"
echo ""
echo "📝 Ver logs:"
echo "   docker-compose logs -f"
echo ""
echo "🛑 Detener:"
echo "   docker-compose down"
echo ""
