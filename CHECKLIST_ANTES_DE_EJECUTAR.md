# ✅ Checklist Antes de Ejecutar - Trading Bot Pro

## 📋 Verificación Pre-Ejecución

### 1. Instalación de Software Base

- [ ] Python 3.8+ instalado
  ```bash
  python --version
  ```

- [ ] Node.js 18+ instalado (para versión web)
  ```bash
  node --version
  ```

- [ ] pip actualizado
  ```bash
  python -m pip install --upgrade pip
  ```

### 2. Dependencias de Python

- [ ] Entorno virtual creado
  ```bash
  python -m venv env
  ```

- [ ] Entorno virtual activado
  ```bash
  # Windows:
  env\Scripts\activate
  # Linux/Mac:
  source env/bin/activate
  ```

- [ ] Dependencias instaladas
  ```bash
  pip install -r requirements.txt
  ```

- [ ] Verificar instalación de FastAPI
  ```bash
  pip show fastapi
  ```

- [ ] Verificar instalación de stable-baselines3
  ```bash
  pip show stable-baselines3
  ```

### 3. Dependencias de Node.js (Solo Versión Web)

- [ ] Dependencias del frontend instaladas
  ```bash
  cd frontend-web
  npm install
  cd ..
  ```

- [ ] Verificar instalación de Next.js
  ```bash
  cd frontend-web
  npm list next
  cd ..
  ```

### 4. Configuración de Variables de Entorno

- [ ] Archivo `.env` existe en la raíz
  ```bash
  # Windows:
  if exist .env (echo OK) else (echo FALTA)
  # Linux/Mac:
  [ -f .env ] && echo "OK" || echo "FALTA"
  ```

- [ ] Credenciales de Exnova configuradas
  - [ ] EXNOVA_EMAIL
  - [ ] EXNOVA_PASSWORD

- [ ] Configuración del bot
  - [ ] BROKER_NAME=exnova
  - [ ] ACCOUNT_TYPE=PRACTICE (para pruebas)

- [ ] Configuración de IA (opcional)
  - [ ] GROQ_API_KEY (si usas Groq)
  - [ ] USE_LLM=True
  - [ ] USE_GROQ=True

- [ ] Archivo `frontend-web/.env.local` existe (solo web)
  ```bash
  # Windows:
  if exist frontend-web\.env.local (echo OK) else (echo FALTA)
  # Linux/Mac:
  [ -f frontend-web/.env.local ] && echo "OK" || echo "FALTA"
  ```

- [ ] URLs configuradas en `.env.local`
  - [ ] NEXT_PUBLIC_API_URL=http://localhost:8000
  - [ ] NEXT_PUBLIC_WS_URL=http://localhost:8000

### 5. Verificación de Puertos

- [ ] Puerto 8000 libre (backend)
  ```bash
  # Windows:
  netstat -ano | findstr :8000
  # Linux/Mac:
  lsof -i :8000
  ```
  (No debe mostrar nada si está libre)

- [ ] Puerto 3000 libre (frontend)
  ```bash
  # Windows:
  netstat -ano | findstr :3000
  # Linux/Mac:
  lsof -i :3000
  ```
  (No debe mostrar nada si está libre)

### 6. Verificación de Archivos Clave

- [ ] Backend existe
  ```bash
  # Windows:
  if exist backend\api\main.py (echo OK) else (echo FALTA)
  # Linux/Mac:
  [ -f backend/api/main.py ] && echo "OK" || echo "FALTA"
  ```

- [ ] Core del bot existe
  ```bash
  # Windows:
  if exist core\trader.py (echo OK) else (echo FALTA)
  # Linux/Mac:
  [ -f core/trader.py ] && echo "OK" || echo "FALTA"
  ```

- [ ] Frontend existe (solo web)
  ```bash
  # Windows:
  if exist frontend-web\src\app\page.tsx (echo OK) else (echo FALTA)
  # Linux/Mac:
  [ -f frontend-web/src/app/page.tsx ] && echo "OK" || echo "FALTA"
  ```

### 7. Conexión a Internet

- [ ] Conexión a internet activa
  ```bash
  # Windows:
  ping -n 1 google.com
  # Linux/Mac:
  ping -c 1 google.com
  ```

- [ ] Acceso a Exnova/IQ Option
  ```bash
  # Windows:
  ping -n 1 exnova.com
  # Linux/Mac:
  ping -c 1 exnova.com
  ```

### 8. Credenciales del Broker

- [ ] Cuenta de Exnova creada
- [ ] Email verificado
- [ ] Contraseña correcta
- [ ] Cuenta PRACTICE tiene balance
- [ ] Puedes acceder a la web de Exnova

### 9. Configuración de IA (Opcional)

Si usas Groq:
- [ ] API Key de Groq obtenida
- [ ] API Key configurada en `.env`
- [ ] Conexión a Groq funciona

Si usas Ollama:
- [ ] Ollama instalado localmente
- [ ] Modelo descargado (llama3)
  ```bash
  ollama list
  ```
- [ ] Ollama corriendo
  ```bash
  curl http://localhost:11434/api/tags
  ```

### 10. Prueba de Componentes

- [ ] Importar módulos principales funciona
  ```bash
  python -c "from core.trader import LiveTrader; print('OK')"
  ```

- [ ] Importar FastAPI funciona
  ```bash
  python -c "import fastapi; print('OK')"
  ```

- [ ] Importar stable-baselines3 funciona
  ```bash
  python -c "import stable_baselines3; print('OK')"
  ```

## 🚀 Listo para Ejecutar

Si todos los checks están ✅, puedes ejecutar:

### Versión Desktop
```bash
python main_modern.py
```

### Versión Web
```bash
# Windows:
start_web.bat

# Linux/Mac:
./start_web.sh
```

## ⚠️ Antes de Empezar a Tradear

### Configuración Inicial Recomendada

- [ ] Modo: **PRACTICE** (no REAL)
- [ ] Capital por trade: **$10**
- [ ] Pérdida máxima diaria: **$100**
- [ ] Pasos martingala: **3**
- [ ] Activo: **EURUSD-OTC**
- [ ] Usar LLM: **True** (si tienes API key)

### Primeros Pasos

1. [ ] Conectar al broker
2. [ ] Verificar balance visible
3. [ ] Observar el bot sin iniciar (ver análisis)
4. [ ] Iniciar bot en PRACTICE
5. [ ] Monitorear primeros 5 trades
6. [ ] Revisar estadísticas
7. [ ] Ajustar configuración si es necesario

### Monitoreo Continuo

- [ ] Revisar logs cada 15 minutos
- [ ] Verificar win rate después de 20 trades
- [ ] Ajustar parámetros según resultados
- [ ] Detener si pérdidas superan límite
- [ ] Hacer backup de configuración exitosa

## 🐛 Si Algo Falla

### Backend no inicia
1. [ ] Verificar puerto 8000 libre
2. [ ] Reinstalar dependencias
3. [ ] Revisar logs de error
4. [ ] Verificar `.env` configurado

### Frontend no inicia
1. [ ] Verificar puerto 3000 libre
2. [ ] Reinstalar node_modules
3. [ ] Verificar `.env.local` configurado
4. [ ] Limpiar caché de Next.js

### No conecta al broker
1. [ ] Verificar credenciales
2. [ ] Verificar conexión a internet
3. [ ] Probar acceso web a Exnova
4. [ ] Revisar logs del bot
5. [ ] Intentar con otro broker

### Bot no ejecuta trades
1. [ ] Verificar que está iniciado
2. [ ] Verificar balance suficiente
3. [ ] Revisar logs de análisis
4. [ ] Verificar activo disponible
5. [ ] Ajustar parámetros de entrada

## 📊 Métricas de Éxito

Después de 50 trades en PRACTICE:

- [ ] Win rate > 60%
- [ ] Profit total > $0
- [ ] Drawdown < 20%
- [ ] Sin errores críticos
- [ ] Logs sin warnings constantes

Si cumples estos criterios, puedes considerar:
- Aumentar capital por trade
- Probar otros activos
- Optimizar parámetros
- (Solo si estás seguro) Cambiar a REAL

## ⚠️ IMPORTANTE

**NUNCA cambies a modo REAL sin:**
1. Probar extensivamente en PRACTICE
2. Tener win rate consistente > 60%
3. Entender completamente cómo funciona el bot
4. Estar preparado para perder el capital invertido
5. Monitorear constantemente el bot

## 📝 Notas Finales

- Guarda este checklist para futuras ejecuciones
- Actualiza según tu experiencia
- Documenta problemas y soluciones
- Haz backups regulares de configuración
- Mantén logs de rendimiento

---

**¡Buena suerte con el trading! 🚀📈**
