# ========================================================================
# Configuration de l'accès réseau distant pour Homeflix
# Exécuter en tant qu'administrateur : clic droit > Exécuter en tant qu'administrateur
# ========================================================================

Write-Host "🔧 Configuration de l'accès réseau distant pour Homeflix" -ForegroundColor Cyan
Write-Host ""

# 1. Vérifier les droits admin
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
$isAdmin = $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "❌ Ce script nécessite des droits administrateur." -ForegroundColor Red
    Write-Host "   Clic droit sur le fichier > Exécuter en tant qu'administrateur" -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host "✅ Droits administrateur détectés" -ForegroundColor Green
Write-Host ""

# 2. Configurer le firewall pour le port 8000 (HTTP)
Write-Host "🔥 Configuration du pare-feu Windows..." -ForegroundColor Cyan

# Supprimer l'ancienne règle si elle existe
netsh advfirewall firewall delete rule name="Homeflix FastAPI" | Out-Null

# Créer la nouvelle règle
netsh advfirewall firewall add rule name="Homeflix FastAPI" dir=in action=allow protocol=TCP localport=8000
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Règle firewall créée pour le port 8000" -ForegroundColor Green
} else {
    Write-Host "   ❌ Erreur lors de la création de la règle firewall" -ForegroundColor Red
}

# 3. Configurer le firewall pour le port 8443 (HTTPS)
netsh advfirewall firewall add rule name="Homeflix FastAPI HTTPS" dir=in action=allow protocol=TCP localport=8443
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Règle firewall créée pour le port 8443 (HTTPS)" -ForegroundColor Green
} else {
    Write-Host "   ❌ Erreur lors de la création de la règle firewall" -ForegroundColor Red
}

Write-Host ""

# 4. Afficher les adresses réseau disponibles
Write-Host "🌐 Adresses réseau disponibles :" -ForegroundColor Cyan
$adapters = Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -notlike "127.*" }
foreach ($adapter in $adapters) {
    $ifIndex = $adapter.InterfaceIndex
    $ifAlias = (Get-NetAdapter -InterfaceIndex $ifIndex).Name
    Write-Host "   • $($adapter.IPAddress) ($ifAlias)" -ForegroundColor Yellow
}

Write-Host ""

# 5. Instructions pour tester
Write-Host "📱 Pour tester depuis votre téléphone :" -ForegroundColor Cyan
Write-Host "   1. Connectez votre téléphone au même réseau (WiFi ou Tailscale)" -ForegroundColor White
Write-Host "   2. Démarrez le serveur Homeflix" -ForegroundColor White
Write-Host "   3. Ouvrez votre navigateur sur :" -ForegroundColor White
Write-Host ""
foreach ($adapter in $adapters) {
    if ($adapter.IPAddress -like "100.72.*" -or $adapter.IPAddress -like "192.168.*" -or $adapter.IPAddress -like "10.*") {
        Write-Host "      http://$($adapter.IPAddress):5173" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "⚠️  Si le navigateur bloque l'accès HTTP :" -ForegroundColor Yellow
Write-Host "   - Sur Chrome/Edge : Tapez 'thisisunsafe' sur la page d'avertissement" -ForegroundColor White
Write-Host "   - Ou utilisez HTTPS (voir option certificat SSL ci-dessous)" -ForegroundColor White

Write-Host ""
Write-Host "🔒 Pour activer HTTPS (recommandé) :" -ForegroundColor Cyan
Write-Host "   1. Installez mkcert : winget install FiloSottile.mkcert" -ForegroundColor White
Write-Host "   2. Exécutez le script : .\setup-https.ps1" -ForegroundColor White

Write-Host ""
Write-Host "✅ Configuration terminée !" -ForegroundColor Green
Write-Host ""

pause
