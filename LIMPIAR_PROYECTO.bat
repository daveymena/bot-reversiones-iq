@echo off
echo ============================================
echo LIMPIANDO PROYECTO PARA GIT
echo ============================================
echo.

echo [1/6] Eliminando node_modules...
if exist "frontend-web\node_modules" (
    rmdir /s /q "frontend-web\node_modules"
    echo    ✅ frontend-web\node_modules eliminado
) else (
    echo    ⏭️ No existe frontend-web\node_modules
)

if exist "backend\node_modules" (
    rmdir /s /q "backend\node_modules"
    echo    ✅ backend\node_modules eliminado
) else (
    echo    ⏭️ No existe backend\node_modules
)

echo.
echo [2/6] Eliminando __pycache__...
for /d /r %%d in (__pycache__) do @if exist "%%d" (
    rmdir /s /q "%%d"
    echo    ✅ %%d eliminado
)

echo.
echo [3/6] Eliminando archivos .pyc...
del /s /q *.pyc 2>nul
echo    ✅ Archivos .pyc eliminados

echo.
echo [4/6] Eliminando entorno virtual...
if exist "env" (
    rmdir /s /q "env"
    echo    ✅ env eliminado
) else (
    echo    ⏭️ No existe env
)

if exist "venv" (
    rmdir /s /q "venv"
    echo    ✅ venv eliminado
) else (
    echo    ⏭️ No existe venv
)

echo.
echo [5/6] Eliminando archivos temporales...
if exist "data\experiences.json" (
    del /q "data\experiences.json"
    echo    ✅ data\experiences.json eliminado
)

if exist "data\experiences_backup.json" (
    del /q "data\experiences_backup.json"
    echo    ✅ data\experiences_backup.json eliminado
)

del /q *.log 2>nul
echo    ✅ Archivos .log eliminados

echo.
echo [6/6] Eliminando .next y cache de frontend...
if exist "frontend-web\.next" (
    rmdir /s /q "frontend-web\.next"
    echo    ✅ frontend-web\.next eliminado
)

if exist "frontend-web\out" (
    rmdir /s /q "frontend-web\out"
    echo    ✅ frontend-web\out eliminado
)

echo.
echo ============================================
echo ✅ PROYECTO LIMPIO Y LISTO PARA GIT
echo ============================================
echo.
echo Tamaño reducido significativamente.
echo Ahora puedes hacer:
echo   git add .
echo   git commit -m "Bot limpio y optimizado"
echo   git push
echo.
pause
