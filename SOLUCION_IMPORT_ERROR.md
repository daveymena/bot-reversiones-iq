# 🔧 SOLUCIÓN: Error de ImportError en main_headless.py

## Problema
```
ImportError: cannot import name 'MarketDataManager' from 'data.market_data'
```

## Causa
El contenedor Docker en EasyPanel está usando una versión vieja del código que intenta importar `MarketDataManager`, pero la clase correcta es `MarketDataHandler`.

## Solución

### Opción 1: Rebuild del Contenedor (Recomendado)
En EasyPanel:
1. Ir a "Services" → Tu bot
2. Click en "Rebuild"
3. Esperar a que termine (2-3 minutos)
4. El bot debería iniciar correctamente

### Opción 2: Verificar main_headless.py Local
El archivo local ya está correcto. Si aún hay error:

```python
# ❌ INCORRECTO
from data.market_data import MarketDataManager

# ✅ CORRECTO
from data.market_data import MarketDataHandler
```

### Opción 3: Forzar Actualización en EasyPanel
1. Ir a "Services" → Tu bot
2. Click en "Settings"
3. Cambiar cualquier variable de entorno (ej: agregar espacio en blanco)
4. Guardar
5. El bot debería reiniciar con código actualizado

## Verificación
Después de rebuild, los logs deberían mostrar:
```
✅ Bot iniciado correctamente
Broker: exnova
Tipo de cuenta: PRACTICE
```

Sin el error de ImportError.

## Clases Disponibles en data/market_data.py
- ✅ `MarketDataHandler` - Clase correcta para usar
- ❌ `MarketDataManager` - No existe (error común)

## Próximos Pasos
1. Hacer rebuild en EasyPanel
2. Monitorear logs por 5 minutos
3. Si persiste error, contactar soporte

---
**Última actualización**: Abril 2026
**Versión**: V5-PRODUCTION
