# 🧪 PLAN DE TESTING - MEJORAS IMPLEMENTADAS

## 📋 Resumen de Cambios
- ✅ Umbral de confianza: 40% → 65%
- ✅ RSI: 30/70 → 25/75
- ✅ MACD: Validación de divergencia clara
- ✅ Pullback: Validación real (0.05% - 0.5%)
- ✅ Cooldown: 60s → 180s
- ✅ Umbral mínimo: 45 → 65 puntos

---

## 🚀 FASE 1: TESTING LOCAL (30 minutos)

### Paso 1: Ejecutar Bot en PRACTICE
```bash
python run_learning_bot.py
```

### Paso 2: Monitorear Logs (Primeros 5 minutos)
Buscar estos mensajes:

✅ **CORRECTO**:
```
[21:15:47] GBPUSD-OTC>>> CALL $1 3min [PULLBACK] (Conf: 65%)
RSI: 22.5 | MACD: 0.00015
✅ Pullback real (0.15%)
[OK] ID: 13774160566 | Esperando...
[WIN] $+1.00
```

❌ **INCORRECTO** (Rechazar):
```
[21:15:47] GBPUSD-OTC>>> CALL $1 3min [PULLBACK] (Conf: 45%)
❌ RECHAZADA (Confianza baja: 45% < 65%)
```

### Paso 3: Verificar Métricas Clave

| Métrica | Esperado | Acción |
|---------|----------|--------|
| Confianza | > 65% | ✅ OK |
| RSI | < 25 o > 75 | ✅ OK |
| MACD | > 0.0001 | ✅ OK |
| Pullback | 0.05% - 0.5% | ✅ OK |
| Cooldown | 180s | ✅ OK |

---

## 🎯 FASE 2: TESTING EXTENDIDO (1-2 horas)

### Objetivo
Recopilar 20-30 operaciones para validar win rate

### Monitoreo
```
Ciclo 1 | 0m0s | T:1 | 1/1 | WR:100% | $+1.00
Ciclo 2 | 3m15s | T:2 | 2/2 | WR:100% | $+2.00
Ciclo 3 | 6m30s | T:3 | 3/3 | WR:100% | $+3.00
...
```

### Criterios de Éxito
- [ ] Win rate > 60%
- [ ] Operaciones consistentes
- [ ] Confianza > 65% en todas
- [ ] Cooldown respetado (180s)
- [ ] Sin operaciones rechazadas por confianza baja

### Criterios de Fallo
- ❌ Win rate < 50%
- ❌ Muchas operaciones rechazadas
- ❌ Confianza inconsistente
- ❌ Errores de conexión

---

## 📊 FASE 3: ANÁLISIS DE RESULTADOS

### Si Win Rate > 60% ✅
```
ÉXITO - Pasar a REAL
1. Hacer commit de resultados
2. Cambiar ACCOUNT_TYPE=REAL
3. Aumentar CAPITAL_PER_TRADE a 2-5
4. Monitorear 1 semana
```

### Si Win Rate 50-60% ⚠️
```
PARCIAL - Ajustar parámetros
1. Aumentar umbral a 70%
2. Bajar MACD a 0.00005
3. Testear 1 hora más
4. Decidir si continuar
```

### Si Win Rate < 50% ❌
```
FALLO - Revertir cambios
1. git revert be5f7ef
2. Investigar qué salió mal
3. Ajustar parámetros
4. Testear nuevamente
```

---

## 🔍 DEBUGGING

### Si Confianza Baja (< 65%)
```python
# Verificar en logs:
# 1. RSI está en rango correcto?
# 2. MACD tiene divergencia clara?
# 3. Pullback es real?
# 4. Hay confluencia de señales?

# Solución:
# - Bajar umbral a 60%
# - Revisar indicadores
# - Ajustar thresholds
```

### Si Operaciones Muy Pocas
```python
# Verificar:
# 1. Cooldown está muy alto?
# 2. Umbral de confianza muy alto?
# 3. Mercado sin volatilidad?

# Solución:
# - Bajar cooldown a 120s
# - Bajar umbral a 60%
# - Cambiar activo
```

### Si Operaciones Muy Frecuentes
```python
# Verificar:
# 1. Cooldown se está respetando?
# 2. Umbral de confianza muy bajo?

# Solución:
# - Aumentar cooldown a 240s
# - Aumentar umbral a 70%
```

---

## 📝 REPORTE DE TESTING

### Template
```
REPORTE DE TESTING - MEJORAS IMPLEMENTADAS
Fecha: [FECHA]
Duración: [TIEMPO]
Operaciones: [TOTAL]

RESULTADOS:
- Win Rate: [%]
- Ganancias: $[TOTAL]
- Pérdidas: $[TOTAL]
- Promedio por operación: $[PROMEDIO]

MÉTRICAS:
- Confianza promedio: [%]
- RSI promedio: [VALOR]
- MACD promedio: [VALOR]
- Pullback promedio: [%]

CONCLUSIÓN:
[ÉXITO / PARCIAL / FALLO]

PRÓXIMOS PASOS:
[ACCIONES]
```

---

## ⏱️ TIMELINE

| Fase | Duración | Acción |
|------|----------|--------|
| 1 | 30 min | Testing local |
| 2 | 1-2 hrs | Testing extendido |
| 3 | 30 min | Análisis |
| **Total** | **2-3 hrs** | **Decisión final** |

---

## 🎯 MÉTRICAS FINALES

### Objetivo Principal
**Win Rate > 60%**

### Métricas Secundarias
- Confianza > 65%
- Operaciones 20-30/hora
- Ganancias consistentes
- Sin rechazos por confianza baja

### Métricas de Riesgo
- Pérdida máxima < 10%
- Drawdown < 5%
- Cooldown respetado

---

## 📞 SOPORTE

Si algo falla:
1. Revisar logs completos
2. Comparar con RESUMEN_MEJORAS_IMPLEMENTADAS.md
3. Verificar que los cambios se aplicaron
4. Hacer git status para confirmar

---

**Documento creado**: Abril 5, 2026
**Versión**: V5-PRODUCTION
**Estado**: Listo para testing
