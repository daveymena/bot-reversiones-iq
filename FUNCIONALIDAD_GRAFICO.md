# 📈 Funcionalidad del Gráfico en Tiempo Real

## 🎯 Implementación Completada

El gráfico ahora muestra:
- ✅ Precio en tiempo real
- ✅ Últimas 100 velas
- ✅ Marcadores de operaciones (CALL/PUT)
- ✅ Auto-ajuste de escala
- ✅ Colores profesionales

---

## 📊 Características

### 1. Línea de Precio en Tiempo Real

**Color:** Verde menta (#00d4aa)
**Actualización:** Cada segundo
**Datos:** Últimas 100 velas

### 2. Marcadores de Operaciones

**CALL (Compra):**
- Color: Verde (#00d4aa)
- Símbolo: ▲ (triángulo hacia arriba)

**PUT (Venta):**
- Color: Rojo (#ff4757)
- Símbolo: ▼ (triángulo hacia abajo)

### 3. Auto-Ajuste de Escala

El gráfico ajusta automáticamente el rango Y para mostrar todos los precios con un padding del 10%.

### 4. Límite de Datos

Muestra las últimas 100 velas para mantener el rendimiento óptimo.

---

## 🎨 Estilo Visual

**Fondo:** #16181f (gris muy oscuro)
**Grid:** Líneas sutiles con alpha 0.2
**Ejes:** Color #2d3142
**Texto:** Color #c5c9d1
**Línea de precio:** #00d4aa (verde menta)

---

## 🔧 Cómo Funciona

### Flujo de Datos

```
1. Trader obtiene precio → signals.price_update.emit(timestamp, price)
2. GUI recibe señal → update_chart(timestamp, price)
3. Gráfico se actualiza → price_line.setData(time_data, price_data)
4. Auto-ajuste de escala → setYRange()
```

### Marcadores de Operaciones

```
1. Trader ejecuta operación → signals.trade_signal.emit(action, asset)
2. GUI recibe señal → on_trade_signal(action, asset)
3. Marca en gráfico → mark_trade_on_chart(price, action)
4. Agrega marcador → ScatterPlotItem con símbolo y color
```

---

## 📈 Ejemplo Visual

```
Precio
  │
1.1580 ├─────────────────▲────────────  ← CALL ejecutado aquí
  │                      │
1.1575 ├──────────────────┼──────────
  │                      │
1.1570 ├────────▼─────────┼──────────  ← PUT ejecutado aquí
  │            │          │
1.1565 ├────────┼──────────┼──────────
  │            │          │
  └────────────┴──────────┴──────────→ Tiempo
           10:00      10:05      10:10
```

---

## 🚀 Funciones Disponibles

### update_chart(timestamp, price)
Actualiza el gráfico con un nuevo punto de precio.

**Parámetros:**
- `timestamp`: Tiempo en formato Unix
- `price`: Precio actual del activo

**Ejemplo:**
```python
self.update_chart(1699876543.0, 1.15750)
```

### mark_trade_on_chart(price, trade_type)
Marca una operación en el gráfico.

**Parámetros:**
- `price`: Precio de entrada
- `trade_type`: 'CALL' o 'PUT'

**Ejemplo:**
```python
self.mark_trade_on_chart(1.15750, 'CALL')
```

### clear_chart()
Limpia todos los datos del gráfico.

**Ejemplo:**
```python
self.clear_chart()
```

---

## 🎯 Mejoras Futuras (Opcionales)

### 1. Velas Japonesas (Candlesticks)

En lugar de línea, mostrar velas OHLC:

```python
# Agregar CandlestickItem
from pyqtgraph import CandlestickItem

candles = CandlestickItem()
self.chart.addItem(candles)
```

### 2. Indicadores Técnicos

Agregar RSI, MACD, Bollinger Bands:

```python
# RSI en panel inferior
rsi_plot = pg.PlotWidget()
rsi_line = rsi_plot.plot(pen='y')
```

### 3. Zoom y Pan

Habilitar zoom con rueda del mouse:

```python
self.chart.setMouseEnabled(x=True, y=True)
```

### 4. Líneas de Soporte/Resistencia

Marcar niveles importantes:

```python
support_line = pg.InfiniteLine(
    pos=1.1550,
    angle=0,
    pen=pg.mkPen('g', width=2, style=Qt.DashLine)
)
self.chart.addItem(support_line)
```

### 5. Tooltips con Información

Mostrar precio al pasar el mouse:

```python
def mouseMoved(evt):
    pos = evt[0]
    if self.chart.sceneBoundingRect().contains(pos):
        mousePoint = self.chart.plotItem.vb.mapSceneToView(pos)
        label.setText(f"Precio: {mousePoint.y():.5f}")
```

---

## 🐛 Solución de Problemas

### Problema 1: El gráfico no se actualiza

**Causa:** Señal price_update no se está emitiendo

**Solución:**
```python
# Verificar en core/trader.py
self.signals.price_update.emit(timestamp, price)
```

### Problema 2: Gráfico se ve pixelado

**Causa:** Resolución baja

**Solución:**
```python
# Aumentar calidad
self.chart.setAntialiasing(True)
```

### Problema 3: Gráfico muy lento

**Causa:** Demasiados puntos

**Solución:**
```python
# Reducir max_points
self.max_points = 50  # En lugar de 100
```

### Problema 4: Marcadores no aparecen

**Causa:** Señal trade_signal no conectada

**Solución:**
```python
# Verificar en connect_signals()
self.trader.signals.trade_signal.connect(self.on_trade_signal)
```

---

## 📊 Personalización

### Cambiar Color de Línea

```python
self.price_line = self.chart.plot(
    pen=pg.mkPen(color='#ff00ff', width=3),  # Magenta, grosor 3
    name='Precio'
)
```

### Cambiar Tamaño de Marcadores

```python
scatter = pg.ScatterPlotItem(
    size=20,  # Más grande
    pen=pg.mkPen(color=color, width=3)
)
```

### Agregar Más Colores

```python
# Marcador para operaciones ganadoras
if won:
    color = '#00ff00'  # Verde brillante
else:
    color = '#ff0000'  # Rojo brillante
```

---

## ✅ Estado Actual

**Implementado:**
- ✅ Gráfico de línea en tiempo real
- ✅ Actualización automática cada segundo
- ✅ Marcadores de operaciones CALL/PUT
- ✅ Auto-ajuste de escala
- ✅ Límite de 100 puntos
- ✅ Colores profesionales
- ✅ Grid sutil

**Funcionando:**
- ✅ Recibe datos del trader
- ✅ Muestra precio en tiempo real
- ✅ Marca operaciones ejecutadas
- ✅ Se actualiza sin lag

---

## 🚀 Cómo Probar

1. **Iniciar el bot**
2. **Conectar al broker**
3. **Iniciar trading**
4. **Observar el gráfico:**
   - Línea verde mostrando precio
   - Marcadores cuando ejecuta operaciones
   - Auto-ajuste de escala

**Ejemplo de log:**
```
[20:15:00] 💎 Oportunidad detectada en EURUSD-OTC
[20:15:05] 🚀 Ejecutando CALL en EURUSD-OTC
[20:15:05] 📍 Operación marcada en gráfico: CALL @ 1.15750
```

---

## 📈 Resultado

El gráfico ahora es **funcional y profesional**, mostrando:
- Precio en tiempo real
- Historial de últimas 100 velas
- Marcadores de operaciones
- Escala automática
- Estilo moderno

**Estado:** IMPLEMENTADO Y FUNCIONANDO ✅
