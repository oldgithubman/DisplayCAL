; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{4714199A-0D66-4E69-97FF-7B54BFF80B88}
AppName=dispcalGUI
AppVerName=dispcalGUI %(AppVerName)s
AppPublisherURL=http://dispcalGUI.hoech.net
AppSupportURL=http://dispcalGUI.hoech.net
AppUpdatesURL=http://dispcalGUI.hoech.net
DefaultDirName={pf}\dispcalGUI
DefaultGroupName=dispcalGUI
LicenseFile=..\LICENSE.txt
OutputDir=.
OutputBaseFilename=dispcalGUI-%(AppVersion)s-Setup
SetupIconFile=..\dispcalGUI\theme\icons\dispcalGUI.ico
Compression=lzma
SolidCompression=true
VersionInfoVersion=%(VersionInfoVersion)s
VersionInfoDescription=dispcalGUI Setup
VersionInfoTextVersion=%(VersionInfoTextVersion)s
WizardImageFile=..\misc\media\install.bmp
WizardSmallImageFile=..\misc\media\icon-install.bmp
AppVersion=%(AppVersion)s
UninstallDisplayIcon={app}\dispcalGUI.exe
AlwaysShowComponentsList=false

[Languages]
Name: english; MessagesFile: compiler:Default.isl
Name: german; MessagesFile: compiler:Languages\German.isl
Name: italian; MessagesFile: compiler:Languages\Italian.isl
Name: spanish; MessagesFile: compiler:Languages\Spanish.isl

[Tasks]
Name: desktopicon; Description: {cm:CreateDesktopIcon}; GroupDescription: {cm:AdditionalIcons}; Flags: unchecked
Name: quicklaunchicon; Description: {cm:CreateQuickLaunchIcon}; GroupDescription: {cm:AdditionalIcons}; Flags: unchecked

[Files]
Source: pyi.win32-onedir\dispcalGUI-%(AppVersion)s\*; DestDir: {app}; Flags: ignoreversion recursesubdirs
Source: pyi.win32-onedir\dispcalGUI-%(AppVersion)s\README.html; DestDir: {app}; Flags: ignoreversion isreadme
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: {group}\dispcalGUI; Filename: {app}\dispcalGUI.exe
Name: {group}\{cm:UninstallProgram,dispcalGUI}; Filename: {uninstallexe}; IconFilename: {app}\theme\icons\dispcalGUI-uninstall.ico; Tasks: ; Languages: 
Name: {commondesktop}\dispcalGUI; Filename: {app}\dispcalGUI.exe; Tasks: desktopicon
Name: {userappdata}\Microsoft\Internet Explorer\Quick Launch\dispcalGUI; Filename: {app}\dispcalGUI.exe; Tasks: quicklaunchicon
Name: {group}\LICENSE; Filename: {app}\LICENSE.txt
Name: {group}\README; Filename: {app}\README.html; Tasks: ; Languages: 

[Run]
Filename: {app}\dispcalGUI.exe; Description: {cm:LaunchProgram,dispcalGUI}; Flags: nowait postinstall skipifsilent
