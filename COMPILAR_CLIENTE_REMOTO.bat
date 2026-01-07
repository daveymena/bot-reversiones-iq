@echo off
chcp 65001 >nul
color 0A
title Compilar Cliente Remoto (Solo GUI)

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║     📦 COMPILAR CLIENTE REMOTO - ULTRA LIGERO             ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo 💡 Este ejecutable SOLO contiene la GUI remota
echo    No incluye el bot completo, solo se conecta al backend
echo.

echo [1/5] 🧹 Limpiando builds anteriores...
rmdir /S /Q build 2>nul
rmdir /S /Q dist 2>nul
del /F /Q *.spec 2>nul
echo ✅ Limpieza completada

echo.
echo [2/5] 📝 Creando spec file optimizado...
(
echo # -*- mode: python ; coding: utf-8 -*-
echo.
echo block_cipher = None
echo.
echo a = Analysis^(
echo     ['main_remote_only.py'],
echo     pathex=[],
echo     binaries=[],
echo     datas=[],
echo     hiddenimports=[
echo         'PySide6.QtCore',
echo         'PySide6.QtGui',
echo         'PySide6.QtWidgets',
echo         'PySide6.QtWebSockets',
echo         'requests',
echo         'pyqtgraph',
echo         'numpy'
echo     ],
echo     hookspath=[],
echo     hooksconfig={},
echo     runtime_hooks=[],
echo     excludes=[
echo         'matplotlib',
echo         'scipy',
echo         'sklearn',
echo         'tensorflow',
echo         'torch',
echo         'pandas',
echo         'stable_baselines3',
echo         'gymnasium',
echo         'gym'
echo     ],
echo     win_no_prefer_redirects=False,
echo     win_private_assemblies=False,
echo     cipher=block_cipher,
echo     noarchive=False,
echo ^)
echo.
echo pyz = PYZ^(a.pure, a.zipped_data, cipher=block_cipher^)
echo.
echo exe = EXE^(
echo     pyz,
echo     a.scripts,
echo     a.binaries,
echo     a.zipfiles,
echo     a.datas,
echo     [],
echo     name='TradingBot_Remote',
echo     debug=False,
echo     bootloader_ignore_signals=False,
echo     strip=False,
echo     upx=True,
echo     upx_exclude=[],
echo     runtime_tmpdir=None,
echo     console=False,
echo     disable_windowed_traceback=False,
echo     argv_emulation=False,
echo     target_arch=None,
echo     codesign_identity=None,
echo     entitlements_file=None,
echo     icon='installer_resources/icon.ico'
echo ^)
) > client_remote.spec
echo ✅ Spec file creado

echo.
echo [3/5] 📦 Instalando dependencias mínimas...
pip install -q PySide6 requests pyqtgraph numpy
echo ✅ Dependencias instaladas

echo.
echo [4/5] 🔨 Compilando con PyInstaller...
python -m PyInstaller client_remote.spec --clean --noconfirm
echo ✅ Compilación completada

echo.
echo [5/5] 📦 Verificando ejecutable...
if exist "dist\TradingBot_Remote.exe" (
    echo ✅ Ejecutable creado exitosamente
    echo.
    echo 📍 Ubicación: dist\TradingBot_Remote.exe
    dir "dist\TradingBot_Remote.exe"
    echo.
    echo 📊 Tamaño del ejecutable:
    for %%A in ("dist\TradingBot_Remote.exe") do echo    %%~zA bytes ^(~%%~zA MB^)
) else (
    echo ❌ Error: No se pudo crear el ejecutable
)

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║          ✅ CLIENTE REMOTO COMPILADO                      ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo 💡 Características:
echo    ✅ Solo GUI remota (sin bot local)
echo    ✅ Tamaño ultra-ligero (~50-80 MB)
echo    ✅ No requiere Python instalado
echo    ✅ Se conecta a backend en Easypanel
echo    ✅ Portable - copia y ejecuta en cualquier PC
echo.
echo 🚀 Para usar:
echo    1. Copia TradingBot_Remote.exe a cualquier PC
echo    2. Ejecuta el .exe
echo    3. Ingresa la URL de tu backend
echo    4. ¡Listo!
echo.

pause
