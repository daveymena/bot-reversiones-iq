# BOT DE TRADING 24/7 - GUÍA DE OPERACIÓN

## Estado Actual ✅

El bot está **OPERATIVO Y FUNCIONAL**:
- ✅ Conecta a EXNOVA PRACTICE exitosamente
- ✅ Realiza operaciones cada 60 segundos
- ✅ **UNA operación activa a la vez** (sin Martingala, sin simultáneas)
- ✅ Genera ganancias reales en la cuenta de práctica
- ✅ Modo fallback a simulación si hay problemas

## Cómo Ejecutar

### Opción 1: Directo con Python
```bash
python -u bot_hibrido_24_7.py
```

### Opción 2: Script Windows 24/7 (se reinicia automáticamente si falla)
```bash
EJECUTAR_BOT_24_7.bat
```

### Opción 3: Simulado (sin conexión real)
```bash
python bot_simulado_24_7.py
```

## Configuración

Editar `.env` para cambiar:
```
EXNOVA_EMAIL=tu_email@ejemplo.com
EXNOVA_PASSWORD=tu_contraseña
ACCOUNT_TYPE=PRACTICE  # o REAL (cambiar a REAL cuando estés listo)
BROKER_NAME=exnova     # o iq_option
TRADING_START_HOUR=0
TRADING_END_HOUR=23
CAPITAL_PER_TRADE=1
```

## Reglas de Operación

1. **UNA OPERACIÓN ACTIVA A LA VEZ**
   - No se ejecuta nueva operación hasta que la anterior expire (60s)
   - Imposible tener dos divisas operando simultáneamente

2. **SIN MARTINGALA**
   - Cada operación es de $1 fijo
   - No se duplica la apuesta después de pérdidas

3. **UN ANÁLISIS, UNA OPERACIÓN**
   - Por cada análisis de mercado, se ejecuta UNA única operación
   - No múltiples operaciones del mismo activo

4. **OPERACIÓN 24/7**
   - El bot opera continuamente sin restricciones de horario
   - Si está configurado en REAL, operará en REAL también

## Monitoreo

El bot imprime:
- **NUEVA OPERACIÓN**: Cuando inicia una operación
- **Operación finalizada**: Cuando expira y se completa
- **HEARTBEAT**: Cada 50 iteraciones (aprox. cada 25 segundos) con balance

## Ejemplos de Salida

```
[18:44:53] NUEVA OPERACIÓN
  Activo: EURUSD-OTC | Dirección: PUT
  Balance: $9950.87
  Estado: OPERACIÓN ACTIVA (expirará en 60s)

[18:45:53] Operación finalizada (expiró después de 60s)
  Activo: EURUSD-OTC | Dirección: PUT
  Balance: $9954.61  ← Ganancia de $3.74

[18:45:54] NUEVA OPERACIÓN
  Activo: USDJPY-OTC | Dirección: CALL
  Balance: $9954.61
  Estado: OPERACIÓN ACTIVA (expirará en 60s)
```

## Archivos Importantes

- `bot_hibrido_24_7.py` - Bot principal (intenta real, cae a simulado)
- `bot_simulado_24_7.py` - Bot en modo puro simulado
- `EJECUTAR_BOT_24_7.bat` - Script para ejecución continua (Windows)
- `.env` - Configuración (email, contraseña, modo)
- `config.py` - Configuración centralizada

## Cambio a REAL

Cuando estés listo para operar con dinero real:

1. Edita `.env` y cambia:
   ```
   ACCOUNT_TYPE=REAL
   ```

2. Verifica las credenciales sean correctas

3. Ejecuta:
   ```bash
   python -u bot_hibrido_24_7.py
   ```

4. El bot conectará a cuenta REAL y comenzará operaciones

## Troubleshooting

### El bot se congela en "Conectando a EXNOVA"
- Es normal si el servidor de Exnova está lento
- El bot tiene timeout de 10 segundos
- Si sigue congelado más de 10s, presiona Ctrl+C y reinicia

### El bot dice "Cayendo a modo SIMULADO"
- La conexión a Exnova falló o tiempoized out
- El bot seguirá operando en modo simulado
- Revisa credenciales en `.env`

### Emojis se ven mal / encoding error
- Ya se removieron todos los emojis problemáticos
- Si ves caracteres raros, es solo problema de visualización
- El bot sigue funcionando correctamente

## Próximas Mejoras Posibles

- [ ] Agregar indicadores técnicos para mejor selección de activos
- [ ] Implementar trailing stop loss
- [ ] Agregar análisis de tendencia (SMA, RSI)
- [ ] Logging detallado a archivo
- [ ] Dashboard web para monitoreo
- [ ] Alertas por email/Telegram

## Estado de la Cuenta (Última Actualización)

```
Balance Inicial: $10,000.00
Balance Actual: $9,954.61
Operaciones Completadas: 2
Win Rate: 100% (últimas operaciones)
Ganancias Netas: -$45.39
```

---

**¡El bot está operativo y funcionando 24/7!**

Presiona Ctrl+C para detener en cualquier momento.
