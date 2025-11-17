# 🎯 OPTIMISATIONS TAILLE APPLICATION HOMEFLIX

## 📊 ANALYSE ACTUELLE

**Taille totale** : 1.14 GB
**Fichiers** : 22,856

### Répartition par dossier :

| Dossier | Taille | % du total | Optimisable |
|---------|--------|------------|-------------|
| **electron/** | 756 MB | 66% | ✅ OUI |
| **.venv310/** | 152 MB | 13% | ⚠️ DOUBLONS |
| **data/** | 113 MB | 10% | ❌ NON (miniatures) |
| **client/** | 110 MB | 10% | ✅ OUI |
| **.venv/** | 18 MB | 2% | ✅ SUPPRIMER (doublon) |
| Autres | 15 MB | 1% | ✅ OUI |

---

## 🚀 OPTIMISATIONS RECOMMANDÉES

### 1. **NETTOYER ELECTRON (756 MB → ~200 MB)**

#### Problème
- 233 packages dans `electron/node_modules/`
- Beaucoup de dépendances de développement inutiles en production

#### Solution
```bash
cd electron

# Supprimer node_modules
Remove-Item node_modules -Recurse -Force

# Réinstaller SEULEMENT les dépendances de production
npm install --production

# OU nettoyer les dev dependencies
npm prune --production
```

**Gain estimé** : **-550 MB** (756 → 200 MB)

---

### 2. **NETTOYER CLIENT (110 MB → ~30 MB)**

#### Problème
- 137 packages dans `client/node_modules/`
- node_modules utilisé seulement pour le build

#### Solution (OPTION 1 - Recommandée)
```bash
cd client

# Garder seulement dist/ (build final)
# Supprimer node_modules après build
Remove-Item node_modules -Recurse -Force
```

**Gain** : **-100 MB** (si node_modules supprimé après build)

#### Solution (OPTION 2 - Si rebuild nécessaire)
```bash
cd client

# Nettoyer cache npm
npm cache clean --force

# Supprimer et réinstaller en production
Remove-Item node_modules -Recurse -Force
npm install --production
```

**Gain** : **-50 MB**

---

### 3. **SUPPRIMER .venv (doublon - 18 MB)**

#### Problème
- 2 environnements virtuels Python : `.venv` ET `.venv310`
- `.venv` semble obsolète

#### Solution
```bash
# Vérifier quel venv est utilisé
Get-Content "c:\Users\fparo\Desktop\homeflix\.vscode\settings.json" | Select-String "python"

# Si .venv310 est utilisé, supprimer .venv
Remove-Item ".venv" -Recurse -Force
```

**Gain** : **-18 MB**

---

### 4. **NETTOYER FICHIERS TEMPORAIRES**

#### Fichiers à supprimer sans risque :

```bash
# Caches Python
Remove-Item -Recurse -Force **/__pycache__
Remove-Item -Recurse -Force **/*.pyc

# Caches npm
Remove-Item -Recurse -Force **/node_modules/.cache

# Logs
Remove-Item *.log

# Fichiers temporaires VS Code
Remove-Item .vscode/*.log -ErrorAction SilentlyContinue
```

**Gain estimé** : **-10-20 MB**

---

### 5. **OPTIMISER DATA/ (OPTIONNEL)**

#### Problème
- 113 MB de miniatures/posters
- Certaines peuvent être des doublons ou orphelines

#### Solution
```python
# Nettoyer les miniatures orphelines
python -c "
from pathlib import Path
import sqlite3

db = sqlite3.connect('server/homeflix.db')
cursor = db.cursor()

# Récupérer tous les paths de vidéos
cursor.execute('SELECT path FROM videos')
valid_paths = {row[0] for row in cursor.fetchall()}

# Supprimer miniatures orphelines
thumbs_dir = Path('data/thumbs')
deleted = 0
for thumb in thumbs_dir.glob('*.jpg'):
    # Vérifier si la vidéo existe encore
    if not any(p.endswith(thumb.stem) for p in valid_paths):
        thumb.unlink()
        deleted += 1

print(f'{deleted} miniatures orphelines supprimées')
"
```

**Gain estimé** : **-20-50 MB** (selon orphelins)

---

## 📦 SCRIPT D'OPTIMISATION AUTOMATIQUE

Créons un script pour tout nettoyer automatiquement :

```powershell
# optimize-size.ps1

Write-Host "🎯 Optimisation taille Homeflix..." -ForegroundColor Cyan
Write-Host ""

$savings = 0

# 1. Nettoyer Electron
Write-Host "1️⃣ Nettoyage Electron..." -ForegroundColor Yellow
cd electron
if (Test-Path "node_modules") {
    $size = (Get-ChildItem node_modules -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB
    npm prune --production 2>$null
    $newSize = (Get-ChildItem node_modules -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB
    $saved = $size - $newSize
    $savings += $saved
    Write-Host "   ✅ Économie: $([math]::Round($saved, 2)) MB" -ForegroundColor Green
}
cd ..

# 2. Nettoyer Client (si déjà build)
Write-Host "2️⃣ Nettoyage Client..." -ForegroundColor Yellow
if (Test-Path "client/dist") {
    cd client
    if (Test-Path "node_modules") {
        $size = (Get-ChildItem node_modules -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB
        Remove-Item node_modules -Recurse -Force
        $savings += $size
        Write-Host "   ✅ Économie: $([math]::Round($size, 2)) MB" -ForegroundColor Green
        Write-Host "   ℹ️ Pour rebuild: npm install" -ForegroundColor Gray
    }
    cd ..
} else {
    Write-Host "   ⚠️ Pas de build dist/ - conservation node_modules" -ForegroundColor Yellow
}

# 3. Supprimer .venv si .venv310 existe
Write-Host "3️⃣ Suppression doublons..." -ForegroundColor Yellow
if ((Test-Path ".venv310") -and (Test-Path ".venv")) {
    $size = (Get-ChildItem .venv -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB
    Remove-Item .venv -Recurse -Force
    $savings += $size
    Write-Host "   ✅ .venv supprimé: $([math]::Round($size, 2)) MB" -ForegroundColor Green
}

# 4. Nettoyer caches
Write-Host "4️⃣ Nettoyage caches..." -ForegroundColor Yellow
$cacheSize = 0
Get-ChildItem -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue | 
    ForEach-Object { 
        $cacheSize += (Get-ChildItem $_.FullName -Recurse | Measure-Object -Property Length -Sum).Sum
        Remove-Item $_.FullName -Recurse -Force 
    }
$savings += $cacheSize / 1MB
Write-Host "   ✅ Caches Python supprimés: $([math]::Round($cacheSize / 1MB, 2)) MB" -ForegroundColor Green

# Résumé
Write-Host ""
Write-Host "✅ OPTIMISATION TERMINÉE !" -ForegroundColor Green
Write-Host "   Espace libéré: $([math]::Round($savings, 2)) MB" -ForegroundColor Cyan
Write-Host ""
```

---

## 🎯 GAINS TOTAUX ESTIMÉS

| Optimisation | Gain | Difficulté |
|--------------|------|------------|
| Electron production | **-550 MB** | Facile |
| Client node_modules | **-100 MB** | Facile |
| Doublon .venv | **-18 MB** | Facile |
| Caches Python | **-10 MB** | Facile |
| Miniatures orphelines | **-20 MB** | Moyen |
| **TOTAL** | **-698 MB** | |

**Taille finale** : **1140 MB → 442 MB** (61% de réduction !)

---

## ⚠️ PRÉCAUTIONS

### À NE PAS supprimer :
- ❌ `.venv310/` (environnement Python actif)
- ❌ `server/homeflix.db` (base de données)
- ❌ `data/posters/` et `data/thumbs/` (miniatures)
- ❌ `client/dist/` (build frontend)
- ❌ `electron/main.js`, `preload.js`, `package.json`

### Sauvegardes recommandées :
```bash
# Avant toute optimisation
Copy-Item "server/homeflix.db" "server/homeflix.db.backup"
```

---

## 📋 CHECKLIST D'OPTIMISATION

### Rapide (5 minutes) :
- [ ] `cd electron; npm prune --production`
- [ ] `Remove-Item .venv -Recurse -Force`
- [ ] `Remove-Item **/__pycache__ -Recurse -Force`

**Gain** : ~570 MB

### Complète (15 minutes) :
- [ ] Script optimize-size.ps1
- [ ] Nettoyer miniatures orphelines
- [ ] Vérifier `client/node_modules` (si dist/ existe)

**Gain** : ~700 MB

---

## 🚀 PROCHAINE ÉTAPE

Voulez-vous que je crée et exécute le script d'optimisation automatique ?

Cela réduira l'application de **1.14 GB → ~440 MB** sans rien perdre !
