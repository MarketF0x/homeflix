# Démarre le serveur Python et le client Vite, et nettoie tout à la fermeture
# Usage: powershell -ExecutionPolicy Bypass -File .\start-dev.ps1

$ErrorActionPreference = 'Stop'

# 1) Purge préalable des ports/dev serveurs
& .\scripts\cleanup-dev.ps1 -Silent -Ports @(5173,5174,8000) | Out-Null

# 2) Démarrage serveur Python (FastAPI)
Write-Host "[START] Serveur Python" -ForegroundColor Green
$serverProc = Start-Process -FilePath "python" -ArgumentList "main.py" -WorkingDirectory "server" -PassThru -WindowStyle Hidden

# 3) Démarrage client Vite sur port 5173 (échec explicite si pris)
Write-Host "[START] Client Vite (port 5173)" -ForegroundColor Green
Push-Location client
$env:VITE_PORT = "5173"

try {
    # Lancement bloquant pour capter Ctrl+C dans ce terminal
    npm run dev
}
finally {
    Pop-Location
    Write-Host "[CLEANUP] Arrêt en cours..." -ForegroundColor Yellow
    # Tuer serveur Python si encore actif
    if ($serverProc -and -not $serverProc.HasExited) {
        try { $serverProc | Stop-Process -Force -ErrorAction SilentlyContinue } catch {}
    }
    # Purge ports et processus résiduels
    & .\scripts\cleanup-dev.ps1 -Silent -Ports @(5173,5174,8000) | Out-Null
    Write-Host "[DONE] Nettoyage terminé." -ForegroundColor Green
}
