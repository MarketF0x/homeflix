# 🎬 INSTALLATION HOMEFLIX
# Script d'installation rapide pour Windows
# Exécuter avec: .\INSTALLER.ps1

Write-Host ""
Write-Host "╔════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                                        ║" -ForegroundColor Cyan
Write-Host "║           🎬 HOMEFLIX 2.0             ║" -ForegroundColor Cyan
Write-Host "║   Installation de votre serveur de    ║" -ForegroundColor Cyan
Write-Host "║         streaming personnel            ║" -ForegroundColor Cyan
Write-Host "║                                        ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

$projectRoot = $PSScriptRoot

# Vérifier que le script détaillé existe
$fullInstaller = Join-Path $projectRoot ".scripts\install.ps1"
if (-not (Test-Path $fullInstaller)) {
    Write-Host "❌ Erreur: Fichier d'installation introuvable" -ForegroundColor Red
    Write-Host "   Chemin attendu: $fullInstaller" -ForegroundColor Yellow
    exit 1
}

Write-Host "🚀 Lancement de l'installation complète..." -ForegroundColor Green
Write-Host ""
Start-Sleep -Seconds 1

# Appeler le script d'installation complet
& $fullInstaller

Write-Host ""
Write-Host "═══════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "Installation terminée!" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "📖 Consultez README.md pour démarrer" -ForegroundColor White
Write-Host ""
