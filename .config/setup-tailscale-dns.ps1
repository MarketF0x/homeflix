# ========================================================================
# Configuration Tailscale MagicDNS pour HomeOne
# Cette solution permet d'accéder à votre serveur via un nom depuis n'importe où
# ========================================================================

Write-Host "🌐 Configuration Tailscale MagicDNS pour HomeOne" -ForegroundColor Cyan
Write-Host ""

# 1. Vérifier si Tailscale est installé
$tailscale = Get-Command tailscale -ErrorAction SilentlyContinue

if (-not $tailscale) {
    Write-Host "❌ Tailscale n'est pas installé" -ForegroundColor Red
    Write-Host ""
    Write-Host "📥 Installation de Tailscale :" -ForegroundColor Yellow
    Write-Host "   1. Via Winget : winget install tailscale.tailscale" -ForegroundColor White
    Write-Host "   2. Via le site : https://tailscale.com/download" -ForegroundColor White
    Write-Host ""
    Write-Host "💡 Ou exécutez le script existant : .\install-tailscale.ps1" -ForegroundColor Cyan
    Write-Host ""
    pause
    exit 1
}

Write-Host "✅ Tailscale détecté : $($tailscale.Source)" -ForegroundColor Green
Write-Host ""

# 2. Vérifier le statut Tailscale
Write-Host "🔍 Vérification du statut Tailscale..." -ForegroundColor Cyan
$status = & tailscale status --json 2>$null | ConvertFrom-Json

if (-not $status) {
    Write-Host "❌ Tailscale n'est pas démarré ou connecté" -ForegroundColor Red
    Write-Host ""
    Write-Host "🚀 Démarrez Tailscale et connectez-vous :" -ForegroundColor Yellow
    Write-Host "   1. Ouvrez l'application Tailscale" -ForegroundColor White
    Write-Host "   2. Cliquez sur 'Connect' ou 'Se connecter'" -ForegroundColor White
    Write-Host "   3. Suivez les instructions de connexion" -ForegroundColor White
    Write-Host ""
    pause
    exit 1
}

# 3. Récupérer le nom de la machine Tailscale
$self = $status.Self
$hostname = $self.HostName
$tailscaleIP = $self.TailscaleIPs[0]
$magicDNSName = "$hostname.$($status.MagicDNSSuffix)"

Write-Host "   ✅ Tailscale actif" -ForegroundColor Green
Write-Host "   📍 IP Tailscale : $tailscaleIP" -ForegroundColor Yellow
Write-Host "   🏷️  Nom actuel : $hostname" -ForegroundColor Yellow
if ($status.MagicDNSSuffix) {
    Write-Host "   🌐 MagicDNS : $magicDNSName" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  MagicDNS non activé" -ForegroundColor Yellow
}
Write-Host ""

# 4. Proposer de renommer la machine en "homeone"
if ($hostname -ne "homeone") {
    Write-Host "🏠 Souhaitez-vous renommer cette machine en 'homeone' ?" -ForegroundColor Cyan
    Write-Host "   Nom actuel : $hostname" -ForegroundColor White
    Write-Host "   Nouveau nom : homeone" -ForegroundColor Green
    Write-Host ""
    $rename = Read-Host "Renommer ? (o/n)"
    
    if ($rename -eq "o" -or $rename -eq "O" -or $rename -eq "oui") {
        Write-Host ""
        Write-Host "🔄 Renommage de la machine..." -ForegroundColor Cyan
        & tailscale set --hostname homeone
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✅ Machine renommée en 'homeone'" -ForegroundColor Green
            $hostname = "homeone"
            $magicDNSName = "homeone.$($status.MagicDNSSuffix)"
        } else {
            Write-Host "   ❌ Erreur lors du renommage" -ForegroundColor Red
            Write-Host "      Vous pouvez le faire manuellement via l'admin Tailscale" -ForegroundColor Yellow
        }
    }
    Write-Host ""
}

# 5. Vérifier si MagicDNS est activé
if (-not $status.MagicDNSSuffix) {
    Write-Host "⚠️  MagicDNS n'est pas activé sur votre réseau Tailscale" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "📝 Pour activer MagicDNS :" -ForegroundColor Cyan
    Write-Host "   1. Allez sur https://login.tailscale.com/admin/dns" -ForegroundColor White
    Write-Host "   2. Activez 'MagicDNS'" -ForegroundColor White
    Write-Host "   3. (Optionnel) Activez 'Override local DNS'" -ForegroundColor White
    Write-Host ""
    Write-Host "💡 Une fois activé, vous pourrez accéder à votre serveur via :" -ForegroundColor Cyan
    Write-Host "   http://$hostname.tail<votre-domaine>.ts.net:5173" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host "✅ MagicDNS est activé !" -ForegroundColor Green
    Write-Host ""
    Write-Host "🌐 Vous pouvez maintenant accéder à votre serveur via :" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "   Sur ce réseau Tailscale :" -ForegroundColor Yellow
    Write-Host "   • http://$magicDNSName:5173" -ForegroundColor Green
    Write-Host "   • https://$magicDNSName:5173 (si HTTPS configuré)" -ForegroundColor Green
    Write-Host ""
    Write-Host "   Depuis n'importe où (via Tailscale) :" -ForegroundColor Yellow
    Write-Host "   • http://$hostname:5173" -ForegroundColor Green
    Write-Host "   • https://$hostname:5173" -ForegroundColor Green
    Write-Host ""
}

# 6. Afficher les autres appareils connectés
Write-Host "📱 Autres appareils sur votre réseau Tailscale :" -ForegroundColor Cyan
$peers = $status.Peer
if ($peers -and $peers.Count -gt 0) {
    foreach ($peer in $peers.PSObject.Properties) {
        $device = $peer.Value
        if ($device.Online) {
            $deviceName = $device.HostName
            $deviceIP = $device.TailscaleIPs[0]
            Write-Host "   • $deviceName ($deviceIP)" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host "   Aucun autre appareil connecté" -ForegroundColor DarkGray
}
Write-Host ""

# 7. Instructions pour connecter le téléphone
Write-Host "📱 Pour accéder depuis votre téléphone :" -ForegroundColor Cyan
Write-Host "   1. Installez Tailscale sur votre téléphone" -ForegroundColor White
Write-Host "      • Android : Google Play Store" -ForegroundColor DarkGray
Write-Host "      • iOS : App Store" -ForegroundColor DarkGray
Write-Host ""
Write-Host "   2. Connectez-vous avec le même compte Tailscale" -ForegroundColor White
Write-Host ""
Write-Host "   3. Ouvrez votre navigateur et allez sur :" -ForegroundColor White
if ($status.MagicDNSSuffix) {
    Write-Host "      http://$hostname:5173" -ForegroundColor Green
} else {
    Write-Host "      http://$tailscaleIP:5173" -ForegroundColor Green
}
Write-Host ""

# 8. Résumé
Write-Host "=" * 70 -ForegroundColor DarkGray
Write-Host ""
Write-Host "✅ RÉSUMÉ" -ForegroundColor Green
Write-Host ""
Write-Host "   Nom de la machine : $hostname" -ForegroundColor White
Write-Host "   IP Tailscale : $tailscaleIP" -ForegroundColor White
if ($status.MagicDNSSuffix) {
    Write-Host "   URL MagicDNS : http://$magicDNSName:5173" -ForegroundColor Green
    Write-Host ""
    Write-Host "   👉 Utilisez cette URL depuis tous vos appareils Tailscale" -ForegroundColor Cyan
} else {
    Write-Host "   URL directe : http://$tailscaleIP:5173" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   💡 Activez MagicDNS pour utiliser un nom au lieu de l'IP" -ForegroundColor Yellow
}
Write-Host ""
Write-Host "=" * 70 -ForegroundColor DarkGray
Write-Host ""

pause
