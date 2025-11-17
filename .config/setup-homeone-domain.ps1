# ========================================================================
# Configuration du nom de domaine "homeone.local" pour Homeflix
# Exécuter en tant qu'administrateur
# ========================================================================

Write-Host "🏠 Configuration du domaine HomeOne" -ForegroundColor Cyan
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

# 2. Récupérer les adresses IP de ce PC
Write-Host "🌐 Détection des adresses IP..." -ForegroundColor Cyan
$adapters = Get-NetIPAddress -AddressFamily IPv4 | Where-Object { 
    $_.IPAddress -notlike "127.*" -and 
    ($_.IPAddress -like "192.168.*" -or $_.IPAddress -like "10.*" -or $_.IPAddress -like "100.72.*")
}

if ($adapters.Count -eq 0) {
    Write-Host "❌ Aucune adresse IP réseau détectée" -ForegroundColor Red
    pause
    exit 1
}

$selectedIP = $null
if ($adapters.Count -eq 1) {
    $selectedIP = $adapters[0].IPAddress
    Write-Host "   ✅ IP détectée : $selectedIP" -ForegroundColor Green
} else {
    Write-Host "   Plusieurs interfaces réseau détectées :" -ForegroundColor Yellow
    for ($i = 0; $i -lt $adapters.Count; $i++) {
        $adapter = $adapters[$i]
        $ifAlias = (Get-NetAdapter -InterfaceIndex $adapter.InterfaceIndex).Name
        Write-Host "   $($i + 1). $($adapter.IPAddress) - $ifAlias" -ForegroundColor White
    }
    Write-Host ""
    $choice = Read-Host "Choisissez le numéro de l'interface principale (1-$($adapters.Count))"
    $selectedIP = $adapters[[int]$choice - 1].IPAddress
    Write-Host "   ✅ IP sélectionnée : $selectedIP" -ForegroundColor Green
}

Write-Host ""

# 3. Modifier le fichier hosts de Windows
$hostsPath = "$env:SystemRoot\System32\drivers\etc\hosts"
Write-Host "📝 Configuration du fichier hosts..." -ForegroundColor Cyan

# Lire le contenu actuel
$hostsContent = Get-Content $hostsPath -ErrorAction SilentlyContinue
if (-not $hostsContent) {
    $hostsContent = @()
}

# Supprimer les anciennes entrées homeone.local
$hostsContent = $hostsContent | Where-Object { $_ -notlike "*homeone.local*" }

# Ajouter les nouvelles entrées
$newEntries = @(
    "",
    "# ========== Homeflix - HomeOne Domain ==========",
    "$selectedIP    homeone.local",
    "$selectedIP    www.homeone.local",
    "# ==============================================="
)

$hostsContent += $newEntries
$hostsContent | Out-File -FilePath $hostsPath -Encoding ASCII

Write-Host "   ✅ Fichier hosts mis à jour" -ForegroundColor Green
Write-Host "      $selectedIP → homeone.local" -ForegroundColor Yellow
Write-Host ""

# 4. Vider le cache DNS
Write-Host "🔄 Vidage du cache DNS..." -ForegroundColor Cyan
ipconfig /flushdns | Out-Null
Write-Host "   ✅ Cache DNS vidé" -ForegroundColor Green
Write-Host ""

# 5. Tester la résolution DNS
Write-Host "🧪 Test de résolution DNS..." -ForegroundColor Cyan
$pingResult = Test-Connection -ComputerName "homeone.local" -Count 1 -ErrorAction SilentlyContinue
if ($pingResult) {
    Write-Host "   ✅ homeone.local résout correctement vers $selectedIP" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  Test ping échoué (normal si firewall actif)" -ForegroundColor Yellow
    Write-Host "      La résolution DNS devrait quand même fonctionner" -ForegroundColor White
}
Write-Host ""

# 6. Afficher les instructions pour les appareils distants
Write-Host "📱 Configuration des appareils distants (téléphone, tablette, etc.)" -ForegroundColor Cyan
Write-Host ""
Write-Host "=" * 70 -ForegroundColor DarkGray
Write-Host ""
Write-Host "🔧 MÉTHODE 1 : Application DNS locale (RECOMMANDÉ)" -ForegroundColor Yellow
Write-Host "   1. Installez une app comme 'DNS Override' ou 'Hosts Editor'" -ForegroundColor White
Write-Host "   2. Ajoutez l'entrée : $selectedIP → homeone.local" -ForegroundColor White
Write-Host ""
Write-Host "🔧 MÉTHODE 2 : Serveur DNS local (avancé)" -ForegroundColor Yellow
Write-Host "   Configurez un serveur DNS (Pi-hole, AdGuard Home, etc.)" -ForegroundColor White
Write-Host "   Ajoutez l'entrée DNS : homeone.local → $selectedIP" -ForegroundColor White
Write-Host ""
Write-Host "🔧 MÉTHODE 3 : Configuration manuelle du DNS sur téléphone" -ForegroundColor Yellow
Write-Host "   Android :" -ForegroundColor Cyan
Write-Host "     1. Paramètres > Réseau et Internet > WiFi" -ForegroundColor White
Write-Host "     2. Appuyez sur votre réseau > Avancé" -ForegroundColor White
Write-Host "     3. Paramètres IP > Statique" -ForegroundColor White
Write-Host "     4. DNS 1 : $selectedIP" -ForegroundColor White
Write-Host "     ⚠️  Cette méthode nécessite un serveur DNS sur ce PC" -ForegroundColor Yellow
Write-Host ""
Write-Host "   iOS :" -ForegroundColor Cyan
Write-Host "     1. Réglages > Wi-Fi" -ForegroundColor White
Write-Host "     2. Touchez (i) à côté de votre réseau" -ForegroundColor White
Write-Host "     3. Configurer le DNS > Manuel" -ForegroundColor White
Write-Host "     4. Ajoutez $selectedIP" -ForegroundColor White
Write-Host "     ⚠️  Cette méthode nécessite un serveur DNS sur ce PC" -ForegroundColor Yellow
Write-Host ""
Write-Host "=" * 70 -ForegroundColor DarkGray
Write-Host ""

# 7. Instructions finales
Write-Host "✅ Configuration terminée sur ce PC !" -ForegroundColor Green
Write-Host ""
Write-Host "🚀 Pour démarrer Homeflix :" -ForegroundColor Cyan
Write-Host "   Sur ce PC : http://homeone.local:5173" -ForegroundColor Green
Write-Host "   ou : https://homeone.local:5173 (si HTTPS configuré)" -ForegroundColor Green
Write-Host ""
Write-Host "📱 Depuis un téléphone (après configuration DNS) :" -ForegroundColor Cyan
Write-Host "   http://homeone.local:5173" -ForegroundColor Green
Write-Host "   ou : https://homeone.local:5173" -ForegroundColor Green
Write-Host ""
Write-Host "💡 ASTUCE : Pour éviter de configurer le DNS sur chaque appareil," -ForegroundColor Yellow
Write-Host "    utilisez Tailscale avec MagicDNS (configuration automatique)" -ForegroundColor Yellow
Write-Host ""

pause
