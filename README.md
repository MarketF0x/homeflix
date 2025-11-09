# 🎬 HomeOne - Gestionnaire de bibliothèque vidéo personnel

HomeOne est une application moderne de gestion de bibliothèque vidéo avec interface web style Netflix, développée avec FastAPI (backend) et React (frontend).

## ✨ Fonctionnalités

- 📁 **Scan automatique** des dossiers vidéo avec nettoyage intelligent des noms de fichiers
- 🎨 **Interface Netflix-style** avec carrousel et catégories
- 🖼️ **Miniatures automatiques** via TMDb API et FFmpeg
- 🔍 **Filtrage avancé** : films/séries, par année, par genre
- ⏸️ **Reprise de lecture** et suivi des vidéos vues
- 🚀 **Scan automatique** toutes les 10 minutes en arrière-plan
- 🎯 **Lecture directe** via le lecteur vidéo par défaut du système
- 🧹 **Nettoyage intelligent** des noms de fichiers pour améliorer la reconnaissance TMDB

## 🏗️ Architecture

```
homeflix/
├── client/              # Frontend React + Vite
│   ├── src/
│   │   ├── App.jsx             # Composant principal
│   │   ├── Carousel.jsx        # Carrousel d'en-tête
│   │   ├── CategoryRow.jsx     # Rangées de catégories
│   │   ├── VideoCard.jsx       # Cartes vidéo
│   │   └── VideoDetail.jsx     # Modal détails vidéo
│   └── package.json
│
├── server/              # Backend FastAPI
│   ├── core/
│   │   ├── config_manager.py   # Gestion settings.yaml
│   │   ├── db.py               # Configuration SQLAlchemy
│   │   ├── models.py           # Modèles de données
│   │   ├── scanner.py          # Scanner de fichiers vidéo
│   │   ├── thumbnails.py       # Génération miniatures
│   │   └── player.py           # Ouverture lecteur vidéo
│   ├── main.py                 # API REST FastAPI
│   └── requirements.txt
│
├── data/                # Base de données SQLite + miniatures
│   ├── homeone.db
│   └── thumbs/
│
├── settings.yaml        # Configuration utilisateur
├── launch_homeone.ps1   # Lanceur principal (backend + frontend)
├── launch_homeone_silent.vbs  # Lanceur silencieux
└── create_shortcut.ps1  # Création raccourci Bureau
```

## 🚀 Installation rapide

### Prérequis

- **Python 3.10+** avec pip
- **Node.js 18+** avec npm
- **FFmpeg** (optionnel, pour génération miniatures locales)

### Installation automatique

**Windows :**
```powershell
.\install.ps1
```

**Linux/macOS :**
```bash
chmod +x install.sh
./install.sh
```

## 🎮 Utilisation

### Démarrage rapide

**Windows :**
```powershell
.\start-dev.ps1
```

**Linux/macOS :**
```bash
./start.sh
```

L'application s'ouvre automatiquement sur `http://localhost:5173`

### Configuration

Éditez `settings.yaml` pour personnaliser :

```yaml
video_directories:
  - "C:/Users/VotreNom/Videos"
  - "D:/Films"

min_film_minutes: 75
max_series_minutes: 55
session_mode: mixed  # mixed, films, ou series

tmdb_api_key: "votre_cle_api"  # Optionnel - https://www.themoviedb.org/
auto_clean_filenames: true     # Nettoyage automatique des noms de fichiers
```

## 🧹 Nettoyage des fichiers

Pour améliorer la reconnaissance TMDB, vous pouvez nettoyer les noms de fichiers :

```powershell
# Aperçu des changements
python clean_filenames.py --preview

# Simulation complète
python clean_filenames.py --dry-run

# Exécution réelle (renomme les fichiers)
python clean_filenames.py --execute
```

## 🖼️ Génération de miniatures

Les miniatures sont générées automatiquement via :
1. TMDb API (si clé configurée)
2. FFmpeg (extraction locale si installé)

Pour forcer la régénération :
```powershell
python generate_thumbnails.py
```

### Lancement via raccourci (recommandé)
Double-cliquez sur le raccourci **HomeOne** créé sur votre Bureau.

### Lancement manuel

**Option 1 : Lanceur automatique (backend + frontend)**
```powershell
powershell -ExecutionPolicy Bypass -File launch_homeone.ps1
```

**Option 2 : Lancement séparé**

Terminal 1 - Backend :
```powershell
cd server
python main.py
# ou
uvicorn main:app --reload
```

Terminal 2 - Frontend :
```powershell
cd client
npm run dev
```

Ouvrez votre navigateur sur **http://localhost:5173**

## 🛠️ API REST

### Endpoints principaux

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/api/videos` | Liste toutes les vidéos (filtrable par mode) |
| `GET` | `/api/categories` | Vidéos organisées par catégories |
| `GET` | `/api/random` | Retourne une vidéo aléatoire |
| `POST` | `/api/scan` | Lance un scan complet des dossiers |
| `POST` | `/api/open` | Ouvre une vidéo dans le lecteur |
| `GET` | `/api/thumbnail?path=...` | Récupère la miniature d'une vidéo |
| `POST` | `/api/thumbnails/generate` | Génère toutes les miniatures |
| `POST` | `/api/thumbnails/repair` | Régénère les miniatures manquantes |
| `POST` | `/api/video/update` | Met à jour les métadonnées |
| `GET` | `/api/settings` | Récupère la configuration |
| `POST` | `/api/settings` | Met à jour la configuration |

## ⚙️ Configuration

### Paramètres `settings.yaml`

```yaml
# Dossiers à scanner
video_directories:
  - "C:/Users/VotreNom/Videos"
  - "D:/Films"

# Durée minimale pour considérer comme film (minutes)
min_film_minutes: 75

# Durée maximale pour considérer comme série (minutes)
max_series_minutes: 55

# Mode par défaut : mixed, films, series
session_mode: mixed

# Langue de l'interface
language: fr

# Nettoyage automatique des noms de fichiers
auto_clean_filenames: true

# Clé API TMDb (optionnel mais recommandé)
# Obtenez-la gratuitement sur https://www.themoviedb.org/settings/api
tmdb_api_key: "votre_cle_api"
```

### Scan automatique

Le backend scanne automatiquement les dossiers **toutes les 10 minutes** en arrière-plan.

### Formats vidéo supportés

`.mp4`, `.mkv`, `.avi`, `.mov`, `.wmv`, `.flv`, `.webm`

## 🎨 Personnalisation

### Changer l'icône
Éditez `generate_icon.py` puis exécutez :
```powershell
python generate_icon.py
```

### Modifier l'interface
- **Frontend** : Éditez les fichiers dans `client/src/`
- **Styles** : Modifiez `client/src/App.css` et `client/src/styles.css`

## 🐛 Dépannage

### Le scan ne trouve pas mes vidéos

- Vérifiez les chemins dans `settings.yaml` (utilisez `/` au lieu de `\`)
- Assurez-vous que les formats sont supportés
- Vérifiez les permissions sur les dossiers

### Les miniatures ne s'affichent pas

1. Vérifiez que FFmpeg est installé : `ffmpeg -version`
2. Ajoutez une clé TMDb API dans `settings.yaml`
3. Lancez manuellement : `python generate_thumbnails.py`

### Erreur "Module not found"

```powershell
# Backend
cd server
pip install -r requirements.txt

# Frontend
cd client
npm install
```

### Le lecteur ne s'ouvre pas

L'application utilise le lecteur par défaut du système.

## 📊 Base de données

**Emplacement** : `data/homeone.db` (SQLite)

**Schéma Video** :

```sql
- id (INTEGER PRIMARY KEY)
- path (TEXT UNIQUE)
- title (TEXT)
- duration_seconds (INTEGER)
- size (BIGINT)
- year (INTEGER)
- genre (TEXT)
- watched (BOOLEAN)
- last_position (INTEGER)
- created_at (DATETIME)
- updated_at (DATETIME)
```

## 🔐 Sécurité

⚠️ **Attention** : Cette application est conçue pour un usage **local uniquement**.

- Aucune authentification n'est implémentée
- N'exposez pas le port 8000 sur Internet
- Les clés API sont stockées en clair dans `settings.yaml`

## 📝 Licence

MIT License - Libre d'utilisation et de modification

1. Fork le projet
2. Créez une branche (`git checkout -b feature/amelioration`)
3. Committez vos changements (`git commit -am 'Ajout fonctionnalité'`)
4. Push vers la branche (`git push origin feature/amelioration`)
5. Ouvrez une Pull Request

## 📜 Licence

Projet personnel

## 🙏 Remerciements

- **FastAPI** - Framework web moderne
- **React** - Interface utilisateur réactive
- **TMDb** - Base de données de films
- **FFmpeg** - Traitement vidéo

---

**Version** : 2.4  
**Dernière mise à jour** : Novembre 2024  
**Auteur** : fparo
