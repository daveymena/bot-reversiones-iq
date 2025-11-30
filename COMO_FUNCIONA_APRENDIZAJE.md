# 🧠 CÓMO FUNCIONA EL APRENDIZAJE DEL BOT

## 🎯 Concepto Simple

El bot tiene **2 tipos de aprendizaje**:

### 1. 📚 Entrenamiento Inicial (Offline)
- Se hace **UNA VEZ** al principio
- Usa datos históricos del broker
- Crea el modelo base

### 2. 🔄 Aprendizaje Continuo (Online)
- Se hace **AUTOMÁTICAMENTE** mientras opera
- Aprende de **CADA operación real**
- Mejora constantemente

---

## 📚 ENTRENAMIENTO INICIAL

### ¿Cuándo?
```
Primera vez que usas el bot
O cuando quieres "resetear" el aprendizaje
```

### ¿Cómo funciona?

```
┌─────────────────────────────────────────────────────────────┐
│                  ENTRENAMIENTO INICIAL                      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  1. Descargar datos históricos del broker                   │
│     └─ Ejemplo: 1000 velas de EURUSD-OTC                    │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  2. Calcular indicadores técnicos                           │
│     ├─ RSI                                                  │
│     ├─ MACD                                                 │
│     ├─ Bollinger Bands                                      │
│     ├─ ATR                                                  │
│     └─ 13 indicadores más...                                │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  3. Crear entorno de simulación                             │
│     └─ Simula trading con esos datos                        │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  4. Entrenar agente RL (Reinforcement Learning)             │
│                                                             │
│     El agente prueba miles de operaciones:                  │
│     ├─ Intenta CALL → Gana/Pierde → Aprende                │
│     ├─ Intenta PUT → Gana/Pierde → Aprende                 │
│     ├─ Intenta HOLD → No opera → Aprende                   │
│     └─ Repite 10,000 veces                                  │
│                                                             │
│     Aprende:                                                │
│     ✅ Cuándo hacer CALL                                     │
│     ✅ Cuándo hacer PUT                                      │
│     ✅ Cuándo NO operar (HOLD)                              │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  5. Guardar modelo entrenado                                │
│     └─ models/ppo_trading_agent.zip                         │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
                    ✅ LISTO PARA OPERAR
```

### Ejemplo en la Interfaz

```
[Tab Entrenamiento]

Activo: EURUSD-OTC
Velas: 1000
Timesteps: 10000

[Entrenar Modelo] ← Click aquí

Logs:
✅ Conectado a Exnova
📊 Descargando 1000 velas...
✅ 1000 velas obtenidas
📊 Calculando indicadores...
✅ 17 indicadores calculados
🎓 Entrenando agente RL...
  [████████████████████] 100% | 10000/10000
✅ Entrenamiento completado
💾 Modelo guardado
```

---

## 🔄 APRENDIZAJE CONTINUO

### ¿Cuándo?
```
SIEMPRE que el bot opera en REAL
Automático, no requiere intervención
```

### ¿Cómo funciona?

```
╔═════════════════════════════════════════════════════════════╗
║              CICLO DE APRENDIZAJE CONTINUO                  ║
╚═════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────┐
│  OPERACIÓN #1                                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. ANTES de operar:                                        │
│     ├─ Captura estado del mercado                          │
│     │  └─ RSI: 28, MACD: 0.05, Precio: 1.15234            │
│     └─ Guarda en memoria                                    │
│                                                             │
│  2. EJECUTA operación REAL:                                 │
│     └─ CALL $10 en GBPUSD-OTC                              │
│                                                             │
│  3. ESPERA resultado (60 segundos)                          │
│                                                             │
│  4. OBTIENE resultado de Exnova:                            │
│     └─ ✅ GANÓ: +$8.50                                      │
│                                                             │
│  5. DESPUÉS de operar:                                      │
│     ├─ Captura nuevo estado del mercado                    │
│     │  └─ RSI: 32, MACD: 0.06, Precio: 1.15389            │
│     └─ Guarda en memoria                                    │
│                                                             │
│  6. GUARDA EXPERIENCIA COMPLETA:                            │
│     {                                                       │
│       estado_antes: [RSI:28, MACD:0.05, ...],              │
│       accion: CALL,                                         │
│       resultado: +$8.50,                                    │
│       estado_despues: [RSI:32, MACD:0.06, ...],            │
│       metadata: {activo: "GBPUSD-OTC", ganó: true}         │
│     }                                                       │
│                                                             │
│  📝 Experiencia #1 guardada                                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  OPERACIONES #2 a #99                                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Cada operación:                                            │
│  ├─ Guarda su experiencia                                  │
│  ├─ Acumula en el buffer                                   │
│  └─ Continúa operando                                       │
│                                                             │
│  📝 99 experiencias acumuladas                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  OPERACIÓN #100 → TRIGGER RE-ENTRENAMIENTO                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  🎓 INICIANDO RE-ENTRENAMIENTO AUTOMÁTICO                   │
│                                                             │
│  1. Cargar experiencias reales:                             │
│     └─ Últimas 500 operaciones                             │
│                                                             │
│  2. Descargar datos frescos:                                │
│     └─ 1000 velas recientes de Exnova                      │
│                                                             │
│  3. Calcular indicadores:                                   │
│     └─ RSI, MACD, BB, etc.                                 │
│                                                             │
│  4. Re-entrenar modelo:                                     │
│     ├─ Usa experiencias REALES                             │
│     ├─ Usa datos FRESCOS                                   │
│     └─ 2000 pasos de entrenamiento                         │
│                                                             │
│  5. Guardar modelo actualizado:                             │
│     └─ Sobrescribe modelo anterior                         │
│                                                             │
│  ✅ RE-ENTRENAMIENTO COMPLETADO                             │
│                                                             │
│  📊 Estadísticas:                                           │
│     Total: 100 operaciones                                  │
│     Ganadas: 58                                             │
│     Perdidas: 42                                            │
│     Win Rate: 58%                                           │
│     Profit: +$45.50                                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  OPERACIÓN #101                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ✨ Ahora usa el MODELO MEJORADO                            │
│                                                             │
│  El modelo aprendió de:                                     │
│  ✅ 100 operaciones reales                                  │
│  ✅ Resultados reales de Exnova                             │
│  ✅ Condiciones reales del mercado                          │
│                                                             │
│  Continúa operando...                                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘

                    ⬇️ CICLO SE REPITE ⬇️

┌─────────────────────────────────────────────────────────────┐
│  OPERACIÓN #200 → RE-ENTRENAMIENTO                          │
│  OPERACIÓN #300 → RE-ENTRENAMIENTO                          │
│  OPERACIÓN #400 → RE-ENTRENAMIENTO                          │
│  ...                                                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 🗄️ ALMACENAMIENTO DE EXPERIENCIAS

### Archivo: `data/experiences.json`

```json
[
  {
    "timestamp": "2025-11-24T14:23:45",
    "state": [28.5, 0.05, 1.15234, ...],
    "action": 1,  // CALL
    "reward": 8.50,  // Ganó $8.50
    "next_state": [32.1, 0.06, 1.15389, ...],
    "done": false,
    "metadata": {
      "asset": "GBPUSD-OTC",
      "entry_price": 1.15234,
      "exit_price": 1.15389,
      "won": true
    }
  },
  {
    "timestamp": "2025-11-24T14:26:30",
    "state": [72.3, -0.03, 1.15401, ...],
    "action": 2,  // PUT
    "reward": -10.00,  // Perdió $10.00
    "next_state": [68.9, -0.04, 1.15456, ...],
    "done": false,
    "metadata": {
      "asset": "GBPUSD-OTC",
      "entry_price": 1.15401,
      "exit_price": 1.15456,
      "won": false
    }
  }
  // ... hasta 10,000 experiencias
]
```

### Características

- ✅ **Persistente**: Se guarda en disco
- ✅ **Automático**: Guarda cada 10 operaciones
- ✅ **Limitado**: Máximo 10,000 (las más recientes)
- ✅ **Legible**: Formato JSON
- ✅ **Portable**: Puedes copiar/compartir

---

## 🧠 QUÉ APRENDE EL BOT

### De Cada Operación Aprende:

```
┌─────────────────────────────────────────────────────────────┐
│  SITUACIÓN                                                  │
├─────────────────────────────────────────────────────────────┤
│  RSI: 28 (sobreventa)                                       │
│  MACD: 0.05 (alcista)                                       │
│  Precio: En BB inferior                                     │
│  Tendencia: Alcista                                         │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  ACCIÓN TOMADA                                              │
├─────────────────────────────────────────────────────────────┤
│  CALL                                                       │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  RESULTADO                                                  │
├─────────────────────────────────────────────────────────────┤
│  ✅ GANÓ +$8.50                                             │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  APRENDIZAJE                                                │
├─────────────────────────────────────────────────────────────┤
│  "Cuando RSI < 30 + MACD alcista + BB inferior              │
│   → CALL es buena decisión"                                 │
│                                                             │
│  Refuerza esta estrategia en el modelo                      │
└─────────────────────────────────────────────────────────────┘
```

### Aprende Patrones Como:

1. **Reversiones en Soportes**
   ```
   RSI < 30 + Precio en soporte → CALL funciona bien
   ```

2. **Reversiones en Resistencias**
   ```
   RSI > 70 + Precio en resistencia → PUT funciona bien
   ```

3. **Continuación de Tendencia**
   ```
   Tendencia fuerte + MACD alineado → Seguir tendencia
   ```

4. **Cuándo NO Operar**
   ```
   Señales mixtas + Volatilidad baja → HOLD es mejor
   ```

---

## 📊 MONITOREO DEL APRENDIZAJE

### En la Interfaz

```
[Tab Análisis]

╔═══════════════════════════════════════════════════════════╗
║           ESTADÍSTICAS DE APRENDIZAJE                     ║
╠═══════════════════════════════════════════════════════════╣
║                                                           ║
║  Total Experiencias: 250                                  ║
║  Operaciones Ganadas: 145                                 ║
║  Operaciones Perdidas: 105                                ║
║  Win Rate: 58%                                            ║
║  Profit Total: +$67.50                                    ║
║                                                           ║
║  Último Re-entrenamiento: Hace 50 operaciones             ║
║  Próximo Re-entrenamiento: En 50 operaciones              ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
```

### En los Logs

```
[14:23:45] 📝 Experiencia guardada para aprendizaje continuo
[14:23:45] ✅ 100 experiencias guardadas

[14:25:30] 🎓 Iniciando re-entrenamiento con 100 experiencias reales...
[14:27:15] ✅ Re-entrenamiento completado
[14:27:16] 📊 Win Rate: 58.0% | Profit: $45.50
```

---

## ⚙️ CONFIGURACIÓN

### Frecuencia de Re-entrenamiento

En `core/continuous_learner.py`:

```python
# Re-entrenar cada 100 operaciones (por defecto)
retrain_frequency = 100

# Cambiar a cada 50 operaciones (más frecuente)
retrain_frequency = 50

# Cambiar a cada 200 operaciones (menos frecuente)
retrain_frequency = 200
```

### Pasos de Re-entrenamiento

```python
# 2000 pasos por defecto (~2 minutos)
retrain_timesteps = 2000

# Más rápido pero menos preciso
retrain_timesteps = 1000

# Más lento pero más preciso
retrain_timesteps = 5000
```

### Mínimo de Experiencias

```python
# Mínimo 50 experiencias para empezar
min_experiences_to_train = 50

# Cambiar a 100 (más conservador)
min_experiences_to_train = 100
```

---

## 🎯 MEJORES PRÁCTICAS

### 1. Fase Inicial (Primeras 50 operaciones)
```
✅ Dejar que acumule experiencias
✅ No re-entrenar todavía
✅ Observar patrones
✅ Monitorear win rate
```

### 2. Fase de Aprendizaje (50-500 operaciones)
```
✅ Re-entrenamientos automáticos cada 100
✅ Observar mejora en win rate
✅ Ajustar parámetros si es necesario
✅ Guardar backups del modelo
```

### 3. Fase Madura (500+ operaciones)
```
✅ Modelo bien entrenado
✅ Win rate estable
✅ Continuar aprendiendo
✅ Monitorear cambios en el mercado
```

---

## 📈 EVOLUCIÓN DEL WIN RATE

```
Operaciones    Win Rate    Estado
─────────────────────────────────────────────────────
0-50           50-55%      Modelo inicial
50-100         52-58%      Primer re-entrenamiento
100-200        55-60%      Aprendiendo patrones
200-500        58-65%      Modelo maduro
500+           60-70%      Modelo experto
```

---

## ✅ RESUMEN

### Entrenamiento Inicial
- ✅ Una vez al principio
- ✅ Usa datos históricos
- ✅ Crea modelo base
- ✅ ~10 minutos

### Aprendizaje Continuo
- ✅ Automático mientras opera
- ✅ Aprende de operaciones reales
- ✅ Re-entrena cada 100 operaciones
- ✅ Mejora constantemente

### Resultado
- ✅ Bot que aprende de sus errores
- ✅ Se adapta al mercado
- ✅ Mejora con el tiempo
- ✅ No se queda obsoleto

---

**🧠 ¡El bot tiene memoria y aprende de cada operación! 📈**
