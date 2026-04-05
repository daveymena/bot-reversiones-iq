# 🚀 Deployment en EasyPanel

Guía paso a paso para desplegar el Trading Bot en EasyPanel.

## 📋 Requisitos Previos

- Cuenta en EasyPanel
- Repositorio Git con el código del bot
- Credenciales de Exnova (email y password)
- (Opcional) Servidor Ollama configurado

## 🎯 Paso 1: Preparar el Repositorio

### 1.1 Verificar que el repositorio esté limpio

```bash
# Asegurar que .env NO está en el repositorio
git status | grep ".env"  # No debe aparecer

# Verificar .gitignore
cat .gitignore | grep ".env"  # Debe estar presente
```

### 1.2 Hacer commit de cambios

```bash
git add .
git commit -m "Preparar bot para EasyPanel - V5-PRODUCTION"
git push origin main
```

## 🐳 Paso 2: Crear Aplicación en EasyPanel

### 2.1 Acceder a EasyPanel

1. Ir a https://easypanel.io
2. Iniciar sesión con tu cuenta
3. Ir a "Applications" → "Create New"

### 2.2 Configurar la Aplicación

**Nombre**: `trading-bot-pro`

**Tipo**: Docker

**Configuración Docker**:
- **Repository**: Tu URL de Git (ej: `https://github.com/usuario/trading-bot.git`)
- **Branch**: `main`
- **Dockerfile**: `Dockerfile`
- **Build Context**: `.`

### 2.3 Configurar Puertos (si es necesario)

- No se necesitan puertos expuestos (bot es headless)
- Logs se guardan en `/app/logs`

## 🔐 Paso 3: Configurar Variables de Entorno

En EasyPanel, ir a "Environment Variables" y agregar:

```bash
# ============= BROKER =============
BROKER_NAME=exnova
ACCOUNT_TYPE=PRACTICE  # Cambiar a REAL después de validar

# Credenciales Exnova (IMPORTANTE: Cambiar estos valores)
EXNOVA_EMAIL=tu@email.com
EXNOVA_PASSWORD=tupassword

# ============= TRADING =============
CAPITAL_PER_TRADE=1
MAX_MARTINGALE=0
DEFAULT_ASSET=EURUSD-OTC

# ============= AI/LLM =============
USE_LLM=True
USE_GROQ=False

# Ollama Configuration
AI_PROVIDER=ollama
USE_OLLAMA=true
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:1b
OLLAMA_TIMEOUT=120000

# ============= SYSTEM =============
HEADLESS_MODE=True
PYTHONUNBUFFERED=1
```

## 💾 Paso 4: Configurar Volúmenes (Persistencia)

En EasyPanel, ir a "Volumes" y crear:

| Ruta en Contenedor | Ruta en Host | Descripción |
|---|---|---|
| `/app/data` | `/data/trading-bot` | Datos y experiencias |
| `/app/models` | `/models/trading-bot` | Modelos entrenados |
| `/app/logs` | `/logs/trading-bot` | Logs de ejecución |

## 🚀 Paso 5: Desplegar

### 5.1 Iniciar la Aplicación

1. En EasyPanel, hacer clic en "Deploy"
2. Esperar a que se construya la imagen Docker (5-10 minutos)
3. Esperar a que inicie el contenedor

### 5.2 Verificar que está funcionando

```bash
# Ver logs en EasyPanel
# Ir a "Logs" y verificar que aparezca:
# "✅ Bot iniciado correctamente"
# "Broker: exnova"
# "Tipo de cuenta: PRACTICE"
```

## 📊 Paso 6: Monitoreo

### 6.1 Ver Logs

En EasyPanel:
1. Ir a la aplicación
2. Hacer clic en "Logs"
3. Ver logs en tiempo real

### 6.2 Verificar Salud

En EasyPanel:
1. Ir a "Health Check"
2. Debe mostrar "Healthy" (verde)

### 6.3 Acceder a Datos

Los datos se guardan en:
- `/data/trading-bot/experiences.json` - Experiencias
- `/data/trading-bot/deep_lessons.json` - Lecciones aprendidas
- `/data/trading-bot/history.csv` - Historial de operaciones
- `/logs/trading-bot/bot_*.log` - Logs

## 🔄 Paso 7: Actualizar el Bot

### 7.1 Hacer cambios locales

```bash
# Hacer cambios en el código
git add .
git commit -m "Actualizar bot"
git push origin main
```

### 7.2 Redeploy en EasyPanel

1. En EasyPanel, ir a la aplicación
2. Hacer clic en "Redeploy"
3. Esperar a que se construya y reinicie

## ⚠️ Paso 8: Cambiar a Cuenta REAL

**IMPORTANTE**: Solo después de validar en PRACTICE durante 1-2 semanas

### 8.1 Cambiar Variable de Entorno

En EasyPanel:
1. Ir a "Environment Variables"
2. Cambiar `ACCOUNT_TYPE=PRACTICE` a `ACCOUNT_TYPE=REAL`
3. Hacer clic en "Save"
4. Hacer clic en "Restart"

### 8.2 Verificar en Logs

```
"Tipo de cuenta: REAL"
```

## 🆘 Troubleshooting

### Problema: Bot no inicia

**Síntomas**: Health check falla, logs vacíos

**Soluciones**:
1. Verificar variables de entorno en EasyPanel
2. Verificar que EXNOVA_EMAIL y EXNOVA_PASSWORD están configurados
3. Ver logs completos en EasyPanel

```bash
# En EasyPanel, ver logs:
# Debe aparecer: "✅ Bot iniciado correctamente"
```

### Problema: Conexión rechazada

**Síntomas**: Error "Connection refused" en logs

**Soluciones**:
1. Verificar credenciales de Exnova
2. Verificar que la cuenta está activa
3. Probar credenciales localmente:

```bash
# Localmente
python -c "from exnovaapi.api import ExnovaAPI; api = ExnovaAPI(email='tu@email.com', password='pass'); print('OK')"
```

### Problema: Ollama no disponible

**Síntomas**: Error "Connection refused" para Ollama

**Soluciones**:
1. Verificar que Ollama está corriendo
2. Cambiar `USE_OLLAMA=false` temporalmente
3. Usar Groq en su lugar: `USE_GROQ=True`

### Problema: Logs no se guardan

**Síntomas**: Carpeta `/logs/trading-bot` vacía

**Soluciones**:
1. Verificar que el volumen está configurado correctamente
2. Verificar permisos de escritura
3. Ver logs en tiempo real en EasyPanel

## 📈 Optimización

### Limitar Recursos

En EasyPanel, ir a "Resources" y configurar:

```
CPU: 1-2 cores
Memory: 1-2 GB
```

### Configurar Auto-Restart

En EasyPanel, ir a "Restart Policy":
- **Policy**: Always
- **Max Retries**: 5
- **Delay**: 10 segundos

## 🔒 Seguridad

### Cambiar Credenciales Regularmente

```bash
# Cambiar password en Exnova
# Actualizar en EasyPanel:
# Environment Variables → EXNOVA_PASSWORD
```

### Usar Secrets (Recomendado)

Si EasyPanel soporta secrets:
1. Crear secret para EXNOVA_PASSWORD
2. Usar en lugar de variable de entorno

### Monitorear Acceso

1. Revisar logs regularmente
2. Verificar operaciones en Exnova
3. Alertas si hay errores de autenticación

## 📞 Soporte

Si tienes problemas:

1. Revisar logs en EasyPanel
2. Verificar variables de entorno
3. Probar localmente con `python main_headless.py`
4. Abrir issue en GitHub

---

**Última actualización**: Abril 2026
**Versión**: V5-PRODUCTION
