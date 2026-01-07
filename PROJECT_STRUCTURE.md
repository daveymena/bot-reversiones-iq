# 🚀 Trading Bot - Arquitectura Moderna

## Estructura del Proyecto

```
trading-bot/
├── backend/                    # FastAPI Backend
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI app
│   │   ├── routes/
│   │   │   ├── auth.py        # Autenticación
│   │   │   ├── trading.py     # Operaciones de trading
│   │   │   ├── training.py    # Entrenamiento del modelo
│   │   │   └── websocket.py   # WebSocket para tiempo real
│   │   └── models/
│   │       ├── schemas.py     # Pydantic models
│   │       └── responses.py
│   ├── core/                  # Lógica del bot (código actual)
│   ├── strategies/
│   ├── data/
│   ├── ai/
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend-web/              # Next.js 15 + React 19
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx       # Dashboard principal
│   │   │   ├── trading/
│   │   │   ├── training/
│   │   │   └── analytics/
│   │   ├── components/
│   │   │   ├── ui/            # shadcn/ui components
│   │   │   ├── charts/        # TradingView charts
│   │   │   ├── trading/
│   │   │   └── layout/
│   │   ├── lib/
│   │   │   ├── api.ts         # API client
│   │   │   └── websocket.ts   # WebSocket client
│   │   └── hooks/
│   ├── package.json
│   ├── next.config.js
│   └── Dockerfile
│
├── desktop-app/               # Electron + React
│   ├── electron/
│   │   ├── main.ts            # Electron main process
│   │   └── preload.ts
│   ├── src/                   # Mismo código que frontend-web
│   ├── package.json
│   └── electron-builder.yml
│
└── docker-compose.yml         # Para Easypanel
```

## Stack Tecnológico

### Backend
- **FastAPI** - API REST moderna y rápida
- **WebSocket** - Comunicación en tiempo real
- **SQLAlchemy** - ORM para base de datos
- **Redis** - Cache y pub/sub
- **Celery** - Tareas asíncronas (entrenamiento)

### Frontend Web
- **Next.js 15** - Framework React con App Router
- **React 19** - UI library
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **shadcn/ui** - Componentes UI modernos
- **TradingView Lightweight Charts** - Gráficos profesionales
- **Zustand** - State management
- **React Query** - Data fetching
- **Socket.io-client** - WebSocket

### Desktop
- **Electron** - Desktop wrapper
- **React** - Mismo código del web
- **electron-builder** - Empaquetado

## Características

### ✅ Implementadas
- Dashboard en tiempo real
- Gráficos de velas japonesas
- Conexión a brokers (IQ Option, Exnova)
- Trading manual y automático
- Entrenamiento de modelo RL
- Análisis con IA (Groq/Ollama)
- Gestión de riesgo
- Martingala inteligente
- Estadísticas y métricas

### 🚀 Nuevas (Web/Desktop)
- Autenticación de usuarios
- Multi-cuenta
- Historial persistente
- Backtesting visual
- Alertas y notificaciones
- Modo oscuro/claro
- Responsive design
- PWA support
- Sincronización multi-dispositivo

## Despliegue

### Easypanel (Web)
1. Backend: FastAPI + PostgreSQL + Redis
2. Frontend: Next.js (SSR/SSG)
3. Nginx como reverse proxy
4. SSL automático

### Desktop
1. Build para Windows/Mac/Linux
2. Auto-update integrado
3. Instalador nativo
