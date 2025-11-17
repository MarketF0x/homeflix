; =====================================================
; HOMEFLIX - SCRIPT D'INSTALLATION INNOSETUP
; =====================================================
; Installateur Windows professionnel avec :
; - Choix de langue (FR/EN/ES)
; - Détection automatique des dépendances
; - Installation de Python, Node.js, FFmpeg
; - Configuration automatique
; - Création de raccourcis
; =====================================================

#define MyAppName "HomeFlix"
#define MyAppVersion ReadIni(SourcePath + "\version.ini", "Version", "Number", "1.0.0")
#define MyAppPublisher "HomeFlix Team"
#define MyAppURL "https://github.com/homeflix"
#define MyAppExeName "homeflix.exe"

[Setup]
; Informations de base
AppId={{8D5F4A1C-3B2E-4F9A-A1C3-9E8D7F6A5B4C}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; Répertoire d'installation par défaut
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}

; Fichiers de sortie
OutputDir=output
OutputBaseFilename=HomeFlix-Setup-{#MyAppVersion}
SetupIconFile=..\generate_icon.py
Compression=lzma2/max
SolidCompression=yes

; Interface
WizardStyle=modern
DisableWelcomePage=no
LicenseFile=..\LICENSE
InfoBeforeFile=README_INSTALL.txt

; Privilèges
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog

; Langues
ShowLanguageDialog=yes

; Désinstallation
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName}

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\French.isl"; LicenseFile: "locales\LICENSE.fr.txt"; InfoBeforeFile: "locales\README.fr.txt"
Name: "english"; MessagesFile: "compiler:Default.isl"; LicenseFile: "locales\LICENSE.en.txt"; InfoBeforeFile: "locales\README.en.txt"
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"; LicenseFile: "locales\LICENSE.es.txt"; InfoBeforeFile: "locales\README.es.txt"

[Types]
Name: "full"; Description: {cm:FullInstallation}
Name: "minimal"; Description: {cm:MinimalInstallation}
Name: "custom"; Description: {cm:CustomInstallation}; Flags: iscustom

[Components]
Name: "core"; Description: {cm:CoreApp}; Types: full minimal custom; Flags: fixed
Name: "python"; Description: "Python 3.10+"; Types: full
Name: "nodejs"; Description: "Node.js 18+"; Types: full
Name: "ffmpeg"; Description: "FFmpeg"; Types: full custom
Name: "service"; Description: {cm:WindowsService}; Types: full

[Files]
; Application principale
Source: "..\server\*"; DestDir: "{app}\server"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: core
Source: "..\client\dist\*"; DestDir: "{app}\client\dist"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: core
Source: "..\settings.yaml"; DestDir: "{app}"; Flags: ignoreversion; Components: core
Source: "..\README.md"; DestDir: "{app}"; Flags: ignoreversion; Components: core
Source: "..\README_APP.md"; DestDir: "{app}"; Flags: ignoreversion; Components: core
Source: "..\ELECTRON_SETUP.md"; DestDir: "{app}"; Flags: ignoreversion; Components: core

; Application Electron
Source: "..\electron\*"; DestDir: "{app}\electron"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: core
Source: "..\electron\icon.png"; DestDir: "{app}\electron"; Flags: ignoreversion; Components: core

; Scripts d'installation
Source: "detect-environment.ps1"; DestDir: "{app}\installer"; Flags: ignoreversion; Components: core
Source: "install-dependencies.ps1"; DestDir: "{app}\installer"; Flags: ignoreversion; Components: core
Source: "configure-system.ps1"; DestDir: "{app}\installer"; Flags: ignoreversion; Components: core

; Fichiers de traduction
Source: "locales\*.json"; DestDir: "{app}\locales"; Flags: ignoreversion; Components: core

; Scripts de lancement
Source: "..\start-homeflix-app.ps1"; DestDir: "{app}"; Flags: ignoreversion; Components: core
Source: "..\homeflix.ps1"; DestDir: "{app}"; Flags: ignoreversion; Components: core
Source: "..\test-electron-setup.ps1"; DestDir: "{app}"; Flags: ignoreversion; Components: core

; Installateurs des dépendances (si non détectés)
Source: "downloads\python-3.10.*-amd64.exe"; DestDir: "{tmp}"; Flags: external skipifsourcedoesntexist deleteafterinstall; Components: python; Check: NeedsPython
Source: "downloads\node-v18.*-x64.msi"; DestDir: "{tmp}"; Flags: external skipifsourcedoesntexist deleteafterinstall; Components: nodejs; Check: NeedsNodeJS
Source: "downloads\ffmpeg-*.zip"; DestDir: "{tmp}"; Flags: external skipifsourcedoesntexist deleteafterinstall; Components: ffmpeg; Check: NeedsFFmpeg

[Dirs]
Name: "{app}\data"; Permissions: users-full
Name: "{app}\data\posters"; Permissions: users-full
Name: "{app}\data\thumbs"; Permissions: users-full
Name: "{app}\cache"; Permissions: users-full
Name: "{commonappdata}\HomeFlix"; Permissions: users-full
Name: "{userappdata}\HomeFlix"; Permissions: users-full

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "powershell.exe"; Parameters: "-ExecutionPolicy Bypass -File ""{app}\start-homeflix-app.ps1"""; IconFilename: "{app}\electron\icon.png"; WorkingDir: "{app}"; Comment: "Lancer Homeflix (Application native)"
Name: "{group}\{#MyAppName} Web"; Filename: "powershell.exe"; Parameters: "-ExecutionPolicy Bypass -File ""{app}\homeflix.ps1"""; WorkingDir: "{app}"; Comment: "Lancer Homeflix (Navigateur web)"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "powershell.exe"; Parameters: "-ExecutionPolicy Bypass -File ""{app}\start-homeflix-app.ps1"""; IconFilename: "{app}\electron\icon.png"; WorkingDir: "{app}"; Tasks: desktopicon; Comment: "Homeflix - Streaming vidéo personnel"

[Tasks]
Name: "desktopicon"; Description: {cm:CreateDesktopIcon}; GroupDescription: {cm:AdditionalIcons}
Name: "quicklaunchicon"; Description: {cm:CreateQuickLaunchIcon}; GroupDescription: {cm:AdditionalIcons}; Flags: unchecked
Name: "startupicon"; Description: {cm:LaunchAtStartup}; GroupDescription: {cm:AdditionalOptions}; Flags: unchecked
Name: "firewall"; Description: {cm:ConfigureFirewall}; GroupDescription: {cm:AdditionalOptions}; Flags: unchecked

[Run]
; Détection de l'environnement
Filename: "powershell.exe"; Parameters: "-ExecutionPolicy Bypass -File ""{app}\installer\detect-environment.ps1"" -Json"; StatusMsg: {cm:DetectingEnvironment}; Flags: runhidden

; Installation Python si nécessaire
Filename: "{tmp}\python-3.10.*-amd64.exe"; Parameters: "/quiet InstallAllUsers=1 PrependPath=1"; StatusMsg: {cm:InstallingPython}; Flags: waituntilterminated; Components: python; Check: NeedsPython

; Installation Node.js si nécessaire
Filename: "msiexec.exe"; Parameters: "/i ""{tmp}\node-v18.*-x64.msi"" /quiet /norestart"; StatusMsg: {cm:InstallingNodeJS}; Flags: waituntilterminated; Components: nodejs; Check: NeedsNodeJS

; Installation FFmpeg si nécessaire
Filename: "powershell.exe"; Parameters: "-ExecutionPolicy Bypass -File ""{app}\installer\install-ffmpeg.ps1"""; StatusMsg: {cm:InstallingFFmpeg}; Flags: runhidden waituntilterminated; Components: ffmpeg; Check: NeedsFFmpeg

; Installation des dépendances Python/Node
Filename: "powershell.exe"; Parameters: "-ExecutionPolicy Bypass -File ""{app}\installer\install-dependencies.ps1"""; StatusMsg: {cm:InstallingDependencies}; Flags: runhidden waituntilterminated

; Installation dépendances Electron
Filename: "powershell.exe"; Parameters: "-ExecutionPolicy Bypass -Command ""cd '{app}\electron'; npm install"""; StatusMsg: "Installation de l'application Electron..."; Flags: runhidden waituntilterminated

; Création de l'icône Electron
Filename: "powershell.exe"; Parameters: "-ExecutionPolicy Bypass -Command ""cd '{app}'; python create_electron_icon.py"""; StatusMsg: "Génération de l'icône..."; Flags: runhidden

; Configuration du système (pare-feu, base de données, etc.)
Filename: "powershell.exe"; Parameters: "-ExecutionPolicy Bypass -File ""{app}\installer\configure-system.ps1"" -Lang {language}"; StatusMsg: {cm:ConfiguringSystem}; Flags: runhidden waituntilterminated

; Proposition de lancer l'application
Filename: "powershell.exe"; Parameters: "-ExecutionPolicy Bypass -File ""{app}\start-homeflix-app.ps1"""; Description: {cm:LaunchProgram,{#MyAppName}}; Flags: nowait postinstall skipifsilent

[UninstallRun]
Filename: "powershell.exe"; Parameters: "-ExecutionPolicy Bypass -Command ""Get-Process python,node -ErrorAction SilentlyContinue | Where-Object {{ $_.Path -like '*HomeFlix*' }} | Stop-Process -Force"""; Flags: runhidden

[Code]
var
  VideoFoldersPage: TInputDirWizardPage;
  TMDbKeyPage: TInputQueryWizardPage;
  DetectionResult: String;
  PythonDetected: Boolean;
  NodeJSDetected: Boolean;
  FFmpegDetected: Boolean;

{ =====================================================
  DÉTECTION DE L'ENVIRONNEMENT
  ===================================================== }

function NeedsPython: Boolean;
begin
  Result := not PythonDetected;
end;

function NeedsNodeJS: Boolean;
begin
  Result := not NodeJSDetected;
end;

function NeedsFFmpeg: Boolean;
begin
  Result := not FFmpegDetected;
end;

procedure DetectEnvironment;
var
  ResultCode: Integer;
  JsonFile: String;
  JsonContent: TStringList;
begin
  // Exécuter le script de détection
  Exec('powershell.exe', 
       '-ExecutionPolicy Bypass -File "' + ExpandConstant('{tmp}\detect-environment.ps1') + '" -Json',
       '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  
  // Lire le résultat JSON
  JsonFile := ExpandConstant('{tmp}\detection_result.json');
  if FileExists(JsonFile) then
  begin
    JsonContent := TStringList.Create;
    try
      JsonContent.LoadFromFile(JsonFile);
      DetectionResult := JsonContent.Text;
      
      // Parser le JSON pour déterminer ce qui est installé
      PythonDetected := Pos('"Installed":true', DetectionResult) > 0;
      NodeJSDetected := Pos('"Installed":true', DetectionResult) > 0;
      FFmpegDetected := Pos('"Installed":true', DetectionResult) > 0;
    finally
      JsonContent.Free;
    end;
  end;
end;

{ =====================================================
  PAGES PERSONNALISÉES
  ===================================================== }

procedure InitializeWizard;
begin
  // Page de sélection des dossiers vidéo
  VideoFoldersPage := CreateInputDirWizardPage(wpSelectComponents,
    CustomMessage('VideoFoldersTitle'), 
    CustomMessage('VideoFoldersDescription'),
    CustomMessage('VideoFoldersSubText'),
    False, '');
  
  VideoFoldersPage.Add(CustomMessage('VideoFolder1'));
  VideoFoldersPage.Values[0] := ExpandConstant('{uservideos}');
  
  // Page de configuration TMDb
  TMDbKeyPage := CreateInputQueryWizardPage(wpSelectDir,
    CustomMessage('TMDbConfigTitle'),
    CustomMessage('TMDbConfigDescription'),
    CustomMessage('TMDbConfigSubText'));
  
  TMDbKeyPage.Add(CustomMessage('TMDbKeyLabel'), False);
  
  // Détection de l'environnement au démarrage
  DetectEnvironment;
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  
  // Validation de la page TMDb
  if CurPageID = TMDbKeyPage.ID then
  begin
    if (Length(TMDbKeyPage.Values[0]) > 0) and (Length(TMDbKeyPage.Values[0]) < 32) then
    begin
      MsgBox(CustomMessage('InvalidTMDbKey'), mbError, MB_OK);
      Result := False;
    end;
  end;
end;

{ =====================================================
  GÉNÉRATION DU FICHIER DE CONFIGURATION
  ===================================================== }

procedure CurStepChanged(CurStep: TSetupStep);
var
  ConfigFile: String;
  ConfigContent: TStringList;
  I: Integer;
begin
  if CurStep = ssPostInstall then
  begin
    ConfigFile := ExpandConstant('{app}\settings.yaml');
    ConfigContent := TStringList.Create;
    try
      // Générer le fichier settings.yaml
      ConfigContent.Add('# HomeFlix Configuration');
      ConfigContent.Add('# Généré automatiquement par l''installateur');
      ConfigContent.Add('');
      ConfigContent.Add('# Répertoires vidéo');
      ConfigContent.Add('video_directories:');
      
      for I := 0 to VideoFoldersPage.GetItemsCount - 1 do
      begin
        if VideoFoldersPage.Values[I] <> '' then
          ConfigContent.Add('  - "' + VideoFoldersPage.Values[I] + '"');
      end;
      
      ConfigContent.Add('');
      ConfigContent.Add('# Clé API TMDb');
      if TMDbKeyPage.Values[0] <> '' then
        ConfigContent.Add('tmdb_api_key: "' + TMDbKeyPage.Values[0] + '"')
      else
        ConfigContent.Add('tmdb_api_key: ""');
      
      ConfigContent.Add('');
      ConfigContent.Add('# Configuration par défaut');
      ConfigContent.Add('min_film_minutes: 75');
      ConfigContent.Add('max_series_minutes: 55');
      ConfigContent.Add('session_mode: mixed');
      ConfigContent.Add('auto_clean_filenames: true');
      
      case ActiveLanguage of
        'french': ConfigContent.Add('language: fr');
        'spanish': ConfigContent.Add('language: es');
      else
        ConfigContent.Add('language: en');
      end;
      
      ConfigContent.SaveToFile(ConfigFile);
    finally
      ConfigContent.Free;
    end;
  end;
end;

{ =====================================================
  MESSAGES PERSONNALISÉS
  ===================================================== }

[CustomMessages]
; Français
french.FullInstallation=Installation complète
french.MinimalInstallation=Installation minimale
french.CustomInstallation=Installation personnalisée
french.CoreApp=Application principale (obligatoire)
french.WindowsService=Service Windows (démarrage automatique)
french.CreateDesktopIcon=Créer une icône sur le bureau
french.CreateQuickLaunchIcon=Créer une icône dans la barre de lancement rapide
french.LaunchAtStartup=Lancer au démarrage de Windows
french.ConfigureFirewall=Configurer automatiquement le pare-feu Windows
french.AdditionalOptions=Options supplémentaires
french.DetectingEnvironment=Détection de l'environnement système...
french.InstallingPython=Installation de Python...
french.InstallingNodeJS=Installation de Node.js...
french.InstallingFFmpeg=Installation de FFmpeg...
french.InstallingDependencies=Installation des dépendances...
french.ConfiguringSystem=Configuration du système...
french.VideoFoldersTitle=Configuration des dossiers vidéo
french.VideoFoldersDescription=Sélectionnez les dossiers contenant vos vidéos
french.VideoFoldersSubText=Vous pourrez modifier ces dossiers plus tard dans les paramètres.
french.VideoFolder1=Dossier principal :
french.TMDbConfigTitle=Configuration TMDb
french.TMDbConfigDescription=Clé API TMDb (optionnel)
french.TMDbConfigSubText=Pour récupérer automatiquement les affiches et métadonnées, entrez votre clé API TMDb. Vous pouvez l'obtenir gratuitement sur themoviedb.org/settings/api
french.TMDbKeyLabel=Clé API TMDb :
french.InvalidTMDbKey=La clé API TMDb semble invalide. Elle doit contenir 32 caractères.

; English
english.FullInstallation=Full installation
english.MinimalInstallation=Minimal installation
english.CustomInstallation=Custom installation
english.CoreApp=Core application (required)
english.WindowsService=Windows Service (auto-start)
english.CreateDesktopIcon=Create a desktop icon
english.CreateQuickLaunchIcon=Create a Quick Launch icon
english.LaunchAtStartup=Launch at Windows startup
english.ConfigureFirewall=Automatically configure Windows Firewall
english.AdditionalOptions=Additional options
english.DetectingEnvironment=Detecting system environment...
english.InstallingPython=Installing Python...
english.InstallingNodeJS=Installing Node.js...
english.InstallingFFmpeg=Installing FFmpeg...
english.InstallingDependencies=Installing dependencies...
english.ConfiguringSystem=Configuring system...
english.VideoFoldersTitle=Video Folders Configuration
english.VideoFoldersDescription=Select folders containing your videos
english.VideoFoldersSubText=You can modify these folders later in settings.
english.VideoFolder1=Main folder:
english.TMDbConfigTitle=TMDb Configuration
english.TMDbConfigDescription=TMDb API Key (optional)
english.TMDbConfigSubText=To automatically retrieve posters and metadata, enter your TMDb API key. You can get one for free at themoviedb.org/settings/api
english.TMDbKeyLabel=TMDb API Key:
english.InvalidTMDbKey=The TMDb API key appears to be invalid. It should contain 32 characters.

; Español
spanish.FullInstallation=Instalación completa
spanish.MinimalInstallation=Instalación mínima
spanish.CustomInstallation=Instalación personalizada
spanish.CoreApp=Aplicación principal (obligatorio)
spanish.WindowsService=Servicio Windows (inicio automático)
spanish.CreateDesktopIcon=Crear un icono en el escritorio
spanish.CreateQuickLaunchIcon=Crear un icono en la barra de inicio rápido
spanish.LaunchAtStartup=Iniciar al arrancar Windows
spanish.ConfigureFirewall=Configurar automáticamente el cortafuegos de Windows
spanish.AdditionalOptions=Opciones adicionales
spanish.DetectingEnvironment=Detectando entorno del sistema...
spanish.InstallingPython=Instalando Python...
spanish.InstallingNodeJS=Instalando Node.js...
spanish.InstallingFFmpeg=Instalando FFmpeg...
spanish.InstallingDependencies=Instalando dependencias...
spanish.ConfiguringSystem=Configurando sistema...
spanish.VideoFoldersTitle=Configuración de carpetas de vídeo
spanish.VideoFoldersDescription=Seleccione las carpetas que contienen sus vídeos
spanish.VideoFoldersSubText=Podrá modificar estas carpetas más tarde en la configuración.
spanish.VideoFolder1=Carpeta principal:
spanish.TMDbConfigTitle=Configuración TMDb
spanish.TMDbConfigDescription=Clave API TMDb (opcional)
spanish.TMDbConfigSubText=Para recuperar automáticamente carteles y metadatos, introduzca su clave API de TMDb. Puede obtener una gratis en themoviedb.org/settings/api
spanish.TMDbKeyLabel=Clave API TMDb:
spanish.InvalidTMDbKey=La clave API de TMDb parece no ser válida. Debe contener 32 caracteres.
