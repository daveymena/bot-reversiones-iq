@echo off
chcp 65001 >nul
cls
echo ╔════════════════════════════════════════════════════════════╗
echo ║     SUBIR SOLO CÓDIGO ESENCIAL - SIN ARCHIVOS GRANDES     ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

echo [1/7] 🗑️ Eliminando archivos grandes localmente...
echo.

REM Eliminar carpetas grandes
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "installer_output" rmdir /s /q "installer_output"
if exist "trading" rmdir /s /q "trading"
if exist "temp" rmdir /s /q "temp"
if exist "env_installer" rmdir /s /q "env_installer"

REM Eliminar ejecutables
if exist "*.exe" del /q "*.exe"
if exist "OllamaSetup.exe" del /q "OllamaSetup.exe"

REM Eliminar logs
if exist "*.log" del /q "*.log"

REM Eliminar specs
if exist "*.spec" del /q "*.spec"

echo ✅ Archivos grandes eliminados

echo.
echo [2/7] 🗑️ Eliminando .git actual...
echo.

if exist ".git" rmdir /s /q ".git"
echo ✅ .git eliminado

echo.
echo [3/7] 📝 Creando .gitignore completo...
echo.

(
echo # Python
echo __pycache__/
echo *.py[cod]
echo *.pyc
echo *.pyo
echo *.log
echo.
echo # Archivos grandes
echo *.exe
echo *.msi
echo *.dmg
echo OllamaSetup.exe
echo trading/
echo.
echo # Build
echo build/
echo dist/
echo *.spec
echo installer_output/
echo temp/
echo env_installer/
echo.
echo # Environment
echo .env
echo venv/
echo env/
echo.
echo # Data
echo data/experiences.json
echo data/experiences_backup.json
echo models/*.zip
echo.
echo # IDE
echo .vscode/
echo .idea/
) > .gitignore

echo ✅ .gitignore creado

echo.
echo [4/7] 🆕 Inicializando repositorio limpio...
echo.

git init
git branch -M main
git remote add origin https://github.com/daveymena/bot-reversiones-iq.git

echo ✅ Repositorio inicializado

echo.
echo [5/7] 📦 Agregando solo código fuente...
echo.

REM Agregar solo archivos esenciales
git add *.py
git add *.md
git add *.txt
git add *.bat
git add .gitignore
git add .env.example
git add core/
git add strategies/
git add ai/
git add gui/
git add exnovaapi/
git add env/
git add installer_resources/

echo ✅ Archivos agregados

echo.
echo [6/7] 📝 Creando commit...
echo.

git commit -m "🎉 Bot Exnova v2.0 - Código limpio con IA (Groq + RL + Análisis Técnico)"

echo ✅ Commit creado

echo.
echo [7/7] 🚀 Subiendo a GitHub...
echo.

git push -u origin main --force

if errorlevel 1 (
    echo.
    echo ❌ Error al subir
    echo.
    echo Si el error persiste, crea un nuevo repositorio en GitHub:
    echo    1. Ve a https://github.com/new
    echo    2. Crea "trading-bot-exnova"
    echo    3. Actualiza el remote:
    echo       git remote set-url origin https://github.com/daveymena/trading-bot-exnova.git
    echo    4. Ejecuta: git push -u origin main
    echo.
) else (
    echo.
    echo ╔════════════════════════════════════════════════════════════╗
    echo ║          ✅ CÓDIGO SUBIDO EXITOSAMENTE                    ║
    echo ╚════════════════════════════════════════════════════════════╝
    echo.
    echo 🎉 Repositorio limpio en GitHub
    echo    Solo código fuente, sin archivos grandes
    echo.
)

pause
