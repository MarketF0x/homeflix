# 📁 STRUCTURE DU PROJET HOMEFLIX

## Vue d'ensemble

Après installation, l'utilisateur final voit une structure **propre et épurée** :

```
homeflix/
├── 📄 README.md          ← Guide utilisateur simple
├── 📄 INSTALLER.ps1      ← Installation en 1 clic
├── 📄 homeflix.ps1       ← Lancement de l'application
├── 📄 settings.yaml      ← Configuration (dossiers vidéos, etc.)
├── 📄 LICENSE            ← Licence MIT
├── 📄 CHANGELOG.md       ← Historique des versions
│
├── 📁 client/            ← Interface web (React)
├── 📁 server/            ← Backend API (Python)
├── 📁 data/              ← Base de données et médias générés
│
└── 📁 [Dossiers cachés]  ← Fichiers techniques (commencent par .)
```

---

## Fichiers Visibles (Utilisateur Final)

### Fichiers Principaux
- **README.md** - Guide de démarrage rapide et liens vers documentation
- **INSTALLER.ps1** - Script d'installation rapide (appelle `.scripts/install.ps1`)
- **homeflix.ps1** - Script de lancement principal (tout-en-un)
- **settings.yaml** - Configuration de l'application (dossiers vidéos, clé TMDb, etc.)
- **LICENSE** - Licence MIT avec attributions
- **CHANGELOG.md** - Historique des versions et modifications

### Dossiers Principaux
- **client/** - Code source de l'interface web (React + Vite)
- **server/** - Code source du backend (FastAPI Python)
- **data/** - Données de l'application (base SQLite, posters, thumbnails)

### Dossiers Secondaires
- **docs/** - Archive des rapports historiques (docs/archives/)
- **tests/** - Tests unitaires (test_*.py)
- **scripts/** - Scripts de développement divers
- **installer/** - Installateur Windows (Inno Setup)
- **exemple_ui/** - Exemples d'interface
- **netlify-deploy/** - Configuration Netlify

---

## Dossiers Cachés (Techniques)

Ces dossiers commencent par `.` et sont **masqués par défaut** dans l'explorateur Windows.

### `.config/` - Scripts de Configuration

Scripts PowerShell pour configuration avancée :

```
.config/
├── check-dependencies.ps1            ← Vérifier les dépendances système
├── configure-firewall.ps1            ← Configuration du pare-feu Windows
├── configure-firewall-tailscale.ps1  ← Configuration pare-feu pour Tailscale
├── configure-network-access.ps1      ← Configuration accès réseau
├── create_shortcut.ps1               ← Créer un raccourci bureau
├── install-tailscale.ps1             ← Installer Tailscale VPN
├── setup-homeone-domain.ps1          ← Configuration domaine homeone.local
├── setup-https.ps1                   ← Configuration HTTPS
├── setup-multi-domains.ps1           ← Configuration multi-domaines
├── setup-tailscale-dns.ps1           ← Configuration DNS Tailscale
├── setup-tmdb-key.ps1                ← Configuration clé API TMDb (IMPORTANT)
└── update-profiles.ps1               ← Mise à jour des profils utilisateurs
```

### `.scripts/` - Scripts d'Installation et Démarrage

Scripts de développement et installation :

```
.scripts/
├── install.ps1               ← Installation complète (appelé par INSTALLER.ps1)
├── install.sh                ← Installation Linux/Mac
├── start-homeflix.ps1        ← Démarrage avancé (modes dev/production)
├── start-homeone.ps1         ← Démarrage variante HomeOne
├── homeflix.code-workspace   ← Workspace VS Code
├── homeflix_icon.ico         ← Icône Homeflix
└── homeone.ico               ← Icône HomeOne
```

### `.utils/` - Utilitaires Python

Scripts Python pour maintenance et optimisation :

```
.utils/
├── check_and_install_ffmpeg.py   ← Installer FFmpeg automatiquement
├── check_durations.py            ← Vérifier durées des vidéos
├── clean_filenames.py            ← Nettoyer les noms de fichiers
├── compress_background.py        ← Compression en arrière-plan
├── compress_large_videos.py      ← Compresser les vidéos volumineuses
├── compress_one_video.py         ← Compresser une vidéo spécifique
├── create_default_poster.py      ← Créer affiche par défaut
├── extract_durations.py          ← Extraire durées des vidéos
├── generate_icon.py              ← Générer icônes
├── generate_qrcode.py            ← Générer QR codes (accès mobile)
├── generate_thumbnails.py        ← Générer miniatures
└── video_compressor.py           ← Compresseur vidéo générique
```

### `.docs/` - Documentation Technique

Toute la documentation avancée et guides techniques :

```
.docs/
├── GUIDE_DEMARRAGE.md               ← Guide complet de démarrage
├── GUIDE_TMDB_API_KEY.md            ← Obtenir clé API TMDb (étape par étape)
├── GUIDE_PROFILS.md                 ← Gestion des profils utilisateurs
├── GUIDE_SECURITE_PROFILS.md        ← Sécurité et restrictions
├── GUIDE_COMPRESSION.md             ← Compression vidéos
├── GUIDE_PISTES_AUDIO_SOUSTITRES.md ← Multi-pistes audio/sous-titres
├── GUIDE_HOMEONE_DOMAIN.md          ← Configuration domaine local
│
├── ACCES_RESEAU.md                  ← Accès réseau local
├── ACCES_INTERNET.md                ← Accès internet (Tailscale)
├── PARTAGE_RESEAU.md                ← Partage réseau
│
├── TMDB_TERMS_SUMMARY.md            ← Résumé conditions TMDb
├── ANALYSE_LICENCES_COMMERCIAL.md   ← Analyse licences pour usage commercial
├── RESUME_CONFORMITE_LEGALE.md      ← Résumé conformité légale
│
├── FORMAT_VIDEO_COMPATIBILITE.md    ← Formats vidéo compatibles
├── SOLUTION_CODEC_VIDEO.md          ← Solutions codecs
├── SOLUTION_COMPRESSION.md          ← Solutions compression
├── COMPRESSION_MIGRATION.md         ← Migration compression
├── ESPACE_DISQUE.md                 ← Gestion espace disque
├── MASQUAGE_VIDEOS.md               ← Masquer certaines vidéos
│
├── README_MULTI_DOMAINES.md         ← Multi-domaines
├── README_UTILISATION.md            ← Utilisation détaillée
├── INSTALL_RAPIDE.md                ← Installation rapide
├── AUDIT_NETTOYAGE.md               ← Audit du projet
│
└── archives/                        ← Rapports historiques
    ├── RAPPORT_AUDIT_2025.md
    ├── MISE_A_JOUR_NOV_2025.md
    ├── OPTIMISATIONS_APPLIQUEES.md
    ├── OPTIMISATIONS_STREAMING.md
    ├── AMELIORATIONS_STREAMING_v2.md
    ├── HARMONISATION_UI_PROFILS.md
    └── RESTAURATION_DEV.md
```

### Autres Dossiers Cachés

- **.venv/** et **.venv310/** - Environnements virtuels Python
- **.git/** - Historique Git
- **.github/** - Configuration GitHub
- **.vscode/** - Configuration VS Code

---

## Accès aux Fichiers Cachés

### Pour l'Utilisateur Final

**Tout est accessible depuis le README.md** avec des liens directs :
- Configuration TMDb → `.\.config\setup-tmdb-key.ps1`
- Compression → `.\.utils\compress_large_videos.py`
- Documentation → `.docs\GUIDE_*.md`

### Afficher les Dossiers Cachés (Windows)

1. **Explorateur de fichiers** → Affichage → Cocher "Éléments masqués"
2. **PowerShell** : `Get-ChildItem -Force`

---

## Avantages de cette Structure

✅ **Interface Utilisateur Claire**
- Seuls 6 fichiers visibles à la racine
- Tout ce dont l'utilisateur a besoin est accessible facilement

✅ **Organisation Professionnelle**
- Fichiers techniques regroupés par fonction
- Documentation centralisée
- Facile à maintenir

✅ **Installation Simple**
- Double-clic sur `INSTALLER.ps1`
- Puis double-clic sur `homeflix.ps1`

✅ **Évolutivité**
- Facile d'ajouter de nouveaux scripts sans encombrer la racine
- Structure modulaire pour développeurs

✅ **Compatible Déploiement**
- Structure propre pour création d'installateur
- Peut être packagée facilement (Inno Setup, NSIS, etc.)

---

## Modification de la Structure

### Ajouter un Nouveau Script de Configuration

```powershell
# Créer le fichier dans .config/
New-Item -Path ".config\mon-nouveau-script.ps1" -ItemType File

# Référencer dans README.md ou GUIDE correspondant
```

### Ajouter une Nouvelle Documentation

```markdown
<!-- Dans README.md -->
📖 **Mon nouveau guide** : [`.docs/MON_GUIDE.md`](.docs/MON_GUIDE.md)
```

---

**Dernière mise à jour** : 14 novembre 2025  
**Version** : 2.0
