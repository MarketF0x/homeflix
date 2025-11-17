param(
    [switch]$NoRestart,
    [switch]$SkipServerCopy
)

# Détermine la racine du projet en fonction de l'endroit où la commande est lancée
$pwdPath = (Get-Location).Path

function Resolve-Root {
    param([string]$pwdPath)
    if (Test-Path (Join-Path $pwdPath 'client\dist')) { return $pwdPath }
    $up = Resolve-Path (Join-Path $pwdPath '..')
    if (Test-Path (Join-Path $up 'client\dist')) { return $up }
    return $pwdPath
}

$root = (Resolve-Root -pwdPath $pwdPath)

# Localise client/dist
$clientDist = $null
if (Test-Path (Join-Path $root 'client\dist')) {
    $clientDist = (Join-Path $root 'client\dist\*')
} elseif (Test-Path (Join-Path $root 'dist')) {
    $clientDist = (Join-Path $root 'dist\*')
} else {
    throw "Dossier 'dist' introuvable sous: `n - $($root)\client\dist `n - $($root)\dist"
}

# Localise resources Electron
$resourcesRoot = $null
if (Test-Path (Join-Path $root 'electron\dist\win-unpacked\resources')) {
    $resourcesRoot = (Join-Path $root 'electron\dist\win-unpacked\resources')
} elseif (Test-Path (Join-Path $root '..\electron\dist\win-unpacked\resources')) {
    $resourcesRoot = (Resolve-Path (Join-Path $root '..\electron\dist\win-unpacked\resources')).Path
} else {
    throw "Ressources Electron introuvables depuis: $root"
}

$dest = Join-Path $resourcesRoot 'client\dist'
if (!(Test-Path $dest)) { New-Item -ItemType Directory -Force -Path $dest | Out-Null }

Write-Host "[COPY] $clientDist -> $dest"
Copy-Item $clientDist $dest -Recurse -Force
Write-Host "[OK] Copie des fichiers client terminée"

# Optionnel: copier le serveur si présent
if (-not $SkipServerCopy) {
    $serverSrc = Join-Path $root 'server\\main.py'
    $serverDestDir = Join-Path $resourcesRoot 'server'
    if (Test-Path $serverSrc) {
        if (!(Test-Path $serverDestDir)) { New-Item -ItemType Directory -Force -Path $serverDestDir | Out-Null }
        Copy-Item $serverSrc (Join-Path $serverDestDir 'main.py') -Force
        Write-Host "[OK] Copie server/main.py -> $serverDestDir"
    } else {
        Write-Host "[SKIP] server/main.py non trouvé, étape ignorée"
    }
}

# Redémarre l'app si demandé
if (-not $NoRestart) {
    Get-Process Homeflix,python -ErrorAction SilentlyContinue | Stop-Process -Force
    Start-Sleep -Seconds 2

    $appCandidates = @(
        (Join-Path $root 'electron\dist\win-unpacked\Homeflix.exe'),
        (Join-Path (Split-Path $resourcesRoot -Parent) 'Homeflix.exe')
    )

    $appPath = $appCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
    if (-not $appPath) {
        $found = Get-ChildItem (Join-Path $root 'electron\dist') -Recurse -Filter 'Homeflix.exe' -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty FullName
        if ($found) { $appPath = $found }
    }

    if ($appPath) {
        Write-Host "[START] Lancement: $appPath"
        Start-Process $appPath
    } else {
        Write-Error "Homeflix.exe non trouvé sous electron\\dist"
    }
}

Write-Host "[DONE] Déploiement client -> Electron terminé"
