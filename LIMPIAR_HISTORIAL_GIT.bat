@echo off
chcp 65001 >nul
cls
echo ╔════════════════════════════════════════════════════════════╗
echo ║     LIMPIAR HISTORIAL DE GIT - ARCHIVOS GRANDES           ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo ⚠️ ADVERTENCIA: Esto reescribirá el historial de Git
echo.
echo Archivos a eliminar del historial:
echo   - trading/bot_errors.log (477 MB)
echo   - OllamaSetup.exe (1.1 GB)
echo.
echo ¿Continuar?
echo.

choice /C SN /N /M "(S/N): "

if errorlevel 2 goto END

echo.
echo [1/4] 🗑️ Eliminando archivos del historial de Git...
echo.

REM Eliminar archivos grandes del historial
git filter-branch --force --index-filter "git rm --cached --ignore-unmatch trading/bot_errors.log" --prune-empty --tag-name-filter cat -- --all

git filter-branch --force --index-filter "git rm --cached --ignore-unmatch OllamaSetup.exe" --prune-empty --tag-name-filter cat -- --all

echo ✅ Archivos eliminados del historial

echo.
echo [2/4] 🧹 Limpiando referencias...
echo.

git for-each-ref --format="delete %(refname)" refs/original | git update-ref --stdin
git reflog expire --expire=now --all
git gc --prune=now --aggressive

echo ✅ Referencias limpiadas

echo.
echo [3/4] 📝 Actualizando .gitignore...
echo.

echo. >> .gitignore
echo # Archivos grandes >> .gitignore
echo *.log >> .gitignore
echo trading/ >> .gitignore
echo OllamaSetup.exe >> .gitignore

git add .gitignore
git commit -m "📝 Actualizado .gitignore para evitar archivos grandes"

echo ✅ .gitignore actualizado

echo.
echo [4/4] 🚀 Subiendo cambios...
echo.

git push origin main --force

if errorlevel 1 (
    echo.
    echo ❌ Error al subir
    echo.
    echo Intenta manualmente:
    echo    git push origin main --force
    echo.
) else (
    echo.
    echo ✅ Cambios subidos exitosamente
)

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║          ✅ HISTORIAL LIMPIADO                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
pause
goto END

:END
