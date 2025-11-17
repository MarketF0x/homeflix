# Script pour arrêter proprement la version DEV de Homeflix
# Tue tous les processus Python et Node.js liés à Homeflix

Write-Host "`n[INFO] Arrêt de la version DEV..." -ForegroundColor Cyan

# Arrêter les processus Python (backend)
$pythonProcesses = Get-Process -Name python -ErrorAction SilentlyContinue | Where-Object {
    $_.Path -like "*homeflix*" -or $_.CommandLine -like "*main.py*"
}

if ($pythonProcesses) {
    Write-Host "[INFO] Arrêt du backend Python..." -ForegroundColor Yellow
    $pythonProcesses | Stop-Process -Force
    Write-Host "[OK] Backend arrêté" -ForegroundColor Green
} else {
    Write-Host "[INFO] Aucun backend Python en cours" -ForegroundColor Gray
}

# Arrêter les processus Node (frontend Vite)
$nodeProcesses = Get-Process -Name node -ErrorAction SilentlyContinue | Where-Object {
    $_.Path -like "*homeflix*"
}

if ($nodeProcesses) {
    Write-Host "[INFO] Arrêt du frontend Vite..." -ForegroundColor Yellow
    $nodeProcesses | Stop-Process -Force
    Write-Host "[OK] Frontend arrêté" -ForegroundColor Green
} else {
    Write-Host "[INFO] Aucun frontend Vite en cours" -ForegroundColor Gray
}

# Vérifier les ports
Start-Sleep -Seconds 1

$port8000 = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
$port5173 = Get-NetTCPConnection -LocalPort 5173 -State Listen -ErrorAction SilentlyContinue

if (-not $port8000) {
    Write-Host "[OK] Port 8000 libéré" -ForegroundColor Green
} else {
    Write-Host "[ATTENTION] Port 8000 encore utilisé" -ForegroundColor Yellow
}

if (-not $port5173) {
    Write-Host "[OK] Port 5173 libéré" -ForegroundColor Green
} else {
    Write-Host "[ATTENTION] Port 5173 encore utilisé" -ForegroundColor Yellow
}

Write-Host "`n[OK] Version DEV arrêtée - Vous pouvez maintenant lancer la version STABLE`n" -ForegroundColor Green
