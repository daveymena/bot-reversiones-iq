# 🎯 CRITERIOS DE EJECUCIÓN DEL BOT

## Sistema de Decisión en 10 Pasos

El bot usa un sistema de **doble validación**: **AdaptiveLearner** (aprende de trades pasados) + **MarketAI** (analiza el contexto actual).

---

## 📊 PASO 1: Detección de Zona

El bot busca que el precio esté cerca de una **zona de soporte/resistencia**:

### Criterios de Zona:
- ✅ **Distancia máxima**: Precio a menos de 0.15% de la zona
- ✅ **Fuerza mínima**: Zona con strength ≥ 0.35 (aprende y ajusta)
- ✅ **Toques históricos**: Mínimo 2 toques previos
- ✅ **Hold rate**: Preferiblemente ≥ 60% (cuántas veces rebotó)

### Puntuación Extra:
- 🟢 **Zona fuerte** (strength ≥ 0.70): +puntos
- 🟢 **Multi-timeframe** (≥3 toques): +puntos
- 🟢 **Hold rate alto** (≥60%): +puntos

---

## 📈 PASO 2: Análisis de Tendencia

### Criterios:
- ✅ **Tendencia dominante**: Detecta si es uptrend, downtrend o lateral
- ✅ **Alineación**: Prefiere operar a favor de la tendencia
- ⚠️ **Contra-tendencia**: Permitido pero con penalización (-7%)

### Puntuación:
- 🟢 **A favor de tendencia**: +puntos
- 🟡 **Contra-tendencia**: -7% score (pero no bloquea)

---

## 📉 PASO 3: RSI (Sobrecompra/Sobreventa)

### Criterios:
- ✅ **RSI extremo**: < 28 o > 72 (señal fuerte)
- ✅ **RSI sobrevendido**: < 38 para CALL
- ✅ **RSI sobrecomprado**: > 62 para PUT
- ✅ **Divergencia RSI**: Precio vs RSI en direcciones opuestas (señal premium)

### Puntuación:
- 🟢 **RSI extremo**: +puntos importantes
- 🟢 **Divergencia**: +puntos extra
- 🟡 **RSI neutral** (40-60): Sin penalización

---

## 🕯️ PASO 4: Patrón de Vela (CERRADA)

**IMPORTANTE**: Solo analiza velas **CERRADAS** (no velas en formación).

### Patrones Detectados:
1. **Pin Bar** (rechazo con mecha larga)
2. **Engulfing** (vela que envuelve la anterior)
3. **Hammer / Shooting Star** (martillo o estrella fugaz)
4. **Morning Star / Evening Star** (patrón de 3 velas)
5. **Doji Reversal** (indecisión que precede reversión)

### Criterios:
- ✅ **Patrón fuerte**: Strength ≥ 0.75
- ✅ **Vela confirmada**: Cerrada completamente
- ✅ **Rechazo visible**: Mecha ≥ 20% del rango

### Puntuación:
- 🟢 **Patrón fuerte**: +puntos
- 🟢 **Pin bar o engulfing**: +puntos extra
- 🟡 **Sin patrón**: Puede operar si otros factores son fuertes

---

## 📊 PASO 5: MACD (Momentum)

### Criterios:
- ✅ **Cruce MACD**: Histograma cambiando de dirección
- ✅ **MACD girando**: Momentum cambiando

### Puntuación:
- 🟢 **MACD confirmando**: +puntos
- 🟡 **MACD neutral**: Sin impacto

---

## 🔄 PASO 6: Multi-Timeframe (MTF)

Analiza 3 timeframes: **M1, M5, M15**

### Criterios:
- ✅ **Alineación**: 2 de 3 timeframes en la misma dirección
- ✅ **Estructura clara**: Tendencia definida en cada TF

### Puntuación:
- 🟢 **MTF alineado**: +puntos importantes
- 🟡 **MTF mixto**: Penalización leve

---

## ⏰ PASO 7: Timing de Entrada

### Criterios:
- ✅ **Vela cerrada**: No entra en velas en formación
- ✅ **Approach limpio**: Precio cayendo a soporte o subiendo a resistencia
- ✅ **Rechazo visible**: Mecha de rechazo ≥ 20%

### Puntuación:
- 🟢 **Timing perfecto**: +puntos
- 🟡 **Timing imperfecto**: -6% score (pero no bloquea)

---

## 🧠 PASO 8: MarketAI (IA Local)

**MarketAI** analiza TODO el contexto y da un veredicto:

### Análisis de MarketAI:
1. **Lee la estructura del mercado** (tendencia, fase, impulso)
2. **Evalúa la zona** (fuerza, toques, hold rate)
3. **Interpreta el patrón** (tipo, calidad, micro-estructura)
4. **Analiza momentum** (RSI, MACD, divergencias)
5. **Verifica alineación MTF**
6. **Detecta trampas** (fake breakouts, spikes, mercado muerto)
7. **Sintetiza con ponderación bayesiana**
8. **Construye narrativa explicable**

### Veredicto de MarketAI:
- **Score**: 0-100 (calidad del setup)
- **Confianza**: 0-100% (certeza del análisis)
- **Label**: EXCELENTE / BUENO / MODERADO / DÉBIL / SKIP
- **Should trade**: true/false (recomendación final)
- **Narrativa**: Explicación en lenguaje natural

### Decisión:
- 🔴 **SKIP** (score < 30): NO OPERA
- 🟡 **DÉBIL** (30-45): Opera solo si otros factores son muy fuertes
- 🟢 **MODERADO** (45-60): Opera si cumple umbral mínimo
- 🟢 **BUENO** (60-75): Opera con confianza
- 🟢 **EXCELENTE** (75-100): Opera con alta confianza

---

## 🎯 PASO 9: Puntuación Combinada

### Fórmula:
```
Score Final = (AdaptiveLearner × 50%) + (MarketAI × 50%)
```

### AdaptiveLearner:
- Aprende de trades pasados
- Ajusta pesos de cada condición
- Penaliza condiciones que históricamente pierden
- Recompensa condiciones que históricamente ganan

### Penalizaciones Suaves:
- **Contra-tendencia**: -7%
- **RSI neutral**: -4%
- **Hold rate bajo**: -5%
- **Timing imperfecto**: -6%

### Umbral Dinámico:
- **Normal**: Score ≥ 45% (aprende y ajusta)
- **IA dice EXCELENTE/BUENO**: Score ≥ 35% (más permisivo)
- **IA dice MODERADO**: Score ≥ 45%
- **IA dice DÉBIL**: Score ≥ 50% (más estricto)

---

## ✅ PASO 10: Decisión Final

### Condiciones para OPERAR:

**Opción 1: Score Alto**
```
Score Final ≥ Umbral Mínimo (45% por defecto)
```

**Opción 2: IA Recomienda**
```
MarketAI.should_trade = true
Y Score Final ≥ 38%
```

### Cálculo de Confianza:
```
Confianza = (Confianza_Técnica × 60%) + (Confianza_IA × 40%)
```

### Confianza Mínima:
- ✅ **Confianza ≥ 65%**: Opera
- ❌ **Confianza < 65%**: Espera mejor oportunidad

---

## 📋 RESUMEN: Checklist de Ejecución

Para que el bot ejecute una operación, debe cumplir:

### ✅ Obligatorios:
1. ✅ Precio cerca de zona (< 0.15% distancia)
2. ✅ Zona con fuerza ≥ 0.35
3. ✅ Vela CERRADA (no en formación)
4. ✅ MarketAI NO dice "SKIP"
5. ✅ Score combinado ≥ umbral (35-50% según IA)
6. ✅ Confianza ≥ 65%

### 🟢 Deseables (suman puntos):
- 🟢 Zona fuerte (≥ 0.70)
- 🟢 RSI extremo (< 28 o > 72)
- 🟢 Patrón fuerte (pin bar, engulfing)
- 🟢 MTF alineado
- 🟢 A favor de tendencia
- 🟢 MACD confirmando
- 🟢 MarketAI dice "EXCELENTE" o "BUENO"

### ⚠️ Penalizaciones (restan puntos):
- ⚠️ Contra-tendencia (-7%)
- ⚠️ RSI neutral (-4%)
- ⚠️ Hold rate bajo (-5%)
- ⚠️ Timing imperfecto (-6%)
- ⚠️ MTF no alineado (penalización)

---

## 🎓 Sistema de Aprendizaje

Después de cada trade:

1. **Evalúa el resultado** (WIN/LOSS)
2. **Analiza qué funcionó** y qué no
3. **Ajusta pesos** de cada condición
4. **Actualiza umbrales** (zona, RSI, score mínimo)
5. **Guarda en memoria** para futuros trades

### Ejemplo de Aprendizaje:
```
Si "zone_strength_high" + "rsi_extreme" → WIN (70% del tiempo)
  → Aumenta peso de estas condiciones

Si "counter_trend" + "pattern_weak" → LOSS (80% del tiempo)
  → Reduce peso o aumenta penalización
```

---

## 🔍 Ejemplo Real de Decisión

### Escenario:
```
Activo: EURUSD-OTC
Precio: 1.18234
Zona: 1.18250 (resistencia, strength=0.85, 12 toques, hold=95%)
Distancia: 0.013% ✅
Tendencia: Uptrend (alcista)
RSI: 76 (sobrecomprado) ✅
Patrón: Pin Bar Bearish (strength=0.88) ✅
MACD: Girando a la baja ✅
MTF: M1=up, M5=up, M15=neutral (2/3 alcista)
```

### Análisis MarketAI:
```
Score: 82/100
Confianza: 89%
Label: EXCELENTE
Narrativa: "Mercado en tendencia alcista llegó a resistencia 
           muy fuerte formando pin bar bajista con RSI en 
           sobrecompra extrema. → IA recomienda PUT con 
           confianza 89% [EXCELENTE]"
Should trade: true
```

### Puntuación:
```
AdaptiveLearner: 0.78 (78%)
MarketAI: 0.82 (82%)
Score Final: (0.78 × 50%) + (0.82 × 50%) = 0.80 (80%)
Umbral: 35% (IA dice EXCELENTE)
```

### Decisión:
```
✅ Score 80% ≥ 35% → CUMPLE
✅ Confianza 89% ≥ 65% → CUMPLE
✅ MarketAI recomienda → CUMPLE

→ EJECUTA: PUT en EURUSD-OTC
→ Monto: $63.84 (2% del balance)
→ Expiración: 3 minutos
```

---

## 🎯 Configuración Actual

```python
MIN_CONFIDENCE = 0.65        # 65% confianza mínima
TRADE_AMOUNT_PCT = 0.02      # 2% del balance por trade
MIN_BETWEEN_TRADES = 45      # 45 segundos entre trades
COOLDOWN_AFTER_LOSS = 90     # 90 segundos después de pérdida
MAX_CONSEC_LOSSES = 4        # Pausa después de 4 pérdidas seguidas
```

---

## 📊 Estadísticas de Filtrado

En promedio, el bot:
- **Escanea**: 100 oportunidades
- **Pasan zona**: 30 (30%)
- **Pasan RSI**: 15 (15%)
- **Pasan patrón**: 8 (8%)
- **Pasan MarketAI**: 3 (3%)
- **Ejecuta**: 1-2 (1-2%)

**Ratio de selectividad: 98-99% rechazado, 1-2% ejecutado**

Esto significa que el bot es **MUY selectivo** y solo opera cuando tiene alta probabilidad de éxito.

---

**Fecha**: 2025-01-09  
**Versión**: 4.0  
**Motor**: IntelligentEngine + MarketAI  
**Modo**: PRACTICE (cuenta demo)
