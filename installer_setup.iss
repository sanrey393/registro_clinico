; Script de Inno Setup para crear el instalador profesional de Windows (.exe)
; Requiere Inno Setup (https://jrsoftware.org/isdl.php)

#define MyAppName "Sistema de Registro Clinico"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Tu Clinica / Psicologia"
#define MyAppExeName "SistemaClinico.exe"

[Setup]
AppId={{D8A14932-B8F7-4A63-9D27-5825D6E18B92}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=Output
OutputBaseFilename=Instalador_SistemaClinico_v1.0.0
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Copia todos los archivos generados por PyInstaller en dist\SistemaClinico
Source: "dist\SistemaClinico\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

