@echo off
chcp 65001 >nul
cls
echo ╔════════════════════════════════════════════════════════════╗
echo ║     LIMPIAR PROYECTO - SOLO EXNOVA                        ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo Este script eliminará:
echo   - Archivos de IQ Option
echo   - Backend/Frontend web (Next.js)
echo   - Archivos de documentación obsoletos
echo   - Archivos de compilación antiguos
echo   - Archivos temporales
echo.
echo ⚠️ ADVERTENCIA: Esta acción no se puede deshacer
echo.
echo ¿Continuar?
echo.

choice /C SN /N /M "(S/N): "

if errorlevel 2 goto END

echo.
echo [1/8] 🗑️ Eliminando archivos de IQ Option...
echo.

if exist "diagnostico_iq.py" del /q "diagnostico_iq.py"
if exist "test_iq_option.py" del /q "test_iq_option.py"
if exist "CREAR_BOT_IQ_OPTION.bat" del /q "CREAR_BOT_IQ_OPTION.bat"
if exist "test_bot_completo.py" del /q "test_bot_completo.py"

echo ✅ Archivos de IQ Option eliminados

echo.
echo [2/8] 🗑️ Eliminando backend/frontend web...
echo.

if exist "backend" rmdir /s /q "backend"
if exist "frontend-web" rmdir /s /q "frontend-web"
if exist "docker-compose.yml" del /q "docker-compose.yml"
if exist "easypanel-config.yml" del /q "easypanel-config.yml"

echo ✅ Backend/Frontend web eliminados

echo.
echo [3/8] 🗑️ Eliminando archivos de deployment web...
echo.

if exist "DEPLOYMENT_EASYPANEL_FINAL.md" del /q "DEPLOYMENT_EASYPANEL_FINAL.md"
if exist "DEPLOYMENT_GUIDE.md" del /q "DEPLOYMENT_GUIDE.md"
if exist "EASYPANEL_SETUP.md" del /q "EASYPANEL_SETUP.md"
if exist "GUIA_DEPLOYMENT_EASYPANEL.md" del /q "GUIA_DEPLOYMENT_EASYPANEL.md"
if exist "VARIABLES_EASYPANEL.md" del /q "VARIABLES_EASYPANEL.md"
if exist "ARQUITECTURA_REMOTA.md" del /q "ARQUITECTURA_REMOTA.md"
if exist "RESUMEN_ARQUITECTURA_REMOTA.md" del /q "RESUMEN_ARQUITECTURA_REMOTA.md"

echo ✅ Archivos de deployment eliminados

echo.
echo [4/8] 🗑️ Eliminando archivos de versión web...
echo.

if exist "PLAN_VERSION_WEB_COMPLETO.md" del /q "PLAN_VERSION_WEB_COMPLETO.md"
if exist "VERSION_WEB_COMPLETA.md" del /q "VERSION_WEB_COMPLETA.md"
if exist "README_VERSION_WEB.md" del /q "README_VERSION_WEB.md"
if exist "COMO_EJECUTAR_VERSION_WEB.md" del /q "COMO_EJECUTAR_VERSION_WEB.md"
if exist "EJECUTAR_VERSION_WEB.md" del /q "EJECUTAR_VERSION_WEB.md"
if exist "GUIA_EJECUCION_WEB_V2.md" del /q "GUIA_EJECUCION_WEB_V2.md"
if exist "INICIO_RAPIDO_WEB.md" del /q "INICIO_RAPIDO_WEB.md"
if exist "COMANDOS_RAPIDOS_WEB.md" del /q "COMANDOS_RAPIDOS_WEB.md"
if exist "start_web.bat" del /q "start_web.bat"
if exist "start_web.sh" del /q "start_web.sh"

echo ✅ Archivos de versión web eliminados

echo.
echo [5/8] 🗑️ Eliminando archivos remotos obsoletos...
echo.

if exist "main_remote.py" del /q "main_remote.py"
if exist "main_remote_simple.py" del /q "main_remote_simple.py"
if exist "main_remote_modern.py" del /q "main_remote_modern.py"
if exist "gui_remote.py" del /q "gui_remote.py"
if exist "COMO_USAR_BOT_REMOTO.md" del /q "COMO_USAR_BOT_REMOTO.md"

echo ✅ Archivos remotos eliminados

echo.
echo [6/8] 🗑️ Eliminando documentación obsoleta...
echo.

REM Eliminar múltiples resúmenes redundantes
if exist "RESUMEN_*.md" (
    for %%f in (RESUMEN_*.md) do (
        if not "%%f"=="RESUMEN_FINAL.md" del /q "%%f"
    )
)

REM Eliminar documentación de instaladores antiguos
if exist "COMPARACION_INSTALADORES.md" del /q "COMPARACION_INSTALADORES.md"
if exist "GUIA_INSTALADOR_PROFESIONAL.md" del /q "GUIA_INSTALADOR_PROFESIONAL.md"
if exist "CREAR_INSTALADOR_WINDOWS.md" del /q "CREAR_INSTALADOR_WINDOWS.md"

REM Eliminar documentación de correcciones antiguas
if exist "CORRECCION_*.md" del /q "CORRECCION_*.md"
if exist "SOLUCION_*.md" del /q "SOLUCION_*.md"

echo ✅ Documentación obsoleta eliminada

echo.
echo [7/8] 🗑️ Eliminando archivos de compilación antiguos...
echo.

if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "installer_output" rmdir /s /q "installer_output"
if exist "*.spec" del /q "*.spec"
if exist "temp" rmdir /s /q "temp"

echo ✅ Archivos de compilación eliminados

echo.
echo [8/8] 🗑️ Eliminando archivos temporales...
echo.

REM Eliminar cache de Python
for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d" 2>nul
for /r . %%f in (*.pyc) do @if exist "%%f" del /q "%%f" 2>nul
for /r . %%f in (*.pyo) do @if exist "%%f" del /q "%%f" 2>nul

REM Eliminar logs antiguos
if exist "*.log" del /q "*.log"

echo ✅ Archivos temporales eliminados

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║          ✅ LIMPIEZA COMPLETADA                           ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo 📦 Proyecto limpio - Solo archivos de Exnova
echo.
echo 🎯 Próximo paso: Actualizar Git
echo    .\ACTUALIZAR_GIT.bat
echo.
pause
goto END

:END
