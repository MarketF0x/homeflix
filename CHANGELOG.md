# 📋 Changelog HomeFlix

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/lang/fr/).

---

## [Non publié]

### À venir
- Système de mise à jour automatique intégré
- Synchronisation cloud optionnelle
- Application mobile iOS/Android
- Historique de visionnage par profil

---

## [1.1.1] - 2025-11-15

### 🔐 Améliorations de Sécurité

#### Ajouté
- **🔒 Protection par mot de passe**
  - Mot de passe pour le profil principal
  - Hachage SHA-256 pour stockage sécurisé
  - Indicateur visuel 🔒 sur les profils protégés
  - Validation au moment de la sélection du profil
  
- **🔑 Récupération de mot de passe**
  - Système de question secrète
  - Réinitialisation sécurisée via question/réponse
  - Hash SHA-256 pour les réponses secrètes
  - Interface intuitive "Mot de passe oublié"
  
- **📋 Nouvelle interface de gestion**
  - Vue liste de tous les profils
  - Bouton "Gérer les profils" séparé
  - Actions modifier/supprimer depuis la liste
  - Mode création/édition distinct

#### Modifié
- **Backend**
  - Nouvelles colonnes : `password_hash`, `security_question`, `security_answer`
  - API : `POST /api/profiles/verify-password`
  - API : `POST /api/profiles/reset-password`
  - Migration automatique pour installations existantes
  
- **Frontend**
  - `ProfileSelector` : retrait des icônes de modification depuis les vignettes
  - `ProfileManager` : ajout de la vue liste avec actions
  - `PasswordPrompt` : nouveau composant pour saisie sécurisée
  - Amélioration de l'UX avec états de chargement
  
- **Sécurité**
  - Mot de passe par défaut "0" pour développement
  - Recommandation forte de changement au premier usage
  - Aucun stockage en clair des données sensibles

#### Documentation
- **Nouveau guide** : `GUIDE_SECURITE_PROFILS.md`
  - Procédures de configuration
  - Bonnes pratiques de sécurité
  - Dépannage et récupération
  - Réinitialisation manuelle

---

## [1.1.0] - 2025-11-14

### 🎉 Nouvelle fonctionnalité : Gestion des Profils

#### Ajouté
- **👥 Système de profils utilisateurs**
  - Profil principal avec tous les droits
  - Création de profils secondaires illimitée
  - Nom personnalisable (max 20 caractères)
  
- **🎨 Avatars personnalisés**
  - 6 avatars personnages (bleu, rose, vert, orange, violet, cyan)
  - 6 avatars abstraits (formes géométriques)
  - Format SVG vectoriel pour qualité optimale
  
- **🔒 Restrictions par profil**
  - Mode enfants (contenu tout public uniquement)
  - Masquage du contenu adulte
  - Interface simplifiée pour profils restreints
  
- **🔄 Gestion intuitive**
  - Écran de sélection au démarrage
  - Modification/suppression de profils
  - Changement de profil à la volée
  - Bouton de profil dans le header

#### Modifié
- **Backend**
  - Nouvelle API REST `/api/profiles` (GET, POST, PUT, DELETE)
  - Migration automatique de la base de données
  - Table `profiles` avec gestion des restrictions
  
- **Frontend**
  - Nouveaux composants `ProfileSelector.jsx` et `ProfileManager.jsx`
  - Intégration dans `App.jsx` avec état de profil
  - Styles CSS complets pour l'interface des profils

- **Scripts de démarrage**
  - Migration automatique au lancement
  - Vérification de l'intégrité des avatars
  - Script de mise à jour `update-profiles.ps1`

#### Documentation
- Nouveau guide complet `GUIDE_PROFILS.md`
- Mise à jour du `README.md` avec section profils
- Instructions de migration pour utilisateurs existants

---

## [1.0.0] - 2025-11-14

### 🎉 Première version publique

#### Ajouté
- **Interface web moderne** avec React 19 et Vite
- **Backend Python** avec FastAPI et SQLite
- **Scan automatique** des dossiers vidéo
- **Détection automatique** films vs séries (basé sur la durée)
- **Intégration TMDb** pour métadonnées et affiches
- **Détection de collections** (sagas de films)
- **Reprise de lecture** - mémorisation de la position
- **Marquage vidéos vues** - historique de visionnage
- **Recherche** par titre, année, genre
- **Filtres avancés** :
  - Par année (carousel des années)
  - Par genre
  - Collections et sagas
  - Vidéos vues
  - Vidéos à reprendre
- **Lecteur vidéo intégré** avec :
  - Barre de progression
  - Contrôles tactiles/souris
  - Gestion des sous-titres
  - Pistes audio multiples
  - Plein écran
- **Générateur de miniatures** avec FFmpeg
- **QR Code** pour accès mobile rapide
- **Support multi-langues** : Français, Anglais, Espagnol
- **Installateur Windows** professionnel avec :
  - Détection automatique des dépendances
  - Installation silencieuse Python/Node.js/FFmpeg
  - Configuration pare-feu automatique
  - Scan de dossiers vidéo auto
  - Interface multi-langue
  - Création de raccourcis
  - Désinstallation propre

#### Technique
- **Stack Frontend** : React 19, Vite, Three.js
- **Stack Backend** : Python 3.10+, FastAPI, SQLite
- **Streaming** : Optimisé avec range requests HTTP
- **Cache** : Système de cache pour les métadonnées
- **Base de données** : SQLite avec index optimisés
- **Logs** : Système de logging rotatif
- **Scripts** : PowerShell pour Windows, Bash pour Linux

#### Documentation
- Guide d'installation rapide
- Guide de démarrage
- Documentation API
- Guide de build de l'installateur
- Guide utilisateur complet
- FAQ et dépannage

---

## [0.9.0-beta] - 2025-11-10

### Beta test interne

#### Ajouté
- Première version fonctionnelle
- Interface basique React
- Backend FastAPI
- Scan de vidéos
- Intégration TMDb de base

#### Problèmes connus
- Pas de gestion des collections
- Interface à améliorer
- Pas d'installateur

---

## [0.5.0-alpha] - 2025-11-01

### Prototype initial

#### Ajouté
- Proof of concept
- Scan basique de fichiers
- Lecteur vidéo simple

---

## Types de changements

- **Ajouté** pour les nouvelles fonctionnalités
- **Modifié** pour les changements dans les fonctionnalités existantes
- **Déprécié** pour les fonctionnalités qui seront bientôt supprimées
- **Supprimé** pour les fonctionnalités supprimées
- **Corrigé** pour les corrections de bugs
- **Sécurité** en cas de vulnérabilités

---

## Politique de versioning

HomeFlix suit le [Semantic Versioning](https://semver.org/lang/fr/) :

- **MAJOR** (1.x.x) : Changements incompatibles de l'API
- **MINOR** (x.1.x) : Ajout de fonctionnalités rétro-compatibles
- **PATCH** (x.x.1) : Corrections de bugs rétro-compatibles

Exemples :
- `1.0.0` → `1.0.1` : Correction de bug
- `1.0.0` → `1.1.0` : Nouvelle fonctionnalité
- `1.0.0` → `2.0.0` : Changement majeur (breaking change)

---

## Liens

- [Code source](https://github.com/homeflix)
- [Issues](https://github.com/homeflix/issues)
- [Releases](https://github.com/homeflix/releases)
- [Documentation](https://github.com/homeflix/wiki)
