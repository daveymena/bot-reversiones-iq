# 🔧 Solución: Error "no such file or directory: Dockerfile"

## ❌ Error Completo

```
ERROR: failed to build: failed to solve: failed to read dockerfile: 
open Dockerfile : no such file or directory

Command failed with exit code 1: docker buildx build --network host 
-f '/etc/easypanel/projects/ollama/exnova-trader/code/Dockerfile ' 
-t easypanel/ollama/exnova-trader --label 'keep=true' --no-cache 
--build-arg 'GIT_SHA=50d848000ff99c684ad1b3eb115f8c9fa62974f4' 
/etc/easypanel/projects/ollama/exnova-trader/code/
```

## 🔍 Causa del Problema

Nota el **espacio extra** en la ruta:
```
'/etc/easypanel/projects/ollama/exnova-trader/code/Dockerfile '
                                                              ↑
                                                        Espacio aquí
```

Este espacio hace que Docker busque un archivo llamado `Dockerfile ` (con espacio) en lugar de `Dockerfile`.

---

## ✅ Soluciones

### Solución 1: Configurar Correctamente en EasyPanel (RECOMENDADO)

1. **Ve a tu proyecto en EasyPanel**
2. **Click en "Settings" o "Configuration"**
3. **Busca la sección "Build"**
4. **En "Dockerfile Path", asegúrate de que sea EXACTAMENTE**:
   ```
   Dockerfile
   ```
   **SIN espacios antes o después**

5. **Verifica también "Build Context"**:
   ```
   .
   ```
   (Un punto, sin espacios)

6. **Guarda y redeploy**

---

### Solución 2: Usar docker-compose.yml

Si EasyPanel soporta docker-compose:

1. **En EasyPanel, selecciona "Docker Compose" en lugar de "Dockerfile"**
2. **El archivo `docker-compose.yml` ya está configurado correctamente**
3. **Deploy**

---

### Solución 3: Renombrar Dockerfile (Workaround)

Si las soluciones anteriores no funcionan:

1. **Crear un Dockerfile sin espacios en el nombre**:
   ```bash
   # En tu máquina local
   cp Dockerfile dockerfile.build
   git add dockerfile.build
   git commit -m "Add dockerfile.build como workaround"
   git push origin main
   ```

2. **En EasyPanel, configurar**:
   ```
   Dockerfile Path: dockerfile.build
   ```

---

### Solución 4: Verificar Configuración de EasyPanel

#### A. Verificar Variables de Entorno

Asegúrate de que estas variables estén configuradas:

```bash
EXNOVA_EMAIL=tu@email.com
EXNOVA_PASSWORD=tupassword
BROKER_NAME=exnova
ACCOUNT_TYPE=PRACTICE
GROQ_API_KEY=tu_groq_key
USE_LLM=True
HEADLESS_MODE=True
```

#### B. Verificar Configuración de Build

En EasyPanel:
- **Build Method**: Dockerfile
- **Dockerfile Path**: `Dockerfile` (sin espacios)
- **Build Context**: `.` (punto)
- **Build Args**: (vacío o según necesites)

#### C. Verificar Repositorio

- **Repository URL**: `https://github.com/daveymena/bot-reversiones-iq.git`
- **Branch**: `main`
- **Auto Deploy**: Activado (opcional)

---

## 🧪 Verificar Localmente

Antes de deployar, verifica que el Dockerfile funciona localmente:

```bash
# Build local
docker build -t trading-bot-test .

# Si funciona, el problema es de configuración en EasyPanel
```

---

## 📋 Checklist de Verificación

- [ ] Dockerfile existe en la raíz del proyecto
- [ ] Dockerfile Path en EasyPanel es exactamente: `Dockerfile`
- [ ] Build Context en EasyPanel es: `.`
- [ ] No hay espacios extra en la configuración
- [ ] Variables de entorno están configuradas
- [ ] Repositorio está conectado correctamente
- [ ] Branch es `main`

---

## 🔄 Alternativa: Usar GitHub Actions

Si EasyPanel sigue dando problemas, puedes usar GitHub Actions para build y push a un registry:

### 1. Crear `.github/workflows/deploy.yml`:

```yaml
name: Build and Deploy

on:
  push:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Docker image
        run: docker build -t trading-bot .
      
      - name: Push to registry
        run: |
          echo "Build exitoso"
          # Aquí puedes agregar push a Docker Hub o GitHub Container Registry
```

### 2. Luego en EasyPanel:
- Usar imagen pre-construida en lugar de build desde Dockerfile

---

## 💡 Recomendación Final

**La solución más simple**: 

1. Ve a EasyPanel
2. Settings → Build Configuration
3. Asegúrate de que "Dockerfile Path" sea: `Dockerfile` (sin espacios)
4. Guarda
5. Redeploy

Si el problema persiste, contacta al soporte de EasyPanel mostrándoles el error del espacio extra en la ruta.

---

## 📞 Soporte Adicional

Si ninguna solución funciona:

1. **Verifica la documentación de EasyPanel**: https://easypanel.io/docs
2. **Contacta soporte de EasyPanel**: Muéstrales el error del espacio extra
3. **Alternativa**: Usa otro servicio como Railway, Render, o DigitalOcean App Platform

---

## ✅ Archivos Creados para Ayudar

- `.easypanel` - Configuración explícita para EasyPanel
- `docker-compose.yml` - Alternativa usando compose
- Este archivo - Guía de solución

---

**Última actualización**: 4 de Abril, 2026
**Estado**: Esperando corrección en EasyPanel
