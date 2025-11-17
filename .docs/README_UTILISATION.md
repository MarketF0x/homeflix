# 🎬 HomeFlix - Guide d'utilisation

## 📋 Table des matières
1. [Démarrage rapide](#démarrage-rapide)
2. [Scripts disponibles](#scripts-disponibles)
3. [Configuration](#configuration)
4. [Architecture du projet](#architecture-du-projet)
5. [Dépannage](#dépannage)

---

## 🚀 Démarrage rapide

### Prérequis
- Python 3.10+ avec environnement virtuel `.venv310`
- Node.js 16+ et npm
- FFmpeg (optionnel, pour les miniatures)

### Lancement
```powershell
# Méthode recommandée (production)
.\start.ps1

# Mode développement
.\start-dev.ps1
```

L'application sera accessible sur :
- **Frontend** : http://localhost:5173
- **Backend API** : http://localhost:8000

---

## 📜 Scripts disponibles

### Scripts principaux

| Script | Description | Usage recommandé |
|--------|-------------|------------------|
| `start.ps1` | ⭐ **RECOMMANDÉ** - Démarrage robuste avec gestion des ports | Production |
| `start-dev.ps1` | Mode développement avec rechargement automatique | Développement |

### Scripts obsolètes (conservés pour compatibilité)
- `start-simple.ps1` - Remplacé par `start.ps1`
- `start-servers.ps1` - Remplacé par `start.ps1`
- `start-optimized.bat` - Remplacé par `start.ps1`

### Scripts utilitaires

| Script | Description |
|--------|-------------|
| `install.ps1` | Installation complète du projet |
| `check_and_install_ffmpeg.py` | Vérification et installation de FFmpeg |
| `generate_qrcode.py` | Génération d'un QR code pour accès réseau |
| `clean_filenames.py` | Nettoyage manuel des noms de fichiers |

---

## ⚙️ Configuration

### Fichier `settings.yaml` (racine du projet)

```yaml
# Répertoires à scanner
video_directories:
  - "C:/Users/NomUtilisateur/Videos"
  - "D:/Films"

# Durées pour filtrage films/séries
min_film_minutes: 75      # >= 1h15 = film
max_series_minutes: 55    # entre 20 et 55 min = série

# Mode par défaut (mixed | films | series)
session_mode: mixed

# Clé API TMDb (gratuite sur themoviedb.org)
tmdb_api_key: "VOTRE_CLE_API_ICI"

# Nettoyage automatique des noms
auto_clean_filenames: true

# Langue de l'interface
language: fr
```

### Obtenir une clé API TMDb
1. Créez un compte sur https://www.themoviedb.org/
2. Allez dans Paramètres > API
3. Demandez une clé API (gratuite)
4. Copiez la clé dans `settings.yaml`

---

## 🏗️ Architecture du projet

```
homeflix/
├── client/                  # Frontend React + Vite
│   ├── src/
│   │   ├── App.jsx         # Composant principal
│   │   ├── api.js          # Connexion API
│   │   └── components/     # Composants UI
│   └── package.json
│
├── server/                  # Backend FastAPI
│   ├── main.py             # Point d'entrée
│   ├── core/               # Logique métier
│   │   ├── scanner.py      # Scan des vidéos
│   │   ├── metadata_enricher.py  # Enrichissement TMDb
│   │   ├── thumbnails.py   # Génération miniatures
│   │   ├── title_utils.py  # ⭐ Utilitaires partagés
│   │   └── config_manager.py
│   ├── api/                # Routes API
│   └── requirements.txt
│
├── settings.yaml           # ⭐ Configuration principale
├── start.ps1               # ⭐ Script de démarrage recommandé
├── start-dev.ps1           # Script développement
└── README_UTILISATION.md   # Ce fichier
```

### Fichiers importants

| Fichier | Rôle |
|---------|------|
| `settings.yaml` | **Configuration unique** (racine du projet) |
| `server/core/title_utils.py` | **Utilitaires partagés** pour nettoyage des titres |
| `server/core/config_manager.py` | Chargement de la configuration |
| `client/src/api.js` | Configuration de l'URL de l'API |

---

## 🔧 Dépannage

### Problème : Port 5173 ou 8000 occupé
**Solution** : `start.ps1` libère automatiquement les ports. Si le problème persiste :
```powershell
# Trouver le processus occupant le port
Get-NetTCPConnection -LocalPort 5173 | Select-Object OwningProcess
# Tuer le processus (remplacer XXXX par l'ID)
Stop-Process -Id XXXX -Force
```

### Problème : Miniatures manquantes
1. Vérifiez que FFmpeg est installé :
   ```powershell
   python check_and_install_ffmpeg.py
   ```
2. Vérifiez votre clé API TMDb dans `settings.yaml`
3. Relancez le scan depuis l'interface web

### Problème : Vidéos non détectées
1. Vérifiez les chemins dans `settings.yaml`
2. Les formats supportés : `.mp4`, `.mkv`, `.avi`, `.mov`, `.wmv`, `.flv`, `.webm`
3. Relancez un scan manuel depuis l'interface

### Problème : Erreur "settings.yaml not found"
**Cause** : Le fichier doit être à la racine du projet (pas dans `/server/`)
**Solution** : Vérifiez que `c:\Users\fparo\Desktop\homeflix\settings.yaml` existe

### Logs et diagnostic
- Les logs backend s'affichent dans le terminal qui exécute le serveur
- Les logs frontend s'affichent dans la console du navigateur (F12)
- Utilisez `.\scripts\cleanup-dev.ps1` pour nettoyer les processus résiduels

---

## 🌐 Accès réseau

Pour accéder à HomeFlix depuis un autre appareil sur votre réseau :

1. Générez un QR code avec votre IP :
   ```powershell
   python generate_qrcode.py
   ```

2. Ou trouvez votre IP manuellement :
   ```powershell
   ipconfig
   # Cherchez "Adresse IPv4" (ex: 192.168.1.10)
   ```

3. Accédez depuis un autre appareil :
   ```
   http://192.168.1.10:5173
   ```

4. Consultez `ACCES_RESEAU.md` pour configurer le pare-feu Windows

---

## 📝 Notes importantes

### ⚠️ Fichiers à NE PAS modifier
- Ne créez PAS de `/server/settings.yaml` (utilisez celui de la racine)
- Ne créez PAS de fichiers `.code-workspace` dans `/client/src/`

### ✅ Bonnes pratiques
- Utilisez toujours `start.ps1` pour démarrer en production
- Mettez à jour les dépendances régulièrement :
  ```powershell
  cd client
  npm update
  
  cd ../server
  .\..\venv310\Scripts\activate
  pip install --upgrade -r requirements.txt
  ```

### 🔄 Mise à jour du scan automatique
Le serveur scanne automatiquement les dossiers **toutes les 10 minutes** pour détecter :
- Nouvelles vidéos ajoutées
- Vidéos supprimées
- Nettoyage automatique des noms (si activé)

---

## 📚 Documentation complémentaire

- `AMELIORATIONS_STREAMING.md` - Optimisations du streaming vidéo
- `DIAGNOSTIC_VIDEOS.md` - Diagnostic des problèmes de lecture
- `ACCES_RESEAU.md` - Configuration réseau avancée
- `PARTAGE_RESEAU.md` - Partage sur le réseau local

---

**Version du document** : 1.0  
**Dernière mise à jour** : 11 novembre 2025
