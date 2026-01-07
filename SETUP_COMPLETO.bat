@echo off
echo ============================================
echo SETUP COMPLETO: EXNOVA + IQ OPTION
echo ============================================
echo.
echo Este script hará:
echo 1. Limpiar proyecto Exnova actual
echo 2. Crear bot separado para IQ Option
echo 3. Preparar todo para Git
echo.
echo ¿Continuar? (S/N)
set /p RESPUESTA=
if /i not "%RESPUESTA%"=="S" (
    echo Operación cancelada.
    pause
    exit /b
)

echo.
echo ============================================
echo PASO 1: LIMPIANDO PROYECTO EXNOVA
echo ============================================
call LIMPIAR_PROYECTO.bat

echo.
echo ============================================
echo PASO 2: CREANDO BOT IQ OPTION
echo ============================================
call CREAR_BOT_IQ_OPTION.bat

echo.
echo ============================================
echo ✅ SETUP COMPLETO FINALIZADO
echo ============================================
echo.
echo 📁 Estructura creada:
echo    C:\trading\trading\      ← Bot Exnova (limpio)
echo    C:\trading\trading-iq\   ← Bot IQ Option (nuevo)
echo.
echo 📋 PRÓXIMOS PASOS:
echo.
echo Para Bot IQ Option:
echo   1. cd C:\trading\trading-iq
echo   2. python -m venv env
echo   3. env\Scripts\activate
echo   4. pip install -r requirements_iq.txt
echo   5. pip install https://github.com/Lu-Yi-Hsun/iqoptionapi/archive/master.zip
echo   6. Editar .env con credenciales
echo   7. python main_modern.py
echo.
echo Para subir Exnova a Git:
echo   1. git add .
echo   2. git commit -m "Bot Exnova optimizado"
echo   3. git push
echo.
pause
