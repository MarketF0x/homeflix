# Script de lancement Homeflix - Application Electron
# Ce script installe les dependances et lance l'application

Write-Host "Homeflix - Lancement de l'application..." -ForegroundColor Cyan

# Verifier si Node.js est installe
try {
    $nodeVersion = node --version
    Write-Host "OK Node.js detecte: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "ERREUR: Node.js n'est pas installe !" -ForegroundColor Red
    Write-Host "   Telechargez-le sur: https://nodejs.org/" -ForegroundColor Yellow
    Read-Host "Appuyez sur Entree pour quitter"
    exit 1
}

# Aller dans le dossier electron
$electronPath = Join-Path $PSScriptRoot "electron"

if (-not (Test-Path $electronPath)) {
    Write-Host "ERREUR: Dossier electron/ introuvable !" -ForegroundColor Red
    Read-Host "Appuyez sur Entree pour quitter"
    exit 1
}

Set-Location $electronPath

# Verifier si node_modules existe
if (-not (Test-Path "node_modules")) {
    Write-Host "Installation des dependances Electron..." -ForegroundColor Yellow
    npm install
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERREUR: Echec lors de l'installation !" -ForegroundColor Red
        Read-Host "Appuyez sur Entree pour quitter"
        exit 1
    }
}

# Verifier que Python est disponible
try {
    $pythonVersion = python --version
    Write-Host "OK Python detecte: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERREUR: Python n'est pas installe !" -ForegroundColor Red
    Read-Host "Appuyez sur Entree pour quitter"
    exit 1
}

# Lancer l'application Electron
Write-Host ""
Write-Host "Demarrage de Homeflix..." -ForegroundColor Cyan
Write-Host ""

npm start

# Si l'app se ferme, retour au dossier racine
Set-Location $PSScriptRoot
