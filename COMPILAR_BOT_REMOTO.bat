@echo off
chcp 65001 >nul
echo ╔════════════════════════════════════════════════════════════╗
echo ║     COMPILAR BOT REMOTO - TRADING BOT PRO                 ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

echo [1/4] 🛑 Deteniendo procesos...
taskkill /F /IM TradingBotRemote.exe 2>nul
timeout /t 2 /nobreak >nul
echo ✅ Procesos detenidos

echo.
echo [2/4] 🧹 Limpiando archivos temporales...
if exist build rmdir /s /q build 2>nul
if exist dist rmdir /s /q dist 2>nul
if exist TradingBotRemote.spec del /q TradingBotRemote.spec 2>nul
echo ✅ Limpieza completada

echo.
echo [3/4] 🔨 Compilando BOT REMOTO...
echo    (Esto puede tardar 3-5 minutos)
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

if not exist "dist\TradingBotRemote.exe" (
    echo.
    echo ❌ Error al compilar BOT REMOTO
    pause
    exit /b 1
)

echo.
echo [4/4] 📊 Información del ejecutable...
echo.
for %%A in ("dist\TradingBotRemote.exe") do (
    echo    📦 Nombre: %%~nxA
    echo    📏 Tamaño: %%~zA bytes (~%%~zAMB)
    echo    📍 Ubicación: %%~fA
)

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║          ✅ COMPILACIÓN COMPLETADA                        ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo 🎯 Próximos pasos:
echo    1. Ejecuta build_installer.bat para crear el instalador
echo    2. O distribuye directamente dist\TradingBotRemote.exe
echo.
pause
