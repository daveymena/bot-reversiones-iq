# 💎 SELECTOR MULTI-DIVISA INTELIGENTE

## Concepto

El bot ahora **NO opera un solo activo**. En su lugar:

1. 🔍 **Monitorea múltiples activos simultáneamente**
2. 📊 **Analiza cada uno en tiempo real**
3. 🎯 **Elige el que tiene mejor oportunidad**
4. ⚡ **Opera en el momento perfecto**

## Funcionamiento

### Fase 1: Inicialización
```
Bot inicia → Escanea activos OTC disponibles → Selecciona top 5 para monitoreo
```

### Fase 2: Monitoreo Continuo
```
Cada ciclo:
  Para cada activo monitoreado:
    - Obtener datos recientes
    - Calcular indicadores
    - Analizar oportunidad
    - Asignar score (0-100)
```

### Fase 3: Selección Inteligente
```
Comparar todos los activos → Elegir el de mayor score → Operar si score > 50
```

## Sistema de Scoring

Cada activo recibe un score basado en:

### 1. RSI (30 puntos)
- RSI < 30 (sobreventa) → +30 puntos → CALL
- RSI > 70 (sobrecompra) → +30 puntos → PUT
- RSI neutral (40-60) → +10 puntos

### 2. MACD (20 puntos)
- MACD alcista → +20 puntos → CALL
- MACD bajista → +20 puntos → PUT

### 3. Bollinger Bands (20 puntos)
- Precio en BB inferior → +20 puntos → CALL
- Precio en BB superior → +20 puntos → PUT

### 4. Tendencia (15 puntos)
- SMA 20 > SMA 50 → +15 puntos (alcista)
- SMA 20 < SMA 50 → +15 puntos (bajista)

### 5. Volatilidad (15 puntos)
- Alta volatilidad → +15 puntos
- Baja volatilidad → +10 puntos

**Score mínimo para operar: 50/100**

## Ejemplo de Escaneo

```
🔍 ESCANEANDO MÚLTIPLES ACTIVOS...

EURUSD-OTC: 45/100 (RSI neutral, MACD alcista)
GBPUSD-OTC: 75/100 (RSI sobreventa, MACD alcista, BB inferior) ✅
USDJPY-OTC: 30/100 (señales mixtas)
AUDUSD-OTC: 55/100 (tendencia clara, volatilidad alta)

💎 MEJOR OPORTUNIDAD ENCONTRADA:
   Activo: GBPUSD-OTC
   Score: 75/100
   Acción: CALL
   Confianza: 75%
   Razón: RSI sobreventa, MACD alcista, Precio en BB inferior
```

## Activos Monitoreados

### OTC (24/7)
- EURUSD-OTC
- GBPUSD-OTC
- USDJPY-OTC
- AUDUSD-OTC
- USDCAD-OTC
- EURJPY-OTC
- EURGBP-OTC
- GBPJPY-OTC
- AUDJPY-OTC

### Normales (Horario de Mercado)
- EURUSD
- GBPUSD
- USDJPY
- AUDUSD
- USDCAD
- EURJPY

## Ventajas

✅ **Más Oportunidades**: No espera a que un solo activo tenga señal
✅ **Mejor Timing**: Opera cuando hay oportunidad clara
✅ **Diversificación**: No depende de un solo par
✅ **Mayor Efectividad**: Elige el mejor momento de cada activo
✅ **Adaptabilidad**: Se ajusta a condiciones del mercado

## Flujo Completo

```
1. Bot inicia
   ↓
2. Escanea activos disponibles
   ↓
3. Monitorea top 5 activos
   ↓
4. Cada ciclo:
   - Analiza todos los activos
   - Calcula scores
   - Elige el mejor
   ↓
5. Si score > 50:
   - Groq analiza timing
   - Valida decisión
   - Ejecuta operación
   ↓
6. Vuelve a escanear
```

## Configuración

El modo multi-divisa está **activado por defecto**. No requiere configuración adicional.

Para desactivarlo (no recomendado):
```python
# En core/asset_manager.py
self.multi_asset_mode = False
```

## Logs del Bot

```
🔍 Inicializando modo multi-divisa...
✅ 5 activos disponibles para monitoreo

🔍 ESCANEANDO MÚLTIPLES ACTIVOS...
💎 MEJOR OPORTUNIDAD ENCONTRADA:
   Activo: GBPUSD-OTC
   Score: 75/100
   Acción: CALL
   Confianza: 75%
   Razón: RSI sobreventa, MACD alcista, Precio en BB inferior

⏱️ Groq analizando timing óptimo...
   Momento óptimo: ✅ SÍ
   Confianza: 85%
   Expiración recomendada: 2 min
   Razón: Momentum fuerte, volatilidad alta

🚀 Ejecutando CALL en GBPUSD-OTC
   Monto: $10.00
   Expiración: 2 min
```

## Resultado

El bot ahora es **mucho más inteligente**:
- No espera pasivamente a que un activo dé señal
- Busca activamente la mejor oportunidad
- Opera en el momento perfecto
- Maximiza probabilidad de éxito
