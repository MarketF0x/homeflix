# Script de demarrage de Homeflix - Version DEV
param(
    [switch]$SkipCleanup
)

$ErrorActionPreference = "Stop"

# Couleurs
function Write-Info { param($msg) Write-Host "[INFO] $msg" -ForegroundColor Cyan }
function Write-Success { param($msg) Write-Host "[OK] $msg" -ForegroundColor Green }
function WriteError-Custom { param($msg) Write-Host "[ERREUR] $msg" -ForegroundColor Red }
function Write-Warning-Custom { param($msg) Write-Host "[ATTENTION] $msg" -ForegroundColor Yellow }

# Bannière
Write-Host ""
Write-Host "=========================================" -ForegroundColor Magenta
Write-Host "  HOMEFLIX - VERSION DEVELOPPEMENT" -ForegroundColor Magenta
Write-Host "=========================================" -ForegroundColor Magenta
Write-Host ""
Write-Warning-Custom "Mode DEV - Modifications en temps reel"
Write-Host ""

# Nettoyage optionnel
if (-not $SkipCleanup) {
    Write-Info "Nettoyage de l environnement..."
    & "$PSScriptRoot\scripts\cleanup-dev.ps1" -Silent
    Start-Sleep -Seconds 1
}

# Demarrer le backend
Write-Info "Demarrage du serveur backend (Python/FastAPI)..."
$backendPath = Join-Path $PSScriptRoot "server"
$venvPath = Join-Path $PSScriptRoot ".venv310\Scripts\Activate.ps1"

Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "& '$venvPath'; cd '$backendPath'; python main.py"
) -WindowStyle Normal

Start-Sleep -Seconds 3

# Demarrer le frontend
Write-Info "Demarrage du serveur frontend (Vite)..."
$clientPath = Join-Path $PSScriptRoot "client"

Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd '$clientPath'; npm run dev"
) -WindowStyle Normal

Start-Sleep -Seconds 2

Write-Success "Homeflix DEV en cours de demarrage..."
Write-Host ""
Write-Info "Frontend DEV: http://localhost:5173"
Write-Info "Backend API: http://localhost:8000"
Write-Host ""
Write-Warning-Custom "Les serveurs s executent dans des fenetres separees"
Write-Info "Fermez les fenetres pour arreter les serveurs"
Write-Host ""
