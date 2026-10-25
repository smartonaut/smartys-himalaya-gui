; Inno-Setup-Skript fuer die Windows-Fassung.
;
; Ergebnis: ein Installer, der sich wie ein normales Windows-Programm
; verhaelt — Startmenue-Eintrag, Eintrag in "Apps & Features", Deinstallation,
; Icon. Alles Noetige ist enthalten (Python steckt in der .exe, himalaya liegt
; daneben), der Nutzer muss nichts nachinstallieren.
;
; Bauen: iscc.exe /DPROJEKT=<pfad> packaging\windows-installer.iss

#ifndef PROJEKT
  #define PROJEKT ".."
#endif
#ifndef VERSION
  #define VERSION "0.1.0"
#endif

#define APPNAME "Smartys Himalaya GUI"
#define APPEXE "SmartysHimalayaGUI.exe"
#define HERSTELLER "Smartys"

[Setup]
AppId={{8F3A5C21-7D64-4E19-9B2A-4C5518E7A903}
AppName={#APPNAME}
AppVersion={#VERSION}
AppVerName={#APPNAME} {#VERSION}
AppPublisher={#HERSTELLER}
AppPublisherURL=https://github.com/smartonaut/smartys-himalaya-gui
AppSupportURL=https://github.com/smartonaut/smartys-himalaya-gui/issues
AppUpdatesURL=https://github.com/smartonaut/smartys-himalaya-gui/releases
DefaultDirName={autopf}\{#APPNAME}
DefaultGroupName={#APPNAME}
DisableProgramGroupPage=yes
; Keine Administratorrechte noetig: Installation nur fuer den angemeldeten
; Benutzer. So klappt es auch auf Rechnern ohne Admin-Kennwort.
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
OutputDir={#PROJEKT}\dist
OutputBaseFilename=SmartysHimalayaGUI-{#VERSION}-Setup
SetupIconFile={#PROJEKT}\assets\icons\smartys-himalaya-gui.ico
UninstallDisplayIcon={app}\{#APPEXE}
UninstallDisplayName={#APPNAME}
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
; Die App laeuft nur mit Edge WebView2 — unter Windows 10/11 vorinstalliert.
LicenseFile={#PROJEKT}\LICENSE
MinVersion=10.0

[Languages]
Name: "deutsch"; MessagesFile: "compiler:Languages\German.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Die Anwendung selbst — Python und alle Module stecken darin
Source: "{#PROJEKT}\dist\{#APPEXE}"; DestDir: "{app}"; Flags: ignoreversion
; himalaya mitliefern: sonst muesste jeder Nutzer erst ein Rust-Binary
; herunterladen und ablegen, bevor die App ein Konto findet.
Source: "{#PROJEKT}\build\windows\himalaya.exe"; DestDir: "{app}\himalaya"; Flags: ignoreversion
; Lizenz und Hinweise zum Nachlesen
Source: "{#PROJEKT}\LICENSE"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#PROJEKT}\README.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#APPNAME}"; Filename: "{app}\{#APPEXE}"; IconFilename: "{app}\{#APPEXE}"
Name: "{group}\{#APPNAME} deinstallieren"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#APPNAME}"; Filename: "{app}\{#APPEXE}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#APPEXE}"; Description: "{cm:LaunchProgram,{#APPNAME}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Der Programmordner geht restlos weg; Einstellungen und Postfach-Daten
; liegen in %APPDATA% und bleiben bewusst stehen — wer neu installiert,
; findet seine Konten wieder.
Type: filesandordirs; Name: "{app}"
