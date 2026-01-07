@echo off
chcp 65001 >nul
echo ╔════════════════════════════════════════════════════════════╗
echo ║     TRADING BOT PRO - INSTALADOR PROFESIONAL              ║
echo ║     Creando instalador para Windows                       ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Verificar que estamos en el directorio correcto
if not exist "main_remote.py" (
    echo ❌ Error: No se encuentra main_remote.py
    echo    Ejecuta este script desde la carpeta raíz del proyecto
    pause
    exit /b 1
)

echo [1/8] 📦 Verificando dependencias...
echo.

REM Verificar PyInstaller
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo    ⚙️ Instalando PyInstaller...
    pip install pyinstaller
) else (
    echo    ✅ PyInstaller instalado
)

REM Verificar Pillow (para iconos)
pip show pillow >nul 2>&1
if errorlevel 1 (
    echo    ⚙️ Instalando Pillow...
    pip install pillow
) else (
    echo    ✅ Pillow instalado
)

echo.
echo [2/8] 🎨 Creando recursos visuales...
echo.

REM Crear carpeta de recursos
if not exist "installer_resources" mkdir installer_resources

REM Crear icono (si no existe)
if not exist "installer_resources\icon.ico" (
    echo    ⚙️ Generando icono por defecto...
    python -c "from PIL import Image, ImageDraw; img = Image.new('RGB', (256, 256), color='#1e3a8a'); draw = ImageDraw.Draw(img); draw.rectangle([50, 50, 206, 206], fill='#3b82f6'); draw.rectangle([80, 80, 176, 176], fill='#60a5fa'); img.save('installer_resources/icon.ico', format='ICO', sizes=[(256,256), (128,128), (64,64), (48,48), (32,32), (16,16)])"
    echo    ✅ Icono creado
) else (
    echo    ✅ Icono existente
)

REM Crear banner para instalador
if not exist "installer_resources\banner.bmp" (
    echo    ⚙️ Generando banner...
    python -c "from PIL import Image, ImageDraw, ImageFont; img = Image.new('RGB', (497, 58), color='#1e3a8a'); draw = ImageDraw.Draw(img); draw.text((20, 15), 'Trading Bot Pro', fill='white'); img.save('installer_resources/banner.bmp')"
    echo    ✅ Banner creado
) else (
    echo    ✅ Banner existente
)

echo.
echo [3/8] 📄 Creando archivos de documentación...
echo.

REM Crear LICENSE.txt
if not exist "installer_resources\LICENSE.txt" (
    (
        echo LICENCIA DE USO - TRADING BOT PRO
        echo.
        echo Copyright ^(c^) 2025 Trading Bot Pro
        echo.
        echo Este software se proporciona "tal cual", sin garantía de ningún tipo.
        echo El uso de este software es bajo tu propio riesgo.
        echo.
        echo TÉRMINOS DE USO:
        echo.
        echo 1. Este software es para uso personal o comercial.
        echo 2. No se permite la redistribución sin autorización.
        echo 3. El autor no se hace responsable de pérdidas financieras.
        echo 4. Usa siempre la cuenta PRACTICE antes de operar con dinero real.
        echo.
        echo Para soporte, visita: https://github.com/tu-usuario/trading-bot
    ) > "installer_resources\LICENSE.txt"
    echo    ✅ LICENSE.txt creado
) else (
    echo    ✅ LICENSE.txt existente
)

REM Crear README para usuarios finales
if not exist "installer_resources\README_USUARIO.txt" (
    (
        echo ╔════════════════════════════════════════════════════════════╗
        echo ║           TRADING BOT PRO - GUÍA DE INICIO                ║
        echo ╚════════════════════════════════════════════════════════════╝
        echo.
        echo ¡Gracias por instalar Trading Bot Pro!
        echo.
        echo 🚀 INICIO RÁPIDO:
        echo.
        echo 1. Ejecuta "Trading Bot Remote" desde el menú inicio
        echo 2. Ingresa la URL de tu servidor ^(ej: https://tu-bot.easypanel.host^)
        echo 3. Haz clic en "Probar Conexión"
        echo 4. Ingresa tus credenciales del broker
        echo 5. Conecta al broker
        echo 6. ¡Inicia el bot!
        echo.
        echo ⚠️ IMPORTANTE:
        echo.
        echo - Usa SIEMPRE la cuenta PRACTICE primero
        echo - Verifica que el servidor esté corriendo
        echo - Mantén tus credenciales seguras
        echo.
        echo 📚 DOCUMENTACIÓN:
        echo.
        echo Visita: https://github.com/tu-usuario/trading-bot/wiki
        echo.
        echo 📞 SOPORTE:
        echo.
        echo Email: soporte@tradingbotpro.com
        echo Discord: discord.gg/tradingbotpro
        echo.
        echo ═══════════════════════════════════════════════════════════
        echo Trading Bot Pro v1.0 - 2025
        echo ═══════════════════════════════════════════════════════════
    ) > "installer_resources\README_USUARIO.txt"
    echo    ✅ README_USUARIO.txt creado
) else (
    echo    ✅ README_USUARIO.txt existente
)

echo.
echo [4/8] 🧹 Limpiando builds anteriores...
echo.

if exist "build" (
    rmdir /s /q "build"
    echo    ✅ Carpeta build eliminada
)

if exist "dist" (
    rmdir /s /q "dist"
    echo    ✅ Carpeta dist eliminada
)

if exist "installer_output" (
    rmdir /s /q "installer_output"
    echo    ✅ Carpeta installer_output eliminada
)

echo.
echo [5/8] 🔨 Compilando ejecutable...
echo    (Esto puede tardar 3-5 minutos)
echo.

python -m PyInstaller --noconfirm ^
    --onefile ^
    --windowed ^
    --name="TradingBotRemote" ^
    --icon="installer_resources\icon.ico" ^
    --add-data "gui;gui" ^
    --add-data "installer_resources\README_USUARIO.txt;." ^
    --hidden-import="PySide6.QtCore" ^
    --hidden-import="PySide6.QtGui" ^
    --hidden-import="PySide6.QtWidgets" ^
    --exclude-module="matplotlib" ^
    --exclude-module="numpy" ^
    --exclude-module="pandas" ^
    --exclude-module="scipy" ^
    --exclude-module="tensorflow" ^
    --exclude-module="torch" ^
    --exclude-module="sklearn" ^
    --exclude-module="pygame" ^
    --exclude-module="cv2" ^
    --exclude-module="PIL" ^
    --exclude-module="pytest" ^
    --exclude-module="IPython" ^
    --exclude-module="notebook" ^
    --exclude-module="gym" ^
    --exclude-module="gymnasium" ^
    --exclude-module="stable_baselines3" ^
    main_remote_simple.py

if not exist "dist\TradingBotRemote.exe" (
    echo.
    echo ❌ ERROR: No se pudo crear el ejecutable
    echo    Revisa los errores arriba
    pause
    exit /b 1
)

echo.
echo    ✅ Ejecutable creado exitosamente
echo.

echo [6/8] 📊 Información del ejecutable...
echo.
for %%A in ("dist\TradingBotRemote.exe") do (
    echo    📦 Nombre: %%~nxA
    echo    📏 Tamaño: %%~zA bytes ^(~%%~zA / 1048576 MB^)
    echo    📍 Ubicación: %%~fA
)

echo.
echo [7/8] 📝 Creando script de Inno Setup...
echo.

REM Crear script de Inno Setup
(
    echo ; Script generado automáticamente para Trading Bot Pro
    echo ; Instalador profesional para Windows
    echo.
    echo #define MyAppName "Trading Bot Pro"
    echo #define MyAppVersion "1.0.0"
    echo #define MyAppPublisher "Trading Bot Pro Team"
    echo #define MyAppURL "https://github.com/tu-usuario/trading-bot"
    echo #define MyAppExeName "TradingBotRemote.exe"
    echo.
    echo [Setup]
    echo AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
    echo AppName={#MyAppName}
    echo AppVersion={#MyAppVersion}
    echo AppPublisher={#MyAppPublisher}
    echo AppPublisherURL={#MyAppURL}
    echo AppSupportURL={#MyAppURL}
    echo AppUpdatesURL={#MyAppURL}
    echo DefaultDirName={autopf}\{#MyAppName}
    echo DefaultGroupName={#MyAppName}
    echo AllowNoIcons=yes
    echo LicenseFile=installer_resources\LICENSE.txt
    echo InfoBeforeFile=installer_resources\README_USUARIO.txt
    echo OutputDir=installer_output
    echo OutputBaseFilename=TradingBotPro_Setup_v1.0.0
    echo SetupIconFile=installer_resources\icon.ico
    echo Compression=lzma2/ultra64
    echo SolidCompression=yes
    echo WizardStyle=modern
    echo WizardImageFile=compiler:WizModernImage-IS.bmp
    echo WizardSmallImageFile=compiler:WizModernSmallImage-IS.bmp
    echo ArchitecturesInstallIn64BitMode=x64
    echo UninstallDisplayIcon={app}\{#MyAppExeName}
    echo.
    echo [Languages]
    echo Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"
    echo Name: "english"; MessagesFile: "compiler:Default.isl"
    echo.
    echo [Tasks]
    echo Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
    echo Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode
    echo.
    echo [Files]
    echo Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
    echo Source: "installer_resources\README_USUARIO.txt"; DestDir: "{app}"; Flags: ignoreversion
    echo Source: "installer_resources\LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion
    echo.
    echo [Icons]
    echo Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
    echo Name: "{group}\{cm:ProgramOnTheWeb,{#MyAppName}}"; Filename: "{#MyAppURL}"
    echo Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
    echo Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
    echo Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon
    echo.
    echo [Run]
    echo Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange^(MyAppName, '&', '&&'^)}}"; Flags: nowait postinstall skipifsilent
    echo.
    echo [Code]
    echo procedure InitializeWizard^(^);
    echo begin
    echo   WizardForm.WelcomeLabel1.Caption := '¡Bienvenido al Asistente de Instalación de Trading Bot Pro!';
    echo   WizardForm.WelcomeLabel2.Caption := 'Este asistente te guiará en la instalación de Trading Bot Pro en tu computadora.' + #13#10#13#10 + 'Se recomienda cerrar todas las demás aplicaciones antes de continuar.' + #13#10#13#10 + 'Haz clic en Siguiente para continuar.';
    echo end;
) > "installer_script.iss"

echo    ✅ Script de Inno Setup creado: installer_script.iss
echo.

echo [8/8] 📦 Verificando Inno Setup...
echo.

REM Verificar si Inno Setup está instalado
set "INNO_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"

if exist "%INNO_PATH%" (
    echo    ✅ Inno Setup encontrado
    echo    🔨 Compilando instalador...
    echo.
    
    "%INNO_PATH%" "installer_script.iss"
    
    if exist "installer_output\TradingBotPro_Setup_v1.0.0.exe" (
        echo.
        echo ╔════════════════════════════════════════════════════════════╗
        echo ║          ✅ INSTALADOR CREADO EXITOSAMENTE                ║
        echo ╚════════════════════════════════════════════════════════════╝
        echo.
        echo 📦 Archivos generados:
        echo.
        echo    1. Ejecutable portable:
        echo       📍 dist\TradingBotRemote.exe
        for %%A in ("dist\TradingBotRemote.exe") do echo       📏 Tamaño: %%~zA bytes
        echo.
        echo    2. Instalador profesional:
        echo       📍 installer_output\TradingBotPro_Setup_v1.0.0.exe
        for %%A in ("installer_output\TradingBotPro_Setup_v1.0.0.exe") do echo       📏 Tamaño: %%~zA bytes
        echo.
        echo ═══════════════════════════════════════════════════════════
        echo.
        echo 🎯 PRÓXIMOS PASOS:
        echo.
        echo    1. Prueba el instalador en una máquina limpia
        echo    2. Distribuye el instalador a tus usuarios
        echo    3. Asegúrate de que el backend esté en Easypanel
        echo.
        echo 📚 DOCUMENTACIÓN:
        echo    - README_USUARIO.txt incluido en el instalador
        echo    - LICENSE.txt incluido en el instalador
        echo.
        echo ═══════════════════════════════════════════════════════════
    ) else (
        echo.
        echo ❌ ERROR: No se pudo crear el instalador
        echo    Revisa los errores de Inno Setup arriba
    )
) else (
    echo    ⚠️ Inno Setup no encontrado
    echo.
    echo    Para crear el instalador profesional:
    echo.
    echo    1. Descarga Inno Setup desde:
    echo       https://jrsoftware.org/isdl.php
    echo.
    echo    2. Instala Inno Setup
    echo.
    echo    3. Ejecuta este script nuevamente
    echo.
    echo    O compila manualmente:
    echo       - Abre Inno Setup
    echo       - File → Open → installer_script.iss
    echo       - Build → Compile
    echo.
    echo ═══════════════════════════════════════════════════════════
    echo.
    echo ✅ Ejecutable portable creado en: dist\TradingBotRemote.exe
    echo    Puedes distribuir este archivo directamente.
    echo.
)

echo.
pause
