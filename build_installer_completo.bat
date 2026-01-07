@echo off
chcp 65001 >nul
echo ╔════════════════════════════════════════════════════════════╗
echo ║     TRADING BOT PRO - INSTALADOR COMPLETO (LOCAL)         ║
echo ║     Bot con IA que ejecuta TODO localmente                ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Verificar que estamos en el directorio correcto
if not exist "main_modern.py" (
    echo ❌ Error: No se encuentra main_modern.py
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
echo [2/8] 🎨 Verificando recursos visuales...
echo.

REM Usar los mismos recursos que el remoto
if not exist "installer_resources\icon.ico" (
    echo    ❌ Error: Ejecuta primero build_installer.bat para crear recursos
    pause
    exit /b 1
) else (
    echo    ✅ Recursos existentes
)

echo.
echo [3/8] 📄 Creando documentación para versión completa...
echo.

REM Crear README específico para versión completa
(
    echo ╔════════════════════════════════════════════════════════════╗
    echo ║           TRADING BOT PRO - VERSIÓN COMPLETA              ║
    echo ╚════════════════════════════════════════════════════════════╝
    echo.
    echo ¡Gracias por instalar Trading Bot Pro - Versión Completa!
    echo.
    echo Esta versión incluye TODO el bot ejecutándose localmente:
    echo - ✅ Reinforcement Learning ^(PPO^)
    echo - ✅ Análisis con IA ^(Groq/Ollama^)
    echo - ✅ 6 Mejoras de Rentabilidad
    echo - ✅ Gestión de Riesgo Avanzada
    echo - ✅ Aprendizaje Continuo
    echo - ✅ Interfaz Gráfica Moderna
    echo.
    echo 🚀 INICIO RÁPIDO:
    echo.
    echo 1. Ejecuta "Trading Bot Pro" desde el menú inicio
    echo 2. Selecciona tu broker ^(Exnova recomendado^)
    echo 3. Ingresa tus credenciales
    echo 4. Haz clic en "CONECTAR"
    echo 5. Entrena el modelo ^(pestaña Entrenamiento^)
    echo 6. ¡Inicia el bot!
    echo.
    echo ⚠️ IMPORTANTE:
    echo.
    echo - Usa SIEMPRE la cuenta PRACTICE primero
    echo - Entrena el modelo antes de operar
    echo - Mantén tus credenciales seguras
    echo - El bot ejecuta TODO en tu PC ^(no requiere servidor^)
    echo.
    echo 📚 CARACTERÍSTICAS:
    echo.
    echo ✨ Reinforcement Learning
    echo    El bot aprende de cada operación usando PPO
    echo.
    echo ✨ Análisis con IA
    echo    Groq/Ollama validan cada decisión
    echo.
    echo ✨ 6 Mejoras de Rentabilidad
    echo    - Cooldown por activo
    echo    - Detección de resistencias
    echo    - Confirmación de reversión
    echo    - Análisis de momentum
    echo    - Filtros de rentabilidad
    echo    - Verificación de volatilidad
    echo.
    echo ✨ Gestión de Riesgo
    echo    Stop Loss, Take Profit, Martingala inteligente
    echo.
    echo ═══════════════════════════════════════════════════════════
    echo Trading Bot Pro v1.0 - Versión Completa
    echo ═══════════════════════════════════════════════════════════
) > "installer_resources\README_COMPLETO.txt"
echo    ✅ README_COMPLETO.txt creado

echo.
echo [4/8] 🧹 Limpiando builds anteriores...
echo.

if exist "build" (
    rmdir /s /q "build"
    echo    ✅ Carpeta build eliminada
)

if exist "dist\TradingBotPro.exe" (
    del /q "dist\TradingBotPro.exe"
    echo    ✅ Ejecutable anterior eliminado
)

echo.
echo [5/8] 🔨 Compilando ejecutable COMPLETO...
echo    (Esto puede tardar 5-10 minutos - incluye RL, LLM, etc.)
echo.

python -m PyInstaller --noconfirm ^
    --onefile ^
    --windowed ^
    --name="TradingBotPro" ^
    --icon="installer_resources\icon.ico" ^
    --add-data "gui;gui" ^
    --add-data "core;core" ^
    --add-data "strategies;strategies" ^
    --add-data "ai;ai" ^
    --add-data "data;data" ^
    --add-data "models;models" ^
    --add-data "exnovaapi;exnovaapi" ^
    --add-data "installer_resources\README_COMPLETO.txt;." ^
    --hidden-import="PySide6.QtCore" ^
    --hidden-import="PySide6.QtGui" ^
    --hidden-import="PySide6.QtWidgets" ^
    --hidden-import="PySide6.QtNetwork" ^
    --hidden-import="pyqtgraph" ^
    --hidden-import="pyqtgraph.graphicsItems" ^
    --hidden-import="pyqtgraph.exporters" ^
    --hidden-import="stable_baselines3" ^
    --hidden-import="stable_baselines3.ppo" ^
    --hidden-import="gymnasium" ^
    --hidden-import="gymnasium.spaces" ^
    --hidden-import="groq" ^
    --hidden-import="ta" ^
    --hidden-import="pandas" ^
    --hidden-import="numpy" ^
    --hidden-import="websocket" ^
    --hidden-import="websocket._app" ^
    --exclude-module="matplotlib" ^
    --exclude-module="scipy" ^
    --exclude-module="tensorflow" ^
    --exclude-module="torch" ^
    --exclude-module="pygame" ^
    --exclude-module="cv2" ^
    --exclude-module="PIL" ^
    --exclude-module="pytest" ^
    --exclude-module="IPython" ^
    --exclude-module="notebook" ^
    main_modern.py

if not exist "dist\TradingBotPro.exe" (
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
for %%A in ("dist\TradingBotPro.exe") do (
    echo    📦 Nombre: %%~nxA
    echo    📏 Tamaño: %%~zA bytes ^(~%%~zA / 1048576 MB^)
    echo    📍 Ubicación: %%~fA
)

echo.
echo [7/8] 📝 Creando script de Inno Setup...
echo.

REM Crear script de Inno Setup para versión completa
(
    echo ; Script para Trading Bot Pro - Versión Completa
    echo.
    echo #define MyAppName "Trading Bot Pro - Completo"
    echo #define MyAppVersion "1.0.0"
    echo #define MyAppPublisher "Trading Bot Pro Team"
    echo #define MyAppURL "https://github.com/tu-usuario/trading-bot"
    echo #define MyAppExeName "TradingBotPro.exe"
    echo.
    echo [Setup]
    echo AppId={{B2C3D4E5-F6G7-8901-BCDE-FG2345678901}
    echo AppName={#MyAppName}
    echo AppVersion={#MyAppVersion}
    echo AppPublisher={#MyAppPublisher}
    echo AppPublisherURL={#MyAppURL}
    echo AppSupportURL={#MyAppURL}
    echo AppUpdatesURL={#MyAppURL}
    echo DefaultDirName={autopf}\{#MyAppName}
    echo DefaultGroupName=Trading Bot Pro
    echo AllowNoIcons=yes
    echo LicenseFile=installer_resources\LICENSE.txt
    echo InfoBeforeFile=installer_resources\README_COMPLETO.txt
    echo OutputDir=installer_output
    echo OutputBaseFilename=TradingBotPro_Completo_Setup_v1.0.0
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
    echo Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"
    echo Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode
    echo.
    echo [Files]
    echo Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
    echo Source: "installer_resources\README_COMPLETO.txt"; DestDir: "{app}"; Flags: ignoreversion
    echo Source: "installer_resources\LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion
    echo.
    echo [Icons]
    echo Name: "{group}\Trading Bot Pro"; Filename: "{app}\{#MyAppExeName}"
    echo Name: "{group}\{cm:ProgramOnTheWeb,{#MyAppName}}"; Filename: "{#MyAppURL}"
    echo Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
    echo Name: "{autodesktop}\Trading Bot Pro"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
    echo Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\Trading Bot Pro"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon
    echo.
    echo [Run]
    echo Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,Trading Bot Pro}"; Flags: nowait postinstall skipifsilent
    echo.
    echo [Code]
    echo procedure InitializeWizard^(^);
    echo begin
    echo   WizardForm.WelcomeLabel1.Caption := '¡Bienvenido a Trading Bot Pro - Versión Completa!';
    echo   WizardForm.WelcomeLabel2.Caption := 'Esta versión incluye TODO el bot con IA ejecutándose localmente en tu PC.' + #13#10#13#10 + 'No requiere servidor externo.' + #13#10#13#10 + 'Haz clic en Siguiente para continuar.';
    echo end;
) > "installer_script_completo.iss"

echo    ✅ Script de Inno Setup creado: installer_script_completo.iss
echo.

echo [8/8] 📦 Verificando Inno Setup...
echo.

REM Verificar si Inno Setup está instalado
set "INNO_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"

if exist "%INNO_PATH%" (
    echo    ✅ Inno Setup encontrado
    echo    🔨 Compilando instalador...
    echo.
    
    "%INNO_PATH%" "installer_script_completo.iss"
    
    if exist "installer_output\TradingBotPro_Completo_Setup_v1.0.0.exe" (
        echo.
        echo ╔════════════════════════════════════════════════════════════╗
        echo ║       ✅ INSTALADOR COMPLETO CREADO EXITOSAMENTE          ║
        echo ╚════════════════════════════════════════════════════════════╝
        echo.
        echo 📦 Archivos generados:
        echo.
        echo    1. Ejecutable portable:
        echo       📍 dist\TradingBotPro.exe
        for %%A in ("dist\TradingBotPro.exe") do echo       📏 Tamaño: %%~zA bytes
        echo.
        echo    2. Instalador profesional:
        echo       📍 installer_output\TradingBotPro_Completo_Setup_v1.0.0.exe
        for %%A in ("installer_output\TradingBotPro_Completo_Setup_v1.0.0.exe") do echo       📏 Tamaño: %%~zA bytes
        echo.
        echo ═══════════════════════════════════════════════════════════
        echo.
        echo 🎯 VERSIÓN COMPLETA:
        echo    - Incluye RL, LLM, análisis avanzado
        echo    - Ejecuta TODO localmente
        echo    - No requiere servidor
        echo    - Más pesado pero autónomo
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
    echo    1. Descarga Inno Setup: https://jrsoftware.org/isdl.php
    echo    2. Instala Inno Setup
    echo    3. Ejecuta este script nuevamente
    echo.
    echo ═══════════════════════════════════════════════════════════
    echo.
    echo ✅ Ejecutable portable creado en: dist\TradingBotPro.exe
    echo    Puedes distribuir este archivo directamente.
    echo.
)

echo.
pause
