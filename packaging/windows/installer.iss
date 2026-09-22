#ifndef MyAppVersion
  #define MyAppVersion "0.1.0"
#endif
#ifndef MyAppSource
  #define MyAppSource "..\..\dist\Calculator-of-Knots-and-Links"
#endif
#ifndef MyOutputDir
  #define MyOutputDir "..\..\artifacts"
#endif

#define MyAppName "Calculator of Knots and Links"
#define MyAppExeName "Calculator-of-Knots-and-Links.exe"

[Setup]
AppId={{C1B32BDF-1A82-4DD1-8E53-0C1E8F0D3E62}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher=Calculator of Knots and Links contributors
AppPublisherURL=https://github.com/Dongqiyu829/Calculator-of-Knots-and-Links
AppSupportURL=https://github.com/Dongqiyu829/Calculator-of-Knots-and-Links/issues
DefaultDirName={localappdata}\Programs\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
OutputDir={#MyOutputDir}
OutputBaseFilename=Calculator-of-Knots-and-Links-Windows-x64-Setup
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
Uninstallable=yes
UninstallDisplayIcon={app}\{#MyAppExeName}
VersionInfoVersion={#MyAppVersion}
VersionInfoDescription={#MyAppName} Windows installer
VersionInfoProductName={#MyAppName}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: unchecked

[Files]
Source: "{#MyAppSource}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent
