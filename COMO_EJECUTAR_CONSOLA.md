# Cómo Ejecutar el Bot en Modo Consola

## Descripción

La versión consola (`main_console.py`) es una versión simplificada del bot que **NO usa interfaz gráfica**. Esto evita problemas de cierre inesperado relacionados con Qt/PySide6.

## Ventajas de la Versión Consola

✅ **Más estable**: No depende de Qt/PySide6
✅ **Menos recursos**: Consume menos memoria y CPU
✅ **Ideal para servidores**: Perfecto para ejecutar en VPS/Cloud
✅ **Logs claros**: Toda la información en consola
✅ **No se cierra inesperadamente**: Sin problemas de GUI

## Cómo Ejecutar

### Opción 1: Usando el archivo .bat (Windows)

```bash
start_console.bat
```

### Opción 2: Directamente con Python

```bash
python main_console.py
```

### Opción 3: En Linux/Mac

```bash
chmod +x main_console.py
./main_console.py
```

## Detener el Bot

Para detener el bot de forma segura:

1. Presiona `Ctrl+C` en la consola
2. El bot cerrará limpiamente y mostrará un resumen

## Qué Hace el Bot en Modo Consola

1. **Conecta al broker** (Exnova o IQ Option)
2. **Verifica activos disponibles**
3. **Escanea oportunidades** cada 30 segundos
4. **Ejecuta operaciones** cuando detecta señales
5. **Monitorea resultados** automáticamente
6. **Muestra logs** en tiempo real
7. **Actualiza balance** después de cada operación

## Ejemplo de Salida

```
============================================================
TRADING BOT PRO - AI POWERED (CONSOLA)
============================================================
Fecha: 2024-01-27 14:30:00
Broker: EXNOVA
Modo: REAL
============================================================

📦 Inicializando componentes...
✅ Modelo RL cargado
✅ Cliente LLM inicializado
✅ Componentes inicializados

🔌 Conectando a EXNOVA...
✅ Conectado a EXNOVA

💰 Balance inicial: $100.00

🔍 Verificando activos disponibles...
   ✅ EURUSD-OTC
   ✅ GBPUSD-OTC
   ✅ USDJPY-OTC

✅ 3 activos disponibles

============================================================
🚀 INICIANDO BOT DE TRADING
============================================================
Presiona Ctrl+C para detener

🔍 Escaneando oportunidades... (14:30:15)

💎 Oportunidad detectada:
   Asset: EURUSD-OTC
   Dirección: CALL
   Confianza: 75.5%

🚀 Ejecutando CALL en EURUSD-OTC
   Monto: $1.00
   Expiración: 3 min
✅ Operación ejecutada - ID: 12345678
⏳ Cooldown: 2 minutos antes de la próxima operación

💓 Bot activo - Iteración #30 - Balance: $100.00

📊 Verificando resultado de operación 12345678...
✅ GANADA: +$0.85
💰 Balance actual: $100.85

🔍 Escaneando oportunidades... (14:35:20)
⏳ No hay oportunidades claras, esperando...
```

## Configuración

El bot usa la misma configuración que la versión GUI:

- **Archivo**: `.env`
- **Broker**: `BROKER_NAME=exnova` o `iq`
- **Modo**: `ACCOUNT_TYPE=PRACTICE` o `REAL`
- **Credenciales**: `EXNOVA_EMAIL`, `EXNOVA_PASSWORD`, etc.

## Logs y Debugging

Todos los logs se muestran en la consola en tiempo real:

- `✅` = Éxito
- `❌` = Error
- `⚠️` = Advertencia
- `💎` = Oportunidad detectada
- `🚀` = Operación ejecutada
- `📊` = Verificando resultado
- `💓` = Heartbeat (bot activo)

## Diferencias con la Versión GUI

| Característica | GUI | Consola |
|----------------|-----|---------|
| Interfaz gráfica | ✅ | ❌ |
| Gráficos en tiempo real | ✅ | ❌ |
| Logs en consola | ⚠️ | ✅ |
| Estabilidad | ⚠️ | ✅ |
| Uso de recursos | Alto | Bajo |
| Ideal para servidor | ❌ | ✅ |
| Funcionalidad de trading | ✅ | ✅ |

## Ejecutar en Segundo Plano (Linux/Mac)

Para ejecutar el bot en segundo plano:

```bash
nohup python main_console.py > bot.log 2>&1 &
```

Ver logs en tiempo real:
```bash
tail -f bot.log
```

Detener el bot:
```bash
pkill -f main_console.py
```

## Ejecutar en Segundo Plano (Windows)

Usar `pythonw` para ejecutar sin ventana:

```bash
pythonw main_console.py
```

O crear un servicio de Windows con `nssm`:

```bash
nssm install TradingBot "C:\Python\python.exe" "C:\trading\main_console.py"
nssm start TradingBot
```

## Monitoreo Remoto

Para monitorear el bot remotamente:

1. **SSH**: Conectar por SSH y ver logs
2. **Screen/Tmux**: Usar sesiones persistentes
3. **Logs a archivo**: Redirigir salida a archivo

Ejemplo con screen:
```bash
screen -S trading_bot
python main_console.py
# Presionar Ctrl+A, luego D para desconectar
# Reconectar con: screen -r trading_bot
```

## Troubleshooting

### El bot no se conecta

1. Verificar credenciales en `.env`
2. Verificar conexión a internet
3. Verificar que el broker esté disponible

### No detecta oportunidades

1. Verificar que los activos estén abiertos
2. Ajustar `MIN_CONFIDENCE` en `config.py`
3. Verificar que el modelo RL esté entrenado

### El bot se cierra inesperadamente

1. Revisar logs para ver el error
2. Verificar que todas las dependencias estén instaladas
3. Ejecutar con `python -u main_console.py` para logs sin buffer

## Recomendaciones

✅ **Usar en PRACTICE primero** para validar funcionamiento
✅ **Monitorear los primeros días** para ajustar parámetros
✅ **Guardar logs** para análisis posterior
✅ **Configurar alertas** (email, Telegram, etc.)
✅ **Hacer backups** de la configuración

## Próximos Pasos

Una vez que el bot funcione correctamente en consola:

1. Ejecutar en servidor/VPS para operación 24/7
2. Configurar monitoreo automático
3. Implementar notificaciones
4. Optimizar parámetros basado en resultados

## Soporte

Si tienes problemas:

1. Revisar logs en consola
2. Verificar configuración en `.env`
3. Consultar documentación técnica
4. Revisar issues en GitHub
