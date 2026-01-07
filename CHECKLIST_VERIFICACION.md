# ✅ Checklist de Verificación

## Antes de Ejecutar el Bot

### 1. Configuración Básica

- [ ] Verificar `.env` tiene `CAPITAL_PER_TRADE=1`
- [ ] Verificar `.env` tiene `MAX_MARTINGALE=0`
- [ ] Verificar credenciales de Exnova están correctas
- [ ] Verificar `ACCOUNT_TYPE=REAL` (o cambiar a PRACTICE para pruebas)

### 2. Archivos Necesarios

- [ ] Existe `data/` folder
- [ ] Existe `models/` folder
- [ ] Existe `data/experiences.json` (se crea automáticamente si no existe)
- [ ] Existe `models/rl_agent.zip` (se crea al entrenar)

### 3. Dependencias

- [ ] Python 3.10+ instalado
- [ ] Todas las dependencias instaladas (`pip install -r requirements.txt`)
- [ ] Conexión a internet activa

### 4. Horario

- [ ] Verificar hora del sistema es correcta
- [ ] Confirmar zona horaria
- [ ] Ajustar horario en `.env` si es necesario:
  ```
  TRADING_START_HOUR=7
  TRADING_END_HOUR=9
  TRADING_END_MINUTE=30
  ```

## Durante la Ejecución

### Verificar Logs

- [ ] Aparece "Esperando horario de inicio" antes de las 7:00 AM
- [ ] Aparece "Verificando volatilidad" entre 7:00-7:30 AM
- [ ] Aparece "Iniciando operaciones" cuando volatilidad es adecuada
- [ ] Aparece "Escaneando oportunidades" cada 30 segundos
- [ ] Aparece "Experiencia agregada" después de cada operación
- [ ] Aparece "Re-entrenamiento programado" cada 20 operaciones

### Verificar Operaciones

- [ ] Monto de cada operación es $1.00
- [ ] NO aparece "Aplicar Martingala"
- [ ] Aparece "NO Martingala" después de pérdidas
- [ ] Balance se actualiza correctamente
- [ ] Cooldown de 2 minutos entre operaciones

### Verificar Aprendizaje

- [ ] Archivo `data/experiences.json` crece con cada operación
- [ ] Aparece "EVALUACIÓN CONTINUA" cada 10 operaciones
- [ ] Aparece "Re-entrenamiento completado" periódicamente
- [ ] Fecha de `models/rl_agent.zip` se actualiza

## Después de la Sesión (9:30 AM)

### Verificar Cierre

- [ ] Aparece "Horario de operación finalizado"
- [ ] Aparece "Sesión completada"
- [ ] Muestra resumen final con:
  - Balance final
  - Ganancia/Pérdida total
  - Total de operaciones
  - Operaciones ganadas
  - Operaciones perdidas
  - Win rate

### Revisar Resultados

- [ ] Verificar balance en broker coincide con logs
- [ ] Revisar `data/experiences.json` tiene todas las operaciones
- [ ] Verificar `models/rl_agent.zip` fue actualizado
- [ ] Guardar logs para análisis (copiar de consola)

## Solución de Problemas

### Si el bot no inicia:

1. Verificar credenciales en `.env`
2. Verificar conexión a internet
3. Verificar hora del sistema
4. Revisar logs de error

### Si opera con monto incorrecto:

1. Verificar `.env` tiene `CAPITAL_PER_TRADE=1`
2. Reiniciar el bot
3. Verificar logs muestran "Monto: $1.00"

### Si aplica martingala:

1. Verificar `.env` tiene `MAX_MARTINGALE=0`
2. Reiniciar el bot
3. Verificar logs muestran "NO Martingala"

### Si no se detiene a las 9:30 AM:

1. Verificar hora del sistema
2. Verificar `.env` tiene horarios correctos
3. Detener manualmente con Ctrl+C

### Si no aprende:

1. Verificar existe `data/experiences.json`
2. Verificar logs muestran "Experiencia agregada"
3. Verificar logs muestran "Re-entrenamiento"
4. Revisar permisos de escritura en carpeta `data/`

### Si hay error en experiences.json:

1. Ejecutar `REPARAR_EXPERIENCES.bat`
2. Se creará backup automático
3. Se limpiará el archivo corrupto
4. El bot empezará a guardar experiencias nuevas

## Comandos Útiles

### Ejecutar el bot:
```bash
start.bat
```

### Ver experiencias guardadas:
```bash
type data\experiences.json
```

### Ver última modificación del modelo:
```bash
dir models\rl_agent.zip
```

### Contar operaciones en experiences.json:
```bash
find /c "action" data\experiences.json
```

### Reparar experiences.json corrupto:
```bash
REPARAR_EXPERIENCES.bat
```

### Limpiar experiencias antiguas (CUIDADO):
```bash
del data\experiences.json
```

## Contacto y Soporte

**Documentación:**
- `RESUMEN_EJECUTIVO.md` - Resumen general
- `RESUMEN_CAMBIOS_FINALES.md` - Cambios detallados
- `SISTEMA_APRENDIZAJE_ACTIVO.md` - Sistema de aprendizaje
- `CONFIGURACION_HORARIO.md` - Configuración de horarios
- `INSTRUCCIONES_RAPIDAS.txt` - Guía rápida

---

**Usa este checklist cada vez que ejecutes el bot** ✅
