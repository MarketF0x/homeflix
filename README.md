# 🎬 Homeflix# 🎬 Homeflix# 🎬 Homeflix



Votre serveur de streaming personnel pour vos vidéos avec interface web moderne.



---Votre serveur de streaming personnel pour vos vidéos avec interface web moderne.Votre serveur de streaming personnel pour vos vidéos avec interface web moderne.



## 🚀 Démarrage



### Installation---



Double-cliquez sur **`INSTALLER.ps1`** pour installer automatiquement.



**Déjà installé ?** Le script détecte automatiquement et propose :## 🚀 Démarrage---## 🚀 Démarrage Rapide

- 🔧 **Réparation** - Répare les fichiers corrompus (conserve vos données)

- 🔄 **Réinstallation** - Réinstalle tout en conservant la base de données



📖 **Mode réparation** : [`.docs/MODE_REPARATION.md`](.docs/MODE_REPARATION.md)### Installation



### Lancer l'Application



Double-cliquez sur **`homeflix.ps1`** pour démarrer.Double-cliquez sur **`INSTALLER.ps1`** pour installer automatiquement.## 🚀 Démarrage### Première Installation



L'application s'ouvre automatiquement dans votre navigateur.



### Arrêter l'Application### Lancer l'Application



Fermez simplement la fenêtre PowerShell ou appuyez sur `Ctrl+C`.



### DésinstallationDouble-cliquez sur **`homeflix.ps1`** pour démarrer.### Lancer l'Application```powershell



Pour désinstaller Homeflix :



```powershellL'application s'ouvre automatiquement dans votre navigateur..\install.ps1

.\DESINSTALLER.ps1

```



**Options** :### Arrêter l'ApplicationDouble-cliquez sur **`homeflix.ps1`** ou exécutez :```

- `.\DESINSTALLER.ps1 -KeepData` - Conserve la base de données

- `.\DESINSTALLER.ps1 -Force` - Désinstalle sans confirmation



📖 **Guide complet** : [`.docs/GUIDE_DESINSTALLATION.md`](.docs/GUIDE_DESINSTALLATION.md)Fermez simplement la fenêtre PowerShell ou appuyez sur `Ctrl+C`.



---



## 📁 Ajouter vos Vidéos### Désinstallation```powershell**Important** : Après l'installation, configurez votre clé API TMDb :



1. Ouvrez le fichier **`settings.yaml`**

2. Ajoutez vos dossiers de vidéos :

Pour désinstaller Homeflix :.\homeflix.ps1```powershell

```yaml

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
