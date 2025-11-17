# Script pour corriger le raccourci Homeflix App
# Crée un raccourci direct vers l'exécutable Electron

$projectRoot = "c:\Users\fparo\Desktop\homeflix"
$desktopPath = [System.Environment]::GetFolderPath('Desktop')
$shortcutPath = Join-Path $desktopPath "Homeflix App.lnk"

Write-Host "Correction du raccourci Homeflix App..." -ForegroundColor Cyan

# Supprimer l'ancien raccourci s'il existe
if (Test-Path $shortcutPath) {
    Remove-Item $shortcutPath -Force
    Write-Host "Ancien raccourci supprime" -ForegroundColor Yellow
}

# Vérifier que l'exécutable existe
$exePath = Join-Path $projectRoot "electron\dist\win-unpacked\Homeflix.exe"
if (-not (Test-Path $exePath)) {
    Write-Host "ERREUR: Executable introuvable a: $exePath" -ForegroundColor Red
    exit 1
}

# Créer le nouveau raccourci
try {
    $WScriptShell = New-Object -ComObject WScript.Shell
    $shortcut = $WScriptShell.CreateShortcut($shortcutPath)
    $shortcut.TargetPath = $exePath
    $shortcut.WorkingDirectory = Join-Path $projectRoot "electron\dist\win-unpacked"
    $shortcut.Description = "Homeflix - Application de streaming"
    
    # Utiliser l'icône favicon (même que l'onglet web)
    $iconPath = Join-Path $projectRoot "client\public\favicon.ico"
    if (Test-Path $iconPath) {
        $shortcut.IconLocation = $iconPath
    }
    
    $shortcut.Save()
    
    Write-Host "Raccourci cree avec succes!" -ForegroundColor Green
    Write-Host "Emplacement: $shortcutPath" -ForegroundColor Gray
    Write-Host "Cible: $exePath" -ForegroundColor Gray
} catch {
    Write-Host "ERREUR lors de la creation du raccourci:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}
