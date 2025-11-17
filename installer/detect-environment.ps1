# =====================================================
# HOMEFLIX - SCRIPT DE DÉTECTION AUTOMATIQUE
# =====================================================
# Détecte : Python, Node.js, FFmpeg, dossiers vidéo
# Utilisé par l'installateur InnoSetup

param(
    [Parameter(Mandatory=$false)]
    [switch]$Json
)

$ErrorActionPreference = "SilentlyContinue"

# =====================================================
# DÉTECTION PYTHON
# =====================================================
function Detect-Python {
    $pythonPath = $null
    $pythonVersion = $null
    
    # Essayer python dans le PATH
    $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonCmd) {
        $version = & python --version 2>&1
        if ($version -match "Python (\d+)\.(\d+)\.(\d+)") {
            $major = [int]$matches[1]
            $minor = [int]$matches[2]
            if ($major -ge 3 -and $minor -ge 10) {
                $pythonPath = $pythonCmd.Source
                $pythonVersion = "$major.$minor.$($matches[3])"
            }
        }
    }
    
    # Chercher dans les emplacements communs
    if (-not $pythonPath) {
        $commonPaths = @(
            "$env:LOCALAPPDATA\Programs\Python\Python3*\python.exe",
            "$env:PROGRAMFILES\Python3*\python.exe",
            "$env:PROGRAMFILES(x86)\Python3*\python.exe"
        )
        
        foreach ($pattern in $commonPaths) {
            $found = Get-ChildItem $pattern -ErrorAction SilentlyContinue | Sort-Object -Descending | Select-Object -First 1
            if ($found) {
                $version = & $found.FullName --version 2>&1
                if ($version -match "Python (\d+)\.(\d+)\.(\d+)") {
                    $major = [int]$matches[1]
                    $minor = [int]$matches[2]
                    if ($major -ge 3 -and $minor -ge 10) {
                        $pythonPath = $found.FullName
                        $pythonVersion = "$major.$minor.$($matches[3])"
                        break
                    }
                }
            }
        }
    }
    
    return @{
        Installed = ($null -ne $pythonPath)
        Path = $pythonPath
        Version = $pythonVersion
    }
}

# =====================================================
# DÉTECTION NODE.JS
# =====================================================
function Detect-NodeJS {
    $nodePath = $null
    $nodeVersion = $null
    
    $nodeCmd = Get-Command node -ErrorAction SilentlyContinue
    if ($nodeCmd) {
        $version = & node --version 2>&1
        if ($version -match "v(\d+)\.(\d+)\.(\d+)") {
            $major = [int]$matches[1]
            if ($major -ge 18) {
                $nodePath = $nodeCmd.Source
                $nodeVersion = "$major.$($matches[2]).$($matches[3])"
            }
        }
    }
    
    return @{
        Installed = ($null -ne $nodePath)
        Path = $nodePath
        Version = $nodeVersion
    }
}

# =====================================================
# DÉTECTION FFMPEG
# =====================================================
function Detect-FFmpeg {
    $ffmpegPath = $null
    $ffmpegVersion = $null
    
    $ffmpegCmd = Get-Command ffmpeg -ErrorAction SilentlyContinue
    if ($ffmpegCmd) {
        $version = & ffmpeg -version 2>&1 | Select-Object -First 1
        if ($version -match "ffmpeg version ([0-9.]+)") {
            $ffmpegPath = $ffmpegCmd.Source
            $ffmpegVersion = $matches[1]
        }
    }
    
    return @{
        Installed = ($null -ne $ffmpegPath)
        Path = $ffmpegPath
        Version = $ffmpegVersion
    }
}

# =====================================================
# DÉTECTION DOSSIERS VIDÉO
# =====================================================
function Detect-VideoFolders {
    $videoFolders = @()
    
    # Dossiers utilisateur communs
    $userFolders = @(
        "$env:USERPROFILE\Videos",
        "$env:USERPROFILE\Vidéos",
        "$env:USERPROFILE\Movies",
        "$env:USERPROFILE\Films",
        "$env:PUBLIC\Videos",
        "$env:PUBLIC\Vidéos",
        "$env:PUBLIC\Movies"
    )
    
    foreach ($folder in $userFolders) {
        if (Test-Path $folder) {
            $videoCount = (Get-ChildItem $folder -Include *.mp4,*.mkv,*.avi,*.mov,*.m4v,*.webm -Recurse -ErrorAction SilentlyContinue | Measure-Object).Count
            if ($videoCount -gt 0) {
                $videoFolders += @{
                    Path = $folder
                    VideoCount = $videoCount
                    Type = "User"
                }
            }
        }
    }
    
    # Scanner tous les lecteurs pour trouver des dossiers "Films", "Movies", "Series", etc.
    $drives = Get-PSDrive -PSProvider FileSystem | Where-Object { $_.Used -gt 0 }
    
    foreach ($drive in $drives) {
        $commonVideoNames = @("Films", "Movies", "Vidéos", "Videos", "Series", "TV Shows", "Multimedia", "Media")
        
        foreach ($name in $commonVideoNames) {
            $searchPath = Join-Path $drive.Root $name
            if (Test-Path $searchPath) {
                # Éviter les doublons
                if ($videoFolders.Path -notcontains $searchPath) {
                    $videoCount = (Get-ChildItem $searchPath -Include *.mp4,*.mkv,*.avi,*.mov,*.m4v,*.webm -Recurse -ErrorAction SilentlyContinue -Depth 2 | Measure-Object).Count
                    if ($videoCount -gt 0) {
                        $videoFolders += @{
                            Path = $searchPath
                            VideoCount = $videoCount
                            Type = "Drive"
                        }
                    }
                }
            }
        }
    }
    
    return $videoFolders | Sort-Object -Property VideoCount -Descending
}

# =====================================================
# DÉTECTION ADRESSE IP LOCALE
# =====================================================
function Get-LocalIP {
    $ips = Get-NetIPAddress -AddressFamily IPv4 | 
           Where-Object { $_.IPAddress -notlike "127.*" -and $_.PrefixOrigin -eq "Dhcp" -or $_.PrefixOrigin -eq "Manual" } |
           Select-Object -ExpandProperty IPAddress
    
    return $ips | Select-Object -First 1
}

# =====================================================
# VÉRIFICATION DROITS ADMIN
# =====================================================
function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# =====================================================
# EXÉCUTION
# =====================================================

Write-Host "🔍 Détection de l'environnement système..." -ForegroundColor Cyan
Write-Host ""

$python = Detect-Python
$nodejs = Detect-NodeJS
$ffmpeg = Detect-FFmpeg
$isAdmin = Test-Administrator
$localIP = Get-LocalIP

Write-Host "Python 3.10+:" -NoNewline
if ($python.Installed) {
    Write-Host " ✅ Détecté (v$($python.Version))" -ForegroundColor Green
    Write-Host "   Chemin: $($python.Path)" -ForegroundColor Gray
} else {
    Write-Host " ❌ Non détecté" -ForegroundColor Red
}

Write-Host ""
Write-Host "Node.js 18+:" -NoNewline
if ($nodejs.Installed) {
    Write-Host " ✅ Détecté (v$($nodejs.Version))" -ForegroundColor Green
    Write-Host "   Chemin: $($nodejs.Path)" -ForegroundColor Gray
} else {
    Write-Host " ❌ Non détecté" -ForegroundColor Red
}

Write-Host ""
Write-Host "FFmpeg:" -NoNewline
if ($ffmpeg.Installed) {
    Write-Host " ✅ Détecté (v$($ffmpeg.Version))" -ForegroundColor Green
    Write-Host "   Chemin: $($ffmpeg.Path)" -ForegroundColor Gray
} else {
    Write-Host " ⚠️  Non détecté (optionnel)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Droits administrateur:" -NoNewline
if ($isAdmin) {
    Write-Host " ✅ Oui" -ForegroundColor Green
} else {
    Write-Host " ⚠️  Non (certaines installations nécessiteront des droits admin)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Adresse IP locale: $localIP" -ForegroundColor Cyan

Write-Host ""
Write-Host "🔍 Recherche de dossiers vidéo..." -ForegroundColor Cyan
$videoFolders = Detect-VideoFolders

if ($videoFolders.Count -gt 0) {
    Write-Host "✅ Dossiers trouvés ($($videoFolders.Count)):" -ForegroundColor Green
    foreach ($folder in $videoFolders) {
        Write-Host "   📁 $($folder.Path)" -ForegroundColor White
        Write-Host "      $($folder.VideoCount) vidéo(s) détectée(s)" -ForegroundColor Gray
    }
} else {
    Write-Host "⚠️  Aucun dossier vidéo détecté" -ForegroundColor Yellow
}

# Export JSON pour InnoSetup
if ($Json) {
    $result = @{
        python = $python
        nodejs = $nodejs
        ffmpeg = $ffmpeg
        isAdmin = $isAdmin
        localIP = $localIP
        videoFolders = $videoFolders
    }
    
    $jsonPath = Join-Path $PSScriptRoot "detection_result.json"
    $result | ConvertTo-Json -Depth 10 | Out-File -FilePath $jsonPath -Encoding UTF8
    Write-Host ""
    Write-Host "✅ Résultat exporté vers: $jsonPath" -ForegroundColor Green
}
