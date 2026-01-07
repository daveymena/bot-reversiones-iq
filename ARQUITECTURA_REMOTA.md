# Arquitectura Cliente-Servidor

## Descripción

El bot ahora funciona con arquitectura distribuida:

```
┌─────────────────────┐         ┌──────────────────────┐
│   GUI de Escritorio │ ◄─────► │  Backend en Easypanel│
│   (Windows/Mac/Linux)│  HTTP   │  (FastAPI + Bot)     │
│                     │  WS     │                      │
└─────────────────────┘         └──────────────────────┘
                                          │
                                          ▼
                                   ┌─────────────┐
                                   │   Exnova    │
                                   │   Broker    │
                                   └─────────────┘
```

## Componentes

### 1. Backend (Easypanel)

**Ubicación**: `backend/api/main.py`

**Funciones**:
- Conectar/desconectar del broker
- Ejecutar operaciones de trading
- Gestionar el agente RL
- Exponer API REST + WebSocket
- Mantener estado del bot 24/7

**Endpoints**:
- `GET /` - Info de la API
- `GET /health` - Health check
- `POST /connect` - Conectar al broker
- `POST /disconnect` - Desconectar
- `GET /balance` - Obtener balance
- `GET /assets` - Listar activos
- `POST /start` - Iniciar trading
- `POST /stop` - Detener trading
- `GET /status` - Estado completo
- `GET /history` - Historial de trades
- `POST /config` - Actualizar configuración
- `WS /ws` - WebSocket para tiempo real

### 2. GUI de Escritorio (Cliente)

**Ubicación**: `gui/remote_main_window.py`

**Funciones**:
- Interfaz gráfica para control del bot
- Conectar a backend remoto
- Visualizar estado en tiempo real
- Configurar parámetros
- Ver gráficos y logs

**Características**:
- ✅ Misma interfaz que la versión local
- ✅ Conexión a cualquier backend (URL configurable)
- ✅ Actualizaciones en tiempo real vía WebSocket
- ✅ Gráficos de velas japonesas
- ✅ Logs en tiempo real
- ✅ Control completo del bot

### 3. API Client

**Ubicación**: `gui/api_client.py`

**Funciones**:
- Comunicación HTTP con backend
- Manejo de WebSocket
- Señales Qt para actualizar GUI
- Polling de estado

## Deployment

### Backend en Easypanel

1. **Crear aplicación en Easypanel**
   - Conectar repo: `https://github.com/daveymena/bot-reversiones-iq.git`
   - Easypanel detecta automáticamente el Dockerfile

2. **Configurar variables de entorno**:
   ```env
   EXNOVA_EMAIL=tu@email.com
   EXNOVA_PASSWORD=tupassword
   BROKER_NAME=exnova
   ACCOUNT_TYPE=PRACTICE
   GROQ_API_KEY=tu_api_key
   USE_LLM=True
   ```

3. **Configurar volúmenes persistentes**:
   - `/app/data` → 1GB (para experiences.json)
   - `/app/models` → 500MB (para rl_agent.zip)

4. **Deploy**
   - Click en "Deploy"
   - Esperar a que se construya
   - Obtener URL pública (ej: `https://tu-bot.easypanel.host`)

### GUI de Escritorio

1. **Instalar dependencias**:
   ```bash
   pip install -r requirements_gui.txt
   ```

2. **Ejecutar en modo desarrollo**:
   ```bash
   python main_remote.py
   ```

3. **Compilar ejecutable**:
   ```bash
   .\COMPILAR_GUI_REMOTA.bat
   ```
   
   Genera: `dist\TradingBot_Remote.exe`

4. **Distribuir**:
   - Copiar `TradingBot_Remote.exe` a cualquier PC
   - No requiere Python instalado
   - Solo necesita la URL del backend

## Uso

### Primera vez

1. **Desplegar backend en Easypanel**
2. **Abrir GUI de escritorio**
3. **Configurar URL del backend**:
   - Ingresar: `https://tu-bot.easypanel.host`
   - Click en "Configurar"
4. **Conectar al broker**:
   - Click en "🔌 Conectar Broker"
   - Esperar confirmación
5. **Iniciar trading**:
   - Click en "▶️ Iniciar Trading"

### Uso diario

1. Abrir GUI
2. Conectar (la URL se guarda automáticamente)
3. Monitorear estado
4. Ajustar configuración si es necesario

## Ventajas

✅ **Bot 24/7**: El backend corre continuamente en Easypanel  
✅ **Control remoto**: Controla el bot desde cualquier lugar  
✅ **Sin instalación compleja**: GUI solo necesita URL del backend  
✅ **Escalable**: Puedes tener múltiples GUIs conectadas al mismo backend  
✅ **Logs centralizados**: Todo se registra en el servidor  
✅ **Actualizaciones fáciles**: Solo actualiza el backend, las GUIs siguen funcionando  

## Seguridad

⚠️ **IMPORTANTE**:

1. **HTTPS**: Usa siempre HTTPS en producción
2. **Autenticación**: Considera agregar API keys o JWT
3. **Firewall**: Restringe acceso solo a IPs conocidas
4. **Variables de entorno**: Nunca commitees credenciales
5. **Modo PRACTICE**: Prueba primero en cuenta demo

## Troubleshooting

### Backend no responde
- Verifica que Easypanel esté corriendo
- Revisa logs en Easypanel
- Verifica variables de entorno

### GUI no conecta
- Verifica URL del backend
- Verifica que el puerto 8000 esté abierto
- Revisa firewall

### WebSocket se desconecta
- Normal después de inactividad
- Se reconecta automáticamente
- Verifica configuración de proxy/firewall

## Próximos Pasos

- [ ] Agregar autenticación JWT
- [ ] Dashboard web adicional
- [ ] Notificaciones push
- [ ] Multi-usuario
- [ ] Histórico de trades en base de datos
