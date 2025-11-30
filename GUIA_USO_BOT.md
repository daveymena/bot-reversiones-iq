# 🚀 GUÍA DE USO DEL BOT DE TRADING

## 📋 INICIO RÁPIDO

### 1. Iniciar la Interfaz
```bash
python main_modern.py
```

### 2. Conectarse al Broker

**Panel Izquierdo - Conexión:**
1. Broker: **Exnova** (recomendado)
2. Email: `daveymena16@gmail.com`
3. Password: `6715320Dvd.`
4. Cuenta: **PRACTICE** (para pruebas)
5. Click: **🔌 CONECTAR**

**Resultado esperado:**
```
✅ Conectado a EXNOVA
💰 Balance: $9,543.67 (PRACTICE)
```

### 3. Entrenar el Modelo RL

**Panel Derecho - Tab "🎓 Entrenamiento":**

1. **Configuración:**
   - Velas: `2000` (recomendado para inicio)
   - Timesteps: `10000` (más = mejor, pero más lento)

2. **Click: 🎓 ENTRENAR MODELO**

3. **Esperar:** El proceso toma 2-5 minutos

4. **Resultado esperado:**
   ```
   ✅ Modelo Entrenado
   Entrenado con 1950 velas
   ```

### 4. Configurar Estrategias

**Panel Derecho - Tab "🎯 Estrategias":**

✅ Activar:
- 🤖 Reinforcement Learning
- 📊 Martingala Inteligente
- 🧠 Análisis LLM (Groq)

⚙️ Configurar Riesgo:
- Stop Loss: `5%`
- Take Profit: `10%`
- Max Martingala: `3`

### 5. Iniciar el Bot

**Panel Central - Botones de Trading:**

1. **Click: ▶️ INICIAR BOT**

2. **El bot comenzará a:**
   - Analizar el mercado
   - Calcular indicadores
   - Consultar IA
   - Tomar decisiones
   - Ejecutar operaciones

3. **Monitorear en:**
   - Logs del Sistema
   - Panel de Análisis
   - Historial de Operaciones

## 📊 ENTENDIENDO LA INTERFAZ

### Panel Izquierdo: Control

```
┌─────────────────────────┐
│  🤖 Trading Bot         │
├─────────────────────────┤
│  📡 Conexión            │
│  • Broker               │
│  • Credenciales         │
│  • Tipo de cuenta       │
├─────────────────────────┤
│  📊 Activo              │
│  • Par de divisas       │
│  • OTC 24/7             │
├─────────────────────────┤
│  💰 Trading             │
│  • Monto por operación  │
│  • Duración             │
└─────────────────────────┘
```

### Panel Central: Trading

```
┌─────────────────────────────────────┐
│  💰 Balance  📊 Profit  🎯 Win Rate │
├─────────────────────────────────────┤
│                                     │
│         📈 GRÁFICO                  │
│      (Tiempo Real)                  │
│                                     │
├─────────────────────────────────────┤
│  📈 CALL  ▶️ BOT  📉 PUT           │
├─────────────────────────────────────┤
│  📝 Logs del Sistema                │
│  • Conexiones                       │
│  • Operaciones                      │
│  • Resultados                       │
└─────────────────────────────────────┘
```

### Panel Derecho: Análisis

**Tab 1: 🎯 Estrategias**
- Activar/desactivar estrategias
- Configurar gestión de riesgo
- Ver indicadores en tiempo real

**Tab 2: 🎓 Entrenamiento**
- Estado del modelo RL
- Entrenar/re-entrenar
- Ver métricas de entrenamiento

**Tab 3: 📊 Análisis**
- Estadísticas de trading
- Estado de martingala
- Señales y recomendaciones
- Historial de operaciones

## 🎯 ESTRATEGIAS DE USO

### Modo Conservador (Principiantes)

```python
Configuración:
• Monto: $1
• Stop Loss: 3%
• Take Profit: 5%
• Martingala: Desactivada
• Solo RL: Activado
```

**Características:**
- Bajo riesgo
- Operaciones selectivas
- Ideal para aprender

### Modo Balanceado (Recomendado)

```python
Configuración:
• Monto: $1-2
• Stop Loss: 5%
• Take Profit: 10%
• Martingala: Activada (Max 3)
• RL + Indicadores + LLM
```

**Características:**
- Riesgo moderado
- Mejor rendimiento
- Recuperación inteligente

### Modo Agresivo (Avanzados)

```python
Configuración:
• Monto: $5+
• Stop Loss: 10%
• Take Profit: 20%
• Martingala: Activada (Max 5)
• Todas las estrategias
```

**Características:**
- Alto riesgo/recompensa
- Requiere capital mayor
- Monitoreo constante

## 📈 INTERPRETANDO RESULTADOS

### Indicadores Técnicos

**RSI (Relative Strength Index):**
- `< 30`: 🟢 Sobreventa (posible CALL)
- `30-70`: ⚪ Neutral
- `> 70`: 🔴 Sobrecompra (posible PUT)

**MACD:**
- `Positivo`: 🟢 Tendencia alcista
- `Negativo`: 🔴 Tendencia bajista
- `Cruce`: ⚡ Cambio de tendencia

**Bollinger Bands:**
- `Precio en banda inferior`: 🟢 Posible rebote
- `Precio en banda superior`: 🔴 Posible caída
- `Bandas estrechas`: ⚡ Volatilidad próxima

### Señales del Bot

```
🤖 RL predice: CALL
📊 RSI: 28 (Sobreventa)
📈 MACD: Cruce alcista
🧠 LLM: Tendencia alcista confirmada
✅ DECISIÓN: CALL
```

### Martingala Inteligente

**Nivel 0:** Operación normal ($1)
**Nivel 1:** Primera pérdida ($2.20)
**Nivel 2:** Segunda pérdida ($4.84)
**Nivel 3:** Tercera pérdida ($10.65)

**El bot NO aplica martingala si:**
- Cambio de tendencia fuerte
- Señales contradictorias
- Límite alcanzado

## 🔄 MANTENIMIENTO

### Re-entrenamiento Diario

**Recomendado:** Re-entrenar cada 24 horas

1. Click: **🔄 RE-ENTRENAR**
2. Usa datos de las últimas 24 horas
3. Adapta el modelo a condiciones actuales

### Optimización de Parámetros

**Si Win Rate < 50%:**
- Aumentar timesteps de entrenamiento
- Usar más velas históricas
- Ajustar stop loss/take profit

**Si Win Rate > 60%:**
- Aumentar monto por operación
- Activar martingala
- Operar más activos

### Backtesting

```bash
# Probar estrategia en datos históricos
python backtest.py --asset EURUSD-OTC --days 30
```

## ⚠️ ADVERTENCIAS

### 🔴 NUNCA:
- Operar con dinero que no puedes perder
- Ignorar el stop loss
- Operar sin entrenar el modelo
- Usar cuenta REAL sin probar en DEMO
- Dejar el bot sin supervisión

### 🟢 SIEMPRE:
- Empezar en cuenta PRACTICE
- Monitorear resultados
- Ajustar parámetros según rendimiento
- Hacer backups del modelo entrenado
- Diversificar activos

## 🆘 SOLUCIÓN DE PROBLEMAS

### "No se pudo conectar"
```
Solución:
1. Verificar credenciales en .env
2. Verificar conexión a internet
3. Probar con otro broker
```

### "Modelo no entrenado"
```
Solución:
1. Ir a tab "Entrenamiento"
2. Click "ENTRENAR MODELO"
3. Esperar a que termine
```

### "Error obteniendo datos"
```
Solución:
1. Verificar que estás conectado
2. Probar con otro activo
3. Verificar que el mercado está abierto
```

### "Win Rate muy bajo"
```
Solución:
1. Re-entrenar con más datos
2. Aumentar timesteps
3. Ajustar parámetros de riesgo
4. Probar otros activos
```

## 📞 SOPORTE

### Logs del Sistema
Todos los eventos se registran en el panel de logs.
Útil para debugging.

### Archivos de Configuración
- `.env`: Credenciales
- `config.py`: Parámetros del bot
- `models/rl_agent.zip`: Modelo entrenado

### Comandos Útiles

```bash
# Entrenar desde terminal
python train_bot.py --asset EURUSD-OTC --timesteps 10000

# Test de conexión
python test_exnova_completo.py

# Demo de operación
python demo_operacion_exnova.py
```

## 🎓 RECURSOS ADICIONALES

- `SISTEMA_ENTRENAMIENTO.md`: Detalles técnicos
- `RESUMEN_PRUEBAS_FINAL.md`: Estado del sistema
- `CONFLICTO_WEBSOCKET.md`: Info sobre brokers

## 🚀 PRÓXIMOS PASOS

1. ✅ Conectar y entrenar
2. ⏳ Operar en DEMO por 1 semana
3. ⏳ Analizar resultados
4. ⏳ Optimizar parámetros
5. ⏳ Considerar cuenta REAL (con precaución)

---

**¡Buena suerte con tu trading! 🚀📈**
