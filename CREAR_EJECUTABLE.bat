@echo off
echo ========================================
echo CREAR EJECUTABLE WINDOWS - TRADING BOT
echo ========================================
echo.

echo [1/5] Verificando PyInstaller...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller no instalado, instalando...
    pip install pyinstaller
) else (
    echo ✅ PyInstaller ya instalado
)

echo.
echo [2/5] Limpiando builds anteriores...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist TradingBotPro.spec del TradingBotPro.spec

echo.
echo [3/5] Creando archivo spec...
(
echo # -*- mode: python ; coding: utf-8 -*-
echo.
echo block_cipher = None
echo.
echo a = Analysis^(
echo     ['main_modern.py'],
echo     pathex=[],
echo     binaries=[],
echo     datas=[
echo         ^('models', 'models'^),
echo         ^('data', 'data'^),
echo         ^('.env.example', '.'^),
echo         ^('README.md', '.'^),
echo     ],
echo     hiddenimports=[
echo         'PySide6.QtCore',
echo         'PySide6.QtGui',
echo         'PySide6.QtWidgets',
echo         'pyqtgraph',
echo         'pandas',
echo         'numpy',
echo         'ta',
echo         'stable_baselines3',
echo         'gymnasium',
echo         'psycopg2',
echo         'groq',
echo         'requests',
echo     ],
echo     hookspath=[],
echo     hooksconfig={},
echo     runtime_hooks=[],
echo     excludes=[],
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
echo     [],
echo     exclude_binaries=True,
echo     name='TradingBotPro',
echo     debug=False,
echo     bootloader_ignore_signals=False,
echo     strip=False,
echo     upx=True,
echo     console=False,
echo     disable_windowed_traceback=False,
echo     argv_emulation=False,
echo     target_arch=None,
echo     codesign_identity=None,
echo     entitlements_file=None,
echo ^)
echo.
echo coll = COLLECT^(
echo     exe,
echo     a.binaries,
echo     a.zipfiles,
echo     a.datas,
echo     strip=False,
echo     upx=True,
echo     upx_exclude=[],
echo     name='TradingBotPro',
echo ^)
) > TradingBotPro.spec

echo ✅ Archivo spec creado

echo.
echo [4/5] Compilando ejecutable...
echo Esto puede tardar varios minutos...
pyinstaller TradingBotPro.spec

if errorlevel 1 (
    echo.
    echo ❌ ERROR en la compilación
    echo Revisa los logs arriba
    pause
    exit /b 1
)

echo.
echo [5/5] Creando archivo ZIP...
powershell -Command "Compress-Archive -Path dist\TradingBotPro -DestinationPath TradingBotPro_v2.0.zip -Force"

echo.
echo ========================================
echo ✅ EJECUTABLE CREADO EXITOSAMENTE
echo ========================================
echo.
echo Ubicación: dist\TradingBotPro\TradingBotPro.exe
echo ZIP: TradingBotPro_v2.0.zip
echo.
echo Para distribuir, usa el archivo ZIP
echo.
pause
