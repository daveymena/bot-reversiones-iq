@echo off
chcp 65001 >nul
echo ╔════════════════════════════════════════════════════════════╗
echo ║     COMPILAR BOT MODERNO - TRADING BOT PRO                ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

echo [1/4] 🛑 Deteniendo procesos...
taskkill /F /IM TradingBotPro.exe 2>nul
timeout /t 2 /nobreak >nul
echo ✅ Procesos detenidos

echo.
echo [2/4] 🧹 Limpiando archivos temporales...
if exist build rmdir /s /q build 2>nul
if exist dist\TradingBotPro.exe del /q dist\TradingBotPro.exe 2>nul
if exist TradingBotPro.spec del /q TradingBotPro.spec 2>nul
echo ✅ Limpieza completada

echo.
echo [3/4] 🔨 Compilando BOT MODERNO (con interfaz profesional)...
echo    ⚠️ NOTA: Esto puede tardar 5-10 minutos
echo    ⚠️ Si falla, usaremos una versión sin módulos problemáticos
echo.

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
    --hidden-import="pyqtgraph.graphicsItems" ^
    --hidden-import="pyqtgraph.exporters" ^
    --hidden-import="websocket" ^
    --hidden-import="websocket._app" ^
    --hidden-import="ta" ^
    --hidden-import="groq" ^
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
    --exclude-module="setuptools._vendor" ^
    --exclude-module="setuptools.command" ^
    --exclude-module="distutils" ^
    --log-level=ERROR ^
    main_modern.py

if exist "dist\TradingBotPro.exe" (
    echo.
    echo ✅ BOT MODERNO compilado exitosamente
    goto SUCCESS
) else (
    echo.
    echo ❌ Error al compilar con módulos IA/ML
    echo 🔧 Intentando compilación alternativa sin módulos problemáticos...
    echo.
    goto ALTERNATIVE
)

:ALTERNATIVE
echo Creando versión alternativa sin stable_baselines3 y gymnasium...
echo.

REM Limpiar
if exist build rmdir /s /q build 2>nul
if exist TradingBotPro.spec del /q TradingBotPro.spec 2>nul

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
    --hidden-import="websocket" ^
    --hidden-import="ta" ^
    --hidden-import="groq" ^
    --collect-all="PySide6" ^
    --collect-all="pyqtgraph" ^
    --exclude-module="stable_baselines3" ^
    --exclude-module="gymnasium" ^
    --exclude-module="gym" ^
    --exclude-module="numpy" ^
    --exclude-module="pandas" ^
    --exclude-module="matplotlib" ^
    --exclude-module="scipy" ^
    --exclude-module="tensorflow" ^
    --exclude-module="torch" ^
    --exclude-module="sklearn" ^
    --exclude-module="pygame" ^
    --exclude-module="cv2" ^
    --exclude-module="PIL" ^
    --exclude-module="pytest" ^
    --exclude-module="IPython" ^
    --exclude-module="notebook" ^
    --exclude-module="tkinter" ^
    --exclude-module="setuptools._vendor" ^
    --log-level=ERROR ^
    main_modern.py

if not exist "dist\TradingBotPro.exe" (
    echo.
    echo ❌ Error al compilar versión alternativa
    echo.
    echo 💡 SOLUCIÓN:
    echo    El bot moderno requiere módulos que tienen problemas de compilación.
    echo    Opciones:
    echo.
    echo    1. Usar el Bot Remoto (ya compilado, interfaz básica pero funcional)
    echo    2. Actualizar a Python 3.11+ y reintentar
    echo    3. Crear una versión del bot moderno sin RL (solo análisis técnico)
    echo.
    pause
    exit /b 1
)

:SUCCESS
echo.
echo [4/4] 📊 Información del ejecutable...
echo.
for %%A in ("dist\TradingBotPro.exe") do (
    echo    📦 Nombre: %%~nxA
    echo    📏 Tamaño: %%~zA bytes
    echo    📍 Ubicación: %%~fA
)

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║          ✅ COMPILACIÓN COMPLETADA                        ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo 🎯 Próximos pasos:
echo    1. Ejecuta build_installer_completo.bat para crear instalador
echo    2. O distribuye directamente dist\TradingBotPro.exe
echo.
echo ⚠️ NOTA: Si el bot no incluye RL, el entrenamiento no funcionará
echo    pero el análisis técnico y LLM sí funcionarán.
echo.
pause
