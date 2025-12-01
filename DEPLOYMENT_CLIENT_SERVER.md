# Guía de Deployment: Arquitectura Cliente-Servidor

## 🏗️ Arquitectura

```
┌─────────────────────┐         ┌──────────────────────┐
│  CLIENTE WINDOWS    │  HTTPS  │   SERVIDOR EASYPANEL │
│  (Ejecutable .exe)  │◄────────┤   (Backend FastAPI)  │
│                     │         │                      │
│  - GUI Moderna      │   API   │  - LiveTrader 24/7   │
│  - TradingBotClient │         │  - WebSocket         │
│  - Polling/WS       │         │  - Database          │
└─────────────────────┘         └──────────────────────┘
```

## 📦 PARTE 1: Desplegar Backend en EasyPanel

### 1.1 Configurar Variables de Entorno en EasyPanel

En EasyPanel, agregar estas variables:

```
EXNOVA_EMAIL=tu_email@example.com
EXNOVA_PASSWORD=tu_contraseña
GROQ_API_KEY=tu_groq_key
BROKER_NAME=exnova
ACCOUNT_TYPE=PRACTICE  # o REAL
OLLAMA_URL=https://davey-ollama2.mapf5v.easypanel.host/api/generate
```

### 1.2 Crear Aplicación en EasyPanel

1. **Nueva App** → **Git Source**
2. **Repository:** `https://github.com/daveymena/bot-reversiones-iq`
3. **Branch:** `main`
4. **Build Method:** Dockerfile
5. **Port:** 8000
6. **Environment Variables:** (configuradas arriba)
7. **Deploy**

### 1.3 Obtener URL del Servidor

Una vez desplegado, EasyPanel te dará una URL como:
```
https://trading-bot-api.tudominio.easypanel.host
```

**Guarda esta URL**, la necesitarás para configurar el cliente.

## 🖥️ PARTE 2: Generar Ejecutable Windows

### 2.1 Instalar PyInstaller (si no lo tienes)

```bash
pip install pyinstaller
```

### 2.2 Configurar URL del Servidor

Edita `run_client.py` y cambia la línea:

```python
SERVER_URL = "https://trading-bot-api.tudominio.easypanel.host"
```

### 2.3 Generar Ejecutable

#### Opción A: Script Automático (Recomendado)
```bash
python build_exe.py
```

#### Opción B: Comando Manual
```bash
pyinstaller --onefile --windowed --name=TradingBotClient run_client.py
```

El ejecutable se generará en: `dist/TradingBotClient.exe`

## 🚀 PARTE 3: Distribuir el Cliente

### 3.1 Archivos a Distribuir

**Opción Portable (Sin instalación):**
- `TradingBotClient.exe` (único archivo necesario)

**Opción Instalador (Más profesional):**
Usa **Inno Setup** o **NSIS** para crear un instalador `.exe`

### 3.2 Configuración de Usuario

El usuario final solo necesita:
1. Ejecutar `TradingBotClient.exe`
2. La aplicación se conectará automáticamente a tu servidor en EasyPanel

## 🔧 PARTE 4: Actualizar Backend

Si el backend cambia en GitHub, en EasyPanel solo haz clic en:
- **Redeploy** → El servidor se actualizará automáticamente

Los clientes se beneficiarán de las mejoras sin necesidad de actualizar el ejecutable.

## 🔐 PARTE 5: Seguridad

### 5.1 HTTPS (Obligatorio)

EasyPanel proporciona HTTPS automáticamente. Asegúrate de usar `https://` en `SERVER_URL`.

### 5.2 Autenticación (Opcional)

Para evitar que cualquiera use tu servidor, puedes agregar autenticación:

1. Editar `backend/api/main.py`:
```python
from fastapi import Header, HTTPException

API_KEY = os.getenv("API_KEY", "mi_clave_secreta")

@app.post("/api/start")
async def start_bot(api_key: str = Header(None)):
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
    # ... resto del código
```

2. En el cliente, agregar header:
```python
headers = {"api_key": "mi_clave_secreta"}
response = requests.post(url, headers=headers)
```

## 📊 Ventajas de Esta Arquitectura

✅ **Backend 24/7:** El bot nunca se detiene, opera continuamente en EasyPanel
✅ **Múltiples Clientes:** Puedes conectarte desde varias computadoras
✅ **Actualizaciones:** Cambias el código una vez y todos los clientes se benefician
✅ **GUI Local:** Interfaz rápida y responsiva
✅ **Datos Centralizados:** Historial y estadísticas en un solo lugar
✅ **Portable:** El .exe puede ejecutarse sin instalación

## 🧪 Probar Localmente Primero

Antes de desplegar a producción:

1. **Terminal 1:** Iniciar backend local
```bash
uvicorn backend.api.main:app --reload
```

2. **Terminal 2:** Probar cliente
```bash
python run_client.py
```

Si funciona, el ejecutable también funcionará.

## 📝 Notas Finales

- El ejecutable es **solo la GUI**, no incluye el bot.
- El bot siempre corre en el servidor.
- Si el servidor cae, los clientes mostrarán "Desconectado".
- Puedes crear múltiples ejecutables con diferentes `SERVER_URL` para diferentes usuarios.
