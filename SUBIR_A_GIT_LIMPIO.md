# 🚀 Guía para Subir a Git (Repositorio Limpio)

## Problema Actual
El repositorio tiene archivos grandes en el historial (bot_errors.log 477MB, OllamaSetup.exe 1.1GB) que impiden el push.

## Solución: Crear Repositorio Limpio

### Paso 1: Backup del código actual
```bash
# Crear backup
cd C:\trading
xcopy trading trading_backup /E /I /H
```

### Paso 2: Eliminar .git y crear nuevo repositorio
```bash
cd C:\trading\trading

# Eliminar historial antiguo
Remove-Item -Recurse -Force .git

# Inicializar nuevo repositorio
git init
git branch -M main
```

### Paso 3: Agregar archivos importantes
```bash
# Agregar solo archivos necesarios
git add core/ strategies/ data/ ai/ gui/ database/ exnovaapi/ models/
git add *.py *.md *.txt *.yml *.sh *.bat
git add .env.example .gitignore
git add .kiro/

# Verificar que no haya archivos grandes
git ls-files | ForEach-Object { if (Test-Path $_) { Get-Item $_ | Where-Object { $_.Length -gt 10MB } } }
```

### Paso 4: Commit inicial limpio
```bash
git commit -m "🎉 Repositorio limpio v2.0 - Bot Trading Profesional

✅ Características principales:
- RL Agent (PPO) con aprendizaje continuo
- Análisis LLM (Groq/Ollama)
- GUI moderna con PySide6
- Soporte Exnova + IQ Option
- Base de datos PostgreSQL
- Sistema de validación multi-capa
- Análisis de estructura de mercado
- Bot 24/7 ultra estable

✅ Correcciones críticas aplicadas:
- GUI nunca se congela
- Bot no se detiene después de operaciones
- BD con timeouts (no bloquea)
- Estadísticas en tiempo real
- Conflicto de señales resuelto"
```

### Paso 5: Conectar con GitHub
```bash
# Conectar con el repositorio remoto
git remote add origin https://github.com/daveymena/bot-reversiones-iq.git

# Forzar push del nuevo historial limpio
git push -u origin main --force
```

## Alternativa: Usar Git LFS para archivos grandes

Si necesitas subir archivos grandes (modelos, datos):

```bash
# Instalar Git LFS
git lfs install

# Trackear archivos grandes
git lfs track "*.zip"
git lfs track "*.pkl"
git lfs track "*.h5"

# Agregar .gitattributes
git add .gitattributes
git commit -m "Configurar Git LFS"
```

## Verificación Final

Antes de hacer push, verificar tamaño:
```bash
git count-objects -vH
```

Debe ser < 100 MB para GitHub.

## Notas Importantes

⚠️ **ANTES de hacer --force**:
1. Asegúrate de tener backup
2. Avisa a otros colaboradores (si los hay)
3. El historial antiguo se perderá

✅ **Después del push**:
1. Verificar en GitHub que todo esté
2. Clonar en otra carpeta para probar
3. Eliminar backup si todo funciona
