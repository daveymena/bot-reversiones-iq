@echo off
echo ========================================
echo SUBIR BOT A GIT - REPOSITORIO LIMPIO
echo ========================================
echo.

echo [1/6] Verificando archivos grandes...
git ls-files | findstr /i "\.log$ \.exe$ node_modules .next" > archivos_grandes.txt
if exist archivos_grandes.txt (
    echo Archivos grandes encontrados, eliminando del cache...
    for /f "delims=" %%i in (archivos_grandes.txt) do git rm --cached "%%i" 2>nul
    del archivos_grandes.txt
)

echo.
echo [2/6] Verificando .gitignore...
if not exist .gitignore (
    echo ERROR: .gitignore no existe
    pause
    exit /b 1
)

echo.
echo [3/6] Agregando archivos al staging...
git add core/ strategies/ data/ ai/ gui/ database/ exnovaapi/ models/
git add *.py *.md requirements*.txt *.yml .env.example .gitignore
git add .kiro/

echo.
echo [4/6] Verificando tamaño del repositorio...
git count-objects -vH

echo.
echo [5/6] Creando commit...
git commit -m "🎉 Bot Trading Pro v2.0 - Ultra Estable

✅ Características:
- RL Agent (PPO) + Aprendizaje Continuo
- Análisis LLM (Groq/Ollama)
- GUI Moderna (PySide6)
- Soporte Exnova + IQ Option
- PostgreSQL con timeouts
- Validación multi-capa
- Análisis estructura de mercado
- Bot 24/7 ultra estable

✅ Correcciones críticas:
- GUI nunca se congela
- Bot no se detiene después de operaciones
- BD con timeouts (no bloquea)
- Estadísticas en tiempo real
- Conflicto de señales resuelto
- Validaciones de datos completas"

echo.
echo [6/6] Subiendo a GitHub...
echo IMPORTANTE: Esto hará un push --force
echo Presiona Ctrl+C para cancelar o cualquier tecla para continuar...
pause >nul

git push origin main --force

echo.
echo ========================================
echo ✅ SUBIDA COMPLETADA
echo ========================================
echo.
echo Verifica en: https://github.com/daveymena/bot-reversiones-iq
echo.
pause
