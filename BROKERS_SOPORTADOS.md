# Brokers Soportados

## ✅ Exnova (Recomendado)

**Estado:** 100% Funcional

**Características:**
- ✅ Activos OTC disponibles 24/7
- ✅ API estable y probada
- ✅ Sin conflictos de dependencias
- ✅ Soporte completo en el bot
- ✅ Cuenta PRACTICE y REAL

**Activos OTC disponibles:**
- EURUSD-OTC
- GBPUSD-OTC
- USDJPY-OTC
- AUDUSD-OTC
- USDCAD-OTC
- EURJPY-OTC
- EURGBP-OTC
- GBPJPY-OTC
- AUDJPY-OTC

**Cómo usar:**
1. Crea cuenta en [Exnova](https://exnova.com)
2. Configura credenciales en `.env` o en la GUI
3. Selecciona `PRACTICE` para pruebas
4. ¡Listo para operar!

---

## ⚠️ IQ Option (No Recomendado)

**Estado:** Conflicto de dependencias

**Problema:**
- IQ Option requiere `websocket-client==1.8.0`
- Exnova funciona con versiones más nuevas
- No pueden coexistir en el mismo entorno

**Solución:**
Si necesitas IQ Option, debes:
1. Crear un entorno virtual separado
2. Instalar solo dependencias de IQ Option
3. Usar una instancia del bot dedicada

**Alternativa recomendada:**
Usa Exnova que tiene mejor soporte y activos OTC 24/7.

---

## 🔮 Futuros Brokers

Planeamos agregar soporte para:
- Quotex
- Pocket Option
- Binomo

Estos brokers serán agregados cuando tengamos APIs estables y sin conflictos de dependencias.

---

## 💡 Recomendación

**Para la mayoría de usuarios:** Usa **Exnova**
- Más estable
- OTC 24/7
- Sin problemas de dependencias
- Mejor documentado

**Solo usa IQ Option si:**
- Ya tienes cuenta con fondos ahí
- Estás dispuesto a mantener un entorno separado
- Entiendes los conflictos de websocket-client
