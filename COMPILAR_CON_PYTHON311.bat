@echo off
chcp 65001 >nul
echo ╔════════════════════════════════════════════════════════════╗
echo ║     COMPILAR BOT MODERNO CON PYTHON 3.11                  ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

echo [1/5] 🔍 Verificando Python 3.11...
echo.

"C:\Program Files\Python311\python.exe" --version 2>nul
if errorlevel 1 (
    echo ❌ Python 3.11 no encontrado en C:\Program Files\Python311
    echo.
    echo Verifica la instalación de Python 3.11
    pause
    exit /b 1
)

echo ✅ Python 3.11 encontrado
"C:\Program Files\Python311\python.exe" --version
echo.

echo [2/5] 📦 Instalando PyInstaller en Python 3.11...
echo.

"C:\Program Files\Python311\python.exe" -m pip install --upgrade pyinstaller

echo.
echo [3/5] 🧹 Limpiando builds anteriores...
echo.

taskkill /F /IM TradingBotPro.exe 2>nul
timeout /t 2 /nobreak >nul

if exist build rmdir /s /q build 2>nul
if exist dist\TradingBotPro.exe del /q dist\TradingBotPro.exe 2>nul
if exist TradingBotPro.spec del /q TradingBotPro.spec 2>nul

echo ✅ Limpieza completada
echo.

echo [4/5] 🔨 Compilando BOT MODERNO con Python 3.11...
echo    (Esto puede tardar 5-10 minutos)
echo.

"C:\Program Files\Python311\python.exe" -m PyInstaller --noconfirm ^
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

if not exist "dist\TradingBotPro.exe" (
    echo.
    echo ❌ Error al compilar BOT MODERNO
    echo.
    pause
    exit /b 1
)

echo.
echo [5/5] 📊 Información del ejecutable...
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
echo 🎉 Bot moderno con interfaz profesional compilado exitosamente
echo.
echo 🎯 Próximo paso:
echo    .\build_installer_completo.bat
echo.
pause
