@echo off
chcp 65001 >nul
color 0A
title Compilar GUI Profesional Remota

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║     📦 COMPILAR GUI PROFESIONAL - MODO REMOTO             ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo 💡 Usa la GUI moderna profesional conectada a Easypanel
echo.

echo [1/4] 🧹 Limpiando builds anteriores...
rmdir /S /Q build 2>nul
rmdir /S /Q dist 2>nul
del /F /Q *.spec 2>nul
echo ✅ Limpieza completada

echo.
echo [2/4] 📝 Compilando con Python 3.11.9...
py -3.11 -m PyInstaller ^
    --name="TradingBot_Pro" ^
    --onefile ^
    --windowed ^
    --icon=installer_resources/icon.ico ^
    --hidden-import=PySide6.QtCore ^
    --hidden-import=PySide6.QtGui ^
    --hidden-import=PySide6.QtWidgets ^
    --hidden-import=PySide6.QtWebSockets ^
    --hidden-import=pyqtgraph ^
    --hidden-import=requests ^
    --hidden-import=numpy ^
    --collect-data=PySide6 ^
    --exclude-module=matplotlib ^
    --exclude-module=scipy ^
    --exclude-module=pandas ^
    --exclude-module=stable_baselines3 ^
    --exclude-module=gymnasium ^
    --exclude-module=gym ^
    --exclude-module=torch ^
    --exclude-module=tensorflow ^
    main_modern.py

if exist "dist\TradingBot_Pro.exe" (
    echo.
    echo ✅ Ejecutable creado exitosamente
    echo.
    echo 📍 Ubicación: dist\TradingBot_Pro.exe
    dir "dist\TradingBot_Pro.exe"
    echo.
    echo 📊 Tamaño:
    for %%A in ("dist\TradingBot_Pro.exe") do echo    %%~zAz bytes (~%%~zA MB)
) else (
    echo.
    echo ❌ Error: No se pudo crear el ejecutable
)

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║          ✅ COMPILACIÓN COMPLETADA                        ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo 💡 Características:
echo    ✅ GUI profesional moderna (la que ya tienes)
echo    ✅ Gráficos de velas japonesas
echo    ✅ Indicadores técnicos en tiempo real
echo    ✅ Modo Local o Remoto (seleccionas al abrir)
echo    ✅ Se conecta a Easypanel cuando eliges remoto
echo.

pause
