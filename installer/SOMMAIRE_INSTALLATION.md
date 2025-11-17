# 🎯 HomeFlix - Package d'Installation Complet

## ✅ Ce qui a été créé

### 📁 Structure du dossier `installer/`

```
installer/
├── 📝 homeflix.iss                    ← Script InnoSetup principal
├── 🔨 build-installer.ps1              ← Script pour compiler l'installateur
├── 🔍 detect-environment.ps1           ← Détection Python/Node/FFmpeg/dossiers vidéo
├── 📦 install-dependencies.ps1         ← Installation des packages pip/npm
├── ⚙️  configure-system.ps1            ← Configuration DB/pare-feu/dossiers
├── 📚 BUILD_GUIDE.md                   ← Guide complet de build
├── 📖 README_USER.md                   ← Guide utilisateur (après installation)
├── 🆕 version.ini                      ← Version (auto-généré par build)
└── locales/
    ├── 🇫🇷 fr.json                     ← Traductions françaises
    ├── 🇬🇧 en.json                     ← Traductions anglaises
    ├── 🇪🇸 es.json                     ← Traductions espagnoles
    ├── LICENSE.fr.txt                  ← Licence FR (auto-généré)
    ├── LICENSE.en.txt                  ← Licence EN (auto-généré)
    ├── LICENSE.es.txt                  ← Licence ES (auto-généré)
    ├── README.fr.txt                   ← README install FR (auto-généré)
    ├── README.en.txt                   ← README install EN (auto-généré)
    └── README.es.txt                   ← README install ES (auto-généré)
```

### 📄 Fichiers racine

```
homeflix/
├── 📋 CHANGELOG.md                     ← Historique des versions
└── ... (fichiers existants conservés)
```

---

## 🚀 Comment créer l'installateur

### Prérequis

1. **Installer InnoSetup 6**
   - Télécharger : https://jrsoftware.org/isdl.php
   - Version minimale : 6.0

2. **Installer ps2exe** (optionnel)
   ```powershell
   Install-Module ps2exe -Scope CurrentUser
   ```

### Commande simple

```powershell
cd installer
.\build-installer.ps1
```

**Résultat :** `installer/output/HomeFlix-Setup-X.X.X.exe`

---

## 📦 Ce que l'installateur fait

### Étapes d'installation

1. **Choix de la langue** (FR/EN/ES)
2. **Licence MIT** à accepter
3. **Choix du dossier** d'installation
4. **Sélection des composants** :
   - ✅ Application (obligatoire)
   - ⚙️ Python 3.10+ (si non détecté)
   - ⚙️ Node.js 18+ (si non détecté)
   - 🎬 FFmpeg (optionnel)
   - 🔄 Service Windows (optionnel)

5. **Détection automatique** des dossiers vidéo
   - Scanne tous les lecteurs
   - Détecte "Films", "Movies", "Videos", "Series", etc.
   - Compte les vidéos dans chaque dossier

6. **Configuration TMDb** (optionnel)
   - Saisie de la clé API
   - Ou skip pour plus tard

7. **Installation** :
   - Installation de Python (si besoin)
   - Installation de Node.js (si besoin)
   - Installation de FFmpeg (si besoin)
   - Création environnement virtuel Python
   - Installation packages pip (requirements.txt)
   - Installation packages npm (package.json)
   - Compilation du frontend (npm run build)
   - Création de la base de données SQLite
   - Configuration du pare-feu Windows
   - Création des dossiers de données
   - Génération de settings.yaml
   - Création des raccourcis

8. **Fin** avec option de lancer immédiatement

---

## 🔄 Mise à jour de la version

### Avant chaque build

**Modifier `client/package.json` :**

```json
{
  "name": "client",
  "version": "1.2.3",  ← CHANGER ICI
  ...
}
```

Le script de build lira automatiquement cette version.

---

## ✨ Fonctionnalités de l'installateur

### Détection intelligente

- ✅ Détecte Python 3.10+ déjà installé
- ✅ Détecte Node.js 18+ déjà installé
- ✅ Détecte FFmpeg déjà installé
- ✅ Scanne tous les lecteurs pour trouver des vidéos
- ✅ Compte les vidéos dans chaque dossier
- ✅ Détecte l'adresse IP locale

### Installation automatique

- ✅ Télécharge et installe Python si nécessaire
- ✅ Télécharge et installe Node.js si nécessaire
- ✅ Télécharge et installe FFmpeg si nécessaire
- ✅ Crée l'environnement virtuel Python
- ✅ Installe tous les packages automatiquement
- ✅ Compile le frontend en mode production

### Configuration automatique

- ✅ Génère `settings.yaml` avec les dossiers détectés
- ✅ Ajoute la clé TMDb si fournie
- ✅ Crée la base de données SQLite
- ✅ Configure les règles de pare-feu Windows
- ✅ Crée tous les dossiers nécessaires

### Intégration système

- ✅ Raccourci sur le bureau
- ✅ Raccourci dans le menu Démarrer
- ✅ Option de service Windows
- ✅ Désinstallateur propre

### Multi-langue

- 🇫🇷 Français
- 🇬🇧 Anglais
- 🇪🇸 Espagnol

---

## 🎯 Réponse à ta question

> "Même si on crée l'installeur maintenant et que l'on change le programme, 
> l'installeur il va se mettre à jour pour installé la bonne version ?"

**Réponse : OUI, MAIS...**

### Comment ça marche

1. **La version est lue au moment du BUILD**, pas de l'installation
2. Le script `build-installer.ps1` lit `client/package.json`
3. Il crée `version.ini` avec cette version
4. InnoSetup compile avec cette version
5. L'installateur contient le CODE au moment du build

### Donc :

✅ **Si tu modifies le code** → Il faut **reconstruire** l'installateur

```powershell
# Workflow :
1. Modifier le code
2. Modifier la version dans client/package.json
3. cd installer
4. .\build-installer.ps1
5. Nouveau HomeFlix-Setup-X.X.X.exe créé
```

❌ **L'installateur ne se met PAS à jour tout seul**

Il faut le reconstruire pour chaque nouvelle version.

### Workflow complet

```
CODE CHANGE
    ↓
UPDATE client/package.json version
    ↓
UPDATE CHANGELOG.md
    ↓
cd installer; .\build-installer.ps1
    ↓
TEST sur machine vierge
    ↓
PUBLISH HomeFlix-Setup-X.X.X.exe
```

---

## 📋 Checklist avant publication

### Code

- [ ] Tous les tests passent
- [ ] Pas d'erreurs dans les logs
- [ ] Frontend compile sans warnings
- [ ] Backend démarre correctement

### Version

- [ ] Version mise à jour dans `client/package.json`
- [ ] CHANGELOG.md mis à jour avec les nouveautés
- [ ] Date de release dans CHANGELOG.md

### Build

- [ ] `cd installer; .\build-installer.ps1` exécuté
- [ ] Aucune erreur de compilation
- [ ] Fichier .exe créé dans `installer/output/`

### Tests

- [ ] Installateur testé sur Windows 10
- [ ] Installateur testé sur Windows 11
- [ ] Test avec Python déjà installé
- [ ] Test sans Python (installation auto)
- [ ] Test avec Node.js déjà installé
- [ ] Test sans Node.js (installation auto)
- [ ] Test en tant qu'admin
- [ ] Test en tant qu'utilisateur normal
- [ ] Désinstallation propre testée

### Distribution

- [ ] Checksum SHA256 généré
- [ ] Tag Git créé (`git tag v1.2.3`)
- [ ] Release GitHub créée
- [ ] Fichier .exe uploadé
- [ ] README GitHub mis à jour

---

## 🔒 Sécurité

### Fichiers EXCLUS de l'installateur

Ces fichiers ne sont JAMAIS inclus :

- ❌ `homeflix.db` (base de données utilisateur)
- ❌ `settings.yaml` avec vraie clé API
- ❌ `*.log` (logs de développement)
- ❌ `__pycache__/` (cache Python)
- ❌ `node_modules/` (packages npm - réinstallés)
- ❌ `.venv*/` (environnement virtuel - recréé)
- ❌ `data/posters/` (affiches - re-téléchargées)
- ❌ `data/thumbs/` (miniatures - régénérées)

### Fichiers INCLUS

- ✅ Code source Python (`server/`)
- ✅ Code source React (`client/src/`)
- ✅ `requirements.txt`
- ✅ `package.json`
- ✅ Scripts d'installation
- ✅ Fichiers de traduction
- ✅ Documentation

---

## 📞 Support

### Si problème avec le build

1. Vérifier InnoSetup installé
2. Vérifier version dans `client/package.json`
3. Lire les logs d'erreur
4. Consulter `installer/BUILD_GUIDE.md`

### Si problème avec l'installateur

1. Tester sur machine vierge (VM ou Windows Sandbox)
2. Vérifier les logs d'installation
3. Vérifier les droits admin si nécessaire

---

## 🎉 C'est terminé !

Tu as maintenant :

✅ Un **installateur Windows professionnel**
✅ **Multi-langue** (FR/EN/ES)
✅ **Détection automatique** de tout
✅ **Installation silencieuse** des dépendances
✅ **Configuration automatique**
✅ **Documentation complète**
✅ **Système de versioning**

**Pour créer ton premier installateur :**

```powershell
cd installer
.\build-installer.ps1
```

**Le fichier sera créé dans :**
`installer/output/HomeFlix-Setup-1.0.0.exe`

**Bonne distribution ! 🚀**
