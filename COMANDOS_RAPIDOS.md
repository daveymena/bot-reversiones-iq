# ⚡ COMANDOS RÁPIDOS

## 🔍 Validación

```bash
# Validar que todo está listo
python scripts/validate_deployment.py
```

## 📤 Git

```bash
# Ver estado
git status

# Agregar cambios
git add .

# Commit
git commit -m "Preparar bot para Git y EasyPanel - V5-PRODUCTION"

# Push
git push origin main

# Ver cambios
git log --oneline -5
```

## 🐳 Docker Local

```bash
# Construir imagen
docker build -t trading-bot .

# Ejecutar contenedor
docker run -d \
  --name trading-bot \
  -e EXNOVA_EMAIL=tu@email.com \
  -e EXNOVA_PASSWORD=tupassword \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/models:/app/models \
  -v $(pwd)/logs:/app/logs \
  trading-bot

# Ver logs
docker logs -f trading-bot

# Detener
docker stop trading-bot

# Remover
docker rm trading-bot
```

## 🐳 Docker Compose

```bash
# Iniciar
docker-compose up -d

# Ver logs
docker-compose logs -f trading-bot

# Detener
docker-compose down

# Reiniciar
docker-compose restart trading-bot

# Rebuild
docker-compose up -d --build
```

## 🚀 EasyPanel

### Crear Aplicación
1. https://easypanel.io
2. Applications → Create New
3. Nombre: `trading-bot-pro`
4. Tipo: Docker
5. Repository: Tu URL de Git
6. Branch: `main`

### Configurar Variables
```bash
BROKER_NAME=exnova
ACCOUNT_TYPE=PRACTICE
EXNOVA_EMAIL=tu@email.com
EXNOVA_PASSWORD=tupassword
CAPITAL_PER_TRADE=1
MAX_MARTINGALE=0
USE_LLM=True
USE_GROQ=False
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:1b
```

### Configurar Volúmenes
| Contenedor | Host |
|-----------|------|
| `/app/data` | `/data/trading-bot` |
| `/app/models` | `/models/trading-bot` |
| `/app/logs` | `/logs/trading-bot` |

### Desplegar
1. Deploy
2. Esperar 5-10 minutos
3. Ver logs

### Redeploy
1. Applications → trading-bot-pro
2. Redeploy
3. Esperar

## 📊 Monitoreo

```bash
# Ver logs locales
tail -f logs/bot_*.log

# Ver datos
ls -la data/

# Ver modelos
ls -la models/

# Ver experiencias
cat data/experiences.json | python -m json.tool | head -50

# Ver lecciones
cat data/deep_lessons.json | python -m json.tool | head -50
```

## 🔧 Mantenimiento

```bash
# Limpiar caché
find . -type d -name __pycache__ -exec rm -r {} +
find . -type f -name "*.pyc" -delete

# Limpiar logs antiguos
rm logs/bot_*.log

# Backup de datos
cp -r data data_backup_$(date +%Y%m%d)

# Restaurar backup
cp -r data_backup_YYYYMMDD data
```

## 🆘 Troubleshooting

```bash
# Verificar conexión Exnova
python -c "from exnovaapi.api import ExnovaAPI; print('OK')"

# Verificar configuración
python -c "from config import Config; print(f'Email: {Config.EXNOVA_EMAIL}')"

# Verificar LLM
python -c "from ai.llm_client import LLMClient; print('OK')"

# Verificar RL Agent
python -c "from core.agent import RLAgent; print('OK')"
```

## 📝 Cambiar Configuración

```bash
# Editar .env
nano .env  # o usar tu editor favorito

# Cambiar a REAL (después de validar en PRACTICE)
# Editar .env:
# ACCOUNT_TYPE=REAL

# Cambiar credenciales
# Editar .env:
# EXNOVA_EMAIL=nuevo@email.com
# EXNOVA_PASSWORD=nuevapassword
```

## 🔄 Actualizar Bot

```bash
# 1. Hacer cambios locales
# 2. Commit y push
git add .
git commit -m "Actualizar bot"
git push origin main

# 3. En EasyPanel: Redeploy
# O en Docker Compose:
docker-compose up -d --build
```

## 📚 Documentación

```bash
# Leer README
cat README.md

# Leer guía de deployment
cat docs/DEPLOYMENT_EASYPANEL.md

# Leer checklist
cat CHECKLIST_FINAL.md

# Leer resumen
cat RESUMEN_PREPARACION.md

# Leer inicio rápido
cat INICIO_RAPIDO_GIT_EASYPANEL.md
```

## 🎯 Flujo Completo

```bash
# 1. Validar
python scripts/validate_deployment.py

# 2. Subir a Git
git add .
git commit -m "Preparar bot para Git y EasyPanel - V5-PRODUCTION"
git push origin main

# 3. Desplegar en EasyPanel
# - Crear aplicación
# - Configurar variables
# - Configurar volúmenes
# - Desplegar

# 4. Monitorear
# - Ver logs en EasyPanel
# - Verificar operaciones en Exnova
# - Revisar rentabilidad

# 5. Cambiar a REAL (opcional)
# - Después de 1-2 semanas en PRACTICE
# - Cambiar ACCOUNT_TYPE=REAL
# - Redeploy
```

---

**Última actualización**: Abril 2026
**Versión**: V5-PRODUCTION
