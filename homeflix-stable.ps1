# Script de gestion de Homeflix - Version STABLE (Electron)
param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("start", "build", "rebuild", "status")]
    [string]$Action = "start"
)

$ErrorActionPreference = "Stop"

# Configuration
$STABLE_DIR = "$PSScriptRoot\homeflix-stable"
$ELECTRON_DIR = "$STABLE_DIR\electron"

# Couleurs
function Write-Info { param($msg) Write-Host "[INFO] $msg" -ForegroundColor Cyan }
function Write-Success { param($msg) Write-Host "[OK] $msg" -ForegroundColor Green }
function WriteError-Custom { param($msg) Write-Host "[ERREUR] $msg" -ForegroundColor Red }
function Write-Warning-Custom { param($msg) Write-Host "[ATTENTION] $msg" -ForegroundColor Yellow }

# Bannière
Write-Host ""
Write-Host "=========================================" -ForegroundColor Blue
Write-Host "  HOMEFLIX - VERSION STABLE (Electron)" -ForegroundColor Blue
Write-Host "=========================================" -ForegroundColor Blue
Write-Host ""

# Vérifier Node.js
function Test-NodeJS {
    try {
        $null = npm --version
        return $true
    }
    catch {
        WriteError-Custom "Node.js/npm non installe"
        Write-Info "Installez depuis: https://nodejs.org/"
        return $false
    }
}

# Construire la version STABLE
function New-StableVersion {
    Write-Info "Construction de la version STABLE..."
    
    # Créer le dossier stable
    if (-not (Test-Path $STABLE_DIR)) {
        Write-Info "Creation du dossier STABLE..."
        New-Item -ItemType Directory -Path $STABLE_DIR -Force | Out-Null
    }
    
    # Copier les fichiers
    Write-Info "Copie des fichiers..."
    
    # Server
    Write-Info "  - Server..."
    if (Test-Path "$PSScriptRoot\server") {
        # Copier le serveur SANS la base de données
        Copy-Item -Path "$PSScriptRoot\server" -Destination "$STABLE_DIR\server" -Recurse -Force -Exclude "homeflix.db","homeflix.db-shm","homeflix.db-wal"
        
        # Copier la base de données UNIQUEMENT si elle n'existe pas déjà dans STABLE
        # Cela permet de partager la même DB entre les deux versions
        $stableDb = "$STABLE_DIR\server\homeflix.db"
        $devDb = "$PSScriptRoot\server\homeflix.db"
        
        if (-not (Test-Path $stableDb) -and (Test-Path $devDb)) {
            Write-Info "  - Copie de la base de donnees partagee (premiere fois)..."
            Copy-Item -Path $devDb -Destination $stableDb -Force
            # Copier aussi les fichiers WAL si présents
            if (Test-Path "$PSScriptRoot\server\homeflix.db-shm") {
                Copy-Item -Path "$PSScriptRoot\server\homeflix.db-shm" -Destination "$STABLE_DIR\server\" -Force
            }
            if (Test-Path "$PSScriptRoot\server\homeflix.db-wal") {
                Copy-Item -Path "$PSScriptRoot\server\homeflix.db-wal" -Destination "$STABLE_DIR\server\" -Force
            }
        } else {
            Write-Info "  - Base de donnees deja presente (conservee)"
        }
    }
    
    # Client (sans node_modules et dist)
    Write-Info "  - Client..."
    if (Test-Path "$PSScriptRoot\client") {
        # Copier le dossier client
        if (Test-Path "$STABLE_DIR\client") {
            Remove-Item "$STABLE_DIR\client\node_modules" -Recurse -Force -ErrorAction SilentlyContinue
            Remove-Item "$STABLE_DIR\client\dist" -Recurse -Force -ErrorAction SilentlyContinue
        }
        Copy-Item -Path "$PSScriptRoot\client" -Destination "$STABLE_DIR\client" -Recurse -Force
    }
    
    # Electron
    Write-Info "  - Electron..."
    if (Test-Path "$PSScriptRoot\electron") {
        Copy-Item -Path "$PSScriptRoot\electron" -Destination "$STABLE_DIR\electron" -Recurse -Force
    }
    
    # Data
    if (Test-Path "$PSScriptRoot\data") {
        Write-Info "  - Data..."
        Copy-Item -Path "$PSScriptRoot\data" -Destination "$STABLE_DIR\data" -Recurse -Force
    }
    
    # settings.yaml
    if (Test-Path "$PSScriptRoot\settings.yaml") {
        Write-Info "  - Settings..."
        Copy-Item -Path "$PSScriptRoot\settings.yaml" -Destination "$STABLE_DIR\settings.yaml" -Force
    }
    
    Write-Success "Fichiers copies"
    
    # Builder le frontend
    Write-Info "Build du frontend React..."
    Push-Location "$STABLE_DIR\client"
    try {
        if (-not (Test-Path "node_modules")) {
            Write-Info "Installation dependances frontend..."
            npm install 2>&1 | Out-Null
        }
        npm run build 2>&1 | Out-Null
        Write-Success "Frontend build"
    }
    finally {
        Pop-Location
    }
    
    # Installer dépendances Electron
    Write-Info "Installation dependances Electron..."
    Push-Location $ELECTRON_DIR
    try {
        if (-not (Test-Path "node_modules")) {
            npm install 2>&1 | Out-Null
        }
        Write-Success "Dependances Electron installees"
    }
    finally {
        Pop-Location
    }
    
    Write-Success "Version STABLE construite!"
    Write-Info "Emplacement: $STABLE_DIR"
}

# Démarrer la version STABLE
function Start-StableVersion {
    if (-not (Test-Path $ELECTRON_DIR)) {
        Write-Warning-Custom "Version STABLE non trouvee"
        Write-Info "Construction en cours..."
        New-StableVersion
    }
    
    $distPath = "$STABLE_DIR\client\dist"
    if (-not (Test-Path $distPath)) {
        Write-Warning-Custom "Frontend non build"
        New-StableVersion
    }
    
    # SYNCHRONISER la base de donnees depuis DEV vers STABLE avant de demarrer
    Write-Info "Synchronisation de la base de donnees..."
    $devDb = "$PSScriptRoot\server\homeflix.db"
    $stableDb = "$STABLE_DIR\server\homeflix.db"
    
    if (Test-Path $devDb) {
        Copy-Item -Path $devDb -Destination $stableDb -Force
        # Copier aussi les fichiers WAL si présents
        if (Test-Path "$PSScriptRoot\server\homeflix.db-shm") {
            Copy-Item -Path "$PSScriptRoot\server\homeflix.db-shm" -Destination "$STABLE_DIR\server\" -Force
        }
        if (Test-Path "$PSScriptRoot\server\homeflix.db-wal") {
            Copy-Item -Path "$PSScriptRoot\server\homeflix.db-wal" -Destination "$STABLE_DIR\server\" -Force
        }
        Write-Success "Base de donnees synchronisee (comptes et profils a jour)"
    }
    
    Write-Info "Demarrage Homeflix STABLE (Electron)..."
    Write-Success "Application en cours de lancement"
    Write-Host ""
    
    Push-Location $ELECTRON_DIR
    try {
        npm start
    }
    finally {
        Pop-Location
    }
}

# Reconstruire
function Update-StableVersion {
    Write-Warning-Custom "Reconstruction complete..."
    
    if (Test-Path $STABLE_DIR) {
        Write-Info "Suppression ancienne version..."
        Remove-Item -Path $STABLE_DIR -Recurse -Force
    }
    
    New-StableVersion
    Write-Success "Reconstruction terminee!"
}

# Statut
function Get-StableStatus {
    Write-Info "Statut version STABLE:"
    Write-Host ""
    
    if (Test-Path $STABLE_DIR) {
        Write-Success "Version STABLE installee"
        Write-Info "Emplacement: $STABLE_DIR"
        
        if (Test-Path "$STABLE_DIR\client\dist") {
            Write-Success "Frontend build"
        } else {
            Write-Warning-Custom "Frontend non build"
        }
        
        if (Test-Path "$ELECTRON_DIR\node_modules") {
            Write-Success "Dependances Electron OK"
        } else {
            Write-Warning-Custom "Dependances Electron manquantes"
        }
    } else {
        Write-Warning-Custom "Version STABLE non installee"
        Write-Info "Utilisez: .\homeflix-stable.ps1 build"
    }
    
    Write-Host ""
}

# Main
if (-not (Test-NodeJS)) {
    exit 1
}

switch ($Action) {
    "start"   { Start-StableVersion }
    "build"   { New-StableVersion }
    "rebuild" { Update-StableVersion }
    "status"  { Get-StableStatus }
}

Write-Host ""
