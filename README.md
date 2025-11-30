# 🤖 BOT DE TRADING PROFESIONAL CON IA

Bot de trading automático para opciones binarias con Reinforcement Learning, Martingala Inteligente y análisis de IA.

## 🌟 CARACTERÍSTICAS

### 🧠 Inteligencia Artificial
- **Reinforcement Learning (PPO)**: Agente entrenado con datos históricos
- **Análisis LLM (Groq)**: Consulta a IA generativa para decisiones informadas
- **Auto-entrenamiento**: Se adapta automáticamente a condiciones del mercado

### 📊 Análisis Técnico Avanzado
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- Bollinger Bands
- SMA (Simple Moving Averages)
- ATR (Average True Range)
- Patrones de velas (Hammer, Bullish Engulfing)

### 💰 Gestión de Riesgo Inteligente
- **Martingala Inteligente**: NO duplica ciegamente, analiza por qué se perdió
- Stop Loss y Take Profit configurables
- Límites de martingala (máximo 3 niveles)
- Análisis post-trade para decisiones informadas

### 🎯 Múltiples Estrategias
- RL puro
- RL + Indicadores técnicos
- RL + LLM
- Estrategia híbrida (recomendada)

### 🌐 Brokers Soportados
- ✅ **Exnova** (Recomendado - 100% funcional)
- ⚠️ **IQ Option** (Conflicto de versiones de websocket)

### 📈 Activos Disponibles
- **OTC (24/7)**: EURUSD-OTC, GBPUSD-OTC, USDJPY-OTC, etc.
- **Normales**: EURUSD, GBPUSD, USDJPY, etc.
- **Total**: 252 activos disponibles

## 🚀 INICIO RÁPIDO

### 1. Instalación

```bash
# Clonar repositorio
git clone <repo-url>
cd trading-bot

# Instalar dependencias
pip install -r requirements.txt

# Configurar credenciales
cp .env.example .env
# Editar .env con tus credenciales
```

### 2. Configuración

Edita `.env`:
```env
EXNOVA_EMAIL=tu@email.com
EXNOVA_PASSWORD=tupassword
GROQ_API_KEY=tu_api_key
BROKER_NAME=exnova
```

### 3. Entrenar el Modelo

```bash
# Entrenar con datos históricos
python train_bot.py --asset EURUSD-OTC --timesteps 10000

# O usar la interfaz gráfica (Tab "Entrenamiento")
python main_modern.py
```

### 4. Iniciar el Bot

```bash
# Interfaz moderna
python main_modern.py

# O interfaz clásica
python main.py
```

## 📖 DOCUMENTACIÓN

### Guías Principales
- 📘 [**GUIA_USO_BOT.md**](GUIA_USO_BOT.md) - Guía completa de uso
- 🎓 [**SISTEMA_ENTRENAMIENTO.md**](SISTEMA_ENTRENAMIENTO.md) - Detalles del sistema de RL
- 📊 [**ACTIVOS_OTC_VS_NORMALES.md**](ACTIVOS_OTC_VS_NORMALES.md) - Diferencias entre activos

### Documentos Técnicos
- 🔧 [**SOLUCION_IQ_OPTION.md**](SOLUCION_IQ_OPTION.md) - Problemas resueltos de IQ Option
- ⚠️ [**CONFLICTO_WEBSOCKET.md**](CONFLICTO_WEBSOCKET.md) - Info sobre versiones de websocket
- ✅ [**RESUMEN_PRUEBAS_FINAL.md**](RESUMEN_PRUEBAS_FINAL.md) - Estado del sistema

## 🎮 USO DE LA INTERFAZ

### Panel Izquierdo: Conexión
1. Seleccionar broker (Exnova recomendado)
2. Ingresar credenciales
3. Seleccionar tipo de cuenta (PRACTICE/REAL)
4. Click en "CONECTAR"

### Panel Central: Trading
- **Gráfico en tiempo real**: Visualiza el mercado
- **Botones de trading**: CALL, PUT, INICIAR BOT
- **Logs del sistema**: Monitorea todas las acciones

### Panel Derecho: Análisis y Control

**Tab 1: 🎯 Estrategias**
- Activar/desactivar estrategias
- Configurar gestión de riesgo
- Ver indicadores en tiempo real

**Tab 2: 🎓 Entrenamiento**
- Entrenar modelo RL
- Re-entrenar con datos recientes
- Ver métricas de entrenamiento

**Tab 3: 📊 Análisis**
- Estadísticas de trading
- Estado de martingala
- Historial de operaciones

## 📊 ARQUITECTURA DEL SISTEMA

```
┌─────────────────────────────────────────────────────────┐
│                   BOT DE TRADING                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Market Data ──▶ Feature Engineer ──▶ RL Agent         │
│       │                                    │            │
│       │                                    ▼            │
│       │                            ┌──────────────┐    │
│       │                            │  Strategies  │    │
│       │                            └──────┬───────┘    │
│       │                                   │            │
│       ▼                                   ▼            │
│  ┌──────────┐  ┌──────────┐      ┌──────────┐        │
│  │   Risk   │  │  Trade   │      │  Asset   │        │
│  │ Manager  │  │ Analyzer │      │ Manager  │        │
│  └────┬─────┘  └────┬─────┘      └────┬─────┘        │
│       │             │                   │              │
│       └─────────────┴───────────────────┘              │
│                     │                                  │
│                     ▼                                  │
│              ┌──────────────┐                         │
│              │   Broker     │                         │
│              │   (Exnova)   │                         │
│              └──────────────┘                         │
└─────────────────────────────────────────────────────────┘
```

## 🧪 PRUEBAS Y DIAGNÓSTICO

### Probar Conexión
```bash
# Exnova
python test_exnova_completo.py

# IQ Option
python diagnostico_iq.py
```

### Verificar Activos
```bash
python test_activos_disponibles.py
```

### Demo de Operación
```bash
# Exnova
python demo_operacion_exnova.py

# IQ Option
python demo_operacion_real.py
```

### Test Completo del Bot
```bash
python test_bot_completo.py
```

## 📈 ESTRATEGIAS DE TRADING

### Modo Conservador (Principiantes)
```python
CAPITAL_PER_TRADE = 1.0
STOP_LOSS_PCT = 0.03
TAKE_PROFIT_PCT = 0.05
USE_MARTINGALE = False
```

### Modo Balanceado (Recomendado)
```python
CAPITAL_PER_TRADE = 1.0
STOP_LOSS_PCT = 0.05
TAKE_PROFIT_PCT = 0.10
USE_MARTINGALE = True
MAX_MARTINGALE_STEPS = 3
```

### Modo Agresivo (Avanzados)
```python
CAPITAL_PER_TRADE = 5.0
STOP_LOSS_PCT = 0.10
TAKE_PROFIT_PCT = 0.20
USE_MARTINGALE = True
MAX_MARTINGALE_STEPS = 5
```

## 🔧 CONFIGURACIÓN AVANZADA

### config.py
```python
# Broker
BROKER_NAME = "exnova"  # o "iq"

# Trading
CAPITAL_PER_TRADE = 1.0
STOP_LOSS_PCT = 0.05
TAKE_PROFIT_PCT = 0.10
TIMEFRAME = 60  # segundos

# RL
TIMESTEPS = 10000
MODEL_PATH = "models/rl_agent"

# LLM
USE_LLM = True
GROQ_API_KEY = "tu_api_key"
```

## 📊 MÉTRICAS Y RENDIMIENTO

### Indicadores Clave
- **Win Rate**: Porcentaje de operaciones ganadas
- **Profit Factor**: Ganancias totales / Pérdidas totales
- **Max Drawdown**: Pérdida máxima consecutiva
- **Sharpe Ratio**: Retorno ajustado por riesgo

### Objetivos Recomendados
- Win Rate: > 55%
- Profit Factor: > 1.5
- Max Drawdown: < 20%

## ⚠️ ADVERTENCIAS IMPORTANTES

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
1. Verificar credenciales en `.env`
2. Verificar conexión a internet
3. Probar con otro broker

### "Modelo no entrenado"
1. Ir a tab "Entrenamiento"
2. Click "ENTRENAR MODELO"
3. Esperar a que termine

### "No se encontraron activos"
1. Verificar que estás conectado
2. Usar activos OTC (disponibles 24/7)
3. Ejecutar `python test_activos_disponibles.py`

### "Win Rate muy bajo"
1. Re-entrenar con más datos
2. Aumentar timesteps de entrenamiento
3. Ajustar parámetros de riesgo
4. Probar otros activos

## 📦 ESTRUCTURA DEL PROYECTO

```
trading-bot/
├── ai/                     # IA y LLM
│   └── llm_client.py
├── core/                   # Lógica principal
│   ├── agent.py           # Agente RL
│   ├── auto_trainer.py    # Auto-entrenamiento
│   ├── risk.py            # Gestión de riesgo
│   ├── trader.py          # Trading engine
│   ├── trade_analyzer.py  # Análisis post-trade
│   └── asset_manager.py   # Gestión de activos
├── data/                   # Datos de mercado
│   └── market_data.py
├── env/                    # Entorno de RL
│   └── trading_env.py
├── exnovaapi/             # API de Exnova
├── gui/                    # Interfaz gráfica
│   ├── modern_main_window.py  # Interfaz moderna
│   └── ...
├── models/                 # Modelos entrenados
│   └── rl_agent.zip
├── strategies/             # Estrategias de trading
│   └── technical.py
├── config.py              # Configuración
├── main_modern.py         # Inicio interfaz moderna
├── train_bot.py           # Script de entrenamiento
└── requirements.txt       # Dependencias
```

## 🔄 ACTUALIZACIONES Y MANTENIMIENTO

### Re-entrenamiento Diario
```bash
# Automático (en la interfaz)
Tab "Entrenamiento" → "RE-ENTRENAR"

# Manual
python train_bot.py --retrain --days 7
```

### Backup del Modelo
```bash
# Copiar modelo entrenado
cp models/rl_agent.zip models/backup/rl_agent_$(date +%Y%m%d).zip
```

### Actualizar Dependencias
```bash
pip install --upgrade -r requirements.txt
```

## 📞 SOPORTE Y RECURSOS

### Documentación
- Todos los archivos `.md` en el proyecto
- Comentarios en el código
- Logs del sistema

### Comandos Útiles
```bash
# Ver logs en tiempo real
tail -f logs/trading.log

# Limpiar cache
rm -rf __pycache__ */__pycache__

# Resetear modelo
rm models/rl_agent.zip
```

## 🎓 APRENDIZAJE Y MEJORA

### Recursos Recomendados
- Stable Baselines3 Documentation
- Reinforcement Learning: An Introduction (Sutton & Barto)
- Technical Analysis of Financial Markets

### Próximas Mejoras
- [ ] Backtesting avanzado
- [ ] Optimización de hiperparámetros
- [ ] Más estrategias de trading
- [ ] Análisis de sentimiento
- [ ] Dashboard web
- [ ] Notificaciones móviles

## 📄 LICENCIA

Este proyecto es para uso educativo y de investigación.

**DISCLAIMER**: El trading de opciones binarias conlleva riesgos significativos. Este bot no garantiza ganancias. Usa bajo tu propio riesgo.

## 🙏 CRÉDITOS

- **Stable Baselines3**: Framework de RL
- **PySide6**: Interfaz gráfica
- **Groq**: API de IA
- **Exnova/IQ Option**: Brokers

---

**¡Buena suerte con tu trading! 🚀📈**

Para más información, consulta la documentación en los archivos `.md` del proyecto.
