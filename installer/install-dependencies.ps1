# =====================================================
# HOMEFLIX - INSTALLATION DES DÉPENDANCES
# =====================================================
# Installe les packages Python et Node.js

param(
    [Parameter(Mandatory=$false)]
    [string]$InstallPath = $PSScriptRoot
)

$ErrorActionPreference = "Stop"

Write-Host "📦 Installation des dépendances HomeFlix..." -ForegroundColor Cyan
Write-Host ""

# Aller dans le dossier d'installation
$appPath = Split-Path -Parent $InstallPath
Set-Location $appPath

# =====================================================
# ENVIRONNEMENT VIRTUEL PYTHON
# =====================================================

Write-Host "🐍 Configuration de l'environnement Python..." -ForegroundColor Yellow

$venvPath = Join-Path $appPath ".venv310"

if (-not (Test-Path $venvPath)) {
    Write-Host "   Création de l'environnement virtuel..." -ForegroundColor Gray
    python -m venv $venvPath
    if ($LASTEXITCODE -ne 0) {
        throw "Impossible de créer l'environnement virtuel Python"
    }
} else {
    Write-Host "   Environnement virtuel déjà présent" -ForegroundColor Gray
}

# Activer l'environnement
$pythonExe = Join-Path $venvPath "Scripts\python.exe"
$pipExe = Join-Path $venvPath "Scripts\pip.exe"

# Mettre à jour pip
Write-Host "   Mise à jour de pip..." -ForegroundColor Gray
& $pythonExe -m pip install --upgrade pip --quiet

# Installer les dépendances depuis requirements.txt
$requirementsFile = Join-Path $appPath "server\requirements.txt"
if (Test-Path $requirementsFile) {
    Write-Host "   Installation des packages Python..." -ForegroundColor Gray
    & $pipExe install -r $requirementsFile --quiet
    if ($LASTEXITCODE -ne 0) {
        throw "Erreur lors de l'installation des packages Python"
    }
} else {
    Write-Host "   ⚠️  Fichier requirements.txt introuvable" -ForegroundColor Yellow
}

Write-Host "✅ Python configuré avec succès" -ForegroundColor Green
Write-Host ""

# =====================================================
# PACKAGES NODE.JS
# =====================================================

Write-Host "📦 Installation des packages Node.js..." -ForegroundColor Yellow

$clientPath = Join-Path $appPath "client"
if (Test-Path $clientPath) {
    Set-Location $clientPath
    
    Write-Host "   Installation via npm..." -ForegroundColor Gray
    npm install --silent --no-progress
    if ($LASTEXITCODE -ne 0) {
        throw "Erreur lors de l'installation des packages Node.js"
    }
    
    # Build du frontend pour production
    Write-Host "   Compilation du frontend..." -ForegroundColor Gray
    npm run build --silent
    if ($LASTEXITCODE -ne 0) {
        throw "Erreur lors de la compilation du frontend"
    }
    
    Set-Location $appPath
    Write-Host "✅ Frontend compilé avec succès" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  Dossier client introuvable" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "✅ Toutes les dépendances sont installées !" -ForegroundColor Green
