-- ============================================
-- SCHEMA PARA BOT DE TRADING INTELIGENTE
-- Base de datos profesional para aprendizaje continuo
-- ============================================

-- Extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "timescaledb";

-- ============================================
-- TABLA: trades (Operaciones ejecutadas)
-- ============================================
CREATE TABLE trades (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    trade_id VARCHAR(100) UNIQUE,  -- ID del broker
    
    -- Información básica
    asset VARCHAR(50) NOT NULL,
    direction VARCHAR(10) NOT NULL,  -- 'call' o 'put'
    amount DECIMAL(10, 2) NOT NULL,
    duration INTEGER NOT NULL,  -- minutos
    
    -- Precios
    entry_price DECIMAL(20, 10) NOT NULL,
    exit_price DECIMAL(20, 10),
    
    -- Resultado
    result VARCHAR(10),  -- 'win', 'loss', 'draw'
    profit DECIMAL(10, 2),
    profit_pct DECIMAL(5, 2),
    
    -- Timestamps
    entry_time TIMESTAMP NOT NULL,
    exit_time TIMESTAMP,
    
    -- Contexto del mercado al entrar
    market_context JSONB,  -- RSI, MACD, Bollinger, etc.
    
    -- Decisión del bot
    rl_confidence DECIMAL(5, 2),  -- Confianza del RL agent
    llm_analysis TEXT,  -- Análisis del LLM
    decision_score INTEGER,  -- Score de la decisión (0-100)
    
    -- Metadata
    broker VARCHAR(20),
    account_type VARCHAR(20),
    session_id UUID,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Índices para trades
CREATE INDEX idx_trades_asset ON trades(asset);
CREATE INDEX idx_trades_result ON trades(result);
CREATE INDEX idx_trades_entry_time ON trades(entry_time DESC);
CREATE INDEX idx_trades_session ON trades(session_id);

-- Convertir a TimescaleDB hypertable para series temporales
SELECT create_hypertable('trades', 'entry_time', if_not_exists => TRUE);

-- ============================================
-- TABLA: market_conditions (Condiciones del mercado)
-- ============================================
CREATE TABLE market_conditions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Identificación
    asset VARCHAR(50) NOT NULL,
    timeframe INTEGER NOT NULL,  -- segundos
    timestamp TIMESTAMP NOT NULL,
    
    -- Indicadores técnicos
    rsi DECIMAL(10, 4),
    macd DECIMAL(10, 6),
    macd_signal DECIMAL(10, 6),
    macd_hist DECIMAL(10, 6),
    
    -- Medias móviles
    sma_20 DECIMAL(20, 10),
    sma_50 DECIMAL(20, 10),
    sma_200 DECIMAL(20, 10),
    ema_12 DECIMAL(20, 10),
    ema_26 DECIMAL(20, 10),
    
    -- Bollinger Bands
    bb_upper DECIMAL(20, 10),
    bb_middle DECIMAL(20, 10),
    bb_lower DECIMAL(20, 10),
    bb_width DECIMAL(10, 6),
    
    -- Volatilidad
    atr DECIMAL(10, 6),
    volatility DECIMAL(10, 6),
    
    -- Volumen y momentum
    volume BIGINT,
    momentum DECIMAL(10, 6),
    roc DECIMAL(10, 6),  -- Rate of Change
    
    -- Precio
    open DECIMAL(20, 10),
    high DECIMAL(20, 10),
    low DECIMAL(20, 10),
    close DECIMAL(20, 10),
    
    -- Patrones detectados
    patterns JSONB,  -- Patrones de velas, soportes, resistencias
    
    -- Smart Money Concepts
    order_blocks JSONB,
    fair_value_gaps JSONB,
    liquidity_zones JSONB,
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- Índices para market_conditions
CREATE INDEX idx_market_asset_time ON market_conditions(asset, timestamp DESC);
CREATE INDEX idx_market_timestamp ON market_conditions(timestamp DESC);

-- Convertir a hypertable
SELECT create_hypertable('market_conditions', 'timestamp', if_not_exists => TRUE);

-- ============================================
-- TABLA: learning_experiences (Experiencias de aprendizaje)
-- ============================================
CREATE TABLE learning_experiences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Relación con trade
    trade_id UUID REFERENCES trades(id),
    
    -- Estado antes de la decisión
    state JSONB NOT NULL,  -- Estado completo del mercado
    
    -- Acción tomada
    action VARCHAR(10) NOT NULL,  -- 'call', 'put', 'hold'
    action_confidence DECIMAL(5, 2),
    
    -- Resultado
    reward DECIMAL(10, 4) NOT NULL,  -- Recompensa obtenida
    next_state JSONB,  -- Estado después de la acción
    
    -- Análisis post-trade
    was_correct BOOLEAN,
    error_type VARCHAR(50),  -- 'false_signal', 'bad_timing', 'market_reversal', etc.
    
    -- Lecciones aprendidas
    lesson TEXT,
    should_avoid BOOLEAN DEFAULT FALSE,
    
    -- Metadata
    timestamp TIMESTAMP DEFAULT NOW(),
    model_version VARCHAR(20)
);

-- Índices
CREATE INDEX idx_experiences_trade ON learning_experiences(trade_id);
CREATE INDEX idx_experiences_action ON learning_experiences(action);
CREATE INDEX idx_experiences_reward ON learning_experiences(reward DESC);
CREATE INDEX idx_experiences_timestamp ON learning_experiences(timestamp DESC);

-- ============================================
-- TABLA: pattern_performance (Rendimiento de patrones)
-- ============================================
CREATE TABLE pattern_performance (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Patrón identificado
    pattern_type VARCHAR(100) NOT NULL,  -- 'rsi_oversold', 'macd_cross', 'bb_squeeze', etc.
    pattern_details JSONB,
    
    -- Contexto
    asset VARCHAR(50) NOT NULL,
    timeframe INTEGER NOT NULL,
    
    -- Estadísticas
    total_occurrences INTEGER DEFAULT 0,
    wins INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0,
    win_rate DECIMAL(5, 2),
    avg_profit DECIMAL(10, 2),
    
    -- Condiciones óptimas
    best_conditions JSONB,  -- Condiciones donde funciona mejor
    worst_conditions JSONB,  -- Condiciones donde falla
    
    -- Timestamps
    first_seen TIMESTAMP,
    last_seen TIMESTAMP,
    last_updated TIMESTAMP DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_pattern_type ON pattern_performance(pattern_type);
CREATE INDEX idx_pattern_asset ON pattern_performance(asset);
CREATE INDEX idx_pattern_winrate ON pattern_performance(win_rate DESC);

-- ============================================
-- TABLA: model_performance (Rendimiento del modelo)
-- ============================================
CREATE TABLE model_performance (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Versión del modelo
    model_version VARCHAR(20) NOT NULL,
    model_type VARCHAR(50) NOT NULL,  -- 'rl_agent', 'llm_validator', etc.
    
    -- Período de evaluación
    evaluation_start TIMESTAMP NOT NULL,
    evaluation_end TIMESTAMP NOT NULL,
    
    -- Métricas
    total_trades INTEGER,
    wins INTEGER,
    losses INTEGER,
    win_rate DECIMAL(5, 2),
    total_profit DECIMAL(10, 2),
    avg_profit_per_trade DECIMAL(10, 2),
    max_drawdown DECIMAL(10, 2),
    sharpe_ratio DECIMAL(10, 4),
    
    -- Métricas por activo
    performance_by_asset JSONB,
    
    -- Métricas por condición de mercado
    performance_by_volatility JSONB,
    performance_by_trend JSONB,
    
    -- Metadata
    training_data_size INTEGER,
    hyperparameters JSONB,
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_model_version ON model_performance(model_version);
CREATE INDEX idx_model_eval_end ON model_performance(evaluation_end DESC);

-- ============================================
-- TABLA: decision_logs (Log de decisiones)
-- ============================================
CREATE TABLE decision_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Contexto
    asset VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    
    -- Análisis RL
    rl_prediction VARCHAR(10),  -- 'call', 'put', 'hold'
    rl_confidence DECIMAL(5, 2),
    rl_reasoning JSONB,
    
    -- Análisis técnico
    technical_signals JSONB,
    technical_score INTEGER,
    
    -- Análisis LLM
    llm_recommendation VARCHAR(10),
    llm_confidence DECIMAL(5, 2),
    llm_reasoning TEXT,
    
    -- Validación multi-capa
    validator_approved BOOLEAN,
    validator_score INTEGER,
    validator_reasons JSONB,
    
    -- Decisión final
    final_decision VARCHAR(10),
    decision_executed BOOLEAN,
    execution_reason TEXT,
    
    -- Resultado (si se ejecutó)
    trade_id UUID REFERENCES trades(id),
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_decision_asset_time ON decision_logs(asset, timestamp DESC);
CREATE INDEX idx_decision_executed ON decision_logs(decision_executed);
CREATE INDEX idx_decision_trade ON decision_logs(trade_id);

-- ============================================
-- TABLA: error_patterns (Patrones de errores)
-- ============================================
CREATE TABLE error_patterns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Tipo de error
    error_type VARCHAR(100) NOT NULL,
    error_description TEXT,
    
    -- Frecuencia
    occurrences INTEGER DEFAULT 1,
    
    -- Condiciones comunes
    common_conditions JSONB,
    
    -- Trades afectados
    affected_trades UUID[],
    
    -- Solución propuesta
    proposed_solution TEXT,
    solution_implemented BOOLEAN DEFAULT FALSE,
    
    -- Impacto
    total_loss DECIMAL(10, 2),
    avg_loss_per_occurrence DECIMAL(10, 2),
    
    -- Timestamps
    first_occurrence TIMESTAMP,
    last_occurrence TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_error_type ON error_patterns(error_type);
CREATE INDEX idx_error_occurrences ON error_patterns(occurrences DESC);

-- ============================================
-- TABLA: strategy_evolution (Evolución de estrategias)
-- ============================================
CREATE TABLE strategy_evolution (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Estrategia
    strategy_name VARCHAR(100) NOT NULL,
    strategy_version VARCHAR(20) NOT NULL,
    strategy_config JSONB NOT NULL,
    
    -- Período de prueba
    test_start TIMESTAMP NOT NULL,
    test_end TIMESTAMP,
    
    -- Resultados
    trades_executed INTEGER DEFAULT 0,
    win_rate DECIMAL(5, 2),
    profit DECIMAL(10, 2),
    
    -- Comparación con versión anterior
    previous_version VARCHAR(20),
    improvement_pct DECIMAL(5, 2),
    
    -- Estado
    status VARCHAR(20),  -- 'testing', 'approved', 'rejected', 'active'
    
    -- Notas
    notes TEXT,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_strategy_name ON strategy_evolution(strategy_name);
CREATE INDEX idx_strategy_status ON strategy_evolution(status);

-- ============================================
-- TABLA: market_regime (Régimen de mercado)
-- ============================================
CREATE TABLE market_regime (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Identificación
    asset VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    
    -- Régimen detectado
    regime VARCHAR(50) NOT NULL,  -- 'trending_up', 'trending_down', 'ranging', 'volatile', 'calm'
    regime_strength DECIMAL(5, 2),  -- 0-100
    
    -- Características
    volatility_level VARCHAR(20),  -- 'low', 'medium', 'high', 'extreme'
    trend_direction VARCHAR(20),  -- 'bullish', 'bearish', 'neutral'
    trend_strength DECIMAL(5, 2),
    
    -- Mejor estrategia para este régimen
    recommended_strategy VARCHAR(100),
    strategy_confidence DECIMAL(5, 2),
    
    -- Duración del régimen
    regime_start TIMESTAMP,
    regime_duration INTEGER,  -- minutos
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_regime_asset_time ON market_regime(asset, timestamp DESC);
CREATE INDEX idx_regime_type ON market_regime(regime);

-- Convertir a hypertable
SELECT create_hypertable('market_regime', 'timestamp', if_not_exists => TRUE);

-- ============================================
-- VISTAS ÚTILES
-- ============================================

-- Vista: Rendimiento por activo
CREATE VIEW performance_by_asset AS
SELECT 
    asset,
    COUNT(*) as total_trades,
    SUM(CASE WHEN result = 'win' THEN 1 ELSE 0 END) as wins,
    SUM(CASE WHEN result = 'loss' THEN 1 ELSE 0 END) as losses,
    ROUND(AVG(CASE WHEN result = 'win' THEN 1.0 ELSE 0.0 END) * 100, 2) as win_rate,
    ROUND(SUM(profit), 2) as total_profit,
    ROUND(AVG(profit), 2) as avg_profit,
    MAX(profit) as best_trade,
    MIN(profit) as worst_trade
FROM trades
WHERE result IS NOT NULL
GROUP BY asset
ORDER BY total_profit DESC;

-- Vista: Rendimiento por hora del día
CREATE VIEW performance_by_hour AS
SELECT 
    EXTRACT(HOUR FROM entry_time) as hour,
    COUNT(*) as total_trades,
    SUM(CASE WHEN result = 'win' THEN 1 ELSE 0 END) as wins,
    ROUND(AVG(CASE WHEN result = 'win' THEN 1.0 ELSE 0.0 END) * 100, 2) as win_rate,
    ROUND(SUM(profit), 2) as total_profit
FROM trades
WHERE result IS NOT NULL
GROUP BY EXTRACT(HOUR FROM entry_time)
ORDER BY hour;

-- Vista: Mejores patrones
CREATE VIEW best_patterns AS
SELECT 
    pattern_type,
    asset,
    total_occurrences,
    wins,
    losses,
    win_rate,
    avg_profit,
    best_conditions
FROM pattern_performance
WHERE total_occurrences >= 10  -- Mínimo 10 ocurrencias
ORDER BY win_rate DESC, avg_profit DESC
LIMIT 20;

-- Vista: Errores más costosos
CREATE VIEW costly_errors AS
SELECT 
    error_type,
    occurrences,
    total_loss,
    avg_loss_per_occurrence,
    proposed_solution,
    solution_implemented
FROM error_patterns
ORDER BY total_loss DESC
LIMIT 20;

-- ============================================
-- FUNCIONES ÚTILES
-- ============================================

-- Función: Calcular win rate de un período
CREATE OR REPLACE FUNCTION calculate_win_rate(
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    p_asset VARCHAR DEFAULT NULL
)
RETURNS DECIMAL(5,2) AS $$
DECLARE
    win_rate DECIMAL(5,2);
BEGIN
    SELECT 
        ROUND(AVG(CASE WHEN result = 'win' THEN 1.0 ELSE 0.0 END) * 100, 2)
    INTO win_rate
    FROM trades
    WHERE entry_time BETWEEN start_date AND end_date
        AND result IS NOT NULL
        AND (p_asset IS NULL OR asset = p_asset);
    
    RETURN COALESCE(win_rate, 0);
END;
$$ LANGUAGE plpgsql;

-- Función: Obtener mejor estrategia para condiciones actuales
CREATE OR REPLACE FUNCTION get_best_strategy(
    p_asset VARCHAR,
    p_volatility DECIMAL,
    p_trend VARCHAR
)
RETURNS TABLE(
    strategy_name VARCHAR,
    confidence DECIMAL,
    expected_win_rate DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        se.strategy_name,
        se.improvement_pct as confidence,
        se.win_rate as expected_win_rate
    FROM strategy_evolution se
    WHERE se.status = 'active'
        AND se.strategy_config->>'asset' = p_asset
    ORDER BY se.win_rate DESC, se.profit DESC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- TRIGGERS
-- ============================================

-- Trigger: Actualizar timestamp en trades
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trades_updated_at
    BEFORE UPDATE ON trades
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- Trigger: Actualizar estadísticas de patrones cuando se cierra un trade
CREATE OR REPLACE FUNCTION update_pattern_stats()
RETURNS TRIGGER AS $$
BEGIN
    -- Actualizar estadísticas de patrones detectados en este trade
    -- (Implementar lógica específica según patrones)
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trade_closed_update_patterns
    AFTER UPDATE ON trades
    FOR EACH ROW
    WHEN (OLD.result IS NULL AND NEW.result IS NOT NULL)
    EXECUTE FUNCTION update_pattern_stats();

-- ============================================
-- POLÍTICAS DE RETENCIÓN
-- ============================================

-- Mantener datos detallados por 90 días, luego agregar
SELECT add_retention_policy('market_conditions', INTERVAL '90 days');
SELECT add_retention_policy('decision_logs', INTERVAL '90 days');

-- Mantener trades indefinidamente (son valiosos para aprendizaje)
-- No aplicar política de retención a trades

-- ============================================
-- COMENTARIOS
-- ============================================

COMMENT ON TABLE trades IS 'Registro completo de todas las operaciones ejecutadas';
COMMENT ON TABLE market_conditions IS 'Condiciones del mercado en cada momento (series temporales)';
COMMENT ON TABLE learning_experiences IS 'Experiencias de aprendizaje para el modelo RL';
COMMENT ON TABLE pattern_performance IS 'Rendimiento histórico de patrones detectados';
COMMENT ON TABLE model_performance IS 'Métricas de rendimiento de diferentes versiones del modelo';
COMMENT ON TABLE decision_logs IS 'Log detallado de cada decisión tomada por el bot';
COMMENT ON TABLE error_patterns IS 'Patrones de errores identificados y sus soluciones';
COMMENT ON TABLE strategy_evolution IS 'Evolución y pruebas de diferentes estrategias';
COMMENT ON TABLE market_regime IS 'Detección de régimen de mercado en tiempo real';
