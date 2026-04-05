# 🚀 INSTRUCCIONES PARA ARREGLAR EL BOT EN EASYPANEL

## ⚠️ Error Actual
```
ImportError: cannot import name 'MarketDataManager' from 'data.market_data'
```

## ✅ SOLUCIÓN RÁPIDA (2 minutos)

### Paso 1: Ir a EasyPanel
1. Abre https://easypanel.io
2. Inicia sesión
3. Selecciona tu servidor

### Paso 2: Rebuild del Contenedor
1. Busca tu servicio del bot (ej: "trading-bot")
2. Click en el servicio
3. Click en el botón **"Rebuild"** (esquina superior derecha)
4. Espera a que termine (verás "Build completed")

### Paso 3: Verificar Logs
1. Después del rebuild, click en **"Logs"**
2. Deberías ver:
   ```
   ✅ Bot iniciado correctamente
   Broker: exnova
   Tipo de cuenta: PRACTICE
   ```

### Paso 4: Confirmar Funcionamiento
- Si ves el mensaje anterior = ✅ **FUNCIONANDO**
- Si ves el error de ImportError = Ir a "Opción B"

---

## 🔄 OPCIÓN B: Si el Rebuild No Funciona

### Forzar Actualización Manual
1. En EasyPanel, ir a tu servicio
2. Click en **"Settings"**
3. Buscar **"Environment Variables"**
4. Agregar una variable nueva:
   ```
   FORCE_UPDATE=true
   ```
5. Click en **"Save"**
6. El servicio debería reiniciar automáticamente
7. Esperar 30 segundos y verificar logs

---

## 🛠️ OPCIÓN C: Verificar Código Local

Si tienes acceso a la máquina local:

```bash
# Verificar que main_headless.py está correcto
grep "MarketDataHandler" main_headless.py

# Debería mostrar algo como:
# from data.market_data import MarketDataHandler
```

Si muestra `MarketDataManager`, necesitas actualizar el archivo.

---

## 📊 CHECKLIST DE VERIFICACIÓN

Después de cualquier fix, verificar en logs:

- [ ] ✅ Bot iniciado correctamente
- [ ] ✅ Broker: exnova
- [ ] ✅ Tipo de cuenta: PRACTICE
- [ ] ✅ Monto por operación: 1
- [ ] ✅ IA/LLM: Activada (o Desactivada)
- [ ] ✅ Sin errores de ImportError
- [ ] ✅ Sin errores de conexión

---

## 🆘 Si Aún No Funciona

### Verificar Dockerfile
El Dockerfile debe tener:
```dockerfile
CMD ["python", "main_headless.py"]
```

### Verificar requirements_cloud.txt
Debe incluir todas las dependencias necesarias.

### Última Opción: Redeploy Completo
1. En EasyPanel, eliminar el servicio
2. Crear nuevo servicio desde cero
3. Usar el Dockerfile del repositorio

---

## 📝 NOTAS IMPORTANTES

- El rebuild toma 2-3 minutos
- Los logs se actualizan en tiempo real
- El bot se reinicia automáticamente después del rebuild
- No perderás datos (están en `data/` y `models/`)

---

**Última actualización**: Abril 2026
**Versión**: V5-PRODUCTION
**Estado**: ✅ Listo para producción
