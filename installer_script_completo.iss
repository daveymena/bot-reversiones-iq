; Script para Trading Bot Pro - Versión Completa

#define MyAppName "Trading Bot Pro - Completo"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Trading Bot Pro Team"
#define MyAppURL "https://github.com/tu-usuario/trading-bot"
#define MyAppExeName "TradingBotPro.exe"

[Setup]
AppId={{B2C3D4E5-F6G7-8901-BCDE-FG2345678901}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName=Trading Bot Pro
AllowNoIcons=yes
LicenseFile=installer_resources\LICENSE.txt
InfoBeforeFile=installer_resources\README_COMPLETO.txt
OutputDir=installer_output
OutputBaseFilename=TradingBotPro_Completo_Setup_v1.0.0
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
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "installer_resources\README_COMPLETO.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "installer_resources\LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Trading Bot Pro"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:ProgramOnTheWeb,{#MyAppName}}"; Filename: "{#MyAppURL}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Trading Bot Pro"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\Trading Bot Pro"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,Trading Bot Pro}"; Flags: nowait postinstall skipifsilent

[Code]
procedure InitializeWizard();
begin
  WizardForm.WelcomeLabel1.Caption := '¡Bienvenido a Trading Bot Pro - Versión Completa!';
  WizardForm.WelcomeLabel2.Caption := 'Esta versión incluye TODO el bot con IA ejecutándose localmente en tu PC.' + #13#10#13#10 + 'No requiere servidor externo.' + #13#10#13#10 + 'Haz clic en Siguiente para continuar.';
end;
