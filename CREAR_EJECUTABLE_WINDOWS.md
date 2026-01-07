# 💻 Crear Ejecutable Windows del Bot

## Opción 1: PyInstaller (Recomendado)

### Paso 1: Instalar PyInstaller
```bash
pip install pyinstaller
```

### Paso 2: Crear archivo spec personalizado

Crear `bot_trading.spec`:

```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main_modern.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('models', 'models'),
        ('data', 'data'),
        ('.env.example', '.'),
        ('README.md', '.'),
    ],
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'pyqtgraph',
        'pandas',
        'numpy',
        'ta',
        'stable_baselines3',
        'gymnasium',
        'psycopg2',
        'groq',
        'requests',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='TradingBotPro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Sin consola para GUI
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico'  # Agregar tu icono aquí
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='TradingBotPro',
)
```

### Paso 3: Compilar
```bash
pyinstaller bot_trading.spec
```

El ejecutable estará en: `dist/TradingBotPro/TradingBotPro.exe`

### Paso 4: Crear instalador con Inno Setup

Descargar Inno Setup: https://jrsoftware.org/isdl.php

Crear `installer.iss`:

```ini
[Setup]
AppName=Trading Bot Pro
AppVersion=2.0
DefaultDirName={pf}\TradingBotPro
DefaultGroupName=Trading Bot Pro
OutputDir=output
OutputBaseFilename=TradingBotPro_Setup
Compression=lzma2
SolidCompression=yes

[Files]
Source: "dist\TradingBotPro\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs

[Icons]
Name: "{group}\Trading Bot Pro"; Filename: "{app}\TradingBotPro.exe"
Name: "{commondesktop}\Trading Bot Pro"; Filename: "{app}\TradingBotPro.exe"

[Run]
Filename: "{app}\TradingBotPro.exe"; Description: "Ejecutar Trading Bot Pro"; Flags: postinstall nowait skipifsilent
```

Compilar con Inno Setup para crear `TradingBotPro_Setup.exe`

## Opción 2: cx_Freeze (Alternativa)

### Paso 1: Instalar
```bash
pip install cx_Freeze
```

### Paso 2: Crear setup.py
```python
from cx_Freeze import setup, Executable
import sys

build_exe_options = {
    "packages": [
        "PySide6",
        "pandas",
        "numpy",
        "ta",
        "stable_baselines3",
        "gymnasium",
        "psycopg2",
        "groq",
    ],
    "include_files": [
        ("models", "models"),
        ("data", "data"),
        (".env.example", ".env.example"),
    ],
    "excludes": ["tkinter"],
}

base = None
if sys.platform == "win32":
    base = "Win32GUI"  # Sin consola

setup(
    name="TradingBotPro",
    version="2.0",
    description="Bot de Trading Profesional con IA",
    options={"build_exe": build_exe_options},
    executables=[Executable("main_modern.py", base=base, icon="icon.ico")],
)
```

### Paso 3: Compilar
```bash
python setup.py build
```

## Opción 3: Auto-py-to-exe (GUI Fácil)

### Paso 1: Instalar
```bash
pip install auto-py-to-exe
```

### Paso 2: Ejecutar
```bash
auto-py-to-exe
```

### Paso 3: Configurar en la GUI
- **Script Location**: `main_modern.py`
- **Onefile**: No (más rápido)
- **Console Window**: No (GUI)
- **Icon**: Seleccionar `icon.ico`
- **Additional Files**: Agregar carpetas `models`, `data`
- **Hidden Imports**: Agregar todos los módulos necesarios

### Paso 4: Convertir
Click en "CONVERT .PY TO .EXE"

## Crear Icono (Opcional)

Usar herramienta online: https://www.icoconverter.com/

O con Python:
```bash
pip install pillow
```

```python
from PIL import Image

img = Image.open('logo.png')
img.save('icon.ico', format='ICO', sizes=[(256, 256)])
```

## Estructura Final del Ejecutable

```
TradingBotPro/
├── TradingBotPro.exe          # Ejecutable principal
├── _internal/                  # Librerías
│   ├── PySide6/
│   ├── pandas/
│   └── ...
├── models/                     # Modelos RL
│   └── rl_agent.zip
├── data/                       # Datos
│   └── experiences.json
└── .env.example               # Template de configuración
```

## Configuración Primera Vez

Al ejecutar por primera vez:

1. Copiar `.env.example` a `.env`
2. Editar `.env` con tus credenciales:
```bash
EXNOVA_EMAIL=tu_email@gmail.com
EXNOVA_PASSWORD=tu_password
BROKER_NAME=exnova
ACCOUNT_TYPE=PRACTICE
```

3. Ejecutar `TradingBotPro.exe`

## Distribución

### Opción A: Archivo ZIP
```bash
# Comprimir carpeta dist
Compress-Archive -Path dist\TradingBotPro -DestinationPath TradingBotPro_v2.0.zip
```

### Opción B: Instalador
Usar el `.exe` generado por Inno Setup

### Opción C: Microsoft Store (Avanzado)
Requiere cuenta de desarrollador ($19/año)

## Troubleshooting

### Error: "DLL not found"
```bash
# Incluir DLLs manualmente
pyinstaller --add-binary "C:\path\to\dll;." main_modern.py
```

### Error: "Module not found"
```bash
# Agregar hidden import
pyinstaller --hidden-import=nombre_modulo main_modern.py
```

### Ejecutable muy grande (>500MB)
```bash
# Usar UPX para comprimir
pip install pyinstaller[encryption]
pyinstaller --upx-dir=C:\upx bot_trading.spec
```

### Antivirus bloquea el ejecutable
- Firmar digitalmente el ejecutable
- O agregar excepción en el antivirus

## Actualización Automática (Futuro)

Implementar con PyUpdater:
```bash
pip install pyupdater
```

Permite actualizar el bot sin reinstalar.

## Tamaño Estimado

- **Ejecutable básico**: ~150MB
- **Con todas las dependencias**: ~300MB
- **Comprimido (ZIP)**: ~100MB
- **Instalador**: ~120MB

## Recomendación Final

Para distribución profesional:
1. ✅ Usar PyInstaller con spec personalizado
2. ✅ Crear instalador con Inno Setup
3. ✅ Firmar digitalmente (opcional)
4. ✅ Incluir README y documentación
5. ✅ Probar en PC limpia antes de distribuir
