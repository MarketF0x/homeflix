<div align="center">

<img src="public/logo.svg" alt="Homeflix Logo" width="180" height="180"/>

# Homeflix

**Votre serveur de streaming personnel avec interface web moderne**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.0.0-green.svg)](CHANGELOG.md)
[![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](#)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](#)
[![Node](https://img.shields.io/badge/node-16+-green.svg)](#)
[![Production Ready](https://img.shields.io/badge/production-ready-success.svg)](docs/)
[![Security Audit](https://img.shields.io/badge/security-0%20vulnerabilities-success.svg)](#)

[Installation](#-installation-rapide) • [Fonctionnalités](#-fonctionnalités) • [Documentation](docs/) • [Support](#-support)

</div>

---

## 📖 Description

Homeflix est un serveur de streaming personnel open-source qui vous permet de gérer et regarder vos vidéos avec une interface web élégante et moderne. Alternative légère à Plex ou Jellyfin, Homeflix met l'accent sur la simplicité d'utilisation tout en offrant des fonctionnalités avancées.

### ✨ Points Forts

- 🚀 **Installation en un clic** - Lancez l'installateur et c'est tout
- 🎨 **Interface moderne** - Design réactif, sombre/clair, intuitive
- 👥 **Multi-profils** - Chaque utilisateur sa progression et ses préférences
- 📂 **Collections intelligentes** - Organisez vos films et séries automatiquement
- 🎞️ **Métadonnées automatiques** - Affiches et informations via TMDb
- 🎥 **Lecteur avancé** - Sous-titres, pistes audio, reprise automatique
- 🔐 **100% local** - Vos données restent chez vous
- 🆓 **Gratuit et open-source** - Licence MIT

---

## 🚀 Installation Rapide

### Prérequis

- **Windows 10/11** (64 bits)
- **Python 3.8+** ([Télécharger](https://www.python.org/downloads/))
- **Node.js 16+** ([Télécharger](https://nodejs.org/))
- **FFmpeg** (optionnel, recommandé) ([Télécharger](https://ffmpeg.org/download.html))

### Installation

1. **Téléchargez** la dernière version de Homeflix
2. **Extrayez** l'archive dans un dossier de votre choix
3. **Double-cliquez** sur `INSTALLER.ps1`
4. **Attendez** la fin de l'installation (quelques minutes)
5. **C'est prêt !** L'application s'ouvre automatiquement

### Configuration Initiale

#### 1️⃣ Clé API TMDb (gratuite)

Pour afficher les affiches et métadonnées :

1. Créez un compte sur [themoviedb.org](https://www.themoviedb.org)
2. Allez dans **Paramètres → API**
3. Demandez une clé API (gratuit, instantané)
4. Copiez la clé dans `settings.yaml`

#### 2️⃣ Ajoutez vos dossiers vidéos

Éditez `settings.yaml` :

```yaml
tmdb:
  api_key: "VOTRE_CLE_API_ICI"

video_folders:
  - "C:/Mes Videos/Films"
  - "D:/Series"
```

**C'est tout !** Lancez `homeflix.ps1` et profitez.

---

## 🎯 Fonctionnalités

### 🎬 Gestion de Bibliothèque

- **Scan automatique** de vos dossiers vidéos
- **Détection intelligente** (films, séries, documentaires)
- **Métadonnées TMDb** (affiches, synopsis, acteurs, notes)
- **Miniatures** générées automatiquement
- **Recherche rapide** par titre, acteur, genre, année
- **Tri et filtres** avancés

### 👥 Profils Utilisateurs

- **Profils multiples** pour toute la famille
- **Protection par mot de passe** optionnelle
- **Progression individuelle** - chaque profil sa reprise
- **Préférences personnalisées** (langue audio/sous-titres)
- **Historique de visionnage**

### 📂 Collections

- **Organisation automatique** (Marvel, Disney, franchises)
- **Collections personnalisées**
- **Fusion intelligente** des doublons
- **Affiches de collection** personnalisables
- **Gestion simplifiée**

### 🎥 Lecteur Vidéo

- **Lecture directe** ou **transcodage FFmpeg**
- **Reprise automatique** là où vous étiez
- **Sous-titres** (VTT, SRT) avec auto-sélection
- **Pistes audio multiples** avec détection automatique
- **Contrôles tactiles** et raccourcis clavier
- **Mode plein écran** optimisé
- **Sélection de qualité** (720p, 1080p, 4K)

### 🔧 Fonctions Avancées

- **Mode sombre/clair** avec transition fluide
- **Masquer des vidéos** de la bibliothèque
- **Marquer comme vu/non vu**
- **Gestion des séries** par saisons et épisodes
- **Export/Import** de collections
- **API REST** complète pour intégrations

---

## 📚 Documentation

**📖 Toute la documentation est dans le dossier [`docs/`](docs/)**

| Document | Description |
|----------|-------------|
| [🚀 LANCEMENT.md](docs/LANCEMENT.md) | **Démarrez ici** - Vue d'ensemble et prochaines étapes |
| [📖 GUIDE_UTILISATEUR.md](docs/GUIDE_UTILISATEUR.md) | Guide complet d'installation et d'utilisation |
| [❓ FAQ.md](docs/FAQ.md) | Questions fréquentes et dépannage |
| [🔧 BUILD_PRODUCTION.md](docs/BUILD_PRODUCTION.md) | Créer des builds de production |
| [✅ CHECKLIST_COMMERCIALISATION.md](docs/CHECKLIST_COMMERCIALISATION.md) | État de préparation commerciale |

� **[Accéder à toute la documentation](docs/)**

---

## 💻 Utilisation

### Démarrer Homeflix

```powershell
# Double-clic ou exécutez :
.\homeflix.ps1
```

L'application s'ouvre automatiquement à : `http://localhost:5173`

### Arrêter Homeflix

- Fermez la fenêtre PowerShell, ou
- Appuyez sur `Ctrl+C`

### Mettre à jour

```powershell
# Téléchargez la nouvelle version et :
.\INSTALLER.ps1
# → Choisissez "Réparation" pour conserver vos données
```

---

## 🛠️ Dépannage

### Les vidéos ne se lisent pas

**Solution** : Installez FFmpeg et activez le transcodage

```powershell
# Vérifier si FFmpeg est installé
ffmpeg -version

# Si non installé, téléchargez depuis ffmpeg.org
```

### Port déjà utilisé

**Solution** : Libérez les ports 5173 et 8000

```powershell
# Trouver le processus
netstat -ano | findstr :5173

# Arrêter le processus (remplacez XXXX par le PID)
Stop-Process -Id XXXX -Force
```

### Les affiches ne s'affichent pas

**Solution** : Vérifiez votre clé API TMDb dans `settings.yaml`

---

## 🤝 Support

### 📌 Issues GitHub

Pour signaler un bug ou suggérer une fonctionnalité :
[Ouvrir un ticket](https://github.com/MarketF0x/homeflix/issues)

### 📧 Contact

Pour toute question : voir les issues GitHub

### 🌐 Communauté

- ⭐ **Star le projet** si vous l'aimez !
- 🐛 **Signalez les bugs** pour nous aider à améliorer
- 💡 **Proposez des fonctionnalités**
- 🔧 **Contribuez** au code (Pull Requests bienvenues)

---

## 🏗️ Pour les Développeurs

### Architecture

```
homeflix/
├── client/          # Frontend React + Vite
├── server/          # Backend FastAPI (Python)
├── electron/        # Packaging Electron
└── installer/       # Scripts d'installation
```

### Développement

```powershell
# Installer les dépendances
cd client
npm install
cd ../server
pip install -r requirements.txt

# Lancer en mode dev
cd ..
.\homeflix-dev.ps1
```

### Build de Production

```powershell
# Build client optimisé
npm run build

# Valider le build
python validate-build.py

# Créer une release
.\create-release.ps1 -Version "1.0.0"
```

---

## 📜 Licence

Homeflix est distribué sous **licence MIT**. Voir [LICENSE](LICENSE) pour plus de détails.

### Mentions Tierces

- **TMDb** : Ce produit utilise l'API TMDb mais n'est ni approuvé ni certifié par TMDb.
- **FFmpeg** : Utilisé comme outil externe optionnel (LGPL/GPL).
- Voir [LICENSE](LICENSE) pour la liste complète des dépendances.

---

## 🙏 Crédits

Homeflix est développé avec ❤️ par la communauté open-source.

**Technologies utilisées :**

- [React](https://react.dev/) - Interface utilisateur
- [Vite](https://vitejs.dev/) - Build tool
- [FastAPI](https://fastapi.tiangolo.com/) - Backend API
- [SQLAlchemy](https://www.sqlalchemy.org/) - ORM
- [TMDb API](https://www.themoviedb.org/documentation/api) - Métadonnées
- [FFmpeg](https://ffmpeg.org/) - Traitement vidéo

---

## 🌟 Remerciements

Merci à tous les contributeurs et utilisateurs qui rendent Homeflix meilleur chaque jour !

**Vous aimez Homeflix ? Donnez-lui une ⭐ sur GitHub !**

---

<div align="center">

**[⬆ Retour en haut](#-homeflix)**

Made with ❤️ for the home streaming community

</div>


video_folders:

  - "C:\\Mes\\Videos"

  - "D:\\Films"```powershell```.\setup-tmdb-key.ps1

  - "E:\\Series"

```.\DESINSTALLER.ps1



3. Relancez Homeflix``````

4. Vos vidéos apparaîtront automatiquement avec métadonnées et miniatures



---

**Options** :L'application s'ouvre automatiquement dans votre navigateur :

## ⚙️ Configuration Avancée

- `.\DESINSTALLER.ps1 -KeepData` - Conserve la base de données

### Clé API TMDb (Recommandée)

- `.\DESINSTALLER.ps1 -Force` - Désinstalle sans confirmation- **Interface Web** : http://localhost:5173📚 **Guide complet** : [GUIDE_TMDB_API_KEY.md](GUIDE_TMDB_API_KEY.md)

Pour obtenir automatiquement les affiches, synopsis, acteurs :



```powershell

.\.config\setup-tmdb-key.ps1---- **Accès Réseau Local** : Disponible sur votre WiFi

```



Le script vous guidera pour obtenir une clé gratuite en 2 minutes.

## 📁 Ajouter vos Vidéos- **Accès Distant** : Via Tailscale (si configuré)### Lancer l'Application

📖 **Guide détaillé** : [`.docs/GUIDE_TMDB_API_KEY.md`](.docs/GUIDE_TMDB_API_KEY.md)



### Accès Réseau

1. Ouvrez le fichier **`settings.yaml`**

Pour accéder à Homeflix depuis d'autres appareils (téléphone, tablette, TV) :

2. Ajoutez vos dossiers de vidéos :

```powershell

.\.config\configure-network-access.ps1### Arrêter l'Application```powershell

```

```yaml

### Profils Utilisateurs

video_folders:.\start-homeflix.ps1 -Mode production

Créez des profils pour chaque membre de la famille avec restrictions parentales :

  - "C:\\Mes\\Videos"

📖 **Guide des profils** : [`.docs/GUIDE_PROFILS.md`](.docs/GUIDE_PROFILS.md)

  - "D:\\Films"Fermez simplement la fenêtre PowerShell ou appuyez sur `Ctrl+C`.```

### Compression Vidéos

  - "E:\\Series"

Pour réduire la taille des vidéos volumineuses :

```

```powershell

python .\.utils\compress_large_videos.py

```

3. Relancez Homeflix---L'application démarre en arrière-plan (aucune fenêtre visible) :

📖 **Guide compression** : [`.docs/GUIDE_COMPRESSION.md`](.docs/GUIDE_COMPRESSION.md)

4. Vos vidéos apparaîtront automatiquement avec métadonnées et miniatures

---

- **Interface Web** : http://localhost:5173

## 📚 Documentation

---

Toute la documentation technique est disponible dans le dossier **`.docs/`** :

## 📁 Ajouter vos Vidéos- **API Backend** : http://localhost:8000

| Guide | Description |

|-------|-------------|## ⚙️ Configuration Avancée

| **[GUIDE_DEMARRAGE.md](.docs/GUIDE_DEMARRAGE.md)** | Installation et configuration complète |

| **[MODE_REPARATION.md](.docs/MODE_REPARATION.md)** | Réparer une installation existante |

| **[GUIDE_DESINSTALLATION.md](.docs/GUIDE_DESINSTALLATION.md)** | Désinstaller Homeflix |

| **[GUIDE_PROFILS.md](.docs/GUIDE_PROFILS.md)** | Gestion des profils utilisateurs |### Clé API TMDb (Recommandée)

| **[GUIDE_COMPRESSION.md](.docs/GUIDE_COMPRESSION.md)** | Optimisation de l'espace disque |

| **[GUIDE_TMDB_API_KEY.md](.docs/GUIDE_TMDB_API_KEY.md)** | Configuration TMDb |1. Ouvrez le fichier **`settings.yaml`**## ⚖️ Licence et Usage Commercial

| **[ACCES_RESEAU.md](.docs/ACCES_RESEAU.md)** | Accès depuis d'autres appareils |

| **[PARTAGE_RESEAU.md](.docs/PARTAGE_RESEAU.md)** | Partage sur le réseau local |Pour obtenir automatiquement les affiches, synopsis, acteurs :



---2. Ajoutez vos dossiers de vidéos :



## ⚖️ Licence```powershell



**Homeflix** est distribué sous [licence MIT](LICENSE) - **libre d'utilisation, y compris commerciale**..\.config\setup-tmdb-key.ps1Homeflix est distribué sous **licence MIT** - libre d'utilisation, y compris commerciale.



### Usage Commercial```



- ✅ Le code source est libre (MIT)```yaml

- ⚠️ **L'API TMDb** nécessite une licence commerciale pour usage commercial

Le script vous guidera pour obtenir une clé gratuite en 2 minutes.

📄 **Détails légaux** : [`.docs/TMDB_TERMS_SUMMARY.md`](.docs/TMDB_TERMS_SUMMARY.md)

video_folders:**Cependant** : L'API TMDb a des restrictions pour l'usage commercial.

---

📖 **Guide détaillé** : [`.docs/GUIDE_TMDB_API_KEY.md`](.docs/GUIDE_TMDB_API_KEY.md)

## 🆘 Besoin d'Aide ?

  - "C:\\Mes\\Videos"

- **Problème de démarrage** → Consultez [`.docs/GUIDE_DEMARRAGE.md`](.docs/GUIDE_DEMARRAGE.md)

- **Problème d'installation** → Utilisez le mode réparation ([`.docs/MODE_REPARATION.md`](.docs/MODE_REPARATION.md))### Accès Réseau

- **Problème de réseau** → Consultez [`.docs/ACCES_RESEAU.md`](.docs/ACCES_RESEAU.md)

- **Vidéos ne s'affichent pas** → Vérifiez `settings.yaml` et relancez  - "D:\\Films"- ✅ **Usage Personnel/Gratuit** → Clé API gratuite

- **Erreur FFmpeg** → Le script l'installe automatiquement au premier lancement

Pour accéder à Homeflix depuis d'autres appareils (téléphone, tablette, TV) :

---

  - "E:\\Series"- ⚠️ **Usage Commercial** → Licence commerciale TMDb requise

## 🎯 Fonctionnalités Principales

```powershell

✅ **Streaming Vidéo** - Lecture directe ou transcodage automatique  

✅ **Métadonnées Enrichies** - Affiches, synopsis, acteurs via TMDb  .\.config\configure-network-access.ps1```

✅ **Thumbnails Automatiques** - Génération de vignettes  

✅ **Multi-pistes** - Audio et sous-titres multiples  ```

✅ **Profils Utilisateurs** - Gestion familiale avec restrictions  

✅ **Recherche Avancée** - Par titre, genre, année, réalisateur  📄 **Détails** : [TMDB_TERMS_SUMMARY.md](TMDB_TERMS_SUMMARY.md) et [ANALYSE_LICENCES_COMMERCIAL.md](ANALYSE_LICENCES_COMMERCIAL.md)

✅ **Interface Moderne** - React avec animations 3D  

✅ **Accès Multi-Appareils** - PC, mobile, tablette, TV  ### Profils Utilisateurs



---3. Relancez Homeflix



**Version 2.0** • Développé avec ❤️ • MIT LicenseCréez des profils pour chaque membre de la famille avec restrictions parentales :


4. Vos vidéos apparaîtront automatiquement avec métadonnées et miniatures## 📋 Fonctionnalités

📖 **Guide des profils** : [`.docs/GUIDE_PROFILS.md`](.docs/GUIDE_PROFILS.md)



### Compression Vidéos

---- ✅ **Streaming Vidéo** : Lecture directe ou transcodage automatique

Pour réduire la taille des vidéos volumineuses :

- ✅ **Métadonnées Enrichies** : Récupération automatique via TMDb

```powershell

python .\.utils\compress_large_videos.py## ⚙️ Configuration Avancée- ✅ **Thumbnails** : Génération automatique de vignettes

```

- ✅ **Multi-pistes Audio/Sous-titres** : Sélection facile dans le lecteur

📖 **Guide compression** : [`.docs/GUIDE_COMPRESSION.md`](.docs/GUIDE_COMPRESSION.md)

### Clé API TMDb (Recommandée)- ✅ **Compression** : Option de compression pour les gros fichiers

---

- ✅ **Nettoyage Auto** : Suppression des tags techniques dans les titres

## 📚 Documentation

Pour obtenir automatiquement les affiches, synopsis, acteurs :- ✅ **Recherche** : Par titre, genre, année, réalisateur

Toute la documentation technique est disponible dans le dossier **`.docs/`** :

- ✅ **Interface Moderne** : React + Vite avec fond WebGL

| Guide | Description |

|-------|-------------|```powershell- ✅ **👥 Gestion des Profils** : Profils utilisateurs avec avatars personnalisés et restrictions

| **[GUIDE_DEMARRAGE.md](.docs/GUIDE_DEMARRAGE.md)** | Installation et configuration complète |

| **[GUIDE_PROFILS.md](.docs/GUIDE_PROFILS.md)** | Gestion des profils utilisateurs |.\.config\setup-tmdb-key.ps1

| **[GUIDE_COMPRESSION.md](.docs/GUIDE_COMPRESSION.md)** | Optimisation de l'espace disque |

| **[GUIDE_TMDB_API_KEY.md](.docs/GUIDE_TMDB_API_KEY.md)** | Configuration TMDb |```## 👥 Nouveauté : Gestion des Profils

| **[ACCES_RESEAU.md](.docs/ACCES_RESEAU.md)** | Accès depuis d'autres appareils |

| **[PARTAGE_RESEAU.md](.docs/PARTAGE_RESEAU.md)** | Partage sur le réseau local |



---Le script vous guidera pour obtenir une clé gratuite en 2 minutes.Homeflix intègre désormais un système complet de gestion des profils :



## ⚖️ Licence- **Profil Principal** automatique avec tous les droits



**Homeflix** est distribué sous [licence MIT](LICENSE) - **libre d'utilisation, y compris commerciale**.📖 **Guide détaillé** : [`.docs/GUIDE_TMDB_API_KEY.md`](.docs/GUIDE_TMDB_API_KEY.md)- **Profils Secondaires** personnalisables (nom, avatar, restrictions)



### Usage Commercial- **12 Avatars** au choix (personnages et formes abstraites)



- ✅ Le code source est libre (MIT)### Accès Réseau- **Restrictions** : Mode enfants, masquage contenu adulte

- ⚠️ **L'API TMDb** nécessite une licence commerciale pour usage commercial

- **Interface Intuitive** : Sélection au démarrage, changement rapide

📄 **Détails légaux** : [`.docs/TMDB_TERMS_SUMMARY.md`](.docs/TMDB_TERMS_SUMMARY.md)

Pour accéder à Homeflix depuis d'autres appareils (téléphone, tablette, TV) :

---

📖 **Guide détaillé** : Consultez [GUIDE_PROFILS.md](GUIDE_PROFILS.md)

## 🆘 Besoin d'Aide ?

```powershell

- **Problème de démarrage** → Consultez [`.docs/GUIDE_DEMARRAGE.md`](.docs/GUIDE_DEMARRAGE.md)

- **Problème de réseau** → Consultez [`.docs/ACCES_RESEAU.md`](.docs/ACCES_RESEAU.md).\.config\configure-network-access.ps1## 🛠️ Configuration

- **Vidéos ne s'affichent pas** → Vérifiez `settings.yaml` et relancez

- **Erreur FFmpeg** → Le script l'installe automatiquement au premier lancement```



---### Ajouter vos Vidéos



## 🎯 Fonctionnalités Principales### Profils Utilisateurs



✅ **Streaming Vidéo** - Lecture directe ou transcodage automatique  1. Modifier `settings.yaml` :

✅ **Métadonnées Enrichies** - Affiches, synopsis, acteurs via TMDb  

✅ **Thumbnails Automatiques** - Génération de vignettes  Créez des profils pour chaque membre de la famille avec restrictions parentales :```yaml

✅ **Multi-pistes** - Audio et sous-titres multiples  

✅ **Profils Utilisateurs** - Gestion familiale avec restrictions  video_folders:

✅ **Recherche Avancée** - Par titre, genre, année, réalisateur  

✅ **Interface Moderne** - React avec animations 3D  📖 **Guide des profils** : [`.docs/GUIDE_PROFILS.md`](.docs/GUIDE_PROFILS.md)  - "C:\\Mes\\Videos"

✅ **Accès Multi-Appareils** - PC, mobile, tablette, TV  

  - "D:\\Films"

---

### Compression Vidéos```

**Version 2.0** • Développé avec ❤️ • MIT License



Pour réduire la taille des vidéos volumineuses :2. Redémarrer l'application



```powershell### Activer TMDb (Recommandé)

.\.utils\compress_large_videos.py

```1. Obtenir une clé API sur https://www.themoviedb.org/settings/api

2. Modifier `settings.yaml` :

📖 **Guide compression** : [`.docs/GUIDE_COMPRESSION.md`](.docs/GUIDE_COMPRESSION.md)```yaml

tmdb_api_key: "votre_clé_api"

---```



## 📚 Documentation## 📁 Structure du Projet



Toute la documentation technique est disponible dans le dossier **`.docs/`** :```

homeflix/

| Guide | Description |├── server/          # Backend FastAPI (Python)

|-------|-------------|│   ├── main.py      # Point d'entrée

| **[GUIDE_DEMARRAGE.md](.docs/GUIDE_DEMARRAGE.md)** | Installation et configuration complète |│   ├── api/         # Routes API

| **[GUIDE_PROFILS.md](.docs/GUIDE_PROFILS.md)** | Gestion des profils utilisateurs |│   └── core/        # Logique métier

| **[GUIDE_COMPRESSION.md](.docs/GUIDE_COMPRESSION.md)** | Optimisation de l'espace disque |├── client/          # Frontend React + Vite

| **[GUIDE_TMDB_API_KEY.md](.docs/GUIDE_TMDB_API_KEY.md)** | Configuration TMDb |│   └── src/         # Composants React

| **[ACCES_RESEAU.md](.docs/ACCES_RESEAU.md)** | Accès depuis d'autres appareils |├── data/            # Base de données SQLite

| **[PARTAGE_RESEAU.md](.docs/PARTAGE_RESEAU.md)** | Partage sur le réseau local |└── settings.yaml    # Configuration

```

---

## 🔧 Scripts Utiles

## ⚖️ Licence

### Compression Manuelle

**Homeflix** est distribué sous [licence MIT](LICENSE) - **libre d'utilisation, y compris commerciale**.

```powershell

### Usage Commercialpython compress_one_video.py "chemin/vers/video.mkv"

```

- ✅ Le code source est libre (MIT)

- ⚠️ **L'API TMDb** nécessite une licence commerciale pour usage commercial### Compression de Masse



📄 **Détails légaux** : [`.docs/TMDB_TERMS_SUMMARY.md`](.docs/TMDB_TERMS_SUMMARY.md)```powershell

python compress_background.py

---```



## 🆘 Besoin d'Aide ?### Nettoyage des Noms de Fichiers



- **Problème de démarrage** → Consultez [`.docs/GUIDE_DEMARRAGE.md`](.docs/GUIDE_DEMARRAGE.md)```powershell

- **Problème de réseau** → Consultez [`.docs/ACCES_RESEAU.md`](.docs/ACCES_RESEAU.md)python clean_filenames.py

- **Vidéos ne s'affichent pas** → Vérifiez `settings.yaml` et relancez```

- **Erreur FFmpeg** → Le script l'installe automatiquement au premier lancement

## 🌐 Accès Réseau

---

### Local (même ordinateur)

## 🎯 Fonctionnalités Principales- http://localhost:5173



✅ **Streaming Vidéo** - Lecture directe ou transcodage automatique  ### Réseau Local (autres appareils)

✅ **Métadonnées Enrichies** - Affiches, synopsis, acteurs via TMDb  - http://[votre-ip]:5173

✅ **Thumbnails Automatiques** - Génération de vignettes  - Exemple : http://192.168.1.5:5173

✅ **Multi-pistes** - Audio et sous-titres multiples  

✅ **Profils Utilisateurs** - Gestion familiale avec restrictions  ### Internet (avec Tailscale)

✅ **Recherche Avancée** - Par titre, genre, année, réalisateur  ```powershell

✅ **Interface Moderne** - React avec animations 3D  .\install-tailscale.ps1

✅ **Accès Multi-Appareils** - PC, mobile, tablette, TV  ```



---## ⚙️ Technologies



**Version 2.0** • Développé avec ❤️ • MIT License- **Backend** : Python 3.10, FastAPI, Uvicorn, SQLite

- **Frontend** : React 18, Vite, Three.js
- **Streaming** : FFmpeg (transcodage H.264/AAC)
- **Métadonnées** : TMDb API
- **Thumbnails** : OpenCV

## 📝 Modes de Démarrage

```powershell
# Production (recommandé) - Arrière-plan silencieux
.\start-homeflix.ps1 -Mode production

# Développement - Rechargement automatique
.\start-homeflix.ps1 -Mode dev

# Simple - Fenêtres PowerShell séparées
.\start-homeflix.ps1 -Mode simple
```

## 🛑 Arrêt de l'Application

Les serveurs tournent en arrière-plan. Pour les arrêter :

```powershell
Get-Process | Where-Object {$_.ProcessName -eq "python" -or $_.ProcessName -eq "node"} | Stop-Process -Force
```

Ou via le Gestionnaire des tâches Windows.

## 📚 Documentation

- `README_UTILISATION.md` - Guide utilisateur complet
- `GUIDE_COMPRESSION.md` - Compression et optimisation vidéo
- `GUIDE_PISTES_AUDIO_SOUSTITRES.md` - Gestion des pistes audio/sous-titres
- `AMELIORATIONS_STREAMING_v2.md` - Optimisations streaming
- `ACCES_INTERNET.md` - Accès depuis internet
- `PARTAGE_RESEAU.md` - Partage réseau local
- `ESPACE_DISQUE.md` - Gestion de l'espace disque

## 🐛 Dépannage

### Le frontend ne démarre pas
```powershell
cd client
npm install
npm run dev
```

### Le backend ne démarre pas
```powershell
.\.venv310\Scripts\python.exe -m uvicorn server.main:app --reload
```

### Port déjà utilisé
```powershell
# Libérer le port 8000
Get-Process | Where-Object {(Get-NetTCPConnection -OwningProcess $_.Id -ErrorAction SilentlyContinue).LocalPort -eq 8000} | Stop-Process -Force

# Libérer le port 5173
Get-Process | Where-Object {(Get-NetTCPConnection -OwningProcess $_.Id -ErrorAction SilentlyContinue).LocalPort -eq 5173} | Stop-Process -Force
```

## 📄 Licence

Projet personnel - Tous droits réservés

## 🙏 Crédits

- TMDb pour les métadonnées de films
- FFmpeg pour le transcodage vidéo
- React et Vite pour l'interface moderne
