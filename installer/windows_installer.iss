[Setup]
AppName=AppUsageGUI
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
Name: "{group}\AppUsageGUI"; Filename: "{app}\App-${#MyAppVersion}.exe"
Name: "{commondesktop}\AppUsageGUI"; Filename: "{app}\App-${#MyAppVersion}.exe"
