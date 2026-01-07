@echo off
echo ========================================
echo Ejecutando GUI Limpia
echo ========================================
echo.

REM Cerrar todos los procesos Python
echo 1. Cerrando procesos Python anteriores...
taskkill /F /IM python.exe 2>nul
timeout /t 2 /nobreak >nul

REM Verificar que no haya procesos
echo 2. Verificando procesos...
tasklist /FI "IMAGENAME eq python.exe" | find /I "python.exe" >nul
if %ERRORLEVEL% EQU 0 (
    echo    ADVERTENCIA: Aun hay procesos Python corriendo
) else (
    echo    OK: No hay procesos Python
)

echo.
echo 3. Iniciando GUI moderna...
echo.
python main_modern.py

pause
