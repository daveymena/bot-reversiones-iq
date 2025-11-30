# 🧪 Guía de Prueba del Bot - Paso a Paso

## ✅ Estado Actual
La aplicación GUI está ejecutándose. Deberías ver la ventana del bot en tu pantalla.

## 📋 Pasos para Probar

### PASO 1: Conectar a IQ Option

1. **En el Panel de Conexión (izquierda superior):**
   - ✅ Selecciona: **IQ Option**
   - ✅ Selecciona: **DEMO (Práctica)**
   - ✅ Email: `deinermena25@gmail.com`
   - ✅ Password: `6715320daveymena15.D`
   - ✅ Token: (dejar vacío)

2. **Haz clic en el botón azul "CONECTAR"**

3. **Espera el mensaje en los logs:**
   ```
   ✅ Conectado a IQ OPTION (PRACTICE)
   💰 Balance: $9662.16
   ```

### PASO 2: Configurar Activo

1. **En el mismo panel:**
   - Selecciona **EURUSD** del dropdown
   - ✅ Marca la casilla **"Usar OTC (24/7)"** (importante para operar ahora)

2. **Verifica en los logs:**
   ```
   📊 Activo seleccionado: EURUSD-OTC
   ```

### PASO 3: Configurar Estrategia

1. **En el Panel de Estrategia (izquierda inferior):**
   - ✅ Marca: **Aprendizaje por Refuerzo (RL)**
   - ☐ Deja sin marcar: Scalping y Reversión (por ahora)

### PASO 4: Iniciar el Bot

1. **Haz clic en el botón verde gigante: "INICIAR BOT"**

2. **El botón cambiará a rojo: "DETENER BOT"**

3. **Observa los logs - Deberías ver:**
   ```
   ▶️ Bot INICIADO
   Conectando a IQ OPTION (PRACTICE)...
   ✅ Conectado a IQ OPTION
   💰 Balance (PRACTICE): $9662.16
   📊 Activo seleccionado: EURUSD-OTC
   
   [Auto-Trainer] Descargando datos recientes...
   [Auto-Trainer] Entrenando modelo con datos actuales...
   [Auto-Trainer] Modelo actualizado
   
   [AssetManager] Escaneando activos disponibles...
   [AssetManager] Activo actual: EURUSD-OTC
   
   [LiveTrader] Iniciando ciclo de trading...
   [LiveTrader] Obteniendo velas de EURUSD-OTC...
   [FeatureEngineer] Calculando indicadores técnicos...
   [FeatureEngineer] RSI: XX.XX
   [FeatureEngineer] MACD: X.XXXX
   
   [LLM] Consultando análisis de mercado...
   [LLM] Respuesta: "El mercado muestra..."
   
   [RLAgent] Predicción: CALL/PUT
   [RLAgent] Confianza: XX%
   
   [LiveTrader] Ejecutando operación...
   💰 Operación CALL en EURUSD-OTC por $10
   ```

### PASO 5: Monitorear Operaciones

1. **Panel de Gráficos (centro):**
   - Verás el precio moviéndose en tiempo real (línea amarilla)

2. **Panel de Logs (abajo - pestaña "Logs del Sistema"):**
   - Verás todos los eventos en tiempo real
   - Análisis de indicadores
   - Decisiones del RL
   - Consejos del LLM (Groq)

3. **Panel de Historial (abajo - pestaña "Historial de Operaciones"):**
   - Cuando se cierren operaciones, aparecerán aquí
   - Verás: Hora, Activo, Tipo (CALL/PUT), Resultado, Profit

4. **Panel de Estado (izquierda):**
   - Balance se actualizará en tiempo real
   - Profit Diario mostrará ganancias/pérdidas
   - Racha mostrará operaciones consecutivas
   - Win Rate mostrará % de éxito

## 🔍 Qué Observar

### Análisis Técnico
Busca en los logs:
```
[FeatureEngineer] Indicadores calculados:
  RSI: 45.23 (Neutral)
  MACD: 0.0012 (Alcista)
  Bollinger: Precio cerca de banda inferior
  SMA: Tendencia alcista
```

### Análisis de IA (Groq)
Busca:
```
[LLM] Análisis de mercado:
  "Basándome en los indicadores, el RSI está en zona neutral
   pero el MACD muestra divergencia alcista. Recomiendo esperar
   confirmación de ruptura de resistencia..."
```

### Decisión del RL
Busca:
```
[RLAgent] Decisión:
  Acción: CALL
  Confianza: 78%
  Razón: Convergencia de señales alcistas
```

### Ejecución
Busca:
```
[LiveTrader] Ejecutando operación:
  Activo: EURUSD-OTC
  Dirección: CALL
  Monto: $10.00
  Duración: 1 min
  
✅ Operación ejecutada - ID: 12345678
```

### Resultado
Después de 1 minuto:
```
[TradeAnalyzer] Analizando resultado...
  Precio entrada: 1.05234
  Precio cierre: 1.05256
  
✅ OPERACIÓN GANADA: +$8.50
💰 Nuevo balance: $9670.66
📊 Win Rate: 100%
```

## ⚠️ Si Algo Sale Mal

### "No se conecta"
- Verifica credenciales en el panel
- Revisa los logs para ver el error exacto
- Intenta desconectar y reconectar

### "No ejecuta operaciones"
- Verifica que el botón diga "DETENER BOT" (rojo)
- Asegúrate de que el activo OTC esté seleccionado
- Revisa que haya suficiente balance

### "Error en los logs"
- Copia el error completo
- Revisa si es un problema de datos de mercado
- Intenta cambiar de activo

## 🎯 Métricas de Éxito

Después de 5-10 operaciones, deberías ver:

- ✅ **Win Rate**: >60% (bueno), >70% (excelente)
- ✅ **Profit Diario**: Positivo
- ✅ **Racha**: Máximo 2-3 pérdidas consecutivas
- ✅ **Balance**: Creciendo gradualmente

## 🛑 Detener el Bot

Cuando quieras parar:
1. Haz clic en el botón rojo "DETENER BOT"
2. Espera a que termine la operación actual
3. Verás: `⏸️ Bot PAUSADO`

## 📸 Capturas Recomendadas

Toma screenshots de:
1. Panel completo con operación en curso
2. Logs mostrando análisis de IA
3. Historial con operaciones ganadas
4. Panel de estado con métricas

¡Listo para operar! 🚀
