# ⚡ INICIO RÁPIDO - Git y EasyPanel

## 🚀 En 5 Minutos: Subir a Git

```bash
# 1. Validar que todo está listo
python scripts/validate_deployment.py

# 2. Agregar cambios
git add .

# 3. Commit
git commit -m "Preparar bot para Git y EasyPanel - V5-PRODUCTION"

# 4. Push
git push origin main
```

**✅ Listo en Git**

---

## 🐳 En 15 Minutos: Desplegar en EasyPanel

### Paso 1: Crear Aplicación
1. Ir a https://easypanel.io
2. "Applications" → "Create New"
3. Nombre: `trading-bot-pro`
4. Tipo: Docker
5. Repository: Tu URL de Git
6. Branch: `main`
7. Dockerfile: `Dockerfile`

### Paso 2: Configurar Variables
En "Environment Variables", agregar:

```bash
BROKER_NAME=exnova
ACCOUNT_TYPE=PRACTICE
EXNOVA_EMAIL=tu@email.com
EXNOVA_PASSWORD=tupassword
CAPITAL_PER_TRADE=1
MAX_MARTINGALE=0
USE_LLM=True
USE_GROQ=False
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:1b
```

### Paso 3: Configurar Volúmenes
En "Volumes", crear:

| Contenedor | Host |
|-----------|------|
| `/app/data` | `/data/trading-bot` |
| `/app/models` | `/models/trading-bot` |
| `/app/logs` | `/logs/trading-bot` |

### Paso 4: Desplegar
1. Hacer clic en "Deploy"
2. Esperar 5-10 minutos
3. Ver logs para verificar

**✅ Listo en EasyPanel**

---

## 📊 Verificar que Funciona

### Ver Logs
```bash
# En EasyPanel
Applications → trading-bot-pro → Logs

# Debe aparecer:
# ✅ Bot iniciado correctamente
# Broker: exnova
# Tipo de cuenta: PRACTICE
```

### Ver Datos
```bash
# En EasyPanel
Files → /data/trading-bot/

# Debe haber:
# - experiences.json
# - deep_lessons.json
# - history.csv
```

---

## ⚠️ Importante

### Antes de Desplegar
- [ ] Verificar que `.env` no tiene credenciales reales
- [ ] Ejecutar `python scripts/validate_deployment.py`
- [ ] Revisar `docs/DEPLOYMENT_EASYPANEL.md`

### Después de Desplegar
- [ ] Monitorear logs durante 1 hora
- [ ] Verificar que el bot está operando
- [ ] Revisar operaciones en Exnova
- [ ] Validar en PRACTICE 1-2 semanas

---

## 🔄 Actualizar Bot

```bash
# 1. Hacer cambios locales
# 2. Commit y push
git add .
git commit -m "Actualizar bot"
git push origin main

# 3. En EasyPanel
# Applications → trading-bot-pro → Redeploy
```

---

## 🆘 Problemas

### Bot no inicia
1. Ver logs en EasyPanel
2. Verificar variables de entorno
3. Verificar credenciales de Exnova

### Conexión rechazada
1. Verificar EXNOVA_EMAIL y EXNOVA_PASSWORD
2. Verificar que la cuenta está activa
3. Probar credenciales localmente

### Ollama no disponible
1. Cambiar `USE_OLLAMA=false`
2. Usar Groq: `USE_GROQ=True`

---

## 📚 Documentación Completa

- `README.md` - Guía general
- `docs/DEPLOYMENT_EASYPANEL.md` - Deployment detallado
- `CHECKLIST_FINAL.md` - Validación completa
- `RESUMEN_PREPARACION.md` - Resumen de cambios

---

**¡Listo! El bot está preparado para Git y EasyPanel** ✅
