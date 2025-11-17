# 🎬 Homeflix

Serveur de streaming personnel pour vos vidéos avec interface web moderne.

## 🚀 Démarrage Rapide

### Première Installation

```powershell
.\install.ps1
```

**Important** : Après l'installation, configurez votre clé API TMDb :
```powershell
.\setup-tmdb-key.ps1
```

📚 **Guide complet** : [GUIDE_TMDB_API_KEY.md](GUIDE_TMDB_API_KEY.md)

### Lancer l'Application

```powershell
.\start-homeflix.ps1 -Mode production
```

L'application démarre en arrière-plan (aucune fenêtre visible) :
- **Interface Web** : http://localhost:5173
- **API Backend** : http://localhost:8000

## ⚖️ Licence et Usage Commercial

Homeflix est distribué sous **licence MIT** - libre d'utilisation, y compris commerciale.

**Cependant** : L'API TMDb a des restrictions pour l'usage commercial.

- ✅ **Usage Personnel/Gratuit** → Clé API gratuite
- ⚠️ **Usage Commercial** → Licence commerciale TMDb requise

📄 **Détails** : [TMDB_TERMS_SUMMARY.md](TMDB_TERMS_SUMMARY.md) et [ANALYSE_LICENCES_COMMERCIAL.md](ANALYSE_LICENCES_COMMERCIAL.md)

## 📋 Fonctionnalités

- ✅ **Streaming Vidéo** : Lecture directe ou transcodage automatique
- ✅ **Métadonnées Enrichies** : Récupération automatique via TMDb
- ✅ **Thumbnails** : Génération automatique de vignettes
- ✅ **Multi-pistes Audio/Sous-titres** : Sélection facile dans le lecteur
- ✅ **Compression** : Option de compression pour les gros fichiers
- ✅ **Nettoyage Auto** : Suppression des tags techniques dans les titres
- ✅ **Recherche** : Par titre, genre, année, réalisateur
- ✅ **Interface Moderne** : React + Vite avec fond WebGL
- ✅ **👥 Gestion des Profils** : Profils utilisateurs avec avatars personnalisés et restrictions

## 👥 Nouveauté : Gestion des Profils

Homeflix intègre désormais un système complet de gestion des profils :
- **Profil Principal** automatique avec tous les droits
- **Profils Secondaires** personnalisables (nom, avatar, restrictions)
- **12 Avatars** au choix (personnages et formes abstraites)
- **Restrictions** : Mode enfants, masquage contenu adulte
- **Interface Intuitive** : Sélection au démarrage, changement rapide

📖 **Guide détaillé** : Consultez [GUIDE_PROFILS.md](GUIDE_PROFILS.md)

## 🛠️ Configuration

### Ajouter vos Vidéos

1. Modifier `settings.yaml` :
```yaml
video_folders:
  - "C:\\Mes\\Videos"
  - "D:\\Films"
```

2. Redémarrer l'application

### Activer TMDb (Recommandé)

1. Obtenir une clé API sur https://www.themoviedb.org/settings/api
2. Modifier `settings.yaml` :
```yaml
tmdb_api_key: "votre_clé_api"
```

## 📁 Structure du Projet

```
homeflix/
├── server/          # Backend FastAPI (Python)
│   ├── main.py      # Point d'entrée
│   ├── api/         # Routes API
│   └── core/        # Logique métier
├── client/          # Frontend React + Vite
│   └── src/         # Composants React
├── data/            # Base de données SQLite
└── settings.yaml    # Configuration
```

## 🔧 Scripts Utiles

### Compression Manuelle

```powershell
python compress_one_video.py "chemin/vers/video.mkv"
```

### Compression de Masse

```powershell
python compress_background.py
```

### Nettoyage des Noms de Fichiers

```powershell
python clean_filenames.py
```

## 🌐 Accès Réseau

### Local (même ordinateur)
- http://localhost:5173

### Réseau Local (autres appareils)
- http://[votre-ip]:5173
- Exemple : http://192.168.1.5:5173

### Internet (avec Tailscale)
```powershell
.\install-tailscale.ps1
```

## ⚙️ Technologies

- **Backend** : Python 3.10, FastAPI, Uvicorn, SQLite
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
