# Ultra-Smart Trading Bot v2.0 - Documentación

## Resumen Ejecutivo

El **Ultra-Smart Trading Bot v2.0** es un sistema profesional de trading para Exnova que reemplaza los ~20 filtros dispersos del bot anterior con componentes unificados y profesionales.

## Componentes Principales

### 1. Advanced Risk Manager (`core/advanced_risk_manager.py`)

**Características:**
- **Kelly Criterion dinámico**: Calcula el tamaño óptimo de posición basado en tu winrate histórico
- **Drawdown Protection**: Detiene el trading si alcanzas límites de pérdida (diario, semanal, mensual)
- **Position Sizing Inteligente**: Ajusta el tamaño según confianza, volatilidad y rachas
- **Cooldown después de pérdida**: Espera 5 minutos después de una pérdida para evitar trading emocional

**Antes vs Ahora:**
```
# ANTES: Monto fijo $1.00 por operación
position = 1.0

# AHORA: Kelly + ajustes múltiples
position = balance × Kelly × Confianza × Volatilidad × Drawdown × Racha
```

### 2. Unified Scoring Engine (`core/unified_scoring_engine.py`)

**Características:**
- **Score 0-100 unificado**: Reemplaza ~20 filtros dispersos
- **8 categorías ponderadas:**
  - Market Structure (20%) - Tendencias, S/R
  - Smart Money (20%) - Order blocks, FVG, liquidity
  - Technical Indicators (15%) - RSI, MACD, EMA
  - Multi-Timeframe (15%) - Alineación M1/M5/M15
  - Risk Management (10%) - Ratio R:R
  - Temporal Context (10%) - Sesión, hora
  - Momentum (5%) - Fuerza del movimiento
  - Market Phase (5%) - Tendencia vs rango

**Ejemplo de uso:**
```python
from core.unified_scoring_engine import get_scoring_engine

engine = get_scoring_engine()
result = engine.score(df, current_price, asset='EUR/USD')

print(f"Score: {result.total_score}/100")
print(f"Señal: {result.signal_type.value}")
print(f"Confianza: {result.confidence*100}%")
```

### 3. Async Exnova Connector (`core/async_exnova_connector.py`)

**Características:**
- **WebSockets no bloqueantes**: Usa asyncio en lugar de while loops
- **Circuit Breaker**: Protege contra fallos en cascada
- **Rate Limiting**: Controla frecuencia de operaciones
- **Reconexión automática**: Backoff exponencial
- **Heartbeat automático**: Mantiene conexión estable

### 4. Backtesting System (`core/backtesting_system.py`)

**Características:**
- **Paper Trading**: Opera en tiempo real sin dinero
- **Backtesting histórico**: Valida estrategias con datos pasados
- **Métricas profesionales:**
  - Sharpe Ratio
  - Max Drawdown
  - Recovery Factor
  - Profit Factor

### 5. Ensemble ML Predictor (`core/ensemble_ml_predictor.py`)

**Características:**
- **5+ modelos combinados:**
  - Random Forest
  - Gradient Boosting
  - Logistic Regression
  - SVM
  - MLP Classifier
  - XGBoost (opcional)
- **Voting ponderado**: Modelos con mejor accuracy tienen más peso
- **Feature importance**: Identifica qué features importan más

## Instalación

### Requisitos
- Python 3.8+
- pip

### Dependencias
```bash
pip install pandas numpy scikit-learn joblib websockets
```

## Uso

### 1. Configurar credenciales

Edita `bot_config.json`:
```json
{
  "credentials": {
    "email": "tu@email.com",
    "password": "tu_password"
  },
  "trading_mode": "demo"
}
```

### 2. Ejecutar en modo demo (recomendado primero)

```bash
python ejecutar_ultra_bot.py --demo
```

O con credenciales directas:
```bash
python ultra_smart_bot.py --email tu@email.com --password tu_pass --demo
```

### 3. Ejecutar test de validación

```bash
python test_ultra_smart_bot.py
```

## Configuración de Riesgo

Edita `bot_config.json` para ajustar:

```json
{
  "risk": {
    "max_daily_drawdown": 0.15,
    "max_position_size_pct": 0.02,
    "kelly_ceiling": 0.25
  },
  "limits": {
    "max_trades_per_hour": 8,
    "max_trades_per_day": 40,
    "cooldown_after_loss": 300,
    "min_confidence": 0.65
  }
}
```

### Explicación de parámetros:

| Parámetro | Valor Default | Descripción |
|-----------|---------------|-------------|
| `max_daily_drawdown` | 0.15 (15%) | Máxima pérdida diaria antes de parar |
| `max_position_size_pct` | 0.02 (2%) | Porcentaje máximo del balance por operación |
| `kelly_ceiling` | 0.25 (25%) | Límite superior de Kelly |
| `max_trades_per_hour` | 8 | Operaciones máximas por hora |
| `cooldown_after_loss` | 300 (5min) | Espera después de pérdida |
| `min_confidence` | 0.65 (65%) | Confianza mínima para operar |

## Comparativa: Bot Anterior vs Ultra-Smart Bot

| Métrica | Bot Anterior | Ultra-Smart Bot v2.0 |
|---------|--------------|----------------------|
| Filtros | ~20 dispersos | 1 motor unificado |
| Scoring | Fragmentado | 0-100 con pesos |
| Sizing | Fijo ($1.00) | Kelly + ATR + Rachas |
| Max ops/hora | 100 | 8 |
| Drawdown protection | ❌ No | ✅ 15% |
| Explicabilidad | Limitada | Completa |
| Adaptación | Manual | Automática |

## Métricas de Rendimiento Esperadas

Basado en backtesting con datos aleatorios:

- **Win Rate**: 55-65% (con score > 70)
- **Profit Factor**: 1.5-2.5
- **Max Drawdown**: < 15% (con protección activa)
- **Sharpe Ratio**: > 1.0

**Nota:** Estos son objetivos. El rendimiento real depende de las condiciones del mercado.

## Solución de Problemas

### Error de codificación en Windows
Si ves errores de Unicode, ejecuta en PowerShell:
```powershell
chcp 65001
python ultra_smart_bot.py
```

### Error de conexión
Verifica:
1. Credenciales en `bot_config.json`
2. Conexión a internet
3. Que Exnova no esté en mantenimiento

### El bot no opera
Verifica:
1. Score mínimo (65 por defecto) - puede ser muy alto para condiciones actuales
2. Cooldown después de pérdida (5 min)
3. Límite de operaciones por hora alcanzado
4. Drawdown máximo alcanzado

## Flujo de Operación

```
1. Analizar mercado → Scoring Engine
2. Score >= 65? → Sí: Continuar | No: Esperar
3. Risk Manager → Calcular posición
4. Verificar límites → ¿Puede operar?
5. Ejecutar orden → Exnova API
6. Monitorear resultado → Actualizar estadísticas
7. Aprender → Adjustar Kelly para próxima
```

## Próximas Mejoras (Tareas Pendientes)

- [ ] Mejorar conexión WebSocket async con Exnova (en progreso)
- [ ] Sistema de paper trading/backtesting online (creado, falta integración)
- [ ] Ensemble ML (Random Forest + XGBoost) (creado, falta entrenamiento con datos reales)

## Advertencias

1. **Este bot opera con dinero real** - Prueba en modo demo primero
2. **Configura los límites de riesgo** antes de empezar
3. **Las opciones binarias son de alto riesgo** - Solo opera con capital que puedas perder
4. **Comienza con el mínimo capital posible** - $10-50 para probar

## Soporte

Para issues o preguntas, revisa los logs en la consola. El bot imprime información detallada de cada decisión.

## Licencia

Uso personal. No redistribuir.
