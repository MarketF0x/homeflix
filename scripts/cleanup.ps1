# Script de nettoyage complet des serveurs Homeflix

Write-Host "🧹 Nettoyage complet des serveurs Homeflix..." -ForegroundColor Yellow
Write-Host ""

# Arrêter tous les jobs PowerShell
Write-Host "1. Arrêt des jobs PowerShell..." -ForegroundColor Cyan
Get-Job | Stop-Job -ErrorAction SilentlyContinue
Get-Job | Remove-Job -ErrorAction SilentlyContinue
Write-Host "   ✅ Jobs PowerShell arrêtés" -ForegroundColor Green

# Tuer tous les processus Node.js
Write-Host "2. Arrêt des processus Node.js..." -ForegroundColor Cyan
$nodeProcesses = Get-Process -Name "node" -ErrorAction SilentlyContinue
if ($nodeProcesses) {
    Write-Host "   Arrêt de $($nodeProcesses.Count) processus Node..." -ForegroundColor Yellow
    $nodeProcesses | Stop-Process -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
    Write-Host "   ✅ Processus Node arrêtés" -ForegroundColor Green
} else {
    Write-Host "   ℹ️  Aucun processus Node en cours" -ForegroundColor Gray
}

# Tuer tous les processus Python
Write-Host "3. Arrêt des processus Python..." -ForegroundColor Cyan
$pythonProcesses = Get-Process -Name "python" -ErrorAction SilentlyContinue
if ($pythonProcesses) {
    Write-Host "   Arrêt de $($pythonProcesses.Count) processus Python..." -ForegroundColor Yellow
    $pythonProcesses | Stop-Process -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
    Write-Host "   ✅ Processus Python arrêtés" -ForegroundColor Green
} else {
    Write-Host "   ℹ️  Aucun processus Python en cours" -ForegroundColor Gray
}

# Libérer le port 5173 (Vite)
Write-Host "4. Libération du port 5173 (Frontend)..." -ForegroundColor Cyan
$port5173 = Get-NetTCPConnection -LocalPort 5173 -State Listen -ErrorAction SilentlyContinue
if ($port5173) {
    $processId = $port5173.OwningProcess
    Write-Host "   Port 5173 utilisé par le processus $processId" -ForegroundColor Yellow
    Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 1
    Write-Host "   ✅ Port 5173 libéré" -ForegroundColor Green
} else {
    Write-Host "   ℹ️  Port 5173 déjà libre" -ForegroundColor Gray
}

# Libérer le port 8000 (FastAPI)
Write-Host "5. Libération du port 8000 (Backend)..." -ForegroundColor Cyan
$port8000 = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
if ($port8000) {
    $processId = $port8000.OwningProcess
    Write-Host "   Port 8000 utilisé par le processus $processId" -ForegroundColor Yellow
    Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 1
    Write-Host "   ✅ Port 8000 libéré" -ForegroundColor Green
} else {
    Write-Host "   ℹ️  Port 8000 déjà libre" -ForegroundColor Gray
}

# Vérification finale
Write-Host ""
Write-Host "6. Vérification finale..." -ForegroundColor Cyan
$remainingNode = Get-Process -Name "node" -ErrorAction SilentlyContinue
$remainingPython = Get-Process -Name "python" -ErrorAction SilentlyContinue
$remaining5173 = Get-NetTCPConnection -LocalPort 5173 -ErrorAction SilentlyContinue
$remaining8000 = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue

if ($remainingNode -or $remainingPython -or $remaining5173 -or $remaining8000) {
    Write-Host "   ⚠️  Quelques processus persistent encore..." -ForegroundColor Yellow
    if ($remainingNode) { Write-Host "      - $($remainingNode.Count) processus Node" -ForegroundColor Yellow }
    if ($remainingPython) { Write-Host "      - $($remainingPython.Count) processus Python" -ForegroundColor Yellow }
    if ($remaining5173) { Write-Host "      - Port 5173 encore occupé" -ForegroundColor Yellow }
    if ($remaining8000) { Write-Host "      - Port 8000 encore occupé" -ForegroundColor Yellow }
} else {
    Write-Host "   ✅ Tout est propre !" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "✅ Nettoyage terminé" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Vous pouvez maintenant relancer les serveurs:" -ForegroundColor Cyan
Write-Host "   .\scripts\watch-servers.ps1" -ForegroundColor White
