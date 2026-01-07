# 🎯 Plan: Interfaz Estilo Exnova

## Objetivo
Crear una interfaz que se vea exactamente como Exnova con velas grandes, claras y profesionales.

## Características a Implementar

### 1. Selector de Timeframe
```
[30s] [1m] [5m] [15m] [30m] [1h] [4h] [1d]
```
- Botones en la parte superior del gráfico
- Cambio dinámico de timeframe
- Actualización automática

### 2. Gráfico Principal
- **Velas grandes** (verde brillante / rojo brillante)
- **EMAs overlay** (20, 50, 200)
- **Grid sutil** (líneas grises claras)
- **Fondo oscuro** (#1a1d2e)

### 3. Indicadores Overlay (en el gráfico)
- EMA 20 (naranja)
- EMA 50 (rosa)
- EMA 200 (azul) - opcional

### 4. Subgráfico de Indicadores (pequeño, abajo)
- **ADX** (líneas verde/naranja/roja)
- **RSI** (línea amarilla con niveles 30/70)
- Altura: 20% del gráfico principal

### 5. Panel Superior (Info)
```
📊 EUR/JPY (OTC) | 💰 Precio: 161.7408 | ▲ +8.1% | 📈 SUBE 76%
```

### 6. Diseño Responsive
- Desktop: 3 columnas (izq, centro, der)
- Móvil: 1 columna apilada
- Gráfico siempre visible y grande

## Implementación

### Paso 1: Agregar Selector de Timeframe
- Botones horizontales arriba del gráfico
- Variable `self.current_timeframe`
- Método `change_timeframe()`

### Paso 2: Mejorar Velas
- Aumentar ancho de velas
- Colores más brillantes
- Bordes más definidos

### Paso 3: Agregar Subgráfico
- PlotWidget adicional (20% altura)
- ADX y RSI juntos
- Sincronizado con gráfico principal

### Paso 4: Responsive Design
- QSplitter para paneles ajustables
- Mínimos y máximos de tamaño
- Ocultar paneles en móvil

## Resultado Esperado
Una interfaz que se vea **exactamente como Exnova**:
- Profesional
- Limpia
- Velas grandes y claras
- Indicadores útiles
- Fácil de usar
