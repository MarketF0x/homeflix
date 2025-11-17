# Nettoyage des processus Node et Python liés au dev Homeflix
# A exécuter quand vous fermez l'application pour libérer les ports (5173, 8000, etc.)

param(
    [switch]$Silent,
    [switch]$DryRun,
    [int[]]$Ports = @(5173, 5174, 8000)
)

function Write-Info($msg) {
    if (-not $Silent) { Write-Host "[INFO] $msg" -ForegroundColor Cyan }
}

function Get-PortPids([int]$Port) {
    $conns = Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction SilentlyContinue
    if ($conns) { $conns | Select-Object -ExpandProperty OwningProcess | Sort-Object -Unique }
}

# 1. Déterminer PID node / python associés
$nodePids = (Get-Process -ErrorAction SilentlyContinue | Where-Object { $_.ProcessName -like 'node*' }).Id
$pythonPids = (Get-Process -ErrorAction SilentlyContinue | Where-Object { $_.ProcessName -like 'python*' }).Id

# 2. Ajouter les PIDs écoutant sur les ports cibles
$portPids = @()
foreach ($p in $Ports) {
    $pids = Get-PortPids -Port $p
    if ($pids) { $portPids += $pids }
}
$portPids = $portPids | Sort-Object -Unique

# Fusion
$targetPids = (@($nodePids) + @($pythonPids) + @($portPids)) | Sort-Object -Unique | Where-Object { $_ }

if (-not $targetPids -or $targetPids.Count -eq 0) {
    Write-Info "Aucun processus Node/Python/port cible à arrêter."
    exit 0
}

Write-Info "Processus détectés: $($targetPids -join ', ')"

if ($DryRun) {
    Write-Info "DryRun actif: aucun arrêt effectué."
    exit 0
}

# 3. Arrêt forcé
foreach ($processId in $targetPids) {
    try {
        Stop-Process -Id $processId -Force -ErrorAction Stop
        Write-Info "Arrêt PID $processId OK"
    } catch {
        Write-Info "Échec arrêt PID $processId : $_"
    }
}

Write-Info "Nettoyage terminé. Tous les ports devraient être libérés."
