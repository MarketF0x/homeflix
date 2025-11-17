# =====================================================
# HOMEFLIX - CONFIGURATION SYSTÈME
# =====================================================
# Configure la base de données, le pare-feu, etc.

param(
    [Parameter(Mandatory=$false)]
    [string]$InstallPath = $PSScriptRoot,
    
    [Parameter(Mandatory=$false)]
    [ValidateSet("french", "english", "spanish")]
    [string]$Lang = "french"
)

$ErrorActionPreference = "Continue"

Write-Host "⚙️  Configuration système de HomeFlix..." -ForegroundColor Cyan
Write-Host ""

# Aller dans le dossier d'installation
$appPath = Split-Path -Parent $InstallPath
Set-Location $appPath

# =====================================================
# CRÉATION DE LA BASE DE DONNÉES
# =====================================================

Write-Host "🗄️  Initialisation de la base de données..." -ForegroundColor Yellow

$dbPath = Join-Path $appPath "server\homeflix.db"
$pythonExe = Join-Path $appPath ".venv310\Scripts\python.exe"

if (-not (Test-Path $dbPath)) {
    Write-Host "   Création de la base de données..." -ForegroundColor Gray
    
    # Le serveur créera la DB au premier lancement, mais on peut la préparer
    $initScript = @"
import sqlite3
import os

db_path = r'$dbPath'
os.makedirs(os.path.dirname(db_path), exist_ok=True)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Table videos
cursor.execute('''
    CREATE TABLE IF NOT EXISTS videos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        path TEXT UNIQUE NOT NULL,
        filename TEXT NOT NULL,
        title TEXT,
        year INTEGER,
        genre TEXT,
        duration INTEGER,
        poster_path TEXT,
        backdrop_path TEXT,
        tmdb_id INTEGER,
        overview TEXT,
        vote_average REAL,
        release_date TEXT,
        media_type TEXT,
        collection_name TEXT,
        collection_order INTEGER,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')

# Table progress
cursor.execute('''
    CREATE TABLE IF NOT EXISTS progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        video_id INTEGER NOT NULL,
        position INTEGER NOT NULL,
        duration INTEGER NOT NULL,
        watched BOOLEAN DEFAULT 0,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (video_id) REFERENCES videos(id) ON DELETE CASCADE
    )
''')

# Index pour les performances
cursor.execute('CREATE INDEX IF NOT EXISTS idx_videos_title ON videos(title)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_videos_year ON videos(year)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_videos_genre ON videos(genre)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_videos_collection ON videos(collection_name)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_progress_video ON progress(video_id)')

conn.commit()
conn.close()
print('Base de données créée avec succès')
"@
    
    $initScript | & $pythonExe -
    
    if (Test-Path $dbPath) {
        Write-Host "✅ Base de données créée" -ForegroundColor Green
    } else {
        Write-Host "⚠️  La base de données sera créée au premier lancement" -ForegroundColor Yellow
    }
} else {
    Write-Host "✅ Base de données déjà présente" -ForegroundColor Green
}

Write-Host ""

# =====================================================
# CONFIGURATION DU PARE-FEU WINDOWS
# =====================================================

Write-Host "🔥 Configuration du pare-feu Windows..." -ForegroundColor Yellow

try {
    # Vérifier si les règles existent déjà
    $rule8000 = Get-NetFirewallRule -DisplayName "HomeFlix - Backend API" -ErrorAction SilentlyContinue
    $rule5173 = Get-NetFirewallRule -DisplayName "HomeFlix - Frontend Dev" -ErrorAction SilentlyContinue
    
    if (-not $rule8000) {
        Write-Host "   Ajout de la règle pour le port 8000..." -ForegroundColor Gray
        New-NetFirewallRule -DisplayName "HomeFlix - Backend API" `
                           -Direction Inbound `
                           -Protocol TCP `
                           -LocalPort 8000 `
                           -Action Allow `
                           -Profile Private,Domain `
                           -ErrorAction Stop | Out-Null
    }
    
    if (-not $rule5173) {
        Write-Host "   Ajout de la règle pour le port 5173..." -ForegroundColor Gray
        New-NetFirewallRule -DisplayName "HomeFlix - Frontend Dev" `
                           -Direction Inbound `
                           -Protocol TCP `
                           -LocalPort 5173 `
                           -Action Allow `
                           -Profile Private,Domain `
                           -ErrorAction Stop | Out-Null
    }
    
    Write-Host "✅ Pare-feu configuré" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Impossible de configurer le pare-feu automatiquement" -ForegroundColor Yellow
    Write-Host "   Vous devrez autoriser les ports 8000 et 5173 manuellement" -ForegroundColor Yellow
}

Write-Host ""

# =====================================================
# CRÉATION DES DOSSIERS DE DONNÉES
# =====================================================

Write-Host "📁 Création des dossiers de données..." -ForegroundColor Yellow

$folders = @(
    (Join-Path $appPath "data"),
    (Join-Path $appPath "data\posters"),
    (Join-Path $appPath "data\thumbs"),
    (Join-Path $appPath "cache"),
    (Join-Path $appPath "logs")
)

foreach ($folder in $folders) {
    if (-not (Test-Path $folder)) {
        New-Item -ItemType Directory -Path $folder -Force | Out-Null
        Write-Host "   Créé: $folder" -ForegroundColor Gray
    }
}

Write-Host "✅ Dossiers créés" -ForegroundColor Green
Write-Host ""

# =====================================================
# COPIE DE LA LICENCE
# =====================================================

Write-Host "📄 Installation des fichiers de documentation..." -ForegroundColor Yellow

$licenseMap = @{
    "french" = "fr"
    "english" = "en"
    "spanish" = "es"
}

$langCode = $licenseMap[$Lang]
if (-not $langCode) { $langCode = "en" }

# Créer un fichier README localisé
$readmePath = Join-Path $appPath "README_USER.txt"
$readmeContent = @"
═══════════════════════════════════════════════════
           HOMEFLIX - GUIDE DE DÉMARRAGE
═══════════════════════════════════════════════════

✅ Installation terminée avec succès !

🚀 LANCEMENT RAPIDE
-------------------
1. Double-cliquez sur l'icône HomeFlix sur votre bureau
   OU
2. Cherchez "HomeFlix" dans le menu Démarrer

📱 ACCÈS DEPUIS D'AUTRES APPAREILS
-----------------------------------
Depuis votre réseau local, accédez à :
  http://[VOTRE-IP-LOCALE]:8000

Pour trouver votre IP :
- Windows : Ouvrir cmd.exe et taper "ipconfig"
- Chercher "Adresse IPv4"

⚙️  CONFIGURATION
-----------------
Le fichier de configuration se trouve dans :
  $appPath\settings.yaml

Vous pouvez y modifier :
- Les dossiers vidéo à scanner
- Votre clé API TMDb
- Les paramètres de filtrage films/séries

🔑 CLÉ API TMDB (OPTIONNEL MAIS RECOMMANDÉ)
--------------------------------------------
Pour récupérer automatiquement les affiches :
1. Créez un compte sur https://www.themoviedb.org
2. Allez sur https://www.themoviedb.org/settings/api
3. Demandez une clé API (gratuit)
4. Ajoutez-la dans settings.yaml

📚 AIDE ET SUPPORT
------------------
Documentation : https://github.com/homeflix
Issues : https://github.com/homeflix/issues

═══════════════════════════════════════════════════
"@

$readmeContent | Out-File -FilePath $readmePath -Encoding UTF8
Write-Host "✅ Documentation installée" -ForegroundColor Green

Write-Host ""
Write-Host "✅ Configuration terminée avec succès !" -ForegroundColor Green
