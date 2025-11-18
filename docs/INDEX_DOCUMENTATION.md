# 📚 INDEX DE DOCUMENTATION - HOMEFLIX

**Navigation rapide vers tous les documents de votre projet**

---

## 🎯 DÉMARRAGE RAPIDE

**Nouveau sur Homeflix ? Commencez ici :**

1. 📖 **[LANCEMENT.md](LANCEMENT.md)** - **COMMENCEZ ICI !**
   - Vue d'ensemble de la préparation commerciale
   - Fichiers créés aujourd'hui
   - Prochaines étapes

2. 🚀 **[README.md](README.md)** - Guide principal
   - Installation et configuration
   - Fonctionnalités
   - Utilisation quotidienne

---

## 👥 DOCUMENTATION UTILISATEUR

**Pour vos utilisateurs finaux :**

- 📘 **[GUIDE_UTILISATEUR.md](GUIDE_UTILISATEUR.md)** - Guide complet
  - Installation détaillée
  - Configuration TMDb
  - Utilisation de toutes les fonctionnalités
  - Raccourcis clavier
  - Organisation recommandée

- ❓ **[FAQ.md](FAQ.md)** - Questions fréquentes
  - Problèmes courants
  - Solutions de dépannage
  - Astuces et conseils
  - Support

---

## 🏗️ DOCUMENTATION DÉVELOPPEUR

**Pour créer des builds et développer :**

### Build et Production

- 🏭 **[BUILD_PRODUCTION.md](BUILD_PRODUCTION.md)** - Guide de build
  - Créer un build de production
  - Checklist avant distribution
  - Optimisations avancées
  - Vérification du build
  - Versioning

- 📦 **[create-release.ps1](create-release.ps1)** - Script de release
  - Créer automatiquement une archive de distribution
  - Génération de checksum SHA256
  - Statistiques de build

- ✅ **[validate-build.py](validate-build.py)** - Validation
  - Vérifier que le build est prêt
  - Détecter les problèmes
  - Validation de sécurité

### Configuration

- ⚙️ **[.env.production](.env.production)** - Environnement production
  - Variables d'environnement
  - Configuration sécurisée

- 🚫 **[.distignore](.distignore)** - Fichiers exclus
  - Liste des fichiers de dev à exclure
  - Build propre

---

## 💼 DOCUMENTATION COMMERCIALE

**Pour la commercialisation et le lancement :**

### Vue d'Ensemble

- 🎯 **[RESUME_COMMERCIALISATION.md](RESUME_COMMERCIALISATION.md)** - Résumé exécutif
  - Score de préparation (95%)
  - État global
  - Recommandations
  - Processus de release
  - Modèle commercial

- ✅ **[CHECKLIST_COMMERCIALISATION.md](CHECKLIST_COMMERCIALISATION.md)** - Checklist détaillée
  - Toutes les tâches à accomplir
  - État d'avancement
  - Actions prioritaires
  - Validation finale

### Modifications

- 📋 **[PREPARATION_COMMERCIALISATION.md](PREPARATION_COMMERCIALISATION.md)** - Modifications effectuées
  - Fichiers créés
  - Fichiers modifiés
  - Détail des changements
  - Guide de release

---

## 📜 DOCUMENTATION LÉGALE

- ⚖️ **[LICENSE](LICENSE)** - Licence MIT
  - Termes de la licence
  - Copyright 2025
  - Attributions tierces (TMDb, FFmpeg)
  - Dépendances

---

## 📝 HISTORIQUE ET VERSIONS

- 📅 **[CHANGELOG.md](CHANGELOG.md)** - Historique des versions
  - Notes de version
  - Nouvelles fonctionnalités
  - Corrections de bugs
  - Améliorations

---

## 🔧 CONFIGURATION ET SCRIPTS

### Scripts PowerShell

- 🏃 **[homeflix.ps1](homeflix.ps1)** - Lancer l'application
  - Démarrage normal
  - Serveur + Client

- 📥 **[INSTALLER.ps1](INSTALLER.ps1)** - Installation
  - Installation automatique
  - Détection des prérequis
  - Mode réparation

- 🗑️ **[DESINSTALLER.ps1](DESINSTALLER.ps1)** - Désinstallation
  - Suppression propre
  - Option de conservation des données
  - Nettoyage complet

- 🚀 **[homeflix-dev.ps1](homeflix-dev.ps1)** - Mode développement
  - Développement local
  - Hot-reload activé

### Configuration

- ⚙️ **[settings.yaml](settings.yaml)** - Configuration principale
  - Clé API TMDb
  - Dossiers vidéos
  - Préférences vidéo
  - Configuration serveur

- 📦 **[package.json](package.json)** - Métadonnées du projet
  - Version (1.0.0)
  - Scripts NPM
  - Dépendances

---

## 🎨 CODE SOURCE

### Frontend (Client)

```
client/
├── src/                    # Code source React
│   ├── App.jsx            # Composant principal
│   ├── VideoPlayer.jsx    # Lecteur vidéo
│   ├── CollectionsView.jsx # Gestion collections
│   └── ...
├── public/                # Assets publics
├── vite.config.js        # Configuration Vite (OPTIMISÉ)
└── package.json          # Dépendances frontend
```

### Backend (Serveur)

```
server/
├── main.py               # Point d'entrée FastAPI
├── api/                  # Routes API
│   ├── videos.py        # Gestion vidéos
│   ├── collections.py   # Gestion collections
│   └── profiles.py      # Gestion profils
├── core/                # Logique métier
│   ├── scanner.py       # Scanner de vidéos
│   ├── tmdb.py         # Intégration TMDb
│   └── player.py       # Lecteur backend
└── requirements.txt    # Dépendances Python
```

### Electron

```
electron/
├── main.js             # Process principal Electron
├── preload.js         # Script de préchargement
└── package.json       # Config Electron
```

---

## 📊 AUDITS ET RAPPORTS

**Documents d'analyse technique (archives) :**

- 📄 `AUDIT_COMPLET_PROFESSIONNEL_NOV2025.md`
- 📄 `CORRECTIFS_COLLECTION_MODAL_NOV2025.md`
- 📄 `CORRECTIFS_LECTEUR_VIDEO_NOV2025.md`
- 📄 `OPTIMISATIONS_LECTEUR_NOV2025.md`
- 📄 `NETTOYAGE_NOV2025.md`

*Ces documents sont conservés pour historique mais ne sont pas nécessaires pour la commercialisation.*

---

## 🎯 GUIDES PAR OBJECTIF

### Je veux installer Homeflix

1. **[README.md](README.md)** → Section "Installation Rapide"
2. **[GUIDE_UTILISATEUR.md](GUIDE_UTILISATEUR.md)** → "Installation"

### Je veux utiliser Homeflix

1. **[GUIDE_UTILISATEUR.md](GUIDE_UTILISATEUR.md)** → Guide complet
2. **[FAQ.md](FAQ.md)** → Solutions aux problèmes

### Je veux développer/modifier Homeflix

1. **[README.md](README.md)** → Section "Pour les Développeurs"
2. **[BUILD_PRODUCTION.md](BUILD_PRODUCTION.md)** → Process de build

### Je veux créer une release

1. **[LANCEMENT.md](LANCEMENT.md)** → "Comment Créer Votre Première Release"
2. **[BUILD_PRODUCTION.md](BUILD_PRODUCTION.md)** → "Distribution"
3. **[create-release.ps1](create-release.ps1)** → Exécuter le script

### Je veux commercialiser Homeflix

1. **[LANCEMENT.md](LANCEMENT.md)** → Vue d'ensemble
2. **[RESUME_COMMERCIALISATION.md](RESUME_COMMERCIALISATION.md)** → Résumé exécutif
3. **[CHECKLIST_COMMERCIALISATION.md](CHECKLIST_COMMERCIALISATION.md)** → Tâches à faire

### J'ai un problème

1. **[FAQ.md](FAQ.md)** → Questions fréquentes
2. **[GUIDE_UTILISATEUR.md](GUIDE_UTILISATEUR.md)** → "Dépannage"
3. **GitHub Issues** → Créer un ticket

---

## 🌟 FICHIERS IMPORTANTS PAR PRIORITÉ

### 🔥 Essentiels (À lire absolument)

1. **[LANCEMENT.md](LANCEMENT.md)** - Démarrez ici !
2. **[README.md](README.md)** - Guide principal
3. **[GUIDE_UTILISATEUR.md](GUIDE_UTILISATEUR.md)** - Pour utilisateurs
4. **[LICENSE](LICENSE)** - Termes légaux

### ⭐ Très Importants

5. **[BUILD_PRODUCTION.md](BUILD_PRODUCTION.md)** - Créer des releases
6. **[FAQ.md](FAQ.md)** - Support utilisateurs
7. **[CHECKLIST_COMMERCIALISATION.md](CHECKLIST_COMMERCIALISATION.md)** - Suivi

### 📌 Utiles

8. **[RESUME_COMMERCIALISATION.md](RESUME_COMMERCIALISATION.md)** - Vue stratégique
9. **[PREPARATION_COMMERCIALISATION.md](PREPARATION_COMMERCIALISATION.md)** - Détails techniques
10. **[CHANGELOG.md](CHANGELOG.md)** - Historique

---

## 🔍 RECHERCHE RAPIDE

**Vous cherchez :**

- **Installation** → README.md, GUIDE_UTILISATEUR.md
- **Configuration TMDb** → GUIDE_UTILISATEUR.md, FAQ.md
- **Problèmes vidéo** → FAQ.md ("Lecteur Vidéo")
- **Créer release** → LANCEMENT.md, BUILD_PRODUCTION.md
- **État du projet** → LANCEMENT.md, RESUME_COMMERCIALISATION.md
- **Licence** → LICENSE
- **Build production** → BUILD_PRODUCTION.md, create-release.ps1
- **Validation** → validate-build.py, CHECKLIST_COMMERCIALISATION.md

---

## 📞 LIENS EXTERNES

- **Repository GitHub** : [github.com/MarketF0x/homeflix](https://github.com/MarketF0x/homeflix)
- **TMDb API** : [themoviedb.org/documentation/api](https://www.themoviedb.org/documentation/api)
- **FFmpeg** : [ffmpeg.org](https://ffmpeg.org)
- **Python** : [python.org](https://www.python.org)
- **Node.js** : [nodejs.org](https://nodejs.org)

---

**Navigation simplifiée pour tous vos besoins ! 🧭**

*Dernière mise à jour : 18 novembre 2025*
