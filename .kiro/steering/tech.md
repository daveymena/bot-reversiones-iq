# Tech Stack

## Core Technologies

### Python 3.x
Primary language for the entire application.

### Machine Learning & AI
- **stable-baselines3**: Reinforcement Learning framework (PPO algorithm)
- **gymnasium**: RL environment interface
- **groq**: Fast LLM API for trading analysis
- **ollama**: Local LLM support for offline analysis

### Data & Analysis
- **pandas**: Data manipulation and time series
- **numpy**: Numerical computations
- **ta**: Technical analysis indicators library

### GUI
- **PySide6**: Qt-based desktop interface
- **pyqtgraph**: Real-time charting and visualization

### Broker APIs
- **iqoptionapi**: IQ Option broker integration
- **exnovaapi**: Exnova broker integration (custom implementation)
- **websocket-client==1.8.0**: WebSocket communication (pinned version due to conflicts)

### Utilities
- **python-dotenv**: Environment variable management
- **requests**: HTTP client

## Project Architecture

### Core Components

```
core/
├── agent.py              # RL agent (PPO model)
├── trader.py             # Main trading loop (QThread)
├── risk.py               # Risk management
├── asset_manager.py      # Multi-asset monitoring
├── auto_trainer.py       # Automatic retraining
├── continuous_learner.py # Continuous learning system
├── decision_validator.py # Multi-layer decision validation
├── trade_analyzer.py     # Post-trade analysis
├── trade_intelligence.py # LLM-based analysis
└── observational_learner.py # Learn from unexecuted opportunities
```

### Supporting Modules

```
strategies/          # Technical analysis strategies
├── technical.py     # Feature engineering
├── optimizer.py     # Strategy optimization
├── smart_money_filter.py
└── advanced_analysis.py

data/               # Market data handling
├── market_data.py  # Broker data interface
└── experiences.json # Training experiences

ai/                 # LLM integration
└── llm_client.py   # Groq/Ollama client

gui/                # Desktop interface
├── modern_main_window.py
├── chart_widget.py
└── ...
```

## Configuration

### Environment Variables (.env)
```bash
# Broker credentials
EXNOVA_EMAIL=your@email.com
EXNOVA_PASSWORD=yourpassword
IQ_OPTION_EMAIL=your@email.com
IQ_OPTION_PASSWORD=yourpassword

# Active broker
BROKER_NAME=exnova  # or 'iq'
ACCOUNT_TYPE=PRACTICE  # or 'REAL'

# AI/LLM
GROQ_API_KEY=your_groq_key
USE_LLM=True
USE_GROQ=True
OLLAMA_MODEL=llama3
OLLAMA_BASE_URL=http://localhost:11434
```

### Config (config.py)
Centralized configuration with defaults loaded from environment variables.

## Common Commands

### Run the Bot
```bash
# Modern GUI interface
python main_modern.py

# Classic interface
python main.py
```

### Training
```bash
# Train from scratch
python train_bot.py --asset EURUSD-OTC --timesteps 10000

# Retrain with recent data
python train_bot.py --retrain --days 7
```

### Testing & Diagnostics
```bash
# Test Exnova connection
python test_exnova_completo.py

# Test IQ Option connection
python diagnostico_iq.py

# Check available assets
python test_activos_disponibles.py

# Demo operation
python demo_operacion_exnova.py

# Full bot test
python test_bot_completo.py

# Test LLM integration
python test_ollama_analysis.py
```

### Dependencies
```bash
# Install all dependencies
pip install -r requirements.txt

# Note: iqoptionapi may need manual installation
pip install https://github.com/Lu-Yi-Hsun/iqoptionapi/archive/master.zip
```

## Key Design Patterns

### Threading
- `LiveTrader` runs in a `QThread` to avoid blocking the GUI
- Signals/Slots pattern for thread-safe communication

### State Management
- Active trades tracked in memory with full context
- Experiences saved to JSON for continuous learning
- Model checkpoints saved to `models/rl_agent.zip`

### Error Handling
- Protected execution with try-catch blocks
- Graceful degradation (continues operating on non-critical errors)
- Comprehensive logging to GUI and console

### Multi-Layer Validation
1. Data quality check (sufficient candles, valid indicators)
2. RL agent prediction
3. Technical indicators analysis
4. LLM validation (Groq/Ollama)
5. Confluence check (all signals must agree)
6. Confidence threshold (minimum 60%)

## Performance Considerations

- **Cooldown periods**: 2 min between trades, 5 min after losses
- **Batch processing**: Indicators calculated once per candle
- **Lazy loading**: Model loaded only when needed
- **Timeout protection**: Training has 300s timeout
- **Memory management**: Old experiences pruned periodically
