# 🔴 Cómo Cambiar el Bot a Modo REAL

## ⚠️ ADVERTENCIA IMPORTANTE
**Operar en modo REAL usa dinero real. Asegúrate de estar listo antes de cambiar.**

---

## 📋 Pasos para Cambiar a Modo REAL

### 1. Editar el archivo `.env`

Abre el archivo `.env` en la raíz del proyecto y cambia:

```env
# Cambiar de PRACTICE a REAL
ACCOUNT_TYPE=REAL
```

### 2. Guardar y Reiniciar el Bot

Después de cambiar el archivo `.env`:
1. **Guarda** el archivo
2. **Cierra** el bot si está corriendo
3. **Reinicia** el bot con:
   ```bash
   python main.py
   ```

### 3. Verificar la Conexión

Al iniciar, deberías ver:
```
✅ Conectado a EXNOVA (REAL)
```

Si ves `(PRACTICE)`, el cambio no se aplicó correctamente.

---

## 🔄 Cambiar de Vuelta a PRACTICE

Para volver al modo seguro de práctica:

```env
ACCOUNT_TYPE=PRACTICE
```

Y reinicia el bot.

---

## 🛡️ Recomendaciones de Seguridad

### Antes de Operar en REAL:

1. ✅ **Prueba en PRACTICE** por al menos 1 semana
2. ✅ **Verifica Win Rate** > 60% en modo práctica
3. ✅ **Revisa el capital** disponible en tu cuenta real
4. ✅ **Ajusta CAPITAL_PER_TRADE** en `config.py` a un monto pequeño ($1-$5)
5. ✅ **Monitorea constantemente** las primeras operaciones

### Durante Operaciones REAL:

- 👁️ **Supervisa activamente** el bot
- 🛑 **Detén el bot** si ves comportamiento extraño
- 📊 **Revisa los logs** regularmente
- 💰 **No arriesgues más del 1-2%** de tu capital por operación

---

## 🔍 Verificar Modo Actual

Para verificar en qué modo está operando el bot:

1. Mira el log de inicio:
   ```
   ✅ Conectado a EXNOVA (PRACTICE)  ← Modo práctica
   ✅ Conectado a EXNOVA (REAL)      ← Modo real
   ```

2. Revisa el balance en el broker:
   - **PRACTICE**: Balance virtual (generalmente $10,000)
   - **REAL**: Tu balance real de dinero

---

## ❌ Problemas Comunes

### El bot sigue en PRACTICE después de cambiar

**Solución:**
1. Verifica que guardaste el archivo `.env`
2. Asegúrate de reiniciar completamente el bot
3. Revisa que no haya espacios extra en `.env`:
   ```env
   ACCOUNT_TYPE=REAL  ✅ Correcto
   ACCOUNT_TYPE = REAL  ❌ Incorrecto (espacios)
   ```

### Error de conexión al cambiar a REAL

**Posibles causas:**
- Tu cuenta real no está activada en el broker
- Necesitas verificar tu identidad en el broker
- Fondos insuficientes en la cuenta real

---

## 📞 Soporte

Si tienes problemas cambiando a modo REAL:
1. Revisa los logs del bot
2. Verifica tu cuenta en el broker
3. Contacta al soporte del broker si es necesario

---

## 🎯 Configuración Recomendada para REAL

En `config.py`, ajusta estos valores para modo REAL:

```python
# Configuración conservadora para REAL
CAPITAL_PER_TRADE = 1.0      # Empezar con $1
STOP_LOSS_PCT = 0.05         # Detener si pierdes 5% del día
TAKE_PROFIT_PCT = 0.10       # Objetivo: 10% de ganancia diaria
```

---

**Última actualización:** 2025-11-25
