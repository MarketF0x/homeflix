# Script d'installation automatique Homeflix pour Windows
# Exécuter avec: .\install.ps1

param(
    [Parameter(Mandatory=$false)]
    [switch]$Repair
)

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path | Split-Path -Parent

# Fonction pour détecter si Homeflix est déjà installé
function Test-HomeflixInstalled {
    $markers = @(
        (Test-Path "$projectRoot\.venv\Scripts\python.exe"),
        (Test-Path "$projectRoot\.venv310\Scripts\python.exe"),
        (Test-Path "$projectRoot\client\node_modules"),
        (Test-Path "$projectRoot\data\homeflix.db")
    )
    
    $installedCount = ($markers | Where-Object { $_ -eq $true }).Count
    return $installedCount -ge 2
}

# Fonction pour afficher le menu de réparation
function Show-RepairMenu {
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════╗" -ForegroundColor Yellow
    Write-Host "║                                                        ║" -ForegroundColor Yellow
    Write-Host "║     🔧 HOMEFLIX DÉJÀ INSTALLÉ - MODE RÉPARATION       ║" -ForegroundColor Yellow
    Write-Host "║                                                        ║" -ForegroundColor Yellow
    Write-Host "╚════════════════════════════════════════════════════════╝" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Une installation existante a été détectée." -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Que souhaitez-vous faire ?" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  [1] 🔧 Réparer l'installation" -ForegroundColor White
    Write-Host "      → Réinstalle les dépendances manquantes" -ForegroundColor Gray
    Write-Host "      → Conserve la base de données et configuration" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  [2] 🔄 Réinstallation complète" -ForegroundColor White
    Write-Host "      → Supprime et réinstalle tout" -ForegroundColor Gray
    Write-Host "      → CONSERVE la base de données et settings.yaml" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  [3] ❌ Annuler" -ForegroundColor White
    Write-Host ""
    Write-Host "Votre choix (1/2/3): " -ForegroundColor Yellow -NoNewline
    
    $choice = Read-Host
    return $choice
}

# Fonction pour réparer l'installation
function Repair-Installation {
    Write-Host ""
    Write-Host "🔧 Réparation de l'installation..." -ForegroundColor Cyan
    Write-Host ""
    
    # Vérifier et réparer l'environnement Python
    if (-not (Test-Path "$projectRoot\.venv310\Scripts\python.exe")) {
        Write-Host "📦 Recréation de l'environnement Python..." -ForegroundColor Yellow
        if (Test-Path "$projectRoot\.venv310") {
            Remove-Item "$projectRoot\.venv310" -Recurse -Force -ErrorAction SilentlyContinue
        }
        python -m venv "$projectRoot\.venv310"
        Write-Host "   ✓ Environnement Python recréé" -ForegroundColor Green
    } else {
        Write-Host "✅ Environnement Python OK" -ForegroundColor Green
    }
    
    # Réinstaller les dépendances Python
    Write-Host "📦 Vérification des dépendances Python..." -ForegroundColor Yellow
    & "$projectRoot\.venv310\Scripts\python.exe" -m pip install --upgrade pip --quiet
    & "$projectRoot\.venv310\Scripts\pip.exe" install -r "$projectRoot\server\requirements.txt" --quiet
    Write-Host "   ✓ Dépendances Python vérifiées" -ForegroundColor Green
    
    # Vérifier et réparer node_modules
    if (-not (Test-Path "$projectRoot\client\node_modules")) {
        Write-Host "📦 Installation des dépendances Node.js..." -ForegroundColor Yellow
        Push-Location "$projectRoot\client"
        npm install --silent
        Pop-Location
        Write-Host "   ✓ Dépendances Node.js installées" -ForegroundColor Green
    } else {
        Write-Host "✅ Dépendances Node.js OK" -ForegroundColor Green
    }
    
    # Vérifier les dossiers essentiels
    Write-Host "📁 Vérification de la structure..." -ForegroundColor Yellow
    $essentialDirs = @("data", "data\thumbs", "data\posters")
    foreach ($dir in $essentialDirs) {
        if (-not (Test-Path "$projectRoot\$dir")) {
            New-Item -ItemType Directory -Path "$projectRoot\$dir" -Force | Out-Null
            Write-Host "   ✓ Dossier $dir créé" -ForegroundColor Gray
        }
    }
    Write-Host "   ✓ Structure vérifiée" -ForegroundColor Green
    
    Write-Host ""
    Write-Host "✅ Réparation terminée avec succès!" -ForegroundColor Green
}

# DÉBUT DU SCRIPT PRINCIPAL

Clear-Host
Write-Host ""

# Détecter si déjà installé
$isInstalled = Test-HomeflixInstalled

if ($isInstalled -and -not $Repair) {
    $choice = Show-RepairMenu
    
    switch ($choice) {
        "1" {
            # Réparation
            Repair-Installation
            Write-Host ""
            Write-Host "🚀 Vous pouvez maintenant lancer Homeflix avec:" -ForegroundColor Cyan
            Write-Host "   .\homeflix.ps1" -ForegroundColor White
            Write-Host ""
            exit 0
        }
        "2" {
            # Réinstallation complète
            Write-Host ""
            Write-Host "🔄 Réinstallation complète..." -ForegroundColor Cyan
            Write-Host ""
            Write-Host "⚠️  Sauvegarde de la base de données..." -ForegroundColor Yellow
            if (Test-Path "$projectRoot\data\homeflix.db") {
                Copy-Item "$projectRoot\data\homeflix.db" "$projectRoot\data\homeflix.db.backup" -Force
                Write-Host "   ✓ Sauvegardée dans data\homeflix.db.backup" -ForegroundColor Green
            }
            Write-Host ""
            Write-Host "🗑️  Suppression des environnements..." -ForegroundColor Yellow
            Remove-Item "$projectRoot\.venv" -Recurse -Force -ErrorAction SilentlyContinue
            Remove-Item "$projectRoot\.venv310" -Recurse -Force -ErrorAction SilentlyContinue
            Remove-Item "$projectRoot\client\node_modules" -Recurse -Force -ErrorAction SilentlyContinue
            Write-Host "   ✓ Environnements supprimés" -ForegroundColor Green
            Write-Host ""
            # Continuer avec l'installation normale
        }
        "3" {
            Write-Host ""
            Write-Host "❌ Installation annulée" -ForegroundColor Red
            exit 0
        }
        default {
            Write-Host ""
            Write-Host "❌ Choix invalide. Installation annulée." -ForegroundColor Red
            exit 1
        }
    }
}

Write-Host "🎬 Installation de Homeflix - Serveur de streaming personnel" -ForegroundColor Cyan
Write-Host "=============================================================" -ForegroundColor Cyan
Write-Host ""

# ═══════════════════════════════════════════════════════════════
# VÉRIFICATION ET INSTALLATION AUTOMATIQUE DES DÉPENDANCES
# ═══════════════════════════════════════════════════════════════

Write-Host "🔍 Vérification des dépendances système..." -ForegroundColor Cyan
Write-Host ""

# Fonction pour installer Python automatiquement
function Install-Python {
    Write-Host "📦 Installation automatique de Python 3.11..." -ForegroundColor Yellow
    $pythonUrl = "https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"
    $pythonInstaller = "$env:TEMP\python-installer.exe"
    
    try {
        Write-Host "   Téléchargement de Python..." -ForegroundColor Gray
        Invoke-WebRequest -Uri $pythonUrl -OutFile $pythonInstaller -UseBasicParsing
        
        Write-Host "   Installation en cours..." -ForegroundColor Gray
        Start-Process -FilePath $pythonInstaller -ArgumentList "/quiet","InstallAllUsers=1","PrependPath=1","Include_test=0" -Wait
        
        # Rafraîchir l'environnement PATH
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        
        Write-Host "✅ Python installé avec succès!" -ForegroundColor Green
        Remove-Item $pythonInstaller -Force -ErrorAction SilentlyContinue
        return $true
    } catch {
        Write-Host "❌ Erreur lors de l'installation de Python" -ForegroundColor Red
        Write-Host "   Veuillez installer manuellement: https://www.python.org/downloads/" -ForegroundColor Yellow
        return $false
    }
}

# Fonction pour installer Node.js automatiquement
function Install-NodeJS {
    Write-Host "📦 Installation automatique de Node.js LTS..." -ForegroundColor Yellow
    $nodeUrl = "https://nodejs.org/dist/v20.18.1/node-v20.18.1-x64.msi"
    $nodeInstaller = "$env:TEMP\nodejs-installer.msi"
    
    try {
        Write-Host "   Téléchargement de Node.js..." -ForegroundColor Gray
        Invoke-WebRequest -Uri $nodeUrl -OutFile $nodeInstaller -UseBasicParsing
        
        Write-Host "   Installation en cours (cela peut prendre 2-3 minutes)..." -ForegroundColor Gray
        Start-Process msiexec.exe -ArgumentList "/i","$nodeInstaller","/quiet","/norestart" -Wait
        
        # Rafraîchir l'environnement PATH
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        
        Write-Host "✅ Node.js installé avec succès!" -ForegroundColor Green
        Remove-Item $nodeInstaller -Force -ErrorAction SilentlyContinue
        return $true
    } catch {
        Write-Host "❌ Erreur lors de l'installation de Node.js" -ForegroundColor Red
        Write-Host "   Veuillez installer manuellement: https://nodejs.org/" -ForegroundColor Yellow
        return $false
    }
}

# Fonction pour installer FFmpeg automatiquement
function Install-FFmpeg {
    Write-Host "📦 Installation automatique de FFmpeg..." -ForegroundColor Yellow
    
    # Utiliser le script existant si disponible
    if (Test-Path "$projectRoot\check_and_install_ffmpeg.py") {
        try {
            & python "$projectRoot\check_and_install_ffmpeg.py"
            Write-Host "✅ FFmpeg installé avec succès!" -ForegroundColor Green
            return $true
        } catch {
            Write-Host "⚠️  Installation FFmpeg échouée (non critique)" -ForegroundColor Yellow
            return $false
        }
    }
    
    # Alternative: installation manuelle guidée
    Write-Host "   Installation manuelle recommandée:" -ForegroundColor Gray
    Write-Host "   1. Télécharger: https://github.com/BtbN/FFmpeg-Builds/releases" -ForegroundColor Gray
    Write-Host "   2. Extraire dans C:\ffmpeg" -ForegroundColor Gray
    Write-Host "   3. Ajouter C:\ffmpeg\bin au PATH" -ForegroundColor Gray
    return $false
}

# Vérification de Python
Write-Host "1️⃣  Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "   ✅ Python trouvé: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️  Python non trouvé" -ForegroundColor Yellow
    $installPython = Read-Host "   Installer Python automatiquement ? (O/n)"
    if ($installPython -ne 'n' -and $installPython -ne 'N') {
        if (-not (Install-Python)) {
            exit 1
        }
    } else {
        Write-Host "❌ Python est requis pour continuer" -ForegroundColor Red
        exit 1
    }
}

# Vérification de Node.js
Write-Host "2️⃣  Node.js..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version 2>&1
    Write-Host "   ✅ Node.js trouvé: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️  Node.js non trouvé" -ForegroundColor Yellow
    $installNode = Read-Host "   Installer Node.js automatiquement ? (O/n)"
    if ($installNode -ne 'n' -and $installNode -ne 'N') {
        if (-not (Install-NodeJS)) {
            exit 1
        }
    } else {
        Write-Host "❌ Node.js est requis pour continuer" -ForegroundColor Red
        exit 1
    }
}

# Vérification de FFmpeg
Write-Host "3️⃣  FFmpeg..." -ForegroundColor Yellow
try {
    $ffmpegVersion = ffmpeg -version 2>&1 | Select-Object -First 1
    Write-Host "   ✅ FFmpeg trouvé: $ffmpegVersion" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️  FFmpeg non trouvé (recommandé)" -ForegroundColor Yellow
    $installFFmpeg = Read-Host "   Installer FFmpeg automatiquement ? (O/n)"
    if ($installFFmpeg -ne 'n' -and $installFFmpeg -ne 'N') {
        Install-FFmpeg | Out-Null
    } else {
        Write-Host "   ℹ️  Vous pourrez l'installer plus tard" -ForegroundColor Cyan
    }
}

Write-Host ""
Write-Host "📦 Installation des dépendances..." -ForegroundColor Cyan

# Créer l'environnement virtuel Python
if (-not (Test-Path "$projectRoot\.venv310")) {
    Write-Host "🔧 Création de l'environnement virtuel Python..." -ForegroundColor Yellow
    python -m venv "$projectRoot\.venv310"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Erreur lors de la création de l'environnement virtuel" -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ Environnement virtuel créé" -ForegroundColor Green
} else {
    Write-Host "✅ Environnement virtuel déjà présent" -ForegroundColor Green
}

# Activer l'environnement virtuel
Write-Host "🔧 Activation de l'environnement virtuel..." -ForegroundColor Yellow
& "$projectRoot\.venv310\Scripts\Activate.ps1"

# Installer les dépendances Python
Write-Host "🔧 Installation des dépendances Python..." -ForegroundColor Yellow
& "$projectRoot\.venv310\Scripts\pip.exe" install -r "$projectRoot\server\requirements.txt" --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erreur lors de l'installation des dépendances Python" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Dépendances Python installées" -ForegroundColor Green

# Installer les dépendances Node.js
Write-Host "🔧 Installation des dépendances Node.js (Frontend)..." -ForegroundColor Yellow
Push-Location "$projectRoot\client"
npm install --silent
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erreur lors de l'installation des dépendances Node.js" -ForegroundColor Red
    Pop-Location
    exit 1
}
Pop-Location
Write-Host "✅ Dépendances Frontend installées" -ForegroundColor Green

# Installer les dépendances Electron (optionnel mais recommandé)
Write-Host "🔧 Installation de l'application Electron..." -ForegroundColor Yellow
if (Test-Path "$projectRoot\electron\package.json") {
    Push-Location "$projectRoot\electron"
    npm install --silent
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Application Electron installée" -ForegroundColor Green
        
        # Créer l'icône si nécessaire
        if (-not (Test-Path "$projectRoot\electron\icon.png")) {
            Write-Host "🎨 Génération de l'icône..." -ForegroundColor Yellow
            if (Test-Path "$projectRoot\create_electron_icon.py") {
                & "$projectRoot\.venv310\Scripts\python.exe" "$projectRoot\create_electron_icon.py"
            }
        }
    } else {
        Write-Host "⚠️  Erreur installation Electron (non critique)" -ForegroundColor Yellow
    }
    Pop-Location
} else {
    Write-Host "ℹ️  Electron non configuré (optionnel)" -ForegroundColor Cyan
}

# Créer le dossier data si nécessaire
if (-not (Test-Path "$projectRoot\data")) {
    New-Item -ItemType Directory -Path "$projectRoot\data" -Force | Out-Null
}
if (-not (Test-Path "$projectRoot\data\thumbs")) {
    New-Item -ItemType Directory -Path "$projectRoot\data\thumbs" -Force | Out-Null
}
if (-not (Test-Path "$projectRoot\data\posters")) {
    New-Item -ItemType Directory -Path "$projectRoot\data\posters" -Force | Out-Null
}

# Vérifier le fichier settings.yaml
Write-Host ""
Write-Host "🔧 Configuration..." -ForegroundColor Cyan
if (-not (Test-Path "$projectRoot\settings.yaml")) {
    Write-Host "⚠️  Fichier settings.yaml introuvable" -ForegroundColor Yellow
    Write-Host "   Création d'un fichier de configuration par défaut..." -ForegroundColor Yellow
    
    $defaultSettings = @"
# Répertoires à scanner pour les vidéos
video_directories:
  - "$env:USERPROFILE\Videos"

# Durées minimales/maximales pour filtrer films/séries
min_film_minutes: 75      # >= 1h15 = film
max_series_minutes: 55    # entre 20 et 55 min = série

# Mode de session par défaut (mixed | films | series)
session_mode: mixed

# Clé API TMDb pour récupérer les métadonnées en ligne (gratuit)
# Obtenez votre clé sur: https://www.themoviedb.org/settings/api
tmdb_api_key: ""

# Nettoyage automatique des noms de fichiers (true/false)
auto_clean_filenames: true

# Langue de l'interface (fr/en/de/es)
language: fr
"@
    
    $defaultSettings | Out-File -FilePath "$projectRoot\settings.yaml" -Encoding UTF8
    Write-Host "✅ Fichier settings.yaml créé" -ForegroundColor Green
    Write-Host ""
    Write-Host "⚠️  IMPORTANT: Éditez settings.yaml pour:" -ForegroundColor Yellow
    Write-Host "   1. Ajouter vos répertoires vidéo" -ForegroundColor Yellow
    Write-Host "   2. Ajouter votre clé API TMDb (optionnel mais recommandé)" -ForegroundColor Yellow
} else {
    Write-Host "✅ Fichier settings.yaml trouvé" -ForegroundColor Green
}

Write-Host ""
Write-Host "✨ Installation terminée avec succès!" -ForegroundColor Green
Write-Host ""

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION AUTOMATIQUE TMDB
# ═══════════════════════════════════════════════════════════════

Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                                                                ║" -ForegroundColor Cyan
Write-Host "║          🔑 Configuration de la Clé API TMDb                  ║" -ForegroundColor Cyan
Write-Host "║                    (OBLIGATOIRE)                               ║" -ForegroundColor Cyan
Write-Host "║                                                                ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "TMDb permet d'afficher les affiches, synopsis et métadonnées de vos films." -ForegroundColor White
Write-Host "La clé API est GRATUITE pour usage personnel." -ForegroundColor Green
Write-Host ""

# Vérifier si une clé existe déjà
$existingKey = $null
if (Test-Path "$projectRoot\settings.yaml") {
    $content = Get-Content "$projectRoot\settings.yaml" -Raw
    if ($content -match "tmdb_api_key:\s*'?([a-f0-9]{32})'?") {
        $existingKey = $matches[1]
    }
}

if ($existingKey) {
    Write-Host "✅ Clé TMDb déjà configurée: $($existingKey.Substring(0,8))..." -ForegroundColor Green
    Write-Host ""
    $reconfigureTmdb = Read-Host "Reconfigurer la clé TMDb ? (o/N)"
    if ($reconfigureTmdb -ne 'o' -and $reconfigureTmdb -ne 'O') {
        Write-Host "ℹ️  Configuration TMDb conservée" -ForegroundColor Cyan
        $skipTmdb = $true
    } else {
        $skipTmdb = $false
    }
} else {
    $skipTmdb = $false
}

if (-not $skipTmdb) {
    Write-Host "📋 Options de configuration TMDb:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  [1] 🌐 Ouvrir le guide et saisir la clé maintenant (RECOMMANDÉ)" -ForegroundColor White
    Write-Host "  [2] ⏭️  Configurer plus tard" -ForegroundColor Gray
    Write-Host ""
    $tmdbChoice = Read-Host "Votre choix (1/2)"
    
    if ($tmdbChoice -eq "1") {
        Write-Host ""
        Write-Host "📋 Instructions rapides:" -ForegroundColor Yellow
        Write-Host "1. Je vais ouvrir la page d'inscription TMDb dans votre navigateur" -ForegroundColor White
        Write-Host "2. Créez un compte (gratuit, 2 minutes)" -ForegroundColor White
        Write-Host "3. Confirmez votre email" -ForegroundColor White
        Write-Host "4. Allez sur: https://www.themoviedb.org/settings/api" -ForegroundColor White
        Write-Host "5. Cliquez 'Request an API Key' → 'Developer'" -ForegroundColor White
        Write-Host "6. Remplissez le formulaire (usage personnel)" -ForegroundColor White
        Write-Host "7. Copiez la clé API (v3 auth) - 32 caractères" -ForegroundColor White
        Write-Host ""
        
        $openBrowser = Read-Host "Ouvrir la page d'inscription TMDb maintenant ? (O/n)"
        if ($openBrowser -ne 'n' -and $openBrowser -ne 'N') {
            Write-Host "🌐 Ouverture du navigateur..." -ForegroundColor Cyan
            Start-Process "https://www.themoviedb.org/signup"
            Write-Host ""
            Write-Host "⏱️  Prenez le temps de créer votre compte et d'obtenir la clé API..." -ForegroundColor Yellow
            Write-Host "📚 Guide détaillé disponible: .docs\GUIDE_TMDB_API_KEY.md" -ForegroundColor Gray
            Write-Host ""
            Read-Host "Appuyez sur Entrée quand vous avez votre clé API"
        }
        
        Write-Host ""
        Write-Host "🔑 Entrez votre clé API TMDb (32 caractères):" -ForegroundColor Cyan
        $tmdbKey = Read-Host
        
        # Valider et enregistrer la clé
        if ($tmdbKey -match '^[a-f0-9]{32}$') {
            Write-Host "🔍 Validation de la clé..." -ForegroundColor Yellow
            
            try {
                $response = Invoke-RestMethod -Uri "https://api.themoviedb.org/3/configuration?api_key=$tmdbKey" -ErrorAction Stop
                Write-Host "✅ Clé API valide et fonctionnelle!" -ForegroundColor Green
                
                # Enregistrer dans settings.yaml
                $content = Get-Content "$projectRoot\settings.yaml" -Raw
                if ($content -match "tmdb_api_key:\s*.*") {
                    $content = $content -replace "tmdb_api_key:\s*.*", "tmdb_api_key: '$tmdbKey'"
                } else {
                    $content += "`ntmdb_api_key: '$tmdbKey'"
                }
                Set-Content -Path "$projectRoot\settings.yaml" -Value $content -NoNewline
                Write-Host "✅ Clé enregistrée dans settings.yaml" -ForegroundColor Green
            } catch {
                Write-Host "⚠️  Impossible de valider la clé (problème de connexion)" -ForegroundColor Yellow
                Write-Host "   La clé sera quand même enregistrée" -ForegroundColor Gray
                
                $content = Get-Content "$projectRoot\settings.yaml" -Raw
                if ($content -match "tmdb_api_key:\s*.*") {
                    $content = $content -replace "tmdb_api_key:\s*.*", "tmdb_api_key: '$tmdbKey'"
                } else {
                    $content += "`ntmdb_api_key: '$tmdbKey'"
                }
                Set-Content -Path "$projectRoot\settings.yaml" -Value $content -NoNewline
                Write-Host "✅ Clé enregistrée dans settings.yaml" -ForegroundColor Green
            }
        } else {
            Write-Host "⚠️  Format de clé invalide (doit être 32 caractères hexadécimaux)" -ForegroundColor Yellow
            Write-Host "   Vous pourrez la configurer plus tard avec:" -ForegroundColor Gray
            Write-Host "   .\.config\setup-tmdb-key.ps1" -ForegroundColor White
        }
    } else {
        Write-Host ""
        Write-Host "ℹ️  Configuration TMDb reportée" -ForegroundColor Cyan
        Write-Host "   Pour configurer plus tard: .\.config\setup-tmdb-key.ps1" -ForegroundColor Gray
    }
}

Write-Host ""

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION TAILSCALE (ACCÈS DISTANT)
# ═══════════════════════════════════════════════════════════════

Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                                                                ║" -ForegroundColor Cyan
Write-Host "║          🌐 Configuration Tailscale (Accès Distant)           ║" -ForegroundColor Cyan
Write-Host "║                    (OBLIGATOIRE)                               ║" -ForegroundColor Cyan
Write-Host "║                                                                ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "Tailscale permet d'accéder à Homeflix depuis n'importe où en toute sécurité." -ForegroundColor White
Write-Host "C'est comme un VPN privé entre vos appareils (gratuit pour usage personnel)." -ForegroundColor Green
Write-Host ""

# Vérifier si Tailscale est déjà installé
$tailscaleInstalled = $false
try {
    $tailscaleService = Get-Service -Name "Tailscale" -ErrorAction SilentlyContinue
    if ($tailscaleService) {
        $tailscaleInstalled = $true
        Write-Host "✅ Tailscale est déjà installé" -ForegroundColor Green
        
        # Vérifier s'il est connecté
        try {
            $tailscaleStatus = & tailscale status 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ Tailscale est connecté et actif" -ForegroundColor Green
                Write-Host ""
                Write-Host "Votre réseau Tailscale:" -ForegroundColor Cyan
                Write-Host $tailscaleStatus
                $skipTailscale = $true
            } else {
                Write-Host "⚠️  Tailscale n'est pas connecté" -ForegroundColor Yellow
                $skipTailscale = $false
            }
        } catch {
            $skipTailscale = $false
        }
    }
} catch {
    $tailscaleInstalled = $false
}

if (-not $skipTailscale) {
    Write-Host "📋 Options Tailscale:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  [1] 🌐 Installer et configurer Tailscale maintenant (RECOMMANDÉ)" -ForegroundColor White
    Write-Host "  [2] ⏭️  Installer plus tard (accès local uniquement)" -ForegroundColor Gray
    Write-Host ""
    $tailscaleChoice = Read-Host "Votre choix (1/2)"
    
    if ($tailscaleChoice -eq "1") {
        if (-not $tailscaleInstalled) {
            Write-Host ""
            Write-Host "📦 Installation de Tailscale..." -ForegroundColor Yellow
            
            $tailscaleUrl = "https://pkgs.tailscale.com/stable/tailscale-setup-latest.exe"
            $tailscaleInstaller = "$env:TEMP\tailscale-setup.exe"
            
            try {
                Write-Host "   Téléchargement..." -ForegroundColor Gray
                Invoke-WebRequest -Uri $tailscaleUrl -OutFile $tailscaleInstaller -UseBasicParsing
                
                Write-Host "   Installation en cours..." -ForegroundColor Gray
                Write-Host ""
                Write-Host "   ⚠️  IMPORTANT: Suivez l'assistant d'installation Tailscale" -ForegroundColor Yellow
                Write-Host ""
                Start-Process -FilePath $tailscaleInstaller -Wait
                
                Write-Host "✅ Tailscale installé!" -ForegroundColor Green
                Remove-Item $tailscaleInstaller -Force -ErrorAction SilentlyContinue
            } catch {
                Write-Host "❌ Erreur lors de l'installation de Tailscale" -ForegroundColor Red
                Write-Host "   Téléchargez manuellement: https://tailscale.com/download/windows" -ForegroundColor Yellow
            }
        }
        
        Write-Host ""
        Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
        Write-Host "║                                                                ║" -ForegroundColor Green
        Write-Host "║          📖 Guide de Configuration Tailscale                   ║" -ForegroundColor Green
        Write-Host "║                                                                ║" -ForegroundColor Green
        Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Green
        Write-Host ""
        Write-Host "Sur CET ORDINATEUR (serveur Homeflix):" -ForegroundColor Cyan
        Write-Host "  1. Cliquez sur l'icône Tailscale dans la barre des tâches" -ForegroundColor White
        Write-Host "  2. Cliquez 'Log in'" -ForegroundColor White
        Write-Host "  3. Connectez-vous avec Google, Microsoft ou GitHub" -ForegroundColor White
        Write-Host "  4. Votre PC recevra une adresse IP Tailscale (ex: 100.x.x.x)" -ForegroundColor White
        Write-Host ""
        Write-Host "Sur L'ORDINATEUR DISTANT (client):" -ForegroundColor Cyan
        Write-Host "  1. Installez Tailscale: https://tailscale.com/download" -ForegroundColor White
        Write-Host "  2. Connectez-vous avec le MÊME compte" -ForegroundColor White
        Write-Host "  3. Les deux appareils seront dans le même réseau privé" -ForegroundColor White
        Write-Host ""
        Write-Host "ACCÈS À HOMEFLIX à distance:" -ForegroundColor Cyan
        Write-Host "  • Lancez Homeflix sur ce PC (serveur)" -ForegroundColor White
        Write-Host "  • Sur l'appareil distant, ouvrez un navigateur" -ForegroundColor White
        Write-Host "  • Allez sur: http://[IP-TAILSCALE-DU-SERVEUR]:8000" -ForegroundColor White
        Write-Host "  • L'IP Tailscale s'affichera au lancement de Homeflix" -ForegroundColor White
        Write-Host ""
        Write-Host "💡 Astuce: Tailscale fonctionne automatiquement en arrière-plan" -ForegroundColor Yellow
        Write-Host "    Pas besoin de configuration de routeur ou port forwarding!" -ForegroundColor Yellow
        Write-Host ""
        
        Read-Host "Appuyez sur Entrée pour continuer"
    } else {
        Write-Host ""
        Write-Host "ℹ️  Installation Tailscale reportée" -ForegroundColor Cyan
        Write-Host "   ⚠️  Homeflix sera accessible uniquement en local (localhost)" -ForegroundColor Yellow
        Write-Host "   Pour installer plus tard: .\.config\install-tailscale.ps1" -ForegroundColor Gray
    }
}

Write-Host ""

# ═══════════════════════════════════════════════════════════════
# RÉSUMÉ ET PROCHAINES ÉTAPES
# ═══════════════════════════════════════════════════════════════

Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                                                                ║" -ForegroundColor Green
Write-Host "║          ✅ INSTALLATION TERMINÉE AVEC SUCCÈS!                ║" -ForegroundColor Green
Write-Host "║                                                                ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""

Write-Host "📝 Prochaines étapes:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1️⃣  Configurer vos dossiers vidéo" -ForegroundColor Yellow
Write-Host "   → Éditez: settings.yaml" -ForegroundColor White
Write-Host "   → Ajoutez vos chemins dans 'video_directories'" -ForegroundColor White
Write-Host ""
Write-Host "2️⃣  Lancer Homeflix" -ForegroundColor Yellow
Write-Host "   → Application desktop: .\start-homeflix-app.ps1" -ForegroundColor Cyan
Write-Host "   → Mode navigateur:    .\homeflix.ps1" -ForegroundColor White
Write-Host ""

if (-not $existingKey) {
    Write-Host "⚠️  N'oubliez pas de configurer votre clé TMDb si vous l'avez sautée!" -ForegroundColor Yellow
    Write-Host "   → .\.config\setup-tmdb-key.ps1" -ForegroundColor White
    Write-Host ""
}

if (-not $tailscaleInstalled -or -not $skipTailscale) {
    Write-Host "⚠️  Pour l'accès distant, configurez Tailscale:" -ForegroundColor Yellow
    Write-Host "   → .\.config\install-tailscale.ps1" -ForegroundColor White
    Write-Host ""
}

Write-Host "📚 Documentation:" -ForegroundColor Cyan
Write-Host "   • docs/LANCEMENT.md - Guide de démarrage rapide" -ForegroundColor White
Write-Host "   • docs/GUIDE_UTILISATEUR.md - Guide complet" -ForegroundColor White
Write-Host "   • docs/FAQ.md - Questions fréquentes" -ForegroundColor White
Write-Host ""
