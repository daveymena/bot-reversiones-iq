# Sistema de Validación de Entradas Refinadas

## Resumen de Mejoras Implementadas

Este sistema mejora drásticamente la precisión y consistencia de las entradas del bot de trading.

### Archivos Nuevos Creados

1. **`core/refined_entry_validator.py`**
   - `RefinedEntryValidator`: Validador ultra-estricto con múltiples capas
   - `EntryRefiner`: Refina decisiones antes de ejecutar

2. **`core/refined_opportunity_scorer.py`**
   - `RefinedOpportunityScorer`: Scoring de 0-100 con 8 componentes
   - Requiere score mínimo de 25 (antes 5) - 5x más selectivo

3. **`core/refined_entry_orchestrator.py`**
   - `EntryOrchestrator`: Coordina todos los sistemas de validación
   - Valida oportunidades con scoring + validación refinada + confluencia

### Cambios en Archivos Existentes

- **`core/trader.py`**: Integración del orquestador de validación refinada
- **`core/asset_manager.py`**: Integración del scorer refinado

## Configuración de Strictness

| Parámetro | Anterior | Nuevo | Efecto |
|-----------|----------|-------|--------|
| Score mínimo oportunidad | 5 | 25 | 5x más selectivo |
| Confianza mínima | 40% | 80% | Solo entradas de alta calidad |
| Score filtros rentabilidad | 60 | 80 | Filtros más estrictos |
| Confirmación momentum | Opcional | Obligatoria | Evita señales falsas |
| Validación timing | No | Sí | Solo timing óptimo |
| Validación estructura | No | Sí | Confirmar tendencia |
| Confluencia indicadores | No | Sí (60%) | Múltiples indicadores de acuerdo |

## Cómo Funciona

### Flujo de Validación

1. **Asset Manager** escanea activos → usa `RefinedOpportunityScorer`
   - Score mínimo: 25 puntos
   - Solo retorna oportunidades con score >= 25

2. **Trader** analiza oportunidad → usa `EntryOrchestrator`
   - Evalúa scoring de oportunidad
   - Aplica `EntryRefiner` para validación estricta
   - Verifica confluencia de indicadores
   - Confirma momentum y timing

3. **Validación por Capas**
   - Capa 1: Score de oportunidad >= 25
   - Capa 2: Confianza >= 80%
   - Capa 3: Momentum confirmado
   - Capa 4: Timing óptimo
   - Capa 5: Estructura de mercado válida
   - Capa 6: Confluencia >= 60%

## Estadísticas de Seguimiento

El sistema mantiene estadísticas de:
- Total oportunidades evaluadas
- Oportunidades aprobadas
- Oportunidades rechazadas
- Razones de rechazo

Puedes acceder a estas estadísticas desde el trader:
```python
trader.entry_orchestrator.get_stats()
trader.entry_orchestrator.get_approval_rate()
```

## Impacto Esperado

- **Mayor consistencia**: El bot solo opera en las mejores condiciones
- **Menor ruido**: Reduce operaciones de baja calidad
- **Mejor win rate**: Las operaciones aprobadas tienen mayor probabilidad de éxito
- **Trade-off**: Menos operaciones, pero de mayor calidad

## Notas

- El sistema está diseñado para ser **conservador** al principio
- Si el bot está rechazando demasiado, los thresholds pueden ajustarse
- Monitorea las estadísticas de rechazo para calibrar

---

**Fecha de implementación**: 2026
**Estado**: Activo y funcionando