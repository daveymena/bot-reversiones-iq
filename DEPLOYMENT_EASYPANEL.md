# 🚀 Guía de Deployment en EasyPanel

## ✅ Archivos Actualizados

- [x] `Dockerfile` - Actualizado para usar `main_headless.py`
- [x] `docker-compose.yml` - Configurado con volúmenes y logs
- [x] `main_headless.py` - Actualizado con health check flag
- [x] `requirements_cloud.txt` - Dependencias sin GUI

---

## 📋 Configuración en EasyPanel

### 1. Variables de Entorno Requeridas

En EasyPanel, configura estas variables de entorno:

```bash
# Credenciales del Broker
EXNOVA_EMAIL=tu@email.com
EXNOVA_PASSWORD=tupassword

# Configuración del Broker
BROKER_NAME=exnova
ACCOUNT_TYPE=PRACTICE

# AI/LLM (Opcional pero recomendado)
GROQ_API_KEY=tu_groq_api_key
USE_LLM=True
USE_GROQ=True

# Modo Headless
HEADLESS_MODE=True
```

### 2. Configuración del Proyecto

#### A. Crear Nuevo Proyecto
1. Ve a EasyPanel
2. Crea nuevo proyecto: `exnova-trader`
3. Selecciona "Git Repository"
4. URL: `https://github.com/daveymena/bot-reversiones-iq.git`
5. Branch: `main`

#### B. Configurar Build
- **Build Method**: Dockerfile
- **Dockerfile Path**: `Dockerfile` (en la raíz)
- **Build Context**: `.` (raíz del proyecto)

#### C. Configurar Volúmenes (Persistencia)

Crea estos volúmenes para persistir datos:

```yaml
/app/data -> data-volume
/app/models -> models-volume
/app/logs -> logs-volume
```

#### D. Health Check

EasyPanel detectará automáticamente el HEALTHCHECK del Dockerfile:

```dockerfile
HEALTHCHECK --interval=60s --timeout=10s --start-period=30s --retries=3
```

### 3. Deployment

1. **Push a GitHub**:
```bash
git add .
git commit -m "🚀 Preparado para EasyPanel deployment"
git push origin main
```

2. **Deploy en EasyPanel**:
   - Click en "Deploy"
   - Espera a que el build termine
   - Verifica logs

---

## 🔍 Verificación Post-Deployment

### 1. Verificar Logs

En EasyPanel, ve a la sección de Logs y busca:

```
✅ Conectado exitosamente - MODO PRÁCTICA
🚀 Iniciando motor de trading...
🔍 Buscando oportunidades en mercado...
```

### 2. Verificar Health Check

El health check debe estar en estado "healthy":
- Intervalo: cada 60 segundos
- Timeout: 10 segundos
- Retries: 3

### 3. Verificar Persistencia

Los datos deben persistir en los volúmenes:
- `data/deep_lessons.json` - Lecciones aprendidas
- `data/experiences.json` - Experiencias de trading
- `models/rl_agent.zip` - Modelo RL entrenado

---

## 🐛 Troubleshooting

### Error: "No such file or directory: Dockerfile"

**Causa**: Espacio extra en la ruta del Dockerfile

**Solución**: 
1. Verifica que el Dockerfile esté en la raíz del proyecto
2. En EasyPanel, asegúrate de que "Dockerfile Path" sea exactamente: `Dockerfile`
3. No debe tener espacios antes o después

### Error: "Connection refused" al broker

**Causa**: Credenciales incorrectas o broker no disponible

**Solución**:
1. Verifica las variables de entorno en EasyPanel
2. Asegúrate de que `EXNOVA_EMAIL` y `EXNOVA_PASSWORD` sean correctos
3. Verifica que el broker esté disponible

### Error: "Module not found"

**Causa**: Dependencia faltante en `requirements_cloud.txt`

**Solución**:
1. Agrega la dependencia a `requirements_cloud.txt`
2. Haz commit y push
3. Redeploy en EasyPanel

### Bot se detiene después de un tiempo

**Causa**: Error no capturado o pérdida de conexión

**Solución**:
1. Verifica logs en EasyPanel
2. El bot tiene auto-restart configurado en `docker-compose.yml`
3. Verifica que `restart: unless-stopped` esté configurado

---

## 📊 Monitoreo

### Logs en Tiempo Real

En EasyPanel:
1. Ve a tu proyecto
2. Click en "Logs"
3. Verás el output en tiempo real

### Métricas a Monitorear

- ✅ Conexión al broker
- ✅ Operaciones ejecutadas
- ✅ Lecciones aprendidas
- ✅ Win rate
- ✅ Errores

### Logs Importantes

```bash
# Conexión exitosa
✅ Conectado exitosamente - MODO PRÁCTICA

# Operación ejecutada
🚀 [PRACTICE/DEMO] Ejecutando CALL en EURUSD-OTC

# Análisis de pérdida
🔬 ANÁLISIS PROFUNDO DE PÉRDIDA

# Análisis de ganancia
💎 ANÁLISIS DE OPTIMIZACIÓN (Operación Ganada)

# Lección aprendida
✅ Lección aprendida y guardada (Total: 15)
```

---

## 🔄 Actualización del Bot

### Proceso de Actualización

1. **Hacer cambios localmente**:
```bash
# Editar código
git add .
git commit -m "Descripción de cambios"
git push origin main
```

2. **Redeploy en EasyPanel**:
   - EasyPanel detectará el push automáticamente
   - O manualmente: Click en "Redeploy"

3. **Verificar**:
   - Revisa logs para confirmar que inició correctamente
   - Verifica que las lecciones previas se mantienen

---

## 💾 Backup de Datos

### Datos Importantes a Respaldar

1. **Lecciones Aprendidas**: `data/deep_lessons.json`
2. **Experiencias**: `data/experiences.json`
3. **Modelo RL**: `models/rl_agent.zip`

### Cómo Hacer Backup

En EasyPanel, los volúmenes persisten automáticamente. Para backup manual:

1. Descarga los archivos desde el volumen
2. O configura backup automático en EasyPanel

---

## 🎯 Configuración Recomendada

### Para Empezar (PRACTICE)

```bash
ACCOUNT_TYPE=PRACTICE
CAPITAL_PER_TRADE=1.0
MAX_MARTINGALE=0
```

### Para Producción (REAL)

```bash
ACCOUNT_TYPE=REAL
CAPITAL_PER_TRADE=5.0
MAX_MARTINGALE=2
```

⚠️ **IMPORTANTE**: Solo cambia a REAL después de validar en PRACTICE por al menos 1 semana.

---

## 📈 Métricas de Éxito

### Deployment Exitoso:
- ✅ Build completa sin errores
- ✅ Container en estado "running"
- ✅ Health check en estado "healthy"
- ✅ Logs muestran conexión exitosa
- ✅ Bot ejecuta operaciones

### Bot Funcionando Correctamente:
- ✅ Win rate: 65-70%
- ✅ Operaciones: 5-10/día
- ✅ Lecciones aprendidas: +5/día
- ✅ Sin errores críticos
- ✅ Uptime: >99%

---

## 🔗 Enlaces Útiles

- **Repositorio**: https://github.com/daveymena/bot-reversiones-iq.git
- **Documentación**: Ver archivos .md en el repo
- **EasyPanel Docs**: https://easypanel.io/docs

---

## 📞 Soporte

Si tienes problemas:

1. Revisa los logs en EasyPanel
2. Verifica las variables de entorno
3. Consulta la documentación en el repo
4. Revisa `CHECKLIST_DEPLOYMENT.md`

---

**Última actualización**: 4 de Abril, 2026
**Versión**: 4.0 - Deep Learning
**Estado**: ✅ LISTO PARA DEPLOYMENT
