# Configuración para Easypanel (Bot de Aprendizaje 24/7)

## 1. Variables de Entorno
Configura estas variables en Easypanel > Tu App > Environment:

```env
# ============= BROKER =============
BROKER_NAME=exnova
EXNOVA_EMAIL=tu@email.com
EXNOVA_PASSWORD=tupassword
ACCOUNT_TYPE=PRACTICE

# ============= MODO OPERACIÓN (CRÍTICO) =============
HEADLESS_MODE=true

# ============= IA / OLLAMA =============
USE_LLM=True
# Configura la URL de tu servicio de Ollama en Easypanel
OLLAMA_BASE_URL=https://ollama-ollama.ginee6.easypanel.host
OLLAMA_MODEL=llama3.2:1b

# ============= TRADING =============
CAPITAL_PER_TRADE=1
EXPIRATION_TIME=60
```

## 2. Persistencia de Datos (Muy Importante)
Para que el bot no "olvide" lo aprendido cuando se reinicie la app, debes configurar un volumen:

1. Ve a la pestaña **Volumes** en Easypanel.
2. Añade un nuevo volumen:
   - **Host Path**: `trading_data` (o cualquier nombre)
   - **Mount Path**: `/app/data`

Esto asegurará que el archivo `data/learning_database.json` se mantenga a salvo entre reinicios.

## 3. Despliegue
1. Conecta tu repositorio de GitHub.
2. Easypanel detectará automáticamente el `Dockerfile`.
3. El comando de inicio por defecto será `python intelligent_learning.py`.

## 4. Monitoreo
Desde la pestaña **Logs** podrás ver:
- ✅ Conexión al broker.
- 📊 Los análisis técnicos.
- 🎯 Las validaciones de Ollama.
- 🛡️ Los bloqueos por trampas o inercia.
