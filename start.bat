@echo off
cls
echo ========================================
echo   TRADING BOT PRO - MODO CONSOLA
echo ========================================
echo.
echo Configuracion Actual:
echo ------------------------------------
echo  Monto por operacion: $1
echo  Martingala: DESHABILITADA
echo  Horario: 7:00 AM - 11:00 AM
echo  Aprendizaje: ACTIVO
echo  Broker: Exnova
echo  Cuenta: REAL
echo ========================================
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no esta instalado
    echo Instala Python 3.10+ desde: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Verificar archivo .env
if not exist .env (
    echo ⚠️  Archivo .env no encontrado
    echo Creando .env desde .env.example...
    copy .env.example .env
    echo ✅ Archivo .env creado
    echo.
    echo ⚠️  IMPORTANTE: Edita el archivo .env con tus credenciales
    echo Presiona cualquier tecla cuando hayas configurado el .env...
    pause >nul
)

REM Verificar carpetas necesarias
if not exist data mkdir data
if not exist models mkdir models

echo 🔍 Verificando configuracion...
echo.

REM Mostrar configuracion clave del .env
findstr /C:"CAPITAL_PER_TRADE" .env
findstr /C:"MAX_MARTINGALE" .env
findstr /C:"ACCOUNT_TYPE" .env

echo.
echo ========================================
echo   IMPORTANTE - LEER ANTES DE CONTINUAR
echo ========================================
echo.
echo El bot operara con:
echo  - $1 por operacion (fijo)
echo  - SIN martingala (no duplica apuestas)
echo  - Horario: 7:00 AM - 11:00 AM
echo  - Cuenta REAL (dinero real)
echo.
echo El bot aprendera continuamente:
echo  - Guarda cada operacion
echo  - Re-entrena cada 20 operaciones
echo  - Mejora automaticamente
echo.
echo Presiona Ctrl+C para detener en cualquier momento
echo ========================================
echo.
pause

echo.
echo 🚀 Iniciando Trading Bot...
echo ========================================
echo.

REM Ejecutar el bot en modo consola
python main_console.py

echo.
echo ========================================
echo   BOT DETENIDO
echo ========================================
echo.
echo Revisa el resumen de la sesion arriba
echo.
pause
