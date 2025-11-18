# Script de Creation d'Archive de Distribution
# Usage: .\create-release-clean.ps1 -Version "1.0.0"

param(
    [Parameter(Mandatory=$true)]
    [string]$Version,
    
    [switch]$SkipBuild
)

$ErrorActionPreference = "Stop"

Write-Host "Creation de l'archive Homeflix v$Version" -ForegroundColor Cyan

# 1. Build du client (si non skip)
if (-not $SkipBuild) {
    Write-Host "`nBuild du client..." -ForegroundColor Yellow
    Set-Location client
    npm run build
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Erreur lors du build" -ForegroundColor Red
        exit 1
    }
    Set-Location ..
}

# 2. Creer le dossier de distribution
$distFolder = "homeflix-v$Version"
$distPath = ".\dist\$distFolder"

Write-Host "`nCreation du dossier de distribution..." -ForegroundColor Yellow
Remove-Item -Recurse -Force ".\dist" -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path $distPath -Force | Out-Null

# 3. Copier les fichiers necessaires
Write-Host "`nCopie des fichiers..." -ForegroundColor Yellow

# Client build
Write-Host "  - Client (build optimise)"
Copy-Item -Recurse ".\client\dist" "$distPath\client" -Force

# Electron
Write-Host "  - Electron"
Copy-Item -Recurse ".\electron" "$distPath\electron" -Force
Remove-Item "$distPath\electron\dist" -Recurse -Force -ErrorAction SilentlyContinue

# Serveur (exclure fichiers de dev)
Write-Host "  - Serveur"
Copy-Item -Recurse ".\server" "$distPath\server" -Force
Remove-Item "$distPath\server\__pycache__" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "$distPath\server\*.log*" -Force -ErrorAction SilentlyContinue
Remove-Item "$distPath\server\test_*.py" -Force -ErrorAction SilentlyContinue
Remove-Item "$distPath\server\homeflix_dev.db" -Force -ErrorAction SilentlyContinue

# Scripts de lancement
Write-Host "  - Scripts"
Copy-Item ".\homeflix.ps1" "$distPath\" -Force
Copy-Item ".\homeflix-stable.ps1" "$distPath\" -Force

# Settings
Write-Host "  - Configuration"
@"
# Configuration Homeflix
version: $Version
port: 8000
host: 127.0.0.1
media_folder: ./videos
database: homeflix.db
"@ | Out-File -FilePath "$distPath\settings.yaml" -Encoding UTF8

# Documentation
Write-Host "  - Documentation"
Copy-Item ".\docs\README.md" "$distPath\README.md" -Force
Copy-Item ".\docs\LANCEMENT.md" "$distPath\" -Force
Copy-Item ".\docs\GUIDE_UTILISATEUR.md" "$distPath\" -Force
Copy-Item ".\docs\FAQ.md" "$distPath\" -Force
Copy-Item ".\LICENSE" "$distPath\" -Force
Copy-Item ".\CHANGELOG.md" "$distPath\" -Force

# Package.json root
Copy-Item ".\package.json" "$distPath\" -Force

# Creer dossiers vides pour donnees
New-Item -ItemType Directory -Path "$distPath\data\posters" -Force | Out-Null
New-Item -ItemType Directory -Path "$distPath\data\thumbs" -Force | Out-Null

# 4. Creer l'archive
Write-Host "`nCreation de l'archive ZIP..." -ForegroundColor Yellow
$archiveName = "homeflix-v$Version"
$archivePath = ".\dist\$archiveName.zip"

Compress-Archive -Path $distPath -DestinationPath $archivePath -Force

# 5. Calculer le hash
Write-Host "`nCalcul du hash SHA256..." -ForegroundColor Yellow
$hash = Get-FileHash -Path $archivePath -Algorithm SHA256
$hash.Hash | Out-File -FilePath ".\dist\$archiveName.sha256" -Encoding ASCII

# 6. Afficher les resultats
Write-Host "`n========================================" -ForegroundColor Green
Write-Host "Archive creee avec succes !" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "`nFichier: $archivePath"
Write-Host "Taille: $([math]::Round((Get-Item $archivePath).Length / 1MB, 2)) MB"
Write-Host "SHA256: $($hash.Hash)"
Write-Host "`nHash sauvegarde dans: .\dist\$archiveName.sha256"
Write-Host "`nDistribution prete pour la commercialisation !" -ForegroundColor Green
