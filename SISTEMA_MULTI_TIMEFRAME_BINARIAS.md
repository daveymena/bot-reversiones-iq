# 📊 Sistema Multi-Timeframe para Opciones Binarias

## 🎯 Objetivo

Detectar soportes y resistencias válidos analizando 3 temporalidades específicas para opciones binarias: **M1, M15 y M30**.

---

## 📐 Temporalidades Analizadas

### M1 (1 minuto) - Entrada Precisa
- **Propósito**: Timing exacto de entrada
- **Uso**: Detectar el momento preciso para ejecutar
- **Indicadores**: RSI, EMAs, swing points recientes

### M15 (15 minutos) - Estructura Intermedia
- **Propósito**: Contexto de estructura de mercado
- **Uso**: Identificar soportes/resistencias intermedios
- **Indicadores**: Tendencia, niveles clave, volatilidad

### M30 (30 minutos) - Contexto Principal
- **Propósito**: Dirección general del mercado
- **Uso**: Confirmar tendencia principal
- **Indicadores**: Tendencia fuerte, niveles mayores

---

## 🔍 Análisis Realizado

### 1. Detección de Tendencia
Para cada temporalidad:
- **EMA 9 y EMA 21** para determinar dirección
- **Uptrend**: EMA9 > EMA21 y precio > EMA9
- **Downtrend**: EMA9 < EMA21 y precio < EMA9
- **Neutral**: Condiciones mixtas

### 2. Swing Points (Soportes y Resistencias)
- **Swing Highs**: Máximos locales (resistencias potenciales)
- **Swing Lows**: Mínimos locales (soportes potenciales)
- **Lookback**: 10 velas para identificar puntos válidos

### 3. Confluencia de Niveles
El sistema busca niveles que aparecen en **múltiples temporalidades**:

```
Ejemplo de Confluencia:
M1:  Soporte en 1.15450
M15: Soporte en 1.15448
M30: Soporte en 1.15452

→ CONFLUENCIA DETECTADA en 1.15450 (3 temporalidades)
```

### 4. Verificación de Toque
- **Tolerancia**: 0.15% (0.0015)
- Detecta si el precio actual está tocando un nivel clave
- Marca niveles activos: 📍Soporte o 📍Resistencia

---

## ✅ Criterios de Aprobación

Para que el bot opere, se requiere:

### 1. Alineación de Tendencias
- **Mínimo**: 2 de 3 temporalidades deben estar alineadas
- **Ejemplo válido**:
  - M1: Uptrend
  - M15: Uptrend
  - M30: Neutral
  - ✅ APROBADO (2 de 3)

### 2. Confluencia de Niveles S/R
- **Obligatorio**: Debe haber al menos 1 nivel de confluencia
- **Tipos**:
  - Soportes con confluencia (para CALL)
  - Resistencias con confluencia (para PUT)

### 3. Coherencia Direccional
- Si tendencia alcista → Buscar CALL en soporte con confluencia
- Si tendencia bajista → Buscar PUT en resistencia con confluencia

---

## 📊 Output del Sistema

### Cuando Detecta Oportunidad:

```
📊 ANALIZANDO TEMPORALIDADES M1, M15, M30...
   M1: UPTREND | RSI: 32.5 📍Soporte
   M15: UPTREND | RSI: 35.2
   M30: UPTREND | RSI: 38.1

   🟢 SOPORTES CON CONFLUENCIA:
      1.15450 (M1, M15, M30)
      1.15320 (M15, M30)

✅ CONFLUENCIA DETECTADA: CALL (66%)
   Razón: 2 temporalidades alcistas con confluencia de niveles
```

### Cuando Rechaza:

```
📊 ANALIZANDO TEMPORALIDADES M1, M15, M30...
   M1: UPTREND | RSI: 45.2
   M15: DOWNTREND | RSI: 52.1
   M30: NEUTRAL | RSI: 48.5

❌ SIN CONFLUENCIA: Temporalidades no alineadas
⏸️ OPERACIÓN CANCELADA - Se requiere confluencia de temporalidades Y niveles S/R
```

---

## 🎯 Ventajas del Sistema

### 1. Evita Trampas de M1
- No opera solo con señales de 1 minuto
- Requiere confirmación de temporalidades mayores
- Reduce falsas señales

### 2. Detecta Niveles Válidos
- Soportes y resistencias confirmados en múltiples TFs
- Mayor probabilidad de rebote
- Niveles respetados por el mercado

### 3. Contexto Completo
- Entiende la dirección general (M30)
- Valida estructura intermedia (M15)
- Ejecuta con precisión (M1)

### 4. Análisis Profesional
- Similar a traders profesionales
- Basado en confluencia de niveles
- No opera "a ciegas"

---

## 🔧 Configuración Actual

```python
# Temporalidades
M1 = 60 segundos
M15 = 900 segundos
M30 = 1800 segundos

# Criterios de Confluencia
min_timeframes_aligned = 2  # De 3 total
tolerance_levels = 0.002    # 0.2% para confluencia de niveles
tolerance_touch = 0.0015    # 0.15% para detectar toque

# Swing Points
lookback = 10  # Velas para identificar swings
max_swings = 3 # Últimos 3 swings por tipo
```

---

## 📈 Flujo de Decisión

```
1. Detectar oportunidad en M1
   ↓
2. Analizar M1, M15, M30
   ├─ Tendencias
   ├─ RSI
   ├─ Swing points
   └─ Niveles activos
   ↓
3. Buscar confluencia de niveles
   ├─ Soportes en múltiples TFs
   └─ Resistencias en múltiples TFs
   ↓
4. Verificar alineación
   ├─ ❌ <2 TFs alineadas → RECHAZAR
   ├─ ❌ Sin confluencia de niveles → RECHAZAR
   └─ ✅ 2+ TFs + Confluencia → CONTINUAR
   ↓
5. Verificar coherencia direccional
   ├─ Uptrend + Soporte → CALL ✅
   ├─ Downtrend + Resistencia → PUT ✅
   └─ Conflicto → RECHAZAR ❌
   ↓
6. EJECUTAR OPERACIÓN
```

---

## 💡 Ejemplos Prácticos

### Ejemplo 1: CALL Aprobado

```
Situación:
- M1: Uptrend, RSI 28, tocando soporte en 1.15450
- M15: Uptrend, RSI 32, soporte en 1.15448
- M30: Uptrend, RSI 35, soporte en 1.15452

Confluencia:
- Soporte en 1.15450 (M1, M15, M30)

Decisión:
✅ CALL APROBADO
- 3 temporalidades alcistas
- Confluencia de soporte en 3 TFs
- Precio tocando nivel clave
```

### Ejemplo 2: PUT Rechazado

```
Situación:
- M1: Downtrend, RSI 72, tocando resistencia en 1.15800
- M15: Uptrend, RSI 58
- M30: Uptrend, RSI 62

Confluencia:
- Resistencia solo en M1

Decisión:
❌ PUT RECHAZADO
- Solo 1 temporalidad bajista
- Sin confluencia de niveles
- Conflicto con TFs mayores
```

### Ejemplo 3: Esperando Confluencia

```
Situación:
- M1: Uptrend, RSI 35
- M15: Uptrend, RSI 38
- M30: Uptrend, RSI 42

Confluencia:
- Sin niveles de confluencia detectados

Decisión:
❌ RECHAZADO
- Tendencias alineadas ✅
- Sin confluencia de niveles S/R ❌
- Esperando mejor punto de entrada
```

---

## 🎓 Conclusión

Este sistema garantiza que el bot:
1. ✅ No opera sin análisis previo
2. ✅ Requiere confluencia de temporalidades
3. ✅ Detecta soportes/resistencias válidos
4. ✅ Opera solo en puntos óptimos
5. ✅ Reduce operaciones impulsivas
6. ✅ Aumenta probabilidad de éxito

**El bot NO operará "por operar". Solo ejecutará cuando todas las condiciones sean favorables.**

---

**Desarrollado para**: Opciones Binarias (Exnova)
**Temporalidades**: M1, M15, M30
**Fecha**: 2026-04-03
