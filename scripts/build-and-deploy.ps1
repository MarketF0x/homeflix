# Orchestrateur: build client puis déploiement vers Electron
param(
    [switch]$NoRestart,
    [switch]$SkipServerCopy
)

$ErrorActionPreference = 'Stop'

function Resolve-Root {
    param([string]$pwdPath)
    if (Test-Path (Join-Path $pwdPath 'client')) { return $pwdPath }
    $up = Resolve-Path (Join-Path $pwdPath '..')
    if (Test-Path (Join-Path $up 'client')) { return $up }
    return $pwdPath
}

$root = Resolve-Root -pwdPath (Get-Location).Path

# Build client
Write-Host "[BUILD] Client (vite)" -ForegroundColor Cyan
Push-Location (Join-Path $root 'client')
try {
    npm run build
} finally {
    Pop-Location
}
Write-Host "[OK] Build terminé" -ForegroundColor Green

# Deploy vers Electron
$deployScript = Join-Path $root 'scripts\\deploy-client-electron.ps1'
if (!(Test-Path $deployScript)) { throw "Script de déploiement introuvable: $deployScript" }

Write-Host "[DEPLOY] Copie vers Electron + (re)lancement" -ForegroundColor Cyan
$flags = @()
if ($NoRestart) { $flags += '-NoRestart' }
if ($SkipServerCopy) { $flags += '-SkipServerCopy' }

powershell -ExecutionPolicy Bypass -File $deployScript @flags

Write-Host "[DONE] Build + Deploy terminé" -ForegroundColor Green
