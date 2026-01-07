# Variables de Entorno para Easypanel

## Variables Requeridas

Configura estas variables en Easypanel > Tu App > Environment:

```env
# ============= BROKER (Solo Exnova) =============
# Opción 1: Sin credenciales (usuarios ingresan desde GUI)
BROKER_NAME=exnova

# Opción 2: Con credenciales por defecto (opcional)
# EXNOVA_EMAIL=tu@email.com
# EXNOVA_PASSWORD=tupassword
# ACCOUNT_TYPE=PRACTICE

# ============= GROQ API (LLM) =============
GROQ_API_KEY=tu_groq_api_key
USE_LLM=True
USE_GROQ=True

# ============= OLLAMA (Opcional) =============
OLLAMA_URL=https://davey-ollama2.mapf5v.easypanel.host
OLLAMA_MODEL=llama3.2:3b
OLLAMA_MODEL_FAST=gemma2:2b

# ============= TRADING =============
DEFAULT_ASSET=EURUSD-OTC
CAPITAL_PER_TRADE=10
EXPIRATION_TIME=60

# ============= RISK MANAGEMENT =============
MAX_MARTINGALE=2
STOP_LOSS_PERCENT=20
TAKE_PROFIT_PERCENT=10
```

## Variables Opcionales

```env
# Base de datos (si la habilitas)
ENABLE_DATABASE=False
DB_HOST=localhost
DB_PORT=5432
DB_NAME=trading_bot
DB_USER=postgres
DB_PASSWORD=tupassword
```

## ⚠️ IMPORTANTE

1. **Inicia en PRACTICE**: Siempre usa `ACCOUNT_TYPE=PRACTICE` primero
2. **Groq API Key**: Obtén tu key gratis en https://console.groq.com
3. **No commitees credenciales**: Nunca subas el `.env` a GitHub
4. **Cambia a REAL**: Solo después de validar en PRACTICE

## 📋 Checklist de Configuración

- [ ] Variables configuradas en Easypanel
- [ ] `ACCOUNT_TYPE=PRACTICE` para pruebas
- [ ] Groq API Key válida
- [ ] Credenciales de Exnova correctas
- [ ] Deploy exitoso
- [ ] Logs sin errores
- [ ] Bot conecta al broker
- [ ] Validado en PRACTICE por 24h
- [ ] Cambiar a `ACCOUNT_TYPE=REAL` (opcional)

## 🔍 Verificar Configuración

Después del deploy, revisa los logs en Easypanel:

```
✅ Conectado a EXNOVA (PRACTICE)
✅ Modelo RL cargado
✅ Sistema de aprendizaje inicializado
🚀 Iniciando LiveTrader 24/7
```

Si ves errores:
- Verifica credenciales
- Revisa que Groq API Key sea válida
- Confirma que el broker sea "exnova"
