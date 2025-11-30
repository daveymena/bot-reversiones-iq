# ⚡ INICIO RÁPIDO - 5 MINUTOS

## 🚀 Empezar a Usar el Bot en 5 Pasos

### 1️⃣ Iniciar la Interfaz (30 segundos)

```bash
python main_modern.py
```

**Resultado esperado:**
- Ventana moderna se abre
- Credenciales pre-cargadas
- Sistema listo

---

### 2️⃣ Conectar al Broker (30 segundos)

**En el Panel Izquierdo:**

1. Broker: `Exnova` ✅
2. Email: `daveymena16@gmail.com` ✅
3. Password: `6715320Dvd.` ✅
4. Cuenta: `PRACTICE` ✅
5. Click: **🔌 CONECTAR**

**Resultado esperado:**
```
✅ Conectado a EXNOVA
💰 Balance: $9,543.67 (PRACTICE)
```

---

### 3️⃣ Entrenar el Modelo (3 minutos)

**En el Panel Derecho → Tab "🎓 Entrenamiento":**

1. Velas: `2000` ✅
2. Timesteps: `10000` ✅
3. Click: **🎓 ENTRENAR MODELO**
4. ⏳ Esperar 2-3 minutos

**Resultado esperado:**
```
✅ Entrenamiento completado
✅ Modelo guardado
```

---

### 4️⃣ Configurar Estrategias (30 segundos)

**En el Panel Derecho → Tab "🎯 Estrategias":**

✅ Activar:
- 🤖 Reinforcement Learning
- 📊 Martingala Inteligente
- 🧠 Análisis LLM (Groq)

⚙️ Configurar:
- Stop Loss: `5%`
- Take Profit: `10%`
- Max Martingala: `3`

---

### 5️⃣ Iniciar el Bot (10 segundos)

**En el Panel Central:**

1. Click: **▶️ INICIAR BOT**

**Resultado esperado:**
```
▶️ Bot iniciado
🔍 Escaneando mercado...
✅ Activo seleccionado: EURUSD-OTC
📊 Analizando indicadores...
```

---

## 🎯 ¡LISTO! El Bot Está Operando

### Qué Hace el Bot Ahora:

1. 📊 Analiza el mercado cada segundo
2. 🧮 Calcula indicadores técnicos
3. 🤖 Consulta al agente RL
4. 🧠 Consulta a Groq AI
5. 💰 Ejecuta operaciones automáticamente
6. 📈 Monitorea resultados

### Dónde Ver la Actividad:

- **Logs del Sistema**: Panel central inferior
- **Estadísticas**: Panel derecho → Tab "Análisis"
- **Historial**: Tabla de últimas operaciones
- **Balance**: Header superior

---

## 📊 Monitoreo

### Panel Central - Logs
```
[13:45:23] 🔍 Escaneando mercado...
[13:45:24] ✅ Activo: EURUSD-OTC
[13:45:25] 📊 RSI: 45.2
[13:45:26] 🤖 RL predice: CALL
[13:45:27] 🧠 LLM confirma: CALL
[13:45:28] 💰 Ejecutando CALL $1.00
[13:45:29] ✅ Operación ejecutada
[13:46:40] ✅ GANADA: +$0.85
```

### Panel Derecho - Estadísticas
```
Total Operaciones: 5
Ganadas: 3
Perdidas: 2
Win Rate: 60%
Profit Total: +$1.55
```

---

## ⏸️ Detener el Bot

**En el Panel Central:**

Click: **⏸️ DETENER BOT**

El bot se detendrá de forma segura.

---

## 🔄 Re-entrenar (Diario)

**Para mejorar el rendimiento:**

1. Panel Derecho → Tab "Entrenamiento"
2. Click: **🔄 RE-ENTRENAR**
3. Esperar 1-2 minutos

Esto actualiza el modelo con datos recientes.

---

## 📝 Comandos Alternativos

### Entrenar desde Terminal
```bash
python train_bot.py --asset EURUSD-OTC --timesteps 10000
```

### Probar Conexión
```bash
python test_exnova_completo.py
```

### Ver Activos Disponibles
```bash
python test_activos_disponibles.py
```

### Demo de Operación
```bash
python demo_operacion_exnova.py
```

---

## ⚠️ Recordatorios Importantes

### 🔴 ANTES DE OPERAR:

1. ✅ Usar cuenta **PRACTICE** primero
2. ✅ Entrenar el modelo
3. ✅ Probar por varios días
4. ✅ Validar Win Rate > 55%
5. ✅ Entender cómo funciona

### 🔴 DURANTE LA OPERACIÓN:

1. ✅ Monitorear constantemente
2. ✅ Revisar logs
3. ✅ Verificar estadísticas
4. ✅ Ajustar si es necesario
5. ✅ Respetar Stop Loss

### 🔴 NUNCA:

1. ❌ Operar sin entrenar
2. ❌ Ignorar el Stop Loss
3. ❌ Dejar sin supervisión
4. ❌ Usar dinero que no puedes perder
5. ❌ Esperar ganancias garantizadas

---

## 🆘 Problemas Comunes

### "No se pudo conectar"
```
Solución:
1. Verificar credenciales
2. Verificar internet
3. Reintentar
```

### "Modelo no entrenado"
```
Solución:
1. Tab "Entrenamiento"
2. Click "ENTRENAR MODELO"
3. Esperar a que termine
```

### "No se encontraron activos"
```
Solución:
1. Verificar conexión
2. Usar activos OTC
3. Ejecutar: python test_activos_disponibles.py
```

### "Win Rate bajo"
```
Solución:
1. Re-entrenar con más datos
2. Aumentar timesteps
3. Ajustar parámetros
4. Probar otros activos
```

---

## 📚 Más Información

### Documentación Completa
- `README.md` - Documentación principal
- `GUIA_USO_BOT.md` - Guía detallada
- `SISTEMA_ENTRENAMIENTO.md` - Sistema de RL

### Soporte
- Revisar logs en la interfaz
- Ejecutar scripts de diagnóstico
- Consultar documentación

---

## ✅ Checklist de Inicio

- [ ] Interfaz iniciada
- [ ] Conectado a Exnova
- [ ] Modelo entrenado
- [ ] Estrategias configuradas
- [ ] Bot iniciado
- [ ] Monitoreando resultados

---

**🚀 ¡Listo para operar! 📈**

**Tiempo total:** ~5 minutos
**Dificultad:** ⭐⭐☆☆☆ (Fácil)
**Resultado:** Bot operando automáticamente

---

**Siguiente paso:** Leer `GUIA_USO_BOT.md` para uso avanzado
