# ⏰ Configuración de Horario de Operación

## Configuración Aplicada

### ✅ Cambios Realizados

1. **Monto por operación**: $1 (antes era $10)
2. **Martingala**: DESHABILITADA (MAX_MARTINGALE=0)
3. **Horario de operación**: 7:00 AM - 9:30 AM
4. **Verificación de volatilidad**: Entre 7:00-7:30 AM

## Archivos Modificados

### 1. `config.py`
```python
CAPITAL_PER_TRADE = 1  # $1 por operación
MAX_MARTINGALE = 0     # Sin martingala
TRADING_START_HOUR = 7      # 7:00 AM
TRADING_END_HOUR = 9        # 9:30 AM
TRADING_END_MINUTE = 30
MIN_VOLATILITY_TO_START = 0.05  # ATR mínimo para iniciar
```

### 2. `.env`
```bash
CAPITAL_PER_TRADE=1
MAX_MARTINGALE=0
```

### 3. `core/trader.py`
- Agregada verificación de horario en el bucle principal
- Verificación de volatilidad entre 7:00-7:30 AM
- Detención automática a las 9:30 AM

## Comportamiento del Bot

### 🌅 Antes de las 7:00 AM
- El bot espera y muestra mensaje cada minuto
- No realiza operaciones

### 🎯 Entre 7:00-7:30 AM
- Verifica volatilidad del mercado (ATR >= 0.05%)
- Si volatilidad es baja, espera 30 segundos y vuelve a verificar
- Una vez que la volatilidad es adecuada, inicia operaciones

### 📊 Entre 7:30-9:30 AM
- Opera normalmente
- Busca oportunidades cada 30 segundos
- Monto fijo de $1 por operación
- NO aplica martingala

### 🛑 A las 9:30 AM
- Detiene automáticamente el bot
- Muestra resumen de la sesión
- Cierra limpiamente

## Cómo Ejecutar

### Opción 1: Interfaz Gráfica (puede cerrarse sola)
```bash
python main_modern.py
```

### Opción 2: Modo Consola (MÁS ESTABLE - RECOMENDADO)
```bash
python main_console.py
```

O simplemente ejecuta:
```bash
EJECUTAR_BOT_CONSOLA.bat
```

## Ventajas del Modo Consola

✅ **Más estable** - No depende de Qt/PySide6
✅ **Menos recursos** - Consume menos memoria
✅ **Logs claros** - Todo en texto plano
✅ **No se cierra solo** - Más robusto ante errores
✅ **Fácil de monitorear** - Puedes redirigir a archivo

## Ejemplo de Logs

```
⏰ Esperando horario de inicio (7:00 AM). Faltan 15 minutos...
⏳ Volatilidad baja (ATR: 0.032%). Esperando mejores condiciones...
✅ Volatilidad adecuada (ATR: 0.051%). Iniciando operaciones...
💓 Bot activo - Iteración #120 - Balance: $1000.00
🔍 Escaneando oportunidades... (07:15:30)
💎 Oportunidad detectada:
   Asset: EURUSD-OTC
   Dirección: CALL
   Confianza: 72.5%
🚀 Ejecutando CALL en EURUSD-OTC
   Monto: $1.00
   Expiración: 3 min
✅ Operación ejecutada - ID: 13359690680
⏳ Cooldown: 2 minutos antes de la próxima operación
📊 Verificando resultado de operación 13359690680...
✅ GANADA: +$0.85
💰 Balance actual: $1000.85
⏰ Horario de operación finalizado (9:30 AM)
✅ Sesión completada. Deteniendo bot...
```

## Resumen de Seguridad

🔒 **Protecciones Activas:**
- Monto fijo de $1 (no puede aumentar)
- Sin martingala (no duplica apuestas)
- Horario limitado (2.5 horas máximo)
- Verificación de volatilidad
- Cooldown entre operaciones
- Detención automática

## Notas Importantes

⚠️ **IMPORTANTE**: 
- El bot está configurado para operar en cuenta REAL
- Verifica tu balance antes de iniciar
- El horario es en hora local de tu sistema
- Si quieres cambiar el horario, edita `.env`:
  ```bash
  TRADING_START_HOUR=7
  TRADING_END_HOUR=9
  TRADING_END_MINUTE=30
  ```

## Solución al Problema de Cierre

El problema de que la interfaz se cerraba después de la operación de $10 probablemente fue por:
1. Error en la GUI de Qt/PySide6
2. Consumo excesivo de memoria
3. Conflicto en el manejo de threads

**Solución**: Usar el modo consola que es más estable y no tiene estos problemas.
