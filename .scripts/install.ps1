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

# Vérification de Python
Write-Host "🔍 Vérification de Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python trouvé: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python n'est pas installé!" -ForegroundColor Red
    Write-Host "   Téléchargez Python depuis: https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "   Assurez-vous de cocher 'Add Python to PATH' lors de l'installation" -ForegroundColor Yellow
    exit 1
}

# Vérification de Node.js
Write-Host "🔍 Vérification de Node.js..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✅ Node.js trouvé: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js n'est pas installé!" -ForegroundColor Red
    Write-Host "   Téléchargez Node.js depuis: https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}

# Vérification de FFmpeg (optionnel)
Write-Host "🔍 Vérification de FFmpeg..." -ForegroundColor Yellow
try {
    $ffmpegVersion = ffmpeg -version 2>&1 | Select-Object -First 1
    Write-Host "✅ FFmpeg trouvé: $ffmpegVersion" -ForegroundColor Green
} catch {
    Write-Host "⚠️  FFmpeg non trouvé (optionnel)" -ForegroundColor Yellow
    Write-Host "   Les miniatures seront récupérées depuis TMDb uniquement" -ForegroundColor Yellow
    Write-Host "   Pour installer FFmpeg, exécutez: python .utils\check_and_install_ffmpeg.py" -ForegroundColor Yellow
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
Write-Host "📝 Prochaines étapes:" -ForegroundColor Cyan
Write-Host "   1. Configurez votre clé API TMDb (OBLIGATOIRE)" -ForegroundColor Yellow
Write-Host "      → Exécutez: .\.config\setup-tmdb-key.ps1" -ForegroundColor White
Write-Host "      → Guide complet: .docs\GUIDE_TMDB_API_KEY.md" -ForegroundColor White
Write-Host ""
Write-Host "   2. Éditez settings.yaml pour configurer vos répertoires vidéo" -ForegroundColor White
Write-Host ""
Write-Host "   3. Lancez Homeflix:" -ForegroundColor White
Write-Host "      → .\start-homeflix-app.ps1  (Application native - recommandé)" -ForegroundColor Cyan
Write-Host "      → .\homeflix.ps1            (Mode navigateur)" -ForegroundColor White
Write-Host ""
Write-Host "📚 Documentation importante:" -ForegroundColor Cyan
Write-Host "   • README_APP.md - Guide application de bureau" -ForegroundColor White
Write-Host "   • .docs\GUIDE_TMDB_API_KEY.md - Configuration de la clé API" -ForegroundColor White
Write-Host "   • .docs\TMDB_TERMS_SUMMARY.md - Conditions d'utilisation TMDb" -ForegroundColor White
Write-Host "   • LICENSE - Licence MIT du projet" -ForegroundColor White
Write-Host ""

# Proposer de créer les raccourcis
Write-Host "🔗 Créer des raccourcis sur le bureau ? (o/N)" -ForegroundColor Yellow
$createShortcuts = Read-Host
if ($createShortcuts -eq 'o' -or $createShortcuts -eq 'O') {
    Write-Host ""
    if (Test-Path "$projectRoot\.config\create_shortcuts.ps1") {
        & "$projectRoot\.config\create_shortcuts.ps1"
    } else {
        Write-Host "⚠️  Script de création de raccourcis introuvable" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "🔧 Configuration TMDb maintenant ? (o/N)" -ForegroundColor Yellow
$configureTmdb = Read-Host
if ($configureTmdb -eq 'o' -or $configureTmdb -eq 'O') {
    Write-Host ""
    & "$projectRoot\.config\setup-tmdb-key.ps1"
}
Write-Host ""
