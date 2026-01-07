@echo off
chcp 65001 >nul
cls
echo ╔════════════════════════════════════════════════════════════╗
echo ║     LIMPIAR ARCHIVOS GRANDES DE GIT                       ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo Eliminando archivos grandes que GitHub rechaza...
echo.

echo [1/5] 🗑️ Eliminando logs grandes...
if exist "trading\bot_errors.log" del /q "trading\bot_errors.log"
if exist "*.log" del /q "*.log"
if exist "logs\*.log" del /q "logs\*.log"
echo ✅ Logs eliminados

echo.
echo [2/5] 🗑️ Eliminando ejecutables grandes...
if exist "OllamaSetup.exe" del /q "OllamaSetup.exe"
if exist "*.exe" del /q "*.exe"
echo ✅ Ejecutables eliminados

echo.
echo [3/5] 🗑️ Eliminando carpeta trading-iq...
if exist "..\trading-iq" rmdir /s /q "..\trading-iq"
echo ✅ Carpeta trading-iq eliminada

echo.
echo [4/5] 🧹 Limpiando historial de Git...
git rm --cached -r trading/bot_errors.log 2>nul
git rm --cached -r OllamaSetup.exe 2>nul
git rm --cached -r *.exe 2>nul
git rm --cached -r *.log 2>nul
echo ✅ Archivos removidos del staging

echo.
echo [5/5] 📝 Actualizando .gitignore...
echo. >> .gitignore
echo # Archivos grandes >> .gitignore
echo *.log >> .gitignore
echo *.exe >> .gitignore
echo OllamaSetup.exe >> .gitignore
echo trading/ >> .gitignore
echo ../trading-iq/ >> .gitignore
echo ✅ .gitignore actualizado

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║          ✅ LIMPIEZA COMPLETADA                           ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo 🎯 Próximos pasos:
echo.
echo 1. Crear nuevo commit:
echo    git add .
echo    git commit -m "🧹 Eliminados archivos grandes y carpeta trading-iq"
echo.
echo 2. Subir cambios:
echo    git push origin main --force
echo.
pause
