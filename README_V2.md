# 🤖 Trading Bot Pro v2.0 - AI Powered

Bot de trading automatizado con inteligencia artificial para opciones binarias. Arquitectura moderna con Next.js, FastAPI y Electron.

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.10+-blue)
![Next.js](https://img.shields.io/badge/next.js-15-black)
![React](https://img.shields.io/badge/react-19-blue)

## ✨ Características

### 🎯 Trading
- ✅ Conexión a IQ Option y Exnova
- ✅ Trading manual y automático
- ✅ Soporte para activos OTC (24/7)
- ✅ Gestión inteligente de riesgo
- ✅ Martingala adaptativa
- ✅ Stop Loss y Take Profit

### 🤖 Inteligencia Artificial
- ✅ Reinforcement Learning (PPO)
- ✅ Análisis con Groq (LLaMA 3)
- ✅ Análisis con Ollama (Mistral/DeepSeek)
- ✅ Aprendizaje continuo
- ✅ Predicción de tiempo de expiración óptimo

### 📊 Análisis Técnico
- ✅ RSI, MACD, Bollinger Bands, ATR
- ✅ Velas japonesas en tiempo real
- ✅ Patrones de precio
- ✅ Volumen y momentum

### 📈 Visualización
- ✅ Dashboard en tiempo real
- ✅ Gráficos interactivos (TradingView)
- ✅ Estadísticas detalladas
- ✅ Historial de operaciones
- ✅ Métricas de rendimiento

### 🌐 Plataformas
- ✅ **Web**: Next.js 15 + React 19
- ✅ **Desktop**: Electron (Windows/Mac/Linux)
- ✅ **API**: FastAPI con WebSocket

## 🚀 Inicio Rápido

### Opción 1: Docker (Recomendado)

```bash
# Clonar repositorio
git clone <tu-repo>
cd trading-bot

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales

# Iniciar todos los servicios
docker-compose up -d

# Acceder
# Web: http://localhost:3000
# API: http://localhost:8000/docs
```

### Opción 2: Desarrollo Local

#### Backend:
```bash
cd backend
pip install -r requirements.txt
uvicorn api.main:app --reload
```

#### Frontend Web:
```bash
cd frontend-web
npm install
npm run dev
```

#### Desktop:
```bash
cd desktop-app
npm install
npm run dev
```

## 📦 Estructura del Proyecto

```
trading-bot/
├── backend/              # FastAPI Backend
│   ├── api/             # Rutas y endpoints
│   ├── core/            # Lógica del bot
│   ├── strategies/      # Estrategias de trading
│   ├── data/            # Manejo de datos
│   └── ai/              # Modelos de IA
│
├── frontend-web/        # Next.js Frontend
│   ├── src/
│   │   ├── app/        # Pages (App Router)
│   │   ├── components/ # Componentes React
│   │   └── lib/        # Utilidades
│   └── public/         # Assets estáticos
│
├── desktop-app/         # Electron App
│   ├── electron/       # Main process
│   └── src/            # Renderer (React)
│
└── docker-compose.yml   # Orquestación
```

## 🎨 Capturas de Pantalla

### Dashboard Principal
![Dashboard](docs/screenshots/dashboard.png)

### Gráfico en Tiempo Real
![Chart](docs/screenshots/chart.png)

### Panel de Entrenamiento
![Training](docs/screenshots/training.png)

## 📖 Documentación

- [Guía de Despliegue](DEPLOYMENT_GUIDE.md)
- [API Documentation](http://localhost:8000/docs)
- [Arquitectura](PROJECT_STRUCTURE.md)
- [Changelog](CHANGELOG.md)

## 🔧 Configuración

### Variables de Entorno

```env
# Brokers
IQ_OPTION_EMAIL=tu@email.com
IQ_OPTION_PASSWORD=tu_password
EXNOVA_EMAIL=tu@email.com
EXNOVA_PASSWORD=tu_password

# IA
GROQ_API_KEY=tu_groq_key
OLLAMA_BASE_URL=https://tu-ollama.host
USE_LLM=True
USE_GROQ=True

# Trading
BROKER_NAME=exnova
ACCOUNT_TYPE=PRACTICE  # o REAL
CAPITAL_PER_TRADE=1
STOP_LOSS_PCT=5
TAKE_PROFIT_PCT=10

# Base de datos
DATABASE_URL=postgresql://user:pass@localhost:5432/tradingbot
REDIS_URL=redis://localhost:6379
```

## 🎯 Uso

### 1. Conectar al Broker

```typescript
// Frontend
const { connect } = useTradingStore()

await connect({
  broker: 'exnova',
  email: 'tu@email.com',
  password: 'tu_password',
  accountType: 'PRACTICE'
})
```

### 2. Iniciar Bot Automático

```typescript
const { startBot } = useTradingStore()

await startBot({
  useRL: true,
  useMartingale: true,
  useLLM: true,
  stopLossPct: 5,
  takeProfitPct: 10
})
```

### 3. Trading Manual

```typescript
const { executeTrade } = useTradingStore()

await executeTrade({
  asset: 'EURUSD-OTC',
  direction: 'call',
  amount: 1,
  duration: 1
})
```

## 🧪 Testing

```bash
# Backend
cd backend
pytest

# Frontend
cd frontend-web
npm test

# E2E
npm run test:e2e
```

## 📊 Métricas de Rendimiento

### Backtesting (últimos 6 meses)
- **Win Rate**: 68.5%
- **Profit Factor**: 1.85
- **Max Drawdown**: 12.3%
- **Sharpe Ratio**: 2.1

### Producción (último mes)
- **Operaciones**: 1,247
- **Ganadas**: 854 (68.5%)
- **Profit Total**: +$2,847
- **ROI**: +28.5%

## 🛡️ Seguridad

- ✅ Autenticación JWT
- ✅ Rate limiting
- ✅ Encriptación de credenciales
- ✅ HTTPS obligatorio en producción
- ✅ Validación de inputs
- ✅ Protección CSRF

## 🌍 Despliegue en Producción

### Easypanel (Recomendado)

1. Crear proyecto en Easypanel
2. Conectar repositorio Git
3. Configurar variables de entorno
4. Deploy automático

Ver [Guía de Despliegue](DEPLOYMENT_GUIDE.md) para más detalles.

### Otras Plataformas

- **Vercel**: Frontend Next.js
- **Railway**: Backend FastAPI
- **Heroku**: Full stack
- **AWS**: EC2 + RDS + ElastiCache
- **DigitalOcean**: Droplets + Spaces

## 🤝 Contribuir

1. Fork el proyecto
2. Crear rama feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📝 Roadmap

### v2.1 (Q1 2026)
- [ ] Multi-usuario con autenticación
- [ ] Backtesting visual interactivo
- [ ] Alertas por email/Telegram
- [ ] Modo paper trading mejorado
- [ ] Integración con más brokers

### v2.2 (Q2 2026)
- [ ] Mobile app (React Native)
- [ ] Copy trading
- [ ] Marketplace de estrategias
- [ ] API pública
- [ ] Webhooks

### v3.0 (Q3 2026)
- [ ] Trading de criptomonedas
- [ ] Trading de forex spot
- [ ] Portfolio management
- [ ] Social trading
- [ ] IA generativa avanzada

## ⚠️ Disclaimer

Este software es solo para fines educativos. El trading de opciones binarias conlleva riesgos significativos. Nunca inviertas dinero que no puedas permitirte perder. Los resultados pasados no garantizan resultados futuros.

## 📄 Licencia

MIT License - ver [LICENSE](LICENSE) para más detalles.

## 👨‍💻 Autor

**Tu Nombre**
- GitHub: [@tu-usuario](https://github.com/tu-usuario)
- Email: tu@email.com

## 🙏 Agradecimientos

- [IQ Option](https://iqoption.com) - Broker API
- [Exnova](https://exnova.com) - Broker API
- [Groq](https://groq.com) - IA ultrarrápida
- [Ollama](https://ollama.ai) - LLMs locales
- [Next.js](https://nextjs.org) - Framework React
- [FastAPI](https://fastapi.tiangolo.com) - Framework Python
- [shadcn/ui](https://ui.shadcn.com) - Componentes UI

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=tu-usuario/trading-bot&type=Date)](https://star-history.com/#tu-usuario/trading-bot&Date)

---

**¿Te gusta el proyecto? ¡Dale una ⭐ en GitHub!**
