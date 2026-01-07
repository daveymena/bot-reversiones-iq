# 🤖 Trading Bot Pro - Exnova Edition

Bot de trading automático con IA para opciones binarias en **Exnova**.

## ✨ Características

- 🤖 **Reinforcement Learning (PPO)** - Agente que aprende de operaciones
- 🧠 **Análisis LLM (Groq)** - Validación inteligente con IA
- 📊 **Análisis Técnico Avanzado** - RSI, MACD, Bollinger Bands, Smart Money
- 🎯 **Filtros Inteligentes** - Volatilidad, impulso, timing óptimo
- 📈 **Gráficos en Tiempo Real** - Visualización profesional con pyqtgraph
- 🔄 **Aprendizaje Continuo** - Se adapta automáticamente
- 🛡️ **Gestión de Riesgo** - Stop Loss, Take Profit, Martingala Inteligente
- 🌍 **Multi-Activos** - Monitorea 9 pares OTC simultáneamente

## 🚀 Inicio Rápido

### 1. Requisitos

- Python 3.11+
- Cuenta en Exnova (PRACTICE recomendado)
- API Key de Groq (opcional, para análisis LLM)

### 2. Instalación

```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/trading-bot-exnova.git
cd trading-bot-exnova

# Instalar dependencias
pip install -r requirements.txt
```

### 3. Configuración

Crea un archivo `.env`:

```bash
# Credenciales Exnova
EXNOVA_EMAIL=tu@email.com
EXNOVA_PASSWORD=tupassword

# Configuración
BROKER_NAME=exnova
ACCOUNT_TYPE=PRACTICE

# LLM (opcional)
GROQ_API_KEY=tu_api_key
USE_LLM=True
```

### 4. Ejecutar

```bash
# Interfaz moderna
python main_modern.py

# O usar el script
.\EJECUTAR_BOT_MODERNO.bat
```

## 📖 Uso

1. **Conectar** - Haz clic en "CONECTAR" para conectarte a Exnova
2. **Iniciar** - Haz clic en "INICIAR BOT"
3. **Monitorear** - El bot escaneará oportunidades automáticamente
4. **Operar** - Ejecutará operaciones cuando las condiciones sean óptimas

## 🎯 Activos Soportados

- EURUSD-OTC
- GBPUSD-OTC
- USDJPY-OTC
- AUDUSD-OTC
- USDCAD-OTC
- EURJPY-OTC
- EURGBP-OTC
- GBPJPY-OTC
- AUDJPY-OTC

## 🛡️ Seguridad

- ✅ Usa **PRACTICE** primero para probar
- ✅ Filtros de volatilidad y impulso
- ✅ Validación multi-capa antes de operar
- ✅ Stop Loss y Take Profit automáticos
- ✅ Límites de pérdidas consecutivas

## 📊 Arquitectura

```
main_modern.py (Interfaz)
    ↓
core/trader.py (Lógica principal)
    ↓
├── core/agent.py (RL Agent - PPO)
├── core/decision_validator.py (Validación)
├── core/risk.py (Gestión de riesgo)
├── strategies/technical.py (Análisis técnico)
├── ai/llm_client.py (Groq LLM)
└── exnovaapi/ (API de Exnova)
```

## 🔧 Desarrollo

### Estructura del Proyecto

```
trading-bot-exnova/
├── core/              # Lógica principal
├── strategies/        # Análisis técnico
├── ai/               # Integración LLM
├── gui/              # Interfaz gráfica
├── exnovaapi/        # API de Exnova
├── env/              # Entorno RL
├── data/             # Datos y experiencias
└── models/           # Modelos entrenados
```

### Compilar Ejecutable

```bash
# Con Python 3.11
.\COMPILAR_CON_PYTHON311.bat

# Resultado: dist/TradingBotPro.exe
```

## 📚 Documentación

- `COMO_EJECUTAR.md` - Guía de ejecución
- `COMO_FUNCIONA_APRENDIZAJE.md` - Sistema de aprendizaje
- `ANALISIS_INTELIGENTE_DEL_BOT.md` - Análisis del bot

## ⚠️ Advertencias

- **Riesgo financiero**: Trading de opciones binarias conlleva riesgo
- **Usa PRACTICE primero**: Valida el bot antes de usar dinero real
- **No garantías**: El bot no garantiza ganancias
- **Responsabilidad**: Usa bajo tu propio riesgo

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/mejora`)
3. Commit tus cambios (`git commit -m 'Añadir mejora'`)
4. Push a la rama (`git push origin feature/mejora`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto es de código abierto. Úsalo bajo tu propia responsabilidad.

## 🙏 Agradecimientos

- Exnova por su API
- Groq por el análisis LLM
- Stable-Baselines3 por el framework RL
- PySide6 por la interfaz gráfica

---

**Versión:** 2.0.0  
**Última actualización:** 2025-11-27  
**Estado:** ✅ Producción  
**Broker:** Exnova únicamente
