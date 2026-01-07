# ✅ Cómo Ejecutar el Backend Correctamente

## ❌ Error Actual

```
ModuleNotFoundError: No module named 'data'
```

Este error ocurre porque el backend se está ejecutando desde el directorio `backend/` en lugar de la raíz del proyecto.

## ✅ Solución

### Opción 1: Usar el Script Automático (Recomendado)

Detén el backend actual (Ctrl+C) y ejecuta:

```bash
# Windows
start_web.bat

# Linux/Mac
./start_web.sh
```

Este script ejecuta automáticamente el backend desde la raíz del proyecto.

### Opción 2: Ejecutar Manualmente

**IMPORTANTE**: Ejecuta desde la **RAÍZ del proyecto** (donde está el archivo `.env`):

```bash
# ✅ CORRECTO - Desde la raíz del proyecto
python -m uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000

# ❌ INCORRECTO - NO hagas esto
cd backend
python -m uvicorn api.main:app --reload
```

## 🔍 Verificar que Estás en la Raíz

Antes de ejecutar, verifica que estás en el directorio correcto:

```bash
# Windows
dir

# Linux/Mac
ls
```

Debes ver estos directorios:
- ✅ `backend/`
- ✅ `core/`
- ✅ `data/`
- ✅ `frontend-web/`
- ✅ `strategies/`
- ✅ `.env`

## ✅ Verificación de Éxito

Si el backend inicia correctamente, verás:

```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

Luego puedes acceder a:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs

## 🐛 Si el Error Persiste

1. **Detén todos los procesos de uvicorn**:
   ```bash
   # Windows
   taskkill /F /IM python.exe
   
   # Linux/Mac
   pkill -f uvicorn
   ```

2. **Verifica que estás en la raíz**:
   ```bash
   pwd  # Linux/Mac
   cd   # Windows
   ```

3. **Ejecuta el comando correcto**:
   ```bash
   python -m uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000
   ```

## 📝 Resumen

- ✅ Ejecutar desde la **raíz del proyecto**
- ✅ Usar `backend.api.main:app` (con puntos)
- ❌ NO ejecutar desde `backend/`
- ❌ NO usar `api.main:app` (sin backend.)

---

**¡Ahora el backend debería funcionar correctamente! 🚀**
