# 🎬 HomeOne - Guide de Démarrage Rapide# 🚀 Démarrage rapide HomeOne



Bienvenue dans **HomeOne**, votre gestionnaire de bibliothèque vidéo personnel avec interface Netflix-style !## 🎯 Lancement de l'application complète



## 🚀 Installation (5 minutes)### Option 1 : Double-clic sur le raccourci Bureau

Si vous avez créé le raccourci, double-cliquez simplement sur **HomeOne** sur votre Bureau.

### Windows

### Option 2 : Depuis la racine du projet

```powershell```powershell

.\install.ps1cd C:\Users\fparo\Desktop\homeflix

```.\launch_homeone.ps1

```

### Linux/macOS

L'application ouvrira automatiquement votre navigateur sur **http://localhost:5173**

```bash

chmod +x install.sh---

./install.sh

```## 🔧 Lancement manuel (développement)



## ▶️ Lancement### Backend seul (serveur API)

```powershell

### Windowscd C:\Users\fparo\Desktop\homeflix\server

.\start.ps1

```powershell```

.\start-dev.ps1Accessible sur : **http://127.0.0.1:8000**  

```Documentation API : **http://127.0.0.1:8000/docs**



Ou double-cliquez sur le raccourci Bureau si créé :### Frontend seul (interface React)

```powershell

```powershellcd C:\Users\fparo\Desktop\homeflix\client

.\create_shortcut.ps1npm run dev

``````

Accessible sur : **http://localhost:5173**

### Linux/macOS

---

```bash

./start.sh## 📁 Structure des scripts

```

- **`launch_homeone.ps1`** (racine) - Lance backend + frontend + ouvre navigateur

L'application s'ouvre automatiquement sur `http://localhost:5173`- **`launch_homeone_silent.vbs`** (racine) - Même chose en mode silencieux

- **`server/start.ps1`** - Lance uniquement le backend

## ⚙️ Configuration Initiale- **`create_shortcut.ps1`** - Crée le raccourci Bureau



Éditez `settings.yaml` :---



```yaml## ⚙️ Configuration

video_directories:

  - "C:/Vos/Videos"  # Remplacez par vos dossiersÉditez **`settings.yaml`** pour :

  - "D:/Films"- Ajouter/supprimer des dossiers vidéo

- Configurer la clé API TMDb

tmdb_api_key: "votre_cle"  # Optionnel - https://www.themoviedb.org/- Régler les durées films/séries

auto_clean_filenames: true # Nettoyage automatique des noms

```---



## 🎯 Fonctionnalités Principales## 🆘 Problèmes fréquents



- **📁 Scan automatique** : Indexation toutes les 10 minutes### "Le terme ... n'est pas reconnu"

- **🖼️ Miniatures** : Générées automatiquement via TMDb + FFmpeg➡️ Vous êtes dans le mauvais dossier. Les scripts sont à la **racine** du projet.

- **🔍 Filtres** : Films, séries, années, genres

- **⏸️ Reprise** : Reprend là où vous vous êtes arrêté### Le navigateur ne s'ouvre pas

- **🧹 Nettoyage** : Optimise les noms de fichiers pour TMDb➡️ Ouvrez manuellement : **http://localhost:5173**



## 🧹 Nettoyage des Fichiers (Recommandé)### Erreur "port déjà utilisé"

➡️ Un processus utilise déjà le port. Tuez-le :

Pour améliorer la reconnaissance TMDB :```powershell

Get-Process node | Stop-Process -Force

```powershellGet-Process python | Stop-Process -Force

# Aperçu```

python clean_filenames.py --preview

### Pas de vidéos affichées

# Exécution➡️ Lancez un scan :

python clean_filenames.py --execute```powershell

```curl -X POST http://localhost:8000/api/scan

```

## 🖼️ Génération de Miniatures

```powershell
# Génère toutes les miniatures manquantes
python generate_thumbnails.py
```

## 🐛 Dépannage Rapide

### Les vidéos ne s'affichent pas

- Vérifiez `settings.yaml` (chemins avec `/`)
- Relancez : `python server/main.py`

### Les miniatures sont manquantes

1. Vérifiez FFmpeg : `ffmpeg -version`
2. Ajoutez une clé TMDb dans `settings.yaml`
3. Lancez : `python generate_thumbnails.py`

### Erreur "Module not found"

```powershell
cd server
pip install -r requirements.txt
```

## 📚 Documentation Complète

Consultez `README.md` pour tous les détails.

## 🎉 Bon visionnage !
