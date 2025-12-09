; Script de Inno Setup para Sistema de Turnos de Pádel
; Instalador con licencia trial automática de 15 días

#define MyAppName "Sistema de Turnos de Pádel"
#define MyAppVersion "1.0"
#define MyAppPublisher "Velazquez Adrian"
#define MyAppExeName "SistemaTurnosPadel.exe"
#define MyAppURL "https://github.com/Velazquezadrian"

[Setup]
; Información de la aplicación
AppId={{A8F3E5D9-C1B2-4E7F-8A3D-9C5E1B4A7F2D}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=yes
LicenseFile=
; Icono del instalador
SetupIconFile=icono_padel.ico
; Salida del instalador
OutputDir=installer
OutputBaseFilename=SistemaTurnosPadel_Setup_v{#MyAppVersion}
Compression=lzma
SolidCompression=yes
WizardStyle=modern
; Privilegios
PrivilegesRequired=lowest
; Arquitectura
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "Crear acceso directo en Inicio rápido"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Archivos del ejecutable
Source: "dist\SistemaTurnosPadel\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; Ícono
Source: "icono_padel.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "icono_padel.png"; DestDir: "{app}"; Flags: ignoreversion
; Script de inicio
Source: "INICIAR.bat"; DestDir: "{app}"; Flags: ignoreversion
; VBScript para inicio invisible
Source: "iniciar_invisible.vbs"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Acceso directo en el menú Inicio
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\icono_padel.ico"
; Acceso directo en el escritorio (opcional)
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\icono_padel.ico"; Tasks: desktopicon
; Acceso directo en inicio rápido
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\icono_padel.ico"; Tasks: quicklaunchicon

[Run]
; Ejecutar la aplicación al finalizar la instalación
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
var
  TrialInfoPage: TOutputMsgWizardPage;

procedure InitializeWizard;
begin
  // Página de información sobre el trial
  TrialInfoPage := CreateOutputMsgPage(wpWelcome,
    'Licencia Trial de 15 Días',
    'Prueba gratuita incluida',
    'Esta instalación incluye automáticamente una licencia de prueba de 15 días.' + #13#10#13#10 +
    'Características del Trial:' + #13#10 +
    '• Acceso completo a todas las funciones' + #13#10 +
    '• 15 días de uso sin restricciones' + #13#10 +
    '• No requiere tarjeta de crédito' + #13#10#13#10 +
    'Después del período de prueba:' + #13#10 +
    '• Puede activar una licencia completa ingresando un serial' + #13#10 +
    '• Vaya a Licencia > Ingresar serial' + #13#10 +
    '• Contacte al proveedor para obtener su licencia' + #13#10#13#10 +
    '¡Disfrute probando el sistema!');
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  
  // Mostrar mensaje adicional en la página de finalización
  if CurPageID = wpFinished then
  begin
    MsgBox('Su período de prueba de 15 días comienza ahora.' + #13#10#13#10 +
           'La aplicación se iniciará automáticamente y podrá empezar a usarla de inmediato.' + #13#10#13#10 +
           'Para gestionar su licencia, vaya a: Licencia (botón morado en el menú)',
           mbInformation, MB_OK);
  end;
end;

[Messages]
spanish.WelcomeLabel2=Esto instalará [name/ver] en su computadora.%n%nSe incluye una licencia de prueba GRATUITA de 15 días.%n%nSe recomienda que cierre todas las demás aplicaciones antes de continuar.
spanish.FinishedHeadingLabel=Completando el Asistente de Instalación de [name]
spanish.FinishedLabelNoIcons=La instalación de [name] ha terminado.%n%nSu período de prueba de 15 días comienza ahora.
spanish.FinishedLabel=La instalación de [name] ha terminado.%n%nSu período de prueba de 15 días comienza ahora. Puede iniciar la aplicación haciendo clic en los iconos creados.
