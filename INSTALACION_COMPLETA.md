# 📦 Instalación Completa - Trading Bot Pro

## Requisitos del Sistema

- **Python**: 3.8 o superior
- **Node.js**: 18 o superior
- **npm**: Incluido con Node.js
- **Sistema Operativo**: Windows, Linux o macOS

## 🔧 Instalación Paso a Paso

### 1. Clonar o Descargar el Proyecto

Si tienes el proyecto en un repositorio:
```bash
git clone <url-del-repositorio>
cd trading-bot
```

### 2. Instalar Dependencias de Python

```bash
# Crear entorno virtual (recomendado)
python -m venv env

# Activar entorno virtual
# Windows:
env\Scripts\activate
# Linux/Mac:
source env/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

**Nota sobre iqoptionapi**: Si hay problemas con iqoptionapi, instálalo manualmente:
```bash
pip install https://github.com/Lu-Yi-Hsun/iqoptionapi/archive/master.zip
```

### 3. Configurar Variables de Entorno

Copia el archivo de ejemplo:
```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

Edita `.env` con tus credenciales:
```env
# Broker Exnova (Recomendado)
EXNOVA_EMAIL=tu@email.com
EXNOVA_PASSWORD=tupassword

# Broker IQ Option (Opcional)
IQ_OPTION_EMAIL=tu@email.com
IQ_OPTION_PASSWORD=tupassword

# Configuración del Bot
BROKER_NAME=exnova
ACCOUNT_TYPE=PRACTICE

# IA (Opcional pero recomendado)
GROQ_API_KEY=tu_groq_api_key
USE_LLM=True
USE_GROQ=True
OLLAMA_MODEL=llama3
OLLAMA_BASE_URL=http://localhost:11434
```

### 4. Instalar Dependencias del Frontend (Para Versión Web)

```bash
cd frontend-web
npm install
cd ..
```

### 5. Configurar Frontend

```bash
cd frontend-web

# Windows
copy .env.example .env.local

# Linux/Mac
cp .env.example .env.local

cd ..
```

Edita `frontend-web/.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=http://localhost:8000
```

## ✅ Verificar Instalación

### Verificar Python y Dependencias

```bash
python --version
# Debe mostrar Python 3.8 o superior

pip list | grep fastapi
# Debe mostrar fastapi instalado

pip list | grep stable-baselines3
# Debe mostrar stable-baselines3 instalado
```

### Verificar Node.js y Dependencias

```bash
node --version
# Debe mostrar v18.0.0 o superior

cd frontend-web
npm list next
# Debe mostrar next instalado
cd ..
```

## 🚀 Ejecutar el Proyecto

### Opción 1: Versión Desktop (Solo Bot)

```bash
# Activar entorno virtual si no está activo
# Windows: env\Scripts\activate
# Linux/Mac: source env/bin/activate

# Ejecutar interfaz moderna
python main_modern.py

# O interfaz clásica
python main.py
```

### Opción 2: Versión Web (Recomendado)

**Windows**:
```bash
start_web.bat
```

**Linux/Mac**:
```bash
chmod +x start_web.sh
./start_web.sh
```

**Manual** (2 terminales):

Terminal 1 - Backend:
```bash
# Desde la raíz del proyecto
python -m uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000
```

Terminal 2 - Frontend:
```bash
cd frontend-web
npm run dev
```

### Acceso

- **Desktop**: Se abre automáticamente
- **Web Frontend**: http://localhost:3000
- **Web Backend**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 🔍 Solución de Problemas

### Error: "No module named 'fastapi'"

```bash
pip install fastapi uvicorn[standard] python-socketio
```

### Error: "Cannot find module 'next'"

```bash
cd frontend-web
rm -rf node_modules package-lock.json
npm install
cd ..
```

### Error: "Port 8000 already in use"

```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

### Error: "Port 3000 already in use"

```bash
cd frontend-web
npm run dev -- -p 3001
```

### Error de conexión al broker

1. Verifica tus credenciales en `.env`
2. Asegúrate de usar PRACTICE mode primero
3. Verifica tu conexión a internet
4. Revisa los logs del bot

### Error: "websocket-client version conflict"

```bash
pip uninstall websocket-client
pip install websocket-client==1.8.0
```

## 📚 Dependencias Instaladas

### Python (Backend + Bot)
- **numpy**: Cálculos numéricos
- **pandas**: Manipulación de datos
- **ta**: Indicadores técnicos
- **gymnasium**: Entorno RL
- **stable-baselines3**: Algoritmo PPO
- **python-dotenv**: Variables de entorno
- **requests**: Cliente HTTP
- **websocket-client**: WebSocket (versión específica)
- **iqoptionapi**: API de IQ Option
- **PySide6**: Interfaz gráfica desktop
- **pyqtgraph**: Gráficos desktop
- **groq**: Cliente Groq LLM
- **ollama**: Cliente Ollama LLM
- **fastapi**: Framework web
- **uvicorn**: Servidor ASGI
- **python-socketio**: WebSocket servidor
- **python-multipart**: Manejo de formularios
- **aiofiles**: Archivos asíncronos

### Node.js (Frontend Web)
- **next**: Framework React
- **react**: Biblioteca UI
- **typescript**: Tipado estático
- **tailwindcss**: Framework CSS
- **zustand**: Estado global
- **@tanstack/react-query**: Gestión de datos
- **socket.io-client**: Cliente WebSocket
- **lightweight-charts**: Gráficos financieros
- **lucide-react**: Iconos
- **axios**: Cliente HTTP
- **date-fns**: Manejo de fechas

## 🎯 Próximos Pasos

Después de la instalación:

1. **Probar conexión**: Conecta al broker en PRACTICE mode
2. **Verificar balance**: Asegúrate de ver tu balance
3. **Probar bot**: Inicia el bot y observa su comportamiento
4. **Revisar logs**: Monitorea los logs para detectar problemas
5. **Ajustar configuración**: Modifica parámetros según necesites

## 📖 Documentación Adicional

- **Inicio Rápido**: `INICIO_RAPIDO.md`
- **Cómo Ejecutar**: `COMO_EJECUTAR.md`
- **Versión Web**: `EJECUTAR_VERSION_WEB.md`
- **Guía de Uso**: `GUIA_USO_BOT.md`
- **Documentación Completa**: `VERSION_WEB_COMPLETA.md`

## 💡 Consejos

1. **Usa entorno virtual** para evitar conflictos de dependencias
2. **Prueba primero en PRACTICE** antes de usar dinero real
3. **Mantén actualizadas** las dependencias regularmente
4. **Haz backups** de tu configuración y modelos entrenados
5. **Monitorea los logs** constantemente durante el trading

## 🆘 Soporte

Si encuentras problemas:
1. Revisa esta guía de instalación
2. Consulta la documentación específica
3. Revisa los logs de error
4. Verifica que todas las dependencias estén instaladas
5. Asegúrate de tener las versiones correctas

## ✅ Checklist de Instalación

- [ ] Python 3.8+ instalado
- [ ] Node.js 18+ instalado
- [ ] Entorno virtual creado y activado
- [ ] Dependencias de Python instaladas
- [ ] Dependencias de Node.js instaladas
- [ ] Archivo `.env` configurado
- [ ] Archivo `frontend-web/.env.local` configurado
- [ ] Credenciales del broker configuradas
- [ ] Bot desktop funciona correctamente
- [ ] Backend web inicia sin errores
- [ ] Frontend web inicia sin errores
- [ ] Conexión al broker exitosa
- [ ] Gráficos se muestran correctamente

**¡Listo para empezar a hacer trading! 🚀**
