; CivicVerify_AI.iss
; Inno Setup script — compile this with the Inno Setup Compiler to produce
; CivicVerify_AI_Setup.exe.

#define MyAppName "CivicVerify AI"
#define MyAppVersion "1.0"
#define MyAppPublisher "CivicVerify AI"
#define MyAppExeName "launcher.pyw"

[Setup]
AppId={{B1F3C9A2-4D5E-4A8C-9F2B-CIVICVERIFY01}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={userpf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=installer_output
OutputBaseFilename=CivicVerify_AI_Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=lowest

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"

[Files]
Source: "dist\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\python\pythonw.exe"; Parameters: """{app}\{#MyAppExeName}"""; WorkingDir: "{app}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\python\pythonw.exe"; Parameters: """{app}\{#MyAppExeName}"""; WorkingDir: "{app}"; Tasks: desktopicon

[Run]
Filename: "{app}\python\pythonw.exe"; Parameters: """{app}\{#MyAppExeName}"""; WorkingDir: "{app}"; Description: "Launch {#MyAppName} now"; Flags: nowait postinstall skipifsilent