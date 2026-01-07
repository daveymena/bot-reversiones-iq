@echo off
chcp 65001 >nul
echo ╔════════════════════════════════════════════════════════════╗
echo ║     INSTALAR DEPENDENCIAS EN PYTHON 3.11                  ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

echo Instalando todas las dependencias del proyecto en Python 3.11...
echo (Esto puede tardar 10-15 minutos)
echo.

"C:\Program Files\Python311\python.exe" -m pip install -r requirements.txt

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║          ✅ DEPENDENCIAS INSTALADAS                       ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo Ahora puedes compilar el bot con:
echo    .\COMPILAR_CON_PYTHON311.bat
echo.
pause
