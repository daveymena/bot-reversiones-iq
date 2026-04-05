# 🔧 SOLUCIÓN: Bot Se Queda Esperando Resultado

## ⚠️ PROBLEMA

El bot ejecuta una operación pero se queda esperando el resultado indefinidamente.

**Causa**: El método `check_win_v4` espera que Exnova envíe el resultado por websocket, pero a veces no llega.

---

## ✅ SOLUCIÓN ACTUAL

El código YA tiene una solución implementada:

```python
# En core/trader.py línea 1374:
result_status, profit = self.market_data.api.check_win_v4(trade['id'], timeout=90)

# Si timeout (90 segundos), calcula por precio:
if result_status is None:
    profit = self._calculate_profit_by_price(trade)
```

---

## 🔍 DIAGNÓSTICO

### Posibles Causas

1. **Timeout muy largo** (90 segundos)
   - El bot espera 90s antes de calcular por precio
   - Parece que se queda "trabado"

2. **Websocket no recibe resultado**
   - Exnova no envía el resultado por websocket
   - `socket_option_closed` nunca se actualiza

3. **Operación no se ejecutó realmente**
   - El broker rechazó la operación
   - Pero el bot cree que sí se ejecutó

---

## 💡 SOLUCIONES

### Solución 1: Reducir Timeout (RÁPIDO)

Cambiar timeout de 90s a 30s:

```python
# Línea 1374 en core/trader.py
result_status, profit = self.market_data.api.check_win_v4(trade['id'], timeout=30)
```

**Ventaja**: Más rápido, no espera tanto  
**Desventaja**: Puede calcular resultado antes de que termine

### Solución 2: Calcular Siempre por Precio (CONFIABLE)

No esperar resultado del broker, calcular directamente:

```python
# Después de ejecutar operación
time.sleep(expiration_minutes * 60 + 5)  # Esperar expiración + 5s
profit = self._calculate_profit_by_price(trade)
```

**Ventaja**: Siempre funciona, no depende de websocket  
**Desventaja**: Menos preciso que resultado oficial

### Solución 3: Polling Activo (HÍBRIDO)

Consultar activamente al broker cada 5 segundos:

```python
for i in range(expiration_minutes * 12):  # 12 checks por minuto
    time.sleep(5)
    result = self.market_data.api.get_betinfo(trade['id'])
    if result:
        break
```

**Ventaja**: Balance entre velocidad y precisión  
**Desventaja**: Más llamadas al API

---

## 🎯 RECOMENDACIÓN

**Implementar Solución 1** (reducir timeout a 30s):

1. Es rápido de implementar
2. No cambia la lógica actual
3. Reduce tiempo de espera
4. Ya tiene fallback a cálculo por precio

---

## 🔧 IMPLEMENTACIÓN

¿Quieres que implemente la Solución 1 (reducir timeout a 30s)?

Esto hará que el bot:
- Espere máximo 30s por resultado oficial
- Si no llega, calcule por precio automáticamente
- Continue operando sin quedarse trabado

---

**Preparado por**: Kiro AI  
**Fecha**: 04 Abril 2026, 18:00 GMT  
**Recomendación**: Reducir timeout de 90s a 30s
