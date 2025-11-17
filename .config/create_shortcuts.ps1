# Création de raccourcis bureau pour Homeflix
# Ce script crée les raccourcis pour lancer l'application

param(
    [switch]$Silent
)

$projectRoot = Split-Path -Parent $PSScriptRoot
$desktopPath = [System.Environment]::GetFolderPath('Desktop')

if (-not $Silent) {
    Write-Host ""
    Write-Host "🔗 Création des raccourcis Homeflix..." -ForegroundColor Cyan
    Write-Host ""
}

# Fonction pour créer un raccourci
function New-HomeflixShortcut {
    param(
        [string]$Name,
        [string]$Target,
        [string]$Arguments,
        [string]$Description,
        [string]$Icon
    )
    
    $shortcutPath = Join-Path $desktopPath "$Name.lnk"
    
    try {
        $WScriptShell = New-Object -ComObject WScript.Shell
        $shortcut = $WScriptShell.CreateShortcut($shortcutPath)
        $shortcut.TargetPath = $Target
        if ($Arguments) {
            $shortcut.Arguments = $Arguments
        }
        $shortcut.WorkingDirectory = $projectRoot
        $shortcut.Description = $Description
        if ($Icon -and (Test-Path $Icon)) {
            $shortcut.IconLocation = $Icon
        }
        $shortcut.Save()
        
        if (-not $Silent) {
            Write-Host "✅ Raccourci créé: $Name" -ForegroundColor Green
        }
        return $true
    } catch {
        if (-not $Silent) {
            Write-Host "❌ Erreur création raccourci: $Name" -ForegroundColor Red
            Write-Host "   $_" -ForegroundColor Gray
        }
        return $false
    }
}

# Détecter le mode d'installation
$hasElectron = Test-Path (Join-Path $projectRoot "electron\main.js")
$hasElectronApp = Test-Path (Join-Path $projectRoot "electron\dist\win-unpacked\Homeflix.exe")

$shortcuts = @()

# Raccourci principal - Application Electron (si disponible)
if ($hasElectronApp) {
    $shortcuts += @{
        Name = "Homeflix App"
        Target = Join-Path $projectRoot "electron\dist\win-unpacked\Homeflix.exe"
        Arguments = ""
        Description = "Homeflix - Application de streaming (version native)"
        Icon = Join-Path $projectRoot "electron\icon.png"
    }
} elseif ($hasElectron -and (Test-Path (Join-Path $projectRoot "electron\node_modules"))) {
    # Raccourci pour lancer Electron en mode développement
    $shortcuts += @{
        Name = "Homeflix App"
        Target = "powershell.exe"
        Arguments = "-NoProfile -ExecutionPolicy Bypass -File `"$projectRoot\start-homeflix-app.ps1`""
        Description = "Homeflix - Application de streaming (mode développement)"
        Icon = Join-Path $projectRoot "electron\icon.png"
    }
}

# Raccourci alternatif - Mode navigateur (toujours disponible)
$shortcuts += @{
    Name = "Homeflix Web"
    Target = "powershell.exe"
    Arguments = "-NoProfile -ExecutionPolicy Bypass -File `"$projectRoot\homeflix.ps1`""
    Description = "Homeflix - Ouvrir dans le navigateur"
    Icon = Join-Path $projectRoot "client\public\homeflix-logo.png"
}

# Créer tous les raccourcis
$successCount = 0
foreach ($shortcut in $shortcuts) {
    if (New-HomeflixShortcut @shortcut) {
        $successCount++
    }
}

if (-not $Silent) {
    Write-Host ""
    if ($successCount -gt 0) {
        Write-Host "✅ $successCount raccourci(s) créé(s) sur le bureau" -ForegroundColor Green
        Write-Host ""
        Write-Host "📌 Raccourcis disponibles:" -ForegroundColor Cyan
        foreach ($shortcut in $shortcuts) {
            Write-Host "   • $($shortcut.Name)" -ForegroundColor White
        }
    } else {
        Write-Host "❌ Aucun raccourci n'a pu être créé" -ForegroundColor Red
    }
    Write-Host ""
}

# Retourner le nombre de raccourcis créés
exit $successCount
