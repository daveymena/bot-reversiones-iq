# 🤖 Exnova Ultra-Smart Trading Bot v4.0

Bot de trading automatizado para opciones binarias (Exnova/IQ Option) con **motor de IA integrado** para razonamiento, corrección de incoherencias y mejora continua.

## 🧠 Arquitectura IA

```
Señal de mercado
      ↓
Motor Técnico (IntelligentEngine)
  • Zonas S/R multi-timeframe
  • Filtro de tendencia unánime (M1/M5/M15/H1)
  • Zone tolerance dinámica por ATR
  • Patrones de vela + micro-structure
      ↓
Agente Inteligente (IntelligentTradingAgent)
  • Detecta incoherencias técnicas
  • Valida con OpenCode AI (EasyPanel)
      ↓
OpenCode AI — Motor de Razonamiento
  • Modelo rápido: deepseek-v4-flash-free
  • Modelo profundo: qwen3.6-plus-free
  • Veredicto: ENTER / WAIT / SKIP
      ↓
Ejecución en Exnova
      ↓
Aprendizaje Post-Trade (background)
  • learn_from_result() → ajusta pesos de patrones
  • evaluate_session() cada 5 trades → ajusta selectividad
```

## 🚀 Despliegue en EasyPanel

### Variables de Entorno Requeridas

| Variable | Descripción |
|---|---|
| `EXNOVA_EMAIL` | Email de tu cuenta Exnova/IQ Option |
| `EXNOVA_PASSWORD` | Contraseña |
| `OPENCODE_API_KEY` | API Key del servidor IA en EasyPanel |
| `OPENCODE_BASE_URL` | URL del servidor IA (ya configurada por defecto) |
| `GITHUB_TOKEN` | Token de GitHub (fallback de modelos) |

### Pasos en EasyPanel

1. Conecta el repo: `https://github.com/daveymena/bot-reversiones-iq`
2. Tipo de servicio: **App**
3. Build: **Dockerfile** (detectado automáticamente)
4. Agrega las variables de entorno en la sección ENV
5. Deploy ✅

## 📊 Criterios de Operación

- ✅ Confianza mínima: 70%
- ✅ Filtro de tendencia unánime (3+ TFs alineados)
- ✅ Solo opera en zonas S/R validadas con hold rate > 70%
- ✅ Un trade por análisis (cooldown por activo)
- ✅ Máx 3 pérdidas consecutivas → pausa automática 3 min
- ✅ IA valida cada señal antes de ejecutar
- ✅ IA aprende de cada resultado en background
- ✅ IA evalúa y ajusta la estrategia cada 5 trades

## 🏗️ Estructura

```
bot/
├── main.py                    # Orquestador principal
├── config.py                  # Configuración global
├── requirements.txt           # Dependencias Python
├── brain/
│   ├── intelligent_trading_agent.py   # Agente IA core
│   ├── opencode_ai_client.py          # Cliente OpenCode AI ★ NUEVO
│   ├── adaptive_learner.py            # Aprendizaje adaptativo
│   ├── market_memory.py               # Memoria de zonas
│   └── trade_persistence.py           # Persistencia de trades
├── engine/
│   └── intelligent_engine.py          # Motor técnico de señales
├── core/
│   └── advanced_risk_manager.py       # Gestión de riesgo
└── data/
    └── market_data.py                 # Datos de mercado (WebSocket)
```
