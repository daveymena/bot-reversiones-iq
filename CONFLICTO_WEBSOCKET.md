# ⚠️ CONFLICTO DE VERSIONES - WEBSOCKET-CLIENT

## 🔴 PROBLEMA

IQ Option y Exnova requieren **versiones diferentes** de `websocket-client`:

| Broker | Versión Requerida | Estado |
|--------|-------------------|--------|
| **IQ Option** | `websocket-client==0.56.0` | ✅ Funciona con 0.56 |
| **Exnova** | `websocket-client==1.8.0` | ✅ Funciona con 1.8 |

**No pueden coexistir** en el mismo entorno Python.

## ✅ SOLUCIONES

### Opción 1: Usar Solo Exnova (RECOMENDADO)
Exnova tiene las mismas funcionalidades que IQ Option y funciona correctamente.

```bash
# Instalar versión para Exnova
pip install websocket-client==1.8.0
```

**Ventajas:**
- ✅ Funciona perfectamente
- ✅ 149 activos OTC disponibles 24/7
- ✅ Rentabilidad hasta 88%
- ✅ Misma API que IQ Option

### Opción 2: Usar Solo IQ Option
Si prefieres IQ Option, instala su versión:

```bash
# Instalar versión para IQ Option
pip install websocket-client==0.56.0
```

### Opción 3: Entornos Virtuales Separados
Crear dos entornos Python diferentes:

```bash
# Entorno para IQ Option
python -m venv env_iq
env_iq\Scripts\activate
pip install websocket-client==0.56.0
pip install iqoptionapi

# Entorno para Exnova
python -m venv env_exnova
env_exnova\Scripts\activate
pip install websocket-client==1.8.0
pip install -e exnovaapi
```

### Opción 4: Modificar el Código de IQ Option
Actualizar la librería `iqoptionapi` para que funcione con websocket-client 1.8.0 (requiere modificar el código fuente).

## 📊 ESTADO ACTUAL

### ✅ Exnova - FUNCIONANDO
```
websocket-client: 1.8.0
Balance: $9,543.67 (PRACTICE)
Activos OTC: 149 disponibles
Rentabilidad: hasta 88%
```

### ❌ IQ Option - NO FUNCIONA
```
websocket-client: 1.8.0 (incompatible)
Requiere: 0.56.0
Estado: Conexión bloqueada
```

## 🎯 RECOMENDACIÓN

**Usar Exnova** porque:
1. ✅ Funciona con la versión moderna de websocket-client
2. ✅ Más activos disponibles (149 OTC)
3. ✅ Mejor rentabilidad (hasta 88%)
4. ✅ API idéntica a IQ Option
5. ✅ Más estable y mantenido

## 🔧 CONFIGURACIÓN ACTUAL

El bot está configurado para usar **Exnova** por defecto.

Para cambiar el broker, edita `config.py`:

```python
# En config.py
BROKER_NAME = "exnova"  # o "iq"
```

O usa la variable de entorno:

```bash
# En .env
BROKER_NAME=exnova
```

## 📝 PRÓXIMOS PASOS

1. ✅ Exnova probado y funcionando
2. ⏳ Probar operación real en Exnova
3. ⏳ Verificar sistema de entrenamiento
4. ⏳ Crear nueva interfaz moderna
5. ⏳ Optimizar estrategias de trading
