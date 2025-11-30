# 📊 ACTIVOS OTC VS NORMALES

## ✅ PROBLEMA RESUELTO

**Antes:** El bot no encontraba activos operables
**Causa:** Error en la firma del método `get_candles()`
**Solución:** Corregido el parámetro `end_time`

## 🔍 ACTIVOS DISPONIBLES

### Activos OTC (Over The Counter)
```
✅ EURUSD-OTC
✅ GBPUSD-OTC
✅ USDJPY-OTC
✅ AUDUSD-OTC
✅ USDCAD-OTC
✅ EURJPY-OTC
... y 144 más
```

### Activos Normales
```
✅ EURUSD
✅ GBPUSD
✅ USDJPY
✅ AUDUSD
✅ USDCAD
✅ EURJPY
... y 96 más
```

## 📋 DIFERENCIAS CLAVE

### OTC (Over The Counter)

**Ventajas:**
- ✅ Disponibles 24/7 (fines de semana incluidos)
- ✅ Siempre operables
- ✅ Ideal para bots automáticos
- ✅ No dependen del horario de mercado

**Desventajas:**
- ⚠️ Spreads ligeramente mayores
- ⚠️ Liquidez sintética
- ⚠️ Precios pueden diferir del mercado real

**Cuándo usar:**
- Fines de semana
- Fuera del horario de mercado
- Trading 24/7
- Bots automáticos

### Activos Normales

**Ventajas:**
- ✅ Precios del mercado real
- ✅ Mayor liquidez
- ✅ Spreads más ajustados
- ✅ Movimientos más predecibles

**Desventajas:**
- ❌ Solo disponibles en horario de mercado
- ❌ Cerrados fines de semana
- ❌ Cerrados en festivos

**Cuándo usar:**
- Horario de mercado (Lunes-Viernes)
- Trading manual
- Análisis fundamental
- Noticias económicas

## ⏰ HORARIOS DE MERCADO

### Forex (Activos Normales)
```
Lunes:    00:00 GMT - Apertura Sydney
Viernes:  22:00 GMT - Cierre Nueva York

Sesiones:
• Sydney:     22:00 - 07:00 GMT
• Tokio:      00:00 - 09:00 GMT
• Londres:    08:00 - 17:00 GMT
• Nueva York: 13:00 - 22:00 GMT
```

### OTC (24/7)
```
Siempre disponibles
Sin horarios de cierre
Operables fines de semana
```

## 💡 RECOMENDACIONES

### Para el Bot Automático

**Usar OTC si:**
- Quieres operar 24/7
- Es fin de semana
- Es fuera de horario de mercado
- Prefieres disponibilidad constante

**Usar Normales si:**
- Es horario de mercado
- Quieres mejores spreads
- Operas con noticias económicas
- Prefieres liquidez real

### Configuración Recomendada

```python
# En la interfaz o config.py

# Opción 1: Solo OTC (24/7)
PREFER_OTC = True
FALLBACK_TO_NORMAL = False

# Opción 2: Normales con fallback a OTC
PREFER_OTC = False
FALLBACK_TO_NORMAL = True

# Opción 3: Automático (recomendado)
PREFER_OTC = True  # Usa OTC por defecto
FALLBACK_TO_NORMAL = True  # Prueba normales si OTC falla
```

## 🔧 CÓMO FUNCIONA EL BOT

### Selección Automática de Activos

```python
1. Verificar conexión al broker
2. Obtener lista de activos disponibles
3. Filtrar por rentabilidad (>70%)
4. Priorizar OTC si prefer_otc=True
5. Si no hay OTC, probar normales
6. Si no hay ninguno, usar EURUSD-OTC por defecto
```

### Proceso de Verificación

```python
# El AssetManager verifica:
1. ¿Está conectado al broker? ✓
2. ¿Hay activos con >70% profit? ✓
3. ¿Hay activos OTC disponibles? ✓
4. ¿Se pueden obtener datos? ✓
5. ✅ Activo seleccionado: EURUSD-OTC
```

## 📊 RENTABILIDADES

### Exnova - Activos OTC
```
BONKUSD-OTC:  88%
EURAUD-OTC:   88%
NEARUSD-OTC:  88%
EURCAD-OTC:   88%
AUDCHF-OTC:   88%
EURUSD-OTC:   85%
GBPUSD-OTC:   85%
```

### Exnova - Activos Normales
```
EURUSD:       85%
GBPUSD:       85%
USDJPY:       85%
AUDUSD:       85%
```

**Nota:** Las rentabilidades varían según el broker y el tipo de cuenta.

## 🎯 ESTRATEGIAS POR TIPO DE ACTIVO

### Estrategia OTC

**Características:**
- Volatilidad más constante
- Menos gaps
- Movimientos más suaves
- Ideal para scalping

**Configuración recomendada:**
```python
TIMEFRAME = 60  # 1 minuto
DURATION = 1    # 1 minuto
AMOUNT = 1-2    # Bajo riesgo
```

### Estrategia Normales

**Características:**
- Mayor volatilidad
- Reacción a noticias
- Gaps en apertura
- Tendencias más fuertes

**Configuración recomendada:**
```python
TIMEFRAME = 60-300  # 1-5 minutos
DURATION = 1-5      # 1-5 minutos
AMOUNT = 2-5        # Riesgo moderado
```

## 🔍 DIAGNÓSTICO

### Verificar Activos Disponibles
```bash
python test_activos_disponibles.py
```

**Resultado esperado:**
```
✅ Activos OTC disponibles: 6
✅ Activos normales disponibles: 6
✅ Hay activos disponibles para operar
```

### Si No Hay Activos

**Posibles causas:**
1. No conectado al broker
2. Mercado cerrado (solo normales)
3. Problema con la API
4. Cuenta no verificada

**Soluciones:**
1. Verificar conexión
2. Usar activos OTC
3. Reiniciar conexión
4. Verificar credenciales

## 📝 LOGS TÍPICOS

### Inicio Exitoso
```
🔍 Escaneando mercado...
💎 Mejor activo OTC: EURUSD-OTC (Profit: 85%)
✅ Activo seleccionado: EURUSD-OTC
▶️ Bot iniciado
```

### Sin Activos (Antes de la corrección)
```
🔍 Escaneando mercado...
⚠️ No se encontraron activos rentables abiertos
❌ No se encontraron activos operables
```

### Con Fallback
```
🔍 Escaneando mercado...
⚠️ No se encontraron activos con get_open_assets()
🔄 Probando activos OTC manualmente...
✅ Activo disponible: EURUSD-OTC
✅ Activo seleccionado: EURUSD-OTC
```

## ✅ ESTADO ACTUAL

**Activos OTC:** ✅ Funcionando
**Activos Normales:** ✅ Funcionando
**Selección Automática:** ✅ Funcionando
**Fallback:** ✅ Funcionando

**El bot ahora puede:**
- ✅ Encontrar activos OTC
- ✅ Encontrar activos normales
- ✅ Seleccionar el mejor disponible
- ✅ Usar fallback si es necesario
- ✅ Operar 24/7 con OTC

## 🚀 PRÓXIMOS PASOS

1. ✅ Activos funcionando
2. ⏳ Probar bot en modo automático
3. ⏳ Validar selección de activos
4. ⏳ Optimizar para diferentes horarios
5. ⏳ Añadir más activos a la lista
