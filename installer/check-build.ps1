# =====================================================
# HOMEFLIX - SCRIPT DE VÉRIFICATION PRÉ-BUILD
# =====================================================
# Vérifie que tout est prêt avant de créer l'installateur

$ErrorActionPreference = "Continue"

Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "   HOMEFLIX - VÉRIFICATION PRÉ-BUILD" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

$projectRoot = Split-Path -Parent $PSScriptRoot
$allChecks = $true

# =====================================================
# VÉRIFICATION DES FICHIERS ESSENTIELS
# =====================================================

Write-Host "📋 Vérification des fichiers essentiels..." -ForegroundColor Yellow

$requiredFiles = @(
    "client\package.json",
    "client\src\App.jsx",
    "server\main.py",
    "server\requirements.txt",
    "installer\homeflix.iss",
    "installer\build-installer.ps1",
    "installer\detect-environment.ps1",
    "installer\install-dependencies.ps1",
    "installer\configure-system.ps1",
    "installer\locales\fr.json",
    "installer\locales\en.json",
    "installer\locales\es.json",
    "CHANGELOG.md"
)

foreach ($file in $requiredFiles) {
    $fullPath = Join-Path $projectRoot $file
    if (Test-Path $fullPath) {
        Write-Host "   ✅ $file" -ForegroundColor Green
    } else {
        Write-Host "   ❌ MANQUANT: $file" -ForegroundColor Red
        $allChecks = $false
    }
}

Write-Host ""

# =====================================================
# VÉRIFICATION DE LA VERSION
# =====================================================

Write-Host "🔢 Vérification de la version..." -ForegroundColor Yellow

$packageJsonPath = Join-Path $projectRoot "client\package.json"
if (Test-Path $packageJsonPath) {
    $packageJson = Get-Content $packageJsonPath -Raw | ConvertFrom-Json
    $version = $packageJson.version
    
    if ($version -and $version -ne "0.0.0") {
        Write-Host "   ✅ Version: $version" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  Version invalide: $version" -ForegroundColor Yellow
        Write-Host "      Modifier client\package.json" -ForegroundColor Gray
        $allChecks = $false
    }
} else {
    Write-Host "   ❌ package.json introuvable" -ForegroundColor Red
    $allChecks = $false
}

Write-Host ""

# =====================================================
# VÉRIFICATION DU CHANGELOG
# =====================================================

Write-Host "📝 Vérification du CHANGELOG..." -ForegroundColor Yellow

$changelogPath = Join-Path $projectRoot "CHANGELOG.md"
if (Test-Path $changelogPath) {
    $changelog = Get-Content $changelogPath -Raw
    
    if ($changelog -match "\[Unreleased\]|\[Non publié\]") {
        Write-Host "   ⚠️  Version non publiée dans CHANGELOG" -ForegroundColor Yellow
        Write-Host "      Mettre à jour CHANGELOG.md avant release" -ForegroundColor Gray
    } elseif ($changelog -match "\[$version\]") {
        Write-Host "   ✅ Version $version documentée dans CHANGELOG" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  Version $version non trouvée dans CHANGELOG" -ForegroundColor Yellow
        Write-Host "      Ajouter la version dans CHANGELOG.md" -ForegroundColor Gray
    }
} else {
    Write-Host "   ❌ CHANGELOG.md introuvable" -ForegroundColor Red
    $allChecks = $false
}

Write-Host ""

# =====================================================
# VÉRIFICATION DES DÉPENDANCES
# =====================================================

Write-Host "🔧 Vérification des outils..." -ForegroundColor Yellow

# Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "   ✅ Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Python non installé" -ForegroundColor Red
    $allChecks = $false
}

# Node.js
try {
    $nodeVersion = node --version 2>&1
    Write-Host "   ✅ Node.js: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Node.js non installé" -ForegroundColor Red
    $allChecks = $false
}

# npm
try {
    $npmVersion = npm --version 2>&1
    Write-Host "   ✅ npm: v$npmVersion" -ForegroundColor Green
} catch {
    Write-Host "   ❌ npm non installé" -ForegroundColor Red
    $allChecks = $false
}

# InnoSetup
$innoSetupPaths = @(
    "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
    "${env:ProgramFiles}\Inno Setup 6\ISCC.exe"
)

$innoFound = $false
foreach ($path in $innoSetupPaths) {
    if (Test-Path $path) {
        Write-Host "   ✅ InnoSetup: $path" -ForegroundColor Green
        $innoFound = $true
        break
    }
}

if (-not $innoFound) {
    Write-Host "   ❌ InnoSetup non installé" -ForegroundColor Red
    Write-Host "      Télécharger: https://jrsoftware.org/isdl.php" -ForegroundColor Gray
    $allChecks = $false
}

# ps2exe (optionnel)
$ps2exe = Get-Command ps2exe -ErrorAction SilentlyContinue
if ($ps2exe) {
    Write-Host "   ✅ ps2exe: Disponible" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  ps2exe non installé (optionnel)" -ForegroundColor Yellow
    Write-Host "      Install-Module ps2exe" -ForegroundColor Gray
}

Write-Host ""

# =====================================================
# VÉRIFICATION DES PACKAGES
# =====================================================

Write-Host "📦 Vérification des packages..." -ForegroundColor Yellow

# Python packages
$venvPath = Join-Path $projectRoot ".venv310"
if (Test-Path $venvPath) {
    Write-Host "   ✅ Environnement virtuel Python présent" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  Environnement virtuel non créé" -ForegroundColor Yellow
    Write-Host "      Sera créé lors du build" -ForegroundColor Gray
}

# Node modules
$nodeModulesPath = Join-Path $projectRoot "client\node_modules"
if (Test-Path $nodeModulesPath) {
    Write-Host "   ✅ node_modules présent" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  node_modules non installé" -ForegroundColor Yellow
    Write-Host "      Exécuter: cd client; npm install" -ForegroundColor Gray
}

Write-Host ""

# =====================================================
# VÉRIFICATION DU CODE
# =====================================================

Write-Host "🔍 Vérification du code..." -ForegroundColor Yellow

# Vérifier qu'il n'y a pas de clés API hardcodées
$apiKeyFiles = @(
    "server\main.py",
    "settings.yaml"
)

$apiKeyFound = $false
foreach ($file in $apiKeyFiles) {
    $fullPath = Join-Path $projectRoot $file
    if (Test-Path $fullPath) {
        $content = Get-Content $fullPath -Raw
        if ($content -match 'tmdb_api_key:\s*"[a-zA-Z0-9]{32}"') {
            Write-Host "   ⚠️  Clé API TMDb détectée dans $file" -ForegroundColor Yellow
            Write-Host "      Retirer avant distribution" -ForegroundColor Gray
            $apiKeyFound = $true
        }
    }
}

if (-not $apiKeyFound) {
    Write-Host "   ✅ Pas de clé API hardcodée" -ForegroundColor Green
}

# Vérifier les fichiers de log/debug
$debugFiles = @(
    "server\homeflix.log",
    "server\homeflix.log.1",
    "duplicates_log.md",
    "compression_log.txt"
)

$debugFound = $false
foreach ($file in $debugFiles) {
    $fullPath = Join-Path $projectRoot $file
    if (Test-Path $fullPath) {
        Write-Host "   ⚠️  Fichier de log trouvé: $file" -ForegroundColor Yellow
        $debugFound = $true
    }
}

if (-not $debugFound) {
    Write-Host "   ✅ Pas de fichiers de log" -ForegroundColor Green
}

Write-Host ""

# =====================================================
# VÉRIFICATION GIT
# =====================================================

Write-Host "📚 Vérification Git..." -ForegroundColor Yellow

try {
    $gitStatus = git status --porcelain 2>&1
    if ($gitStatus) {
        Write-Host "   ⚠️  Changements non commités détectés" -ForegroundColor Yellow
        Write-Host "      Commiter avant de créer une release" -ForegroundColor Gray
    } else {
        Write-Host "   ✅ Repo Git propre" -ForegroundColor Green
    }
    
    $currentBranch = git branch --show-current 2>&1
    Write-Host "   📍 Branche: $currentBranch" -ForegroundColor Cyan
    
    # Vérifier si un tag existe pour cette version
    $tags = git tag 2>&1
    if ($tags -match "v$version") {
        Write-Host "   ⚠️  Tag v$version existe déjà" -ForegroundColor Yellow
    } else {
        Write-Host "   ℹ️ Tag v$version n'existe pas encore" -ForegroundColor Gray
    }
} catch {
    Write-Host "   ⚠️  Pas un dépôt Git ou Git non installé" -ForegroundColor Yellow
}

Write-Host ""

# =====================================================
# RÉSUMÉ
# =====================================================

Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Cyan

if ($allChecks) {
    Write-Host "   ✅ TOUS LES CONTRÔLES SONT PASSÉS !" -ForegroundColor Green
    Write-Host "" -ForegroundColor Cyan
    Write-Host "   Vous pouvez créer l'installateur :" -ForegroundColor White
    Write-Host "   cd installer" -ForegroundColor Gray
    Write-Host "   .\build-installer.ps1" -ForegroundColor Gray
} else {
    Write-Host "   ⚠️  CERTAINS CONTRÔLES ONT ÉCHOUÉ" -ForegroundColor Yellow
    Write-Host "" -ForegroundColor Yellow
    Write-Host "   Corriger les problèmes avant de builder" -ForegroundColor White
}

Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Retourner le code de sortie approprié
if ($allChecks) {
    exit 0
} else {
    exit 1
}
