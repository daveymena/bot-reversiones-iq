@echo off
chcp 65001 >nul
cls
echo ╔════════════════════════════════════════════════════════════╗
echo ║     ACTUALIZAR A PYTHON 3.11 - SOLUCIÓN DEFINITIVA        ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo El bot con interfaz moderna NO se puede compilar en Python 3.10
echo debido a un bug de bytecode en PyInstaller.
echo.
echo ════════════════════════════════════════════════════════════
echo.
echo 🔍 PROBLEMA:
echo    Python 3.10 + PyInstaller = Error de bytecode
echo    Con módulos: numpy, pandas, stable_baselines3, gymnasium
echo.
echo ✅ SOLUCIÓN:
echo    Actualizar a Python 3.11 o 3.12
echo.
echo ════════════════════════════════════════════════════════════
echo.
echo ⚠️ ADVERTENCIA:
echo    Esto requiere:
echo    1. Descargar Python 3.11
echo    2. Instalar Python 3.11
echo    3. Reinstalar TODAS las dependencias
echo    4. Recompilar el bot
echo.
echo    Tiempo estimado: 30-60 minutos
echo.
echo ════════════════════════════════════════════════════════════
echo.
echo ¿Deseas continuar?
echo.
echo    1. Sí, abrir página de descarga de Python 3.11
echo    2. No, usar el Bot Remoto (ya funciona)
echo    3. Salir
echo.

choice /C 123 /N /M "Selecciona (1-3): "

if errorlevel 3 goto END
if errorlevel 2 goto BOTREMOTO
if errorlevel 1 goto PYTHON311

:PYTHON311
cls
echo ╔════════════════════════════════════════════════════════════╗
echo ║     DESCARGAR PYTHON 3.11                                  ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo 🌐 Abriendo página de descarga...
echo.
start https://www.python.org/downloads/
echo.
echo ════════════════════════════════════════════════════════════
echo.
echo INSTRUCCIONES DETALLADAS:
echo.
echo 1. DESCARGAR:
echo    - Descarga "Python 3.11.x" (versión estable)
echo    - Archivo: python-3.11.x-amd64.exe
echo.
echo 2. INSTALAR:
echo    - ✅ Marca "Add Python 3.11 to PATH"
echo    - Selecciona "Install Now"
echo    - Espera a que termine
echo.
echo 3. VERIFICAR INSTALACIÓN:
echo    - Abre una nueva terminal
echo    - Ejecuta: python --version
echo    - Debe mostrar: Python 3.11.x
echo.
echo 4. REINSTALAR DEPENDENCIAS:
echo    - cd C:\trading\trading
echo    - pip install -r requirements.txt
echo.
echo 5. RECOMPILAR BOT:
echo    - .\COMPILAR_LIMPIO.bat
echo.
echo ════════════════════════════════════════════════════════════
echo.
echo 📝 NOTAS IMPORTANTES:
echo.
echo    - Puedes tener Python 3.10 y 3.11 instalados simultáneamente
echo    - Usa "py -3.11" para ejecutar con Python 3.11
echo    - O desinstala Python 3.10 primero
echo.
echo ════════════════════════════════════════════════════════════
echo.
pause
goto END

:BOTREMOTO
cls
echo ╔════════════════════════════════════════════════════════════╗
echo ║     USAR BOT REMOTO (RECOMENDADO)                         ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo El Bot Remoto ya está compilado y funciona perfectamente.
echo.
echo ✅ VENTAJAS:
echo    - Ya está compilado (238 MB)
echo    - Interfaz funcional
echo    - Arquitectura cliente-servidor moderna
echo    - Toda la IA en el backend
echo    - Más fácil de actualizar
echo    - Escalable
echo.
echo 📦 ARCHIVO:
echo    dist\TradingBotRemote.exe
echo.
echo 🎯 CREAR INSTALADOR:
echo    .\build_installer.bat
echo.
echo ════════════════════════════════════════════════════════════
echo.
pause
goto END

:END
cls
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║     RESUMEN DE OPCIONES                                    ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo 🎯 PARA COMPILAR BOT CON INTERFAZ MODERNA:
echo.
echo    Opción A: Actualizar a Python 3.11
echo    → Ejecuta: .\ACTUALIZAR_PYTHON_311.bat
echo    → Tiempo: 30-60 minutos
echo    → Resultado: Bot moderno compilado
echo.
echo 🎯 PARA USAR LO QUE YA FUNCIONA:
echo.
echo    Opción B: Usar Bot Remoto
echo    → Ya compilado: dist\TradingBotRemote.exe
echo    → Crear instalador: .\build_installer.bat
echo    → Tiempo: 5 minutos
echo    → Resultado: Instalador listo
echo.
echo ════════════════════════════════════════════════════════════
echo.
echo 💡 RECOMENDACIÓN:
echo.
echo    Si necesitas distribuir YA: Usa Bot Remoto (Opción B)
echo    Si tienes tiempo: Actualiza a Python 3.11 (Opción A)
echo.
echo ════════════════════════════════════════════════════════════
echo.
pause
