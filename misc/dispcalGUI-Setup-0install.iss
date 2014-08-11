; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

#include ReadReg(HKEY_LOCAL_MACHINE,'Software\Sherlock Software\InnoTools\Downloader','ScriptPath','')

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppID={{4714199A-0D66-4E69-97FF-7B54BFF80B88}
AppCopyright=%(AppCopyright)s
AppName=dispcalGUI
AppVerName=dispcalGUI %(AppVerName)s
AppPublisher=%(AppPublisher)s
AppPublisherURL=%(AppPublisherURL)s
AppReadmeFile=%(URL)s
AppSupportURL=%(AppSupportURL)s
AppUpdatesURL=%(AppUpdatesURL)s
DefaultDirName={pf}\dispcalGUI
DefaultGroupName=dispcalGUI
LicenseFile=..\LICENSE.txt
OutputDir=.
OutputBaseFilename=dispcalGUI-0install-Setup
SetupIconFile=..\dispcalGUI\theme\icons\dispcalGUI.ico
Compression=lzma/Max
SolidCompression=true
VersionInfoVersion=%(VersionInfoVersion)s
VersionInfoDescription=dispcalGUI Setup
VersionInfoTextVersion=%(VersionInfoTextVersion)s
WizardImageFile=..\misc\media\install.bmp
WizardSmallImageFile=..\misc\media\icon-install.bmp
AppVersion=%(AppVersion)s
UninstallDisplayName={cm:UninstallProgram,dispcalGUI}
UninstallDisplayIcon={app}\dispcalGUI-uninstall.ico
AlwaysShowComponentsList=false
ShowLanguageDialog=auto
MinVersion=0,5.1.2600
DisableDirPage=yes
UsePreviousGroup=False
DisableProgramGroupPage=yes

[Languages]
Name: english; MessagesFile: ..\misc\InnoSetup\v5\Default.isl;
Name: french; MessagesFile: ..\misc\InnoSetup\v5\Languages\French.isl;
Name: german; MessagesFile: ..\misc\InnoSetup\v5\Languages\German.isl;
Name: italian; MessagesFile: ..\misc\InnoSetup\v5\Languages\Italian.isl;
Name: spanish; MessagesFile: ..\misc\InnoSetup\v5\Languages\Spanish.isl;

[Tasks]
Name: calibrationloadinghandledbydispcalgui; Description: {cm:CalibrationLoadingHandledByDispcalGUI}; Flags: exclusive; GroupDescription: {cm:CalibrationLoading};
Name: calibrationloadinghandledbyos; Description: {cm:CalibrationLoadingHandledByOS}; Flags: exclusive unchecked; GroupDescription: {cm:CalibrationLoading}; MinVersion: 0,6.1.7600;

[Files]
Source: ..\dispcalGUI\theme\icons\dispcalGUI-uninstall.ico; DestDir: {app};
Source: SetACL.exe; DestDir: {tmp}; Flags: deleteafterinstall overwritereadonly;

[Icons]
Name: {group}\dispcalGUI; Filename: {reg:HKCU\Software\Zero Install,InstallLocation|{reg:HKLM\Software\Zero Install,InstallLocation}}\0install-win.exe; Parameters: "run --no-wait %(URL)s0install/dispcalGUI.xml";
Name: {group}\{cm:SelectVersion}; Filename: {reg:HKCU\Software\Zero Install,InstallLocation|{reg:HKLM\Software\Zero Install,InstallLocation}}\0install-win.exe; Parameters: "run --gui --no-wait %(URL)s0install/dispcalGUI.xml";
Name: {group}\{cm:ChangeIntegration}; Filename: {reg:HKCU\Software\Zero Install,InstallLocation|{reg:HKLM\Software\Zero Install,InstallLocation}}\0install-win.exe; Parameters: "integrate %(URL)s0install/dispcalGUI.xml";
Name: {group}\{cm:UninstallProgram,dispcalGUI}; Filename: {uninstallexe}; IconFilename: {app}\dispcalGUI-uninstall.ico;
Name: {group}\LICENSE; Filename: %(URL)sLICENSE.txt;
Name: {group}\README; Filename: %(URL)s;
Name: {commonstartup}\dispcalGUI Profile Loader; Filename: {reg:HKCU\Software\Zero Install,InstallLocation|{reg:HKLM\Software\Zero Install,InstallLocation}}\0install-win.exe; Parameters: "run --batch --no-wait --offline --command=run-apply-profiles %(URL)s0install/dispcalGUI.xml"; Tasks: calibrationloadinghandledbydispcalgui;

[Run]
Filename: {reg:HKCU\Software\Zero Install,InstallLocation|{reg:HKLM\Software\Zero Install,InstallLocation}}\0install-win.exe; Parameters: "integrate --refresh %(URL)s0install/dispcalGUI.xml"; Description: {cm:LaunchProgram,dispcalGUI}; Flags: runasoriginaluser
Filename: %(URL)s; Description: {code:Get_RunEntryShellExec_Message|README}; Flags: nowait postinstall shellexec skipifsilent;
Filename: {reg:HKCU\Software\Zero Install,InstallLocation|{reg:HKLM\Software\Zero Install,InstallLocation}}\0install-win.exe; Parameters: "run --not-before=%(AppVersion)s %(URL)s0install/dispcalGUI.xml"; Description: {cm:LaunchProgram,dispcalGUI}; Flags: nowait postinstall skipifsilent
Filename: {tmp}\SetACL.exe; Parameters: "-on {commonappdata}\dispcalGUI -ot file -actn ace -ace ""n:S-1-5-32-545;p:read_ex;s:y;i:sc,so;m:set;w:dacl"""; Flags: RunHidden;
Filename: {tmp}\SetACL.exe; Parameters: "-on {commonappdata}\dispcalGUI -ot file -actn ace -ace ""n:S-1-5-32-545;p:write;s:y;i:io,sc,so;m:grant;w:dacl"""; Flags: RunHidden;
Filename: {reg:HKCU\Software\Zero Install,InstallLocation|{reg:HKLM\Software\Zero Install,InstallLocation}}\0install-win.exe; Parameters: "run --batch --not-before=%(AppVersion)s --command=set-calibration-loading %(URL)s0install/dispcalGUI.xml"; Description: {cm:LaunchProgram,dispcalGUI}; Flags: RunAsCurrentUser; Tasks: calibrationloadinghandledbydispcalgui;
Filename: {reg:HKCU\Software\Zero Install,InstallLocation|{reg:HKLM\Software\Zero Install,InstallLocation}}\0install-win.exe; Parameters: "run --batch --not-before=%(AppVersion)s --command=set-calibration-loading -- %(URL)s0install/dispcalGUI.xml --os"; Description: {cm:LaunchProgram,dispcalGUI}; Flags: RunAsCurrentUser; Tasks: calibrationloadinghandledbyos;

[Dirs]
Name: {commonappdata}\dispcalGUI; Permissions: users-modify;

[Code]
function Get_RunEntryShellExec_Message(Value: string): string;
begin
	Result := FmtMessage(SetupMessage(msgRunEntryShellExec), [Value]);
end;

function Get_UninstallString(AppId: string): string;
var
	UninstallString: string;
begin
	if not RegQueryStringValue(HKLM, 'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\' + AppId + '_is1', 'UninstallString', UninstallString) and
		not RegQueryStringValue(HKLM, 'SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\' + AppId + '_is1', 'UninstallString', UninstallString) and
			not RegQueryStringValue(HKCU, 'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\' + AppId + '_is1', 'UninstallString', UninstallString) then
				RegQueryStringValue(HKCU, 'SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\' + AppId + '_is1', 'UninstallString', UninstallString);
	Result := RemoveQuotes(UninstallString);
end;

function Get_ZeroInstall_InstallLocation: string;
begin
	if not RegQueryStringValue(HKLM, 'SOFTWARE\Zero Install', 'InstallLocation', Result) then
		RegQueryStringValue(HKCU, 'SOFTWARE\Zero Install', 'InstallLocation', Result);
end;

function Get_ZeroInstall_Exe: string;
begin
	Result := Get_ZeroInstall_InstallLocation() + '\0install-win.exe';
end;

function ZeroInstall_IsInstalled: boolean;
var
	ExePath: string;
begin
	ExePath := Get_ZeroInstall_Exe();
	Result := (ExePath <> '') and FileExists(ExePath);
end;

procedure InitializeWizard();
begin
	if not ZeroInstall_IsInstalled() then begin
		ITD_Init;
		ITD_AddFile('http://0install.de/files/zero-install.exe', ExpandConstant('{tmp}\zero-install.exe'));
		ITD_DownloadAfter(wpReady);
	end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
	ErrorCode: integer;
	ZeroInstall: string;
	UninstallString: string;
begin
	if CurStep=ssInstall then begin
		if not ZeroInstall_IsInstalled() then begin
			if not Exec(ExpandConstant('{tmp}\zero-install.exe'), '/SP- /SILENT /NORESTART', '', SW_SHOW, ewWaitUntilTerminated, ErrorCode) then
				SuppressibleMsgBox(SysErrorMessage(ErrorCode), mbCriticalError, MB_OK, MB_OK);
			if not ZeroInstall_IsInstalled() then
				Abort();
		end;
		UninstallString := Get_UninstallString(ExpandConstant('{#emit SetupSetting("AppId")}'));
		if UninstallString <> '' then begin
			if not Exec(UninstallString, '/VERYSILENT /NORESTART /SUPPRESSMSGBOXES', '', SW_SHOW, ewWaitUntilTerminated, ErrorCode) then
				SuppressibleMsgBox(SysErrorMessage(ErrorCode), mbError, MB_OK, MB_OK);
		end;
	end;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
	ErrorCode: integer;
	ZeroInstall: string;
	UninstallString: string;
begin
	if CurUninstallStep=usUninstall then begin
		if ZeroInstall_IsInstalled() then begin
			ZeroInstall := Get_ZeroInstall_Exe();
			if not Exec(ZeroInstall, 'remove --batch %(URL)s0install/dispcalGUI.xml', '', SW_SHOW, ewWaitUntilTerminated, ErrorCode) then
				SuppressibleMsgBox(SysErrorMessage(ErrorCode), mbError, MB_OK, MB_OK);
		end;
	end;
	if CurUninstallStep=usDone then begin
		if ZeroInstall_IsInstalled() then begin
			UninstallString := Get_ZeroInstall_InstallLocation() + '\unins000.exe';
			if (UninstallString <> '') and (SuppressibleMsgBox(FmtMessage(CustomMessage('AskRemove'), ['Zero Install']), mbConfirmation, MB_YESNO, IDNO) = IDYES) then
				Exec(UninstallString, '', '', SW_SHOW, ewNoWait, ErrorCode);
		end;
	end;
end;
