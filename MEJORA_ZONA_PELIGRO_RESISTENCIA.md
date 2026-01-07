# Mejora: Zona de Peligro en Resistencias y Soportes

## Problema Identificado

El bot estaba operando **cerca** de resistencias/soportes, no solo **en** ellas, causando pérdidas por reversiones.

### Ejemplo del Problema

```
Precio: 156.20 (cerca de resistencia en 156.25)
Bot: CALL ❌
Resultado: Precio rebota en resistencia → PÉRDIDA
```

## Solución Implementada

### Antes (Solo en resistencia exacta)

```python
if bb_position == 'UPPER' and action == 1:  # Solo si está EN la resistencia
    rechazar()
```

**Problema**: El precio puede estar "cerca" pero no "en" la resistencia.

### Ahora (Zona de peligro del 20%)

```python
# Calcular zona de peligro
bb_range = bb_high - bb_low
upper_danger_zone = bb_high - (bb_range * 0.2)  # 20% superior
lower_danger_zone = bb_low + (bb_range * 0.2)   # 20% inferior

# Rechazar CALL en zona de peligro superior
if price >= upper_danger_zone and action == 1:
    rechazar("CALL muy cerca de resistencia")

# Rechazar PUT en zona de peligro inferior
if price <= lower_danger_zone and action == 2:
    rechazar("PUT muy cerca de soporte")
```

## Visualización

```
BB Superior (Resistencia) ─────────────────── 156.25
                                    ↑
Zona de Peligro (20%)              ↑ NO CALL aquí
                                    ↑
────────────────────────────────────────────── 156.20 (80% de BB)


Zona Segura para CALL              ↕ OK para CALL


────────────────────────────────────────────── 156.05 (20% de BB)
                                    ↓
Zona de Peligro (20%)              ↓ NO PUT aquí
                                    ↓
BB Inferior (Soporte) ──────────────────────── 156.00
```

## Reglas Implementadas

### ✅ Operaciones Permitidas

| Situación | Acción | Resultado |
|-----------|--------|-----------|
| Precio en zona media/baja de BB | CALL | ✅ Permitido |
| Precio en zona media/alta de BB | PUT | ✅ Permitido |
| Precio en soporte (BB inferior) | CALL | ✅ Permitido (reversión) |
| Precio en resistencia (BB superior) | PUT | ✅ Permitido (reversión) |

### ❌ Operaciones Rechazadas

| Situación | Acción | Razón |
|-----------|--------|-------|
| Precio en zona alta de BB (>80%) | CALL | ❌ Cerca de resistencia |
| Precio en zona baja de BB (<20%) | PUT | ❌ Cerca de soporte |
| Precio EN resistencia (BB superior) | CALL | ❌ En resistencia |
| Precio EN soporte (BB inferior) | PUT | ❌ En soporte |

## Beneficios

1. ✅ **Más conservador**: Evita operar cerca de zonas peligrosas
2. ✅ **Menos pérdidas**: Reduce operaciones contra reversiones
3. ✅ **Mejor timing**: Espera mejores puntos de entrada
4. ✅ **Protección adicional**: Margen de seguridad del 20%

## Ejemplo Práctico

### Antes (Sin zona de peligro)

```
BB Superior: 156.25
Precio: 156.22 (98% de BB)
Bot: CALL ✅ (permitido porque no está exactamente en 156.25)
Resultado: Precio rebota → PÉRDIDA ❌
```

### Ahora (Con zona de peligro)

```
BB Superior: 156.25
Zona peligro: 156.20 (80% de BB)
Precio: 156.22 (en zona de peligro)
Bot: CALL ❌ RECHAZADO ("muy cerca de resistencia")
Resultado: No opera → Capital protegido ✅
```

## Configuración

El margen de seguridad es del **20%** del rango de Bollinger Bands:

```python
upper_danger_zone = bb_high - (bb_range * 0.2)  # 20% superior
lower_danger_zone = bb_low + (bb_range * 0.2)   # 20% inferior
```

### Ajustar el Margen

Si quieres ser más o menos conservador:

```python
# Más conservador (30%)
upper_danger_zone = bb_high - (bb_range * 0.3)

# Menos conservador (10%)
upper_danger_zone = bb_high - (bb_range * 0.1)
```

## Logs del Bot

Ahora verás mensajes como:

```
⚠️ CALL muy cerca de resistencia - RECHAZADO por seguridad
⚠️ PUT muy cerca de soporte - RECHAZADO por seguridad
```

Esto indica que el bot está protegiendo tu capital evitando zonas peligrosas.

## Impacto Esperado

- ✅ **Menos operaciones** (más selectivo)
- ✅ **Mejor win rate** (menos pérdidas por reversión)
- ✅ **Más seguridad** (margen de protección)
- ✅ **Mejor timing** (espera mejores entradas)

## Conclusión

Esta mejora hace que el bot sea más inteligente al:

1. No solo evitar resistencias/soportes exactos
2. Evitar también las **zonas cercanas** (20% del rango)
3. Proteger el capital con un margen de seguridad
4. Esperar mejores puntos de entrada

El bot ahora es más conservador y selectivo, lo cual debería mejorar el win rate. 🎯
