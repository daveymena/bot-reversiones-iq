@echo off
REM Script para generar ejecutable standalone del Trading Bot Client
REM Este .exe funcionará en cualquier PC Windows sin Python instalado

echo ============================================================
echo GENERADOR DE EJECUTABLE - TRADING BOT CLIENT
echo ============================================================
echo.

REM Activar ambiente virtual
echo [1/4] Activando ambiente virtual...
call env\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ERROR: No se pudo activar el ambiente virtual
    echo Crea uno con: python -m venv env
    pause
    exit /b 1
)

REM Instalar PyInstaller si no está
echo.
echo [2/4] Verificando PyInstaller...
pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo Instalando PyInstaller...
    pip install pyinstaller
)

REM Generar ejecutable
echo.
echo [3/4] Generando ejecutable standalone...
pyinstaller --onefile ^
    --windowed ^
    --name=TradingBotClient ^
    --add-data="gui;gui" ^
    --add-data="backend/api;backend/api" ^
    --hidden-import=PySide6 ^
    --hidden-import=PySide6.QtCore ^
    --hidden-import=PySide6.QtGui ^
    --hidden-import=PySide6.QtWidgets ^
    --hidden-import=requests ^
    --hidden-import=websockets ^
    --hidden-import=pyqtgraph ^
    --hidden-import=numpy ^
    --exclude-module=torch ^
    --exclude-module=tensorflow ^
    --exclude-module=stable_baselines3 ^
    --exclude-module=exnovaapi ^
    --exclude-module=data ^
    --exclude-module=core ^
    --exclude-module=strategies ^
    --exclude-module=ai ^
    --clean ^
    run_client.py

if %errorlevel% neq 0 (
    echo ERROR: Fallo al generar ejecutable
    pause
    exit /b 1
)

REM Limpiar archivos temporales
echo.
echo [4/4] Limpiando archivos temporales...
if exist build rmdir /s /q build
if exist __pycache__ rmdir /s /q __pycache__

echo.
echo ============================================================
echo EJECUTABLE GENERADO EXITOSAMENTE
echo ============================================================
echo.
echo Ubicacion: dist\TradingBotClient.exe
echo.
echo Este archivo es COMPLETAMENTE INDEPENDIENTE:
echo - NO requiere Python instalado
echo - Funciona en cualquier Windows 10/11
echo - Incluye todas las dependencias necesarias
echo.
echo Puedes copiar TradingBotClient.exe a cualquier PC y funcionara.
echo.
pause
