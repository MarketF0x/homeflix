# Script d'aide à la configuration de la clé API TMDb
# Pour Homeflix - Usage Commercial Légal

param(
    [switch]$Help
)

function Show-Banner {
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║                                                                ║" -ForegroundColor Cyan
    Write-Host "║          🔑 Configuration de la Clé API TMDb                  ║" -ForegroundColor Cyan
    Write-Host "║                  Pour Homeflix                                 ║" -ForegroundColor Cyan
    Write-Host "║                                                                ║" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
}

function Show-Help {
    Show-Banner
    Write-Host "Ce script vous aide à configurer votre clé API TMDb pour Homeflix." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "📋 Pourquoi ai-je besoin d'une clé API TMDb ?" -ForegroundColor Cyan
    Write-Host "   Homeflix utilise TMDb pour récupérer les affiches, métadonnées et informations sur vos films/séries."
    Write-Host ""
    Write-Host "⚠️  Important : Usage Commercial" -ForegroundColor Yellow
    Write-Host "   • Usage Personnel/Gratuit  → Clé API gratuite (ce script)"
    Write-Host "   • Usage Commercial/Payant  → Licence commerciale TMDb requise"
    Write-Host ""
    Write-Host "📚 Documentation complète : GUIDE_TMDB_API_KEY.md" -ForegroundColor Green
    Write-Host "📄 Conditions TMDb : TMDB_TERMS_SUMMARY.md" -ForegroundColor Green
    Write-Host ""
    Write-Host "Usage : .\setup-tmdb-key.ps1" -ForegroundColor Cyan
    Write-Host ""
}

function Test-TmdbKey {
    param([string]$ApiKey)
    
    if ([string]::IsNullOrWhiteSpace($ApiKey)) {
        return $false
    }
    
    # Vérifier le format (32 caractères hexadécimaux)
    if ($ApiKey -notmatch '^[a-f0-9]{32}$') {
        Write-Host "⚠️  Format de clé invalide. La clé doit être 32 caractères hexadécimaux." -ForegroundColor Yellow
        return $false
    }
    
    Write-Host "🔍 Test de la clé API avec TMDb..." -ForegroundColor Cyan
    
    try {
        $response = Invoke-RestMethod -Uri "https://api.themoviedb.org/3/configuration?api_key=$ApiKey" -ErrorAction Stop
        Write-Host "✅ Clé API valide et fonctionnelle !" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "❌ Clé API invalide ou problème de connexion" -ForegroundColor Red
        Write-Host "   Erreur : $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

function Get-CurrentTmdbKey {
    $settingsPath = "settings.yaml"
    
    if (Test-Path $settingsPath) {
        $content = Get-Content $settingsPath -Raw
        if ($content -match "tmdb_api_key:\s*'?([a-f0-9]{32})'?") {
            return $matches[1]
        }
        elseif ($content -match "tmdb_api_key:\s*([a-f0-9]{32})") {
            return $matches[1]
        }
    }
    
    return $null
}

function Set-TmdbKey {
    param([string]$ApiKey)
    
    $settingsPath = "settings.yaml"
    
    if (-not (Test-Path $settingsPath)) {
        Write-Host "❌ Fichier settings.yaml introuvable" -ForegroundColor Red
        return $false
    }
    
    try {
        $content = Get-Content $settingsPath -Raw
        
        # Remplacer la clé API
        if ($content -match "tmdb_api_key:\s*.*") {
            $content = $content -replace "tmdb_api_key:\s*.*", "tmdb_api_key: '$ApiKey'"
        }
        else {
            # Ajouter si n'existe pas
            $content += "`ntmdb_api_key: '$ApiKey'"
        }
        
        Set-Content -Path $settingsPath -Value $content -NoNewline
        Write-Host "✅ Clé API enregistrée dans settings.yaml" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "❌ Erreur lors de l'enregistrement : $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

function Open-TmdbSignup {
    Write-Host "🌐 Ouverture de la page d'inscription TMDb..." -ForegroundColor Cyan
    Start-Process "https://www.themoviedb.org/signup"
}

function Open-TmdbApiSettings {
    Write-Host "🌐 Ouverture de la page des paramètres API TMDb..." -ForegroundColor Cyan
    Start-Process "https://www.themoviedb.org/settings/api"
}

function Show-Instructions {
    Write-Host ""
    Write-Host "📋 Instructions pour obtenir votre clé API TMDb :" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "1️⃣  Créer un compte TMDb (si vous n'en avez pas)" -ForegroundColor Yellow
    Write-Host "   → https://www.themoviedb.org/signup" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2️⃣  Confirmer votre email" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "3️⃣  Demander une clé API" -ForegroundColor Yellow
    Write-Host "   → https://www.themoviedb.org/settings/api" -ForegroundColor Gray
    Write-Host "   → Cliquer 'Request an API Key'" -ForegroundColor Gray
    Write-Host "   → Choisir 'Developer'" -ForegroundColor Gray
    Write-Host "   → Remplir le formulaire (usage personnel)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "4️⃣  Copier la clé API (v3 auth)" -ForegroundColor Yellow
    Write-Host "   → Format : 32 caractères hexadécimaux" -ForegroundColor Gray
    Write-Host ""
    Write-Host "📚 Guide détaillé disponible dans : GUIDE_TMDB_API_KEY.md" -ForegroundColor Green
    Write-Host ""
}

# Programme principal
if ($Help) {
    Show-Help
    exit 0
}

Show-Banner

# Vérifier si une clé existe déjà
$currentKey = Get-CurrentTmdbKey

if ($currentKey) {
    Write-Host "🔍 Clé API trouvée dans settings.yaml" -ForegroundColor Cyan
    Write-Host "   Clé : $($currentKey.Substring(0,8))..." -ForegroundColor Gray
    Write-Host ""
    
    $test = Read-Host "Voulez-vous tester cette clé ? (o/N)"
    if ($test -eq 'o' -or $test -eq 'O') {
        if (Test-TmdbKey -ApiKey $currentKey) {
            Write-Host ""
            Write-Host "✅ Votre clé API TMDb est configurée et fonctionnelle !" -ForegroundColor Green
            Write-Host ""
            Write-Host "Vous pouvez maintenant lancer Homeflix :" -ForegroundColor Cyan
            Write-Host "   .\start-homeflix.ps1 -Mode production" -ForegroundColor Yellow
            Write-Host ""
            exit 0
        }
    }
    
    Write-Host ""
    $replace = Read-Host "Voulez-vous remplacer cette clé ? (o/N)"
    if ($replace -ne 'o' -and $replace -ne 'O') {
        Write-Host "Configuration annulée." -ForegroundColor Yellow
        exit 0
    }
}

Write-Host "⚠️  IMPORTANT - Usage Commercial" -ForegroundColor Yellow
Write-Host ""
Write-Host "Avant de continuer, confirmez votre type d'usage :" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Usage Personnel/Gratuit" -ForegroundColor Green
Write-Host "   • Application personnelle, sans frais" -ForegroundColor Gray
Write-Host "   • Pas de publicité ni revenus" -ForegroundColor Gray
Write-Host "   • → Clé API gratuite (continuez)" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Usage Commercial/Payant" -ForegroundColor Red
Write-Host "   • Application payante" -ForegroundColor Gray
Write-Host "   • Site web avec revenus" -ForegroundColor Gray
Write-Host "   • → Licence commerciale TMDb requise" -ForegroundColor Gray
Write-Host "   • → Contact : https://www.themoviedb.org/api-for-business" -ForegroundColor Gray
Write-Host ""

$usageType = Read-Host "Votre usage est-il personnel/gratuit ? (O/n)"

if ($usageType -eq 'n' -or $usageType -eq 'N') {
    Write-Host ""
    Write-Host "⚠️  Pour un usage commercial, vous devez :" -ForegroundColor Yellow
    Write-Host "   1. Contacter TMDb pour une licence commerciale" -ForegroundColor Cyan
    Write-Host "      → https://www.themoviedb.org/api-for-business" -ForegroundColor Gray
    Write-Host "   2. Obtenir une clé API commerciale" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "📄 Plus d'infos : TMDB_TERMS_SUMMARY.md" -ForegroundColor Green
    Write-Host ""
    
    $openBusiness = Read-Host "Ouvrir la page API Business ? (o/N)"
    if ($openBusiness -eq 'o' -or $openBusiness -eq 'O') {
        Start-Process "https://www.themoviedb.org/api-for-business"
    }
    
    exit 0
}

Write-Host ""
Write-Host "✅ Parfait ! Procédons à la configuration pour usage personnel." -ForegroundColor Green
Write-Host ""

Show-Instructions

Write-Host "Que souhaitez-vous faire ?" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Ouvrir la page d'inscription TMDb" -ForegroundColor Yellow
Write-Host "   → https://www.themoviedb.org/signup" -ForegroundColor Gray
Write-Host "2. Ouvrir la page des paramètres API" -ForegroundColor Yellow
Write-Host "   → https://www.themoviedb.org/settings/api" -ForegroundColor Gray
Write-Host "3. Entrer ma clé API directement" -ForegroundColor Yellow
Write-Host "4. Lire le guide complet (GUIDE_TMDB_API_KEY.md)" -ForegroundColor Yellow
Write-Host "5. Quitter" -ForegroundColor Yellow
Write-Host ""

$choice = Read-Host "Votre choix (1-5)"

switch ($choice) {
    "1" {
        Open-TmdbSignup
        Write-Host ""
        Write-Host "📋 Instructions :" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "1. Créez votre compte TMDb et confirmez votre email" -ForegroundColor Yellow
        Write-Host "2. Connectez-vous à votre compte" -ForegroundColor Yellow
        Write-Host "3. Allez sur : https://www.themoviedb.org/settings/api" -ForegroundColor Yellow
        Write-Host "4. Cliquez sur 'Request an API Key' → Choisissez 'Developer'" -ForegroundColor Yellow
        Write-Host "5. Remplissez le formulaire (usage personnel)" -ForegroundColor Yellow
        Write-Host "6. Copiez votre clé API (v3 auth)" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "➡️  Relancez ce script pour configurer la clé : .\setup-tmdb-key.ps1" -ForegroundColor Cyan
        Write-Host ""
    }
    "2" {
        Open-TmdbApiSettings
        Write-Host ""
        Write-Host "➡️  Copiez votre clé API (v3 auth), puis relancez ce script." -ForegroundColor Cyan
        Write-Host ""
    }
    "3" {
        Write-Host ""
        Write-Host "📝 Collez votre clé API TMDb (32 caractères) :" -ForegroundColor Cyan
        $apiKey = Read-Host "Clé API"
        
        if (Test-TmdbKey -ApiKey $apiKey) {
            if (Set-TmdbKey -ApiKey $apiKey) {
                Write-Host ""
                Write-Host "🎉 Configuration terminée avec succès !" -ForegroundColor Green
                Write-Host ""
                Write-Host "Vous pouvez maintenant lancer Homeflix :" -ForegroundColor Cyan
                Write-Host "   .\start-homeflix.ps1 -Mode production" -ForegroundColor Yellow
                Write-Host ""
            }
        }
        else {
            Write-Host ""
            Write-Host "❌ La clé n'a pas pu être validée." -ForegroundColor Red
            Write-Host "   Vérifiez que vous avez copié la clé API (v3 auth)" -ForegroundColor Yellow
            Write-Host ""
        }
    }
    "4" {
        if (Test-Path "GUIDE_TMDB_API_KEY.md") {
            Start-Process "GUIDE_TMDB_API_KEY.md"
        }
        else {
            Write-Host "❌ Fichier GUIDE_TMDB_API_KEY.md introuvable" -ForegroundColor Red
        }
    }
    "5" {
        Write-Host "Au revoir !" -ForegroundColor Cyan
        exit 0
    }
    default {
        Write-Host "❌ Choix invalide" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "💡 Astuce : Relancez ce script à tout moment avec .\setup-tmdb-key.ps1" -ForegroundColor Cyan
Write-Host ""
