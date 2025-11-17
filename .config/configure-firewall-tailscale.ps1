# Configuration pare-feu pour Tailscale
# Clic droit > Exécuter en tant qu'administrateur

Write-Host "Configuration du pare-feu pour Tailscale..." -ForegroundColor Cyan
Write-Host ""

# Vérifier droits admin
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
$isAdmin = $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ERREUR : Ce script nécessite des droits administrateur." -ForegroundColor Red
    Write-Host "Clic droit sur le fichier > Exécuter en tant qu'administrateur" -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host "Droits administrateur OK" -ForegroundColor Green
Write-Host ""

# Supprimer anciennes règles si elles existent
Write-Host "Nettoyage des anciennes règles..." -ForegroundColor Yellow
Remove-NetFirewallRule -DisplayName "HomeOne - Vite*" -ErrorAction SilentlyContinue
Remove-NetFirewallRule -DisplayName "HomeOne - FastAPI*" -ErrorAction SilentlyContinue
Remove-NetFirewallRule -DisplayName "Homeflix*" -ErrorAction SilentlyContinue

# Créer règles pour Vite (port 5173)
Write-Host "Création règle pour Vite (port 5173)..." -ForegroundColor Cyan
New-NetFirewallRule -DisplayName "HomeOne - Vite (HTTP)" `
    -Direction Inbound `
    -Protocol TCP `
    -LocalPort 5173 `
    -Action Allow `
    -Profile Any `
    -Enabled True | Out-Null

Write-Host "   OK - Port 5173 ouvert" -ForegroundColor Green

# Créer règles pour FastAPI (port 8000)
Write-Host "Création règle pour FastAPI (port 8000)..." -ForegroundColor Cyan
New-NetFirewallRule -DisplayName "HomeOne - FastAPI (HTTP)" `
    -Direction Inbound `
    -Protocol TCP `
    -LocalPort 8000 `
    -Action Allow `
    -Profile Any `
    -Enabled True | Out-Null

Write-Host "   OK - Port 8000 ouvert" -ForegroundColor Green

# Créer règles pour HTTPS si nécessaire (port 8443)
Write-Host "Création règle pour HTTPS (port 8443)..." -ForegroundColor Cyan
New-NetFirewallRule -DisplayName "HomeOne - FastAPI (HTTPS)" `
    -Direction Inbound `
    -Protocol TCP `
    -LocalPort 8443 `
    -Action Allow `
    -Profile Any `
    -Enabled True | Out-Null

Write-Host "   OK - Port 8443 ouvert" -ForegroundColor Green
Write-Host ""

# Vérifier les règles créées
Write-Host "Règles créées :" -ForegroundColor Green
Get-NetFirewallRule -DisplayName "HomeOne*" | Select-Object DisplayName, Enabled, Direction | Format-Table

Write-Host ""
Write-Host "Configuration terminée !" -ForegroundColor Green
Write-Host ""
Write-Host "Vous pouvez maintenant accéder à HomeOne via Tailscale :" -ForegroundColor Cyan
Write-Host "   http://100.72.164.87:5173" -ForegroundColor Yellow
Write-Host ""

pause
