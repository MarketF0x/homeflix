# ============================================
# 🔄 MISE À JOUR HOMEFLIX - SYSTÈME DE PROFILS
# ============================================
# Ce script met à jour Homeflix avec la nouvelle fonctionnalité de gestion des profils

param(
    [Parameter(Mandatory=$false)]
    [switch]$Silent
)

$ErrorActionPreference = "Stop"
$projectRoot = $PSScriptRoot
$venvPython = "$projectRoot\.venv310\Scripts\python.exe"

function Show-Banner {
    if (-not $Silent) {
        Clear-Host
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host "  MISE À JOUR HOMEFLIX - PROFILS" -ForegroundColor Cyan
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host ""
    }
}

function Test-VirtualEnv {
    if (-not (Test-Path $venvPython)) {
        Write-Host "❌ Environnement virtuel Python introuvable!" -ForegroundColor Red
        Write-Host "   Veuillez executer .\install.ps1 d'abord" -ForegroundColor Yellow
        exit 1
    }
}

function Stop-Servers {
    Write-Host "1. Arrêt des serveurs en cours..." -ForegroundColor Yellow
    
    Get-Process -Name node,python -ErrorAction SilentlyContinue | 
        Where-Object { $_.Path -like "*homeflix*" } | 
        Stop-Process -Force -ErrorAction SilentlyContinue
    
    Get-Job | Stop-Job -ErrorAction SilentlyContinue
    Get-Job | Remove-Job -ErrorAction SilentlyContinue
    
    Start-Sleep -Seconds 2
    Write-Host "   ✓ Serveurs arrêtés" -ForegroundColor Green
    Write-Host ""
}

function Update-Database {
    Write-Host "2. Mise à jour de la base de données..." -ForegroundColor Yellow
    
    try {
        $output = & "$venvPython" "$projectRoot\server\migrate_profiles.py" 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✓ Migration réussie" -ForegroundColor Green
            if (-not $Silent) {
                $output | ForEach-Object { Write-Host "     $_" -ForegroundColor Gray }
            }
        } else {
            throw "Code de sortie: $LASTEXITCODE"
        }
    } catch {
        Write-Host "   ⚠ Avertissement: La migration a échoué" -ForegroundColor Yellow
        Write-Host "     Cela peut signifier que la table existe déjà" -ForegroundColor Gray
        Write-Host "     Erreur: $_" -ForegroundColor Red
    }
    Write-Host ""
}

function Verify-Avatars {
    Write-Host "3. Vérification des avatars..." -ForegroundColor Yellow
    
    $avatarPath = "$projectRoot\client\public\avatars"
    
    if (-not (Test-Path $avatarPath)) {
        Write-Host "   ⚠ Dossier avatars manquant!" -ForegroundColor Red
        Write-Host "     Les avatars ne s'afficheront pas correctement" -ForegroundColor Yellow
        Write-Host ""
        return
    }
    
    $avatarFiles = Get-ChildItem -Path $avatarPath -Filter "*.svg"
    $expectedCount = 12
    
    if ($avatarFiles.Count -eq $expectedCount) {
        Write-Host "   ✓ Tous les avatars sont présents ($expectedCount fichiers)" -ForegroundColor Green
    } else {
        Write-Host "   ⚠ Avatars incomplets: $($avatarFiles.Count)/$expectedCount fichiers" -ForegroundColor Yellow
    }
    Write-Host ""
}

function Show-Summary {
    if (-not $Silent) {
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "  MISE À JOUR TERMINÉE !" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "📋 Nouvelles fonctionnalités disponibles :" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "  ✓ Gestion des profils utilisateurs" -ForegroundColor White
        Write-Host "  ✓ 12 avatars personnalisés (personnages et formes)" -ForegroundColor White
        Write-Host "  ✓ Restrictions par profil (mode enfants, etc.)" -ForegroundColor White
        Write-Host "  ✓ Changement de profil à la volée" -ForegroundColor White
        Write-Host ""
        Write-Host "📖 Documentation :" -ForegroundColor Cyan
        Write-Host "   Consultez GUIDE_PROFILS.md pour plus de détails" -ForegroundColor Gray
        Write-Host ""
        Write-Host "🚀 Démarrage :" -ForegroundColor Cyan
        Write-Host "   .\start-homeflix.ps1 -Mode production" -ForegroundColor White
        Write-Host ""
        Write-Host "Au premier lancement, vous verrez l'écran de sélection" -ForegroundColor Gray
        Write-Host "de profils avec le profil principal déjà créé." -ForegroundColor Gray
        Write-Host ""
    }
}

# ============================================
# EXÉCUTION PRINCIPALE
# ============================================

Show-Banner
Test-VirtualEnv
Stop-Servers
Update-Database
Verify-Avatars
Show-Summary

if (-not $Silent) {
    Write-Host "Appuyez sur une touche pour continuer..." -ForegroundColor Yellow
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}
