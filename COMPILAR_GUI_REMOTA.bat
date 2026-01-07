@echo off
chcp 65001 >nul
color 0A
title Compilar GUI Remota

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║     📦 COMPILAR GUI REMOTA (Cliente de Escritorio)       ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

echo [1/4] 🧹 Limpiando builds anteriores...
rmdir /S /Q build 2>nul
rmdir /S /Q dist 2>nul
del /F /Q *.spec 2>nul
echo ✅ Limpieza completada

echo.
echo [2/4] 📝 Creando spec file...
(
echo # -*- mode: python ; coding: utf-8 -*-
echo.
echo block_cipher = None
echo.
echo a = Analysis^(
echo     ['main_remote.py'],
echo     pathex=[],
echo     binaries=[],
echo     datas=[],
echo     hiddenimports=[
echo         'PySide6.QtCore',
echo         'PySide6.QtGui',
echo         'PySide6.QtWidgets',
echo         'PySide6.QtWebSockets',
echo         'requests',
echo         'pyqtgraph'
echo     ],
echo     hookspath=[],
echo     hooksconfig={},
echo     runtime_hooks=[],
echo     excludes=[
echo         'matplotlib',
echo         'scipy',
echo         'sklearn',
echo         'tensorflow',
echo         'torch'
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
) > gui_remote.spec
echo ✅ Spec file creado

echo.
echo [3/4] 🔨 Compilando con PyInstaller...
pyinstaller gui_remote.spec --clean
echo ✅ Compilación completada

echo.
echo [4/4] 📦 Verificando ejecutable...
if exist "dist\TradingBot_Remote.exe" (
    echo ✅ Ejecutable creado exitosamente
    echo.
    echo 📍 Ubicación: dist\TradingBot_Remote.exe
    dir "dist\TradingBot_Remote.exe"
) else (
    echo ❌ Error: No se pudo crear el ejecutable
)

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║          ✅ PROCESO COMPLETADO                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo 💡 Ejecuta: dist\TradingBot_Remote.exe
echo.

pause
