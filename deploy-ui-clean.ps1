# Script de déploiement UI avec nettoyage complet du cache Electron
# Usage: .\deploy-ui-clean.ps1

Write-Host "🧹 Nettoyage et déploiement UI Homeflix" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan

# 1. Arrêter tous les processus
Write-Host "`n[1/6] Arrêt des processus..." -ForegroundColor Yellow
Get-Process -Name Homeflix,electron,python,node -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2
Write-Host "✅ Processus arrêtés" -ForegroundColor Green

# 2. Nettoyer le cache Chromium d'Electron
Write-Host "`n[2/6] Nettoyage du cache Electron..." -ForegroundColor Yellow
$electronCache = "$env:LOCALAPPDATA\homeflix"
if (Test-Path $electronCache) {
    Remove-Item $electronCache -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "✅ Cache Electron supprimé: $electronCache" -ForegroundColor Green
} else {
    Write-Host "ℹ️  Pas de cache à nettoyer" -ForegroundColor Gray
}

# 3. Nettoyer le cache Vite
Write-Host "`n[3/6] Nettoyage du cache Vite..." -ForegroundColor Yellow
$viteCache = "client\node_modules\.vite"
if (Test-Path $viteCache) {
    Remove-Item $viteCache -Recurse -Force
    Write-Host "✅ Cache Vite supprimé" -ForegroundColor Green
} else {
    Write-Host "ℹ️  Pas de cache Vite" -ForegroundColor Gray
}

# 4. Build du frontend
Write-Host "`n[4/6] Build du frontend..." -ForegroundColor Yellow
Set-Location client
npm run build
Set-Location ..
Write-Host "✅ Build terminé" -ForegroundColor Green

# 5. Copier les fichiers vers Electron
Write-Host "`n[5/6] Copie vers Electron..." -ForegroundColor Yellow
$electronDist = "electron\dist\win-unpacked\resources\client\dist"
Copy-Item "client\dist\*" $electronDist -Recurse -Force
Copy-Item "server\main.py" "electron\dist\win-unpacked\resources\server\main.py" -Force

# Vérifier le hash du CSS déployé
$cssFile = Get-ChildItem "$electronDist\assets\index-*.css" | Select-Object -First 1
if ($cssFile) {
    Write-Host "✅ CSS déployé: $($cssFile.Name) ($([math]::Round($cssFile.Length/1KB, 2)) KB)" -ForegroundColor Green
} else {
    Write-Host "⚠️  Fichier CSS non trouvé!" -ForegroundColor Red
}

# 6. Redémarrer Homeflix
Write-Host "`n[6/6] Redémarrage de Homeflix..." -ForegroundColor Yellow
Start-Process "electron\dist\win-unpacked\Homeflix.exe"
Start-Sleep -Seconds 3

Write-Host "`n✨ Déploiement terminé avec cache nettoyé!" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "`n💡 Astuce: Appuyez sur Ctrl+Shift+R dans Homeflix pour forcer le rechargement" -ForegroundColor Cyan
