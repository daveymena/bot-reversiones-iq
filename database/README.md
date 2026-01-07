# Base de Datos para Bot de Trading Inteligente

## 🎯 Objetivo

Crear una base de datos profesional que permita al bot:
- ✅ **Aprender de verdad** de cada operación
- ✅ **Identificar patrones** que funcionan y que no
- ✅ **Detectar errores recurrentes** y evitarlos
- ✅ **Evolucionar estrategias** basándose en datos reales
- ✅ **Adaptarse a diferentes condiciones** de mercado

## 📊 Estructura de la Base de Datos

### Tablas Principales

#### 1. `trades` - Operaciones Ejecutadas
Registra TODA la información de cada operación:
- Datos básicos (asset, dirección, monto, duración)
- Precios de entrada/salida
- Resultado (win/loss) y profit
- **Contexto del mercado** al momento de entrar
- **Confianza del RL agent** y análisis del LLM
- Score de la decisión

**¿Por qué es importante?**
- Permite analizar qué condiciones llevaron a wins/losses
- Identifica patrones de éxito
- Detecta cuándo el bot está muy confiado pero se equivoca

#### 2. `market_conditions` - Condiciones del Mercado
Guarda el estado completo del mercado cada minuto:
- Todos los indicadores técnicos (RSI, MACD, Bollinger, etc.)
- Medias móviles (SMA, EMA)
- Volatilidad (ATR)
- Patrones detectados
- Smart Money Concepts (order blocks, FVG, liquidity zones)

**¿Por qué es importante?**
- Permite entrenar el modelo con datos históricos reales
- Identifica qué indicadores son más predictivos
- Detecta condiciones de mercado favorables/desfavorables

#### 3. `learning_experiences` - Experiencias de Aprendizaje
Cada decisión del bot se guarda como experiencia:
- Estado antes de la decisión
- Acción tomada
- Recompensa obtenida
- Estado después
- **Si fue correcta o no**
- **Tipo de error** si falló
- **Lección aprendida**

**¿Por qué es importante?**
- Es el corazón del aprendizaje del RL agent
- Permite re-entrenar con experiencias reales
- Identifica qué decisiones fueron buenas/malas

#### 4. `pattern_performance` - Rendimiento de Patrones
Trackea el rendimiento de cada patrón detectado:
- Tipo de patrón (RSI oversold, MACD cross, etc.)
- Cuántas veces apareció
- Win rate del patrón
- Profit promedio
- **Condiciones donde funciona mejor**
- **Condiciones donde falla**

**¿Por qué es importante?**
- Identifica patrones confiables vs no confiables
- Permite ajustar pesos de cada patrón
- Evita operar en patrones que no funcionan

#### 5. `decision_logs` - Log de Decisiones
Registra CADA decisión del bot (ejecutada o no):
- Predicción del RL agent
- Análisis técnico
- Recomendación del LLM
- Validación multi-capa
- **Decisión final y razón**

**¿Por qué es importante?**
- Permite auditar todas las decisiones
- Identifica cuándo el bot rechaza buenas oportunidades
- Detecta falsos positivos

#### 6. `error_patterns` - Patrones de Errores
Identifica errores recurrentes:
- Tipo de error (false signal, bad timing, etc.)
- Frecuencia
- **Condiciones comunes** cuando ocurre
- Impacto económico
- **Solución propuesta**

**¿Por qué es importante?**
- Evita cometer los mismos errores
- Permite implementar filtros específicos
- Reduce pérdidas sistemáticas

#### 7. `strategy_evolution` - Evolución de Estrategias
Trackea diferentes versiones de estrategias:
- Configuración de cada estrategia
- Resultados de pruebas
- Comparación con versión anterior
- Estado (testing, approved, active)

**¿Por qué es importante?**
- Permite A/B testing de estrategias
- Identifica mejoras reales vs aleatorias
- Mantiene historial de evolución

#### 8. `market_regime` - Régimen de Mercado
Detecta el tipo de mercado actual:
- Trending up/down, ranging, volatile, calm
- Fuerza del régimen
- **Mejor estrategia para este régimen**

**¿Por qué es importante?**
- Adapta la estrategia al tipo de mercado
- Evita operar en condiciones desfavorables
- Maximiza profit en condiciones favorables

## 🚀 Instalación

### 1. Instalar PostgreSQL

**Windows:**
```bash
# Descargar de: https://www.postgresql.org/download/windows/
# O usar Docker (recomendado)
docker run --name trading-postgres -e POSTGRES_PASSWORD=tu_password -p 5432:5432 -d postgres:17
```

**Linux:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

**Mac:**
```bash
brew install postgresql
brew services start postgresql
```

### 2. Instalar TimescaleDB (Extensión para series temporales)

```bash
# Agregar repositorio
sudo add-apt-repository ppa:timescale/timescaledb-ppa
sudo apt update

# Instalar
sudo apt install timescaledb-postgresql-14

# Configurar
sudo timescaledb-tune
```

### 3. Crear Base de Datos

```bash
# Conectar a PostgreSQL
psql -U postgres

# Crear base de datos
CREATE DATABASE trading_bot;

# Conectar a la base de datos
\c trading_bot

# Crear extensiones
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "timescaledb";

# Ejecutar schema
\i database/schema.sql
```

### 4. Configurar Variables de Entorno

Agregar a tu `.env`:

```bash
# Base de Datos
DB_HOST=localhost
DB_PORT=5432
DB_NAME=trading_bot
DB_USER=postgres
DB_PASSWORD=tu_password
```

### 5. Instalar Dependencias Python

```bash
pip install psycopg2-binary
```

## 📝 Uso

### Inicializar el Gestor

```python
from database.db_manager import db

# El gestor se conecta automáticamente
```

### Guardar un Trade

```python
trade_data = {
    'trade_id': 'EXNOVA_12345',
    'asset': 'EURUSD-OTC',
    'direction': 'call',
    'amount': 10.0,
    'duration': 1,
    'entry_price': 1.08523,
    'entry_time': datetime.now(),
    'market_context': {
        'rsi': 45.2,
        'macd': 0.0012,
        'trend': 'bullish'
    },
    'rl_confidence': 75.5,
    'llm_analysis': 'Condiciones favorables para CALL',
    'decision_score': 82,
    'broker': 'exnova',
    'account_type': 'PRACTICE',
    'session_id': None
}

trade_uuid = db.save_trade(trade_data)
```

### Actualizar Resultado

```python
db.update_trade_result(
    trade_id='EXNOVA_12345',
    result='win',
    exit_price=1.08545,
    profit=8.5,
    exit_time=datetime.now()
)
```

### Guardar Experiencia de Aprendizaje

```python
experience = {
    'trade_id': trade_uuid,
    'state': {
        'rsi': 45.2,
        'macd': 0.0012,
        'price': 1.08523
    },
    'action': 'call',
    'action_confidence': 75.5,
    'reward': 0.85,  # Normalizado
    'next_state': {
        'rsi': 46.1,
        'macd': 0.0015,
        'price': 1.08545
    },
    'was_correct': True,
    'error_type': None,
    'lesson': 'RSI en zona neutral con MACD positivo es buena señal',
    'should_avoid': False,
    'model_version': 'v1.0'
}

db.save_experience(experience)
```

### Obtener Estadísticas

```python
# Rendimiento últimos 7 días
stats = db.get_performance_stats(days=7)
print(f"Win Rate: {stats['win_rate']}%")
print(f"Total Profit: ${stats['total_profit']}")

# Mejores patrones
best_patterns = db.get_best_patterns(min_occurrences=10)
for pattern in best_patterns:
    print(f"{pattern['pattern_type']}: {pattern['win_rate']}% win rate")

# Errores comunes
errors = db.get_common_errors(limit=5)
for error in errors:
    print(f"{error['error_type']}: {error['occurrences']} veces, ${error['total_loss']} pérdida")
```

## 🎓 Cómo el Bot Aprende

### 1. Aprendizaje por Experiencia

Cada operación genera una experiencia que se guarda en `learning_experiences`:

```
Estado → Acción → Recompensa → Nuevo Estado
```

El modelo RL se re-entrena periódicamente con estas experiencias.

### 2. Aprendizaje de Patrones

Cada patrón detectado se trackea en `pattern_performance`:

```
Patrón detectado → Operación ejecutada → Resultado → Actualizar estadísticas
```

Si un patrón tiene win rate < 50%, el bot deja de usarlo.

### 3. Aprendizaje de Errores

Cada error se analiza y guarda en `error_patterns`:

```
Error detectado → Analizar condiciones → Identificar causa → Proponer solución
```

El bot evita condiciones que históricamente causan errores.

### 4. Adaptación a Régimen de Mercado

El bot detecta el tipo de mercado y adapta su estrategia:

```
Analizar mercado → Detectar régimen → Seleccionar mejor estrategia → Operar
```

## 📊 Queries Útiles

### Ver rendimiento por activo

```sql
SELECT * FROM performance_by_asset;
```

### Ver mejores horas para operar

```sql
SELECT * FROM performance_by_hour
WHERE win_rate > 60
ORDER BY total_profit DESC;
```

### Ver patrones más rentables

```sql
SELECT * FROM best_patterns;
```

### Ver errores más costosos

```sql
SELECT * FROM costly_errors;
```

### Calcular win rate de un período

```sql
SELECT calculate_win_rate('2025-01-01', '2025-01-31', 'EURUSD-OTC');
```

## 🔧 Mantenimiento

### Backup

```bash
# Backup completo
pg_dump -U postgres trading_bot > backup_$(date +%Y%m%d).sql

# Backup solo datos
pg_dump -U postgres --data-only trading_bot > data_backup_$(date +%Y%m%d).sql
```

### Restore

```bash
psql -U postgres trading_bot < backup_20250126.sql
```

### Limpiar datos antiguos

```sql
-- Eliminar market_conditions más antiguos de 90 días
DELETE FROM market_conditions
WHERE timestamp < NOW() - INTERVAL '90 days';

-- Eliminar decision_logs más antiguos de 90 días
DELETE FROM decision_logs
WHERE timestamp < NOW() - INTERVAL '90 days';
```

## 🎯 Próximos Pasos

1. **Integrar con el bot actual**
   - Modificar `core/trader.py` para usar `db_manager`
   - Guardar cada trade en la BD
   - Guardar experiencias para re-entrenamiento

2. **Implementar análisis automático**
   - Script que analiza patrones cada día
   - Identifica errores recurrentes
   - Propone mejoras automáticas

3. **Dashboard de analytics**
   - Visualizar rendimiento en tiempo real
   - Gráficos de evolución
   - Alertas de patrones de error

4. **Sistema de re-entrenamiento automático**
   - Re-entrenar modelo cada semana
   - Usar experiencias de la BD
   - Validar mejora antes de activar

## 📚 Referencias

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [TimescaleDB Documentation](https://docs.timescale.com/)
- [psycopg2 Documentation](https://www.psycopg.org/docs/)
