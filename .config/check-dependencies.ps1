# ============================================================================
# Verification des dependances Homeflix (Serveur)
# ============================================================================

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "  VERIFICATION DES DEPENDANCES SERVEUR" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

# Detecter Python
Write-Host "[1/3] Detection de Python..." -ForegroundColor Yellow

$pythonCmd = $null
$pythonVersion = $null

# Essayer differentes commandes Python
foreach ($cmd in @("python", "python3", "py")) {
    try {
        $version = & $cmd --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            $pythonCmd = $cmd
            $pythonVersion = $version
            break
        }
    } catch {
        continue
    }
}

if ($pythonCmd) {
    Write-Host "   OK: Python detecte - $pythonVersion" -ForegroundColor Green
    
    # Verifier la version (minimum 3.8)
    if ($pythonVersion -match "Python (\d+)\.(\d+)") {
        $major = [int]$matches[1]
        $minor = [int]$matches[2]
        
        if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 8)) {
            Write-Host "   ATTENTION: Python 3.8+ recommande (vous avez $major.$minor)" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host "   ERREUR: Python non detecte!" -ForegroundColor Red
    Write-Host "   Installez Python 3.8+ depuis https://www.python.org" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}
Write-Host ""

# Verifier les packages Python
Write-Host "[2/3] Verification des packages Python..." -ForegroundColor Yellow

$requiredPackages = @(
    "fastapi",
    "uvicorn",
    "sqlalchemy",
    "pydantic",
    "requests",
    "pillow"
)

$missingPackages = @()
$installedCount = 0

foreach ($package in $requiredPackages) {
    try {
        $checkResult = & $pythonCmd -c "import $package; print('OK')" 2>&1
        if ($checkResult -match "OK") {
            Write-Host "   OK: $package" -ForegroundColor Green
            $installedCount++
        } else {
            Write-Host "   MANQUANT: $package" -ForegroundColor Red
            $missingPackages += $package
        }
    } catch {
        Write-Host "   MANQUANT: $package" -ForegroundColor Red
        $missingPackages += $package
    }
}

Write-Host ""
Write-Host "   Packages installes: $installedCount/$($requiredPackages.Count)" -ForegroundColor $(if ($installedCount -eq $requiredPackages.Count) { "Green" } else { "Yellow" })
Write-Host ""

if ($missingPackages.Count -gt 0) {
    Write-Host "   >> Pour installer les packages manquants:" -ForegroundColor Cyan
    Write-Host "      cd server" -ForegroundColor White
    Write-Host "      pip install -r requirements.txt" -ForegroundColor White
    Write-Host ""
}

# Verifier Node.js
Write-Host "[3/3] Detection de Node.js..." -ForegroundColor Yellow

$nodeCmd = $null
$nodeVersion = $null

try {
    $nodeVersion = node --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        $nodeCmd = "node"
        Write-Host "   OK: Node.js detecte - $nodeVersion" -ForegroundColor Green
        
        # Verifier npm
        $npmVersion = npm --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   OK: npm detecte - v$npmVersion" -ForegroundColor Green
        }
    }
} catch {
    Write-Host "   ERREUR: Node.js non detecte!" -ForegroundColor Red
    Write-Host "   Installez Node.js depuis https://nodejs.org" -ForegroundColor Yellow
}
Write-Host ""

# Verifier les modules Node.js du client
if ($nodeCmd) {
    Write-Host "[BONUS] Verification des modules client..." -ForegroundColor Yellow
    
    $nodeModulesPath = "client\node_modules"
    if (Test-Path $nodeModulesPath) {
        Write-Host "   OK: Modules Node.js installes" -ForegroundColor Green
    } else {
        Write-Host "   MANQUANT: Modules Node.js" -ForegroundColor Red
        Write-Host ""
        Write-Host "   >> Pour installer:" -ForegroundColor Cyan
        Write-Host "      cd client" -ForegroundColor White
        Write-Host "      npm install" -ForegroundColor White
    }
    Write-Host ""
}

# Verifier FFmpeg (optionnel mais recommande)
Write-Host "[BONUS] Detection de FFmpeg..." -ForegroundColor Yellow

$ffmpegPath = Get-Command ffmpeg -ErrorAction SilentlyContinue

if ($ffmpegPath) {
    $ffmpegVersion = ffmpeg -version 2>&1 | Select-Object -First 1
    Write-Host "   OK: FFmpeg detecte" -ForegroundColor Green
    Write-Host "       $ffmpegVersion" -ForegroundColor Gray
} else {
    Write-Host "   OPTIONNEL: FFmpeg non detecte" -ForegroundColor Yellow
    Write-Host "   FFmpeg permet la generation locale de miniatures" -ForegroundColor Gray
    Write-Host "   >> Pour installer: python check_and_install_ffmpeg.py" -ForegroundColor Cyan
}
Write-Host ""

# Resume
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "  RESUME" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

$allOk = $pythonCmd -and ($missingPackages.Count -eq 0) -and $nodeCmd

if ($allOk) {
    Write-Host "SUCCES: Toutes les dependances sont installees!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Vous pouvez demarrer Homeflix:" -ForegroundColor White
    Write-Host "   .\start-dev.ps1" -ForegroundColor Cyan
} else {
    Write-Host "ATTENTION: Certaines dependances manquent" -ForegroundColor Yellow
    Write-Host ""
    
    if (-not $pythonCmd) {
        Write-Host "1. Installez Python 3.8+" -ForegroundColor White
    }
    
    if ($missingPackages.Count -gt 0) {
        Write-Host "2. Installez les packages Python:" -ForegroundColor White
        Write-Host "   cd server" -ForegroundColor Cyan
        Write-Host "   pip install -r requirements.txt" -ForegroundColor Cyan
    }
    
    if (-not $nodeCmd) {
        Write-Host "3. Installez Node.js" -ForegroundColor White
    }
}

Write-Host ""
Write-Host "===============================================" -ForegroundColor DarkGray
Write-Host ""
