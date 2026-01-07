@echo off
chcp 65001 >nul
cls
echo ╔════════════════════════════════════════════════════════════╗
echo ║     SOLUCIÓN DEFINITIVA - TRADING BOT PRO                 ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo El problema es una incompatibilidad conocida entre:
echo   - Python 3.10
echo   - PyInstaller 6.x
echo   - Módulos con bytecode optimizado
echo.
echo ════════════════════════════════════════════════════════════
echo.
echo 🔧 SOLUCIONES DISPONIBLES:
echo.
echo    1. Downgrade a PyInstaller 5.13 (RECOMENDADO)
echo    2. Usar solo el Bot Remoto (ya funciona)
echo    3. Actualizar a Python 3.11+
echo    4. Salir
echo.
echo ════════════════════════════════════════════════════════════
echo.

choice /C 1234 /N /M "Selecciona una opción (1-4): "

if errorlevel 4 goto END
if errorlevel 3 goto PYTHON311
if errorlevel 2 goto BOTREMOTO
if errorlevel 1 goto DOWNGRADE

:DOWNGRADE
cls
echo ╔════════════════════════════════════════════════════════════╗
echo ║     DOWNGRADE A PYINSTALLER 5.13                          ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo ⚠️ Esto desinstalará PyInstaller 6.x e instalará 5.13
echo.
echo ¿Continuar?
echo.

choice /C SN /N /M "(S/N): "

if errorlevel 2 goto END

echo.
echo 🔧 Desinstalando PyInstaller 6.x...
pip uninstall -y pyinstaller

echo.
echo 📦 Instalando PyInstaller 5.13.2...
pip install pyinstaller==5.13.2

echo.
echo ✅ PyInstaller 5.13.2 instalado
echo.
echo 🔨 Compilando bot moderno con PyInstaller 5.13...
echo.

REM Limpiar
if exist build rmdir /s /q build 2>nul
if exist dist\TradingBotPro.exe del /q dist\TradingBotPro.exe 2>nul

python -m PyInstaller --noconfirm ^
    --clean ^
    --onefile ^
    --windowed ^
    --name="TradingBotPro" ^
    --icon="installer_resources\icon.ico" ^
    --add-data="gui;gui" ^
    --add-data="core;core" ^
    --add-data="strategies;strategies" ^
    --add-data="ai;ai" ^
    --add-data="data;data" ^
    --add-data="exnovaapi;exnovaapi" ^
    --add-data="installer_resources\README_COMPLETO.txt;." ^
    --hidden-import="PySide6.QtCore" ^
    --hidden-import="PySide6.QtGui" ^
    --hidden-import="PySide6.QtWidgets" ^
    --hidden-import="PySide6.QtNetwork" ^
    --hidden-import="pyqtgraph" ^
    --collect-all="PySide6" ^
    --collect-all="pyqtgraph" ^
    --exclude-module="matplotlib" ^
    --exclude-module="scipy" ^
    --exclude-module="tensorflow" ^
    --exclude-module="torch" ^
    --exclude-module="pygame" ^
    --exclude-module="cv2" ^
    --exclude-module="PIL" ^
    --exclude-module="pytest" ^
    --exclude-module="IPython" ^
    --exclude-module="notebook" ^
    --exclude-module="tkinter" ^
    --log-level=WARN ^
    main_modern.py

if exist "dist\TradingBotPro.exe" (
    echo.
    echo ╔════════════════════════════════════════════════════════════╗
    echo ║          ✅ ÉXITO - BOT MODERNO COMPILADO                 ║
    echo ╚════════════════════════════════════════════════════════════╝
    echo.
    for %%A in ("dist\TradingBotPro.exe") do (
        echo    📦 Archivo: %%~nxA
        echo    📏 Tamaño: %%~zA bytes
    )
    echo.
    echo 🎯 Próximo paso:
    echo    .\build_installer_completo.bat
    echo.
) else (
    echo.
    echo ❌ Error al compilar
    echo.
    echo Si el error persiste, usa la opción 2 (Bot Remoto)
    echo.
)

pause
goto END

:BOTREMOTO
cls
echo ╔════════════════════════════════════════════════════════════╗
echo ║     USAR BOT REMOTO (YA COMPILADO)                        ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

if exist "dist\TradingBotRemote.exe" (
    echo ✅ Bot Remoto ya está compilado
    echo.
    for %%A in ("dist\TradingBotRemote.exe") do (
        echo    📦 Archivo: %%~nxA
        echo    📏 Tamaño: %%~zA bytes
    )
    echo.
    echo 💡 VENTAJAS del Bot Remoto:
    echo    - ✅ Ya funciona (compilado exitosamente)
    echo    - ✅ Interfaz funcional
    echo    - ✅ Arquitectura cliente-servidor
    echo    - ✅ Más ligero
    echo    - ✅ Fácil de actualizar
    echo.
    echo 🎯 Crear instalador:
    echo    .\build_installer.bat
    echo.
) else (
    echo ⚠️ Bot Remoto no encontrado
    echo.
    echo Compilando Bot Remoto...
    call COMPILAR_BOT_REMOTO.bat
)

pause
goto END

:PYTHON311
cls
echo ╔════════════════════════════════════════════════════════════╗
echo ║     ACTUALIZAR A PYTHON 3.11+                             ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo Para solucionar el problema definitivamente:
echo.
echo 1. Descarga Python 3.11 o 3.12:
echo    https://www.python.org/downloads/
echo.
echo 2. Instala Python 3.11+
echo.
echo 3. Reinstala todas las dependencias:
echo    pip install -r requirements.txt
echo.
echo 4. Recompila el bot:
echo    .\COMPILAR_LIMPIO.bat
echo.
echo ════════════════════════════════════════════════════════════
echo.
echo ⚠️ NOTA: Esto requiere reinstalar todo el entorno
echo.
pause
goto END

:END
cls
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║     RESUMEN DE OPCIONES                                    ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo 🎯 OPCIÓN RECOMENDADA:
echo.
echo    Opción 1: Downgrade a PyInstaller 5.13
echo    → Soluciona el problema sin cambiar Python
echo    → Compila el bot moderno con interfaz profesional
echo.
echo 🔄 OPCIÓN ALTERNATIVA:
echo.
echo    Opción 2: Usar Bot Remoto
echo    → Ya funciona (compilado exitosamente)
echo    → Arquitectura cliente-servidor moderna
echo    → Interfaz básica pero funcional
echo.
echo 📚 DOCUMENTACIÓN:
echo    - SOLUCION_ERROR_COMPILACION.md
echo    - README_INSTALACION.md
echo.
echo ════════════════════════════════════════════════════════════
echo.
pause
