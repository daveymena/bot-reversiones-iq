# Project Structure

## Directory Organization

```
trading-bot/
├── core/                   # Core trading logic
│   ├── agent.py           # RL agent (PPO model)
│   ├── trader.py          # Main trading loop (QThread)
│   ├── risk.py            # Risk management
│   ├── asset_manager.py   # Multi-asset monitoring
│   ├── auto_trainer.py    # Automatic retraining
│   ├── continuous_learner.py    # Continuous learning
│   ├── decision_validator.py    # Multi-layer validation
│   ├── trade_analyzer.py        # Post-trade analysis
│   ├── trade_intelligence.py    # LLM-based analysis
│   ├── observational_learner.py # Learn from unexecuted trades
│   └── trader_helpers.py        # Helper functions
│
├── strategies/            # Trading strategies
│   ├── technical.py       # Feature engineering & indicators
│   ├── optimizer.py       # Strategy optimization
│   ├── advanced_analysis.py
│   ├── smart_money_filter.py
│   ├── liquidity_zones.py
│   └── price_action_analysis.py
│
├── data/                  # Data handling
│   ├── market_data.py     # Broker data interface
│   ├── experiences.json   # Training experiences
│   ├── experiences_backup.json
│   └── history.csv        # Historical data
│
├── ai/                    # AI/LLM integration
│   └── llm_client.py      # Groq/Ollama client
│
├── gui/                   # Desktop interface
│   ├── modern_main_window.py  # Main window
│   ├── main_window.py         # Classic window
│   ├── chart_widget.py        # Real-time charts
│   ├── connection_widget.py   # Broker connection
│   ├── status_widget.py       # Status display
│   ├── strategy_widget.py     # Strategy config
│   └── history_widget.py      # Trade history
│
├── exnovaapi/             # Exnova broker API
│   ├── api.py
│   ├── stable_api.py
│   ├── ws/                # WebSocket channels
│   └── http/              # HTTP endpoints
│
├── backend/               # FastAPI backend (future)
│   ├── api/
│   │   ├── main.py
│   │   └── routes/
│   └── models/
│
├── frontend-web/          # Next.js frontend (future)
│   └── src/
│
├── models/                # Trained models
│   └── rl_agent.zip       # PPO model checkpoint
│
├── .env                   # Environment variables (credentials)
├── .env.example           # Template for .env
├── config.py              # Centralized configuration
├── requirements.txt       # Python dependencies
│
├── main.py                # Classic GUI entry point
├── main_modern.py         # Modern GUI entry point
├── train_bot.py           # Training script
│
├── test_*.py              # Test scripts
├── demo_*.py              # Demo scripts
├── diagnostico_*.py       # Diagnostic scripts
│
└── *.md                   # Documentation files
```

## Key File Purposes

### Entry Points
- **main_modern.py**: Primary entry point with modern GUI
- **main.py**: Classic GUI interface
- **train_bot.py**: Standalone training script

### Core Trading Logic
- **core/trader.py**: Main trading loop running in QThread, orchestrates all components
- **core/agent.py**: RL agent wrapper for PPO model
- **core/risk.py**: Risk management (stop loss, take profit, position sizing)
- **core/decision_validator.py**: Multi-layer validation before executing trades

### Learning Systems
- **core/continuous_learner.py**: Automatic retraining based on performance
- **core/observational_learner.py**: Learn from opportunities not executed
- **core/trade_analyzer.py**: Analyze completed trades for insights
- **core/experience_buffer.py**: Manage training experiences

### Data & Analysis
- **strategies/technical.py**: Feature engineering (RSI, MACD, Bollinger Bands, etc.)
- **data/market_data.py**: Unified interface for broker APIs
- **ai/llm_client.py**: LLM integration for trade analysis

### Configuration
- **config.py**: Single source of truth for all configuration
- **.env**: Sensitive credentials (never commit)

## Module Dependencies

### Import Hierarchy
```
main_modern.py
  └── gui/modern_main_window.py
      └── core/trader.py (QThread)
          ├── core/agent.py
          ├── core/risk.py
          ├── core/asset_manager.py
          ├── core/continuous_learner.py
          ├── core/decision_validator.py
          ├── core/trade_intelligence.py
          ├── core/observational_learner.py
          ├── strategies/technical.py
          ├── data/market_data.py
          └── ai/llm_client.py
```

### Data Flow
```
Broker API → market_data.py → trader.py → feature_engineer → agent.py
                                    ↓
                            decision_validator.py
                                    ↓
                            trade_intelligence.py (LLM)
                                    ↓
                            Execute Trade → Broker API
                                    ↓
                            trade_analyzer.py
                                    ↓
                            continuous_learner.py
```

## Naming Conventions

### Files
- **Core modules**: `snake_case.py` (e.g., `trade_analyzer.py`)
- **Test files**: `test_*.py` (e.g., `test_exnova_completo.py`)
- **Demo files**: `demo_*.py` (e.g., `demo_operacion_exnova.py`)
- **Diagnostic files**: `diagnostico_*.py` (e.g., `diagnostico_iq.py`)
- **Documentation**: `UPPERCASE_WITH_UNDERSCORES.md` (e.g., `COMO_EJECUTAR.md`)

### Classes
- **PascalCase**: `LiveTrader`, `RLAgent`, `RiskManager`
- **Qt classes**: Inherit from Qt base classes (e.g., `QThread`, `QMainWindow`)

### Functions/Methods
- **snake_case**: `execute_trade()`, `get_balance()`, `analyze_indicators()`
- **Private methods**: `_run_protected()`, `_calculate_profit_by_price()`

### Variables
- **snake_case**: `active_trades`, `current_asset`, `last_trade_time`
- **Constants**: `UPPERCASE` in config.py (e.g., `CAPITAL_PER_TRADE`)

## Documentation Structure

### User Documentation (Spanish)
- **INICIO_RAPIDO.md**: Quick start guide
- **COMO_EJECUTAR.md**: Detailed execution guide
- **GUIA_USO_BOT.md**: Complete usage guide
- **COMO_FUNCIONA_APRENDIZAJE.md**: Learning system explanation

### Technical Documentation (Spanish)
- **SISTEMA_ENTRENAMIENTO.md**: Training system details
- **VALIDACION_DECISIONES.md**: Decision validation system
- **APRENDIZAJE_CONTINUO.md**: Continuous learning system
- **PROJECT_STRUCTURE.md**: Architecture overview
- **DATABASE_ARCHITECTURE.md**: Database design (future)

### Status & Analysis (Spanish)
- **ESTADO_ACTUAL.md**: Current project status
- **RESUMEN_*.md**: Various summaries and analyses
- **ANALISIS_*.md**: Analysis documents

## Code Organization Principles

### Separation of Concerns
- **GUI**: Only handles display and user interaction
- **Core**: Business logic and trading decisions
- **Data**: Data fetching and storage
- **Strategies**: Technical analysis and indicators
- **AI**: LLM integration

### Single Responsibility
- Each module has one clear purpose
- Large files (like `trader.py`) are split into logical sections with clear comments

### Dependency Injection
- Components receive dependencies via constructor
- Makes testing and swapping implementations easier

### Configuration Over Code
- All tunable parameters in `config.py` or `.env`
- No magic numbers in business logic

## Testing Structure

### Test Categories
- **Connection tests**: `test_exnova_completo.py`, `diagnostico_iq.py`
- **Feature tests**: `test_mejoras.py`, `test_smart_money.py`
- **Integration tests**: `test_bot_completo.py`
- **Demo scripts**: `demo_operacion_exnova.py`

### Test Naming
- Descriptive names indicating what is tested
- Spanish language for consistency with documentation
