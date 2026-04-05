# 🤖 Trading Bot Pro - IA + Reinforcement Learning

Bot de trading automático para opciones binarias que combina **Reinforcement Learning (PPO)**, **análisis técnico avanzado** y **consultas a LLMs** para tomar decisiones de trading informadas.

## ✨ Características Principales

- **🧠 Reinforcement Learning**: Agente PPO entrenado que aprende patrones del mercado
- **📊 Análisis Técnico Avanzado**: Multi-timeframe (M1/M15/M30), Fibonacci, Smart Money, Price Action
- **🤖 Integración LLM**: Validación de decisiones con Groq/Ollama
- **📈 Aprendizaje Continuo**: Se adapta automáticamente guardando experiencias
- **🛡️ Gestión de Riesgo**: Stop Loss, Take Profit, límites de martingala
- **🔄 Martingala Inteligente**: Análisis de pérdidas antes de duplicar apuesta
- **🌍 Multi-Broker**: Exnova (recomendado) e IQ Option
- **🐳 Docker Ready**: Deployment en EasyPanel o cualquier servidor

## 🚀 Inicio Rápido

### Requisitos
- Python 3.10+
- pip o conda
- Cuenta en Exnova (PRACTICE o REAL)

### Instalación Local

```bash
# Clonar repositorio
git clone <repo-url>
cd trading-bot

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar credenciales
cp .env.example .env
# Editar .env con tus credenciales de Exnova
```

### Ejecutar el Bot

**Modo GUI (Local)**
```bash
python main_modern.py
```

**Modo Headless (Servidor)**
```bash
python main_headless.py
```

### Deployment en Docker

```bash
# Construir imagen
docker build -t trading-bot .

# Ejecutar contenedor
docker run -d \
  --name trading-bot \
  -e EXNOVA_EMAIL=tu@email.com \
  -e EXNOVA_PASSWORD=tupassword \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/models:/app/models \
  -v $(pwd)/logs:/app/logs \
  trading-bot
```

**Con Docker Compose**
```bash
# Configurar .env
cp .env.example .env
# Editar .env con tus credenciales

# Ejecutar
docker-compose up -d

# Ver logs
docker-compose logs -f trading-bot
```

## 📁 Estructura del Proyecto

```
trading-bot/
├── core/                    # Lógica de trading
│   ├── trader.py           # Loop principal
│   ├── agent.py            # Agente RL (PPO)
│   ├── risk.py             # Gestión de riesgo
│   ├── decision_validator.py # Validación multi-capa
│   ├── trade_analyzer.py   # Análisis post-trade
│   ├── deep_learning_analyzer.py # Análisis de pérdidas/ganancias
│   └── ...
├── strategies/             # Análisis técnico
│   ├── technical.py        # Indicadores
│   ├── smart_money_filter.py
│   ├── fibonacci_analyzer.py
│   └── ...
├── data/                   # Datos y experiencias
│   ├── market_data.py      # Interfaz con brokers
│   ├── experiences.json    # Experiencias de entrenamiento
│   └── deep_lessons.json   # Lecciones aprendidas
├── ai/                     # Integración LLM
│   └── llm_client.py       # Cliente Groq/Ollama
├── gui/                    # Interfaz gráfica
│   ├── modern_main_window.py
│   ├── chart_widget.py
│   └── ...
├── models/                 # Modelos entrenados
│   └── rl_agent.zip        # Modelo PPO
├── main_modern.py          # Entrada GUI
├── main_headless.py        # Entrada Headless
├── config.py               # Configuración centralizada
├── requirements.txt        # Dependencias
├── requirements_cloud.txt  # Dependencias sin GUI
├── Dockerfile              # Contenedor Docker
├── docker-compose.yml      # Orquestación Docker
└── docs/                   # Documentación
```

## ⚙️ Configuración

### Variables de Entorno (.env)

```bash
# Broker
EXNOVA_EMAIL=tu@email.com
EXNOVA_PASSWORD=tupassword
BROKER_NAME=exnova
ACCOUNT_TYPE=PRACTICE  # o REAL

# Trading
CAPITAL_PER_TRADE=1
MAX_MARTINGALE=0

# AI/LLM
USE_LLM=True
USE_GROQ=False
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:1b
```

Ver `.env.example` para todas las opciones disponibles.

## 📚 Documentación

- **[DEPLOYMENT_EASYPANEL.md](docs/DEPLOYMENT_EASYPANEL.md)** - Guía de deployment en EasyPanel
- **[SISTEMA_APRENDIZAJE_PROFUNDO.md](docs/SISTEMA_APRENDIZAJE_PROFUNDO.md)** - Sistema de Deep Learning
- **[COMO_EJECUTAR.md](docs/COMO_EJECUTAR.md)** - Guía de ejecución
- **[GUIA_USO_BOT.md](docs/GUIA_USO_BOT.md)** - Guía de uso completa

## 🧪 Testing

```bash
# Test de conexión con Exnova
python -m pytest tests/test_exnova_connection.py

# Test del bot completo
python -m pytest tests/test_bot_complete.py

# Test de LLM
python -m pytest tests/test_llm_integration.py
```

## 🔧 Desarrollo

### Estructura de Código

- **Separación de responsabilidades**: GUI, Core, Data, Strategies, AI
- **Configuración centralizada**: `config.py`
- **Logging estructurado**: Logs a archivo y consola
- **Type hints**: Código tipado para mejor mantenibilidad

### Agregar Nueva Estrategia

1. Crear archivo en `strategies/`
2. Heredar de `BaseStrategy`
3. Implementar método `analyze()`
4. Registrar en `decision_validator.py`

## 📊 Monitoreo

### Logs

```bash
# Ver logs en tiempo real
tail -f logs/bot_*.log

# Ver logs en Docker
docker-compose logs -f trading-bot
```

### Métricas

El bot guarda automáticamente:
- `data/experiences.json` - Experiencias de trading
- `data/deep_lessons.json` - Lecciones aprendidas
- `data/history.csv` - Historial de operaciones

## 🐛 Troubleshooting

### Error: "EXNOVA_EMAIL no configurado"
```bash
# Solución: Configurar .env
cp .env.example .env
# Editar .env con tus credenciales
```

### Error: "Conexión rechazada"
```bash
# Verificar credenciales
python -c "from config import Config; print(f'Email: {Config.EXNOVA_EMAIL}')"

# Test de conexión
python -m pytest tests/test_exnova_connection.py -v
```

### Bot se detiene en Docker
```bash
# Ver logs
docker-compose logs trading-bot

# Reiniciar
docker-compose restart trading-bot
```

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## ⚠️ Disclaimer

Este bot es para propósitos educativos. El trading de opciones binarias conlleva riesgo. 
**Usa siempre PRACTICE primero** antes de operar con dinero real.

## 📄 Licencia

Este proyecto está bajo licencia MIT. Ver `LICENSE` para más detalles.

## 📞 Soporte

Para reportar bugs o sugerencias, abre un issue en el repositorio.

---

**Última actualización**: Abril 2026
**Versión**: V5-PRODUCTION
**Estado**: ✅ Listo para producción
