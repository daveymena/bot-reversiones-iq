@echo off
chcp 65001 >nul
cls
echo ╔════════════════════════════════════════════════════════════╗
echo ║     TRADING BOT PRO - CREAR INSTALADOR FINAL              ║
echo ║     Bot Remoto (Cliente-Servidor)                         ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Verificar que el ejecutable ya existe
if exist "dist\TradingBotRemote.exe" (
    echo ✅ Ejecutable encontrado: dist\TradingBotRemote.exe
    for %%A in ("dist\TradingBotRemote.exe") do (
        echo    📏 Tamaño: %%~zA bytes
    )
    echo.
    echo ¿Deseas usar este ejecutable o recompilar?
    echo.
    echo    1. Usar ejecutable existente (RÁPIDO)
    echo    2. Recompilar desde cero (3-5 minutos)
    echo.
    choice /C 12 /N /M "Selecciona una opción (1 o 2): "
    
    if errorlevel 2 (
        echo.
        echo 🔨 Recompilando...
        call COMPILAR_BOT_REMOTO.bat
    ) else (
        echo.
        echo ✅ Usando ejecutable existente
    )
) else (
    echo ⚠️ Ejecutable no encontrado
    echo 🔨 Compilando bot remoto...
    echo.
    call COMPILAR_BOT_REMOTO.bat
)

echo.
echo ════════════════════════════════════════════════════════════
echo.
echo 📦 Creando instalador profesional...
echo.

REM Ejecutar el script de instalador
call build_installer.bat

echo.
echo ════════════════════════════════════════════════════════════
echo.

if exist "installer_output\TradingBotPro_Setup_v1.0.0.exe" (
    echo ╔════════════════════════════════════════════════════════════╗
    echo ║          ✅ INSTALADOR CREADO EXITOSAMENTE                ║
    echo ╚════════════════════════════════════════════════════════════╝
    echo.
    echo 📦 Archivos generados:
    echo.
    echo    1. Ejecutable portable:
    echo       📍 dist\TradingBotRemote.exe
    for %%A in ("dist\TradingBotRemote.exe") do echo       📏 %%~zA bytes (~238 MB)
    echo.
    echo    2. Instalador profesional:
    echo       📍 installer_output\TradingBotPro_Setup_v1.0.0.exe
    for %%A in ("installer_output\TradingBotPro_Setup_v1.0.0.exe") do echo       📏 %%~zA bytes
    echo.
    echo ════════════════════════════════════════════════════════════
    echo.
    echo 🎯 PRÓXIMOS PASOS:
    echo.
    echo    1. Probar el instalador:
    echo       .\installer_output\TradingBotPro_Setup_v1.0.0.exe
    echo.
    echo    2. Asegurar que el backend esté corriendo:
    echo       - Desplegado en Easypanel
    echo       - URL accesible (ej: https://tu-bot.easypanel.host)
    echo.
    echo    3. Distribuir el instalador a tus usuarios
    echo.
    echo ════════════════════════════════════════════════════════════
    echo.
    echo 📚 DOCUMENTACIÓN:
    echo.
    echo    - INSTALACION_EXITOSA.md
    echo    - SOLUCION_ERROR_COMPILACION.md
    echo    - GUIA_INSTALADOR_PROFESIONAL.md
    echo.
    echo ════════════════════════════════════════════════════════════
) else (
    echo ╔════════════════════════════════════════════════════════════╗
    echo ║          ⚠️ INSTALADOR NO CREADO                         ║
    echo ╚════════════════════════════════════════════════════════════╝
    echo.
    echo El ejecutable portable está disponible en:
    echo    📍 dist\TradingBotRemote.exe
    echo.
    echo Para crear el instalador profesional:
    echo    1. Instala Inno Setup: https://jrsoftware.org/isdl.php
    echo    2. Ejecuta este script nuevamente
    echo.
)

echo.
pause
