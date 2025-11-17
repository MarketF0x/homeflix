# 🗑️ DÉSINSTALLATION HOMEFLIX
# Script de désinstallation complète
# Exécuter avec: .\DESINSTALLER.ps1

param(
    [Parameter(Mandatory=$false)]
    [switch]$KeepData,
    [switch]$Force
)

Write-Host ""
Write-Host "╔════════════════════════════════════════╗" -ForegroundColor Red
Write-Host "║                                        ║" -ForegroundColor Red
Write-Host "║     🗑️  DÉSINSTALLATION HOMEFLIX      ║" -ForegroundColor Red
Write-Host "║                                        ║" -ForegroundColor Red
Write-Host "╚════════════════════════════════════════╝" -ForegroundColor Red
Write-Host ""

$projectRoot = $PSScriptRoot

# Fonction pour arrêter les serveurs
function Stop-HomeflixServers {
    Write-Host "🛑 Arrêt des serveurs Homeflix..." -ForegroundColor Yellow
    
    # Arrêter les processus Python (backend)
    $pythonProcesses = Get-Process -Name python -ErrorAction SilentlyContinue | 
        Where-Object { $_.Path -like "*$projectRoot*" }
    
    if ($pythonProcesses) {
        $pythonProcesses | Stop-Process -Force -ErrorAction SilentlyContinue
        Write-Host "   ✓ Backend arrêté" -ForegroundColor Gray
    }
    
    # Arrêter les processus Node (frontend)
    $nodeProcesses = Get-Process -Name node -ErrorAction SilentlyContinue | 
        Where-Object { $_.Path -like "*$projectRoot*" -or $_.CommandLine -like "*$projectRoot*" }
    
    if ($nodeProcesses) {
        $nodeProcesses | Stop-Process -Force -ErrorAction SilentlyContinue
        Write-Host "   ✓ Frontend arrêté" -ForegroundColor Gray
    }
    
    # Libérer les ports
    $ports = @(8000, 5173)
    foreach ($port in $ports) {
        $connection = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
        if ($connection) {
            $processId = $connection.OwningProcess
            Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
            Write-Host "   ✓ Port $port libéré" -ForegroundColor Gray
        }
    }
    
    Start-Sleep -Seconds 2
    Write-Host "   ✅ Serveurs arrêtés" -ForegroundColor Green
    Write-Host ""
}

# Fonction pour supprimer les raccourcis
function Remove-Shortcuts {
    Write-Host "🔗 Suppression des raccourcis..." -ForegroundColor Yellow
    
    $desktop = [Environment]::GetFolderPath("Desktop")
    $shortcuts = @(
        "$desktop\Homeflix.lnk",
        "$desktop\HomeOne.lnk"
    )
    
    $removed = 0
    foreach ($shortcut in $shortcuts) {
        if (Test-Path $shortcut) {
            Remove-Item $shortcut -Force -ErrorAction SilentlyContinue
            $removed++
        }
    }
    
    if ($removed -gt 0) {
        Write-Host "   ✓ $removed raccourci(s) supprimé(s)" -ForegroundColor Gray
    } else {
        Write-Host "   ℹ Aucun raccourci trouvé" -ForegroundColor Gray
    }
    Write-Host ""
}

# Fonction pour nettoyer les règles de pare-feu
function Remove-FirewallRules {
    Write-Host "🔥 Suppression des règles de pare-feu..." -ForegroundColor Yellow
    
    $ruleNames = @(
        "Homeflix Backend",
        "Homeflix Frontend",
        "HomeOne Backend",
        "HomeOne Frontend"
    )
    
    $removed = 0
    foreach ($ruleName in $ruleNames) {
        $rule = Get-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue
        if ($rule) {
            Remove-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue
            $removed++
        }
    }
    
    if ($removed -gt 0) {
        Write-Host "   ✓ $removed règle(s) de pare-feu supprimée(s)" -ForegroundColor Gray
    } else {
        Write-Host "   ℹ Aucune règle de pare-feu trouvée" -ForegroundColor Gray
    }
    Write-Host ""
}

# Fonction pour afficher ce qui sera supprimé
function Show-RemovalPreview {
    Write-Host "📋 Éléments qui seront supprimés :" -ForegroundColor Cyan
    Write-Host ""
    
    # Environnements virtuels Python
    $venvs = @(".venv", ".venv310")
    foreach ($venv in $venvs) {
        if (Test-Path "$projectRoot\$venv") {
            $size = (Get-ChildItem "$projectRoot\$venv" -Recurse -File | 
                Measure-Object -Property Length -Sum).Sum / 1MB
            Write-Host "   📁 $venv ($('{0:N0}' -f $size) MB)" -ForegroundColor Gray
        }
    }
    
    # Node modules
    if (Test-Path "$projectRoot\client\node_modules") {
        $size = (Get-ChildItem "$projectRoot\client\node_modules" -Recurse -File | 
            Measure-Object -Property Length -Sum).Sum / 1MB
        Write-Host "   📁 client\node_modules ($('{0:N0}' -f $size) MB)" -ForegroundColor Gray
    }
    
    # Fichiers générés
    $generatedDirs = @("data\thumbs", "data\posters", "server\__pycache__")
    foreach ($dir in $generatedDirs) {
        if (Test-Path "$projectRoot\$dir") {
            Write-Host "   📁 $dir" -ForegroundColor Gray
        }
    }
    
    # Base de données (si pas KeepData)
    if (-not $KeepData) {
        if (Test-Path "$projectRoot\data\homeflix.db") {
            $size = (Get-Item "$projectRoot\data\homeflix.db").Length / 1MB
            Write-Host "   🗃️  data\homeflix.db ($('{0:N2}' -f $size) MB)" -ForegroundColor Yellow
        }
    }
    
    Write-Host ""
}

# DÉBUT DE LA DÉSINSTALLATION

# Vérification des droits administrateur pour le pare-feu
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $Force) {
    Write-Host "⚠️  ATTENTION : Cette opération va désinstaller Homeflix" -ForegroundColor Yellow
    Write-Host ""
    
    Show-RemovalPreview
    
    if ($KeepData) {
        Write-Host "✓ Mode conservation des données activé" -ForegroundColor Green
        Write-Host "  → La base de données et les vidéos seront conservées" -ForegroundColor Gray
    } else {
        Write-Host "⚠️  Mode suppression complète" -ForegroundColor Red
        Write-Host "  → La base de données sera supprimée définitivement" -ForegroundColor Gray
    }
    Write-Host ""
    
    Write-Host "Voulez-vous continuer ? (O/N) " -ForegroundColor Yellow -NoNewline
    $confirmation = Read-Host
    
    if ($confirmation -ne 'O' -and $confirmation -ne 'o') {
        Write-Host ""
        Write-Host "❌ Désinstallation annulée" -ForegroundColor Red
        exit 0
    }
}

Write-Host ""
Write-Host "🔄 Désinstallation en cours..." -ForegroundColor Cyan
Write-Host ""

# 1. Arrêter les serveurs
Stop-HomeflixServers

# 2. Supprimer les raccourcis
Remove-Shortcuts

# 3. Supprimer les règles de pare-feu (si admin)
if ($isAdmin) {
    Remove-FirewallRules
} else {
    Write-Host "⚠️  Règles de pare-feu non supprimées (droits admin requis)" -ForegroundColor Yellow
    Write-Host "   Exécutez en tant qu'administrateur pour les supprimer" -ForegroundColor Gray
    Write-Host ""
}

# 4. Supprimer les environnements virtuels Python
Write-Host "🐍 Suppression des environnements Python..." -ForegroundColor Yellow
$venvs = @(".venv", ".venv310")
foreach ($venv in $venvs) {
    $venvPath = "$projectRoot\$venv"
    if (Test-Path $venvPath) {
        Remove-Item $venvPath -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "   ✓ $venv supprimé" -ForegroundColor Gray
    }
}
Write-Host ""

# 5. Supprimer node_modules
Write-Host "📦 Suppression des dépendances Node.js..." -ForegroundColor Yellow
$nodeModulesPath = "$projectRoot\client\node_modules"
if (Test-Path $nodeModulesPath) {
    Remove-Item $nodeModulesPath -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "   ✓ node_modules supprimé" -ForegroundColor Gray
} else {
    Write-Host "   ℹ node_modules déjà absent" -ForegroundColor Gray
}
Write-Host ""

# 6. Supprimer les fichiers générés
Write-Host "🧹 Nettoyage des fichiers générés..." -ForegroundColor Yellow
$generatedDirs = @(
    "data\thumbs",
    "data\posters",
    "server\__pycache__",
    "client\dist",
    ".homeflix.lock"
)

foreach ($dir in $generatedDirs) {
    $fullPath = "$projectRoot\$dir"
    if (Test-Path $fullPath) {
        Remove-Item $fullPath -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "   ✓ $dir supprimé" -ForegroundColor Gray
    }
}
Write-Host ""

# 7. Supprimer la base de données (si demandé)
if (-not $KeepData) {
    Write-Host "🗃️  Suppression de la base de données..." -ForegroundColor Yellow
    $dbPath = "$projectRoot\data\homeflix.db"
    if (Test-Path $dbPath) {
        Remove-Item $dbPath -Force -ErrorAction SilentlyContinue
        Write-Host "   ✓ Base de données supprimée" -ForegroundColor Gray
    }
    
    # Supprimer aussi les fichiers de backup
    Get-ChildItem "$projectRoot\data" -Filter "*.db-*" | Remove-Item -Force -ErrorAction SilentlyContinue
    Write-Host ""
} else {
    Write-Host "💾 Conservation de la base de données..." -ForegroundColor Green
    Write-Host "   ℹ Les données sont conservées dans data\" -ForegroundColor Gray
    Write-Host ""
}

# 8. Résumé final
Write-Host ""
Write-Host "═══════════════════════════════════════════" -ForegroundColor Green
Write-Host "✅ Désinstallation terminée avec succès" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════" -ForegroundColor Green
Write-Host ""

if ($KeepData) {
    Write-Host "💾 Données conservées :" -ForegroundColor Cyan
    Write-Host "   → data\homeflix.db" -ForegroundColor Gray
    Write-Host "   → settings.yaml" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Pour réinstaller avec vos données :" -ForegroundColor Cyan
    Write-Host "   → Exécutez simplement INSTALLER.ps1" -ForegroundColor White
} else {
    Write-Host "🗑️  Suppression complète effectuée" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Pour supprimer complètement le dossier :" -ForegroundColor Yellow
    Write-Host "   → Fermez cette fenêtre" -ForegroundColor White
    Write-Host "   → Supprimez le dossier homeflix\" -ForegroundColor White
}

Write-Host ""
Write-Host "Merci d'avoir utilisé Homeflix ! 🎬" -ForegroundColor Cyan
Write-Host ""
