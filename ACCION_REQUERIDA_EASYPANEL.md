# 🎯 ACCIÓN REQUERIDA EN EASYPANEL

## ⚠️ Tu Bot Está Mostrando Este Error

```
ImportError: cannot import name 'MarketDataManager' from 'data.market_data'
```

## ✅ SOLUCIÓN (Toma 2 minutos)

### PASO 1: Abre EasyPanel
- URL: https://easypanel.io
- Inicia sesión con tus credenciales

### PASO 2: Busca Tu Servicio del Bot
- En el dashboard, busca tu servicio (ej: "trading-bot", "bot-reversiones", etc.)
- Click en el servicio

### PASO 3: Haz Rebuild del Contenedor
- Busca el botón **"Rebuild"** (generalmente en la esquina superior derecha)
- Click en "Rebuild"
- Espera a que termine (verás "Build completed" o similar)
- Esto toma 2-3 minutos

### PASO 4: Verifica los Logs
- Después del rebuild, click en **"Logs"**
- Deberías ver algo como:
  ```
  ✅ Bot iniciado correctamente
  Broker: exnova
  Tipo de cuenta: PRACTICE
  Monto por operación: 1
  IA/LLM: Activada
  ```

### PASO 5: Confirma que Funciona
- Si ves el mensaje anterior = ✅ **LISTO**
- Si ves el error de ImportError = Ir a "OPCIÓN B"

---

## 🔄 OPCIÓN B: Si el Rebuild No Funciona

### Forzar Actualización Manual
1. En EasyPanel, ir a tu servicio
2. Click en **"Settings"**
3. Buscar **"Environment Variables"**
4. Agregar esta variable:
   ```
   FORCE_UPDATE=true
   ```
5. Click en **"Save"**
6. El servicio debería reiniciar automáticamente
7. Esperar 30 segundos y verificar logs

---

## 📝 ¿QUÉ PASÓ?

El código en GitHub fue actualizado, pero tu contenedor Docker en EasyPanel estaba usando la versión vieja. El rebuild descarga el código nuevo y lo compila.

---

## 🆘 SOPORTE

Si después de hacer rebuild aún ves el error:

1. Verifica que estés en la rama `main` de GitHub
2. Intenta la "OPCIÓN B" (Forzar Actualización)
3. Si persiste, contacta al equipo de desarrollo

---

## ✨ DESPUÉS DE ARREGLARLO

El bot debería:
- ✅ Conectarse a Exnova automáticamente
- ✅ Analizar el mercado cada minuto
- ✅ Ejecutar operaciones según la estrategia
- ✅ Guardar experiencias para aprendizaje
- ✅ Mostrar logs en tiempo real

---

**Acción requerida**: Hacer Rebuild en EasyPanel
**Tiempo estimado**: 2-3 minutos
**Dificultad**: Muy fácil (solo 1 click)

¡Hazlo ahora! 🚀
