; Inno Setup configuration file for Resume AI
; Download Inno Setup: https://jrsoftware.org/isdl.php

[Setup]
AppName=Resume AI
AppVersion=1.0
AppPublisher=Resume AI
AppURL=https://github.com/yourusername/resume-ai
DefaultDirName={pf}\Resume AI
DefaultGroupName=Resume AI
OutputDir=dist
OutputBaseFilename=ResumeAI-Setup-1.0
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin

; Uncomment to add a license
; LicenseFile=LICENSE.txt

; Icon for installer
SetupIconFile=resume-ai.ico

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1,1

[Files]
; Include the compiled executable and all dependencies
Source: "dist\ResumeAI\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Resume AI"; Filename: "{app}\ResumeAI.exe"; IconFilename: "{app}\resume-ai.ico"
Name: "{group}\{cm:UninstallProgram,Resume AI}"; Filename: "{uninstallexe}"
Name: "{commondesktop}\Resume AI"; Filename: "{app}\ResumeAI.exe"; IconFilename: "{app}\resume-ai.ico"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\Resume AI"; Filename: "{app}\ResumeAI.exe"; IconFilename: "{app}\resume-ai.ico"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\ResumeAI.exe"; Description: "{cm:LaunchProgram,Resume AI}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"
Type: filesandordirs; Name: "{localappdata}\Resume AI"

[Code]
procedure InitializeWizard;
begin
  { Optional: Add custom welcome message }
  WizardForm.WelcomeLabel2.Caption := 
    'This will install Resume AI and guide you through Ollama setup.' + #13#13 +
    'Resume AI uses AI models to enhance your resume.' + #13 +
    'All processing happens locally on your computer - your data never leaves your machine.';
end;
