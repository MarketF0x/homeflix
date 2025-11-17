# Installation automatique de Tailscale
Write-Host "=======================" -ForegroundColor Cyan
Write-Host "Installation Tailscale" -ForegroundColor Cyan
Write-Host "=======================" -ForegroundColor Cyan
Write-Host ""

# Télécharger Tailscale
$url = "https://pkgs.tailscale.com/stable/tailscale-setup-latest.exe"
$output = "$env:TEMP\tailscale-setup.exe"

Write-Host "Téléchargement de Tailscale..." -ForegroundColor Yellow
try {
    Invoke-WebRequest -Uri $url -OutFile $output -UseBasicParsing
    Write-Host "OK: Téléchargement réussi!" -ForegroundColor Green
} catch {
    Write-Host "ERREUR: Impossible de télécharger Tailscale" -ForegroundColor Red
    Write-Host "Veuillez télécharger manuellement depuis: https://tailscale.com/download/windows" -ForegroundColor Yellow
    exit 1
}

# Lancer l'installation
Write-Host ""
Write-Host "Lancement de l'installation..." -ForegroundColor Yellow
Write-Host "IMPORTANT: Suivez les instructions de l'installateur" -ForegroundColor Cyan
Write-Host ""

Start-Process -FilePath $output -Wait

Write-Host ""
Write-Host "=======================" -ForegroundColor Green
Write-Host "Installation terminée!" -ForegroundColor Green
Write-Host "=======================" -ForegroundColor Green
Write-Host ""
Write-Host "Prochaines étapes:" -ForegroundColor Cyan
Write-Host "1. Cliquez sur l'icône Tailscale dans la barre des tâches" -ForegroundColor White
Write-Host "2. Connectez-vous avec votre compte (Google, Microsoft, GitHub...)" -ForegroundColor White
Write-Host "3. Votre PC recevra une adresse IP Tailscale (ex: 100.x.x.x)" -ForegroundColor White
Write-Host ""
Write-Host "Sur l'autre ordinateur distant:" -ForegroundColor Cyan
Write-Host "1. Installez aussi Tailscale" -ForegroundColor White
Write-Host "2. Connectez-vous avec le MÊME compte" -ForegroundColor White
Write-Host "3. Accédez à Homeflix via: http://TAILSCALE-IP:5173" -ForegroundColor White
Write-Host ""
