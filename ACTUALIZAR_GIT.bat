@echo off
chcp 65001 >nul
cls
echo ╔════════════════════════════════════════════════════════════╗
echo ║     ACTUALIZAR GIT - PROYECTO EXNOVA                      ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

echo [1/5] 🔍 Verificando estado de Git...
echo.

git status

echo.
echo [2/5] ➕ Agregando archivos al staging...
echo.

REM Agregar todos los cambios
git add .

REM Agregar archivos eliminados
git add -u

echo ✅ Archivos agregados

echo.
echo [3/5] 📝 Creando commit...
echo.

git commit -m "✨ Bot Exnova v2.0 - Eliminado IQ Option, backend/frontend web - Solo Exnova con IA"

echo.
echo [4/5] 📊 Estado actual...
echo.

git status

echo.
echo [5/5] 🚀 ¿Subir cambios a GitHub?
echo.

choice /C SN /N /M "(S/N): "

if errorlevel 2 goto SKIP_PUSH

echo.
echo 📤 Subiendo cambios...
echo.

git push origin main

if errorlevel 1 (
    echo.
    echo ⚠️ Error al subir. Intenta:
    echo    git push origin master
    echo.
    echo O verifica tu rama con:
    echo    git branch
    echo.
) else (
    echo.
    echo ✅ Cambios subidos exitosamente
)

goto END

:SKIP_PUSH
echo.
echo ⏭️ Push omitido
echo.
echo Para subir manualmente:
echo    git push origin main
echo.

:END
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║          ✅ GIT ACTUALIZADO                               ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
pause
