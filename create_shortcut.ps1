# HomeOne - Script de creation du raccourci Windows
Write-Host ""
Write-Host "---------------------------------------------" -ForegroundColor DarkGray
Write-Host "  Creation du raccourci HomeOne..." -ForegroundColor Green
Write-Host "---------------------------------------------" -ForegroundColor DarkGray
Write-Host ""

$projectRoot = $PSScriptRoot
$vbsLauncher = Join-Path $projectRoot "launch_homeone_silent.vbs"
$iconPath = Join-Path $projectRoot "homeone.ico"
$shortcutPath = Join-Path ([Environment]::GetFolderPath("Desktop")) "HomeOne.lnk"

Write-Host "Debug - Chemins detectes:" -ForegroundColor Yellow
Write-Host "   Projet: $projectRoot" -ForegroundColor Gray
Write-Host "   VBS: $vbsLauncher" -ForegroundColor Gray
Write-Host "   Icone: $iconPath" -ForegroundColor Gray
Write-Host "   Raccourci: $shortcutPath" -ForegroundColor Gray
Write-Host ""

if (-not (Test-Path $vbsLauncher)) {
    Write-Host "Le fichier launch_homeone_silent.vbs est introuvable." -ForegroundColor Red
    Pause
    exit
}

$iconPathResolved = $null
if (Test-Path $iconPath) {
    $iconPathResolved = (Resolve-Path $iconPath).Path
    Write-Host "Icone trouvee: $iconPathResolved" -ForegroundColor Green
} else {
    Write-Host "Icone homeone.ico introuvable" -ForegroundColor Yellow
    $iconPathResolved = "%SystemRoot%\System32\imageres.dll,185"
}

$WshShell = New-Object -ComObject WScript.Shell
$shortcut = $WshShell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $vbsLauncher
$shortcut.WorkingDirectory = $projectRoot
$shortcut.IconLocation = $iconPathResolved
$shortcut.Description = "Lance HomeOne (Backend + Frontend en mode application)"
$shortcut.Save()

Write-Host ""
Write-Host "Raccourci cree sur le Bureau : HomeOne.lnk" -ForegroundColor Green
Write-Host "   Icone : $iconPathResolved" -ForegroundColor Cyan
Write-Host ""
Write-Host "Double-cliquez sur HomeOne pour lancer!" -ForegroundColor Green
