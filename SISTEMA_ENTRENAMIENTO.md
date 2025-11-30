# 🤖 SISTEMA DE ENTRENAMIENTO DEL BOT

## 📚 ARQUITECTURA DEL SISTEMA

### 1. Componentes Principales

```
┌─────────────────────────────────────────────────────────┐
│                   BOT DE TRADING                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐    ┌──────────────┐                 │
│  │  Market Data │───▶│   Feature    │                 │
│  │   Handler    │    │  Engineer    │                 │
│  └──────────────┘    └──────┬───────┘                 │
│                              │                          │
│                              ▼                          │
│                      ┌──────────────┐                  │
│                      │   RL Agent   │                  │
│                      │    (PPO)     │                  │
│                      └──────┬───────┘                  │
│                              │                          │
│         ┌────────────────────┼────────────────┐        │
│         ▼                    ▼                 ▼        │
│  ┌──────────┐        ┌──────────┐      ┌──────────┐   │
│  │   Risk   │        │  Trade   │      │  Asset   │   │
│  │ Manager  │        │ Analyzer │      │ Manager  │   │
│  └──────────┘        └──────────┘      └──────────┘   │
│         │                    │                 │        │
│         └────────────────────┴─────────────────┘        │
│                              │                          │
│                              ▼                          │
│                      ┌──────────────┐                  │
│                      │   Broker     │                  │
│                      │   (Exnova)   │                  │
│                      └──────────────┘                  │
└─────────────────────────────────────────────────────────┘
```

## 🧠 AGENTE DE REINFORCEMENT LEARNING (RL)

### Algoritmo: PPO (Proximal Policy Optimization)
- **Ventajas:**
  - Estable y robusto
  - Eficiente en muestras
  - Funciona bien con espacios de acción discretos
  - Usado por OpenAI en proyectos exitosos

### Espacio de Acciones
```python
0 = HOLD   # No hacer nada
1 = CALL   # Comprar (precio subirá)
2 = PUT    # Vender (precio bajará)
```

### Espacio de Observaciones
Ventana de 10 velas con indicadores:
- **Precio:** open, high, low, close, volume
- **Indicadores técnicos:**
  - RSI (14 períodos)
  - MACD (12, 26, 9)
  - Bollinger Bands (20, 2)
  - SMA (20, 50)
  - ATR (14)
- **Patrones de velas:**
  - Hammer
  - Bullish Engulfing

### Sistema de Recompensas
```python
# Operación ganada
reward = monto * 0.85  # 85% de retorno

# Operación perdida
reward = -monto

# Hold (no operar)
reward = 0
```

## 📊 FEATURE ENGINEERING

### Indicadores Técnicos Implementados

1. **RSI (Relative Strength Index)**
   - Identifica sobrecompra/sobreventa
   - Rango: 0-100
   - Señales: <30 sobreventa, >70 sobrecompra

2. **MACD (Moving Average Convergence Divergence)**
   - Detecta cambios de tendencia
   - Componentes: MACD, Signal, Histogram

3. **Bollinger Bands**
   - Mide volatilidad
   - Identifica breakouts

4. **SMA (Simple Moving Averages)**
   - Identifica tendencias
   - Períodos: 20 y 50

5. **ATR (Average True Range)**
   - Mide volatilidad del mercado

6. **Patrones de Velas**
   - Hammer (alcista)
   - Bullish Engulfing (alcista)

## 🎯 GESTIÓN DE RIESGO INTELIGENTE

### 1. Martingala Inteligente

**NO es martingala tradicional** (que duplica ciegamente).

Es un sistema que analiza **POR QUÉ** se perdió:

```python
# Análisis post-pérdida
if perdida:
    analisis = TradeAnalyzer.analyze_loss(
        entry_candle,
        exit_candle,
        direction,
        subsequent_candles
    )
    
    if analisis['should_martingale']:
        # Solo aplicar si fue error de timing
        # NO si fue cambio de tendencia
        aplicar_martingale()
    else:
        # Resetear y esperar mejor momento
        reset()
```

### Criterios para Aplicar Martingala

✅ **SÍ aplicar si:**
- Error de timing (precio se movió a favor después)
- Pérdida pequeña (ruido de mercado)
- Volatilidad normal

❌ **NO aplicar si:**
- Cambio de tendencia fuerte
- Pérdida grande
- Señales contradictorias

### Límites de Seguridad

```python
max_martingale_steps = 3      # Máximo 3 niveles
martingale_multiplier = 2.2   # 2.2x (no 2x)
stop_loss_daily = 5%          # Pérdida máxima diaria
take_profit_daily = 10%       # Ganancia objetivo diaria
```

## 🔄 PROCESO DE ENTRENAMIENTO

### Fase 1: Recolección de Datos
```python
# Obtener datos históricos
df = market_data.get_candles(
    asset="EURUSD-OTC",
    timeframe=60,  # 1 minuto
    num_candles=1000
)
```

### Fase 2: Procesamiento
```python
# Calcular indicadores
df = feature_engineer.prepare_for_rl(df)

# Resultado: DataFrame con ~17 columnas
# [open, high, low, close, volume, rsi, macd, ...]
```

### Fase 3: Creación del Entorno
```python
# Crear entorno de simulación
env = BinaryOptionsEnv(
    df=df,
    window_size=10,
    initial_balance=1000
)
```

### Fase 4: Entrenamiento
```python
# Crear/cargar modelo
model = PPO("MlpPolicy", env, verbose=1)

# Entrenar
model.learn(total_timesteps=10000)

# Guardar
model.save("models/rl_agent")
```

### Fase 5: Validación
```python
# Probar en datos nuevos
obs = env.reset()
for _ in range(100):
    action, _ = model.predict(obs)
    obs, reward, done, _, info = env.step(action)
    if done:
        break
```

## 🚀 AUTO-ENTRENAMIENTO

El bot puede **re-entrenarse automáticamente** con datos recientes:

```python
auto_trainer = AutoTrainer(market_data, feature_engineer)

# Re-entrenar con datos de las últimas 24 horas
auto_trainer.train_on_recent_data(
    asset="EURUSD-OTC",
    num_candles=1440  # 24 horas en velas de 1 min
)
```

**Ventajas:**
- Se adapta a condiciones cambiantes del mercado
- Aprende de errores recientes
- Mejora continuamente

## 📈 ESTRATEGIAS IMPLEMENTADAS

### 1. Estrategia RL Pura
- Solo usa predicciones del agente RL
- Rápida y eficiente
- Requiere buen entrenamiento

### 2. Estrategia RL + Indicadores
- Combina RL con señales técnicas
- Más conservadora
- Mejor para mercados volátiles

### 3. Estrategia RL + LLM
- Usa Groq AI para análisis adicional
- Considera noticias y contexto
- Más lenta pero más informada

### 4. Estrategia Híbrida (RECOMENDADA)
```python
# Combina todo
decision_rl = agent.predict(obs)
decision_indicators = analyze_indicators(df)
decision_llm = llm_client.get_advice(df, news)

# Voto mayoritario o ponderado
final_decision = combine_decisions(
    decision_rl,
    decision_indicators,
    decision_llm
)
```

## 🎓 PROCESO DE APRENDIZAJE

### Ciclo de Mejora Continua

```
1. OPERAR
   ↓
2. REGISTRAR RESULTADO
   ↓
3. ANALIZAR (¿Por qué ganó/perdió?)
   ↓
4. AJUSTAR ESTRATEGIA
   ↓
5. RE-ENTRENAR
   ↓
(volver a 1)
```

### Métricas de Rendimiento

```python
# Métricas clave
win_rate = wins / total_trades
profit_factor = total_wins / total_losses
sharpe_ratio = mean_return / std_return
max_drawdown = max_consecutive_losses
```

## 🔧 CONFIGURACIÓN ÓPTIMA

### Para Principiantes
```python
CAPITAL_PER_TRADE = 1.0      # Empezar pequeño
STOP_LOSS_PCT = 0.03         # 3% pérdida máxima
TAKE_PROFIT_PCT = 0.05       # 5% ganancia objetivo
TIMEFRAME = 60               # 1 minuto
USE_MARTINGALE = False       # Desactivar al inicio
```

### Para Avanzados
```python
CAPITAL_PER_TRADE = 5.0      # Mayor capital
STOP_LOSS_PCT = 0.05         # 5% pérdida máxima
TAKE_PROFIT_PCT = 0.10       # 10% ganancia objetivo
TIMEFRAME = 60               # 1 minuto
USE_MARTINGALE = True        # Martingala inteligente
MAX_MARTINGALE_STEPS = 3     # Máximo 3 niveles
```

## 📝 COMANDOS DE ENTRENAMIENTO

### Entrenar desde cero
```bash
python train_bot.py --asset EURUSD-OTC --timesteps 10000
```

### Re-entrenar con datos recientes
```bash
python train_bot.py --retrain --days 7
```

### Backtesting
```bash
python backtest.py --asset EURUSD-OTC --days 30
```

### Optimizar hiperparámetros
```bash
python optimize.py --trials 100
```

## ⚠️ ADVERTENCIAS IMPORTANTES

1. **El bot NO es infalible**
   - Trading es inherentemente riesgoso
   - Pérdidas son parte del proceso

2. **Requiere entrenamiento adecuado**
   - Mínimo 1000 velas de datos
   - Preferible 10,000+ para mejor rendimiento

3. **Monitoreo constante**
   - Revisar métricas diariamente
   - Ajustar parámetros según resultados

4. **Empezar en DEMO**
   - Probar estrategias sin riesgo
   - Validar rendimiento antes de usar dinero real

5. **Diversificación**
   - No operar solo un activo
   - Distribuir riesgo entre varios pares

## 🎯 PRÓXIMOS PASOS

1. ✅ Sistema base implementado
2. ⏳ Entrenar modelo con datos históricos
3. ⏳ Validar en cuenta DEMO
4. ⏳ Optimizar hiperparámetros
5. ⏳ Implementar backtesting avanzado
6. ⏳ Añadir más estrategias
7. ⏳ Integrar análisis de sentimiento
8. ⏳ Dashboard de métricas en tiempo real
