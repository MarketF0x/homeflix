# Script d'installation automatique HomeOne pour Windows
# Exécuter avec: .\install.ps1

Write-Host "🎬 Installation de HomeOne - Gestionnaire de bibliothèque vidéo" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
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
    Write-Host "   Pour installer FFmpeg, exécutez: python check_and_install_ffmpeg.py" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📦 Installation des dépendances..." -ForegroundColor Cyan

# Créer l'environnement virtuel Python
if (-not (Test-Path ".venv")) {
    Write-Host "🔧 Création de l'environnement virtuel Python..." -ForegroundColor Yellow
    python -m venv .venv
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
& ".\.venv\Scripts\Activate.ps1"

# Installer les dépendances Python
Write-Host "🔧 Installation des dépendances Python..." -ForegroundColor Yellow
pip install -r server\requirements.txt --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erreur lors de l'installation des dépendances Python" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Dépendances Python installées" -ForegroundColor Green

# Installer les dépendances Node.js
Write-Host "🔧 Installation des dépendances Node.js..." -ForegroundColor Yellow
Set-Location client
npm install --silent
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erreur lors de l'installation des dépendances Node.js" -ForegroundColor Red
    Set-Location ..
    exit 1
}
Set-Location ..
Write-Host "✅ Dépendances Node.js installées" -ForegroundColor Green

# Créer le dossier de configuration si nécessaire
$configDir = "$env:USERPROFILE\.homeone"
if (-not (Test-Path $configDir)) {
    New-Item -ItemType Directory -Path $configDir -Force | Out-Null
}

# Vérifier le fichier settings.yaml
Write-Host ""
Write-Host "🔧 Configuration..." -ForegroundColor Cyan
if (-not (Test-Path "settings.yaml")) {
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
    
    $defaultSettings | Out-File -FilePath "settings.yaml" -Encoding UTF8
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
Write-Host "   1. Éditez settings.yaml pour configurer vos répertoires vidéo" -ForegroundColor White
Write-Host "   2. Obtenez une clé API TMDb sur: https://www.themoviedb.org/settings/api" -ForegroundColor White
Write-Host "   3. Démarrez le serveur: cd server; python main.py" -ForegroundColor White
Write-Host "   4. Dans un autre terminal, démarrez le client: cd client; npm run dev" -ForegroundColor White
Write-Host "   5. Ouvrez votre navigateur sur: http://localhost:5173" -ForegroundColor White
Write-Host ""
Write-Host "🚀 Pour un lancement rapide, utilisez:" -ForegroundColor Cyan
Write-Host "   .\launch_homeone.ps1" -ForegroundColor White
Write-Host ""
