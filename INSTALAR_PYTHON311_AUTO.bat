@echo off
chcp 65001 >nul
cls
echo ╔════════════════════════════════════════════════════════════╗
echo ║     INSTALACIÓN AUTOMÁTICA DE PYTHON 3.11                 ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo Este script descargará e instalará Python 3.11 automáticamente.
echo.
echo ⚠️ ADVERTENCIA:
echo    - Se descargará Python 3.11.9 (~25 MB)
echo    - Se instalará en: C:\Python311
echo    - Se agregará al PATH automáticamente
echo.
echo ¿Continuar?
echo.

choice /C SN /N /M "(S/N): "

if errorlevel 2 goto END

echo.
echo [1/4] 📥 Descargando Python 3.11.9...
echo.

REM Crear carpeta temporal
if not exist "temp" mkdir temp

REM Descargar Python 3.11.9
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe' -OutFile 'temp\python-3.11.9-amd64.exe'}"

if not exist "temp\python-3.11.9-amd64.exe" (
    echo.
    echo ❌ Error al descargar Python 3.11.9
    echo.
    echo Intenta descargar manualmente desde:
    echo https://www.python.org/downloads/release/python-3119/
    echo.
    pause
    goto END
)

echo.
echo ✅ Python 3.11.9 descargado
echo.

echo [2/4] 📦 Instalando Python 3.11.9...
echo.
echo ⚠️ Se abrirá el instalador. Por favor:
echo    1. ✅ Marca "Add Python 3.11 to PATH"
echo    2. Selecciona "Install Now"
echo    3. Espera a que termine
echo.
pause

REM Instalar Python
start /wait temp\python-3.11.9-amd64.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0

echo.
echo ✅ Python 3.11.9 instalado
echo.

echo [3/4] 🔍 Verificando instalación...
echo.

REM Verificar instalación
python --version 2>nul | findstr "3.11" >nul
if errorlevel 1 (
    echo ⚠️ Python 3.11 no detectado en PATH
    echo.
    echo Intenta cerrar y abrir una nueva terminal, luego ejecuta:
    echo    python --version
    echo.
    echo Si no funciona, reinstala Python 3.11 manualmente.
    pause
    goto END
)

echo ✅ Python 3.11 instalado correctamente
python --version
echo.

echo [4/4] 📦 Reinstalando dependencias...
echo.

REM Actualizar pip
python -m pip install --upgrade pip

REM Instalar dependencias
python -m pip install -r requirements.txt

echo.
echo ✅ Dependencias instaladas
echo.

echo ╔════════════════════════════════════════════════════════════╗
echo ║          ✅ INSTALACIÓN COMPLETADA                        ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo 🎯 Próximo paso: Compilar el bot moderno
echo.
echo    .\COMPILAR_LIMPIO.bat
echo.
echo Esto debería compilar sin errores ahora.
echo.
pause
goto END

:END
echo.
pause
