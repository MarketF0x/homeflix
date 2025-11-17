# ============================================
# 🎬 HOMEFLIX - SCRIPT DE DÉMARRAGE UNIVERSEL
# ============================================
# Version: 2.0
# Date: 11 novembre 2025

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("production", "dev", "simple")]
    [string]$Mode = "",
    
    [Parameter(Mandatory=$false)]
    [switch]$Silent
)

$ErrorActionPreference = "Stop"
$projectRoot = $PSScriptRoot
$venvPython = "$projectRoot\.venv310\Scripts\python.exe"

# ============================================
# FONCTIONS UTILITAIRES
# ============================================

function Show-Banner {
    Clear-Host
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "     HOMEFLIX - DEMARRAGE" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
}

function Show-Menu {
    Write-Host "Selectionnez le mode de demarrage :" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  [1] Production (Recommande)" -ForegroundColor Green
    Write-Host "      - Demarrage robuste avec gestion des ports" -ForegroundColor Gray
    Write-Host "      - Logs en temps reel dans le terminal" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  [2] Developpement" -ForegroundColor Cyan
    Write-Host "      - Rechargement automatique des modifications" -ForegroundColor Gray
    Write-Host "      - Arret automatique au Ctrl+C" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  [3] Simple (Fenetres separees)" -ForegroundColor Magenta
    Write-Host "      - Backend et Frontend dans des fenetres distinctes" -ForegroundColor Gray
    Write-Host "      - Facile a arreter individuellement" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  [Q] Quitter" -ForegroundColor Red
    Write-Host ""
    
    $choice = Read-Host "Votre choix"
    return $choice
}

function Test-Environment {
    Write-Host "Verification de l'environnement..." -ForegroundColor Yellow
    
    # Verification Python
    if (-not (Test-Path $venvPython)) {
        Write-Host "ERREUR : Environnement virtuel Python introuvable" -ForegroundColor Red
        Write-Host "Chemin attendu : $venvPython" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Solution : Lancez d'abord .\install.ps1" -ForegroundColor Cyan
        exit 1
    }
    
    # Verification Node.js
    $nodeVersion = & node --version 2>$null
    if (-not $nodeVersion) {
        Write-Host "ATTENTION : Node.js non detecte" -ForegroundColor Yellow
        Write-Host "Le frontend ne pourra pas demarrer" -ForegroundColor Yellow
        $continue = Read-Host "Continuer quand meme ? (O/N)"
        if ($continue -ne "O") { exit 0 }
    }
    
    # Verification client
    if (-not (Test-Path "$projectRoot\client\package.json")) {
        Write-Host "ERREUR : Dossier client introuvable" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "Environnement OK" -ForegroundColor Green
    Write-Host ""
}

function Clear-Port {
    param([int]$Port)
    
    Write-Host "Liberation du port $Port..." -ForegroundColor Yellow
    $maxAttempts = 10
    $attempt = 0
    
    while ($attempt -lt $maxAttempts) {
        $attempt++
        $connection = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
        
        if (-not $connection) {
            Write-Host "  Port $Port libre" -ForegroundColor Green
            return $true
        }
        
        $processId = $connection.OwningProcess
        if ($processId -gt 0) {
            Write-Host "  Tentative $attempt : Arret du processus $processId..." -ForegroundColor Gray
            Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
            Start-Sleep -Seconds 1
        } else {
            Write-Host "  Processus systeme, attente..." -ForegroundColor Yellow
            Start-Sleep -Seconds 2
        }
    }
    
    Write-Host "  Impossible de liberer le port $Port" -ForegroundColor Red
    return $false
}

function Clear-Processes {
    Write-Host "Nettoyage des processus..." -ForegroundColor Yellow
    
    Get-Job | Stop-Job -ErrorAction SilentlyContinue
    Get-Job | Remove-Job -ErrorAction SilentlyContinue
    Get-Process -Name node,python -ErrorAction SilentlyContinue | 
        Where-Object { $_.Path -like "*homeflix*" } | 
        Stop-Process -Force -ErrorAction SilentlyContinue
    
    Start-Sleep -Seconds 2
    Write-Host "Nettoyage termine" -ForegroundColor Green
    Write-Host ""
}

# ============================================
# MODES DE DÉMARRAGE
# ============================================

function Start-Production {
    Write-Host "Demarrage en mode PRODUCTION" -ForegroundColor Green
    Write-Host ""
    
    Clear-Processes
    
    # Liberation des ports
    if (-not (Clear-Port 5173)) { exit 1 }
    if (-not (Clear-Port 8000)) { exit 1 }
    
    Write-Host ""
    Write-Host "Demarrage des serveurs..." -ForegroundColor Cyan
    Write-Host ""
    
    # Migration de la base de données (profils)
    Write-Host "  Migration de la base de donnees..." -ForegroundColor Cyan
    try {
        & "$venvPython" "$projectRoot\server\migrate_profiles.py" 2>&1 | Out-Null
        Write-Host "    Migration terminee" -ForegroundColor Green
    } catch {
        Write-Host "    Avertissement: Migration echouee (peut etre deja executee)" -ForegroundColor Yellow
    }
    Write-Host ""
    
    # Demarrer le Backend en arrière-plan (sans fenêtre)
    Write-Host "  Backend (FastAPI)..." -ForegroundColor Cyan
    Write-Host "    Activation de l'environnement virtuel..." -ForegroundColor Gray
    
    # ✅ ACTIVATION DU VENV AVANT DE LANCER LE SERVEUR
    $backendStartInfo = New-Object System.Diagnostics.ProcessStartInfo
    $backendStartInfo.FileName = "powershell.exe"
    $backendStartInfo.Arguments = "-NoProfile -Command `"& '$projectRoot\.venv310\Scripts\Activate.ps1'; python server/main.py`""
    $backendStartInfo.WorkingDirectory = $projectRoot
    $backendStartInfo.UseShellExecute = $false
    $backendStartInfo.CreateNoWindow = $true
    $backendStartInfo.WindowStyle = [System.Diagnostics.ProcessWindowStyle]::Hidden
    $backendProcess = [System.Diagnostics.Process]::Start($backendStartInfo)
    Write-Host "    Backend demarre avec venv310 (PID: $($backendProcess.Id))" -ForegroundColor Green
    
    Start-Sleep -Seconds 4
    
    # Demarrer le Frontend en arrière-plan (sans fenêtre)
    Write-Host "  Frontend (Vite)..." -ForegroundColor Cyan
    $frontendStartInfo = New-Object System.Diagnostics.ProcessStartInfo
    $frontendStartInfo.FileName = "cmd.exe"
    $frontendStartInfo.Arguments = "/c npm run dev"
    $frontendStartInfo.WorkingDirectory = "$projectRoot\client"
    $frontendStartInfo.UseShellExecute = $false
    $frontendStartInfo.CreateNoWindow = $true
    $frontendStartInfo.WindowStyle = [System.Diagnostics.ProcessWindowStyle]::Hidden
    $frontendProcess = [System.Diagnostics.Process]::Start($frontendStartInfo)
    Write-Host "    Frontend demarre (PID: $($frontendProcess.Id))" -ForegroundColor Green
    
    Start-Sleep -Seconds 5
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "   HOMEFLIX DEMARRE !" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "  Interface  : http://localhost:5173" -ForegroundColor Cyan
    Write-Host "  API        : http://localhost:8000" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Les serveurs tournent en arriere-plan (aucune fenetre visible)." -ForegroundColor Yellow
    Write-Host "Pour les arreter, utilisez le Gestionnaire des taches ou fermez tous les processus Python/Node." -ForegroundColor Gray
    Write-Host ""
    
    # Proposer d'ouvrir le navigateur (sauf en mode silencieux)
    if (-not $Silent) {
        $openBrowser = Read-Host "Ouvrir dans le navigateur ? (O/N)"
        if ($openBrowser -eq "O") {
            Start-Sleep -Seconds 3
            Start-Process "http://localhost:5173"
        }
    } else {
        # En mode silencieux, ouvrir automatiquement le navigateur après 3 secondes
        Start-Sleep -Seconds 3
        Start-Process "http://localhost:5173"
    }
    
    Write-Host ""
    Write-Host "Les serveurs continuent de tourner en arriere-plan." -ForegroundColor Green
    
    if (-not $Silent) {
        Write-Host "Vous pouvez fermer cette fenetre en toute securite." -ForegroundColor Gray
    }
}

function Start-Development {
    Write-Host "Demarrage en mode DEVELOPPEMENT" -ForegroundColor Cyan
    Write-Host ""
    
    # Nettoyage rapide
    if (Test-Path "$projectRoot\scripts\cleanup-dev.ps1") {
        & "$projectRoot\scripts\cleanup-dev.ps1" -Silent -Ports @(5173,5174,8000) 2>$null | Out-Null
    }
    
    Write-Host "Demarrage des serveurs..." -ForegroundColor Cyan
    Write-Host ""
    
    # Migration de la base de données (profils)
    Write-Host "  Migration de la base de donnees..." -ForegroundColor Cyan
    try {
        & "$venvPython" "$projectRoot\server\migrate_profiles.py" 2>&1 | Out-Null
        Write-Host "    Migration terminee" -ForegroundColor Green
    } catch {
        Write-Host "    Avertissement: Migration echouee" -ForegroundColor Yellow
    }
    Write-Host ""
    
    # Demarrer le Backend
    Write-Host "  Backend (mode developpement)..." -ForegroundColor Cyan
    Write-Host "    Activation de l'environnement virtuel..." -ForegroundColor Gray
    
    # ✅ ACTIVATION DU VENV AVANT DE LANCER LE SERVEUR (mode dev)
    $serverProc = Start-Process -FilePath "powershell.exe" -ArgumentList "-NoProfile -Command `"& '$projectRoot\.venv310\Scripts\Activate.ps1'; python server/main.py`"" -WorkingDirectory $projectRoot -PassThru -WindowStyle Hidden
    Write-Host "    Backend demarre avec venv310" -ForegroundColor Green
    
    Start-Sleep -Seconds 3
    
    # Demarrer le Frontend
    Write-Host "  Frontend (hot reload active)..." -ForegroundColor Cyan
    Push-Location "$projectRoot\client"
    $env:VITE_PORT = "5173"
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "   MODE DEVELOPPEMENT ACTIF" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "  Interface : http://localhost:5173" -ForegroundColor Cyan
    Write-Host "  API       : http://localhost:8000" -ForegroundColor Cyan
    Write-Host "  Hot Reload : ACTIVE" -ForegroundColor Green
    Write-Host ""
    
    try {
        npm run dev
    } finally {
        Pop-Location
        Write-Host ""
        Write-Host "Arret en cours..." -ForegroundColor Yellow
        if ($serverProc -and -not $serverProc.HasExited) {
            Stop-Process -Id $serverProc.Id -Force -ErrorAction SilentlyContinue
        }
        if (Test-Path "$projectRoot\scripts\cleanup-dev.ps1") {
            & "$projectRoot\scripts\cleanup-dev.ps1" -Silent -Ports @(5173,5174,8000) 2>$null | Out-Null
        }
        Write-Host "Arret termine" -ForegroundColor Green
    }
}

function Start-Simple {
    Write-Host "Demarrage en mode SIMPLE (fenetres separees)" -ForegroundColor Magenta
    Write-Host ""
    
    Clear-Processes
    
    # Migration de la base de données (profils)
    Write-Host "  Migration de la base de donnees..." -ForegroundColor Cyan
    try {
        & "$venvPython" "$projectRoot\server\migrate_profiles.py" 2>&1 | Out-Null
        Write-Host "    Migration terminee" -ForegroundColor Green
    } catch {
        Write-Host "    Avertissement: Migration echouee" -ForegroundColor Yellow
    }
    Write-Host ""
    
    Write-Host "Ouverture des fenetres..." -ForegroundColor Cyan
    Write-Host ""
    
    # Backend dans une nouvelle fenetre
    Write-Host "  Ouverture Backend..." -ForegroundColor Cyan
    # ✅ ACTIVATION DU VENV AVANT DE LANCER LE SERVEUR (mode simple)
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$projectRoot'; Write-Host 'HOMEFLIX BACKEND' -ForegroundColor Green; Write-Host ''; Write-Host 'Activation venv310...' -ForegroundColor Gray; & '.\.venv310\Scripts\Activate.ps1'; python server\main.py"
    
    Start-Sleep -Seconds 4
    
    # Frontend dans une nouvelle fenetre
    Write-Host "  Ouverture Frontend..." -ForegroundColor Cyan
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$projectRoot\client'; Write-Host 'HOMEFLIX FRONTEND' -ForegroundColor Cyan; Write-Host ''; npm run dev"
    
    Start-Sleep -Seconds 3
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "   HOMEFLIX DEMARRE !" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "  Interface : http://localhost:5173" -ForegroundColor Cyan
    Write-Host "  API       : http://localhost:8000" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Les serveurs tournent dans des fenetres separees" -ForegroundColor Yellow
    Write-Host "Fermez chaque fenetre pour arreter le serveur correspondant" -ForegroundColor Gray
    Write-Host ""
    
    # Proposer d'ouvrir le navigateur
    $openBrowser = Read-Host "Ouvrir dans le navigateur ? (O/N)"
    if ($openBrowser -eq "O") {
        Start-Sleep -Seconds 2
        Start-Process "http://localhost:5173"
    }
}

# ============================================
# PROGRAMME PRINCIPAL
# ============================================

Show-Banner
Test-Environment

# Si le mode est passé en paramètre, l'utiliser directement
if ($Mode) {
    switch ($Mode.ToLower()) {
        "production" { Start-Production }
        "dev" { Start-Development }
        "simple" { Start-Simple }
    }
    exit 0
}

# Sinon, afficher le menu
while ($true) {
    $choice = Show-Menu
    
    switch ($choice) {
        "1" { 
            Start-Production
            break
        }
        "2" { 
            Start-Development
            break
        }
        "3" { 
            Start-Simple
            break
        }
        "Q" { 
            Write-Host "Au revoir !" -ForegroundColor Cyan
            exit 0
        }
        default { 
            Write-Host "Choix invalide, reessayez" -ForegroundColor Red
            Start-Sleep -Seconds 1
            Show-Banner
        }
    }
}
