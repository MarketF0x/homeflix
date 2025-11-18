
+.# 📖 Guide Utilisateur - Homeflix

Bienvenue dans **Homeflix**, votre solution de streaming personnelle pour gérer et regarder vos vidéos.

---

## 🚀 Installation Rapide

### Première Installation

1. **Téléchargez Homeflix** et extrayez le dossier
2. **Double-cliquez sur `INSTALLER.ps1`**
3. Attendez la fin de l'installation (quelques minutes)
4. L'application s'ouvrira automatiquement dans votre navigateur

### Configuration Initiale

#### 1️⃣ Obtenir une clé API TMDb (gratuit)

Pour afficher les affiches et informations de vos films/séries :

1. Créez un compte sur [https://www.themoviedb.org](https://www.themoviedb.org)
2. Allez dans **Paramètres** → **API**
3. Demandez une clé API (gratuit, instantané)
4. Copiez votre clé API

#### 2️⃣ Configurer vos dossiers vidéos

1. Ouvrez le fichier **`settings.yaml`** à la racine de Homeflix
2. Ajoutez vos dossiers de vidéos :

```yaml
tmdb:
  api_key: "VOTRE_CLE_API_ICI"

video_folders:
  - "C:/Mes Videos/Films"
  - "D:/Series"
  - "E:/Documentaires"
```

3. Sauvegardez le fichier

---

## 🎬 Utilisation

### Démarrer Homeflix

**Double-cliquez sur `homeflix.ps1`**

L'application s'ouvre automatiquement à l'adresse : `http://localhost:5173`

### Arrêter Homeflix

- **Fermez la fenêtre PowerShell**, ou
- **Appuyez sur `Ctrl+C`** dans la fenêtre

---

## 📚 Fonctionnalités Principales

### 🎞️ Gestion de Bibliothèque

- **Scanner automatiquement** vos dossiers vidéos
- **Téléchargement automatique** des affiches et métadonnées
- **Catégorisation** par films, séries, documentaires
- **Recherche rapide** par titre, acteur, genre

### 👥 Profils Utilisateurs

- **Créez plusieurs profils** (famille, invités, etc.)
- **Protection par mot de passe** optionnelle
- **Progression individuelle** par profil
- **Recommandations personnalisées**

### 📂 Collections

- **Organisez vos vidéos** en collections (Marvel, Disney, etc.)
- **Fusion automatique** de doublons
- **Gestion des affiches** personnalisées
- **Collections multi-vidéos**

### 🎥 Lecteur Vidéo

- **Lecture directe** ou transcodage automatique
- **Reprise de lecture** là où vous étiez
- **Sous-titres** automatiques (VTT, SRT)
- **Pistes audio multiples**
- **Contrôles tactiles** et raccourcis clavier

### 🔍 Fonctions Avancées

- **Masquer des vidéos** de la bibliothèque
- **Marquer comme vu/non vu**
- **Trier par date, titre, note**
- **Mode sombre/clair**

---

## ⚙️ Configuration Avancée

### Paramètres Vidéo

Dans `settings.yaml` :

```yaml
video:
  # Utiliser le transcodage FFmpeg par défaut
  use_transcode_by_default: false
  
  # Qualité de transcodage (720p, 1080p)
  transcode_quality: "1080p"
  
  # Langue audio préférée
  preferred_audio_language: "fr"
  
  # Langue des sous-titres par défaut
  preferred_subtitle_language: "fr"
```

### Limite de Reprise

Contrôlez quand la lecture reprend automatiquement :

```yaml
resume:
  # Reprendre uniquement si vidéo visionnée à plus de X%
  minimum_percent: 5
  
  # Ne pas reprendre si vidéo visionnée à plus de Y%
  maximum_percent: 90
```

### Performance

```yaml
performance:
  # Nombre de threads pour le scan
  scan_threads: 4
  
  # Cache des métadonnées (secondes)
  cache_duration: 3600
```

---

## 🛠️ Dépannage

### L'application ne démarre pas

1. Vérifiez que **Python 3.8+** est installé
2. Vérifiez que **Node.js 16+** est installé
3. Réexécutez `INSTALLER.ps1`

### Les vidéos ne se lisent pas

1. **Installez FFmpeg** (recommandé) :
   - Téléchargez depuis [ffmpeg.org](https://ffmpeg.org/download.html)
   - Ajoutez FFmpeg au PATH Windows

2. **Activez le transcodage** dans les paramètres du lecteur

### Les affiches ne s'affichent pas

1. Vérifiez que votre **clé API TMDb** est correcte
2. Vérifiez votre **connexion Internet**
3. Relancez un scan de la bibliothèque

### Erreur "Port déjà utilisé"

Un autre programme utilise le port 5173 ou 8000 :

```powershell
# Trouver le processus
netstat -ano | findstr :5173

# Arrêter le processus (remplacez XXXX par le PID)
Stop-Process -Id XXXX -Force
```

---

## 🔐 Sécurité et Confidentialité

- **Vos données restent locales** - aucune donnée n'est envoyée à des serveurs tiers
- **Mots de passe chiffrés** avec bcrypt
- **API TMDb** utilisée uniquement pour récupérer les métadonnées publiques
- **Code source ouvert** - vous pouvez l'auditer

---

## 📞 Support

### Documentation

- **README.md** - Installation et configuration
- **CHANGELOG.md** - Historique des versions
- **START_ICI.md** - Guide de démarrage rapide

### Problèmes et Suggestions

Ouvrez un ticket sur le dépôt GitHub ou consultez la documentation complète.

---

## 🎉 Astuces et Conseils

### 💡 Raccourcis Clavier (Lecteur)

- **Espace** - Pause/Lecture
- **←/→** - Reculer/Avancer de 10s
- **↑/↓** - Volume +/-
- **F** - Plein écran
- **M** - Muet
- **C** - Activer/désactiver sous-titres

### 🎯 Organisation Recommandée

```
Mes Vidéos/
├── Films/
│   ├── Film 1 (2020).mp4
│   └── Film 2 (2021).mkv
├── Series/
│   ├── Série 1/
│   │   ├── S01E01.mp4
│   │   └── S01E02.mp4
└── Documentaires/
    └── Doc 1.mp4
```

### 🚀 Performance

- **Nommez vos fichiers correctement** pour une meilleure détection
- **Utilisez des formats modernes** (MP4, MKV)
- **Activez FFmpeg** pour une compatibilité maximale

---

## 📜 Licence

Homeflix est distribué sous licence **MIT**. Voir le fichier `LICENSE` pour plus de détails.

**TMDb** : Ce produit utilise l'API TMDb mais n'est ni approuvé ni certifié par TMDb.

---

**Profitez de Homeflix ! 🎬**
