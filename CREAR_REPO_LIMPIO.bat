@echo off
chcp 65001 >nul
cls
echo ╔════════════════════════════════════════════════════════════╗
echo ║     CREAR REPOSITORIO LIMPIO - SIN ARCHIVOS GRANDES       ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo Esta es la solución definitiva:
echo   1. Eliminar carpeta .git actual
echo   2. Crear nuevo repositorio limpio
echo   3. Hacer commit inicial sin archivos grandes
echo   4. Subir a GitHub (force push)
echo.
echo ⚠️ ADVERTENCIA: Perderás el historial de commits anterior
echo.
echo ¿Continuar?
echo.

choice /C SN /N /M "(S/N): "

if errorlevel 2 goto END

echo.
echo [1/6] 🗑️ Eliminando repositorio Git actual...
echo.

if exist ".git" rmdir /s /q ".git"
echo ✅ Repositorio anterior eliminado

echo.
echo [2/6] 🗑️ Eliminando archivos grandes...
echo.

if exist "trading" rmdir /s /q "trading"
if exist "OllamaSetup.exe" del /q "OllamaSetup.exe"
if exist "*.log" del /q "*.log"
echo ✅ Archivos grandes eliminados

echo.
echo [3/6] 📝 Actualizando .gitignore...
echo.

echo # Python > .gitignore
echo __pycache__/ >> .gitignore
echo *.py[cod] >> .gitignore
echo *.log >> .gitignore
echo. >> .gitignore
echo # Archivos grandes >> .gitignore
echo *.exe >> .gitignore
echo OllamaSetup.exe >> .gitignore
echo trading/ >> .gitignore
echo. >> .gitignore
echo # Build >> .gitignore
echo build/ >> .gitignore
echo dist/ >> .gitignore
echo *.spec >> .gitignore
echo. >> .gitignore
echo # Environment >> .gitignore
echo .env >> .gitignore
echo venv/ >> .gitignore

echo ✅ .gitignore creado

echo.
echo [4/6] 🆕 Inicializando nuevo repositorio...
echo.

git init
git branch -M main
git remote add origin https://github.com/daveymena/bot-reversiones-iq.git

echo ✅ Repositorio inicializado

echo.
echo [5/6] 📦 Agregando archivos limpios...
echo.

git add .
git commit -m "🎉 Bot Exnova v2.0 - Repositorio limpio con IA (Groq + RL)"

echo ✅ Commit inicial creado

echo.
echo [6/6] 🚀 Subiendo a GitHub...
echo.

git push -u origin main --force

if errorlevel 1 (
    echo.
    echo ❌ Error al subir
    echo.
    echo Verifica tu conexión y credenciales de GitHub
    echo.
) else (
    echo.
    echo ╔════════════════════════════════════════════════════════════╗
    echo ║          ✅ REPOSITORIO LIMPIO CREADO                     ║
    echo ╚════════════════════════════════════════════════════════════╝
    echo.
    echo 🎉 Repositorio subido exitosamente sin archivos grandes
    echo.
)

pause
goto END

:END
