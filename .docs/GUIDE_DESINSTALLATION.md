# 🗑️ GUIDE DE DÉSINSTALLATION

Guide complet pour désinstaller Homeflix de votre système.

---

## 🚀 Désinstallation Rapide

### Méthode Simple

Double-cliquez sur **`DESINSTALLER.ps1`** ou exécutez :

```powershell
.\DESINSTALLER.ps1
```

Le script vous demandera confirmation avant de procéder.

---

## 📋 Options Disponibles

### Conserver les Données

Pour désinstaller Homeflix tout en conservant votre base de données et configuration :

```powershell
.\DESINSTALLER.ps1 -KeepData
```

**Conservé** :
- `data\homeflix.db` - Base de données complète
- `settings.yaml` - Configuration
- Vos dossiers de vidéos (non touchés)

**Supprimé** :
- Environnements Python (`.venv`, `.venv310`)
- Dépendances Node.js (`node_modules`)
- Fichiers générés (miniatures, posters, cache)
- Raccourcis bureau
- Règles de pare-feu

### Désinstallation Silencieuse

Pour désinstaller sans confirmation (scripts automatisés) :

```powershell
.\DESINSTALLER.ps1 -Force
```

### Désinstallation Complète

Pour tout supprimer y compris la base de données :

```powershell
.\DESINSTALLER.ps1
```

Puis répondez **O** (Oui) à la confirmation.

---

## 🔍 Ce qui est Supprimé

### Environnements et Dépendances

- ✅ `.venv/` - Environnement virtuel Python principal
- ✅ `.venv310/` - Environnement virtuel Python 3.10
- ✅ `client/node_modules/` - Dépendances JavaScript
- ✅ `client/dist/` - Build frontend

### Fichiers Générés

- ✅ `data/thumbs/` - Miniatures vidéos
- ✅ `data/posters/` - Affiches téléchargées
- ✅ `server/__pycache__/` - Cache Python
- ✅ `.homeflix.lock` - Fichier de verrouillage

### Configuration Système

- ✅ Raccourcis bureau (`Homeflix.lnk`, `HomeOne.lnk`)
- ✅ Règles de pare-feu Windows (nécessite droits admin)
- ✅ Processus en cours (backend/frontend)
- ✅ Ports libérés (8000, 5173)

### Base de Données (optionnel)

- ⚠️ `data/homeflix.db` - Supprimé **uniquement si -KeepData non spécifié**
- ⚠️ `data/*.db-*` - Fichiers de backup SQLite

---

## 🛡️ Sécurité et Précautions

### Sauvegarde Manuelle (Recommandé)

Avant désinstallation, sauvegardez manuellement :

```powershell
# Créer un dossier de sauvegarde
New-Item -ItemType Directory -Path "$env:USERPROFILE\Documents\Homeflix_Backup" -Force

# Copier la base de données
Copy-Item "data\homeflix.db" "$env:USERPROFILE\Documents\Homeflix_Backup\" -Force

# Copier la configuration
Copy-Item "settings.yaml" "$env:USERPROFILE\Documents\Homeflix_Backup\" -Force
```

### Droits Administrateur

Le script peut fonctionner sans droits admin, mais certaines opérations seront limitées :

- ❌ **Sans admin** : Les règles de pare-feu ne seront pas supprimées
- ✅ **Avec admin** : Désinstallation complète incluant pare-feu

Pour exécuter en tant qu'administrateur :

1. Clic droit sur `DESINSTALLER.ps1`
2. Sélectionner "Exécuter en tant qu'administrateur"

---

## 🔄 Réinstallation Après Désinstallation

### Avec Conservation des Données

Si vous avez utilisé `-KeepData` :

```powershell
# Réinstaller
.\INSTALLER.ps1

# Vos vidéos et profils seront automatiquement restaurés
.\homeflix.ps1
```

### Depuis Sauvegarde Manuelle

Si vous avez sauvegardé manuellement :

```powershell
# Réinstaller
.\INSTALLER.ps1

# Restaurer la base de données
Copy-Item "$env:USERPROFILE\Documents\Homeflix_Backup\homeflix.db" "data\" -Force

# Restaurer la configuration
Copy-Item "$env:USERPROFILE\Documents\Homeflix_Backup\settings.yaml" "." -Force

# Lancer
.\homeflix.ps1
```

---

## 🐛 Dépannage

### Le script ne se lance pas

**Problème** : PowerShell bloque l'exécution de scripts

**Solution** :

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\DESINSTALLER.ps1
```

### Erreur "Accès refusé"

**Problème** : Fichiers ou processus verrouillés

**Solution** :

1. Fermez tous les navigateurs avec Homeflix ouvert
2. Attendez 30 secondes
3. Relancez le désinstalleur

### Les règles de pare-feu ne sont pas supprimées

**Problème** : Pas de droits administrateur

**Solution** :

```powershell
# Exécuter en tant qu'administrateur
Start-Process powershell -Verb RunAs -ArgumentList "-File `"$PWD\DESINSTALLER.ps1`""
```

Ou manuellement :

```powershell
# En tant qu'administrateur
Remove-NetFirewallRule -DisplayName "Homeflix Backend" -ErrorAction SilentlyContinue
Remove-NetFirewallRule -DisplayName "Homeflix Frontend" -ErrorAction SilentlyContinue
```

### Les processus ne s'arrêtent pas

**Problème** : Processus bloqués

**Solution manuelle** :

```powershell
# Arrêter tous les processus Python
Get-Process -Name python | Stop-Process -Force

# Arrêter tous les processus Node
Get-Process -Name node | Stop-Process -Force

# Relancer le désinstalleur
.\DESINSTALLER.ps1
```

### Le dossier ne peut pas être supprimé

**Problème** : Fichiers verrouillés après désinstallation

**Solution** :

1. Redémarrez l'ordinateur
2. Supprimez manuellement le dossier `homeflix`

---

## 📊 Espace Disque Récupéré

Espace typiquement libéré après désinstallation :

| Élément | Taille Moyenne |
|---------|----------------|
| `.venv/` + `.venv310/` | ~500 MB |
| `node_modules/` | ~300 MB |
| `data/thumbs/` | ~50-200 MB (dépend du nombre de vidéos) |
| `data/posters/` | ~10-50 MB |
| `__pycache__/` + `dist/` | ~5 MB |
| **Total (sans DB)** | **~900 MB - 1 GB** |
| Base de données | Variable (dépend de l'usage) |

---

## ✅ Vérification Post-Désinstallation

Pour vérifier que tout a été supprimé :

```powershell
# Vérifier les processus
Get-Process -Name python,node -ErrorAction SilentlyContinue

# Vérifier les ports
Get-NetTCPConnection -LocalPort 8000,5173 -ErrorAction SilentlyContinue

# Vérifier les règles de pare-feu
Get-NetFirewallRule -DisplayName "*Homeflix*" -ErrorAction SilentlyContinue

# Vérifier les raccourcis
Test-Path "$env:USERPROFILE\Desktop\Homeflix.lnk"
```

**Résultats attendus** : Aucun processus, aucun port occupé, aucune règle, aucun raccourci.

---

## 🔙 Alternative : Désactivation Temporaire

Si vous voulez juste arrêter Homeflix temporairement sans désinstaller :

### Arrêter les Serveurs

```powershell
# Méthode 1 : Fermer la fenêtre PowerShell de Homeflix
# Ou appuyer sur Ctrl+C

# Méthode 2 : Arrêter manuellement
Get-Process -Name python,node | Where-Object { $_.Path -like "*homeflix*" } | Stop-Process -Force
```

### Désactiver le Démarrage Automatique

Si vous avez configuré un démarrage automatique :

1. Ouvrir : `shell:startup` (Win+R)
2. Supprimer le raccourci Homeflix

---

## 📞 Support

Pour toute question ou problème de désinstallation :

1. Consultez la section **Dépannage** ci-dessus
2. Vérifiez les logs dans le terminal PowerShell
3. En dernier recours, suppression manuelle du dossier après redémarrage

---

**Dernière mise à jour** : 14 novembre 2025  
**Version du script** : DESINSTALLER.ps1 v1.0
