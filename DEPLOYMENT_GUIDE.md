# Trading Bot SaaS - Guía de Despliegue

## 🎯 Arquitectura

**Backend (EasyPanel):**
- FastAPI server en `backend/api/main.py`
- Ejecuta el bot de trading
- Expone API REST y WebSocket

**Frontend (Ejecutable Windows):**
- GUI existente en `gui/modern_main_window.py`
- Se conecta al backend vía API
- Los usuarios lo instalan localmente

## 📦 Despliegue en EasyPanel

### 1. Preparar Repositorio Git

```bash
# Inicializar Git
git init

# Agregar archivos
git add .

# Commit
git commit -m "Trading Bot SaaS ready for deployment"

# Conectar con GitHub/GitLab
git remote add origin https://github.com/TU-USUARIO/TU-REPO.git
git push -u origin main
```

### 2. Configurar en EasyPanel

1. **Crear nuevo servicio**
   - Tipo: Docker
   - Repositorio: Tu repo de GitHub/GitLab

2. **Variables de entorno** (en EasyPanel):
   ```
   EXNOVA_EMAIL=tu_email@example.com
   EXNOVA_PASSWORD=tu_password
   GROQ_API_KEY=tu_groq_key
   BROKER_NAME=exnova
   ACCOUNT_TYPE=REAL
   ```

3. **Puerto**: 8000

4. **Build**: Automático (usa Dockerfile)

### 3. Verificar Despliegue

Una vez desplegado, tu API estará en:
```
https://tu-app.easypanel.host
```

Prueba:
```bash
curl https://tu-app.easypanel.host/
# Debe responder: {"status":"online","service":"Trading Bot API"}
```

## 🖥️ Crear Ejecutable para Usuarios

### Opción A: PyInstaller (Windows)

```bash
# Instalar PyInstaller
pip install pyinstaller

# Crear ejecutable
pyinstaller --onefile --windowed --name "TradingBot" run_modern_gui.py

# El ejecutable estará en dist/TradingBot.exe
```

### Opción B: Auto-py-to-exe (GUI)

```bash
pip install auto-py-to-exe
auto-py-to-exe
```

## 🔧 Configuración del Ejecutable

Los usuarios deben configurar la URL del servidor en el ejecutable.

Crear archivo `config_client.py`:

```python
# URL del servidor (EasyPanel)
SERVER_URL = "https://tu-app.easypanel.host"
```

## 📊 Flujo de Trabajo

1. **Usuario descarga ejecutable**
2. **Ejecutable se conecta al backend** (EasyPanel)
3. **Backend ejecuta operaciones** de trading
4. **Ejecutable muestra** datos en tiempo real vía WebSocket

## 🔒 Seguridad

Para producción, agregar:
- Autenticación JWT
- Base de datos de usuarios
- Rate limiting
- HTTPS obligatorio

## 📝 Próximos Pasos

1. ✅ Backend creado
2. ✅ Dockerfile listo
3. ⏳ Subir a Git
4. ⏳ Desplegar en EasyPanel
5. ⏳ Crear ejecutable
6. ⏳ Distribuir a usuarios
