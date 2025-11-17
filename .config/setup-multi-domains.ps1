# ========================================================================
# Configuration multi-domaines HomeOne
# homeone.local (réseau local) / homeone.wifi (WiFi) / homeone.web (Tailscale)
# Exécuter en tant qu'administrateur
# ========================================================================

Write-Host "🏠 Configuration multi-domaines HomeOne" -ForegroundColor Cyan
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

# 2. Détecter toutes les interfaces réseau
Write-Host "🌐 Détection des interfaces réseau..." -ForegroundColor Cyan
$adapters = Get-NetIPAddress -AddressFamily IPv4 | Where-Object { 
    $_.IPAddress -notlike "127.*" -and $_.IPAddress -notlike "169.254.*"
}

$wifiIP = $null
$tailscaleIP = $null
$ethernetIP = $null

foreach ($adapter in $adapters) {
    $ifIndex = $adapter.InterfaceIndex
    $ifInfo = Get-NetAdapter -InterfaceIndex $ifIndex
    $ifName = $ifInfo.InterfaceDescription
    $ip = $adapter.IPAddress
    
    # Détection Tailscale
    if ($ip -like "100.*" -or $ifName -like "*Tailscale*") {
        $tailscaleIP = $ip
        Write-Host "   🌍 Tailscale : $ip" -ForegroundColor Green
    }
    # Détection WiFi
    elseif ($ifInfo.PhysicalMediaType -eq "Native 802.11" -or $ifName -like "*Wi-Fi*" -or $ifName -like "*Wireless*") {
        $wifiIP = $ip
        Write-Host "   📡 WiFi : $ip" -ForegroundColor Yellow
    }
    # Détection Ethernet
    elseif ($ifInfo.PhysicalMediaType -eq "802.3" -or $ifName -like "*Ethernet*") {
        $ethernetIP = $ip
        Write-Host "   🔌 Ethernet : $ip" -ForegroundColor Cyan
    }
    else {
        Write-Host "   ❓ Autre ($($ifInfo.Name)) : $ip" -ForegroundColor DarkGray
    }
}

Write-Host ""

# 3. Configuration du fichier hosts
$hostsPath = "$env:SystemRoot\System32\drivers\etc\hosts"
Write-Host "📝 Configuration du fichier hosts..." -ForegroundColor Cyan

# Lire le contenu actuel
$hostsContent = Get-Content $hostsPath -ErrorAction SilentlyContinue
if (-not $hostsContent) {
    $hostsContent = @()
}

# Supprimer les anciennes entrées HomeOne
$hostsContent = $hostsContent | Where-Object { 
    $_ -notlike "*homeone.*" -and $_ -notlike "*HomeOne*" 
}

# Construire les nouvelles entrées
$newEntries = @(
    "",
    "# ========== HomeOne - Multi-Domain Configuration ==========",
    "# homeone.local : Réseau local (toutes interfaces)",
    "# homeone.wifi  : WiFi uniquement",
    "# homeone.web   : Accès distant via Tailscale",
    ""
)

# homeone.local - pointera vers la meilleure interface disponible
$localIP = $wifiIP
if (-not $localIP) { $localIP = $ethernetIP }
if (-not $localIP -and $tailscaleIP) { $localIP = $tailscaleIP }

if ($localIP) {
    $newEntries += "$localIP    homeone.local"
    $newEntries += "$localIP    www.homeone.local"
    Write-Host "   ✅ homeone.local → $localIP" -ForegroundColor Green
}

# homeone.wifi - WiFi uniquement
if ($wifiIP) {
    $newEntries += "$wifiIP    homeone.wifi"
    $newEntries += "$wifiIP    www.homeone.wifi"
    Write-Host "   ✅ homeone.wifi → $wifiIP" -ForegroundColor Yellow
}

# homeone.web - Tailscale (accès distant)
if ($tailscaleIP) {
    $newEntries += "$tailscaleIP    homeone.web"
    $newEntries += "$tailscaleIP    www.homeone.web"
    Write-Host "   ✅ homeone.web → $tailscaleIP" -ForegroundColor Green
}

# homeone.lan - Ethernet
if ($ethernetIP -and $ethernetIP -ne $wifiIP) {
    $newEntries += "$ethernetIP    homeone.lan"
    Write-Host "   ✅ homeone.lan → $ethernetIP" -ForegroundColor Cyan
}

$newEntries += "# ========================================================"

$hostsContent += $newEntries
$hostsContent | Out-File -FilePath $hostsPath -Encoding ASCII

Write-Host ""

# 4. Vider le cache DNS
Write-Host "🔄 Vidage du cache DNS..." -ForegroundColor Cyan
ipconfig /flushdns | Out-Null
Write-Host "   ✅ Cache DNS vidé" -ForegroundColor Green
Write-Host ""

# 5. Générer le certificat SSL multi-domaines
$certDir = Join-Path $PSScriptRoot "certs"
$certFile = Join-Path $certDir "cert.pem"
$keyFile = Join-Path $certDir "key.pem"
$configFile = Join-Path $certDir "openssl.cnf"

Write-Host "🔒 Génération du certificat SSL multi-domaines..." -ForegroundColor Cyan

if (-not (Test-Path $certDir)) {
    New-Item -ItemType Directory -Path $certDir | Out-Null
}

# Vérifier si OpenSSL est disponible
$openssl = Get-Command openssl -ErrorAction SilentlyContinue

if (-not $openssl) {
    Write-Host "   ⚠️  OpenSSL non détecté - certificat non généré" -ForegroundColor Yellow
    Write-Host "      Vous pourrez le générer plus tard avec : .\setup-https.ps1" -ForegroundColor White
    $skipSSL = $true
} else {
    # Créer la configuration OpenSSL avec tous les domaines
    $configContent = @"
[req]
default_bits = 2048
prompt = no
default_md = sha256
distinguished_name = dn
req_extensions = v3_req

[dn]
C=FR
ST=France
L=Paris
O=HomeOne
CN=homeone.local

[v3_req]
keyUsage = keyEncipherment, dataEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names

[alt_names]
DNS.1 = localhost
DNS.2 = homeone.local
DNS.3 = www.homeone.local
DNS.4 = homeone.wifi
DNS.5 = www.homeone.wifi
DNS.6 = homeone.web
DNS.7 = www.homeone.web
DNS.8 = homeone.lan
IP.1 = 127.0.0.1
"@

    $ipIndex = 2
    if ($wifiIP) {
        $configContent += "`nIP.$ipIndex = $wifiIP"
        $ipIndex++
    }
    if ($tailscaleIP) {
        $configContent += "`nIP.$ipIndex = $tailscaleIP"
        $ipIndex++
    }
    if ($ethernetIP -and $ethernetIP -ne $wifiIP) {
        $configContent += "`nIP.$ipIndex = $ethernetIP"
        $ipIndex++
    }

    $configContent | Out-File -FilePath $configFile -Encoding ASCII

    # Générer la clé privée
    & openssl genrsa -out $keyFile 2048 2>&1 | Out-Null
    
    # Générer le certificat
    & openssl req -new -x509 -key $keyFile -out $certFile -days 365 -config $configFile 2>&1 | Out-Null

    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ Certificat SSL généré pour tous les domaines" -ForegroundColor Green
        Write-Host "      Valide pour : homeone.local, homeone.wifi, homeone.web" -ForegroundColor DarkGray
    } else {
        Write-Host "   ❌ Erreur lors de la génération du certificat" -ForegroundColor Red
    }
}

Write-Host ""

# 6. Résumé de la configuration
Write-Host "=" * 70 -ForegroundColor DarkGray
Write-Host ""
Write-Host "✅ CONFIGURATION TERMINÉE" -ForegroundColor Green
Write-Host ""
Write-Host "📱 URLs d'accès disponibles :" -ForegroundColor Cyan
Write-Host ""

if ($localIP) {
    Write-Host "   🏠 Réseau local (toutes interfaces) :" -ForegroundColor White
    Write-Host "      http://homeone.local:5173" -ForegroundColor Green
    if (-not $skipSSL) {
        Write-Host "      https://homeone.local:5173" -ForegroundColor Green
    }
    Write-Host ""
}

if ($wifiIP) {
    Write-Host "   📡 WiFi uniquement :" -ForegroundColor White
    Write-Host "      http://homeone.wifi:5173" -ForegroundColor Yellow
    if (-not $skipSSL) {
        Write-Host "      https://homeone.wifi:5173" -ForegroundColor Yellow
    }
    Write-Host ""
}

if ($tailscaleIP) {
    Write-Host "   🌍 Accès distant (Tailscale) :" -ForegroundColor White
    Write-Host "      http://homeone.web:5173" -ForegroundColor Cyan
    if (-not $skipSSL) {
        Write-Host "      https://homeone.web:5173" -ForegroundColor Cyan
    }
    Write-Host ""
}

if ($ethernetIP -and $ethernetIP -ne $wifiIP) {
    Write-Host "   🔌 Ethernet :" -ForegroundColor White
    Write-Host "      http://homeone.lan:5173" -ForegroundColor Blue
    Write-Host ""
}

Write-Host "💡 Le navigateur affichera automatiquement le bon nom selon votre connexion" -ForegroundColor Yellow
Write-Host ""

# 7. Instructions pour les appareils distants
Write-Host "📱 CONFIGURATION DES APPAREILS DISTANTS" -ForegroundColor Cyan
Write-Host ""
Write-Host "Pour afficher 'homeone.wifi' ou 'homeone.web' sur téléphone/tablette :" -ForegroundColor White
Write-Host ""
Write-Host "1️⃣  OPTION SIMPLE : Application Hosts Editor" -ForegroundColor Yellow
Write-Host "   • Android : 'Virtual Hosts' ou 'Hosts Editor' (Play Store)" -ForegroundColor DarkGray
Write-Host "   • iOS : 'Surge' ou 'Shadowrocket' (App Store, payant)" -ForegroundColor DarkGray
Write-Host ""
if ($wifiIP) {
    Write-Host "   Ajoutez ces entrées :" -ForegroundColor White
    Write-Host "   $wifiIP → homeone.wifi" -ForegroundColor Green
}
if ($tailscaleIP) {
    Write-Host "   $tailscaleIP → homeone.web" -ForegroundColor Green
}
Write-Host ""

Write-Host "2️⃣  OPTION AVANCÉE : Tailscale MagicDNS" -ForegroundColor Yellow
Write-Host "   • Exécutez : .\setup-tailscale-dns.ps1" -ForegroundColor White
Write-Host "   • Renommez votre machine en 'homeone'" -ForegroundColor White
Write-Host "   • Accédez via : http://homeone:5173" -ForegroundColor Green
Write-Host ""

Write-Host "3️⃣  OPTION PRO : Serveur DNS local (Pi-hole, AdGuard Home)" -ForegroundColor Yellow
Write-Host "   • Configurez votre routeur pour utiliser le serveur DNS" -ForegroundColor White
Write-Host "   • Tous les appareils auront accès automatiquement" -ForegroundColor White
Write-Host ""

Write-Host "=" * 70 -ForegroundColor DarkGray
Write-Host ""

# 8. Créer un fichier de configuration pour référence
$configInfo = @"
# HomeOne - Configuration Multi-Domaines
# Généré le $(Get-Date -Format "dd/MM/yyyy à HH:mm")

## Domaines configurés :

homeone.local → $localIP (Réseau local - toutes interfaces)
homeone.wifi  → $wifiIP (WiFi uniquement)
homeone.web   → $tailscaleIP (Accès distant via Tailscale)
homeone.lan   → $ethernetIP (Ethernet)

## URLs d'accès :

### Sur ce PC :
- http://homeone.local:5173
- http://homeone.wifi:5173
- http://homeone.web:5173

### Sur téléphone (après configuration DNS) :
- WiFi : http://homeone.wifi:5173
- Tailscale : http://homeone.web:5173

## Fichiers générés :
- Certificat SSL : certs/cert.pem
- Clé privée : certs/key.pem
- Configuration OpenSSL : certs/openssl.cnf

## Prochaines étapes :
1. Configurez le firewall : .\configure-network-access.ps1
2. Démarrez le serveur : cd server; python main.py
3. Démarrez le client : cd client; npm run dev
4. Testez : http://homeone.local:5173

"@

$configInfo | Out-File -FilePath (Join-Path $PSScriptRoot "homeone-config.txt") -Encoding UTF8
Write-Host "📄 Configuration sauvegardée dans : homeone-config.txt" -ForegroundColor Green
Write-Host ""

pause
