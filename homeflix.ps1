# HOMEFLIX - LANCEUR INTELLIGENT
# Demarre les serveurs et ouvre le navigateur
# Arrete les serveurs quand on ferme la fenetre (local uniquement)

param(
    [Parameter(Mandatory=$false)]
    [switch]$FromShortcut
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$venvPython = "$projectRoot\.venv310\Scripts\python.exe"

# Fonction pour obtenir les adresses IP du systeme
function Get-SystemIPs {
    $ips = @{
        Local = "localhost"
        WiFi = $null
        Tailscale = $null
    }
    
    # Recuperer toutes les interfaces reseau actives
    $adapters = Get-NetIPAddress -AddressFamily IPv4 -PrefixOrigin Dhcp,Manual -ErrorAction SilentlyContinue | 
                Where-Object { $_.IPAddress -notmatch '^169\.254\.' -and $_.IPAddress -ne '127.0.0.1' }
    
    foreach ($adapter in $adapters) {
        $ip = $adapter.IPAddress
        
        # Detecter l'IP WiFi (192.168.x.x ou 10.x.x.x)
        if ($ip -match '^192\.168\.' -or $ip -match '^10\.') {
            $ips.WiFi = $ip
        }
        # Detecter l'IP Tailscale (100.x.x.x)
        elseif ($ip -match '^100\.') {
            $ips.Tailscale = $ip
        }
    }
    
    return $ips
}

# Fonction pour creer/mettre a jour le fichier de configuration des IPs
function Update-IPConfig {
    $ips = Get-SystemIPs
    
    $config = @{
        LastUpdate = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
        LocalURL = "http://localhost:5173"
        WiFiURL = if ($ips.WiFi) { "http://$($ips.WiFi):5173" } else { $null }
        TailscaleURL = if ($ips.Tailscale) { "http://$($ips.Tailscale):5173" } else { $null }
    }
    
    $configPath = "$projectRoot\server\static\network-config.json"
    $configDir = Split-Path -Parent $configPath
    
    if (-not (Test-Path $configDir)) {
        New-Item -ItemType Directory -Path $configDir -Force | Out-Null
    }
    
    $config | ConvertTo-Json | Set-Content -Path $configPath -Encoding UTF8
    
    return $config
}

function Test-ServersRunning {
    try {
        # Methode plus rapide - tester directement les ports
        $backendConn = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
        $frontendConn = Get-NetTCPConnection -LocalPort 5173 -State Listen -ErrorAction SilentlyContinue
        $backend = $null -ne $backendConn
        $frontend = $null -ne $frontendConn
        return ($backend -and $frontend)
    } catch {
        return $false
    }
}

function Start-Servers {
    Write-Host "Demarrage des serveurs HomeFlix..." -ForegroundColor Cyan
    
    # Nettoyer les anciens processus
    Get-Process -Name python,node -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
    
    # Liberer les ports
    $ports = @(8000, 5173)
    foreach ($port in $ports) {
        $connection = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
        if ($connection) {
            $processId = $connection.OwningProcess
            Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
        }
    }
    
    # Demarrer le Backend
    $backendStartInfo = New-Object System.Diagnostics.ProcessStartInfo
    $backendStartInfo.FileName = $venvPython
    $backendStartInfo.Arguments = "-m uvicorn server.main:app --host 0.0.0.0 --port 8000 --log-level info"
    $backendStartInfo.WorkingDirectory = $projectRoot
    $backendStartInfo.UseShellExecute = $false
    $backendStartInfo.CreateNoWindow = $true
    $backendStartInfo.WindowStyle = [System.Diagnostics.ProcessWindowStyle]::Hidden
    $backendProcess = [System.Diagnostics.Process]::Start($backendStartInfo)
    
    Start-Sleep -Seconds 4
    
    # Demarrer le Frontend
    $frontendStartInfo = New-Object System.Diagnostics.ProcessStartInfo
    $frontendStartInfo.FileName = "cmd.exe"
    $frontendStartInfo.Arguments = "/c npm run dev"
    $frontendStartInfo.WorkingDirectory = "$projectRoot\client"
    $frontendStartInfo.UseShellExecute = $false
    $frontendStartInfo.CreateNoWindow = $true
    $frontendStartInfo.WindowStyle = [System.Diagnostics.ProcessWindowStyle]::Hidden
    $frontendProcess = [System.Diagnostics.Process]::Start($frontendStartInfo)
    
    Start-Sleep -Seconds 5
    
    Write-Host "Serveurs demarres (Backend PID: $($backendProcess.Id), Frontend PID: $($frontendProcess.Id))" -ForegroundColor Green
}

function Stop-Servers {
    Write-Host "Arret des serveurs HomeFlix..." -ForegroundColor Yellow
    Get-Process -Name python,node -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
    Write-Host "Serveurs arretes" -ForegroundColor Green
}

# SCRIPT PRINCIPAL
Clear-Host
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "         HOMEFLIX" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Mettre a jour la configuration des IPs
Write-Host "Detection des adresses IP..." -ForegroundColor Cyan
$ipConfig = Update-IPConfig

Write-Host "  Local: $($ipConfig.LocalURL)" -ForegroundColor Gray
if ($ipConfig.WiFiURL) {
    Write-Host "  WiFi: $($ipConfig.WiFiURL)" -ForegroundColor Gray
}
if ($ipConfig.TailscaleURL) {
    Write-Host "  Internet: $($ipConfig.TailscaleURL)" -ForegroundColor Gray
}
Write-Host ""

# Verifier si les serveurs tournent
$serversRunning = Test-ServersRunning

if (-not $serversRunning) {
    Write-Host "Aucun serveur detecte, demarrage..." -ForegroundColor Yellow
    Write-Host ""
    Start-Servers
} else {
    Write-Host "Serveurs deja en cours d'execution" -ForegroundColor Green
}

Write-Host ""
Write-Host "Ouverture de http://localhost:5173" -ForegroundColor Cyan
Write-Host ""

# Ouvrir le navigateur
Start-Sleep -Seconds 2
Start-Process "http://localhost:5173"

# Si connexion locale (via raccourci), attendre Ctrl+C pour arreter
if ($FromShortcut) {
    Write-Host "Connexion locale detectee" -ForegroundColor Yellow
    Write-Host "  -> Appuyez sur Ctrl+C pour arreter HomeFlix" -ForegroundColor Gray
    Write-Host ""
    
    # Creer un fichier de verrouillage
    $lockFile = "$projectRoot\.homeflix.lock"
    Set-Content -Path $lockFile -Value (Get-Date).ToString()
    
    # Attendre Ctrl+C
    try {
        Write-Host "Serveurs actifs - Appuyez sur Ctrl+C pour arreter..." -ForegroundColor Gray
        while ($true) {
            Start-Sleep -Seconds 1
        }
    } finally {
        # Nettoyer et arreter les serveurs
        Remove-Item $lockFile -Force -ErrorAction SilentlyContinue
        Write-Host ""
        Stop-Servers
    }
} else {
    Write-Host "Vous pouvez fermer cette fenetre." -ForegroundColor Green
    Write-Host "Les serveurs restent actifs." -ForegroundColor Gray
    Start-Sleep -Seconds 3
}
