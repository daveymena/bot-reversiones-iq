# 🤖 Trading Bot Pro - Exnova Edition

Bot de trading automático con IA para opciones binarias en **Exnova**.

## ✨ Características Principales

- 🤖 **Reinforcement Learning (PPO)** - Agente que aprende de operaciones reales
- 🧠 **Análisis LLM (Groq)** - Validación inteligente con IA generativa
- 📊 **Análisis Técnico Avanzado** - RSI, MACD, Bollinger Bands, Smart Money Concepts
- 🎯 **Filtros Inteligentes** - Volatilidad, impulso, timing óptimo de entrada
- 📈 **Gráficos en Tiempo Real** - Visualización profesional con pyqtgraph
- 🔄 **Aprendizaje Continuo** - Se adapta automáticamente a las condiciones del mercado
- 🛡️ **Gestión de Riesgo** - Stop Loss, Take Profit, Martingala Inteligente
- 🌍 **Multi-Activos** - Monitorea 9 pares OTC simultáneamente

## 🚀 Inicio Rápido

**Ejecutar el bot:**
```bash
start.bat
```

### ⚙️ Configuración Actual

| Parámetro | Valor |
|-----------|-------|
| 💰 Monto por operación | $1 |
| 🚫 Martingala | DESHABILITADA |
| ⏰ Horario | 7:00 AM - 11:00 AM |
| 🧠 Aprendizaje | ACTIVO |
| 🏦 Broker | Exnova (REAL) |

### Requisitos

- Python 3.10+
- Cuenta en Exnova
- API Key de Groq (opcional, para análisis LLM)

### Instalación

```bash
# Clonar repositorio
git clone https://github.com/daveymena/bot-reversiones-iq.git
cd bot-reversiones-iq

# Instalar dependencias
pip install -r requirements.txt

# Configurar credenciales en .env
# Editar .env con tus credenciales de Exnova

# Instalar dependencias
pip install -r requirements.txt
```

### Configuración

Crea un archivo `.env` basado en `.env.example`:

```bash
# Credenciales Exnova
EXNOVA_EMAIL=tu@email.com
EXNOVA_PASSWORD=tupassword

# Configuración
ACCOUNT_TYPE=PRACTICE

# LLM (opcional)
GROQ_API_KEY=tu_groq_api_key
USE_LLM=True
```

### Ejecutar

```bash
# Modo recomendado (consola estable)
start.bat

# O alternativas:
EJECUTAR_BOT_CONSOLA.bat
python main_console.py

# Interfaz gráfica (puede ser inestable)
python main_modern.py
```

## 📖 Cómo Usar

1. **Conectar** - Haz clic en "CONECTAR" para conectarte a Exnova
2. **Iniciar** - Haz clic en "INICIAR BOT"
3. **Monitorear** - El bot escaneará oportunidades automáticamente
4. **Operar** - Ejecutará operaciones cuando las condiciones sean óptimas

## 🎯 Activos Soportados (OTC 24/7)

- EURUSD-OTC
- GBPUSD-OTC
- USDJPY-OTC
- AUDUSD-OTC
- USDCAD-OTC
- EURJPY-OTC
- EURGBP-OTC
- GBPJPY-OTC
- AUDJPY-OTC

## 🛡️ Seguridad y Mejores Prácticas

- ✅ **Usa PRACTICE primero** - Valida el bot antes de usar dinero real
- ✅ **Filtros de seguridad** - Volatilidad, impulso, timing óptimo
- ✅ **Validación multi-capa** - RL + Indicadores + LLM
- ✅ **Stop Loss automático** - Protección de capital
- ✅ **Límites de pérdidas** - Pausa automática después de pérdidas consecutivas

## 📊 Arquitectura

```
main_modern.py (Interfaz Gráfica)
    ↓
core/trader.py (Motor de Trading)
    ↓
├── core/agent.py (RL Agent - PPO)
├── core/decision_validator.py (Validación Multi-Capa)
├── core/risk.py (Gestión de Riesgo)
├── strategies/technical.py (Análisis Técnico)
├── ai/llm_client.py (Groq LLM)
└── exnovaapi/ (API de Exnova)
```

## 🔧 Compilar Ejecutable

```bash
# Requiere Python 3.11+
.\COMPILAR_CON_PYTHON311.bat

# Resultado: dist/TradingBotPro.exe
```

## 📚 Documentación

- [Cómo Ejecutar](COMO_EJECUTAR.md) - Guía detallada de ejecución
- [Cómo Funciona el Aprendizaje](COMO_FUNCIONA_APRENDIZAJE.md) - Sistema de aprendizaje
- [Análisis Inteligente](ANALISIS_INTELIGENTE_DEL_BOT.md) - Análisis del bot

## 🎓 Sistema de Aprendizaje

El bot utiliza tres capas de aprendizaje:

1. **Reinforcement Learning (PPO)** - Aprende patrones del mercado
2. **Aprendizaje Continuo** - Se adapta con cada operación
3. **Aprendizaje Observacional** - Aprende de oportunidades no ejecutadas

## ⚠️ Advertencias Importantes

- **Riesgo financiero**: El trading de opciones binarias conlleva riesgo de pérdida
- **Sin garantías**: El bot no garantiza ganancias
- **Responsabilidad**: Usa bajo tu propio riesgo
- **Validación**: Siempre prueba en PRACTICE primero

## 🤝 Contribuir

Las contribuciones son bienvenidas:

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/mejora`)
3. Commit tus cambios (`git commit -m 'Añadir mejora'`)
4. Push a la rama (`git push origin feature/mejora`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto es de código abierto. Úsalo bajo tu propia responsabilidad.

## 🙏 Agradecimientos

- **Exnova** por su API estable
- **Groq** por el análisis LLM ultrarrápido
- **Stable-Baselines3** por el framework de RL
- **PySide6** por la interfaz gráfica profesional

---

**Versión:** 2.0.0 - Exnova Edition  
**Última actualización:** 2025-11-27  
**Estado:** ✅ Producción  
**Broker:** Exnova únicamente

---

## 📞 Soporte

Si encuentras problemas o tienes preguntas, abre un issue en GitHub.

**⚠️ Nota:** Este bot está optimizado para Exnova. IQ Option ya no es soportado.


## 📚 Documentación Completa

### Guías de Usuario
- **[RESUMEN_EJECUTIVO.md](RESUMEN_EJECUTIVO.md)** - Resumen general del bot
- **[INSTRUCCIONES_RAPIDAS.txt](INSTRUCCIONES_RAPIDAS.txt)** - Guía rápida de inicio
- **[RESUMEN_CAMBIOS_FINALES.md](RESUMEN_CAMBIOS_FINALES.md)** - Últimos cambios aplicados

### Configuración
- **[CONFIGURACION_HORARIO.md](CONFIGURACION_HORARIO.md)** - Horarios de operación
- **[CHECKLIST_VERIFICACION.md](CHECKLIST_VERIFICACION.md)** - Lista de verificación

### Sistema de Aprendizaje
- **[SISTEMA_APRENDIZAJE_ACTIVO.md](SISTEMA_APRENDIZAJE_ACTIVO.md)** - Cómo aprende el bot

### Arquitectura Técnica
- **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** - Estructura del proyecto
- **[DATABASE_ARCHITECTURE.md](DATABASE_ARCHITECTURE.md)** - Arquitectura de base de datos

## 🔒 Seguridad y Límites

El bot está configurado con múltiples protecciones:

- ✅ **Monto fijo**: $1 por operación (no puede aumentar)
- ✅ **Sin martingala**: No duplica apuestas después de pérdidas
- ✅ **Horario limitado**: Solo opera 4 horas al día (7:00-11:00 AM)
- ✅ **Verificación de volatilidad**: No opera si el mercado está plano
- ✅ **Detención automática**: Se detiene a las 11:00 AM
- ✅ **Cooldown**: Espera entre operaciones

## 🧠 Sistema de Aprendizaje

El bot mejora continuamente mientras opera:

1. **Continuous Learner**: Re-entrena cada 20 operaciones
2. **Parallel Trainer**: Simula operaciones en paralelo
3. **Observational Learner**: Aprende de oportunidades no tomadas
4. **Trade Analyzer**: Analiza cada operación para mejorar

**Importante**: El aprendizaje NO afecta el monto ($1), martingala (0) ni horario. Solo mejora la calidad de las decisiones.

## 📈 Evolución Esperada

- **Semana 1**: Win rate ~45-55% (aprendiendo patrones básicos)
- **Semana 2**: Win rate ~55-65% (reconoce setups ganadores)
- **Semana 3**: Win rate ~60-70% (filtra señales débiles)
- **Semana 4+**: Win rate ~65-75% (optimizado para tu broker)

## ⚠️ Advertencias

- Este bot opera con **dinero real** en Exnova
- Solo usa capital que puedas permitirte perder
- Los resultados pasados no garantizan resultados futuros
- El trading de opciones binarias conlleva riesgos
- Revisa las leyes de tu país sobre trading

## 🆘 Soporte

Si tienes problemas:

1. Revisa **[CHECKLIST_VERIFICACION.md](CHECKLIST_VERIFICACION.md)**
2. Lee **[RESUMEN_CAMBIOS_FINALES.md](RESUMEN_CAMBIOS_FINALES.md)**
3. Verifica que `.env` tenga `CAPITAL_PER_TRADE=1` y `MAX_MARTINGALE=0`
4. Revisa los logs en consola

## 🎯 Próximos Pasos

Después de ejecutar `start.bat`:

1. El bot esperará hasta las 7:00 AM
2. Verificará volatilidad entre 7:00-7:30 AM
3. Operará hasta las 11:00 AM
4. Se detendrá automáticamente mostrando resumen

**¡Listo para operar de forma segura y controlada!** 🚀
