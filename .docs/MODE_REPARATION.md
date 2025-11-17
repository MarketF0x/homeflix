# 🔧 MODE RÉPARATION - GUIDE COMPLET

Guide d'utilisation du mode réparation de l'installateur Homeflix.

---

## 🎯 Qu'est-ce que le Mode Réparation ?

Le mode réparation permet de **réparer une installation existante** sans perdre vos données :

- ✅ Conserve la base de données
- ✅ Conserve la configuration (`settings.yaml`)
- ✅ Conserve vos profils utilisateurs
- ✅ Réinstalle uniquement les dépendances manquantes ou corrompues

---

## 🚀 Utilisation

### Détection Automatique

Lorsque vous lancez l'installateur sur une installation existante :

```powershell
.\INSTALLER.ps1
```

Le script **détecte automatiquement** l'installation existante et affiche un menu :

```
╔════════════════════════════════════════════════════════╗
║                                                        ║
║     🔧 HOMEFLIX DÉJÀ INSTALLÉ - MODE RÉPARATION       ║
║                                                        ║
╚════════════════════════════════════════════════════════╝

Que souhaitez-vous faire ?

  [1] 🔧 Réparer l'installation
  [2] 🔄 Réinstallation complète
  [3] ❌ Annuler
```

### Option 1 : Réparation Rapide

**Recommandé** pour la plupart des problèmes.

```powershell
# Choix 1 dans le menu
```

**Actions effectuées** :
- ✅ Vérifie l'environnement Python
- ✅ Réinstalle les dépendances Python manquantes
- ✅ Vérifie `node_modules`
- ✅ Réinstalle les dépendances Node.js si nécessaire
- ✅ Vérifie la structure des dossiers (`data/`, `thumbs/`, `posters/`)
- ✅ **Ne touche PAS** à la base de données ni à `settings.yaml`

**Durée** : ~2-5 minutes

### Option 2 : Réinstallation Complète

Pour les problèmes graves nécessitant une réinstallation totale.

```powershell
# Choix 2 dans le menu
```

**Actions effectuées** :
- ⚠️ Sauvegarde automatique de `homeflix.db` → `homeflix.db.backup`
- 🗑️ Supprime `.venv` et `.venv310`
- 🗑️ Supprime `node_modules`
- ✅ Réinstalle tout depuis zéro
- ✅ **Conserve** la base de données et `settings.yaml`

**Durée** : ~5-10 minutes

### Option 3 : Annuler

Annule l'opération sans modifications.

---

## 🔍 Quand Utiliser la Réparation ?

### Problèmes Courants Résolus par la Réparation

#### Erreur "Module Not Found"

```
ModuleNotFoundError: No module named 'fastapi'
```

**Cause** : Dépendances Python manquantes  
**Solution** : Réparation (Option 1)

#### Erreur "Cannot find module"

```
Error: Cannot find module 'react'
```

**Cause** : Dépendances Node.js manquantes  
**Solution** : Réparation (Option 1)

#### Le serveur ne démarre pas

```
Failed to start backend/frontend
```

**Cause** : Environnement virtuel corrompu  
**Solution** : Réinstallation complète (Option 2)

#### Dossiers manquants

```
Error: data/thumbs not found
```

**Cause** : Structure de dossiers incomplète  
**Solution** : Réparation (Option 1)

---

## 📋 Critères de Détection

Le script considère Homeflix comme **installé** si au moins **2 des 4 critères** suivants sont vrais :

1. ✅ `.venv\Scripts\python.exe` existe
2. ✅ `.venv310\Scripts\python.exe` existe
3. ✅ `client\node_modules` existe
4. ✅ `data\homeflix.db` existe

---

## 🛡️ Sécurité des Données

### Ce qui est TOUJOURS Conservé

- ✅ `data\homeflix.db` - Base de données complète
- ✅ `settings.yaml` - Configuration
- ✅ `data\posters\` - Affiches téléchargées
- ✅ `data\thumbs\` - Miniatures générées
- ✅ Vos dossiers de vidéos (jamais touchés)

### Sauvegarde Automatique (Option 2)

Lors d'une réinstallation complète :

```
homeflix.db → homeflix.db.backup
```

**Emplacement** : `data\homeflix.db.backup`

### Sauvegarde Manuelle Recommandée

Avant toute opération, sauvegardez manuellement :

```powershell
# Créer une sauvegarde
Copy-Item "data\homeflix.db" "$env:USERPROFILE\Desktop\homeflix_backup_$(Get-Date -Format 'yyyyMMdd').db"
```

---

## 🔄 Scénarios d'Utilisation

### Scénario 1 : Mise à Jour du Code Source

Vous avez mis à jour le code source (Git pull, téléchargement nouvelle version) :

```powershell
# Lancer l'installateur
.\INSTALLER.ps1

# Choisir Option 1 (Réparation)
# Vérifie et installe les nouvelles dépendances
```

### Scénario 2 : Après un Crash Système

Votre PC a crashé et Homeflix ne démarre plus :

```powershell
# Lancer l'installateur
.\INSTALLER.ps1

# Choisir Option 2 (Réinstallation complète)
# Reconstruit tout l'environnement
```

### Scénario 3 : Erreur de Dépendances

Vous avez une erreur de module manquant :

```powershell
# Lancer l'installateur
.\INSTALLER.ps1

# Choisir Option 1 (Réparation)
# Réinstalle les dépendances manquantes
```

### Scénario 4 : Migration vers Nouveau PC

Vous déplacez Homeflix vers un nouveau PC :

1. **Ancien PC** : Copier le dossier `homeflix\` complet
2. **Nouveau PC** : Coller le dossier
3. **Nouveau PC** :

```powershell
# Lancer l'installateur
.\INSTALLER.ps1

# Choisir Option 2 (Réinstallation complète)
# Reconstruit l'environnement pour le nouveau système
```

---

## 🐛 Dépannage

### La réparation échoue

**Problème** : Erreur pendant la réparation

**Solution** :

1. Fermer tous les processus Homeflix
2. Attendre 30 secondes
3. Relancer avec réinstallation complète (Option 2)

### "Installation déjà détectée" mais Homeflix n'est pas installé

**Problème** : Faux positif de détection

**Cause** : Fichiers résiduels d'installation précédente

**Solution** :

```powershell
# Nettoyer manuellement
Remove-Item ".venv" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item ".venv310" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "client\node_modules" -Recurse -Force -ErrorAction SilentlyContinue

# Relancer l'installation
.\INSTALLER.ps1
```

### Erreur "Access Denied"

**Problème** : Permissions insuffisantes

**Solution** :

1. Fermer tous les terminaux et éditeurs de code
2. Fermer tous les navigateurs avec Homeflix ouvert
3. Relancer l'installateur

### Les dépendances ne s'installent pas

**Problème** : Erreur réseau ou cache corrompu

**Solution** :

```powershell
# Nettoyer le cache pip
python -m pip cache purge

# Nettoyer le cache npm
npm cache clean --force

# Relancer l'installateur avec réinstallation complète
.\INSTALLER.ps1  # Choisir Option 2
```

---

## ⚡ Mode Expert : Réparation Manuelle

### Réparer uniquement Python

```powershell
# Supprimer l'environnement
Remove-Item ".venv310" -Recurse -Force

# Recréer
python -m venv .venv310

# Réinstaller les dépendances
.\.venv310\Scripts\pip.exe install -r server\requirements.txt
```

### Réparer uniquement Node.js

```powershell
# Supprimer node_modules
Remove-Item "client\node_modules" -Recurse -Force

# Réinstaller
cd client
npm install
cd ..
```

### Réparer la structure des dossiers

```powershell
# Créer les dossiers manquants
New-Item -ItemType Directory -Path "data" -Force
New-Item -ItemType Directory -Path "data\thumbs" -Force
New-Item -ItemType Directory -Path "data\posters" -Force
```

---

## 📊 Logs et Diagnostics

### Vérifier l'état de l'installation

```powershell
# Vérifier Python
Test-Path ".venv310\Scripts\python.exe"

# Vérifier Node.js
Test-Path "client\node_modules"

# Vérifier base de données
Test-Path "data\homeflix.db"

# Tester Python
.\.venv310\Scripts\python.exe --version

# Tester les imports Python
.\.venv310\Scripts\python.exe -c "import fastapi; print('OK')"
```

---

## ✅ Checklist Post-Réparation

Après une réparation réussie, vérifiez :

- [ ] `.\homeflix.ps1` démarre sans erreur
- [ ] L'interface web s'ouvre dans le navigateur
- [ ] Vos vidéos sont toujours visibles
- [ ] Vos profils utilisateurs sont intacts
- [ ] Les miniatures s'affichent correctement
- [ ] La lecture vidéo fonctionne

---

## 🎓 Conseils de Prévention

Pour éviter de devoir réparer :

1. **Ne pas modifier manuellement** `.venv` ou `node_modules`
2. **Toujours fermer proprement** Homeflix (Ctrl+C)
3. **Sauvegarder régulièrement** `data\homeflix.db`
4. **Mettre à jour via l'installateur** après un Git pull
5. **Ne pas déplacer** le dossier pendant que Homeflix tourne

---

**Dernière mise à jour** : 14 novembre 2025  
**Version** : Mode Réparation v1.0
