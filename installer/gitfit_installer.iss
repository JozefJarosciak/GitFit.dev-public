; GitFit.dev Installer Script for Inno Setup
; This creates a professional Windows installer for GitFit.dev

#define MyAppName "GitFit.dev"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "GitFit"
#define MyAppURL "https://github.com/JozefJarosciak/GitFit.dev-public"
#define MyAppExeName "GitFitDev.exe"
#define MyAppID "{{E3D7F8A1-2C4B-4D5E-9F1A-B2C3D4E5F6A7}"

[Setup]
; Application metadata
AppId={#MyAppID}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; Installation directories - auto selects based on privileges
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes

; Output settings
OutputDir=..\dist
OutputBaseFilename=GitFitDev-{#MyAppVersion}-Setup
SetupIconFile=..\assets\icon_win.ico
Compression=zip
SolidCompression=yes

; Windows version requirements
MinVersion=10.0
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

; Privileges - allow both admin and user installs
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

; Uninstall
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName}

; Additional settings
AllowNoIcons=yes
; LicenseFile=..\LICENSE
; InfoBeforeFile=..\README.md
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[CustomMessages]
SystemTrayInfo=IMPORTANT: GitFit.dev runs in the SYSTEM TRAY%nLook for the green dumbbell icon near your clock!

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
; Removed startup task - the app handles this internally through its Settings menu

[Files]
; Main executable
Source: "..\dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; Additional files if needed
Source: "..\README.md"; DestDir: "{app}"; Flags: ignoreversion
; Source: "..\LICENSE"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Start Menu icons
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"

; Desktop icon (if selected)
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Registry]
; Removed startup registry entry - the app handles this internally through its Settings menu

; Application registry entries - use auto root (HKLM for admin, HKCU for user)
Root: HKCU; Subkey: "Software\{#MyAppPublisher}"; Flags: uninsdeletekeyifempty
Root: HKCU; Subkey: "Software\{#MyAppPublisher}\{#MyAppName}"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\{#MyAppPublisher}\{#MyAppName}"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"
Root: HKCU; Subkey: "Software\{#MyAppPublisher}\{#MyAppName}"; ValueType: string; ValueName: "Version"; ValueData: "{#MyAppVersion}"

[Run]
; Option to run the application after installation - opens settings by default for first-time setup
Filename: "{app}\{#MyAppExeName}"; Parameters: "--show-settings"; Description: "Launch {#MyAppName} and open Settings (recommended for first-time setup)"; Flags: nowait postinstall skipifsilent

[UninstallRun]
; Kill the app if it's running during uninstall
Filename: "{cmd}"; Parameters: "/c taskkill /f /im GitFitDev.exe"; Flags: runhidden

[Code]

// Check if the application is running
function IsAppRunning(): Boolean;
var
  ResultCode: Integer;
begin
  Result := False;
  if Exec('cmd.exe', '/c tasklist /FI "IMAGENAME eq GitFitDev.exe" 2>NUL | find /I "GitFitDev.exe" >NUL', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
  begin
    Result := (ResultCode = 0);
  end;
end;

// Before installation begins
function PrepareToInstall(var NeedsRestart: Boolean): String;
var
  ResultCode: Integer;
begin
  Result := '';
  if IsAppRunning() then
  begin
    if MsgBox('GitFit.dev is currently running. The installer will close it to continue. Do you want to proceed?', mbConfirmation, MB_YESNO) = IDYES then
    begin
      Exec('cmd.exe', '/c taskkill /f /im GitFitDev.exe', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
      Sleep(1000); // Give it time to close
    end
    else
    begin
      Result := 'Installation cancelled - GitFit.dev is running.';
    end;
  end;
end;

// Custom messages
procedure CurPageChanged(CurPageID: Integer);
begin
  if CurPageID = wpWelcome then
  begin
    WizardForm.WelcomeLabel2.Caption :=
      'This will install GitFit.dev on your computer.' + #13#10 + #13#10 +
      'GitFit.dev helps you take regular exercise breaks with fullscreen reminders and fitness-focused messages.' + #13#10 + #13#10 +
      'The application will run in your system tray and remind you to move at configurable intervals.' + #13#10 + #13#10 +
      'Click Next to continue, or Cancel to exit Setup.';
  end;

  if CurPageID = wpFinished then
  begin
    WizardForm.FinishedLabel.Caption :=
      'Setup has finished installing {#MyAppName} on your computer.' + #13#10 + #13#10 +
      'IMPORTANT: The application runs minimized in your SYSTEM TRAY (near the clock).' + #13#10 +
      'Look for the green dumbbell icon in your system tray to access settings and features.' + #13#10 + #13#10 +
      'You can:' + #13#10 +
      '• Right-click the tray icon for quick actions' + #13#10 +
      '• Double-click the tray icon to open Settings' + #13#10 +
      '• Configure break intervals and exercise preferences' + #13#10 + #13#10 +
      'Select the option below to launch the application now.';
  end;
end;