# Script de Création d'Archive de Distribution
# Usage: .\create-release.ps1 -Version "1.0.0"

param(
    [Parameter(Mandatory=$true)]
    [string]$Version,
    
    [switch]$SkipBuild
)

$ErrorActionPreference = "Stop"

Write-Host "🚀 Création de l'archive Homeflix v$Version" -ForegroundColor Cyan

# 1. Build du client (si non skip)
if (-not $SkipBuild) {
    Write-Host "`n📦 Build du client..." -ForegroundColor Yellow
    Set-Location client
    npm run build
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Erreur lors du build" -ForegroundColor Red
        exit 1
    }
    Set-Location ..
}

# 2. Créer le dossier de distribution
$distFolder = "homeflix-v$Version"
$distPath = ".\dist\$distFolder"

Write-Host "`n📁 Création du dossier de distribution..." -ForegroundColor Yellow
Remove-Item -Recurse -Force ".\dist" -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path $distPath -Force | Out-Null

# 3. Copier les fichiers nécessaires
Write-Host "`n📋 Copie des fichiers..." -ForegroundColor Yellow

# Client build
Copy-Item -Recurse ".\client\dist" "$distPath\client" -Force

# Electron
Copy-Item -Recurse ".\electron" "$distPath\electron" -Force
Remove-Item "$distPath\electron\dist" -Recurse -Force -ErrorAction SilentlyContinue

# Serveur (exclure fichiers de dev)
Copy-Item -Recurse ".\server" "$distPath\server" -Force
Remove-Item "$distPath\server\__pycache__" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "$distPath\server\*.log*" -Force -ErrorAction SilentlyContinue
Remove-Item "$distPath\server\test_*.py" -Force -ErrorAction SilentlyContinue
Remove-Item "$distPath\server\homeflix_dev.db" -Force -ErrorAction SilentlyContinue

# Scripts essentiels
Copy-Item ".\homeflix.ps1" "$distPath\" -Force
Copy-Item ".\INSTALLER.ps1" "$distPath\" -Force
Copy-Item ".\DESINSTALLER.ps1" "$distPath\" -Force
Copy-Item ".\generate-version.ps1" "$distPath\" -Force

# Scripts de déploiement (nécessaires)
New-Item -ItemType Directory -Path "$distPath\scripts" -Force | Out-Null
Copy-Item ".\scripts\deploy-client-electron.ps1" "$distPath\scripts\" -Force
Copy-Item ".\scripts\build-and-deploy.ps1" "$distPath\scripts\" -Force

# Configuration par défaut
Copy-Item ".\settings.yaml" "$distPath\settings.yaml.example" -Force

# Créer settings.yaml vide pour l'utilisateur
@"
# Configuration Homeflix
# Remplissez ce fichier après l'installation

tmdb:
  api_key: ""  # Obtenez votre clé sur https://www.themoviedb.org/settings/api

video_folders:
  # - "C:/Mes Videos/Films"
  # - "D:/Series"

video:
  use_transcode_by_default: false
  transcode_quality: "1080p"
  preferred_audio_language: "fr"
  preferred_subtitle_language: "fr"

resume:
  minimum_percent: 5
  maximum_percent: 90

server:
  host: "0.0.0.0"
  port: 8000
"@ | Out-File -FilePath "$distPath\settings.yaml" -Encoding UTF8

# Documentation
Copy-Item ".\README.md" "$distPath\" -Force
Copy-Item ".\GUIDE_UTILISATEUR.md" "$distPath\" -Force
Copy-Item ".\BUILD_PRODUCTION.md" "$distPath\BUILD_PRODUCTION.md" -Force
Copy-Item ".\LICENSE" "$distPath\" -Force
Copy-Item ".\CHANGELOG.md" "$distPath\" -Force

# Package.json root
Copy-Item ".\package.json" "$distPath\" -Force

# Créer dossiers vides pour données
New-Item -ItemType Directory -Path "$distPath\data\posters" -Force | Out-Null
New-Item -ItemType Directory -Path "$distPath\data\thumbs" -Force | Out-Null

# 4. Créer l'archive
Write-Host "`n📦 Création de l'archive ZIP..." -ForegroundColor Yellow
$archiveName = "homeflix-v$Version.zip"
$archivePath = ".\dist\$archiveName"

Compress-Archive -Path $distPath -DestinationPath $archivePath -Force

# 5. Statistiques
$archiveSize = (Get-Item $archivePath).Length / 1MB
Write-Host "`n✅ Archive créée avec succès !" -ForegroundColor Green
Write-Host "   📦 Fichier: $archiveName" -ForegroundColor Cyan
Write-Host "   📊 Taille: $([math]::Round($archiveSize, 2)) MB" -ForegroundColor Cyan
Write-Host "   📍 Emplacement: $(Resolve-Path $archivePath)" -ForegroundColor Cyan

# 6. Créer un fichier de vérification (checksum)
$hash = Get-FileHash $archivePath -Algorithm SHA256
$hash.Hash | Out-File -FilePath ".\dist\$archiveName.sha256" -Encoding UTF8

Write-Host "`n🔐 SHA256: $($hash.Hash)" -ForegroundColor Yellow

# 7. Résumé
Write-Host "`n📋 Contenu de la distribution:" -ForegroundColor Cyan
Get-ChildItem -Recurse $distPath | 
    Where-Object { -not $_.PSIsContainer } | 
    Group-Object Extension | 
    Select-Object Name, Count, @{Name="Size (MB)"; Expression={[math]::Round(($_.Group | Measure-Object Length -Sum).Sum / 1MB, 2)}} | 
    Format-Table -AutoSize

Write-Host "✨ Distribution prête pour la commercialisation !" -ForegroundColor Green
