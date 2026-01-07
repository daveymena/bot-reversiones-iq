# 🚀 Despliegue del Bot Inteligente en Easypanel

Este documento explica cómo subir tu bot con **Aprendizaje Adaptativo** y **Multi-Agentes** a Easypanel para que funcione 24/7 en la nube.

## 📋 Requisitos en Easypanel

1.  **Proyecto**: Crea un nuevo proyecto en Easypanel.
2.  **Servicio**: Crea un servicio tipo "App" desde tu repositorio de GitHub.
3.  **Configuración de Build**: Easypanel detectará automáticamente el `Dockerfile`.

## ⚙️ Variables de Entorno (Environment Variables)

Configura las siguientes variables en la sección de **Environment** de tu App:

| Variable | Valor Sugerido | Descripción |
| :--- | :--- | :--- |
| `BROKER_NAME` | `exnova` | Broker a utilizar |
| `ACCOUNT_TYPE` | `PRACTICE` | **CRÍTICO**: Usa siempre PRACTICE para aprender |
| `EXNOVA_EMAIL` | `tu@email.com` | Tu correo de Exnova |
| `EXNOVA_PASSWORD` | `tu_password` | Tu contraseña de Exnova |
| `HEADLESS_MODE` | `True` | Activa el inicio automático sin menús |
| `USE_LLM` | `True` | Activa la validación por IA |
| `USE_GROQ` | `True` | Activa el uso de Groq |
| `VITE_GROQ_API_KEY` | `gsk_...` | Tu llave de Groq principal |
| `VITE_GROQ_API_KEY_2` | `gsk_...` | Llaves de respaldo para rotación |
| `VITE_OLLAMA_BASE_URL` | `https://tu-ollama.host` | Tu servidor de Ollama (opcional) |

## 💾 Persistencia de Datos (Mundo Real)

Para que el bot **no olvide lo que aprendió** cuando se reinicie el servidor, debes configurar estos volúmenes en la pestaña **Mounts / Volumes**:

*   **Ruta Host / Nombre**: `bot_data` -> **Ruta Contenedor**: `/app/data`
*   **Ruta Host / Nombre**: `bot_models` -> **Ruta Contenedor**: `/app/models`

## 🧠 ¿Cómo funciona el Aprendizaje en la Nube?

En la nube, el bot activará automáticamente el **Ajuste Inteligente de Umbral**:

1.  **Monitorización continua**: Analiza sus últimos 20 resultados en tiempo real.
2.  **Auto-Ajuste**:
    *   Si el Win Rate baja del 60%, el bot sube el umbral de confianza (se vuelve más exigente).
    *   Si el Win Rate sube del 85%, optimiza el volumen de operaciones pero manteniendo la calidad.
3.  **Rotación de IA**: Si tu llave de Groq se agota, el bot rotará a la siguiente llave configurada en las variables de entorno sin detenerse.

## 🛡️ Estilo de Trading: "Aprendizaje Drástico"

El bot ha sido programado para:
*   **Aprender de las pérdidas**: Identifica qué activos están fallando y aplica filtros de volatilidad específicos.
*   **Auto-Protección**: Si el mercado se vuelve errático, el umbral de confianza sube automáticamente hasta un 90% para evitar entradas falsas.
*   **Operación Inteligente**: Solo ejecuta si la estrategia técnica Y el agente de IA (Groq/Ollama) están de acuerdo.

---

**Nota**: Una vez desplegado, puedes monitorear todo desde la pestaña **Logs** de Easypanel. Verás los diálogos de los agentes y cómo se ajustan los umbrales de aprendizaje en tiempo real.
