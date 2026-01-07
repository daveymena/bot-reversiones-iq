# Configuración de Easypanel

## 🎯 Dos Modos de Operación

### Modo 1: Multi-Usuario (Recomendado para distribución)

Cada usuario ingresa sus propias credenciales desde la GUI.

**Variables en Easypanel:**
```env
BROKER_NAME=exnova
GROQ_API_KEY=tu_groq_api_key_aqui
USE_LLM=True
USE_GROQ=True
OLLAMA_URL=https://davey-ollama2.mapf5v.easypanel.host
OLLAMA_MODEL=llama3.2:3b
OLLAMA_MODEL_FAST=gemma2:2b
DEFAULT_ASSET=EURUSD-OTC
CAPITAL_PER_TRADE=10
EXPIRATION_TIME=60
MAX_MARTINGALE=2
STOP_LOSS_PERCENT=20
TAKE_PROFIT_PERCENT=10
```

**Ventajas:**
- ✅ Cada usuario usa sus propias credenciales
- ✅ Cada usuario elige PRACTICE o REAL
- ✅ Más seguro (credenciales no en el servidor)
- ✅ Ideal para distribuir el ejecutable

**Cómo funciona:**
1. Usuario abre la GUI remota
2. Ingresa email y password de Exnova
3. Selecciona PRACTICE o REAL
4. Click en "Conectar"
5. Backend usa esas credenciales temporalmente

---

### Modo 2: Usuario Único (Para uso personal)

Backend tiene credenciales fijas, usuario solo abre la GUI.

**Variables en Easypanel:**
```env
EXNOVA_EMAIL=tu@email.com
EXNOVA_PASSWORD=tupassword
BROKER_NAME=exnova
ACCOUNT_TYPE=PRACTICE
GROQ_API_KEY=tu_groq_api_key_aqui
USE_LLM=True
USE_GROQ=True
OLLAMA_URL=https://davey-ollama2.mapf5v.easypanel.host
OLLAMA_MODEL=llama3.2:3b
OLLAMA_MODEL_FAST=gemma2:2b
DEFAULT_ASSET=EURUSD-OTC
CAPITAL_PER_TRADE=10
EXPIRATION_TIME=60
MAX_MARTINGALE=2
STOP_LOSS_PERCENT=20
TAKE_PROFIT_PERCENT=10
```

**Ventajas:**
- ✅ Más simple (no ingresar credenciales cada vez)
- ✅ Bot puede correr 24/7 automáticamente
- ✅ Ideal para uso personal

**Desventajas:**
- ⚠️ Credenciales en el servidor
- ⚠️ Solo una cuenta por backend
- ⚠️ Cambiar PRACTICE/REAL requiere redeploy

---

## 🎯 Recomendación

**Para distribuir el bot:** Usa **Modo 1** (Multi-Usuario)
- Compila el ejecutable remoto
- Distribuye a quien quieras
- Cada uno usa sus credenciales
- Tú solo pagas el servidor

**Para uso personal:** Usa **Modo 2** (Usuario Único)
- Más cómodo
- No ingresar credenciales cada vez
- Bot 24/7 automático

---

## 📋 Pasos de Configuración

### 1. Configurar Variables en Easypanel

1. Ve a tu app en Easypanel
2. Click en **Environment**
3. Pega las variables según el modo elegido
4. Click en **Save**

### 2. Deploy

1. Click en **Deploy**
2. Espera a que termine (1-2 minutos)
3. Verifica logs: debe decir "Trading Bot API iniciada"

### 3. Obtener URL

Tu backend estará en:
```
https://tu-app.easypanel.host
```

Copia esta URL, la necesitarás para la GUI.

### 4. Probar Conexión

Desde tu PC:
```bash
curl https://tu-app.easypanel.host/health
```

Debe responder:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-28T...",
  "connected": false
}
```

---

## 🔍 Verificar que Funciona

### Logs Correctos

En Easypanel > Logs debes ver:
```
🚀 Trading Bot API iniciada
📊 Broker: exnova
💼 Cuenta: PRACTICE (o vacío si modo multi-usuario)
```

### Errores Comunes

**Error: "No se pudo conectar al broker"**
- Verifica credenciales de Exnova
- Confirma que `BROKER_NAME=exnova`

**Error: "Groq API Key inválida"**
- Verifica que la key sea correcta
- Obtén una nueva en https://console.groq.com

**Error: "Ollama no responde"**
- Verifica que Ollama esté corriendo en Easypanel
- Confirma la URL: `https://davey-ollama2.mapf5v.easypanel.host`

---

## 🚀 Siguiente Paso

Una vez que el backend esté funcionando:

1. **Compila el ejecutable remoto:**
   ```bash
   .\COMPILAR_CLIENTE_REMOTO.bat
   ```

2. **Distribuye `TradingBot_Remote.exe`**
   - Copia el .exe a cualquier PC
   - No requiere Python instalado
   - Solo necesita la URL del backend

3. **Ejecuta y conecta:**
   - Abre el .exe
   - Ingresa URL del backend
   - Ingresa credenciales (si modo multi-usuario)
   - Selecciona PRACTICE o REAL
   - ¡Listo!
