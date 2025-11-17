param(
    [string]$FrontendPath = "client",
    [string]$BackendPath = "server\main.py"
)

Write-Host "=== Surveillance automatique des serveurs Homeflix ===" -ForegroundColor Green
Write-Host "Appuyez sur Ctrl+C pour arrêter la surveillance" -ForegroundColor Yellow
Write-Host ""

# Fonction pour tuer proprement les processus existants
function Stop-ExistingServers {
    Write-Host "🧹 Nettoyage des processus existants..." -ForegroundColor Yellow
    
    # Tuer les processus Node (Vite)
    $nodeProcesses = Get-Process -Name "node" -ErrorAction SilentlyContinue
    if ($nodeProcesses) {
        Write-Host "  - Arrêt de $($nodeProcesses.Count) processus Node.js..." -ForegroundColor Yellow
        $nodeProcesses | Stop-Process -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2
    }
    
    # Tuer les processus Python (serveur backend)
    $pythonProcesses = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object {
        $_.Path -like "*homeflix*" -or $_.CommandLine -like "*main.py*"
    }
    if ($pythonProcesses) {
        Write-Host "  - Arrêt de $($pythonProcesses.Count) processus Python..." -ForegroundColor Yellow
        $pythonProcesses | Stop-Process -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2
    }
    
    # Libérer les ports
    $port5173 = Get-NetTCPConnection -LocalPort 5173 -ErrorAction SilentlyContinue
    if ($port5173) {
        Write-Host "  - Libération du port 5173..." -ForegroundColor Yellow
        $processId = $port5173.OwningProcess
        Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 1
    }
    
    $port8000 = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
    if ($port8000) {
        Write-Host "  - Libération du port 8000..." -ForegroundColor Yellow
        $processId = $port8000.OwningProcess
        Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 1
    }
    
    Write-Host "✅ Nettoyage terminé" -ForegroundColor Green
    Write-Host ""
}

# Nettoyer avant de démarrer
Stop-ExistingServers

$venvPython = "C:\Users\fparo\Desktop\homeflix\.venv310\Scripts\python.exe"
$projectRoot = "C:\Users\fparo\Desktop\homeflix"

# Job Frontend
$frontendJob = Start-Job -ScriptBlock {
    param($root)
    Set-Location $root
    Set-Location "client"
    
    Write-Host "[FRONTEND] Démarrage..." -ForegroundColor Cyan
    & npm run dev
} -ArgumentList $projectRoot

# Job Backend
$backendJob = Start-Job -ScriptBlock {
    param($python, $script, $root)
    Set-Location $root
    
    Write-Host "[BACKEND] Démarrage..." -ForegroundColor Cyan
    & $python $script
} -ArgumentList $venvPython, $BackendPath, $projectRoot

Write-Host "Jobs lancés:" -ForegroundColor Green
Write-Host "  - Frontend (Job $($frontendJob.Id)) sur http://localhost:5173" -ForegroundColor Cyan
Write-Host "  - Backend (Job $($backendJob.Id)) sur http://localhost:8000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Affichage des logs en temps réel..." -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""

# Affichage des logs en temps réel
try {
    while ($true) {
        $frontendJob | Receive-Job
        $backendJob | Receive-Job
        Start-Sleep -Milliseconds 500
    }
} finally {
    Write-Host ""
    Write-Host "🛑 Arrêt des serveurs..." -ForegroundColor Yellow
    
    # Arrêter les jobs
    $frontendJob, $backendJob | Stop-Job -ErrorAction SilentlyContinue
    $frontendJob, $backendJob | Remove-Job -ErrorAction SilentlyContinue
    
    # Nettoyer les processus restants
    Write-Host "🧹 Nettoyage final des processus..." -ForegroundColor Yellow
    Get-Process -Name "node" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
    Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object {
        $_.Path -like "*homeflix*"
    } | Stop-Process -Force -ErrorAction SilentlyContinue
    
    Write-Host "✅ Serveurs arrêtés proprement." -ForegroundColor Green
}
