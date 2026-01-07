@echo off
chcp 65001 >nul
echo ╔════════════════════════════════════════════════════════════╗
echo ║     COMPILAR BOT MODERNO LITE - TRADING BOT PRO           ║
echo ║     Interfaz Moderna + Análisis Técnico + LLM             ║
echo ║     (Sin módulos RL problemáticos)                        ║
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
echo [3/4] 🔨 Compilando BOT MODERNO LITE...
echo    ✅ Interfaz moderna profesional
echo    ✅ Análisis técnico avanzado
echo    ✅ Validación LLM (Groq/Ollama)
echo    ⚠️ Sin Reinforcement Learning
echo.
echo    (Esto puede tardar 3-5 minutos)
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
    --log-level=WARN ^
    main_modern_lite.py

if not exist "dist\TradingBotPro.exe" (
    echo.
    echo ❌ Error al compilar BOT MODERNO LITE
    echo.
    echo Ver errores arriba para más detalles
    pause
    exit /b 1
)

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
echo 📦 Bot Moderno Lite creado exitosamente
echo.
echo ✅ INCLUYE:
echo    - Interfaz moderna profesional
echo    - Gráficos en tiempo real (pyqtgraph)
echo    - Análisis técnico avanzado (RSI, MACD, Bollinger, etc.)
echo    - Validación LLM (Groq/Ollama)
echo    - Smart Money Concepts
echo    - Gestión de riesgo
echo    - Multi-activos
echo.
echo ⚠️ NO INCLUYE:
echo    - Reinforcement Learning (PPO)
echo    - Entrenamiento de modelos
echo    - Módulos numpy/pandas pesados
echo.
echo 💡 VENTAJAS:
echo    - Compila sin errores
echo    - Más ligero
echo    - Análisis técnico robusto
echo    - LLM para validación
echo.
echo 🎯 Próximos pasos:
echo    1. Ejecuta build_installer_completo.bat para crear instalador
echo    2. O distribuye directamente dist\TradingBotPro.exe
echo.
pause
