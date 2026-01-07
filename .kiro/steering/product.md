# Product Overview

## Trading Bot Profesional con IA

Bot de trading automático para opciones binarias que combina Reinforcement Learning (PPO), análisis técnico avanzado y consultas a LLMs (Groq/Ollama) para tomar decisiones de trading informadas.

### Core Features

- **Reinforcement Learning**: Agente PPO entrenado con datos históricos que aprende patrones del mercado
- **Análisis LLM**: Consulta a modelos de IA (Groq/Ollama) para validación de decisiones y análisis de timing
- **Martingala Inteligente**: Sistema de recuperación que analiza por qué se perdió antes de duplicar apuesta
- **Aprendizaje Continuo**: Se adapta automáticamente guardando experiencias y re-entrenando periódicamente
- **Gestión de Riesgo**: Stop Loss, Take Profit, límites de martingala y validación de decisiones

### Supported Brokers

- **Exnova** (Recomendado - 100% funcional)
- **IQ Option** (Conflicto de versiones de websocket)

### Trading Modes

- **PRACTICE**: Cuenta demo para pruebas (recomendado inicialmente)
- **REAL**: Operaciones con dinero real (solo después de validar en PRACTICE)

### Key Differentiators

- Validación multi-capa antes de ejecutar operaciones (RL + Indicadores + LLM)
- Sistema de aprendizaje observacional que registra oportunidades no ejecutadas
- Análisis post-trade para mejorar decisiones futuras
- Modo 24/7 con activos OTC disponibles todo el tiempo
