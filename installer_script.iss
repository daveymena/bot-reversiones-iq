; Script generado automáticamente para Trading Bot Pro
; Instalador profesional para Windows

#define MyAppName "Trading Bot Pro"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Trading Bot Pro Team"
#define MyAppURL "https://github.com/tu-usuario/trading-bot"
#define MyAppExeName "TradingBotRemote.exe"

[Setup]
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=installer_resources\LICENSE.txt
InfoBeforeFile=installer_resources\README_USUARIO.txt
OutputDir=installer_output
OutputBaseFilename=TradingBotPro_Setup_v1.0.0
SetupIconFile=installer_resources\icon.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
WizardImageFile=compiler:WizModernImage-IS.bmp
WizardSmallImageFile=compiler:WizModernSmallImage-IS.bmp
ArchitecturesInstallIn64BitMode=x64
UninstallDisplayIcon={app}\{#MyAppExeName}

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "installer_resources\README_USUARIO.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "installer_resources\LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:ProgramOnTheWeb,{#MyAppName}}"; Filename: "{#MyAppURL}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange^(MyAppName, '&', '&&'^)}}"; Flags: nowait postinstall skipifsilent

[Code]
procedure InitializeWizard();
begin
  WizardForm.WelcomeLabel1.Caption := '¡Bienvenido al Asistente de Instalación de Trading Bot Pro!';
  WizardForm.WelcomeLabel2.Caption := 'Este asistente te guiará en la instalación de Trading Bot Pro en tu computadora.' + #13#10#13#10 + 'Se recomienda cerrar todas las demás aplicaciones antes de continuar.' + #13#10#13#10 + 'Haz clic en Siguiente para continuar.';
end;
