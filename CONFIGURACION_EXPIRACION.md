# ⏱️ Configuración de Tiempo de Expiración

## 🎯 Dos Modos Disponibles

### Modo 1: 🤖 Automático (IA Decide)

**Cómo funciona:**
- Groq analiza el mercado en tiempo real
- Recomienda el tiempo óptimo (1-5 minutos)
- Considera:
  - Volatilidad del mercado
  - Fuerza de la tendencia
  - Momentum
  - Condiciones actuales

**Ejemplo:**
```
⏱️ Groq analizando timing óptimo...
Momento óptimo: ✅ SÍ
Confianza: 85%
Expiración recomendada: 3 min  ← IA recomienda 3 minutos
Razón: Alta volatilidad requiere más tiempo

⏱️ Expiración automática: 3 min (recomendado por IA)
🚀 Ejecutando CALL en EURUSD-OTC
   Monto: $1.00
   Expiración: 3 min  ← Usa la recomendación
```

**Ventajas:**
- ✅ Adaptativo al mercado
- ✅ Optimiza según condiciones
- ✅ Mejor win rate

**Desventajas:**
- ⚠️ Tiempo variable (1-5 min)
- ⚠️ Requiere Groq API

---

### Modo 2: 👤 Manual (Usuario Decide)

**Cómo funciona:**
- Tú configuras el tiempo fijo (ej: 1 minuto)
- El bot SIEMPRE usa ese tiempo
- No importa lo que diga Groq

**Ejemplo:**
```
⏱️ Groq analizando timing óptimo...
Momento óptimo: ✅ SÍ
Confianza: 85%
Expiración recomendada: 3 min  ← Groq recomienda 3 min

⏱️ Expiración manual: 1 min (configurado por usuario)  ← Pero usa 1 min
🚀 Ejecutando CALL en EURUSD-OTC
   Monto: $1.00
   Expiración: 1 min  ← Siempre 1 minuto
```

**Ventajas:**
- ✅ Tiempo predecible
- ✅ Control total
- ✅ No depende de Groq

**Desventajas:**
- ⚠️ No se adapta al mercado
- ⚠️ Puede no ser óptimo

---

## 🔧 Cómo Configurar

### Opción A: Desde la GUI (Interfaz)

1. **Abrir el bot**
2. **Panel izquierdo** → Buscar sección "⏱️ Tiempo de Expiración"
3. **Seleccionar modo:**
   - 🤖 **Automático (IA decide 1-5 min)** ← Recomendado
   - 👤 **Manual:** [1-15 min] ← Para control total

**Captura de pantalla (conceptual):**
```
┌─────────────────────────────────┐
│ ⏱️ Tiempo de Expiración         │
├─────────────────────────────────┤
│ ⚪ 🤖 Automático (IA decide)    │
│ ⚫ 👤 Manual: [1] min           │
└─────────────────────────────────┘
```

### Opción B: Desde config.py

```python
# config.py

# Modo Automático (IA decide)
AUTO_EXPIRATION = True
MANUAL_EXPIRATION = 1  # No se usa en modo automático

# Modo Manual (siempre 1 minuto)
AUTO_EXPIRATION = False
MANUAL_EXPIRATION = 1  # Siempre usa 1 minuto
```

---

## 📊 Comparación

| Característica | Automático 🤖 | Manual 👤 |
|----------------|---------------|-----------|
| **Tiempo** | Variable (1-5 min) | Fijo (1-15 min) |
| **Adaptación** | ✅ Se adapta al mercado | ❌ Siempre igual |
| **Win Rate** | ✅ Optimizado | ⚠️ Depende del mercado |
| **Control** | ⚠️ IA decide | ✅ Usuario decide |
| **Requiere Groq** | ✅ Sí | ❌ No |

---

## 🎯 Recomendaciones

### Para Principiantes
**Usar Modo Automático** 🤖
- Deja que la IA optimice
- Mejor win rate
- Menos decisiones manuales

### Para Expertos
**Usar Modo Manual** 👤
- Control total
- Estrategia específica
- Backtesting con tiempo fijo

### Para Mercados Volátiles
**Usar Modo Automático** 🤖
- La IA ajusta el tiempo según volatilidad
- Mercado rápido → 1 min
- Mercado lento → 3-5 min

### Para Mercados Estables
**Usar Modo Manual (1 min)** 👤
- Mercado predecible
- Tiempo fijo funciona bien
- Más operaciones por hora

---

## 📈 Ejemplos de Uso

### Ejemplo 1: Mercado Volátil (Automático)

```
[10:00:00] 💎 Oportunidad detectada en EURUSD-OTC
[10:00:02] ⏱️ Groq: Alta volatilidad detectada
[10:00:02] Expiración recomendada: 5 min  ← Más tiempo por volatilidad
[10:00:02] ⏱️ Expiración automática: 5 min
[10:00:02] 🚀 Ejecutando CALL
[10:05:02] ✅ GANADA: +$0.85
```

### Ejemplo 2: Mercado Estable (Automático)

```
[11:00:00] 💎 Oportunidad detectada en GBPUSD-OTC
[11:00:02] ⏱️ Groq: Mercado estable, momentum fuerte
[11:00:02] Expiración recomendada: 1 min  ← Menos tiempo, mercado claro
[11:00:02] ⏱️ Expiración automática: 1 min
[11:00:02] 🚀 Ejecutando PUT
[11:01:02] ✅ GANADA: +$0.85
```

### Ejemplo 3: Estrategia Fija (Manual)

```
[12:00:00] 💎 Oportunidad detectada en AUDUSD-OTC
[12:00:02] ⏱️ Groq: Expiración recomendada: 3 min
[12:00:02] ⏱️ Expiración manual: 1 min  ← Ignora recomendación
[12:00:02] 🚀 Ejecutando CALL
[12:01:02] ✅ GANADA: +$0.85
```

---

## ⚙️ Configuración Avanzada

### Cambiar Rango de Expiración Automática

Por defecto, Groq recomienda entre 1-5 minutos. Para cambiar:

```python
# ai/llm_client.py
# Buscar: analyze_entry_timing()

# Cambiar rango
if volatility > 0.5:
    recommended_expiration = 7  # Cambiar de 5 a 7 min
elif volatility > 0.3:
    recommended_expiration = 5
else:
    recommended_expiration = 3  # Cambiar de 1 a 3 min
```

### Cambiar Rango Manual

Por defecto, puedes configurar 1-15 minutos. Para cambiar:

```python
# gui/modern_main_window.py
# Buscar: spin_manual_expiration

self.spin_manual_expiration.setRange(1, 30)  # Cambiar de 15 a 30 min
```

---

## 🐛 Solución de Problemas

### Problema 1: Siempre usa 1 minuto aunque esté en automático

**Causa:** Groq no está funcionando o no hay timing_analysis

**Solución:**
```python
# Verificar en el log:
⏱️ Groq analizando timing óptimo...
Momento óptimo: ✅ SÍ
Expiración recomendada: 3 min  ← Debe aparecer

# Si no aparece, verificar:
1. GROQ_API_KEY en .env
2. Modelo actualizado (llama-3.1-8b-instant)
3. Config.USE_LLM = True
```

### Problema 2: No puedo cambiar el tiempo manual

**Causa:** Modo automático está activado

**Solución:**
1. Seleccionar "👤 Manual" en la GUI
2. El campo se habilitará
3. Configurar el tiempo deseado

### Problema 3: El bot ignora mi configuración

**Causa:** Cambios en config.py no se aplican en tiempo real

**Solución:**
1. Cambiar desde la GUI (se aplica inmediatamente)
2. O reiniciar el bot después de editar config.py

---

## ✅ Resumen

**Modo Automático (Recomendado):**
- IA decide el tiempo óptimo (1-5 min)
- Mejor win rate
- Se adapta al mercado

**Modo Manual:**
- Usuario decide el tiempo fijo
- Control total
- Predecible

**Cómo cambiar:**
- Desde la GUI: Panel izquierdo → "⏱️ Tiempo de Expiración"
- Desde config.py: `AUTO_EXPIRATION = True/False`

**Estado actual:**
- Por defecto: Automático ✅
- Puedes cambiar en cualquier momento
- Los cambios se aplican inmediatamente
