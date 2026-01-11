# 📊 ANÁLISIS MULTI-TIMEFRAME (MTF)

## El Problema que Resuelve

**Antes:** El bot analizaba solo velas de 1 minuto (M1), sin ver el "panorama completo". Era como intentar navegar mirando solo las olas pequeñas, ignorando las corrientes grandes.

**Resultado:** Entraba en operaciones sin saber si estaba en un soporte/resistencia REAL o solo en un nivel temporal sin importancia.

---

## La Solución: Análisis Multi-Timeframe

El bot ahora analiza **3 temporalidades**:

1. **M30 (30 minutos)** - Identifica la TENDENCIA principal y niveles FUERTES
2. **M15 (15 minutos)** - Confirma soportes/resistencias clave
3. **M1 (1 minuto)** - Timing exacto de entrada

---

## 🎯 Cómo Funciona

### Paso 1: Identificar Niveles Clave (M15/M30)

El bot busca en M15 y M30:
- **Soportes**: Mínimos que se han respetado múltiples veces
- **Resistencias**: Máximos que han frenado el precio varias veces
- **Puntos Pivote**: Niveles de equilibrio del mercado

Solo guarda los **5 niveles más importantes** de cada tipo.

### Paso 2: Analizar Contexto

Determina:
- **Tendencia en M30**: ¿Alcista, Bajista o Lateral?
- **Posición actual**: ¿Está el precio EN un soporte/resistencia o entre niveles?
- **Distancia al nivel**: ¿Qué tan cerca está del nivel clave?

### Paso 3: Buscar Entrada en M1

**SOLO** si el precio está en un nivel clave (dentro del 0.2%), busca señal de entrada en M1:

#### Para CALL (Compra en Soporte):
✅ Vela actual es ALCISTA (ya rebotó)  
✅ Vela anterior era BAJISTA (estaba cayendo)  
✅ RSI < 35 (sobreventa)  
✅ Mecha inferior larga (rechazo del soporte)

#### Para PUT (Venta en Resistencia):
✅ Vela actual es BAJISTA (ya rechazó)  
✅ Vela anterior era ALCISTA (estaba subiendo)  
✅ RSI > 65 (sobrecompra)  
✅ Mecha superior larga (rechazo de resistencia)

---

## 📋 Ejemplo Real

```
🔍 Analizando EURUSD-OTC en múltiples temporalidades...

   📊 Contexto M30: UPTREND
   📍 Posición: AT_SUPPORT
   🎯 Nivel clave: 1.08450 (distancia: 0.08%)
   
   ✅ SEÑAL MTF: CALL - Confianza: 85%
   📝 Razón: Rebote confirmado en SOPORTE M30 (1.08450)
   
   🔄 Usando señal Multi-Timeframe (más confiable)
   
   🚀 Enviando orden a EURUSD-OTC (call, 3min)...
```

---

## 🎯 Ventajas del Sistema MTF

### 1. **Entradas Más Precisas**
- Solo opera en niveles que REALMENTE importan
- Evita "ruido" de temporalidades pequeñas

### 2. **Mayor Confianza**
- Soportes/resistencias en M30 son mucho más fuertes
- Menos falsas rupturas

### 3. **Mejor Timing**
- M30 da el "dónde" (nivel clave)
- M1 da el "cuándo" (momento exacto)

### 4. **Filtro Automático**
- Si no hay nivel clave cerca → NO opera
- Evita operaciones "en medio de la nada"

---

## ⚙️ Configuración

### Temporalidades Usadas:
- **M30**: 50 velas (25 horas de datos)
- **M15**: 50 velas (12.5 horas de datos)
- **M1**: 100 velas (1.6 horas de datos)

### Tolerancia de Niveles:
- **Clustering**: Niveles dentro del 0.1% se agrupan
- **Entrada**: Precio debe estar dentro del 0.2% del nivel

### Expiración:
- **3 minutos** (180 segundos) para dar tiempo al rebote/rechazo

---

## 🚫 Qué Rechaza el Sistema

1. **Precio entre niveles**: Si no está cerca de soporte/resistencia → NO opera
2. **Reversión sin nivel M30**: Si la estrategia sugiere reversión pero no hay nivel clave → RECHAZADO
3. **Niveles débiles**: Solo usa niveles que se han respetado múltiples veces

---

## 📊 Impacto Esperado

- **Win Rate**: +15-20% (opera solo en niveles fuertes)
- **Operaciones**: -30% (más selectivo, menos operaciones)
- **Calidad**: Mucho mayor (cada operación tiene fundamento sólido)

---

## 🔄 Integración con Otros Sistemas

El MTF se combina con:
- ✅ **Detector de Trampas**: Evita bull/bear traps
- ✅ **Aprendizaje Histórico**: Penaliza activos tóxicos
- ✅ **Validación IA**: Confirma timing óptimo
- ✅ **Filtros de Rentabilidad**: Score adicional por confluencia

---

## 📝 Logs del Sistema

Cuando el MTF encuentra una oportunidad:

```
🔍 Analizando GBPUSD-OTC en múltiples temporalidades...
   📊 Contexto M30: DOWNTREND
   📍 Posición: AT_RESISTANCE
   🎯 Nivel clave: 1.25680 (distancia: 0.15%)
   ✅ SEÑAL MTF: PUT - Confianza: 80%
   📝 Razón: Rechazo confirmado en RESISTENCIA M30 (1.25680)
   🔄 Usando señal Multi-Timeframe (más confiable)
```

Cuando NO hay señal:

```
🔍 Analizando USDJPY-OTC en múltiples temporalidades...
   ⚠️ No hay señal MTF clara - precio no está en nivel clave M30
   ❌ RECHAZADO: Reversión sin confirmación de nivel M30
```

---

## ⚠️ Importante

- El MTF **NO reemplaza** otras estrategias, las **complementa**
- Si hay señal MTF con confianza ≥70%, **tiene prioridad**
- Si no hay señal MTF, otras estrategias pueden operar (con más filtros)

---

**El bot ahora opera como un trader profesional: analiza el panorama completo antes de entrar.** 🚀
