@echo off
chcp 65001 >nul
:MENU
cls
echo ╔════════════════════════════════════════════════════════════╗
echo ║     TRADING BOT PRO - MENÚ DE INSTALACIÓN                 ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo 📦 Estado Actual:
echo.

if exist "dist\TradingBotRemote.exe" (
    echo    ✅ Bot Remoto compilado
    for %%A in ("dist\TradingBotRemote.exe") do echo       📏 %%~zA bytes (~238 MB)
) else (
    echo    ❌ Bot Remoto NO compilado
)

if exist "installer_output\TradingBotPro_Setup_v1.0.0.exe" (
    echo    ✅ Instalador creado
    for %%A in ("installer_output\TradingBotPro_Setup_v1.0.0.exe") do echo       📏 %%~zA bytes
) else (
    echo    ❌ Instalador NO creado
)

echo.
echo ════════════════════════════════════════════════════════════
echo.
echo 🎯 OPCIONES DISPONIBLES:
echo.
echo    1. 🚀 Crear instalador (RÁPIDO - usa ejecutable existente)
echo    2. 🔨 Recompilar bot remoto (3-5 minutos)
echo    3. 🎁 Proceso completo automático
echo    4. 🧹 Limpiar todo y empezar de cero
echo    5. 📚 Ver documentación
echo    6. ❌ Salir
echo.
echo ════════════════════════════════════════════════════════════
echo.

choice /C 123456 /N /M "Selecciona una opción (1-6): "

if errorlevel 6 goto END
if errorlevel 5 goto DOCS
if errorlevel 4 goto CLEAN
if errorlevel 3 goto FULL
if errorlevel 2 goto COMPILE
if errorlevel 1 goto INSTALLER

:INSTALLER
cls
echo ╔════════════════════════════════════════════════════════════╗
echo ║     CREAR INSTALADOR                                       ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

if not exist "dist\TradingBotRemote.exe" (
    echo ❌ Error: No existe el ejecutable
    echo.
    echo Primero debes compilar el bot remoto (opción 2)
    echo.
    pause
    goto MENU
)

call build_installer.bat
pause
goto MENU

:COMPILE
cls
echo ╔════════════════════════════════════════════════════════════╗
echo ║     COMPILAR BOT REMOTO                                    ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

call COMPILAR_BOT_REMOTO.bat
pause
goto MENU

:FULL
cls
echo ╔════════════════════════════════════════════════════════════╗
echo ║     PROCESO COMPLETO AUTOMÁTICO                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

call CREAR_INSTALADOR_FINAL.bat
pause
goto MENU

:CLEAN
cls
echo ╔════════════════════════════════════════════════════════════╗
echo ║     LIMPIAR TODO                                           ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo ⚠️ ADVERTENCIA: Esto eliminará:
echo    - dist\
echo    - build\
echo    - installer_output\
echo    - *.spec
echo.
echo ¿Estás seguro?
echo.

choice /C SN /N /M "¿Continuar? (S/N): "

if errorlevel 2 goto MENU

echo.
echo 🧹 Limpiando...
echo.

taskkill /F /IM TradingBotRemote.exe 2>nul
taskkill /F /IM TradingBotPro.exe 2>nul
timeout /t 2 /nobreak >nul

if exist build rmdir /s /q build 2>nul
if exist dist rmdir /s /q dist 2>nul
if exist installer_output rmdir /s /q installer_output 2>nul
if exist *.spec del /q *.spec 2>nul

for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d" 2>nul

echo.
echo ✅ Limpieza completada
echo.
pause
goto MENU

:DOCS
cls
echo ╔════════════════════════════════════════════════════════════╗
echo ║     DOCUMENTACIÓN DISPONIBLE                               ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo 📚 Archivos de documentación:
echo.
echo    1. README_INSTALACION.md
echo       → Guía completa de instalación
echo.
echo    2. INSTALACION_EXITOSA.md
echo       → Estado actual y próximos pasos
echo.
echo    3. SOLUCION_ERROR_COMPILACION.md
echo       → Solución al error del bot completo
echo.
echo    4. GUIA_INSTALADOR_PROFESIONAL.md
echo       → Guía detallada del instalador
echo.
echo    5. COMPARACION_INSTALADORES.md
echo       → Comparación de opciones
echo.
echo ════════════════════════════════════════════════════════════
echo.
echo 🎯 RESUMEN RÁPIDO:
echo.
echo    ✅ Bot Remoto: FUNCIONAL (238 MB)
echo    ❌ Bot Completo: Error de compilación
echo.
echo    💡 Solución: Usar Bot Remoto (cliente-servidor)
echo.
echo    📦 Arquitectura:
echo       Cliente (Windows) ← → Backend (Easypanel) ← → Brokers
echo.
echo    🚀 Ventajas:
echo       - Más ligero
echo       - Fácil de actualizar
echo       - IA centralizada
echo       - Sin errores de compilación
echo.
echo ════════════════════════════════════════════════════════════
echo.
pause
goto MENU

:END
cls
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║     GRACIAS POR USAR TRADING BOT PRO                      ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo 📦 Estado Final:
echo.

if exist "dist\TradingBotRemote.exe" (
    echo    ✅ Bot Remoto: LISTO
) else (
    echo    ⚠️ Bot Remoto: Pendiente de compilar
)

if exist "installer_output\TradingBotPro_Setup_v1.0.0.exe" (
    echo    ✅ Instalador: LISTO PARA DISTRIBUIR
    echo.
    echo    📍 Ubicación: installer_output\TradingBotPro_Setup_v1.0.0.exe
) else (
    echo    ⚠️ Instalador: Pendiente de crear
)

echo.
echo 📚 Documentación: README_INSTALACION.md
echo.
echo ════════════════════════════════════════════════════════════
echo.
pause
exit
