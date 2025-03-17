[Setup]
AppName=App Usage GUI
AppVersion={#MyAppVersion}
DefaultDirName={autopf}\AppUsageGUI
DefaultGroupName=AppUsageGUI
OutputDir=release
OutputBaseFilename=AppUsageGUI-Setup-{#MyAppVersion}
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\App-${#MyAppVersion}.exe"; DestDir: "{app}"

[Icons]
Name: "{group}\App Usage GUI"; Filename: "{app}\App-${#MyAppVersion}.exe"
Name: "{commondesktop}\App Usage GUI"; Filename: "{app}\App-${#MyAppVersion}.exe"
