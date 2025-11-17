# ========================================================================
# Démarrage rapide HomeOne avec configuration multi-domaines
# ========================================================================

Write-Host ""
Write-Host "🏠 ═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "🏠   Démarrage de HomeOne" -ForegroundColor Cyan
Write-Host "🏠 ═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

$homeoneDir = $PSScriptRoot

# 1. Vérifier la configuration multi-domaines
Write-Host "🔍 Vérification de la configuration..." -ForegroundColor Yellow

$hostsPath = "$env:SystemRoot\System32\drivers\etc\hosts"
$hostsContent = Get-Content $hostsPath -ErrorAction SilentlyContinue
$hasHomeOne = $hostsContent | Where-Object { $_ -like "*homeone.*" }

if (-not $hasHomeOne) {
    Write-Host ""
    Write-Host "⚠️  Configuration multi-domaines non détectée" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "📝 Pour configurer les noms de domaine (homeone.local, homeone.wifi, homeone.web) :" -ForegroundColor Cyan
    Write-Host "   Clic droit sur setup-multi-domains.ps1 > Exécuter en tant qu'administrateur" -ForegroundColor White
    Write-Host ""
    Write-Host "💡 Vous pouvez continuer sans cette configuration (accès par IP)" -ForegroundColor DarkGray
    Write-Host ""
    
    $response = Read-Host "Continuer le démarrage ? (o/n)"
    if ($response -ne "o" -and $response -ne "O" -and $response -ne "oui") {
        Write-Host "❌ Démarrage annulé" -ForegroundColor Red
        pause
        exit 0
    }
} else {
    Write-Host "   ✅ Configuration multi-domaines détectée" -ForegroundColor Green
    
    # Afficher les domaines configurés
    $domains = $hostsContent | Where-Object { $_ -like "*homeone.*" } | ForEach-Object {
        if ($_ -match "(\d+\.\d+\.\d+\.\d+)\s+(homeone\.\w+)") {
            "      $($matches[2]) → $($matches[1])"
        }
    }
    if ($domains) {
        Write-Host $domains -ForegroundColor DarkGray
    }
}

Write-Host ""

# 2. Arrêter les processus existants
Write-Host "🛑 Arrêt des processus existants..." -ForegroundColor Yellow

$pythonProcs = Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.Path -like '*homeflix*' }
$nodeProcs = Get-Process node -ErrorAction SilentlyContinue

if ($pythonProcs) {
    $pythonProcs | Stop-Process -Force
    Write-Host "   ✅ Serveur Python arrêté" -ForegroundColor Green
}

if ($nodeProcs) {
    $nodeProcs | Stop-Process -Force
    Write-Host "   ✅ Serveur Vite arrêté" -ForegroundColor Green
}

Start-Sleep -Seconds 2
Write-Host ""

# 3. Démarrer le serveur Python
Write-Host "🐍 Démarrage du serveur FastAPI..." -ForegroundColor Yellow

$serverPath = Join-Path $homeoneDir "server"
$pythonExe = Join-Path $homeoneDir ".venv310\Scripts\python.exe"

if (-not (Test-Path $pythonExe)) {
    Write-Host "   ❌ Python venv non trouvé : $pythonExe" -ForegroundColor Red
    Write-Host "   💡 Exécutez d'abord : .\install.ps1" -ForegroundColor Yellow
    pause
    exit 1
}

# Démarrer le serveur en arrière-plan
$serverJob = Start-Process -FilePath $pythonExe `
    -ArgumentList "main.py" `
    -WorkingDirectory $serverPath `
    -WindowStyle Hidden `
    -PassThru

Write-Host "   ⏳ Démarrage en cours..." -ForegroundColor DarkGray
Start-Sleep -Seconds 3

# Vérifier que le serveur est démarré
$serverRunning = Get-Process -Id $serverJob.Id -ErrorAction SilentlyContinue

if ($serverRunning) {
    # Détecter le port utilisé (8000 ou 8443 avec HTTPS)
    $port8000 = netstat -ano | findstr ":8000" | findstr "LISTENING"
    $port8443 = netstat -ano | findstr ":8443" | findstr "LISTENING"
    
    if ($port8443) {
        Write-Host "   ✅ Serveur démarré en mode HTTPS (port 8443)" -ForegroundColor Green
        $apiProtocol = "https"
        $apiPort = 8443
    } elseif ($port8000) {
        Write-Host "   ✅ Serveur démarré en mode HTTP (port 8000)" -ForegroundColor Green
        $apiProtocol = "http"
        $apiPort = 8000
    } else {
        Write-Host "   ⚠️  Serveur démarré mais port non détecté" -ForegroundColor Yellow
        $apiProtocol = "http"
        $apiPort = 8000
    }
} else {
    Write-Host "   ❌ Échec du démarrage du serveur" -ForegroundColor Red
    pause
    exit 1
}

Write-Host ""

# 4. Démarrer le serveur Vite
Write-Host "⚡ Démarrage du serveur Vite..." -ForegroundColor Yellow

$clientPath = Join-Path $homeoneDir "client"

# Vérifier que node_modules existe
if (-not (Test-Path (Join-Path $clientPath "node_modules"))) {
    Write-Host "   ⚠️  node_modules non trouvé, installation..." -ForegroundColor Yellow
    Set-Location $clientPath
    npm install
    Set-Location $homeoneDir
}

# Démarrer Vite en arrière-plan
$viteJob = Start-Process -FilePath "npm.cmd" `
    -ArgumentList "run", "dev" `
    -WorkingDirectory $clientPath `
    -WindowStyle Hidden `
    -PassThru

Write-Host "   ⏳ Démarrage en cours..." -ForegroundColor DarkGray
Start-Sleep -Seconds 4

# Vérifier que Vite est démarré
$viteRunning = Get-Process -Id $viteJob.Id -ErrorAction SilentlyContinue
$port5173 = netstat -ano | findstr ":5173" | findstr "LISTENING"

if ($viteRunning -and $port5173) {
    # Détecter si Vite utilise HTTPS
    $certDir = Join-Path $homeoneDir "certs"
    $certExists = (Test-Path (Join-Path $certDir "cert.pem"))
    
    if ($certExists) {
        Write-Host "   ✅ Serveur Vite démarré en mode HTTPS (port 5173)" -ForegroundColor Green
        $clientProtocol = "https"
    } else {
        Write-Host "   ✅ Serveur Vite démarré en mode HTTP (port 5173)" -ForegroundColor Green
        $clientProtocol = "http"
    }
} else {
    Write-Host "   ❌ Échec du démarrage de Vite" -ForegroundColor Red
    $serverJob | Stop-Process -Force
    pause
    exit 1
}

Write-Host ""

# 5. Détecter les URLs disponibles
Write-Host "🌐 Détection des URLs d'accès..." -ForegroundColor Yellow
Write-Host ""

$adapters = Get-NetIPAddress -AddressFamily IPv4 | Where-Object { 
    $_.IPAddress -notlike "127.*" -and $_.IPAddress -notlike "169.254.*"
}

$urls = @()

# URL locale
$urls += @{
    Name = "🏠 Local (ce PC)"
    URL = "${clientProtocol}://localhost:5173"
    Domain = "${clientProtocol}://homeone.local:5173"
    Color = "White"
}

# URLs réseau
foreach ($adapter in $adapters) {
    $ip = $adapter.IPAddress
    $ifInfo = Get-NetAdapter -InterfaceIndex $adapter.InterfaceIndex
    
    if ($ip -like "100.*" -or $ifInfo.InterfaceDescription -like "*Tailscale*") {
        $urls += @{
            Name = "🌍 Distant (Tailscale)"
            URL = "${clientProtocol}://${ip}:5173"
            Domain = "${clientProtocol}://homeone.web:5173"
            Color = "Cyan"
        }
    }
    elseif ($ifInfo.PhysicalMediaType -eq "Native 802.11" -or $ifInfo.InterfaceDescription -like "*Wi-Fi*") {
        $urls += @{
            Name = "📡 WiFi"
            URL = "${clientProtocol}://${ip}:5173"
            Domain = "${clientProtocol}://homeone.wifi:5173"
            Color = "Yellow"
        }
    }
    elseif ($ifInfo.PhysicalMediaType -eq "802.3" -or $ifInfo.InterfaceDescription -like "*Ethernet*") {
        $urls += @{
            Name = "🔌 Ethernet"
            URL = "${clientProtocol}://${ip}:5173"
            Domain = "${clientProtocol}://homeone.lan:5173"
            Color = "Blue"
        }
    }
}

# Afficher les URLs
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ HomeOne est démarré !" -ForegroundColor Green
Write-Host ""

foreach ($urlInfo in $urls) {
    Write-Host "   $($urlInfo.Name)" -ForegroundColor $urlInfo.Color
    Write-Host "      $($urlInfo.URL)" -ForegroundColor DarkGray
    if ($hasHomeOne -and $urlInfo.Domain) {
        Write-Host "      $($urlInfo.Domain)" -ForegroundColor Green
    }
    Write-Host ""
}

if (-not $hasHomeOne) {
    Write-Host "💡 Pour utiliser les domaines (homeone.wifi, homeone.web, etc.) :" -ForegroundColor Yellow
    Write-Host "   Exécutez : .\setup-multi-domains.ps1 (en tant qu'administrateur)" -ForegroundColor White
    Write-Host ""
}

Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# 6. Ouvrir le navigateur
Write-Host "🌐 Ouverture du navigateur..." -ForegroundColor Yellow

if ($hasHomeOne) {
    Start-Process "${clientProtocol}://homeone.local:5173"
} else {
    Start-Process "${clientProtocol}://localhost:5173"
}

Write-Host ""
Write-Host "✨ Le nom affiché dans le navigateur s'adaptera automatiquement selon" -ForegroundColor Cyan
Write-Host "   votre type de connexion (homeone.wifi, homeone.web, etc.)" -ForegroundColor Cyan
Write-Host ""
Write-Host "📊 Pour arrêter les serveurs :" -ForegroundColor Yellow
Write-Host "   Fermez cette fenêtre ou appuyez sur Ctrl+C" -ForegroundColor White
Write-Host ""

# 7. Garder la fenêtre ouverte et surveiller les processus
Write-Host "⏳ Serveurs en cours d'exécution..." -ForegroundColor Green
Write-Host "   Appuyez sur Ctrl+C pour arrêter" -ForegroundColor DarkGray
Write-Host ""

try {
    while ($true) {
        Start-Sleep -Seconds 5
        
        # Vérifier que les processus tournent toujours
        $serverAlive = Get-Process -Id $serverJob.Id -ErrorAction SilentlyContinue
        $viteAlive = Get-Process -Id $viteJob.Id -ErrorAction SilentlyContinue
        
        if (-not $serverAlive) {
            Write-Host "❌ Le serveur Python s'est arrêté" -ForegroundColor Red
            break
        }
        
        if (-not $viteAlive) {
            Write-Host "❌ Le serveur Vite s'est arrêté" -ForegroundColor Red
            break
        }
    }
} finally {
    Write-Host ""
    Write-Host "🛑 Arrêt des serveurs..." -ForegroundColor Yellow
    
    if ($serverJob) {
        Stop-Process -Id $serverJob.Id -Force -ErrorAction SilentlyContinue
        Write-Host "   ✅ Serveur Python arrêté" -ForegroundColor Green
    }
    
    if ($viteJob) {
        Stop-Process -Id $viteJob.Id -Force -ErrorAction SilentlyContinue
        Write-Host "   ✅ Serveur Vite arrêté" -ForegroundColor Green
    }
    
    Write-Host ""
    Write-Host "👋 HomeOne arrêté proprement" -ForegroundColor Cyan
    Write-Host ""
}
