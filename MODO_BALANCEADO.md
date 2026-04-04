# ⚖️ MODO BALANCEADO - Configuración Activa

## 🎯 Objetivo

Operar con análisis profundo pero sin ser demasiado restrictivo. Balance entre calidad y cantidad de operaciones.

---

## ✅ Configuración Actual

### 1. Multi-Timeframe (Simplificado)
**Antes (Conservador)**:
- Temporalidades: M1, M5, M15, H1
- Requería 75% (3 de 4) temporalidades alineadas
- Requería confluencia de niveles S/R
- Rechazaba casi todo

**Ahora (Balanceado)**:
- ✅ Temporalidades: M1, M15, M30 (correcto para binarias)
- ✅ Requiere solo 1+ temporalidad alineada (33%)
- ✅ Bonus si M30 está alineada (+20 puntos)
- ✅ NO requiere confluencia de niveles S/R
- ✅ Verifica tendencia principal

### 2. Fibonacci (Opcional)
- ✅ Da boost de confianza si coincide
- ✅ NO bloquea si no coincide
- ✅ Golden Ratio: +15% confianza
- ✅ Otros niveles: +5% confianza

### 3. Precision Refiner (Más Flexible)
**Antes**: 80% confianza mínima
**Ahora**: **70% confianza mínima**

**Rangos RSI más amplios**:
- CALL: 20-40 (antes 20-35)
- PUT: 60-80 (antes 65-80)

### 4. Cooldown (Reducido)
- **2 minutos** entre operaciones (antes 5 min)
- **5 minutos** después de perder (antes 10 min)

### 5. Ollama (Obligatorio)
- ✅ Siempre analiza
- ✅ Debe aprobar
- ✅ Si falla, usa respaldo técnico

---

## 📊 Validaciones Activas

| Validación | Requisito | Acción si Falla |
|------------|-----------|-----------------|
| **Ollama** | Debe aprobar | ❌ RECHAZA (o usa respaldo) |
| **Multi-timeframe** | 1+ temporalidad alineada | ⚠️ Continúa |
| **Fibonacci** | Opcional | ⚠️ Sin boost |
| **Precision Refiner** | Score ≥60 | ❌ RECHAZA |
| **Confianza** | ≥70% | ❌ RECHAZA |
| **Cooldown** | 2 min | ⏳ ESPERA |

---

## 🎯 Criterios de Operación

El bot operará cuando:

1. ✅ **Ollama aprueba** (o respaldo técnico)
2. ✅ **Al menos 1 temporalidad alineada**
3. ✅ **Confianza ≥70%**
4. ✅ **Precision Refiner ≥60**
5. ✅ **Cooldown respetado**

---

## 📈 Resultados Esperados

### Operaciones por Día
- **5-10 operaciones** (vs 1-2 en modo conservador)
- **1-2 operaciones por hora** en promedio

### Win Rate Esperado
- **65-70%** (vs 75%+ en modo conservador)
- Balance entre calidad y cantidad

### Características
- ✅ Análisis profundo con Ollama
- ✅ Verificación multi-timeframe
- ✅ Fibonacci como boost
- ✅ Auto-aprendizaje activo
- ✅ Más oportunidades

---

## 🔍 Ejemplo de Operación

```
💎 Oportunidad detectada en GBPUSD-OTC

🧠 OLLAMA ANALIZANDO...
✅ OLLAMA DICE: OPERAR (CALL)
   Razón: RSI sobreventa + Momentum alcista

📊 Verificando tendencia multi-timeframe...
   M1: UPTREND | RSI: 31.0
   M15: NEUTRAL | RSI: 45.2
   M30: NEUTRAL | RSI: 48.5
✅ 1 de 3 temporalidades alcistas → CALL

📐 FIBONACCI: Score 45/100
⚠️ Fibonacci no recomienda entrada
   Continuando sin boost de Fibonacci...

🎯 PRECISION REFINER: Score 72/100
✅ APROBADO

🚀 EJECUTANDO OPERACIÓN
   GBPUSD-OTC CALL @ 1.31532
   Monto: $1.00 | Expiración: 5 min
```

---

## ⚖️ Comparación de Modos

| Característica | Conservador | **Balanceado** | Agresivo |
|----------------|-------------|----------------|----------|
| Ops/día | 1-2 | **5-10** | 15-20 |
| Win rate | 75%+ | **65-70%** | 55-60% |
| Multi-TF | 2/3 + S/R | **1/3** | OFF |
| Fibonacci | Obligatorio | **Opcional** | OFF |
| Confianza | 80% | **70%** | 60% |
| Cooldown | 5 min | **2 min** | 1 min |
| Ollama | Obligatorio | **Obligatorio** | Opcional |

---

## 💡 Ventajas del Modo Balanceado

### ✅ Pros
1. Opera regularmente (5-10 veces/día)
2. Mantiene análisis de Ollama
3. Verifica tendencia multi-timeframe
4. Auto-aprende y se ajusta
5. Balance calidad/cantidad

### ⚠️ Contras
1. Win rate menor que modo conservador
2. Más operaciones = más riesgo
3. Puede operar en condiciones no óptimas

---

## 🎓 Recomendaciones

### Para PRACTICE (Demo)
- ✅ Usar MODO BALANCEADO
- ✅ Monitorear 24-48 horas
- ✅ Verificar win rate ≥65%
- ✅ Ajustar si es necesario

### Para REAL (Dinero Real)
- ⚠️ Solo después de 65%+ win rate en PRACTICE
- ⚠️ Empezar con capital mínimo
- ⚠️ Monitorear primeras 10 operaciones
- ⚠️ Detener si win rate <60%

---

## 🔧 Ajustes Disponibles

Si quieres cambiar el modo:

### Más Conservador
```python
# En precision_refiner.py
'confidence_threshold': 75  # Aumentar

# En multi_timeframe_analyzer.py
uptrend_count >= 2  # Requerir más temporalidades
```

### Más Agresivo
```python
# En precision_refiner.py
'confidence_threshold': 65  # Reducir

# En trader.py
# Comentar validación multi-timeframe
```

---

## 📊 Estado Actual

**MODO ACTIVO**: ⚖️ BALANCEADO

- Multi-timeframe: Simplificado ✅
- Fibonacci: Opcional ✅
- Confianza: 70% ✅
- Cooldown: 2 min ✅
- Ollama: Obligatorio ✅

**El bot está operando con este modo desde**: 2026-04-03 19:04

---

**Desarrollado para**: Opciones Binarias (Exnova)
**Modo**: Balanceado
**Objetivo**: 5-10 operaciones/día con 65-70% win rate
