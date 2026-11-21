; installer_setup.iss
; Script de Inno Setup para crear el instalador profesional de Windows
; Sistema de Registro Clinico v1.1.0
; Requiere Inno Setup 6+ (https://jrsoftware.org/isdl.php)

#define MyAppName      "Sistema de Registro Clinico"
#define MyAppVersion   "1.1.0"
#define MyAppPublisher "Sanrey Systems"
#define MyAppExeName   "SistemaClinico.exe"
#define MyAppURL       "https://github.com/sanrey393/registro_clinico"

[Setup]
AppId={{D8A14932-B8F7-4A63-9D27-5825D6E18B92}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}/releases
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
; Carpeta de salida del instalador
OutputDir=Output
OutputBaseFilename=Instalador_SistemaClinico_v1.1.0
; Compresion maxima
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
; No requiere permisos de administrador
PrivilegesRequired=lowest
; Minima version de Windows soportada (Windows 10)
MinVersion=10.0
; Arquitectura 64 bits
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checkedonce

[Files]
; --- Ejecutable y dependencias generadas por PyInstaller ---
Source: "dist\SistemaClinico\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; --- Archivo de configuracion de Firebase (cliente) ---
; IMPORTANTE: contiene tus claves API de Firebase. No compartir publicamente.
Source: ".env"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist

; --- Cuenta de servicio Firebase Admin SDK ---
; IMPORTANTE: archivo de credenciales privado. No compartir publicamente.
Source: "firebase_service_account.json"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist

; --- Archivo de version para el modulo de actualizacion automatica ---
Source: "version.json"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist

[Icons]
; Acceso directo en el menu Inicio
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
; Acceso directo en el escritorio (si el usuario lo eligio)
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
; Ofrece iniciar la aplicacion al terminar la instalacion
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Limpiar base de datos local al desinstalar (opcional - comentar si no se desea)
; Type: files; Name: "{app}\local_storage.db"
