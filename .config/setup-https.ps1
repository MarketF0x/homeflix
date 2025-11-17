# ========================================================================
# Configuration HTTPS pour Homeflix avec certificat auto-signé
# Exécuter APRÈS configure-network-access.ps1
# ========================================================================

Write-Host "🔒 Configuration HTTPS pour Homeflix" -ForegroundColor Cyan
Write-Host ""

$certDir = Join-Path $PSScriptRoot "certs"

# 1. Créer le répertoire des certificats
if (-not (Test-Path $certDir)) {
    New-Item -ItemType Directory -Path $certDir | Out-Null
    Write-Host "✅ Répertoire certs/ créé" -ForegroundColor Green
}

# 2. Vérifier si OpenSSL est disponible
$openssl = Get-Command openssl -ErrorAction SilentlyContinue

if (-not $openssl) {
    Write-Host "❌ OpenSSL n'est pas installé" -ForegroundColor Red
    Write-Host ""
    Write-Host "📥 Options d'installation :" -ForegroundColor Yellow
    Write-Host "   1. Via Chocolatey : choco install openssl" -ForegroundColor White
    Write-Host "   2. Via Winget : winget install ShiningLight.OpenSSL" -ForegroundColor White
    Write-Host "   3. Téléchargement : https://slproweb.com/products/Win32OpenSSL.html" -ForegroundColor White
    Write-Host ""
    Write-Host "💡 Alternative simple : utilisez mkcert" -ForegroundColor Cyan
    Write-Host "   winget install FiloSottile.mkcert" -ForegroundColor White
    Write-Host "   mkcert -install" -ForegroundColor White
    Write-Host "   mkcert 100.72.164.87 192.168.1.5 localhost 127.0.0.1" -ForegroundColor White
    Write-Host ""
    pause
    exit 1
}

Write-Host "✅ OpenSSL détecté : $($openssl.Source)" -ForegroundColor Green
Write-Host ""

# 3. Récupérer les adresses IP
Write-Host "🌐 Détection des adresses IP..." -ForegroundColor Cyan
$ips = @("localhost", "127.0.0.1")
$adapters = Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -notlike "127.*" }
foreach ($adapter in $adapters) {
    $ips += $adapter.IPAddress
    Write-Host "   • $($adapter.IPAddress)" -ForegroundColor Yellow
}

# 4. Créer la configuration OpenSSL
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
DNS.4 = homeflix.local
IP.1 = 127.0.0.1
"@

$ipIndex = 2
foreach ($ip in $ips | Where-Object { $_ -ne "localhost" -and $_ -ne "127.0.0.1" }) {
    $configContent += "`nIP.$ipIndex = $ip"
    $ipIndex++
}

$configPath = Join-Path $certDir "openssl.cnf"
$configContent | Out-File -FilePath $configPath -Encoding ASCII
Write-Host "✅ Configuration OpenSSL créée" -ForegroundColor Green
Write-Host ""

# 5. Générer la clé privée
Write-Host "🔑 Génération de la clé privée..." -ForegroundColor Cyan
$keyPath = Join-Path $certDir "key.pem"
& openssl genrsa -out $keyPath 2048 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Clé privée générée : certs/key.pem" -ForegroundColor Green
} else {
    Write-Host "   ❌ Erreur lors de la génération de la clé" -ForegroundColor Red
    exit 1
}

# 6. Générer le certificat
Write-Host "📜 Génération du certificat..." -ForegroundColor Cyan
$certPath = Join-Path $certDir "cert.pem"
& openssl req -new -x509 -key $keyPath -out $certPath -days 365 -config $configPath 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Certificat généré : certs/cert.pem" -ForegroundColor Green
    Write-Host "   📅 Valide pendant 365 jours" -ForegroundColor Yellow
} else {
    Write-Host "   ❌ Erreur lors de la génération du certificat" -ForegroundColor Red
    exit 1
}

Write-Host ""

# 7. Afficher les informations du certificat
Write-Host "📋 Informations du certificat :" -ForegroundColor Cyan
& openssl x509 -in $certPath -noout -subject -dates

Write-Host ""

# 8. Instructions
Write-Host "✅ Certificat SSL configuré !" -ForegroundColor Green
Write-Host ""
Write-Host "📱 Pour utiliser HTTPS sur votre téléphone :" -ForegroundColor Cyan
Write-Host "   1. Le serveur va maintenant démarrer sur https://..." -ForegroundColor White
Write-Host "   2. Sur votre téléphone, acceptez l'avertissement de sécurité" -ForegroundColor White
Write-Host "   3. Accédez à l'une de ces URLs :" -ForegroundColor White
Write-Host ""
foreach ($ip in $ips) {
    if ($ip -like "100.72.*" -or $ip -like "192.168.*" -or $ip -eq "localhost") {
        Write-Host "      https://${ip}:8443" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "⚠️  Avertissement de sécurité normal (certificat auto-signé)" -ForegroundColor Yellow
Write-Host "   • Chrome/Edge : Cliquez sur 'Avancé' puis 'Continuer vers le site'" -ForegroundColor White
Write-Host "   • Firefox : Cliquez sur 'Avancé' puis 'Accepter le risque'" -ForegroundColor White
Write-Host "   • Safari : Cliquez sur 'Afficher les détails' puis 'Visiter ce site web'" -ForegroundColor White

Write-Host ""
Write-Host "🚀 Redémarrez maintenant le serveur pour activer HTTPS" -ForegroundColor Cyan
Write-Host ""

pause
