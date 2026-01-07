# 🗄️ Arquitectura de Base de Datos - Trading Bot SaaS

## 📊 Bases de Datos Recomendadas

### 1. **PostgreSQL** (Principal - Datos Estructurados)
**Uso**: Usuarios, suscripciones, configuraciones, historial de trades

**Ventajas**:
- ✅ ACID compliant (transacciones seguras)
- ✅ Relaciones complejas
- ✅ Excelente para datos financieros
- ✅ Backups automáticos
- ✅ Escalable verticalmente

**Tablas**:
```sql
- users (usuarios y autenticación)
- subscriptions (planes y pagos)
- broker_accounts (cuentas de brokers)
- trades (historial de operaciones)
- strategies (estrategias guardadas)
- performance_metrics (métricas de rendimiento)
- audit_logs (logs de auditoría)
```

### 2. **Redis** (Cache + Real-time)
**Uso**: Cache, sesiones, WebSocket, datos en tiempo real

**Ventajas**:
- ✅ Ultra rápido (in-memory)
- ✅ Pub/Sub para WebSocket
- ✅ Cache de precios
- ✅ Rate limiting
- ✅ Sessions store

**Uso**:
```
- market_data:* (precios en tiempo real)
- user_session:* (sesiones activas)
- bot_state:* (estado del bot por usuario)
- rate_limit:* (control de requests)
- cache:* (cache general)
```

### 3. **MongoDB** (Opcional - Datos No Estructurados)
**Uso**: Logs, análisis de IA, datos de entrenamiento

**Ventajas**:
- ✅ Flexible schema
- ✅ Excelente para logs
- ✅ Datos de entrenamiento ML
- ✅ Análisis históricos
- ✅ Time-series data

**Colecciones**:
```
- training_data (datos de entrenamiento)
- ai_predictions (predicciones de IA)
- system_logs (logs del sistema)
- market_analysis (análisis de mercado)
- user_activity (actividad de usuarios)
```

## 🏗️ Arquitectura Recomendada para SaaS

```
┌─────────────────────────────────────────────────┐
│                   FRONTEND                       │
│            (Next.js Multi-tenant)                │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│                 BACKEND API                      │
│              (FastAPI + Auth)                    │
└─┬──────────┬──────────┬──────────┬──────────────┘
  │          │          │          │
  │          │          │          │
┌─▼──────┐ ┌▼────────┐ ┌▼───────┐ ┌▼──────────┐
│PostgreSQL│ │  Redis  │ │ MongoDB│ │  S3/Spaces│
│(Datos)   │ │ (Cache) │ │ (Logs) │ │ (Archivos)│
└──────────┘ └─────────┘ └────────┘ └───────────┘
```

## 📋 Esquema PostgreSQL Completo

```sql
-- USUARIOS Y AUTENTICACIÓN
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'user', -- user, admin, premium
    subscription_tier VARCHAR(50) DEFAULT 'free', -- free, basic, pro, enterprise
    subscription_status VARCHAR(50) DEFAULT 'active',
    subscription_expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_login_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    email_verified BOOLEAN DEFAULT FALSE,
    trial_ends_at TIMESTAMP,
    referral_code VARCHAR(50) UNIQUE,
    referred_by UUID REFERENCES users(id)
);

-- CUENTAS DE BROKERS
CREATE TABLE broker_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    broker VARCHAR(50) NOT NULL, -- exnova, iqoption
    email VARCHAR(255) NOT NULL,
    password_encrypted TEXT NOT NULL, -- Encriptado
    account_type VARCHAR(50) NOT NULL, -- PRACTICE, REAL
    is_active BOOLEAN DEFAULT TRUE,
    last_connected_at TIMESTAMP,
    balance DECIMAL(15, 2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, broker, email)
);

-- CONFIGURACIONES DEL BOT
CREATE TABLE bot_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    broker_account_id UUID REFERENCES broker_accounts(id),
    
    -- Trading
    capital_per_trade DECIMAL(10, 2) DEFAULT 1,
    stop_loss_pct DECIMAL(5, 2) DEFAULT 5,
    take_profit_pct DECIMAL(5, 2) DEFAULT 10,
    max_daily_loss DECIMAL(10, 2),
    max_daily_profit DECIMAL(10, 2),
    
    -- Estrategias
    use_rl BOOLEAN DEFAULT TRUE,
    use_martingale BOOLEAN DEFAULT TRUE,
    use_llm BOOLEAN DEFAULT TRUE,
    max_martingale_level INTEGER DEFAULT 3,
    
    -- Activos
    assets JSONB DEFAULT '[]', -- ["EURUSD-OTC", "GBPUSD-OTC"]
    
    -- Horarios
    trading_hours JSONB, -- {"start": "08:00", "end": "18:00"}
    
    is_active BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- HISTORIAL DE TRADES
CREATE TABLE trades (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    broker_account_id UUID REFERENCES broker_accounts(id),
    bot_config_id UUID REFERENCES bot_configs(id),
    
    -- Trade info
    trade_id VARCHAR(255), -- ID del broker
    asset VARCHAR(50) NOT NULL,
    direction VARCHAR(10) NOT NULL, -- call, put
    amount DECIMAL(10, 2) NOT NULL,
    duration INTEGER NOT NULL, -- minutos
    expiration_time INTEGER,
    
    -- Resultado
    status VARCHAR(50) NOT NULL, -- pending, win, loss, cancelled
    profit DECIMAL(10, 2) DEFAULT 0,
    payout_pct DECIMAL(5, 2),
    
    -- Precios
    entry_price DECIMAL(15, 5),
    exit_price DECIMAL(15, 5),
    
    -- Análisis
    indicators JSONB, -- RSI, MACD, etc
    ai_prediction JSONB, -- Predicción de IA
    confidence DECIMAL(5, 2), -- 0-100
    
    -- Martingala
    martingale_level INTEGER DEFAULT 0,
    is_recovery BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    opened_at TIMESTAMP NOT NULL,
    closed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    
    -- Índices
    INDEX idx_user_trades (user_id, created_at DESC),
    INDEX idx_status (status),
    INDEX idx_asset (asset)
);

-- MODELOS DE RL (Entrenamiento)
CREATE TABLE rl_models (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    version INTEGER DEFAULT 1,
    
    -- Entrenamiento
    training_episodes INTEGER,
    training_timesteps INTEGER,
    training_duration INTEGER, -- segundos
    
    -- Performance
    win_rate DECIMAL(5, 2),
    avg_reward DECIMAL(10, 4),
    sharpe_ratio DECIMAL(10, 4),
    max_drawdown DECIMAL(5, 2),
    
    -- Archivos
    model_path TEXT, -- S3/Spaces URL
    model_size INTEGER, -- bytes
    
    -- Metadata
    hyperparameters JSONB,
    training_data_summary JSONB,
    
    is_active BOOLEAN DEFAULT FALSE,
    trained_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(user_id, name, version)
);

-- MÉTRICAS DE RENDIMIENTO (Agregadas)
CREATE TABLE performance_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    bot_config_id UUID REFERENCES bot_configs(id),
    
    -- Período
    period_type VARCHAR(50) NOT NULL, -- daily, weekly, monthly
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    
    -- Métricas
    total_trades INTEGER DEFAULT 0,
    winning_trades INTEGER DEFAULT 0,
    losing_trades INTEGER DEFAULT 0,
    win_rate DECIMAL(5, 2) DEFAULT 0,
    
    total_profit DECIMAL(15, 2) DEFAULT 0,
    total_loss DECIMAL(15, 2) DEFAULT 0,
    net_profit DECIMAL(15, 2) DEFAULT 0,
    
    avg_profit_per_trade DECIMAL(10, 2) DEFAULT 0,
    max_consecutive_wins INTEGER DEFAULT 0,
    max_consecutive_losses INTEGER DEFAULT 0,
    
    max_drawdown DECIMAL(5, 2) DEFAULT 0,
    sharpe_ratio DECIMAL(10, 4),
    profit_factor DECIMAL(10, 4),
    
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(user_id, bot_config_id, period_type, period_start)
);

-- SUSCRIPCIONES Y PAGOS
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
    plan VARCHAR(50) NOT NULL, -- free, basic, pro, enterprise
    status VARCHAR(50) NOT NULL, -- active, cancelled, expired, past_due
    
    -- Precios
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'USD',
    billing_cycle VARCHAR(50), -- monthly, yearly
    
    -- Fechas
    started_at TIMESTAMP NOT NULL,
    current_period_start TIMESTAMP,
    current_period_end TIMESTAMP,
    cancelled_at TIMESTAMP,
    
    -- Stripe/Payment
    stripe_subscription_id VARCHAR(255),
    stripe_customer_id VARCHAR(255),
    
    -- Límites del plan
    max_bots INTEGER,
    max_trades_per_day INTEGER,
    max_capital_per_trade DECIMAL(10, 2),
    features JSONB, -- {"ai": true, "backtesting": true}
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- PAGOS
CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    subscription_id UUID REFERENCES subscriptions(id),
    
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'USD',
    status VARCHAR(50) NOT NULL, -- succeeded, failed, pending, refunded
    
    payment_method VARCHAR(50), -- card, paypal, crypto
    stripe_payment_id VARCHAR(255),
    
    description TEXT,
    receipt_url TEXT,
    
    paid_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- LOGS DE AUDITORÍA
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    
    action VARCHAR(100) NOT NULL, -- login, trade, config_change, etc
    entity_type VARCHAR(50), -- user, trade, bot_config
    entity_id UUID,
    
    details JSONB,
    ip_address INET,
    user_agent TEXT,
    
    created_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_user_logs (user_id, created_at DESC),
    INDEX idx_action (action)
);

-- NOTIFICACIONES
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
    type VARCHAR(50) NOT NULL, -- trade_result, daily_summary, alert
    title VARCHAR(255) NOT NULL,
    message TEXT,
    data JSONB,
    
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_user_notifications (user_id, is_read, created_at DESC)
);

-- ALERTAS
CREATE TABLE alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL, -- price, profit, loss, win_rate
    
    -- Condiciones
    conditions JSONB NOT NULL, -- {"asset": "EURUSD", "price": ">1.10"}
    
    -- Canales
    notify_email BOOLEAN DEFAULT FALSE,
    notify_telegram BOOLEAN DEFAULT FALSE,
    notify_webhook BOOLEAN DEFAULT FALSE,
    webhook_url TEXT,
    
    is_active BOOLEAN DEFAULT TRUE,
    last_triggered_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ÍNDICES ADICIONALES PARA PERFORMANCE
CREATE INDEX idx_trades_user_date ON trades(user_id, created_at DESC);
CREATE INDEX idx_trades_status_date ON trades(status, created_at DESC);
CREATE INDEX idx_broker_accounts_user ON broker_accounts(user_id, is_active);
CREATE INDEX idx_bot_configs_user ON bot_configs(user_id, is_active);
```

## 🚀 Configuración en Easypanel

### 1. PostgreSQL
```yaml
Servicio: PostgreSQL 16
Nombre: trading-bot-db
Recursos:
  - CPU: 2 cores
  - RAM: 4 GB
  - Storage: 50 GB SSD
Backups: Automáticos diarios
```

### 2. Redis
```yaml
Servicio: Redis 7
Nombre: trading-bot-cache
Recursos:
  - CPU: 1 core
  - RAM: 2 GB
Persistencia: RDB + AOF
```

### 3. MongoDB (Opcional)
```yaml
Servicio: MongoDB 7
Nombre: trading-bot-logs
Recursos:
  - CPU: 1 core
  - RAM: 2 GB
  - Storage: 20 GB
```

## 💰 Planes de Suscripción Sugeridos

### Free (Gratis)
- 1 bot activo
- 10 trades/día
- Capital máximo: $5/trade
- Datos históricos: 7 días
- Sin IA avanzada

### Basic ($29/mes)
- 3 bots activos
- 50 trades/día
- Capital máximo: $20/trade
- Datos históricos: 30 días
- IA básica

### Pro ($99/mes)
- 10 bots activos
- 200 trades/día
- Capital máximo: $100/trade
- Datos históricos: 1 año
- IA avanzada + Backtesting

### Enterprise ($299/mes)
- Bots ilimitados
- Trades ilimitados
- Sin límite de capital
- Datos históricos: Ilimitado
- IA premium + API + Soporte prioritario

## 📊 Estimación de Costos (Easypanel)

```
PostgreSQL 16 (4GB RAM, 50GB):  $20/mes
Redis 7 (2GB RAM):              $10/mes
MongoDB 7 (2GB RAM, 20GB):      $15/mes
Backend (2GB RAM):              $10/mes
Frontend (1GB RAM):             $8/mes
S3/Spaces (100GB):              $5/mes
-------------------------------------------
TOTAL:                          $68/mes

Con 100 usuarios pagando $29/mes = $2,900/mes
Margen: $2,832/mes (97%)
```

## 🔐 Seguridad

1. **Encriptación de credenciales de brokers**
```python
from cryptography.fernet import Fernet

def encrypt_password(password: str, key: bytes) -> str:
    f = Fernet(key)
    return f.encrypt(password.encode()).decode()

def decrypt_password(encrypted: str, key: bytes) -> str:
    f = Fernet(key)
    return f.decrypt(encrypted.encode()).decode()
```

2. **Rate limiting por usuario**
```python
# Redis
key = f"rate_limit:{user_id}:{endpoint}"
requests = redis.incr(key)
if requests == 1:
    redis.expire(key, 60)  # 1 minuto
if requests > limit:
    raise HTTPException(429, "Too many requests")
```

3. **Backups automáticos**
```bash
# Backup diario de PostgreSQL
pg_dump -U user tradingbot | gzip > backup_$(date +%Y%m%d).sql.gz

# Subir a S3/Spaces
aws s3 cp backup_*.sql.gz s3://backups/
```

## 📈 Escalabilidad

### Fase 1: 0-100 usuarios
- 1 instancia de cada servicio
- Costo: ~$70/mes

### Fase 2: 100-1000 usuarios
- PostgreSQL: Escalar a 8GB RAM
- Redis: Cluster con 2 nodos
- Backend: 3 instancias (load balancer)
- Costo: ~$200/mes

### Fase 3: 1000+ usuarios
- PostgreSQL: Read replicas
- Redis: Cluster con 3+ nodos
- Backend: Auto-scaling
- CDN para frontend
- Costo: ~$500-1000/mes

## 🎯 Recomendación Final

**Para empezar (MVP)**:
- ✅ PostgreSQL (datos principales)
- ✅ Redis (cache + real-time)
- ❌ MongoDB (no necesario al inicio)

**Cuando escales (100+ usuarios)**:
- ✅ Agregar MongoDB para logs
- ✅ Implementar read replicas
- ✅ CDN para assets estáticos
- ✅ Monitoring con Grafana

**Base de datos ideal**: **PostgreSQL + Redis**
- Cubre el 95% de necesidades
- Más económico
- Más fácil de mantener
- Excelente performance
