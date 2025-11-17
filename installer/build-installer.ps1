# =====================================================
# HOMEFLIX - SCRIPT DE BUILD DE L'INSTALLATEUR
# =====================================================
# Prépare et compile l'installateur Windows

param(
    [Parameter(Mandatory=$false)]
    [switch]$SkipBuild,
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipTests
)

$ErrorActionPreference = "Stop"

Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "   HOMEFLIX - BUILD DE L'INSTALLATEUR" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

$projectRoot = Split-Path -Parent $PSScriptRoot
$installerDir = Join-Path $projectRoot "installer"
$outputDir = Join-Path $installerDir "output"

# =====================================================
# RÉCUPÉRATION DE LA VERSION
# =====================================================

Write-Host "📌 Récupération de la version..." -ForegroundColor Yellow

$packageJsonPath = Join-Path $projectRoot "client\package.json"
if (Test-Path $packageJsonPath) {
    $packageJson = Get-Content $packageJsonPath -Raw | ConvertFrom-Json
    $version = $packageJson.version
    
    if (-not $version -or $version -eq "0.0.0") {
        # Générer une version basée sur la date
        $version = "1.0." + (Get-Date -Format "yyyyMMdd")
    }
} else {
    $version = "1.0.0"
}

Write-Host "   Version détectée: $version" -ForegroundColor Green
Write-Host ""

# Créer le fichier version.ini pour InnoSetup
$versionIniPath = Join-Path $installerDir "version.ini"
@"
[Version]
Number=$version
Date=$(Get-Date -Format "yyyy-MM-dd")
"@ | Out-File -FilePath $versionIniPath -Encoding ASCII

# =====================================================
# NETTOYAGE
# =====================================================

Write-Host "🧹 Nettoyage des fichiers temporaires..." -ForegroundColor Yellow

# Nettoyer le dossier de sortie
if (Test-Path $outputDir) {
    Remove-Item -Path $outputDir -Recurse -Force
}
New-Item -ItemType Directory -Path $outputDir -Force | Out-Null

# Nettoyer les caches
$cachePaths = @(
    (Join-Path $projectRoot "client\node_modules\.vite"),
    (Join-Path $projectRoot "client\dist"),
    (Join-Path $projectRoot "server\__pycache__"),
    (Join-Path $projectRoot "server\api\__pycache__"),
    (Join-Path $projectRoot "server\core\__pycache__")
)

foreach ($cache in $cachePaths) {
    if (Test-Path $cache) {
        Remove-Item -Path $cache -Recurse -Force -ErrorAction SilentlyContinue
    }
}

Write-Host "✅ Nettoyage terminé" -ForegroundColor Green
Write-Host ""

# =====================================================
# BUILD DU FRONTEND
# =====================================================

if (-not $SkipBuild) {
    Write-Host "🔨 Compilation du frontend..." -ForegroundColor Yellow
    
    $clientPath = Join-Path $projectRoot "client"
    Set-Location $clientPath
    
    # Vérifier que node_modules existe
    if (-not (Test-Path "node_modules")) {
        Write-Host "   Installation des dépendances npm..." -ForegroundColor Gray
        npm install --silent
    }
    
    # Build
    Write-Host "   Build Vite..." -ForegroundColor Gray
    npm run build
    
    if ($LASTEXITCODE -ne 0) {
        throw "Erreur lors de la compilation du frontend"
    }
    
    Set-Location $projectRoot
    Write-Host "✅ Frontend compilé" -ForegroundColor Green
    Write-Host ""
}

# =====================================================
# CRÉATION DU LAUNCHER EXE
# =====================================================

Write-Host "🚀 Création du launcher Windows..." -ForegroundColor Yellow

# Script PowerShell du launcher
$launcherScript = @'
# HomeFlix Launcher
$appPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $appPath

# Vérifier si le serveur tourne déjà
$serverRunning = Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.Path -like "*homeflix*" }

if (-not $serverRunning) {
    # Lancer le serveur
    $pythonExe = Join-Path $appPath ".venv310\Scripts\python.exe"
    $mainPy = Join-Path $appPath "server\main.py"
    
    Start-Process -FilePath $pythonExe -ArgumentList $mainPy -WindowStyle Hidden
    Start-Sleep -Seconds 3
}

# Ouvrir le navigateur
Start-Process "http://localhost:8000"
'@

$launcherScriptPath = Join-Path $installerDir "launcher.ps1"
$launcherScript | Out-File -FilePath $launcherScriptPath -Encoding UTF8

# Convertir en EXE avec ps2exe (si disponible)
$ps2exeCmd = Get-Command ps2exe -ErrorAction SilentlyContinue

if ($ps2exeCmd) {
    $launcherExePath = Join-Path $installerDir "homeflix-launcher.exe"
    $iconPath = Join-Path $projectRoot "data\homeflix-icon.ico"
    
    if (-not (Test-Path $iconPath)) {
        # Générer une icône basique si elle n'existe pas
        Write-Host "   Génération de l'icône..." -ForegroundColor Gray
        & python (Join-Path $projectRoot "generate_icon.py")
    }
    
    Write-Host "   Compilation du launcher..." -ForegroundColor Gray
    ps2exe $launcherScriptPath $launcherExePath -noConsole -iconFile $iconPath
    
    if (Test-Path $launcherExePath) {
        Write-Host "✅ Launcher créé: homeflix-launcher.exe" -ForegroundColor Green
    }
} else {
    Write-Host "⚠️  ps2exe non trouvé - le launcher .ps1 sera utilisé" -ForegroundColor Yellow
    Write-Host "   Pour créer un .exe, installez ps2exe:" -ForegroundColor Yellow
    Write-Host "   Install-Module ps2exe" -ForegroundColor Gray
    
    # Copier le script comme fallback
    Copy-Item $launcherScriptPath (Join-Path $installerDir "homeflix-launcher.ps1")
}

Write-Host ""

# =====================================================
# CRÉATION DES FICHIERS DE LICENCE
# =====================================================

Write-Host "📄 Génération des fichiers de licence..." -ForegroundColor Yellow

$localesDir = Join-Path $installerDir "locales"
if (-not (Test-Path $localesDir)) {
    New-Item -ItemType Directory -Path $localesDir -Force | Out-Null
}

# Licence MIT
$mitLicense = @"
MIT License

Copyright (c) $(Get-Date -Format yyyy) HomeFlix Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

This product uses the TMDb API but is not endorsed or certified by TMDb.
"@

$mitLicense | Out-File -FilePath (Join-Path $localesDir "LICENSE.en.txt") -Encoding UTF8
$mitLicense | Out-File -FilePath (Join-Path $localesDir "LICENSE.fr.txt") -Encoding UTF8
$mitLicense | Out-File -FilePath (Join-Path $localesDir "LICENSE.es.txt") -Encoding UTF8
$mitLicense | Out-File -FilePath (Join-Path $projectRoot "LICENSE") -Encoding UTF8

# README pour l'installateur
$readmeInstaller = @"
═══════════════════════════════════════════════════
               HOMEFLIX v$version
═══════════════════════════════════════════════════

Merci d'avoir choisi HomeFlix !

PRÉREQUIS
---------
L'installateur détectera et installera automatiquement :
• Python 3.10 ou supérieur
• Node.js 18 ou supérieur  
• FFmpeg (optionnel, pour les miniatures)

INSTALLATION
------------
Suivez les étapes de l'assistant d'installation.
Vous pourrez configurer :
• Les dossiers contenant vos vidéos
• Votre clé API TMDb (optionnel)
• Les options de démarrage

APRÈS L'INSTALLATION
--------------------
• Lancez HomeFlix depuis le menu Démarrer
• La première exécution peut prendre quelques secondes
• Accédez à http://localhost:8000 dans votre navigateur

ACCÈS RÉSEAU
------------
Pour accéder depuis d'autres appareils :
• Assurez-vous que le pare-feu Windows autorise les connexions
• Utilisez http://[VOTRE-IP]:8000

SUPPORT
-------
Documentation : https://github.com/homeflix
Issues : https://github.com/homeflix/issues

═══════════════════════════════════════════════════
"@

$readmeInstaller | Out-File -FilePath (Join-Path $installerDir "README_INSTALL.txt") -Encoding UTF8

Write-Host "✅ Fichiers de licence créés" -ForegroundColor Green
Write-Host ""

# =====================================================
# TESTS
# =====================================================

if (-not $SkipTests) {
    Write-Host "🧪 Vérification des fichiers..." -ForegroundColor Yellow
    
    $requiredFiles = @(
        "homeflix.iss",
        "detect-environment.ps1",
        "install-dependencies.ps1",
        "configure-system.ps1",
        "locales\fr.json",
        "locales\en.json",
        "locales\es.json"
    )
    
    $allPresent = $true
    foreach ($file in $requiredFiles) {
        $fullPath = Join-Path $installerDir $file
        if (-not (Test-Path $fullPath)) {
            Write-Host "   ❌ Fichier manquant: $file" -ForegroundColor Red
            $allPresent = $false
        }
    }
    
    if ($allPresent) {
        Write-Host "✅ Tous les fichiers sont présents" -ForegroundColor Green
    } else {
        throw "Fichiers manquants détectés"
    }
    
    Write-Host ""
}

# =====================================================
# COMPILATION INNOSETUP
# =====================================================

Write-Host "🔧 Compilation de l'installateur avec InnoSetup..." -ForegroundColor Yellow

# Chercher InnoSetup
$innoSetupPaths = @(
    "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
    "${env:ProgramFiles}\Inno Setup 6\ISCC.exe",
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
    "C:\Program Files\Inno Setup 6\ISCC.exe"
)

$isccPath = $null
foreach ($path in $innoSetupPaths) {
    if (Test-Path $path) {
        $isccPath = $path
        break
    }
}

if (-not $isccPath) {
    Write-Host "" -ForegroundColor Yellow
    Write-Host "⚠️  InnoSetup non trouvé !" -ForegroundColor Yellow
    Write-Host "" -ForegroundColor Yellow
    Write-Host "Pour compiler l'installateur, installez InnoSetup 6:" -ForegroundColor Yellow
    Write-Host "https://jrsoftware.org/isdl.php" -ForegroundColor Cyan
    Write-Host "" -ForegroundColor Yellow
    Write-Host "Tous les fichiers sont prêts dans:" -ForegroundColor White
    Write-Host $installerDir -ForegroundColor Cyan
    Write-Host "" -ForegroundColor Yellow
    exit 1
}

# Compiler
$issFile = Join-Path $installerDir "homeflix.iss"
Write-Host "   Compilation en cours..." -ForegroundColor Gray

$compileResult = & $isccPath $issFile 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Green
    Write-Host "   ✅ INSTALLATEUR CRÉÉ AVEC SUCCÈS !" -ForegroundColor Green
    Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Green
    Write-Host ""
    Write-Host "📦 Fichier de sortie:" -ForegroundColor Cyan
    
    $setupFile = Get-ChildItem $outputDir -Filter "HomeFlix-Setup-*.exe" | Select-Object -First 1
    if ($setupFile) {
        Write-Host "   $($setupFile.FullName)" -ForegroundColor White
        Write-Host ""
        Write-Host "📊 Taille: $([math]::Round($setupFile.Length / 1MB, 2)) MB" -ForegroundColor Gray
        Write-Host ""
        Write-Host "🚀 Vous pouvez maintenant distribuer cet installateur !" -ForegroundColor Green
    }
} else {
    Write-Host ""
    Write-Host "❌ Erreur lors de la compilation" -ForegroundColor Red
    Write-Host $compileResult -ForegroundColor Gray
    exit 1
}

Write-Host ""
