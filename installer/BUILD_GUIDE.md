# 📦 HomeFlix - Guide de Build de l'Installateur

## 🎯 Prérequis pour créer l'installateur

### Logiciels nécessaires :

1. **InnoSetup 6** (obligatoire)
   - Télécharger : https://jrsoftware.org/isdl.php
   - Installer avec les options par défaut

2. **ps2exe** (optionnel, pour le launcher .exe)

   ```powershell
   Install-Module ps2exe -Scope CurrentUser
   ```

3. **Python 3.10+** et **Node.js 18+** (pour le build)

---

## 🚀 Créer l'installateur

### Méthode simple (tout automatique) :

```powershell
cd installer
.\build-installer.ps1
```

Cela va :
- ✅ Récupérer la version depuis `client/package.json`
- ✅ Nettoyer les fichiers temporaires
- ✅ Compiler le frontend React
- ✅ Créer le launcher Windows
- ✅ Générer les fichiers de licence
- ✅ Compiler l'installateur avec InnoSetup
- ✅ Créer `HomeFlix-Setup-X.X.X.exe` dans `installer/output/`

### Options avancées :

```powershell
# Skip le build du frontend (si déjà compilé)
.\build-installer.ps1 -SkipBuild

# Skip les tests de validation
.\build-installer.ps1 -SkipTests

# Les deux
.\build-installer.ps1 -SkipBuild -SkipTests
```

---

## 📋 Ce qui est inclus dans l'installateur

### Composants installés :

| Composant | Description | Obligatoire |
|-----------|-------------|-------------|
| **Application principale** | Backend Python + Frontend React | ✅ Oui |
| **Python 3.10+** | Si non détecté sur le système | ⚙️ Auto |
| **Node.js 18+** | Si non détecté sur le système | ⚙️ Auto |
| **FFmpeg** | Pour génération miniatures | ❌ Optionnel |
| **Service Windows** | Démarrage automatique | ❌ Optionnel |

### Fonctionnalités de l'installateur :

- ✅ **Multi-langue** : Français, Anglais, Espagnol
- ✅ **Détection automatique** : Python, Node.js, FFmpeg déjà installés
- ✅ **Scan des dossiers vidéo** : Détection auto des dossiers Films/Videos
- ✅ **Configuration TMDb** : Ajout de la clé API pendant l'installation
- ✅ **Configuration pare-feu** : Autorisation automatique des ports 8000/5173
- ✅ **Création DB** : Base de données SQLite prête à l'emploi
- ✅ **Raccourcis** : Bureau + Menu Démarrer

---

## 🔄 Mise à jour de la version

### Automatique (recommandé) :

La version est lue depuis `client/package.json` :

```json
{
  "name": "client",
  "version": "1.2.3",
  ...
}
```

**Modifier cette version avant de builder l'installateur !**

### Manuel :

Créer/modifier `installer/version.ini` :

```ini
[Version]
Number=1.2.3
Date=2025-11-14
```

---

## 🧪 Tester l'installateur

### Sur machine de dev :

1. **Créer une VM ou utiliser Windows Sandbox**
   ```powershell
   # Windows Sandbox (Windows 10 Pro/Enterprise)
   Enable-WindowsOptionalFeature -FeatureName "Containers-DisposableClientVM" -All -Online
   ```

2. **Copier `HomeFlix-Setup-X.X.X.exe` dans la VM**

3. **Exécuter l'installateur**
   - Tester avec et sans droits admin
   - Tester les différentes langues
   - Tester avec/sans Python/Node.js pré-installés

4. **Vérifier** :
   - ✅ Installation complète sans erreurs
   - ✅ Raccourcis fonctionnent
   - ✅ Application se lance correctement
   - ✅ Scan des vidéos fonctionne
   - ✅ Désinstallation propre

---

## 📁 Structure du dossier installer/

```
installer/
├── homeflix.iss                    # Script InnoSetup principal
├── build-installer.ps1              # Script de build
├── detect-environment.ps1           # Détection Python/Node/FFmpeg/dossiers
├── install-dependencies.ps1         # Installation packages pip/npm
├── configure-system.ps1             # Config DB/pare-feu/dossiers
├── locales/
│   ├── fr.json                      # Traductions françaises
│   ├── en.json                      # Traductions anglaises
│   ├── es.json                      # Traductions espagnoles
│   ├── LICENSE.*.txt                # Licences multi-langues
│   └── README.*.txt                 # README multi-langues
├── version.ini                      # Version (auto-généré)
├── homeflix-launcher.exe            # Launcher Windows (auto-généré)
└── output/
    └── HomeFlix-Setup-X.X.X.exe     # INSTALLATEUR FINAL
```

---

## ⚠️ Problèmes courants

### "InnoSetup non trouvé"
```powershell
# Installer InnoSetup 6
# Télécharger depuis : https://jrsoftware.org/isdl.php
```

### "ps2exe non trouvé"
```powershell
# Installer le module PowerShell
Install-Module ps2exe -Scope CurrentUser

# Ou skip la création du .exe
# Le launcher .ps1 sera utilisé à la place
```

### "Erreur lors de la compilation du frontend"
```powershell
# Nettoyer et réinstaller
cd client
Remove-Item -Recurse -Force node_modules, dist
npm install
npm run build
```

### "La version est 0.0.0"
```powershell
# Vérifier client/package.json
# Modifier la propriété "version"
```

---

## 🎯 Checklist avant release

- [ ] Version mise à jour dans `client/package.json`
- [ ] Changelog créé dans `CHANGELOG.md`
- [ ] Tous les tests passent
- [ ] Frontend compilé sans warnings
- [ ] README à jour
- [ ] Installateur testé sur machine vierge
- [ ] Installateur testé avec/sans admin
- [ ] Désinstallation testée et propre
- [ ] Clé API TMDb de test retirée
- [ ] Fichiers de log/debug retirés

---

## 📤 Distribution

### Hébergement recommandé :

1. **GitHub Releases**
   ```bash
   # Créer un tag
   git tag v1.2.3
   git push origin v1.2.3
   
   # Upload sur GitHub Releases
   # Le fichier sera : HomeFlix-Setup-1.2.3.exe
   ```

2. **Checksum** (pour sécurité)
   ```powershell
   # Générer SHA256
   Get-FileHash .\output\HomeFlix-Setup-1.2.3.exe -Algorithm SHA256 | Format-List
   
   # Publier le hash avec le fichier
   ```

3. **Signature de code** (optionnel)
   ```powershell
   # Si vous avez un certificat code signing
   signtool sign /f cert.pfx /p password /tr http://timestamp.digicert.com HomeFlix-Setup-1.2.3.exe
   ```

---

## 🔒 Sécurité

### Fichiers à NE PAS inclure :

- ❌ `homeflix.db` (base de données utilisateur)
- ❌ `settings.yaml` avec vraie clé API
- ❌ `*.log` (fichiers de log)
- ❌ `__pycache__/` (cache Python)
- ❌ `node_modules/` (trop gros, réinstallé automatiquement)
- ❌ `.venv*/` (environnement virtuel, recréé automatiquement)

### Sont inclus :

- ✅ Code source Python/JavaScript
- ✅ `requirements.txt` et `package.json`
- ✅ Scripts d'installation
- ✅ Fichiers de traduction
- ✅ Documentation

---

## 📞 Support

Pour tout problème avec le build de l'installateur :

1. Vérifier les prérequis (InnoSetup installé)
2. Lire les logs d'erreur dans le terminal
3. Tester sur machine vierge
4. Ouvrir une issue sur GitHub avec :
   - Version de Windows
   - Version d'InnoSetup
   - Logs complets de l'erreur
   - Commande exacte utilisée

---

**Bon build ! 🚀**
