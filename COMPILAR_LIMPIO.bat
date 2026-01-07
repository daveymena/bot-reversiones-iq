@echo off
chcp 65001 >nul
echo ╔════════════════════════════════════════════════════════════╗
echo ║     COMPILACIÓN LIMPIA - TRADING BOT PRO                  ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

echo [1/5] 🛑 Deteniendo procesos...
taskkill /F /IM TradingBotPro.exe 2>nul
taskkill /F /IM TradingBotRemote.exe 2>nul
timeout /t 2 /nobreak >nul
echo ✅ Procesos detenidos

echo.
echo [2/5] 🧹 Limpiando archivos temporales...
if exist build rmdir /s /q build 2>nul
if exist dist rmdir /s /q dist 2>nul
if exist __pycache__ rmdir /s /q __pycache__ 2>nul
if exist *.spec del /q *.spec 2>nul

REM Limpiar cache de Python
for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d" 2>nul
for /r . %%f in (*.pyc) do @if exist "%%f" del /q "%%f" 2>nul
for /r . %%f in (*.pyo) do @if exist "%%f" del /q "%%f" 2>nul

echo ✅ Limpieza completada

echo.
echo [3/5] 📦 Actualizando PyInstaller...
pip install --upgrade --force-reinstall pyinstaller
echo ✅ PyInstaller actualizado

echo.
echo [4/5] 🔨 Compilando BOT REMOTO (versión ligera)...
echo.

python -m PyInstaller --noconfirm ^
    --clean ^
    --onefile ^
    --windowed ^
    --name="TradingBotRemote" ^
    --icon="installer_resources\icon.ico" ^
    --add-data="gui;gui" ^
    --add-data="installer_resources\README_USUARIO.txt;." ^
    --hidden-import="PySide6.QtCore" ^
    --hidden-import="PySide6.QtGui" ^
    --hidden-import="PySide6.QtWidgets" ^
    --hidden-import="PySide6.QtNetwork" ^
    --collect-all="PySide6" ^
    --exclude-module="matplotlib" ^
    --exclude-module="numpy" ^
    --exclude-module="pandas" ^
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
    --exclude-module="gym" ^
    --exclude-module="gymnasium" ^
    --exclude-module="stable_baselines3" ^
    --exclude-module="tkinter" ^
    --exclude-module="setuptools._vendor" ^
    --log-level=WARN ^
    main_remote_simple.py

if exist "dist\TradingBotRemote.exe" (
    echo.
    echo ✅ BOT REMOTO compilado exitosamente
    for %%A in ("dist\TradingBotRemote.exe") do (
        echo    📦 Tamaño: %%~zA bytes
    )
) else (
    echo ❌ Error al compilar BOT REMOTO
    pause
    exit /b 1
)

echo.
echo [5/5] 🔨 Compilando BOT COMPLETO (con IA)...
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
    --add-data="models;models" ^
    --add-data="exnovaapi;exnovaapi" ^
    --add-data="installer_resources\README_COMPLETO.txt;." ^
    --hidden-import="PySide6.QtCore" ^
    --hidden-import="PySide6.QtGui" ^
    --hidden-import="PySide6.QtWidgets" ^
    --hidden-import="PySide6.QtNetwork" ^
    --hidden-import="pyqtgraph" ^
    --hidden-import="stable_baselines3" ^
    --hidden-import="gymnasium" ^
    --hidden-import="groq" ^
    --hidden-import="ta" ^
    --hidden-import="pandas" ^
    --hidden-import="numpy" ^
    --hidden-import="websocket" ^
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
    --log-level=WARN ^
    main_modern.py

if exist "dist\TradingBotPro.exe" (
    echo.
    echo ✅ BOT COMPLETO compilado exitosamente
    for %%A in ("dist\TradingBotPro.exe") do (
        echo    📦 Tamaño: %%~zA bytes
    )
) else (
    echo ❌ Error al compilar BOT COMPLETO
    pause
    exit /b 1
)

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║          ✅ COMPILACIÓN COMPLETADA                        ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo 📦 Ejecutables creados:
echo.
echo    1. TradingBotRemote.exe (Cliente ligero)
for %%A in ("dist\TradingBotRemote.exe") do echo       📏 %%~zA bytes
echo.
echo    2. TradingBotPro.exe (Versión completa con IA)
for %%A in ("dist\TradingBotPro.exe") do echo       📏 %%~zA bytes
echo.
echo 🎯 Próximos pasos:
echo    - Ejecuta build_installer.bat para crear instalador del bot remoto
echo    - Ejecuta build_installer_completo.bat para crear instalador del bot completo
echo.
pause
