@echo off
chcp 65001 >nul
echo ╔════════════════════════════════════════════════════════════╗
echo ║     DESCARGAR INNO SETUP                                   ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo Inno Setup es necesario para crear el instalador profesional.
echo.
echo 🌐 Abriendo página de descarga...
echo.
start https://jrsoftware.org/isdl.php
echo.
echo ════════════════════════════════════════════════════════════
echo.
echo INSTRUCCIONES:
echo.
echo 1. Descarga "innosetup-6.x.x.exe" (versión estable)
echo 2. Ejecuta el instalador
echo 3. Sigue el asistente de instalación
echo 4. Una vez instalado, ejecuta: .\build_installer.bat
echo.
echo ════════════════════════════════════════════════════════════
echo.
pause
