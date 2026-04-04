# 🚀 Instrucciones para EasyPanel - SOLUCIÓN AL ERROR

## ❌ Problema Actual

EasyPanel está agregando un espacio extra en la ruta del Dockerfile:
```
'/etc/easypanel/projects/ollama/exnova-trader/code/Dockerfile '
                                                              ↑ espacio aquí
```

---

## ✅ SOLUCIÓN RÁPIDA (3 opciones)

### Opción 1: Usar dockerfile.build (MÁS FÁCIL) ⭐

1. **En EasyPanel, ve a Settings → Build**
2. **Cambia "Dockerfile Path" a**:
   ```
   dockerfile.build
   ```
3. **Guarda y redeploy**

✅ Este archivo ya está en el repositorio y es idéntico al Dockerfile original.

---

### Opción 2: Corregir configuración de Dockerfile

1. **En EasyPanel, ve a Settings → Build**
2. **Asegúrate de que "Dockerfile Path" sea EXACTAMENTE**:
   ```
   Dockerfile
   ```
   **SIN espacios antes o después**
3. **Verifica que "Build Context" sea**:
   ```
   .
   ```
4. **Guarda y redeploy**

---

### Opción 3: Usar Docker Compose

1. **En EasyPanel, cambia el método de build a "Docker Compose"**
2. **El archivo `docker-compose.yml` ya está configurado**
3. **Deploy**

---

## 📋 Configuración Completa en EasyPanel

### 1. Información del Proyecto

```
Nombre: exnova-trader
Repositorio: https://github.com/daveymena/bot-reversiones-iq.git
Branch: main
```

### 2. Build Configuration

**Si usas Opción 1 (dockerfile.build)**:
```
Build Method: Dockerfile
Dockerfile Path: dockerfile.build
Build Context: .
```

**Si usas Opción 2 (Dockerfile)**:
```
Build Method: Dockerfile
Dockerfile Path: Dockerfile
Build Context: .
```

**Si usas Opción 3 (Docker Compose)**:
```
Build Method: Docker Compose
Compose File: docker-compose.yml
```

### 3. Variables de Entorno (REQUERIDAS)

```bash
EXNOVA_EMAIL=tu@email.com
EXNOVA_PASSWORD=tupassword
BROKER_NAME=exnova
ACCOUNT_TYPE=PRACTICE
GROQ_API_KEY=tu_groq_api_key
USE_LLM=True
USE_GROQ=True
HEADLESS_MODE=True
```

### 4. Volúmenes (REQUERIDOS para persistencia)

Crear estos 3 volúmenes:

```
Nombre: data
Path: /app/data

Nombre: models
Path: /app/models

Nombre: logs
Path: /app/logs
```

### 5. Health Check

El health check está configurado automáticamente en el Dockerfile:
```
Intervalo: 60s
Timeout: 10s
Retries: 3
```

---

## 🧪 Verificar que Funciona

Después de deployar, verifica los logs. Deberías ver:

```
🤖 BOT DE TRADING EXNOVA - MODO CONSOLA AVANZADO
📅 Inicio: 2026-04-04 14:30:00
🏦 Broker: Exnova / IQ Option
💰 Capital: $1.0

🧠 Cargando módulos de IA...
📊 Cargando gestores de datos...
🛡️ Inicializando gestores de riesgo...

🔌 Conectando a Exnova como tu@email.com...
✅ Conectado exitosamente - MODO PRÁCTICA

🚀 Iniciando motor de trading...
🔍 Buscando oportunidades en mercado...
```

---

## ⚠️ Troubleshooting

### Error: "Connection refused"
**Causa**: Credenciales incorrectas
**Solución**: Verifica `EXNOVA_EMAIL` y `EXNOVA_PASSWORD`

### Error: "Module not found"
**Causa**: Dependencia faltante
**Solución**: Verifica que `requirements_cloud.txt` esté completo

### Bot se detiene
**Causa**: Error no capturado
**Solución**: 
1. Revisa logs completos
2. El bot tiene auto-restart configurado
3. Verifica que `restart: unless-stopped` esté en docker-compose

### Health check falla
**Causa**: Bot no está creando el flag file
**Solución**: 
1. Verifica que el directorio `/app/data` existe
2. Verifica permisos de escritura
3. El health check tiene 30s de start-period

---

## 📊 Monitoreo

### Logs Importantes a Buscar:

✅ **Conexión exitosa**:
```
✅ Conectado exitosamente - MODO PRÁCTICA
```

✅ **Operación ejecutada**:
```
🚀 [PRACTICE/DEMO] Ejecutando CALL en EURUSD-OTC
```

✅ **Análisis de pérdida**:
```
🔬 ANÁLISIS PROFUNDO DE PÉRDIDA
```

✅ **Análisis de ganancia**:
```
💎 ANÁLISIS DE OPTIMIZACIÓN (Operación Ganada)
```

✅ **Lección aprendida**:
```
✅ Lección aprendida y guardada (Total: 15)
```

---

## 🎯 Checklist Final

Antes de deployar, verifica:

- [ ] Repositorio conectado: `https://github.com/daveymena/bot-reversiones-iq.git`
- [ ] Branch: `main`
- [ ] Build Method configurado (Opción 1, 2 o 3)
- [ ] Variables de entorno configuradas (7 variables)
- [ ] Volúmenes creados (3 volúmenes)
- [ ] Health check habilitado

Después de deployar, verifica:

- [ ] Build completa sin errores
- [ ] Container en estado "running"
- [ ] Health check en estado "healthy"
- [ ] Logs muestran conexión exitosa
- [ ] Bot ejecuta operaciones

---

## 🔗 Recursos

- **Repositorio**: https://github.com/daveymena/bot-reversiones-iq.git
- **Documentación completa**: Ver `DEPLOYMENT_EASYPANEL.md`
- **Solución de errores**: Ver `SOLUCION_ERROR_DOCKERFILE.md`
- **Resumen final**: Ver `RESUMEN_FINAL.md`

---

## 📞 Siguiente Paso

1. **Elige una de las 3 opciones** (recomiendo Opción 1: dockerfile.build)
2. **Configura en EasyPanel** según las instrucciones arriba
3. **Deploy**
4. **Verifica logs**
5. **¡Listo!** El bot empezará a operar y aprender

---

**Última actualización**: 4 de Abril, 2026
**Commit actual**: `2063a17`
**Estado**: ✅ LISTO CON SOLUCIONES ALTERNATIVAS
